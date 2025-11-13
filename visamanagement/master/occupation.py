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







class OccupationVersionListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')
        allowed_sort_fields = ['occupation_version', 'effect_from', 'valid_upto', 'created_at']

        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = OccupationVersion.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(
                Q(occupation_version__istartswith=search) |
                Q(description__istartswith=search) |
                Q(country__country_name__istartswith=search)
            )

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = OccupationVersionSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


# -------------------- Create -------------------- #
class OccupationVersionCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        # Validate mandatory fields
        country_uuid = request.data.get("country_id")
        occupation_version = request.data.get("occupation_version")
        effect_from = request.data.get("effect_from")

        if not country_uuid or not occupation_version or not effect_from:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Mandatory fields missing: country_id, occupation_version, effect_from"
            }, status=400)

        # Validate country
        try:
            country_obj = Country.objects.get(uuid=country_uuid)
        except Country.DoesNotExist:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Invalid country UUID."
            }, status=400)

        # Check duplicate (country + occupation_version + effect_from)
        existing = OccupationVersion.objects.filter(
            country=country_obj,
            occupation_version=occupation_version,
            effect_from=effect_from,
            is_deleted=False
        ).first()
        if existing:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Occupation version for this country and effect_from already exists."
            }, status=400)

        data = request.data.copy()
        data['country_id'] = country_obj.uuid

        serializer = OccupationVersionSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Occupation version created successfully",
                "data": serializer.data
            })

        errors = " ".join([msg for msgs in serializer.errors.values() for msg in msgs])
        return Response({
            "statusCode": 400,
            "status": False,
            "message": errors
        }, status=400)


# -------------------- Retrieve -------------------- #
class OccupationVersionRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = OccupationVersion.objects.get(uuid=uuid, is_deleted=False)
        except OccupationVersion.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "Not found", "data": None}, status=404)
        serializer = OccupationVersionSerializer(obj)
        return Response({"statusCode": 200, "status": True, "message": "Retrieved successfully", "data": serializer.data})


# -------------------- Update -------------------- #
class OccupationVersionUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = OccupationVersion.objects.get(uuid=uuid, is_deleted=False)
        except OccupationVersion.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "Not found", "data": None}, status=404)

        serializer = OccupationVersionSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"statusCode": 200, "status": True, "message": "Updated successfully", "data": serializer.data})

        errors = " ".join([msg for msgs in serializer.errors.values() for msg in msgs])
        return Response({"statusCode": 400, "status": False, "message": errors}, status=400)


# -------------------- Delete -------------------- #
class OccupationVersionDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        ids = request.data.get('id', None)
        if not ids:
            return Response({"statusCode": 400, "status": False, "message": "Provide 'id' field", "data": None}, status=400)

        if ids == "all":
            objs = OccupationVersion.objects.filter(is_deleted=False)
            count = objs.count()
            objs.delete()
            return Response({"statusCode": 200, "status": True, "message": f"All {count} record(s) deleted", "data": None})

        if not isinstance(ids, list):
            return Response({"statusCode": 400, "status": False, "message": "Provide list of UUIDs", "data": None}, status=400)

        valid_uuids, invalid_uuids = [], []
        for u in ids:
            try:
                valid_uuids.append(UUID(u))
            except ValueError:
                invalid_uuids.append(u)

        objs = OccupationVersion.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = objs.count()
        if count == 0:
            return Response({"statusCode": 404, "status": False, "message": "No matching record found", "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None}, status=404)

        objs.delete()
        return Response({"statusCode": 200, "status": True, "message": f"{count} record(s) deleted", "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None})


# -------------------- Export -------------------- #
class OccupationVersionExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'country': 'Country',
            'occupation_version': 'Occupation Version',
            'effect_from': 'Start Date',
            'valid_upto': 'End Date',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'created_at': 'Created On',
            'updated_at': 'Modified On',
        }

        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())
        queryset = OccupationVersion.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'Occupation Versions'

        for obj in queryset:
            row = []
            for field in field_list:
                value = getattr(obj, field, '')
                if field == 'country' and value:
                    value = value.country_name
                elif field in ['created_at', 'updated_at', 'effect_from', 'valid_upto'] and value:
                    value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
                elif isinstance(value, bool):
                    value = int(value)
                row.append(value if value is not None else '')
            dataset.append(row)

        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'occupation_versions.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'occupation_versions.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


# -------------------- Import -------------------- #
class OccupationVersionImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=400)

        format_type = file.name.split('.')[-1].lower()
        duplicate_entries = []
        skipped_rows = []
        required_headers = {'country', 'occupation version', 'start date'}
        optional_headers = {'end date', 'description'}

        try:
            data = []

            # XLSX
            if format_type == 'xlsx':
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames
                if not sheet_name:
                    return Response({'error': 'Provide sheet_name', 'available_sheets': available_sheets}, status=400)
                if sheet_name not in available_sheets:
                    return Response({'error': f'Sheet "{sheet_name}" not found', 'available_sheets': available_sheets}, status=400)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({'error': f'Sheet "{sheet_name}" is empty.'}, status=400)

                headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                if not required_headers.issubset(set(headers)):
                    return Response({'error': f'Missing required headers. Required: {required_headers}, Found: {set(headers)}'}, status=400)

                for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    data.append((idx, row_dict))  # keep row number for skipped rows

            # CSV
            elif format_type == 'csv':
                dataset = Dataset()
                dataset.load(file.read().decode('utf-8'), format='csv')
                for idx, row in enumerate(dataset.dict, start=2):
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({'error': f'Missing required headers. Required: {required_headers}'}, status=400)
                    data.append((idx, row_lower))
            else:
                return Response({'error': 'Unsupported file format. Use .xlsx or .csv'}, status=400)

            imported_count = 0
            for row_number, row in data:
                country_name = str(row.get('country')).strip() if row.get('country') else None
                occupation_version = str(row.get('occupation version')).strip() if row.get('occupation version') else None
                effect_from = row.get('start date')
                valid_upto = row.get('end date', None)
                description = row.get('description', '')

                if not country_name or not occupation_version or not effect_from:
                    skipped_rows.append({'row': row_number, 'Reason': 'Mandatory fields missing'})
                    continue

                try:
                    country_obj = Country.objects.get(country_name__iexact=country_name)
                except Country.DoesNotExist:
                    skipped_rows.append({'row': row_number, 'Reason': 'Country not found'})
                    continue

                existing = OccupationVersion.objects.filter(
                    country=country_obj,
                    occupation_version__iexact=occupation_version,
                    effect_from=effect_from
                ).first()

                if existing:
                    if not existing.is_deleted:
                        duplicate_entries.append(f"{country_name} - {occupation_version}")
                        continue
                    else:
                        existing.valid_upto = valid_upto
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    OccupationVersion.objects.create(
                        country=country_obj,
                        occupation_version=occupation_version,
                        effect_from=effect_from,
                        valid_upto=valid_upto,
                        description=description,
                        is_deleted=False
                    )
                    imported_count += 1

        except Exception as e:
            return Response({'error': str(e)}, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": list(set(duplicate_entries)),
            "skipped_rows": skipped_rows,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count
        }, status=200)



class OccupationCategoryListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')
        allowed_sort_fields = ['occupationcategory', 'occupationcategorycode', 'created_at']

        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = OccupationCategory.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(
                Q(occupationcategory__istartswith=search) |
                Q(occupationcategorycode__istartswith=search) |
                Q(country__country_name__istartswith=search) |
                Q(occupation_version__occupation_version__istartswith=search)
            )

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = OccupationCategorySerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


# -------------------- Create -------------------- #
class OccupationCategoryCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        country_uuid = request.data.get("country_id")
        occupation_version_uuid = request.data.get("occupation_version_id")
        occupationcategory = request.data.get("occupationcategory")

        if not occupationcategory:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Mandatory field missing: occupationcategory"
            }, status=400)

        country_obj = None
        if country_uuid:
            try:
                country_obj = Country.objects.get(uuid=country_uuid)
            except Country.DoesNotExist:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Invalid country UUID."
                }, status=400)

        occupation_version_obj = None
        if occupation_version_uuid:
            try:
                occupation_version_obj = OccupationVersion.objects.get(uuid=occupation_version_uuid)
            except OccupationVersion.DoesNotExist:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Invalid occupation version UUID."
                }, status=400)

        # Check duplicate
        existing = OccupationCategory.objects.filter(
            country=country_obj,
            occupation_version=occupation_version_obj,
            occupationcategory__iexact=occupationcategory,
            is_deleted=False
        ).first()

        if existing:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Occupation category already exists for this country and occupation version."
            }, status=400)

        data = request.data.copy()
        if country_obj:
            data['country_id'] = country_obj.uuid
        if occupation_version_obj:
            data['occupation_version_id'] = occupation_version_obj.uuid

        serializer = OccupationCategorySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Occupation category created successfully",
                "data": serializer.data
            })

        errors = " ".join([msg for msgs in serializer.errors.values() for msg in msgs])
        return Response({
            "statusCode": 400,
            "status": False,
            "message": errors
        }, status=400)


# -------------------- Retrieve -------------------- #
class OccupationCategoryRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = OccupationCategory.objects.get(uuid=uuid, is_deleted=False)
        except OccupationCategory.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "Not found", "data": None}, status=404)

        serializer = OccupationCategorySerializer(obj)
        return Response({"statusCode": 200, "status": True, "message": "Retrieved successfully", "data": serializer.data})


# -------------------- Update -------------------- #
class OccupationCategoryUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = OccupationCategory.objects.get(uuid=uuid, is_deleted=False)
        except OccupationCategory.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "Not found", "data": None}, status=404)

        serializer = OccupationCategorySerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"statusCode": 200, "status": True, "message": "Updated successfully", "data": serializer.data})

        errors = " ".join([msg for msgs in serializer.errors.values() for msg in msgs])
        return Response({"statusCode": 400, "status": False, "message": errors}, status=400)


# -------------------- Delete -------------------- #
class OccupationCategoryDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        ids = request.data.get('id', None)
        if not ids:
            return Response({"statusCode": 400, "status": False, "message": "Provide 'id' field", "data": None}, status=400)

        if ids == "all":
            objs = OccupationCategory.objects.filter(is_deleted=False)
            count = objs.count()
            objs.delete()
            return Response({"statusCode": 200, "status": True, "message": f"All {count} record(s) deleted", "data": None})

        if not isinstance(ids, list):
            return Response({"statusCode": 400, "status": False, "message": "Provide list of UUIDs", "data": None}, status=400)

        valid_uuids, invalid_uuids = [], []
        for u in ids:
            try:
                valid_uuids.append(UUID(u))
            except ValueError:
                invalid_uuids.append(u)

        objs = OccupationCategory.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = objs.count()
        if count == 0:
            return Response({"statusCode": 404, "status": False, "message": "No matching record found", "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None}, status=404)

        objs.delete()
        return Response({"statusCode": 200, "status": True, "message": f"{count} record(s) deleted", "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None})


# -------------------- Export -------------------- #
class OccupationCategoryExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'country': 'Country',
            'occupation_version': 'Occupation Version',
            'occupationcategory': 'Occupation Category',
            'occupationcategorycode': 'Category Code',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'created_at': 'Created On',
            'updated_at': 'Modified On',
        }

        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())
        queryset = OccupationCategory.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'Occupation Categories'

        for obj in queryset:
            row = []
            for field in field_list:
                value = getattr(obj, field, '')
                if field == 'country' and value:
                    value = value.country_name
                elif field == 'occupation_version' and value:
                    value = value.occupation_version
                elif field in ['created_at', 'updated_at'] and value:
                    value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
                elif isinstance(value, bool):
                    value = int(value)
                row.append(value if value is not None else '')
            dataset.append(row)

        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'occupation_categories.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'occupation_categories.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


# -------------------- Import -------------------- #
class OccupationCategoryImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=400)

        format_type = file.name.split('.')[-1].lower()
        duplicate_entries = []
        skipped_rows = []
        required_headers = {'country', 'occupation version', 'occupation category'}
        optional_headers = {'category code', 'description'}

        try:
            data = []

            # XLSX
            if format_type == 'xlsx':
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames
                if not sheet_name:
                    return Response({'error': 'Provide sheet_name', 'available_sheets': available_sheets}, status=400)
                if sheet_name not in available_sheets:
                    return Response({'error': f'Sheet "{sheet_name}" not found', 'available_sheets': available_sheets}, status=400)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({'error': f'Sheet "{sheet_name}" is empty.'}, status=400)

                headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                if not required_headers.issubset(set(headers)):
                    return Response({'error': f'Missing required headers. Required: {required_headers}, Found: {set(headers)}'}, status=400)

                for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    data.append((idx, row_dict))

            # CSV
            elif format_type == 'csv':
                dataset = Dataset()
                dataset.load(file.read().decode('utf-8'), format='csv')
                for idx, row in enumerate(dataset.dict, start=2):
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({'error': f'Missing required headers. Required: {required_headers}'}, status=400)
                    data.append((idx, row_lower))
            else:
                return Response({'error': 'Unsupported file format. Use .xlsx or .csv'}, status=400)

            imported_count = 0
            for row_number, row in data:
                country_name = str(row.get('country')).strip() if row.get('country') else None
                occupation_version_name = str(row.get('occupation version')).strip() if row.get('occupation version') else None
                occupationcategory = str(row.get('occupation category')).strip() if row.get('occupation category') else None
                category_code = row.get('category code', '')
                description = row.get('description', '')

                if not country_name or not occupation_version_name or not occupationcategory:
                    skipped_rows.append({'row': row_number, 'Reason': 'Mandatory fields missing'})
                    continue

                try:
                    country_obj = Country.objects.get(country_name__iexact=country_name)
                except Country.DoesNotExist:
                    skipped_rows.append({'row': row_number, 'Reason': 'Country not found'})
                    continue

                try:
                    occupation_version_obj = OccupationVersion.objects.get(
                        country=country_obj,
                        occupation_version__iexact=occupation_version_name
                    )
                except OccupationVersion.DoesNotExist:
                    skipped_rows.append({'row': row_number, 'Reason': 'Occupation version not found'})
                    continue

                existing = OccupationCategory.objects.filter(
                    country=country_obj,
                    occupation_version=occupation_version_obj,
                    occupationcategory__iexact=occupationcategory
                ).first()

                if existing:
                    if not existing.is_deleted:
                        duplicate_entries.append(f"{country_name} - {occupation_version_name} - {occupationcategory}")
                        continue
                    else:
                        existing.occupationcategorycode = category_code
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    OccupationCategory.objects.create(
                        country=country_obj,
                        occupation_version=occupation_version_obj,
                        occupationcategory=occupationcategory,
                        occupationcategorycode=category_code,
                        description=description,
                        is_deleted=False
                    )
                    imported_count += 1

        except Exception as e:
            return Response({'error': str(e)}, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": list(set(duplicate_entries)),
            "skipped_rows": skipped_rows,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count
        }, status=200)
    

class OccupationLevelCodeListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')
        allowed_sort_fields = ['occupationlevelcode', 'created_at']

        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = OccupationLevelCode.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(
                Q(occupationlevelcode__istartswith=search) |
                Q(description__istartswith=search) |
                Q(country__country_name__istartswith=search) |
                Q(occupation_version__occupation_version__istartswith=search)
            )

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = OccupationLevelCodeSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


# -------------------- Create -------------------- #
class OccupationLevelCodeCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        country_uuid = request.data.get("country_id")
        occupation_version_uuid = request.data.get("occupation_version_id")
        occupationlevelcode = request.data.get("occupationlevelcode")

        if not occupationlevelcode:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Mandatory field missing: occupationlevelcode"
            }, status=400)

        country_obj = None
        if country_uuid:
            try:
                country_obj = Country.objects.get(uuid=country_uuid)
            except Country.DoesNotExist:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Invalid country UUID."
                }, status=400)

        occupation_version_obj = None
        if occupation_version_uuid:
            try:
                occupation_version_obj = OccupationVersion.objects.get(uuid=occupation_version_uuid)
            except OccupationVersion.DoesNotExist:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Invalid occupation version UUID."
                }, status=400)

        # Check duplicate
        existing = OccupationLevelCode.objects.filter(
            country=country_obj,
            occupation_version=occupation_version_obj,
            occupationlevelcode__iexact=occupationlevelcode,
            is_deleted=False
        ).first()

        if existing:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Occupation level code already exists for this country and occupation version."
            }, status=400)

        data = request.data.copy()
        if country_obj:
            data['country_id'] = country_obj.uuid
        if occupation_version_obj:
            data['occupation_version_id'] = occupation_version_obj.uuid

        serializer = OccupationLevelCodeSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Occupation level code created successfully",
                "data": serializer.data
            })

        errors = " ".join([msg for msgs in serializer.errors.values() for msg in msgs])
        return Response({
            "statusCode": 400,
            "status": False,
            "message": errors
        }, status=400)


# -------------------- Retrieve -------------------- #
class OccupationLevelCodeRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = OccupationLevelCode.objects.get(uuid=uuid, is_deleted=False)
        except OccupationLevelCode.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "Not found", "data": None}, status=404)

        serializer = OccupationLevelCodeSerializer(obj)
        return Response({"statusCode": 200, "status": True, "message": "Retrieved successfully", "data": serializer.data})


# -------------------- Update -------------------- #
class OccupationLevelCodeUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = OccupationLevelCode.objects.get(uuid=uuid, is_deleted=False)
        except OccupationLevelCode.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "Not found", "data": None}, status=404)

        serializer = OccupationLevelCodeSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"statusCode": 200, "status": True, "message": "Updated successfully", "data": serializer.data})

        errors = " ".join([msg for msgs in serializer.errors.values() for msg in msgs])
        return Response({"statusCode": 400, "status": False, "message": errors}, status=400)


