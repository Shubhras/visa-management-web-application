from django.shortcuts import render
from  .models  import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import  *
from django.core.paginator import Paginator
from django.db.models import Q
import uuid
from rest_framework.permissions import IsAuthenticated ,AllowAny ,BasePermission 
from django.shortcuts import get_object_or_404
from .pagination import  *
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.exceptions import TokenError  
from rest_framework_simplejwt.authentication import JWTAuthentication
from import_export.formats.base_formats import CSV, XLSX
from tablib import Dataset
import openpyxl
from django.http import HttpResponse
from uuid import UUID
from datetime import datetime  
from django.db import IntegrityError,transaction
import csv
import io
import pytz
from django.utils import timezone
import unicodedata

india_tz = pytz.timezone('Asia/Kolkata')

class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_superuser)
    

class JobTypeListAPIView(APIView):
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['name', 'description', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = JobType.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(Q(name__istartswith=search))

        queryset = queryset.order_by(sort_by)

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = JobTypeSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class JobTypeCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        name = request.data.get("name", "").strip()

        existing = JobType.objects.filter(name__iexact=name, is_deleted=False).first()
        if existing:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Job Type with this name already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = JobTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Job Type created successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        else:
            errors = serializer.errors
            messages = [msg for msgs in errors.values() for msg in msgs]
            return Response({
                "statusCode": 400,
                "status": False,
                "message": " ".join(messages)
            }, status=status.HTTP_400_BAD_REQUEST)


class JobTypeRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            jobtype = JobType.objects.get(uuid=uuid, is_deleted=False)
        except JobType.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Job Type not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = JobTypeSerializer(jobtype)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Job Type retrieved successfully",
            "data": serializer.data
        })


class JobTypeUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            jobtype = JobType.objects.get(uuid=uuid, is_deleted=False)
        except JobType.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Job Type not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = JobTypeSerializer(jobtype, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Job Type updated successfully",
                "data": serializer.data
            })

        messages = [msg for msgs in serializer.errors.values() for msg in msgs]
        return Response({
            "statusCode": 400,
            "status": False,
            "message": " ".join(messages),
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)


class JobTypeDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get('id', None)

        # Delete by UUID
        if uuid:
            try:
                jobtype = JobType.objects.get(uuid=uuid)
                jobtype.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "Job Type permanently deleted.",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            except JobType.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Job Type not found.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        # Delete all
        if ids == "all":
            jobtypes = JobType.objects.all()
            count = jobtypes.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No job types found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
            jobtypes.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} job type(s) permanently deleted.",
                "data": None
            })

        # Bulk delete
        if not ids or not isinstance(ids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide list of UUIDs or 'all'.",
            }, status=status.HTTP_400_BAD_REQUEST)

        valid_uuids, invalid_uuids = [], []
        for u in ids:
            try:
                valid_uuids.append(UUID(u))
            except ValueError:
                invalid_uuids.append(u)

        jobtypes = JobType.objects.filter(uuid__in=valid_uuids)
        count = jobtypes.count()
        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching job types found.",
                "data": {"invalid_uuids": invalid_uuids}
            })

        jobtypes.delete()
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} job type(s) permanently deleted.",
            "data": {"invalid_uuids": invalid_uuids}
        })