# -------------------- Delete -------------------- #
class OccupationLevelCodeDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        ids = request.data.get('id', None)
        if not ids:
            return Response({"statusCode": 400, "status": False, "message": "Provide 'id' field", "data": None}, status=400)

        if ids == "all":
            objs = OccupationLevelCode.objects.filter(is_deleted=False)
            count = objs.count()
            objs.delete()
            return Response({"statusCode": 200, "status": True, "message": f"All {count} record(s) deleted", "data": None})

        if not isinstance(ids, list):
            return Response({"statusCode": 400, "status": False, "message": "Provide list of UUIDs", "data": None}, status=400)

        valid_uuids, invalid_uuids = [], []
        for u in ids:
            try:
                valid_uuids.append(UUID(u))
            except ValueError:
                invalid_uuids.append(u)

        objs = OccupationLevelCode.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = objs.count()
        if count == 0:
            return Response({"statusCode": 404, "status": False, "message": "No matching record found", "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None}, status=404)

        objs.delete()
        return Response({"statusCode": 200, "status": True, "message": f"{count} record(s) deleted", "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None})


# -------------------- Export -------------------- #
class OccupationLevelCodeExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'country': 'Country',
            'occupation_version': 'Occupation Version',
            'occupationlevelcode': 'Occupation Level Code',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'created_at': 'Created On',
            'updated_at': 'Modified On',
        }

        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())
        queryset = OccupationLevelCode.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'Occupation Level Codes'

        for obj in queryset:
            row = []
            for field in field_list:
                value = getattr(obj, field, '')
                if field == 'country' and value:
                    value = value.country_name
                elif field == 'occupation_version' and value:
                    value = value.occupation_version
                elif field in ['created_at', 'updated_at'] and value:
                    value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
                elif isinstance(value, bool):
                    value = int(value)
                row.append(value if value is not None else '')
            dataset.append(row)

        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'occupation_level_codes.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'occupation_level_codes.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


# -------------------- Import -------------------- #
class OccupationLevelCodeImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=400)

        format_type = file.name.split('.')[-1].lower()
        duplicate_entries = []
        skipped_rows = []
        required_headers = {'country', 'occupation version', 'occupation level code'}
        optional_headers = {'description'}

        try:
            data = []

            # XLSX
            if format_type == 'xlsx':
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames
                if not sheet_name:
                    return Response({'error': 'Provide sheet_name', 'available_sheets': available_sheets}, status=400)
                if sheet_name not in available_sheets:
                    return Response({'error': f'Sheet "{sheet_name}" not found', 'available_sheets': available_sheets}, status=400)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({'error': f'Sheet "{sheet_name}" is empty.'}, status=400)

                headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                if not required_headers.issubset(set(headers)):
                    return Response({'error': f'Missing required headers. Required: {required_headers}, Found: {set(headers)}'}, status=400)

                for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    data.append((idx, row_dict))

            # CSV
            elif format_type == 'csv':
                dataset = Dataset()
                dataset.load(file.read().decode('utf-8'), format='csv')
                for idx, row in enumerate(dataset.dict, start=2):
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({'error': f'Missing required headers. Required: {required_headers}'}, status=400)
                    data.append((idx, row_lower))
            else:
                return Response({'error': 'Unsupported file format. Use .xlsx or .csv'}, status=400)

            imported_count = 0
            for row_number, row in data:
                country_name = str(row.get('country')).strip() if row.get('country') else None
                occupation_version_name = str(row.get('occupation version')).strip() if row.get('occupation version') else None
                occupationlevelcode = str(row.get('occupation level code')).strip() if row.get('occupation level code') else None
                description = row.get('description', '')

                if not country_name or not occupation_version_name or not occupationlevelcode:
                    skipped_rows.append({'row': row_number, 'Reason': 'Mandatory fields missing'})
                    continue

                try:
                    country_obj = Country.objects.get(country_name__iexact=country_name)
                except Country.DoesNotExist:
                    skipped_rows.append({'row': row_number, 'Reason': 'Country not found'})
                    continue

                try:
                    occupation_version_obj = OccupationVersion.objects.get(
                        country=country_obj,
                        occupation_version__iexact=occupation_version_name
                    )
                except OccupationVersion.DoesNotExist:
                    skipped_rows.append({'row': row_number, 'Reason': 'Occupation version not found'})
                    continue

                existing = OccupationLevelCode.objects.filter(
                    country=country_obj,
                    occupation_version=occupation_version_obj,
                    occupationlevelcode__iexact=occupationlevelcode
                ).first()

                if existing:
                    if not existing.is_deleted:
                        duplicate_entries.append(f"{country_name} - {occupation_version_name} - {occupationlevelcode}")
                        continue
                    else:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    OccupationLevelCode.objects.create(
                        country=country_obj,
                        occupation_version=occupation_version_obj,
                        occupationlevelcode=occupationlevelcode,
                        description=description,
                        is_deleted=False
                    )
                    imported_count += 1

        except Exception as e:
            return Response({'error': str(e)}, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": list(set(duplicate_entries)),
            "skipped_rows": skipped_rows,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count
        }, status=200)


# -------------------- List -------------------- #
class OccupationLevelListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')
        allowed_sort_fields = ['occupationlevel', 'created_at']

        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = OccupationLevel.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(
                Q(occupationlevel__istartswith=search) |
                Q(description__istartswith=search) |
                Q(country__country_name__istartswith=search) |
                Q(occupationversion__occupation_version__istartswith=search) |
                Q(occupationcategory__occupationcategory__istartswith=search) |
                Q(occupationlevelcode__occupationlevelcode__istartswith=search)
            )

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = OccupationLevelSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


# -------------------- Create -------------------- #
class OccupationLevelCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        country_uuid = request.data.get("country_id")
        occupationversion_uuid = request.data.get("occupationversion_id")
        occupationcategory_uuid = request.data.get("occupationcategory_id")
        occupationlevelcode_uuid = request.data.get("occupationlevelcode_id")
        occupationlevel_name = request.data.get("occupationlevel")

        if not occupationlevel_name:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Mandatory field missing: occupationlevel"
            }, status=400)

        # Validate foreign keys
        country_obj = None
        if country_uuid:
            try:
                country_obj = Country.objects.get(uuid=country_uuid)
            except Country.DoesNotExist:
                return Response({"statusCode": 400, "status": False, "message": "Invalid country UUID."}, status=400)

        occupationversion_obj = None
        if occupationversion_uuid:
            try:
                occupationversion_obj = OccupationVersion.objects.get(uuid=occupationversion_uuid)
            except OccupationVersion.DoesNotExist:
                return Response({"statusCode": 400, "status": False, "message": "Invalid occupation version UUID."}, status=400)

        occupationcategory_obj = None
        if occupationcategory_uuid:
            try:
                occupationcategory_obj = OccupationCategory.objects.get(uuid=occupationcategory_uuid)
            except OccupationCategory.DoesNotExist:
                return Response({"statusCode": 400, "status": False, "message": "Invalid occupation category UUID."}, status=400)

        occupationlevelcode_obj = None
        if occupationlevelcode_uuid:
            try:
                occupationlevelcode_obj = OccupationLevelCode.objects.get(uuid=occupationlevelcode_uuid)
            except OccupationLevelCode.DoesNotExist:
                return Response({"statusCode": 400, "status": False, "message": "Invalid occupation level code UUID."}, status=400)

        # Check duplicate
        existing = OccupationLevel.objects.filter(
            country=country_obj,
            occupationversion=occupationversion_obj,
            occupationcategory=occupationcategory_obj,
            occupationlevelcode=occupationlevelcode_obj,
            occupationlevel__iexact=occupationlevel_name,
            is_deleted=False
        ).first()

        if existing:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Occupation level already exists for this combination."
            }, status=400)

        data = request.data.copy()
        if country_obj:
            data['country_id'] = country_obj.uuid
        if occupationversion_obj:
            data['occupationversion_id'] = occupationversion_obj.uuid
        if occupationcategory_obj:
            data['occupationcategory_id'] = occupationcategory_obj.uuid
        if occupationlevelcode_obj:
            data['occupationlevelcode_id'] = occupationlevelcode_obj.uuid

        serializer = OccupationLevelSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Occupation level created successfully",
                "data": serializer.data
            })

        errors = " ".join([msg for msgs in serializer.errors.values() for msg in msgs])
        return Response({"statusCode": 400, "status": False, "message": errors}, status=400)


# -------------------- Retrieve -------------------- #
class OccupationLevelRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = OccupationLevel.objects.get(uuid=uuid, is_deleted=False)
        except OccupationLevel.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "Not found", "data": None}, status=404)

        serializer = OccupationLevelSerializer(obj)
        return Response({"statusCode": 200, "status": True, "message": "Retrieved successfully", "data": serializer.data})


# -------------------- Update -------------------- #
class OccupationLevelUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = OccupationLevel.objects.get(uuid=uuid, is_deleted=False)
        except OccupationLevel.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "Not found", "data": None}, status=404)

        serializer = OccupationLevelSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"statusCode": 200, "status": True, "message": "Updated successfully", "data": serializer.data})

        errors = " ".join([msg for msgs in serializer.errors.values() for msg in msgs])
        return Response({"statusCode": 400, "status": False, "message": errors}, status=400)


# -------------------- Delete -------------------- #
class OccupationLevelDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        ids = request.data.get('id', None)
        if not ids:
            return Response({"statusCode": 400, "status": False, "message": "Provide 'id' field", "data": None}, status=400)

        if ids == "all":
            objs = OccupationLevel.objects.filter(is_deleted=False)
            count = objs.count()
            objs.delete()
            return Response({"statusCode": 200, "status": True, "message": f"All {count} record(s) deleted", "data": None})

        if not isinstance(ids, list):
            return Response({"statusCode": 400, "status": False, "message": "Provide list of UUIDs", "data": None}, status=400)

        valid_uuids, invalid_uuids = [], []
        for u in ids:
            try:
                valid_uuids.append(UUID(u))
            except ValueError:
                invalid_uuids.append(u)

        objs = OccupationLevel.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = objs.count()
        if count == 0:
            return Response({"statusCode": 404, "status": False, "message": "No matching record found", "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None}, status=404)

        objs.delete()
        return Response({"statusCode": 200, "status": True, "message": f"{count} record(s) deleted", "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None})


# -------------------- Export -------------------- #
class OccupationLevelExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'country': 'Country',
            'occupationversion': 'Occupation Version',
            'occupationcategory': 'Occupation Category',
            'occupationlevelcode': 'Occupation Level Code',
            'occupationlevel': 'Occupation Level',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'created_at': 'Created On',
            'updated_at': 'Modified On',
        }

        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())
        queryset = OccupationLevel.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'Occupation Levels'

        for obj in queryset:
            row = []
            for field in field_list:
                value = getattr(obj, field, '')
                if field == 'country' and value:
                    value = value.country_name
                elif field == 'occupationversion' and value:
                    value = value.occupationversion
                elif field == 'occupationcategory' and value:
                    value = value.occupationcategory
                elif field == 'occupationlevelcode' and value:
                    value = value.occupationlevelcode
                elif field in ['created_at', 'updated_at'] and value:
                    value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
                elif isinstance(value, bool):
                    value = int(value)
                row.append(value if value is not None else '')
            dataset.append(row)

        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'occupation_levels.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'occupation_levels.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


# -------------------- Import -------------------- #
class OccupationLevelImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=400)

        format_type = file.name.split('.')[-1].lower()
        duplicate_entries = []
        skipped_rows = []
        required_headers = {'country', 'occupation version', 'occupation category', 'occupation level code', 'occupation level'}
        optional_headers = {'description'}

        try:
            data = []

            # XLSX
            if format_type == 'xlsx':
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames
                if not sheet_name:
                    return Response({'error': 'Provide sheet_name', 'available_sheets': available_sheets}, status=400)
                if sheet_name not in available_sheets:
                    return Response({'error': f'Sheet "{sheet_name}" not found', 'available_sheets': available_sheets}, status=400)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({'error': f'Sheet "{sheet_name}" is empty.'}, status=400)

                headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                if not required_headers.issubset(set(headers)):
                    return Response({'error': f'Missing required headers. Required: {required_headers}, Found: {set(headers)}'}, status=400)

                for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    data.append((idx, row_dict))

            # CSV
            elif format_type == 'csv':
                dataset = Dataset()
                dataset.load(file.read().decode('utf-8'), format='csv')
                for idx, row in enumerate(dataset.dict, start=2):
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({'error': f'Missing required headers. Required: {required_headers}'}, status=400)
                    data.append((idx, row_lower))
            else:
                return Response({'error': 'Unsupported file format. Use .xlsx or .csv'}, status=400)

            imported_count = 0
            for row_number, row in data:
                country_name = str(row.get('country')).strip() if row.get('country') else None
                occupation_version_name = str(row.get('occupation version')).strip() if row.get('occupation version') else None
                occupation_category_name = str(row.get('occupation category')).strip() if row.get('occupation category') else None
                occupation_level_code_name = str(row.get('occupation level code')).strip() if row.get('occupation level code') else None
                occupation_level_name = str(row.get('occupation level')).strip() if row.get('occupation level') else None
                description = row.get('description', '')

                if not country_name or not occupation_version_name or not occupation_category_name or not occupation_level_code_name or not occupation_level_name:
                    skipped_rows.append({'row': row_number, 'Reason': 'Mandatory fields missing'})
                    continue

                try:
                    country_obj = Country.objects.get(country_name__iexact=country_name)
                except Country.DoesNotExist:
                    skipped_rows.append({'row': row_number, 'Reason': 'Country not found'})
                    continue

                try:
                    occupation_version_obj = OccupationVersion.objects.get(country=country_obj, occupation_version__iexact=occupation_version_name)
                except OccupationVersion.DoesNotExist:
                    skipped_rows.append({'row': row_number, 'Reason': 'Occupation version not found'})
                    continue

                try:
                    occupation_category_obj = OccupationCategory.objects.get(country=country_obj, occupation_version=occupation_version_obj, occupationcategory__iexact=occupation_category_name)
                except OccupationCategory.DoesNotExist:
                    skipped_rows.append({'row': row_number, 'Reason': 'Occupation category not found'})
                    continue

                try:
                    occupation_level_code_obj = OccupationLevelCode.objects.get(
                        country=country_obj,
                        occupation_version=occupation_version_obj,
                        occupationlevelcode__iexact=occupation_level_code_name
                    )
                except OccupationLevelCode.DoesNotExist:
                    skipped_rows.append({'row': row_number, 'Reason': 'Occupation level code not found'})
                    continue

                existing = OccupationLevel.objects.filter(
                    country=country_obj,
                    occupationversion=occupation_version_obj,
                    occupationcategory=occupation_category_obj,
                    occupationlevelcode=occupation_level_code_obj,
                    occupationlevel__iexact=occupation_level_name
                ).first()

                if existing:
                    if not existing.is_deleted:
                        duplicate_entries.append(f"{country_name}-{occupation_version_name}-{occupation_category_name}-{occupation_level_code_name}-{occupation_level_name}")
                        continue
                    else:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    OccupationLevel.objects.create(
                        country=country_obj,
                        occupationversion=occupation_version_obj,
                        occupationcategory=occupation_category_obj,
                        occupationlevelcode=occupation_level_code_obj,
                        occupationlevel=occupation_level_name,
                        description=description,
                        is_deleted=False
                    )
                    imported_count += 1

        except Exception as e:
            return Response({'error': str(e)}, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": list(set(duplicate_entries)),
            "skipped_rows": skipped_rows,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count
        }, status=200)