class JobTypeExportAPIView(APIView):
    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')

        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'name': 'Job Type',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'updated_at': 'Modified On',
        }

        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())

        queryset = JobType.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'Job Type'

        for obj in queryset:
            row = []
            for field in field_list:
                value = getattr(obj, field, '')
                if field in ['created_at', 'updated_at'] and value:
                    value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
                elif isinstance(value, bool):
                    value = int(value)
                row.append(value if value is not None else '')
            dataset.append(row)

        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'job_types.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'job_types.xlsx'

        response = HttpResponse(file_data if format_type == 'csv' else file_data.getvalue(), content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


class JobTypeImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get("file")
        sheet_name = request.data.get("sheet_name")

        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split(".")[-1].lower()
        duplicates, skipped_rows, data = [], [], []

        required_headers = {"job type"}
        optional_headers = {"description"}

        try:
            if format_type == "xlsx":
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames
                if not sheet_name:
                    return Response({"error": "Please provide sheet_name", "available_sheets": available_sheets}, status=400)
                if sheet_name not in available_sheets:
                    return Response({"error": f'Sheet "{sheet_name}" not found', "available_sheets": available_sheets}, status=400)
                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({"message": f'Sheet "{sheet_name}" is empty.'}, status=400)
                headers = [str(c.value).strip().lower() if c.value else "" for c in next(ws.iter_rows(min_row=1, max_row=1))]
                if not required_headers.issubset(set(headers)):
                    return Response({"message": f"Missing required headers {required_headers}"}, status=400)
                for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row): continue
                    row_dict = dict(zip(headers, row))
                    row_dict["_row_number"] = idx
                    data.append(row_dict)

            elif format_type == "csv":
                decoded_file = file.read().decode("utf-8")
                dataset = Dataset()
                dataset.load(decoded_file, format="csv")
                for idx, row in enumerate(dataset.dict, start=2):
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    row_lower["_row_number"] = idx
                    data.append(row_lower)
            else:
                return Response({"message": "Unsupported file format"}, status=400)

            imported_count = 0
            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")
                name = str(row.get("job type")).strip() if row.get("job type") else None
                description = str(row.get("description")).strip() if row.get("description") else ""

                if not name:
                    skipped_rows.append({"Row": row_number, "Reason": "Missing Job Type name"})
                    continue

                existing = JobType.objects.filter(name__iexact=name).first()
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({"Row": row_number, "Job Type": name, "Reason": "Already exists"})
                        continue
                    else:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    JobType.objects.create(name=name, description=description)
                    imported_count += 1

        except Exception as e:
            return Response({"message": str(e)}, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Import successful",
            "imported_count": imported_count,
            "duplicates": duplicates,
            "skipped_rows": skipped_rows
        }, status=200)





class ModeofSalaryListAPIView(APIView):
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['name', 'description', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = ModeofSalary.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(Q(name__istartswith=search))

        queryset = queryset.order_by(sort_by)

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = ModeofSalarySerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class ModeofSalaryCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        name = request.data.get("name", "").strip()

        existing = ModeofSalary.objects.filter(name__iexact=name, is_deleted=False).first()
        if existing:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Mode of Salary with this name already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = ModeofSalarySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Mode of Salary created successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        else:
            messages = [msg for msgs in serializer.errors.values() for msg in msgs]
            return Response({
                "statusCode": 400,
                "status": False,
                "message": " ".join(messages)
            }, status=status.HTTP_400_BAD_REQUEST)


class ModeofSalaryRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = ModeofSalary.objects.get(uuid=uuid, is_deleted=False)
        except ModeofSalary.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Mode of Salary not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = ModeofSalarySerializer(obj)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Mode of Salary retrieved successfully",
            "data": serializer.data
        })


class ModeofSalaryUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = ModeofSalary.objects.get(uuid=uuid, is_deleted=False)
        except ModeofSalary.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Mode of Salary not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = ModeofSalarySerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Mode of Salary updated successfully",
                "data": serializer.data
            })

        messages = [msg for msgs in serializer.errors.values() for msg in msgs]
        return Response({
            "statusCode": 400,
            "status": False,
            "message": " ".join(messages),
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)


class ModeofSalaryDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get('id', None)

        # Single delete
        if uuid:
            try:
                obj = ModeofSalary.objects.get(uuid=uuid)
                obj.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "Mode of Salary permanently deleted.",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            except ModeofSalary.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Mode of Salary not found.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        # Delete all
        if ids == "all":
            objs = ModeofSalary.objects.all()
            count = objs.count()
            if count == 0:
                return Response({"statusCode": 404, "status": False, "message": "No records found to delete."}, status=404)
            objs.delete()
            return Response({"statusCode": 200, "status": True, "message": f"All {count} records deleted."})

        # Bulk delete
        if not ids or not isinstance(ids, list):
            return Response({"statusCode": 400, "status": False, "message": "Provide list of UUIDs or 'all'."}, status=400)

        valid_uuids, invalid_uuids = [], []
        for u in ids:
            try:
                valid_uuids.append(UUID(u))
            except ValueError:
                invalid_uuids.append(u)

        objs = ModeofSalary.objects.filter(uuid__in=valid_uuids)
        count = objs.count()
        if count == 0:
            return Response({"statusCode": 404, "status": False, "message": "No matching records found.", "data": {"invalid_uuids": invalid_uuids}})

        objs.delete()
        return Response({"statusCode": 200, "status": True, "message": f"{count} record(s) deleted.", "data": {"invalid_uuids": invalid_uuids}})


class ModeofSalaryExportAPIView(APIView):
    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'name': 'Mode of Salary',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'updated_at': 'Modified On',
        }
        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())

        queryset = ModeofSalary.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'Mode of Salary'

        for obj in queryset:
            row = []
            for field in field_list:
                value = getattr(obj, field, '')
                if field in ['created_at', 'updated_at'] and value:
                    value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
                elif isinstance(value, bool):
                    value = int(value)
                row.append(value if value is not None else '')
            dataset.append(row)

        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'mode_of_salary.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'mode_of_salary.xlsx'

        response = HttpResponse(file_data if format_type == 'csv' else file_data.getvalue(), content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


class ModeofSalaryImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get("file")
        sheet_name = request.data.get("sheet_name")
        if not file:
            return Response({"error": "No file uploaded"}, status=400)

        format_type = file.name.split(".")[-1].lower()
        duplicates, skipped_rows, data = [], [], []

        required_headers = {"mode of salary"}
        optional_headers = {"description"}

        try:
            if format_type == "xlsx":
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames
                if not sheet_name:
                    return Response({"error": "Provide sheet_name", "available_sheets": available_sheets}, status=400)
                if sheet_name not in available_sheets:
                    return Response({"error": f'Sheet "{sheet_name}" not found', "available_sheets": available_sheets}, status=400)
                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({"message": f'Sheet "{sheet_name}" is empty.'}, status=400)
                headers = [str(c.value).strip().lower() if c.value else "" for c in next(ws.iter_rows(min_row=1, max_row=1))]
                if not required_headers.issubset(set(headers)):
                    return Response({"message": f"Missing required headers {required_headers}"}, status=400)
                for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row): continue
                    row_dict = dict(zip(headers, row))
                    row_dict["_row_number"] = idx
                    data.append(row_dict)
            elif format_type == "csv":
                decoded_file = file.read().decode("utf-8")
                dataset = Dataset()
                dataset.load(decoded_file, format="csv")
                for idx, row in enumerate(dataset.dict, start=2):
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    row_lower["_row_number"] = idx
                    data.append(row_lower)
            else:
                return Response({"message": "Unsupported file format"}, status=400)

            imported_count = 0
            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")
                name = str(row.get("mode of salary")).strip() if row.get("mode of salary") else None
                description = str(row.get("description")).strip() if row.get("description") else ""

                if not name:
                    skipped_rows.append({"Row": row_number, "Reason": "Missing name"})
                    continue

                existing = ModeofSalary.objects.filter(name__iexact=name).first()
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({"Row": row_number, "Name": name, "Reason": "Already exists"})
                        continue
                    else:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    ModeofSalary.objects.create(name=name, description=description)
                    imported_count += 1

        except Exception as e:
            return Response({"message": str(e)}, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Import successful",
            "imported_count": imported_count,
            "duplicates": duplicates,
            "skipped_rows": skipped_rows
        }, status=200)




class ITReturnStatusListAPIView(APIView):
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['name', 'description', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = ITReturnStatus.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(Q(name__istartswith=search))
        queryset = queryset.order_by(sort_by)

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = ITReturnStatusSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class ITReturnStatusCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        name = request.data.get("name", "").strip()

        existing = ITReturnStatus.objects.filter(name__iexact=name, is_deleted=False).first()
        if existing:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "IT Return Status with this name already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = ITReturnStatusSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "IT Return Status created successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        else:
            messages = [msg for msgs in serializer.errors.values() for msg in msgs]
            return Response({
                "statusCode": 400,
                "status": False,
                "message": " ".join(messages)
            }, status=status.HTTP_400_BAD_REQUEST)


class ITReturnStatusRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = ITReturnStatus.objects.get(uuid=uuid, is_deleted=False)
        except ITReturnStatus.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "IT Return Status not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = ITReturnStatusSerializer(obj)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "IT Return Status retrieved successfully",
            "data": serializer.data
        })


class ITReturnStatusUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = ITReturnStatus.objects.get(uuid=uuid, is_deleted=False)
        except ITReturnStatus.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "IT Return Status not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = ITReturnStatusSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "IT Return Status updated successfully",
                "data": serializer.data
            })
        messages = [msg for msgs in serializer.errors.values() for msg in msgs]
        return Response({
            "statusCode": 400,
            "status": False,
            "message": " ".join(messages),
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)


class ITReturnStatusDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get('id', None)

        # Single delete
        if uuid:
            try:
                obj = ITReturnStatus.objects.get(uuid=uuid)
                obj.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "IT Return Status permanently deleted.",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            except ITReturnStatus.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "IT Return Status not found.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        # Delete all
        if ids == "all":
            objs = ITReturnStatus.objects.all()
            count = objs.count()
            if count == 0:
                return Response({"statusCode": 404, "status": False, "message": "No records found to delete."}, status=404)
            objs.delete()
            return Response({"statusCode": 200, "status": True, "message": f"All {count} records deleted."})

        # Bulk delete
        if not ids or not isinstance(ids, list):
            return Response({"statusCode": 400, "status": False, "message": "Provide list of UUIDs or 'all'."}, status=400)

        valid_uuids, invalid_uuids = [], []
        for u in ids:
            try:
                valid_uuids.append(UUID(u))
            except ValueError:
                invalid_uuids.append(u)

        objs = ITReturnStatus.objects.filter(uuid__in=valid_uuids)
        count = objs.count()
        if count == 0:
            return Response({"statusCode": 404, "status": False, "message": "No matching records found.", "data": {"invalid_uuids": invalid_uuids}})

        objs.delete()
        return Response({"statusCode": 200, "status": True, "message": f"{count} record(s) deleted.", "data": {"invalid_uuids": invalid_uuids}})


class ITReturnStatusExportAPIView(APIView):
    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'name': 'IT Return Status',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'updated_at': 'Modified On',
        }
        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())

        queryset = ITReturnStatus.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'IT Return Status'

        for obj in queryset:
            row = []
            for field in field_list:
                value = getattr(obj, field, '')
                if field in ['created_at', 'updated_at'] and value:
                    value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
                elif isinstance(value, bool):
                    value = int(value)
                row.append(value if value is not None else '')
            dataset.append(row)

        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'it_return_status.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'it_return_status.xlsx'

        response = HttpResponse(file_data if format_type == 'csv' else file_data.getvalue(), content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


class ITReturnStatusImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get("file")
        sheet_name = request.data.get("sheet_name")
        if not file:
            return Response({"error": "No file uploaded"}, status=400)

        format_type = file.name.split(".")[-1].lower()
        duplicates, skipped_rows, data = [], [], []

        required_headers = {"it return status"}
        optional_headers = {"description"}

        try:
            if format_type == "xlsx":
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames
                if not sheet_name:
                    return Response({"error": "Provide sheet_name", "available_sheets": available_sheets}, status=400)
                if sheet_name not in available_sheets:
                    return Response({"error": f'Sheet "{sheet_name}" not found', "available_sheets": available_sheets}, status=400)
                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({"message": f'Sheet "{sheet_name}" is empty.'}, status=400)
                headers = [str(c.value).strip().lower() if c.value else "" for c in next(ws.iter_rows(min_row=1, max_row=1))]
                if not required_headers.issubset(set(headers)):
                    return Response({"message": f"Missing required headers {required_headers}"}, status=400)
                for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row): continue
                    row_dict = dict(zip(headers, row))
                    row_dict["_row_number"] = idx
                    data.append(row_dict)
            elif format_type == "csv":
                decoded_file = file.read().decode("utf-8")
                dataset = Dataset()
                dataset.load(decoded_file, format="csv")
                for idx, row in enumerate(dataset.dict, start=2):
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    row_lower["_row_number"] = idx
                    data.append(row_lower)
            else:
                return Response({"message": "Unsupported file format"}, status=400)

            imported_count = 0
            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")
                name = str(row.get("it return status")).strip() if row.get("it return status") else None
                description = str(row.get("description")).strip() if row.get("description") else ""

                if not name:
                    skipped_rows.append({"Row": row_number, "Reason": "Missing name"})
                    continue

                existing = ITReturnStatus.objects.filter(name__iexact=name).first()
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({"Row": row_number, "Name": name, "Reason": "Already exists"})
                        continue
                    else:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    ITReturnStatus.objects.create(name=name, description=description)
                    imported_count += 1

        except Exception as e:
            return Response({"message": str(e)}, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Import successful",
            "imported_count": imported_count,
            "duplicates": duplicates,
            "skipped_rows": skipped_rows
        }, status=200)