# -------------------- List -------------------- #
class OccupationCodeListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')
        allowed_sort_fields = ['occupationcode', 'created_at']

        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = OccupationCode.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(
                Q(occupationcode__istartswith=search) |
                Q(description__istartswith=search) |
                Q(country__country_name__istartswith=search) |
                Q(occupationversion__occupation_version__istartswith=search)
            )

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = OccupationCodeSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


# -------------------- Create -------------------- #
class OccupationCodeCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        country_uuid = request.data.get("country_id")
        occupationversion_uuid = request.data.get("occupationversion_id")
        occupationcode_name = request.data.get("occupationcode")

        if not occupationcode_name:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Mandatory field missing: occupationcode"
            }, status=400)

        # Validate foreign keys
        country_obj = None
        if country_uuid:
            try:
                country_obj = Country.objects.get(uuid=country_uuid)
            except Country.DoesNotExist:
                return Response({"statusCode": 400, "status": False, "message": "Invalid country UUID."}, status=400)

        occupationversion_obj = None
        if occupationversion_uuid:
            try:
                occupationversion_obj = OccupationVersion.objects.get(uuid=occupationversion_uuid)
            except OccupationVersion.DoesNotExist:
                return Response({"statusCode": 400, "status": False, "message": "Invalid occupation version UUID."}, status=400)

        # Check duplicate
        existing = OccupationCode.objects.filter(
            country=country_obj,
            occupationversion=occupationversion_obj,
            occupationcode__iexact=occupationcode_name,
            is_deleted=False
        ).first()

        if existing:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Occupation code already exists for this combination."
            }, status=400)

        data = request.data.copy()
        if country_obj:
            data['country_id'] = country_obj.uuid
        if occupationversion_obj:
            data['occupationversion_id'] = occupationversion_obj.uuid

        serializer = OccupationCodeSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Occupation code created successfully",
                "data": serializer.data
            })

        errors = " ".join([msg for msgs in serializer.errors.values() for msg in msgs])
        return Response({"statusCode": 400, "status": False, "message": errors}, status=400)


# -------------------- Retrieve -------------------- #
class OccupationCodeRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = OccupationCode.objects.get(uuid=uuid, is_deleted=False)
        except OccupationCode.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "Not found", "data": None}, status=404)

        serializer = OccupationCodeSerializer(obj)
        return Response({"statusCode": 200, "status": True, "message": "Retrieved successfully", "data": serializer.data})


# -------------------- Update -------------------- #
class OccupationCodeUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = OccupationCode.objects.get(uuid=uuid, is_deleted=False)
        except OccupationCode.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "Not found", "data": None}, status=404)

        serializer = OccupationCodeSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"statusCode": 200, "status": True, "message": "Updated successfully", "data": serializer.data})

        errors = " ".join([msg for msgs in serializer.errors.values() for msg in msgs])
        return Response({"statusCode": 400, "status": False, "message": errors}, status=400)


# -------------------- Delete -------------------- #
class OccupationCodeDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        ids = request.data.get('id', None)
        if not ids:
            return Response({"statusCode": 400, "status": False, "message": "Provide 'id' field", "data": None}, status=400)

        if ids == "all":
            objs = OccupationCode.objects.filter(is_deleted=False)
            count = objs.count()
            objs.delete()
            return Response({"statusCode": 200, "status": True, "message": f"All {count} record(s) deleted", "data": None})

        if not isinstance(ids, list):
            return Response({"statusCode": 400, "status": False, "message": "Provide list of UUIDs", "data": None}, status=400)

        valid_uuids, invalid_uuids = [], []
        for u in ids:
            try:
                valid_uuids.append(UUID(u))
            except ValueError:
                invalid_uuids.append(u)

        objs = OccupationCode.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = objs.count()
        if count == 0:
            return Response({"statusCode": 404, "status": False, "message": "No matching record found", "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None}, status=404)

        objs.delete()
        return Response({"statusCode": 200, "status": True, "message": f"{count} record(s) deleted", "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None})


# -------------------- Export -------------------- #
class OccupationCodeExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'country': 'Country',
            'occupationversion': 'Occupation Version',
            'occupationcode': 'Occupation Code',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'created_at': 'Created On',
            'updated_at': 'Modified On',
        }

        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())
        queryset = OccupationCode.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'Occupation Codes'

        for obj in queryset:
            row = []
            for field in field_list:
                value = getattr(obj, field, '')
                if field == 'country' and value:
                    value = value.country_name
                elif field == 'occupationversion' and value:
                    value = value.occupationversion
                elif field in ['created_at', 'updated_at'] and value:
                    value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
                elif isinstance(value, bool):
                    value = int(value)
                row.append(value if value is not None else '')
            dataset.append(row)

        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'occupation_codes.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'occupation_codes.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


# -------------------- Import -------------------- #
class OccupationCodeImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=400)

        format_type = file.name.split('.')[-1].lower()
        duplicate_entries = []
        skipped_rows = []
        required_headers = {'country', 'occupation version', 'occupation code'}
        optional_headers = {'description'}

        try:
            data = []

            # XLSX
            if format_type == 'xlsx':
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames
                if not sheet_name:
                    return Response({'error': 'Provide sheet_name', 'available_sheets': available_sheets}, status=400)
                if sheet_name not in available_sheets:
                    return Response({'error': f'Sheet "{sheet_name}" not found', 'available_sheets': available_sheets}, status=400)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({'error': f'Sheet "{sheet_name}" is empty.'}, status=400)

                headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                if not required_headers.issubset(set(headers)):
                    return Response({'error': f'Missing required headers. Required: {required_headers}, Found: {set(headers)}'}, status=400)

                for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    data.append((idx, row_dict))

            # CSV
            elif format_type == 'csv':
                dataset = Dataset()
                dataset.load(file.read().decode('utf-8'), format='csv')
                for idx, row in enumerate(dataset.dict, start=2):
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({'error': f'Missing required headers. Required: {required_headers}'}, status=400)
                    data.append((idx, row_lower))
            else:
                return Response({'error': 'Unsupported file format. Use .xlsx or .csv'}, status=400)

            imported_count = 0
            for row_number, row in data:
                country_name = str(row.get('country')).strip() if row.get('country') else None
                occupation_version_name = str(row.get('occupation version')).strip() if row.get('occupation version') else None
                occupation_code_name = str(row.get('occupation code')).strip() if row.get('occupation code') else None
                description = row.get('description', '')

                if not country_name or not occupation_version_name or not occupation_code_name:
                    skipped_rows.append({'row': row_number, 'Reason': 'Mandatory fields missing'})
                    continue

                try:
                    country_obj = Country.objects.get(country_name__iexact=country_name)
                except Country.DoesNotExist:
                    skipped_rows.append({'row': row_number, 'Reason': 'Country not found'})
                    continue

                try:
                    occupation_version_obj = OccupationVersion.objects.get(country=country_obj, occupation_version__iexact=occupation_version_name)
                except OccupationVersion.DoesNotExist:
                    skipped_rows.append({'row': row_number, 'Reason': 'Occupation version not found'})
                    continue

                existing = OccupationCode.objects.filter(
                    country=country_obj,
                    occupationversion=occupation_version_obj,
                    occupationcode__iexact=occupation_code_name
                ).first()

                if existing:
                    if not existing.is_deleted:
                        duplicate_entries.append(f"{country_name}-{occupation_version_name}-{occupation_code_name}")
                        continue
                    else:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    OccupationCode.objects.create(
                        country=country_obj,
                        occupationversion=occupation_version_obj,
                        occupationcode=occupation_code_name,
                        description=description,
                        is_deleted=False
                    )
                    imported_count += 1

        except Exception as e:
            return Response({'error': str(e)}, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": list(set(duplicate_entries)),
            "skipped_rows": skipped_rows,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count
        }, status=200)





class OccupationTypeListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['name', 'description', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = OccupationType.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(Q(name__istartswith=search))

        queryset = queryset.order_by(sort_by)

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = OccupationTypeSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)


# -------------------- CREATE API --------------------
class OccupationTypeCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        name = request.data.get("name", "").strip()
        if not name:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Name field is required."
            }, status=status.HTTP_400_BAD_REQUEST)

        existing = OccupationType.objects.filter(name__iexact=name, is_deleted=False).first()
        if existing:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "OccupationType with this name already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = OccupationTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "OccupationType created successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        else:
            errors = " ".join([str(msg) for msgs in serializer.errors.values() for msg in msgs])
            return Response({
                "statusCode": 400,
                "status": False,
                "message": errors
            }, status=status.HTTP_400_BAD_REQUEST)


# -------------------- RETRIEVE API --------------------
class OccupationTypeRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = OccupationType.objects.get(uuid=uuid, is_deleted=False)
        except OccupationType.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "OccupationType not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = OccupationTypeSerializer(obj)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "OccupationType retrieved successfully",
            "data": serializer.data
        })


# -------------------- UPDATE API --------------------
class OccupationTypeUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = OccupationType.objects.get(uuid=uuid, is_deleted=False)
        except OccupationType.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "OccupationType not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = OccupationTypeSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "OccupationType updated successfully",
                "data": serializer.data
            })

        errors = " ".join([str(msg) for msgs in serializer.errors.values() for msg in msgs])
        return Response({
            "statusCode": 400,
            "status": False,
            "message": errors,
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)


# -------------------- DELETE API --------------------
class OccupationTypeDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get('id', None)

        # Single delete
        if uuid:
            try:
                obj = OccupationType.objects.get(uuid=uuid)
                obj.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "OccupationType permanently deleted.",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            except OccupationType.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "OccupationType not found.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        # Delete all
        if ids == "all":
            objs = OccupationType.objects.all()
            count = objs.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No OccupationTypes found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
            objs.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} OccupationType(s) permanently deleted.",
                "data": None
            }, status=status.HTTP_200_OK)

        # Bulk delete
        if not ids or not isinstance(ids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide a list of UUIDs in 'id' field or 'all'.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        valid_uuids = []
        invalid_uuids = []
        for u in ids:
            try:
                valid_uuids.append(UUID(u))
            except ValueError:
                invalid_uuids.append(u)

        if not valid_uuids:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "No valid UUIDs provided.",
                "data": {"invalid_uuids": invalid_uuids}
            }, status=status.HTTP_400_BAD_REQUEST)

        objs = OccupationType.objects.filter(uuid__in=valid_uuids)
        count = objs.count()
        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching OccupationTypes found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_404_NOT_FOUND)

        objs.delete()
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} OccupationType(s) permanently deleted.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        }, status=status.HTTP_200_OK)


# -------------------- EXPORT API --------------------
class OccupationTypeExportAPIView(APIView):

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')

        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'name': 'Occupation Type',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'updated_at': 'Modified On',
        }

        if fields:
            field_list = [f.strip() for f in fields.split(',')]
        else:
            field_list = list(field_header_map.keys())

        queryset = OccupationType.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'OccupationType'

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
            file_name = 'occupation_types.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'occupation_types.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


# -------------------- IMPORT API --------------------
class OccupationTypeImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get("file")
        sheet_name = request.data.get("sheet_name")
        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split(".")[-1].lower()
        duplicates = []
        skipped_rows = []

        required_headers = {"occupation type"}
        optional_headers = {"description"}

        try:
            data = []

            if format_type == "xlsx":
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({"error": "Please provide sheet_name", "available_sheets": available_sheets}, status=400)
                if sheet_name not in available_sheets:
                    return Response({"error": f'Sheet "{sheet_name}" not found', "available_sheets": available_sheets}, status=400)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({"statusCode": 400, "status": False, "message": f'Sheet "{sheet_name}" is empty.'}, status=400)

                headers = [str(cell.value).strip().lower() if cell.value else "" for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                if not required_headers.issubset(set(headers)):
                    return Response({"statusCode": 400, "status": False, "message": f"Missing required headers. Required: {required_headers}, Found: {set(headers)}"}, status=400)

                for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row):
                        continue
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
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({"statusCode": 400, "status": False, "message": f"Missing required headers. Required: {', '.join(required_headers)}"}, status=400)
                    data.append(row_lower)
            else:
                return Response({"statusCode": 400, "status": False, "error": "Unsupported file format. Use .xlsx or .csv"}, status=400)

            imported_count = 0
            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")
                name = str(row.get("occupation type")).strip() if row.get("occupation type") else None
                description = str(row.get("description")).strip() if row.get("description") else ""

                if not name:
                    skipped_rows.append({"Row": row_number, "Reason": "Missing occupation type name"})
                    continue

                existing = OccupationType.objects.filter(name__iexact=name).first()
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({"Row": row_number, "Occupation Type": name, "Reason": "Already exists in database"})
                        continue
                    else:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    OccupationType.objects.create(name=name, description=description, is_deleted=False)
                    imported_count += 1

        except Exception as e:
            return Response({"statusCode": 400, "status": False, "message": str(e)}, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": duplicates,
            "skipped_rows": skipped_rows,
        }, status=200)
    


class OccupationProspectListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['name', 'description', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = OccupationProspect.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(Q(name__istartswith=search))

        queryset = queryset.order_by(sort_by)

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = OccupationProspectSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)


# -------------------- CREATE API --------------------
class OccupationProspectCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        name = request.data.get("name", "").strip()
        if not name:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Name field is required."
            }, status=status.HTTP_400_BAD_REQUEST)

        existing = OccupationProspect.objects.filter(name__iexact=name, is_deleted=False).first()
        if existing:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "OccupationProspect with this name already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = OccupationProspectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "OccupationProspect created successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        else:
            errors = " ".join([str(msg) for msgs in serializer.errors.values() for msg in msgs])
            return Response({
                "statusCode": 400,
                "status": False,
                "message": errors
            }, status=status.HTTP_400_BAD_REQUEST)


# -------------------- RETRIEVE API --------------------
class OccupationProspectRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = OccupationProspect.objects.get(uuid=uuid, is_deleted=False)
        except OccupationProspect.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "OccupationProspect not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = OccupationProspectSerializer(obj)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "OccupationProspect retrieved successfully",
            "data": serializer.data
        })


# -------------------- UPDATE API --------------------
class OccupationProspectUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = OccupationProspect.objects.get(uuid=uuid, is_deleted=False)
        except OccupationProspect.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "OccupationProspect not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = OccupationProspectSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "OccupationProspect updated successfully",
                "data": serializer.data
            })

        errors = " ".join([str(msg) for msgs in serializer.errors.values() for msg in msgs])
        return Response({
            "statusCode": 400,
            "status": False,
            "message": errors,
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)


# -------------------- DELETE API --------------------
class OccupationProspectDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get('id', None)

        # Single delete
        if uuid:
            try:
                obj = OccupationProspect.objects.get(uuid=uuid)
                obj.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "OccupationProspect permanently deleted.",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            except OccupationProspect.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "OccupationProspect not found.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        # Delete all
        if ids == "all":
            objs = OccupationProspect.objects.all()
            count = objs.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No OccupationProspects found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
            objs.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} OccupationProspect(s) permanently deleted.",
                "data": None
            }, status=status.HTTP_200_OK)

        # Bulk delete
        if not ids or not isinstance(ids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide a list of UUIDs in 'id' field or 'all'.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        valid_uuids = []
        invalid_uuids = []
        for u in ids:
            try:
                valid_uuids.append(UUID(u))
            except ValueError:
                invalid_uuids.append(u)

        if not valid_uuids:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "No valid UUIDs provided.",
                "data": {"invalid_uuids": invalid_uuids}
            }, status=status.HTTP_400_BAD_REQUEST)

        objs = OccupationProspect.objects.filter(uuid__in=valid_uuids)
        count = objs.count()
        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching OccupationProspects found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_404_NOT_FOUND)

        objs.delete()
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} OccupationProspect(s) permanently deleted.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        }, status=status.HTTP_200_OK)


# -------------------- EXPORT API --------------------
class OccupationProspectExportAPIView(APIView):

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')

        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'name': 'Occupation Prospect',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'updated_at': 'Modified On',
        }

        if fields:
            field_list = [f.strip() for f in fields.split(',')]
        else:
            field_list = list(field_header_map.keys())

        queryset = OccupationProspect.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'OccupationProspect'

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
            file_name = 'occupation_prospects.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'occupation_prospects.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


# -------------------- IMPORT API --------------------
class OccupationProspectImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get("file")
        sheet_name = request.data.get("sheet_name")
        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split(".")[-1].lower()
        duplicates = []
        skipped_rows = []

        required_headers = {"occupation prospect"}
        optional_headers = {"description"}

        try:
            data = []

            if format_type == "xlsx":
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({"error": "Please provide sheet_name", "available_sheets": available_sheets}, status=400)
                if sheet_name not in available_sheets:
                    return Response({"error": f'Sheet "{sheet_name}" not found', "available_sheets": available_sheets}, status=400)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({"statusCode": 400, "status": False, "message": f'Sheet "{sheet_name}" is empty.'}, status=400)

                headers = [str(cell.value).strip().lower() if cell.value else "" for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                if not required_headers.issubset(set(headers)):
                    return Response({"statusCode": 400, "status": False, "message": f"Missing required headers. Required: {required_headers}, Found: {set(headers)}"}, status=400)

                for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row):
                        continue
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
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({"statusCode": 400, "status": False, "message": f"Missing required headers. Required: {', '.join(required_headers)}"}, status=400)
                    data.append(row_lower)
            else:
                return Response({"statusCode": 400, "status": False, "error": "Unsupported file format. Use .xlsx or .csv"}, status=400)

            imported_count = 0
            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")
                name = str(row.get("occupation prospect")).strip() if row.get("occupation prospect") else None
                description = str(row.get("description")).strip() if row.get("description") else ""

                if not name:
                    skipped_rows.append({"Row": row_number, "Reason": "Missing occupation prospect name"})
                    continue

                existing = OccupationProspect.objects.filter(name__iexact=name).first()
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({"Row": row_number, "Occupation Prospect": name, "Reason": "Already exists in database"})
                        continue
                    else:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    OccupationProspect.objects.create(name=name, description=description, is_deleted=False)
                    imported_count += 1

        except Exception as e:
            return Response({"statusCode": 400, "status": False, "message": str(e)}, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": duplicates,
            "skipped_rows": skipped_rows,
        }, status=200)