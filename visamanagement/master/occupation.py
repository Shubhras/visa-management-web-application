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

    def delete(self, request):
        ids = request.data.get("id", None)
        delete_all = request.data.get("deleteAll", False)
        search = request.GET.get("search", "").strip()

        queryset = JobType.objects.filter(is_deleted=False)

        # ---------------------------------------------------
        # CASE 3: deleteAll = true AND search present → Search delete
        # ---------------------------------------------------
        if delete_all and search and (ids in [None, "", []]):
            qs_search = queryset.filter(name__istartswith=search)
            count = qs_search.count()

            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No job types found matching this search filter",
                    "data": None
                }, status=404)

            try:
                with transaction.atomic():
                    qs_search.delete()
            except IntegrityError:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "You can't delete selected job type(s) because they are used in child tables",
                    "data": None
                }, status=400)

            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"{count} job type(s) deleted based on search filter",
                "data": None
            }, status=200)

        # ---------------------------------------------------
        # CASE 2: deleteAll = false AND id = "all" → Delete full table
        # ---------------------------------------------------
        if ids == "all" and delete_all is False and search == "":
            qs_all = queryset
            count = qs_all.count()

            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No job types found to delete",
                    "data": None
                }, status=404)

            deleted, skipped = [], []

            for j in qs_all:
                try:
                    with transaction.atomic():
                        j.delete()
                    deleted.append(str(j.uuid))
                except IntegrityError:
                    skipped.append(j.name)

            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"Delete completed. {len(deleted)} deleted, {len(skipped)} skipped"
            }, status=200)

        # ---------------------------------------------------
        # CASE 1: deleteAll = false AND id = [UUID list] → Bulk delete
        # ---------------------------------------------------
        if delete_all is False and isinstance(ids, list):
            valid_uuids, invalid_uuids = [], []

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
                }, status=400)

            qs_ids = queryset.filter(uuid__in=valid_uuids)
            count = qs_ids.count()

            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No matching job types found for given ID list",
                    "data": None
                }, status=404)

            try:
                with transaction.atomic():
                    qs_ids.delete()
            except IntegrityError:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "One or more job type(s) are used in child tables, cannot delete.",
                    "data": None
                }, status=400)

            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"{count} job type(s) permanently deleted.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=200)

        # ---------------------------------------------------
        # INVALID FORMAT
        # ---------------------------------------------------
        return Response({
            "statusCode": 400,
            "status": False,
            "message": "Invalid delete request format",
            "data": None
        }, status=400)



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
            # ---------------- XLSX ----------------
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
                    if not any(row):
                        skipped_rows.append({"Row": idx, "Reason": "Empty row"})
                        continue
                    row_dict = dict(zip(headers, row))
                    row_dict["_row_number"] = idx
                    data.append(row_dict)

            # ---------------- CSV ----------------
            elif format_type == "csv":
                decoded_file = file.read().decode("utf-8")
                reader = csv.DictReader(io.StringIO(decoded_file))
                for idx, row in enumerate(reader, start=2):
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    row_lower["_row_number"] = idx
                    if not any(row_lower.values()):
                        skipped_rows.append({"Row": idx, "Reason": "Empty row"})
                        continue
                    data.append(row_lower)

            else:
                return Response({"message": "Unsupported file format"}, status=400)

            # ---------------- Process Rows ----------------
            to_create = []
            imported_count = 0
            existing_entries = JobType.objects.all()
            existing_map = {e.name.lower(): e for e in existing_entries}

            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")
                name = str(row.get("job type")).strip() if row.get("job type") else None
                description = str(row.get("description")).strip() if row.get("description") else ""

                if not name:
                    skipped_rows.append({"Row": row_number, "Job Type": name or "", "Description":description or "", "Reason": "Missing Job Type name"})
                    continue

                existing = existing_map.get(name.lower())
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({"Row": row_number, "Job Type": name,"Description":description or "", "Reason": "Already exists"})
                        continue
                    else:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    to_create.append(JobType(name=name, description=description))

            # Bulk insert
            if to_create:
                batch_size = 500
                for i in range(0, len(to_create), batch_size):
                    JobType.objects.bulk_create(to_create[i:i + batch_size])
                imported_count += len(to_create)

        except Exception as e:
            return Response({"message": str(e)}, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": list(reversed(duplicates)),
            "skipped_rows": list(reversed(skipped_rows)),
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

    def delete(self, request):
        ids = request.data.get("id", None)
        delete_all = request.data.get("deleteAll", False)
        search = request.GET.get("search", "").strip()

        queryset = ModeofSalary.objects.all()

        # ---------------------------------------------------
        # CASE 3: deleteAll = true AND search present → Delete only search filter data
        # ---------------------------------------------------
        if delete_all and search and (ids in [None, "", []]):
            qs_search = queryset.filter(name__istartswith=search)
            count = qs_search.count()

            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No records found matching this search filter.",
                    "data": None
                }, status=404)

            try:
                with transaction.atomic():
                    qs_search.delete()
            except IntegrityError:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Cannot delete because this record is used in child tables.",
                    "data": None
                }, status=400)

            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"{count} record(s) deleted based on search filter.",
                "data": None
            }, status=200)

        # ---------------------------------------------------
        # CASE 2: deleteAll = false AND id = "all" AND search empty → Delete full table
        # ---------------------------------------------------
        if ids == "all" and delete_all is False and search == "":
            qs_all = queryset
            count = qs_all.count()

            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No records found to delete.",
                    "data": None
                }, status=404)

            deleted, skipped = [], []

            for j in qs_all:
                try:
                    with transaction.atomic():
                        j.delete()
                    deleted.append(str(j.uuid))
                except IntegrityError:
                    skipped.append(j.name)

            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"Delete completed. {len(deleted)} deleted, {len(skipped)} skipped"
            }, status=200)

        # ---------------------------------------------------
        # CASE 1: deleteAll = false AND UUID list provided → Bulk delete by IDs
        # ---------------------------------------------------
        if delete_all is False and isinstance(ids, list):
            valid_uuids, invalid_uuids = [], []

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
                }, status=400)

            qs_ids = queryset.filter(uuid__in=valid_uuids)
            count = qs_ids.count()

            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No matching records found for given ID list.",
                    "data": None
                }, status=404)

            try:
                with transaction.atomic():
                    qs_ids.delete()
            except IntegrityError:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "One or more record(s) used in child tables, cannot delete.",
                    "data": None
                }, status=400)

            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"{count} record(s) permanently deleted.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=200)

        # ---------------------------------------------------
        # INVALID FORMAT FALLBACK
        # ---------------------------------------------------
        return Response({
            "statusCode": 400,
            "status": False,
            "message": "Invalid delete request format",
            "data": None
        }, status=400)
    

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
                    skipped_rows.append({"Row": row_number,"Mode Of Salary": name or "" ,"Description":description or "", "Reason": "Missing name"})
                    continue

                existing = ModeofSalary.objects.filter(name__iexact=name).first()
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({"Row": row_number, "Mode Of Salary": name,"Description":description or "", "Reason": "Already exists"})
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
            "duplicates": list(reversed(duplicates)),
            "skipped_rows": list(reversed(skipped_rows)),
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

    def delete(self, request):
        ids = request.data.get("id", None)
        delete_all = request.data.get("deleteAll", False)
        search = request.GET.get("search", "").strip()

        queryset = ITReturnStatus.objects.all()

        # ---------------------------------------------------
        # CASE 3: deleteAll = true AND search present → Delete only search filter data
        # ---------------------------------------------------
        if delete_all and search and (ids in [None, "", []]):
            qs_search = queryset.filter(name__istartswith=search)
            count = qs_search.count()

            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No records found matching this search filter.",
                    "data": None
                }, status=404)

            try:
                with transaction.atomic():
                    qs_search.delete()
            except IntegrityError:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Cannot delete because this record is used in child tables.",
                    "data": None
                }, status=400)

            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"{count} record(s) deleted based on search filter.",
                "data": None
            }, status=200)

        # ---------------------------------------------------
        # CASE 2: deleteAll = false AND id = "all" AND search empty → Delete full table
        # ---------------------------------------------------
        if ids == "all" and delete_all is False and search == "":
            qs_all = queryset
            count = qs_all.count()

            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No records found to delete.",
                    "data": None
                }, status=404)

            deleted, skipped = [], []

            for j in qs_all:
                try:
                    with transaction.atomic():
                        j.delete()
                    deleted.append(str(j.uuid))
                except IntegrityError:
                    skipped.append(j.name)

            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"Delete completed. {len(deleted)} deleted, {len(skipped)} skipped",
                "data": {"deleted": deleted, "not_deleted": skipped}
            }, status=200)

        # ---------------------------------------------------
        # CASE 1: deleteAll = false AND UUID list provided → Bulk delete by IDs
        # ---------------------------------------------------
        if delete_all is False and isinstance(ids, list):
            valid_uuids, invalid_uuids = [], []

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
                }, status=400)

            qs_ids = queryset.filter(uuid__in=valid_uuids)
            count = qs_ids.count()

            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No matching records found for given ID list.",
                    "data": None
                }, status=404)

            try:
                with transaction.atomic():
                    qs_ids.delete()
            except IntegrityError:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "One or more record(s) used in child tables, cannot delete.",
                    "data": None
                }, status=400)

            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"{count} record(s) permanently deleted.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=200)

        # ---------------------------------------------------
        # INVALID FORMAT FALLBACK
        # ---------------------------------------------------
        return Response({
            "statusCode": 400,
            "status": False,
            "message": "Invalid delete request format",
            "data": None
        }, status=400)
    

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
                    skipped_rows.append({"Row": row_number, "It Return Status": name or "", "Description":description or "", "Reason": "Missing name"})
                    continue

                existing = ITReturnStatus.objects.filter(name__iexact=name).first()
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({"Row": row_number, "It Return Status": name,"Description":description or "", "Reason": "Already exists"})
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
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": list(reversed(duplicates)),
            "skipped_rows": list(reversed(skipped_rows)),
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
            country_obj = RepresentingCountry.objects.get(uuid=country_uuid)
        except RepresentingCountry.DoesNotExist:
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

    def delete(self, request, uuid=None):
        ids = request.data.get('id', None)

        # Single delete via URL parameter
        
        if uuid:
            try:
                obj = OccupationVersion.objects.get(uuid=uuid, is_deleted=False)
                obj.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "OccupationVersion permanently deleted.",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            except OccupationVersion.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "OccupationVersion not found.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        # Delete all records
        if ids == "all":
            objs = OccupationVersion.objects.filter(is_deleted=False)
            count = objs.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No records found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
            objs.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} record(s) permanently deleted.",
                "data": None
            }, status=status.HTTP_200_OK)

        # Validate bulk UUIDs
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

        # Bulk delete
        objs = OccupationVersion.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = objs.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching records found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_404_NOT_FOUND)

        objs.delete()

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} record(s) permanently deleted.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        }, status=status.HTTP_200_OK)

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
                            value = getattr(value, 'full_name', getattr(value, 'name', str(value)))
                    elif field in ['created_at', 'updated_at'] and value:
                        value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
                    elif field in ['effect_from', 'valid_upto'] and value:
                        value = value.strftime("%d-%m-%Y")
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

            # Read XLSX
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
                    row_dict['_row_number'] = idx
                    data.append(row_dict)

            # Read CSV
            elif format_type == 'csv':
                dataset = Dataset()
                dataset.load(file.read().decode('utf-8'), format='csv')
                for idx, row in enumerate(dataset.dict, start=2):
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    row_lower['_row_number'] = idx
                    data.append(row_lower)
            else:
                return Response({'error': 'Unsupported file format. Use .xlsx or .csv'}, status=400)

            imported_count = 0
            bulk_objects = []

            for row in reversed(data):
                row_number = row.get('_row_number', 'Unknown')
                country_name = str(row.get('country')).strip() if row.get('country') else ""
                occupation_version = str(row.get('occupation version')).strip() if row.get('occupation version') else ""
                effect_from_str = row.get('start date')
                valid_upto_str = row.get('end date', None)
                description = row.get('description', '')

                try:
                    effect_from = datetime.strptime(effect_from_str, '%d-%m-%Y').date() if effect_from_str else None
                    valid_upto = datetime.strptime(valid_upto_str, '%d-%m-%Y').date() if valid_upto_str else None
                except Exception:
                    skipped_rows.append({
                        'Row': row_number,
                        'Country': country_name,
                        'Occupation Version': occupation_version,
                        'Start Date': effect_from_str or "",
                        'End Date': valid_upto_str or "",
                        'Description': description or "",
                        'Reason': 'Invalid date format'
                    })
                    continue

                if not country_name or not occupation_version or not effect_from:
                    skipped_rows.append({
                        'Row': row_number,
                        'Country': country_name,
                        'Occupation Version': occupation_version,
                        'Start Date': effect_from_str or "",
                        'End Date': valid_upto_str or "",
                        'Description': description or "",
                        'Reason': 'Mandatory fields missing'
                    })
                    continue

                country_obj = RepresentingCountry.objects.filter(full_name__iexact=country_name).first()
                if not country_obj:
                    skipped_rows.append({
                        'Row': row_number,
                        'Country': country_name,
                        'Occupation Version': occupation_version,
                        'Start Date': effect_from_str or "",
                        'End Date': valid_upto_str or "",
                        'Description': description or "",
                        'Reason': 'Country not found'
                    })
                    continue

                existing = OccupationVersion.objects.filter(
                    country=country_obj,
                    occupation_version__iexact=occupation_version,
                    effect_from=effect_from
                ).first()

                if existing:
                    if not existing.is_deleted:
                        duplicate_entries.append({
                            'Row': row_number,
                            'Country': country_name,
                            'Occupation Version': occupation_version,
                            'Start Date': effect_from_str or "",
                            'End Date': valid_upto_str or "",
                            'Description': description or "",
                            'Reason': 'Duplicate entry'
                        })
                        continue
                    else:
                        existing.valid_upto = valid_upto
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    # Add to bulk insert list
                    bulk_objects.append(
                        OccupationVersion(
                            country=country_obj,
                            occupation_version=occupation_version,
                            effect_from=effect_from,
                            valid_upto=valid_upto,
                            description=description,
                            is_deleted=False
                        )
                    )

            # Bulk create all new objects
            if bulk_objects:
                OccupationVersion.objects.bulk_create(bulk_objects)
                imported_count += len(bulk_objects)

        except Exception as e:
            return Response({'error': str(e)}, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": list(reversed(duplicate_entries)),
            "skipped_rows": list(reversed(skipped_rows)),
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
                country_obj = RepresentingCountry.objects.get(uuid=country_uuid)
            except RepresentingCountry.DoesNotExist:
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

        # Duplicate check
        existing = OccupationCategory.objects.filter(
            country=country_obj,
            occupationversion=occupation_version_obj,
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
            data['occupation_version_id'] = occupation_version_obj.uuid   # ✅ FIXED

        serializer = OccupationCategorySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Occupation category created successfully",
                "data": serializer.data
            })

        # Join all errors into a single message
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
                        value = value.full_name 
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
        duplicates, skipped_rows, data = [], [], []

        required_headers = {'country', 'occupation version', 'occupation category'}
        optional_headers = {'category code', 'description'}

        try:
            # ---------------- XLSX ----------------
            if format_type == 'xlsx':
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({'error': 'Provide sheet_name', 'available_sheets': available_sheets}, status=400)
                if sheet_name not in available_sheets:
                    return Response({'error': f'Sheet "{sheet_name}" not found', 'available_sheets': available_sheets}, status=400)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({'statusCode': 400, 'status': False, 'message': f'Sheet "{sheet_name}" is empty.'}, status=400)

                headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                if not required_headers.issubset(set(headers)):
                    return Response({'statusCode': 400, 'status': False, 'message': f"Missing required headers. Required: {required_headers}, Found: {set(headers)}"}, status=400)

                for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row):
                        skipped_rows.append({"Row": idx, "Reason": "Empty row"})
                        continue
                    row_dict = dict(zip(headers, row))
                    row_dict["_row_number"] = idx
                    data.append(row_dict)

            # ---------------- CSV ----------------
            elif format_type == 'csv':
                decoded_file = file.read().decode("utf-8")
                reader = csv.DictReader(io.StringIO(decoded_file))
                for idx, row in enumerate(reader, start=2):
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    row_lower["_row_number"] = idx
                    if not any(row_lower.values()):
                        skipped_rows.append({"Row": idx, "Reason": "Empty row"})
                        continue
                    data.append(row_lower)
            else:
                return Response({'statusCode': 400, 'status': False, 'error': 'Unsupported file format. Use .xlsx or .csv'}, status=400)

            # ---------------- Process Rows ----------------
            imported_count = 0
            to_create = []

            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")
                country_name = str(row.get('country')).strip() if row.get('country') else None
                occupation_version_name = str(row.get('occupation version')).strip() if row.get('occupation version') else None
                occupation_category_name = str(row.get('occupation category')).strip() if row.get('occupation category') else None
                category_code = row.get('category code', '')
                description = row.get('description', '')

                if not (country_name and occupation_version_name and occupation_category_name):
                    skipped_rows.append({'Row': row_number, 
                                         'Country': country_name  or "",
                                        'Occupation Version': occupation_version_name  or "",
                                        'Occupation Category': occupation_category_name  or "",
                                        'category code':category_code or "",
                                        'Description':description or "", 
                                        'Reason': 'Mandatory fields missing'})
                    continue

                country_obj = RepresentingCountry.objects.filter(full_name__iexact=country_name).first()
                if not country_obj:
                    skipped_rows.append({'Row': row_number,
                                        'Country': country_name  or "",
                                        'Occupation Version': occupation_version_name  or "",
                                        'Occupation Category': occupation_category_name  or "",
                                        'category code':category_code or "",
                                        'Description':description or "", 
                                        'Reason': 'Country not found'})
                    continue

                occupation_version_obj = OccupationVersion.objects.filter(
                    country=country_obj,
                    occupation_version__iexact=occupation_version_name
                ).first()
                if not occupation_version_obj:
                    skipped_rows.append({'Row': row_number,
                                         'Country': country_name  or "",
                                        'Occupation Version': occupation_version_name  or "",
                                        'Occupation Category': occupation_category_name  or "",
                                        'category code':category_code or "",
                                        'Description':description or "", 
                                        'Reason': 'Occupation version not found'})
                    continue

                existing = OccupationCategory.objects.filter(
                    country=country_obj,
                    occupation_version=occupation_version_obj,
                    occupationcategory__iexact=occupation_category_name
                ).first()

                if existing:
                    if not existing.is_deleted:
                        duplicates.append({
                            'Row': row_number,
                            'Country': country_name  or "",
                            'Occupation Version': occupation_version_name  or "",
                            'Occupation Category': occupation_category_name  or "",
                            'category code':category_code or "",
                            "Description":description or "",
                            'Reason': 'Duplicate entry'
                        })
                        continue
                    else:
                        existing.occupationcategorycode = category_code
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    to_create.append(OccupationCategory(
                        country=country_obj,
                        occupation_version=occupation_version_obj,
                        occupationcategory=occupation_category_name,
                        occupationcategorycode=category_code,
                        description=description,
                        is_deleted=False
                    ))

            # Bulk insert
            if to_create:
                batch_size = 500
                for i in range(0, len(to_create), batch_size):
                    OccupationCategory.objects.bulk_create(to_create[i:i+batch_size])
                imported_count += len(to_create)

        except Exception as e:
            return Response({'statusCode': 400, 'status': False, 'message': str(e)}, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": list(reversed(duplicates)),
            "skipped_rows": list(reversed(skipped_rows)),
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
                country_obj = RepresentingCountry.objects.get(uuid=country_uuid)
            except RepresentingCountry.DoesNotExist:
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
                occupationversion=occupation_version_obj,  # ✅ Correct
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
                    value = value.full_name
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

            # ------------------------------
            #  READ FILE
            # ------------------------------
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

                headers = [
                    str(cell.value).strip().lower() if cell.value else ''
                    for cell in next(ws.iter_rows(min_row=1, max_row=1))
                ]

                if not required_headers.issubset(set(headers)):
                    return Response(
                        {'error': f'Missing required headers. Required: {required_headers}, Found: {set(headers)}'},
                        status=400
                    )

                for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    row_dict["_row_number"] = idx
                    data.append(row_dict)

            elif format_type == 'csv':
                dataset = Dataset()
                dataset.load(file.read().decode('utf-8'), format='csv')

                for idx, row in enumerate(dataset.dict, start=2):
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    row_lower["_row_number"] = idx
                    data.append(row_lower)

            else:
                return Response({'error': 'Unsupported file format. Use .xlsx or .csv'}, status=400)

            # ------------------------------
            #  VALIDATION + BULK LIST
            # ------------------------------
            imported_count = 0
            bulk_objects = []   #  added for bulk insert

            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")

                # Extract with defaults
                country_name = str(row.get('country') or "").strip()
                occupation_version_name = str(row.get('occupation version') or "").strip()
                occupationlevelcode = str(row.get('occupation level code') or "").strip()
                description = row.get('description') or ""

                # Mandatory
                if not country_name or not occupation_version_name or not occupationlevelcode:
                    skipped_rows.append({
                        'Row': row_number,
                        'Country': country_name,
                        'Occupation Version': occupation_version_name,
                        'Occupation Level Code': occupationlevelcode,
                        'Description': description,
                        'Reason': 'Mandatory fields missing'
                    })
                    continue

                # Country
                country_obj = RepresentingCountry.objects.filter(full_name__iexact=country_name).first()
                if not country_obj:
                    skipped_rows.append({
                        'Row': row_number,
                        'Country': country_name,
                        'Occupation Version': occupation_version_name,
                        'Occupation Level Code': occupationlevelcode,
                        'Description': description,
                        'Reason': 'Country not found'
                    })
                    continue

                # Occupation Version
                occupation_version_obj = OccupationVersion.objects.filter(
                    country=country_obj,
                    occupation_version__iexact=occupation_version_name
                ).first()

                if not occupation_version_obj:
                    skipped_rows.append({
                        'Row': row_number,
                        'Country': country_name,
                        'Occupation Version': occupation_version_name,
                        'Occupation Level Code': occupationlevelcode,
                        'Description': description,
                        'Reason': 'Occupation version not found'
                    })
                    continue

                # Existing check
                existing = OccupationLevelCode.objects.filter(
                    country=country_obj,
                    occupation_version=occupation_version_obj,
                    occupationlevelcode__iexact=occupationlevelcode
                ).first()

                if existing:
                    if not existing.is_deleted:
                        duplicate_entries.append({
                            'Row': row_number,
                            'Country': country_name,
                            'Occupation Version': occupation_version_name,
                            'Occupation Level Code': occupationlevelcode,
                            'Description': description,
                            'Reason': 'Duplicate entry'
                        })
                        continue
                    else:
                        # revive deleted record
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                        continue

                # ------------------------------
                # ⭐ Add NEW row to bulk insert
                # ------------------------------
                bulk_objects.append(
                    OccupationLevelCode(
                        country=country_obj,
                        occupation_version=occupation_version_obj,
                        occupationlevelcode=occupationlevelcode,
                        description=description,
                        is_deleted=False
                    )
                )

            # ------------------------------
            # 📌 FINAL BULK CREATE
            # ------------------------------
            if bulk_objects:
                OccupationLevelCode.objects.bulk_create(bulk_objects)
                imported_count += len(bulk_objects)

        except Exception as e:
            return Response({'error': str(e)}, status=400)

        # ------------------------------
        # 📌 RESPONSE (with reversed order)
        # ------------------------------
        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": list(reversed(duplicate_entries)),
            "skipped_rows": list(reversed(skipped_rows)),
            "message": f'Sheet \"{sheet_name}\" imported successfully' if sheet_name else "Import successful",
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
                Q(occupationlevel__istartswith=search) 
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
                country_obj = RepresentingCountry.objects.get(uuid=country_uuid)
            except RepresentingCountry.DoesNotExist:
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
                    value = value.full_name
                elif field == 'occupationversion' and value:
                    value = value.occupation_version
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
        bulk_new_objects = []

        required_headers = {
            'country', 'occupation version', 'occupation category',
            'occupation level code', 'occupation level'
        }

        try:
            data = []

            # ---------- XLSX ----------
            if format_type == 'xlsx':
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({'error': 'Provide sheet_name', 'available_sheets': available_sheets}, status=400)
                if sheet_name not in available_sheets:
                    return Response({'error': f'Sheet "{sheet_name}" not found', 'available_sheets': available_sheets}, status=400)

                ws = wb[sheet_name]

                headers = [
                    str(c.value).strip().lower() if c.value else ""
                    for c in next(ws.iter_rows(min_row=1, max_row=1))
                ]

                if not required_headers.issubset(headers):
                    return Response({'error': f'Missing required headers. Required: {required_headers}'}, status=400)

                for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    row_dict["_row_number"] = idx
                    data.append(row_dict)

            # ---------- CSV ----------
            elif format_type == 'csv':
                dataset = Dataset()
                dataset.load(file.read().decode('utf-8'), format='csv')

                for idx, row in enumerate(dataset.dict, start=2):
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    row_lower["_row_number"] = idx
                    data.append(row_lower)

            else:
                return Response({'error': 'Unsupported file format'}, status=400)

            imported_count = 0

            # ------------------------------------------------------------------
            # PROCESS FROM BOTTOM TO TOP
            # ------------------------------------------------------------------
            for row in reversed(data):

                row_number = row.get("_row_number", "Unknown")

                # Extract & normalize fields
                country_name = str(row.get('country') or "").strip()
                occupation_version_name = str(row.get('occupation version') or "").strip()
                occupation_category_name = str(row.get('occupation category') or "").strip()
                occupation_level_code_name = str(row.get('occupation level code') or "").strip()
                occupation_level_name = str(row.get('occupation level') or "").strip()
                description = row.get('description') or ""

                # Check mandatory
                if not (country_name and occupation_version_name and occupation_category_name and occupation_level_code_name and occupation_level_name):
                    skipped_rows.append({
                        'Row': row_number,
                        'Country': country_name,
                        'Occupation Version': occupation_version_name,
                        'Occupation Category': occupation_category_name,
                        'Occupation Level Code': occupation_level_code_name,
                        'Occupation Level': occupation_level_name,
                        'Description': description,
                        'Reason': 'Mandatory fields missing'
                    })
                    continue

                # Country
                country_obj = RepresentingCountry.objects.filter(full_name__iexact=country_name).first()
                if not country_obj:
                    skipped_rows.append({
                        'Row': row_number,
                        'Country': country_name,
                        'Occupation Version': occupation_version_name,
                        'Occupation Category': occupation_category_name,
                        'Occupation Level Code': occupation_level_code_name,
                        'Occupation Level': occupation_level_name,
                        'Description': description,
                        'Reason': 'Country not found'
                    })
                    continue

                # Version
                occupation_version_obj = OccupationVersion.objects.filter(
                    country=country_obj,
                    occupation_version__iexact=occupation_version_name
                ).first()
                if not occupation_version_obj:
                    skipped_rows.append({
                        'Row': row_number,
                        'Country': country_name,
                        'Occupation Version': occupation_version_name,
                        'Occupation Category': occupation_category_name,
                        'Occupation Level Code': occupation_level_code_name,
                        'Occupation Level': occupation_level_name,
                        'Description': description,
                        'Reason': 'Occupation version not found'
                    })
                    continue

                # Category
                occupation_category_obj = OccupationCategory.objects.filter(
                    country=country_obj,
                    occupation_version=occupation_version_obj,
                    occupationcategory__iexact=occupation_category_name
                ).first()
                if not occupation_category_obj:
                    skipped_rows.append({
                        'Row': row_number,
                        'Country': country_name,
                        'Occupation Version': occupation_version_name,
                        'Occupation Category': occupation_category_name,
                        'Occupation Level Code': occupation_level_code_name,
                        'Occupation Level': occupation_level_name,
                        'Description': description,
                        'Reason': 'Occupation category not found'
                    })
                    continue

                # Level Code
                occupation_level_code_obj = OccupationLevelCode.objects.filter(
                    country=country_obj,
                    occupation_version=occupation_version_obj,
                    occupationlevelcode__iexact=occupation_level_code_name
                ).first()
                if not occupation_level_code_obj:
                    skipped_rows.append({
                        'Row': row_number,
                        'Country': country_name,
                        'Occupation Version': occupation_version_name,
                        'Occupation Category': occupation_category_name,
                        'Occupation Level Code': occupation_level_code_name,
                        'Occupation Level': occupation_level_name,
                        'Description': description,
                        'Reason': 'Occupation level code not found'
                    })
                    continue

                # Check existing
                existing = OccupationLevel.objects.filter(
                    country=country_obj,
                    occupationversion=occupation_version_obj,
                    occupationcategory=occupation_category_obj,
                    occupationlevelcode=occupation_level_code_obj,
                    occupationlevel__iexact=occupation_level_name
                ).first()

                if existing:
                    if not existing.is_deleted:
                        duplicate_entries.append({
                            'Row': row_number,
                            'Country': country_name,
                            'Occupation Version': occupation_version_name,
                            'Occupation Category': occupation_category_name,
                            'Occupation Level Code': occupation_level_code_name,
                            'Occupation Level': occupation_level_name,
                            'Description': description,
                            'Reason': 'Duplicate entry'
                        })
                        continue

                    # revive deleted record
                    existing.description = description
                    existing.is_deleted = False
                    existing.save()
                    imported_count += 1
                    continue

                # NEW → Add to bulk list
                bulk_new_objects.append(
                    OccupationLevel(
                        country=country_obj,
                        occupationversion=occupation_version_obj,
                        occupationcategory=occupation_category_obj,
                        occupationlevelcode=occupation_level_code_obj,
                        occupationlevel=occupation_level_name,
                        description=description,
                        is_deleted=False
                    )
                )

            # -----------------------
            # BULK CREATE
            # -----------------------
            if bulk_new_objects:
                OccupationLevel.objects.bulk_create(bulk_new_objects)
                imported_count += len(bulk_new_objects)

        except Exception as e:
            return Response({'error': str(e)}, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": list(reversed(duplicate_entries)),
            "skipped_rows": list(reversed(skipped_rows)),
            "imported_count": imported_count,
            "message": f'Sheet \"{sheet_name}\" imported successfully'
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
                country_obj = RepresentingCountry.objects.get(uuid=country_uuid)
            except RepresentingCountry.DoesNotExist:
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
                    value = value.full_name
                elif field == 'occupationversion' and value:
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
        bulk_new_objects = []

        required_headers = {'country', 'occupation version', 'occupation code'}

        try:
            data = []

            # ---------- XLSX ----------
            if format_type == 'xlsx':
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({'error': 'Provide sheet_name', 'available_sheets': available_sheets}, status=400)
                if sheet_name not in available_sheets:
                    return Response({'error': f'Sheet "{sheet_name}" not found', 'available_sheets': available_sheets}, status=400)

                ws = wb[sheet_name]
                headers = [str(c.value).strip().lower() if c.value else "" for c in next(ws.iter_rows(min_row=1, max_row=1))]

                if not required_headers.issubset(headers):
                    return Response({'error': f'Missing required headers. Required: {required_headers}'}, status=400)

                for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    row_dict["_row_number"] = idx
                    data.append(row_dict)

            # ---------- CSV ----------
            elif format_type == 'csv':
                dataset = Dataset()
                dataset.load(file.read().decode('utf-8'), format='csv')

                for idx, row in enumerate(dataset.dict, start=2):
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    row_lower["_row_number"] = idx
                    data.append(row_lower)

            else:
                return Response({'error': 'Unsupported file format'}, status=400)

            imported_count = 0

            # --------------------------
            # PROCESS FROM BOTTOM TO TOP
            # --------------------------
            for row in reversed(data):

                row_number = row.get("_row_number", "Unknown")
                country_name = str(row.get('country') or "").strip()
                occupation_version_name = str(row.get('occupation version') or "").strip()
                occupation_code_name = str(row.get('occupation code') or "").strip()
                description = row.get('description') or ""

                # Mandatory fields
                if not (country_name and occupation_version_name and occupation_code_name):
                    skipped_rows.append({
                        'Row': row_number,
                        'Country': country_name,
                        'Occupation Version': occupation_version_name,
                        'Occupation Code': occupation_code_name,
                        'Description': description,
                        'Reason': 'Mandatory fields missing'
                    })
                    continue

                # Country
                country_obj = RepresentingCountry.objects.filter(full_name__iexact=country_name).first()
                if not country_obj:
                    skipped_rows.append({
                        'Row': row_number,
                        'Country': country_name,
                        'Occupation Version': occupation_version_name,
                        'Occupation Code': occupation_code_name,
                        'Description': description,
                        'Reason': 'Country not found'
                    })
                    continue

                # Occupation Version
                occupation_version_obj = OccupationVersion.objects.filter(
                    country=country_obj,
                    occupation_version__iexact=occupation_version_name
                ).first()
                if not occupation_version_obj:
                    skipped_rows.append({
                        'Row': row_number,
                        'Country': country_name,
                        'Occupation Version': occupation_version_name,
                        'Occupation Code': occupation_code_name,
                        'Description': description,
                        'Reason': 'Occupation version not found'
                    })
                    continue

                # Check existing
                existing = OccupationCode.objects.filter(
                    country=country_obj,
                    occupationversion=occupation_version_obj,
                    occupationcode__iexact=occupation_code_name
                ).first()

                if existing:
                    if not existing.is_deleted:
                        duplicate_entries.append({
                            'Row': row_number,
                            'Country': country_name,
                            'Occupation Version': occupation_version_name,
                            'Occupation Code': occupation_code_name,
                            'Description': description,
                            'Reason': 'Duplicate entry'
                        })
                        continue

                    # Revive deleted record
                    existing.description = description
                    existing.is_deleted = False
                    existing.save()
                    imported_count += 1
                    continue

                # NEW → Add to bulk list
                bulk_new_objects.append(
                    OccupationCode(
                        country=country_obj,
                        occupationversion=occupation_version_obj,
                        occupationcode=occupation_code_name,
                        description=description,
                        is_deleted=False
                    )
                )

            # BULK CREATE
            if bulk_new_objects:
                OccupationCode.objects.bulk_create(bulk_new_objects)
                imported_count += len(bulk_new_objects)

        except Exception as e:
            return Response({'error': str(e)}, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": list(reversed(duplicate_entries)),
            "skipped_rows": list(reversed(skipped_rows)),
            "imported_count": imported_count,
            "message": f'Sheet "{sheet_name}" imported successfully'
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
        ids = request.data.get("id", None)
        delete_all = request.data.get("deleteAll", False)
        search = request.GET.get("search", "").strip()

        queryset = OccupationType.objects.all()

        # ---------------------------------------------------
        # CASE 3: deleteAll = true AND search present → Delete only search filter data
        # ---------------------------------------------------
        if delete_all and search and (ids in [None, "", []]):
            qs_search = queryset.filter(name__istartswith=search)
            count = qs_search.count()

            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No records found matching this search filter.",
                    "data": None
                }, status=404)

            try:
                with transaction.atomic():
                    qs_search.delete()
            except IntegrityError:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Cannot delete because this record is used in child tables.",
                    "data": None
                }, status=400)

            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"{count} record(s) deleted based on search filter.",
                "data": None
            }, status=200)

        # ---------------------------------------------------
        # CASE 2: deleteAll = false AND id = "all" AND search empty → Delete full table
        # ---------------------------------------------------
        if ids == "all" and delete_all is False and search == "":
            qs_all = queryset
            count = qs_all.count()

            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No OccupationTypes found to delete.",
                    "data": None
                }, status=404)

            deleted, skipped = [], []

            for obj in qs_all:
                try:
                    with transaction.atomic():
                        obj.delete()
                    deleted.append(str(obj.uuid))
                except IntegrityError:
                    skipped.append(obj.name)

            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"Delete completed. {len(deleted)} deleted, {len(skipped)} skipped",
                "data": {"deleted": deleted, "not_deleted": skipped}
            }, status=200)

        # ---------------------------------------------------
        # CASE 1: deleteAll = false AND UUID list provided → Bulk delete by IDs
        # ---------------------------------------------------
        if delete_all is False and isinstance(ids, list):
            valid_uuids, invalid_uuids = [], []

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
                }, status=400)

            qs_ids = queryset.filter(uuid__in=valid_uuids)
            count = qs_ids.count()

            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No matching OccupationTypes found for given ID list.",
                    "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
                }, status=404)

            try:
                with transaction.atomic():
                    qs_ids.delete()
            except IntegrityError:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "One or more record(s) used in child tables, cannot delete.",
                    "data": None
                }, status=400)

            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"{count} OccupationType(s) permanently deleted.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=200)

        # ---------------------------------------------------
        # Delete by single UUID in URL (optional)
        # ---------------------------------------------------
        if uuid:
            try:
                obj = queryset.get(uuid=uuid)
                try:
                    with transaction.atomic():
                        obj.delete()
                except IntegrityError:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": "Cannot delete because this record is used in child tables.",
                        "data": None
                    }, status=400)

                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "OccupationType permanently deleted.",
                    "data": None
                }, status=204)

            except OccupationType.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "OccupationType not found.",
                    "data": None
                }, status=404)

        # ---------------------------------------------------
        # INVALID FORMAT FALLBACK
        # ---------------------------------------------------
        return Response({
            "statusCode": 400,
            "status": False,
            "message": "Invalid delete request format",
            "data": None
        }, status=400)
    
    

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
                    skipped_rows.append({"Row": row_number, "Occupation Type": name or "", "Description":description or "", "Reason": "Missing occupation type name"})
                    continue

                existing = OccupationType.objects.filter(name__iexact=name).first()
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({"Row": row_number, "Occupation Type": name, "Description":description or "", "Reason": "Already exists in database"})
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
            "duplicates": list(reversed(duplicates)),
            "skipped_rows": list(reversed(skipped_rows)),
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
            return Response({ "statusCode": 400, "status": False,"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split(".")[-1].lower()
        duplicates, skipped_rows, data = [], [], []

        required_headers = {"occupation prospect"}
        optional_headers = {"description"}

        try:
            # ---------------- XLSX ----------------
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

                headers = [str(c.value).strip().lower() if c.value else "" for c in next(ws.iter_rows(min_row=1, max_row=1))]
                if not required_headers.issubset(set(headers)):
                    return Response({"statusCode": 400, "status": False, "message": f"Missing required headers. Required: {required_headers}, Found: {set(headers)}"}, status=400)

                for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row):
                        skipped_rows.append({"Row": idx, "Reason": "Empty row"})
                        continue
                    row_dict = dict(zip(headers, row))
                    row_dict["_row_number"] = idx
                    data.append(row_dict)

            # ---------------- CSV ----------------
            elif format_type == "csv":
                decoded_file = file.read().decode("utf-8")
                reader = csv.DictReader(io.StringIO(decoded_file))
                for idx, row in enumerate(reader, start=2):
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    row_lower["_row_number"] = idx
                    if not any(row_lower.values()):
                        skipped_rows.append({"Row": idx, "Reason": "Empty row"})
                        continue
                    data.append(row_lower)
            else:
                return Response({"statusCode": 400, "status": False, "error": "Unsupported file format. Use .xlsx or .csv"}, status=400)

            # ---------------- Process Rows ----------------
            to_create = []
            imported_count = 0
            existing_entries = OccupationProspect.objects.all()
            existing_map = {e.name.lower(): e for e in existing_entries}

            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")
                name = str(row.get("occupation prospect")).strip() if row.get("occupation prospect") else None
                description = str(row.get("description")).strip() if row.get("description") else ""

                if not name:
                    skipped_rows.append({"Row": row_number,"Occupation Prospect": name or "","Description":description or "", "Reason": "Missing occupation prospect name"})
                    continue

                existing = existing_map.get(name.lower())
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({"Row": row_number, "Occupation Prospect": name,"Description":description or "", "Reason": "Already exists in database"})
                        continue
                    else:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    to_create.append(OccupationProspect(name=name, description=description, is_deleted=False))

            # Bulk insert
            if to_create:
                batch_size = 500
                for i in range(0, len(to_create), batch_size):
                    OccupationProspect.objects.bulk_create(to_create[i:i + batch_size])
                imported_count += len(to_create)

        except Exception as e:
            return Response({"statusCode": 400, "status": False, "message": str(e)}, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": list(reversed(duplicates)),
            "skipped_rows": list(reversed(skipped_rows)),
        }, status=200)

class JobProspectListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')
        allowed_sort_fields = ['occupationname', 'created_at', 'salaryamount']

        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = JobProspect.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(
                Q(occupationname__istartswith=search) |
                Q(country__country_name__istartswith=search) |
                Q(occupationversion__occupation_version__istartswith=search) |
                Q(occupationlevelcode__occupationlevelcode__istartswith=search) |
                Q(occupationtype__name__istartswith=search) |
                Q(occupationcode__occupationcode__istartswith=search) |
                Q(occupationprospect__name__istartswith=search)
            )

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = JobProspectSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


# -------------------- Create -------------------- #
class JobProspectCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        serializer = JobProspectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Job prospect created successfully",
                "data": serializer.data
            })
        errors = " ".join([msg for msgs in serializer.errors.values() for msg in msgs])
        return Response({"statusCode": 400, "status": False, "message": errors}, status=400)


# -------------------- Retrieve -------------------- #
class JobProspectRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = JobProspect.objects.get(uuid=uuid, is_deleted=False)
        except JobProspect.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "Not found", "data": None}, status=404)

        serializer = JobProspectSerializer(obj)
        return Response({"statusCode": 200, "status": True, "message": "Retrieved successfully", "data": serializer.data})


# -------------------- Update -------------------- #
class JobProspectUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = JobProspect.objects.get(uuid=uuid, is_deleted=False)
        except JobProspect.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "Not found", "data": None}, status=404)

        serializer = JobProspectSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"statusCode": 200, "status": True, "message": "Updated successfully", "data": serializer.data})

        errors = " ".join([msg for msgs in serializer.errors.values() for msg in msgs])
        return Response({"statusCode": 400, "status": False, "message": errors}, status=400)


# -------------------- Delete -------------------- #
class JobProspectDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        ids = request.data.get('id', None)
        if not ids:
            return Response({"statusCode": 400, "status": False, "message": "Provide 'id' field", "data": None}, status=400)

        if ids == "all":
            objs = JobProspect.objects.filter(is_deleted=False)
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

        objs = JobProspect.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = objs.count()
        if count == 0:
            return Response({"statusCode": 404, "status": False, "message": "No matching record found", "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None}, status=404)

        objs.delete()
        return Response({"statusCode": 200, "status": True, "message": f"{count} record(s) deleted", "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None})


# -------------------- Export -------------------- #
class JobProspectExportAPIView(APIView):
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
            'occupationlevelcode': 'Occupation Level Code',
            'occupationtype': 'Occupation Type',
            'occupationcode': 'Occupation Code',
            'occupationprospect': 'Occupation Prospect',
            'occupationname': 'Occupation Name',
            'salarycurrency': 'Salary Currency',
            'salaryamount': 'Salary Amount',
            'duration': 'Duration',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'created_at': 'Created On',
            'updated_at': 'Modified On',
        }

        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())
        queryset = JobProspect.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'Job Prospects'

        for obj in queryset:
            row = []
            for field in field_list:
                value = getattr(obj, field, '')
                if field in ['country', 'occupationversion', 'occupationlevelcode', 'occupationtype', 'occupationcode', 'occupationprospect'] and value:
                    value = str(value)
                elif field in ['created_at', 'updated_at'] and value:
                    value = timezone.localtime(value).strftime("%d-%m-%Y %I:%M:%S %p")
                elif isinstance(value, bool):
                    value = int(value)
                row.append(value if value is not None else '')
            dataset.append(row)

        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'job_prospects.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'job_prospects.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


# -------------------- Import -------------------- #
# class JobProspectImportAPIView(APIView):
#     permission_classes = [IsAuthenticated, IsAdminUser]

#     def post(self, request):
#         file = request.FILES.get('file')
#         sheet_name = request.data.get('sheet_name')

#         if not file:
#             return Response({'error': 'No file uploaded'}, status=400)

#         format_type = file.name.split('.')[-1].lower()
#         duplicate_entries = []
#         skipped_rows = []
#         required_headers = {'country', 'occupation version', 'occupation level code', 'occupation type', 'occupation code', 'occupation prospect', 'occupation name'}
#         optional_headers = {'salarycurrency', 'salaryamount', 'duration', 'description'}

#         try:
#             data = []

#             # XLSX
#             if format_type == 'xlsx':
#                 wb = openpyxl.load_workbook(file, read_only=True)
#                 available_sheets = wb.sheetnames
#                 if not sheet_name:
#                     return Response({'error': 'Provide sheet_name', 'available_sheets': available_sheets}, status=400)
#                 if sheet_name not in available_sheets:
#                     return Response({'error': f'Sheet "{sheet_name}" not found', 'available_sheets': available_sheets}, status=400)

#                 ws = wb[sheet_name]
#                 if ws.max_row <= 1:
#                     return Response({'error': f'Sheet "{sheet_name}" is empty.'}, status=400)

#                 headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]
#                 if not required_headers.issubset(set(headers)):
#                     return Response({'error': f'Missing required headers. Required: {required_headers}, Found: {set(headers)}'}, status=400)

#                 for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
#                     if not any(row):
#                         continue
#                     row_dict = dict(zip(headers, row))
#                     data.append((idx, row_dict))

#             # CSV
#             elif format_type == 'csv':
#                 dataset = Dataset()
#                 dataset.load(file.read().decode('utf-8'), format='csv')
#                 for idx, row in enumerate(dataset.dict, start=2):
#                     row_lower = {k.strip().lower(): v for k, v in row.items()}
#                     if not required_headers.issubset(set(row_lower.keys())):
#                         return Response({'error': f'Missing required headers. Required: {required_headers}'}, status=400)
#                     data.append((idx, row_lower))
#             else:
#                 return Response({'error': 'Unsupported file format. Use .xlsx or .csv'}, status=400)

#             imported_count = 0
#             VALID_UNIT_CHOICES = ("Hour", "Month", "Year")
#             for row_number, row in data:
#                 try:
#                     country_obj = Country.objects.get(country_name__iexact=row.get('country'))
#                     occupationversion_obj = OccupationVersion.objects.get(country=country_obj, occupation_version__iexact=row.get('occupation version'))
#                     occupationlevelcode_obj = OccupationLevelCode.objects.get(country=country_obj, occupationlevelcode__iexact=row.get('occupation level code'))
#                     occupationtype_obj = OccupationType.objects.get(name__iexact=row.get('occupation type'))
#                     occupationcode_obj = OccupationCode.objects.get(occupationcode__iexact=row.get('occupation code'))
#                     occupationprospect_obj = OccupationProspect.objects.get(name__iexact=row.get('occupation prospect'))
#                 except (Country.DoesNotExist, OccupationVersion.DoesNotExist, OccupationLevelCode.DoesNotExist, OccupationType.DoesNotExist, OccupationCode.DoesNotExist, OccupationProspect.DoesNotExist):
#                     skipped_rows.append({'row': row_number, 'Reason': 'Foreign key not found'})
#                     continue

                

#                 occupation_name = row.get('occupation name')
#                 duration = row.get('duration')
#                 if not occupation_name:
#                     skipped_rows.append({'row': row_number, 'Reason': 'Mandatory fields missing'})
#                     continue
                
#                 if duration and duration not in VALID_UNIT_CHOICES:
#                     skipped_rows.append({'row': row_number, 'Reason': f'Invalid duration: {duration}. Allowed: {VALID_UNIT_CHOICES}'})
#                     continue

#                 existing = JobProspect.objects.filter(
#                     country=country_obj,
#                     occupationversion=occupationversion_obj,
#                     occupationlevelcode=occupationlevelcode_obj,
#                     occupationtype=occupationtype_obj,
#                     occupationcode=occupationcode_obj,
#                     occupationprospect=occupationprospect_obj,
#                     occupationname__iexact=occupation_name
#                 ).first()

#                 if existing:
#                     if not existing.is_deleted:
#                         duplicate_entries.append({
#                             "row": row_number,
#                             "Occupation Name": occupation_name,
#                             "Country": country_obj.country_name,
#                             "Occupation Version": occupationversion_obj.occupation_version
#                         })
#                         continue
#                     else:
#                         existing.is_deleted = False
#                         existing.save()
#                         imported_count += 1
#                 else:
#                     JobProspect.objects.create(
#                         country=country_obj,
#                         occupationversion=occupationversion_obj,
#                         occupationlevelcode=occupationlevelcode_obj,
#                         occupationtype=occupationtype_obj,
#                         occupationcode=occupationcode_obj,
#                         occupationprospect=occupationprospect_obj,
#                         occupationname=occupation_name,
#                         salarycurrency=row.get('salarycurrency'),
#                         salaryamount=row.get('salaryamount'),
#                         duration=row.get('duration'),
#                         description=row.get('description', ''),
#                         is_deleted=False
#                     )
#                     imported_count += 1

#         except Exception as e:
#             return Response({'error': str(e)}, status=400)

#         return Response({
#             "statusCode": 200,
#             "status": True,
#             "duplicates": list(set(duplicate_entries)),
#             "skipped_rows": skipped_rows,
#             "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
#             "imported_count": imported_count
#         }, status=200)

class JobProspectImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=400)

        format_type = file.name.split('.')[-1].lower()
        duplicate_entries = []
        skipped_rows = []
        required_headers = {
            'country', 'occupation version', 'occupation level code',
            'occupation type', 'occupation code', 'occupation prospect', 'occupation name'
        }
        optional_headers = {'salarycurrency', 'salaryamount', 'duration', 'description'}

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
                    row_dict["_row_number"] = idx
                    data.append(row_dict)

            # CSV
            elif format_type == 'csv':
                dataset = Dataset()
                dataset.load(file.read().decode('utf-8'), format='csv')
                for idx, row in enumerate(dataset.dict, start=2):
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({'error': f'Missing required headers. Required: {required_headers}'}, status=400)
                    row_lower["_row_number"] = idx
                    data.append(row_lower)
            else:
                return Response({'error': 'Unsupported file format. Use .xlsx or .csv'}, status=400)

            imported_count = 0
            VALID_UNIT_CHOICES = ("Hour", "Month", "Year")

            # Process rows from bottom to top
            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")
                country_name = str(row.get('country') or "").strip()
                occupation_version_name = str(row.get('occupation version') or "").strip()
                occupation_level_code_name = str(row.get('occupation level code') or "").strip()
                occupation_type_name = str(row.get('occupation type') or "").strip()
                occupation_code_name = str(row.get('occupation code') or "").strip()
                occupation_prospect_name = str(row.get('occupation prospect') or "").strip()
                occupation_name = str(row.get('occupation name') or "").strip()
                salarycurrency = row.get('salarycurrency')
                salaryamount = row.get('salaryamount')
                duration = row.get('duration')
                description = row.get('description', '')

                # Mandatory check
                if not (country_name and occupation_version_name and occupation_level_code_name and
                        occupation_type_name and occupation_code_name and occupation_prospect_name and occupation_name):
                    skipped_rows.append({
                        'Row': row_number,
                        'Country': country_name,
                        'Occupation Version': occupation_version_name,
                        'Occupation Level Code': occupation_level_code_name,
                        'Occupation Type': occupation_type_name,
                        'Occupation Code': occupation_code_name,
                        'Occupation Prospect': occupation_prospect_name,
                        'Occupation Name': occupation_name,
                        'Reason': 'Mandatory fields missing'
                    })
                    continue

                # Duration validation
                if duration and duration not in VALID_UNIT_CHOICES:
                    skipped_rows.append({
                        'Row': row_number,
                        'Country': country_name,
                        'Occupation Version': occupation_version_name,
                        'Occupation Level Code': occupation_level_code_name,
                        'Occupation Type': occupation_type_name,
                        'Occupation Code': occupation_code_name,
                        'Occupation Prospect': occupation_prospect_name,
                        'Occupation Name': occupation_name,
                        'Reason': f'Invalid duration: {duration}. Allowed: {VALID_UNIT_CHOICES}'
                    })
                    continue

                # Foreign key retrieval
                try:
                    country_obj = Country.objects.get(country_name__iexact=country_name)
                except Country.DoesNotExist:
                    skipped_rows.append({'Row': row_number, 'Country': country_name,
                        'Occupation Version': occupation_version_name,
                        'Occupation Level Code': occupation_level_code_name,
                        'Occupation Type': occupation_type_name,
                        'Occupation Code': occupation_code_name,
                        'Occupation Prospect': occupation_prospect_name,
                        'Occupation Name': occupation_name,
                          'Reason': 'Country not found'})
                    continue

                try:
                    occupationversion_obj = OccupationVersion.objects.get(country=country_obj, occupation_version__iexact=occupation_version_name)
                except OccupationVersion.DoesNotExist:
                    skipped_rows.append({'Row': row_number, 'Country': country_name,
                        'Occupation Version': occupation_version_name,
                        'Occupation Level Code': occupation_level_code_name,
                        'Occupation Type': occupation_type_name,
                        'Occupation Code': occupation_code_name,
                        'Occupation Prospect': occupation_prospect_name,
                        'Occupation Name': occupation_name,
                         'Reason': 'Occupation version not found'})
                    continue

                try:
                    occupationlevelcode_obj = OccupationLevelCode.objects.get(country=country_obj, occupationlevelcode__iexact=occupation_level_code_name)
                except OccupationLevelCode.DoesNotExist:
                    skipped_rows.append({'Row': row_number, 'Country': country_name,
                        'Occupation Version': occupation_version_name,
                        'Occupation Level Code': occupation_level_code_name,
                        'Occupation Type': occupation_type_name,
                        'Occupation Code': occupation_code_name,
                        'Occupation Prospect': occupation_prospect_name,
                        'Occupation Name': occupation_name,
                        'Reason': 'Occupation level code not found'})
                    continue

                try:
                    occupationtype_obj = OccupationType.objects.get(name__iexact=occupation_type_name)
                except OccupationType.DoesNotExist:
                    skipped_rows.append({'Row': row_number,'Country': country_name,
                        'Occupation Version': occupation_version_name,
                        'Occupation Level Code': occupation_level_code_name,
                        'Occupation Type': occupation_type_name,
                        'Occupation Code': occupation_code_name,
                        'Occupation Prospect': occupation_prospect_name,
                        'Occupation Name': occupation_name,
                          'Reason': 'Occupation type not found'})
                    continue

                try:
                    occupationcode_obj = OccupationCode.objects.get(occupationcode__iexact=occupation_code_name)
                except OccupationCode.DoesNotExist:
                    skipped_rows.append({'Row': row_number,'Country': country_name,
                        'Occupation Version': occupation_version_name,
                        'Occupation Level Code': occupation_level_code_name,
                        'Occupation Type': occupation_type_name,
                        'Occupation Code': occupation_code_name,
                        'Occupation Prospect': occupation_prospect_name,
                        'Occupation Name': occupation_name,
                          'Reason': 'Occupation code not found'})
                    continue

                try:
                    occupationprospect_obj = OccupationProspect.objects.get(name__iexact=occupation_prospect_name)
                except OccupationProspect.DoesNotExist:
                    skipped_rows.append({'Row': row_number, 'Country': country_name,
                        'Occupation Version': occupation_version_name,
                        'Occupation Level Code': occupation_level_code_name,
                        'Occupation Type': occupation_type_name,
                        'Occupation Code': occupation_code_name,
                        'Occupation Prospect': occupation_prospect_name,
                        'Occupation Name': occupation_name,
                        'Reason': 'Occupation prospect not found'})
                    continue

                # Duplicate check
                existing = JobProspect.objects.filter(
                    country=country_obj,
                    occupationversion=occupationversion_obj,
                    occupationlevelcode=occupationlevelcode_obj,
                    occupationtype=occupationtype_obj,
                    occupationcode=occupationcode_obj,
                    occupationprospect=occupationprospect_obj,
                    occupationname__iexact=occupation_name
                ).first()

                if existing:
                    if not existing.is_deleted:
                        duplicate_entries.append({
                            'Row': row_number,
                            'Country': country_name,
                            'Occupation Version': occupation_version_name,
                            'Occupation Level Code': occupation_level_code_name,
                            'Occupation Type': occupation_type_name,
                            'Occupation Code': occupation_code_name,
                            'Occupation Prospect': occupation_prospect_name,
                            'Occupation Name': occupation_name,
                            'Reason': 'Duplicate entry'
                        })
                        continue
                    else:
                        existing.is_deleted = False
                        existing.salarycurrency = salarycurrency
                        existing.salaryamount = salaryamount
                        existing.duration = duration
                        existing.description = description
                        existing.save()
                        imported_count += 1
                else:
                    JobProspect.objects.create(
                        country=country_obj,
                        occupationversion=occupationversion_obj,
                        occupationlevelcode=occupationlevelcode_obj,
                        occupationtype=occupationtype_obj,
                        occupationcode=occupationcode_obj,
                        occupationprospect=occupationprospect_obj,
                        occupationname=occupation_name,
                        salarycurrency=salarycurrency,
                        salaryamount=salaryamount,
                        duration=duration,
                        description=description,
                        is_deleted=False
                    )
                    imported_count += 1

        except Exception as e:
            return Response({'error': str(e)}, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": list(reversed(duplicate_entries)),
            "skipped_rows": list(reversed(skipped_rows)),
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count
        }, status=200)

class OccupationNameListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['occupationname', 'created_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = OccupationName.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(occupationname__istartswith=search) |
                Q(description__istartswith=search) |
                Q(Mainduties__istartswith=search) |
                Q(country__country_name__istartswith=search) |
                Q(occupationversion__occupation_version__istartswith=search) |
                Q(occupationcategory__occupationcategory__istartswith=search) |
                Q(occupationlevel__occupationlevel__istartswith=search) |
                Q(occupationlevelcode__occupationlevelcode__istartswith=search) |
                Q(occupationcode__occupationcode__istartswith=search)
            )

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = OccupationNameSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)





class OccupationNameCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        data = request.data.copy()

        # -------------------- Validate foreign keys -------------------- #
        fk_fields = {
            "country_id": RepresentingCountry,
            "occupationversion_id": OccupationVersion,
            "occupationcategory_id": OccupationCategory,
            "occupationlevel_id": OccupationLevel,
            "occupationlevelcode_id": OccupationLevelCode,
            "occupationcode_id": OccupationCode,
        }

        fk_objects = {}
        for field, model in fk_fields.items():
            uuid_val = data.get(field)
            if uuid_val:
                try:
                    fk_objects[field] = model.objects.get(uuid=uuid_val)
                except model.DoesNotExist:
                    return Response({
                        "statusCode": 400, "status": False,
                        "message": f"Invalid {field.replace('_id', '')} UUID."
                    }, status=400)
            else:
                fk_objects[field] = None

        # -------------------- Mandatory field -------------------- #
        occupationname = request.data.get("occupationname")
        if not occupationname:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Mandatory field missing: occupationname"
            }, status=400)

        # -------------------- Duplicate Check -------------------- #
        existing = OccupationName.objects.filter(
            country=fk_objects["country_id"],
            occupationversion=fk_objects["occupationversion_id"],
            occupationcategory=fk_objects["occupationcategory_id"],
            occupationlevel=fk_objects["occupationlevel_id"],
            occupationlevelcode=fk_objects["occupationlevelcode_id"],
            occupationcode=fk_objects["occupationcode_id"],
            occupationname__iexact=occupationname,
            is_deleted=False
        ).first()

        if existing:
            return Response({
                "statusCode": 400, "status": False,
                "message": "Occupation name already exists for this combination."
            }, status=400)

        # Fill FK UUIDs again
        for field, obj in fk_objects.items():
            if obj:
                data[field] = obj.uuid

        serializer = OccupationNameSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Occupation name created successfully",
                "data": serializer.data
            })

        error_message = " ".join([msg for msgs in serializer.errors.values() for msg in msgs])
        return Response({"statusCode": 400, "status": False, "message": error_message}, status=400)





class OccupationNameRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = OccupationName.objects.get(uuid=uuid, is_deleted=False)
        except OccupationName.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "Not found"}, status=404)

        serializer = OccupationNameSerializer(obj)
        return Response({"statusCode": 200, "status": True, "data": serializer.data})




class OccupationNameUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = OccupationName.objects.get(uuid=uuid, is_deleted=False)
        except OccupationName.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "Not found"}, status=404)

        serializer = OccupationNameSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Updated successfully",
                "data": serializer.data
            })

        err = " ".join([msg for msgs in serializer.errors.values() for msg in msgs])
        return Response({"statusCode": 400, "status": False, "message": err}, status=400)



class OccupationNameDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        ids = request.data.get('id')

        if not ids:
            return Response({"status": False, "message": "Provide 'id' field"}, status=400)

        if ids == "all":
            objs = OccupationName.objects.filter(is_deleted=False)
            count = objs.count()
            objs.update(is_deleted=True)
            return Response({"status": True, "message": f"All {count} records deleted"})

        if not isinstance(ids, list):
            return Response({"status": False, "message": "Send list of UUIDs"}, status=400)

        valid, invalid = [], []
        for u in ids:
            try:
                valid.append(UUID(u))
            except:
                invalid.append(u)

        objs = OccupationName.objects.filter(uuid__in=valid, is_deleted=False)
        count = objs.count()
        objs.update(is_deleted=True)

        return Response({
            "status": True,
            "message": f"{count} record(s) deleted",
            "invalid_uuids": invalid if invalid else None
        })

class OccupationNameExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get("format", "xlsx").lower()
        fields = request.GET.get("fields")
        uuids = request.GET.get("uuids", "")
        uuids = [u for u in uuids.split(",") if u]

        field_header = {
            'uuid': 'UUID',
            'country': 'Country',
            'occupationversion': 'Occupation Version',
            'occupationcategory': 'Occupation Category',
            'occupationlevel': 'Occupation Level',
            'occupationlevelcode': 'Level Code',
            'occupationcode': 'Occupation Code',
            'occupationname': 'Occupation Name',
            'description': 'Description',
            'Mainduties': 'Main Duties',
            'is_deleted': 'Deleted',
            'created_at': 'Created On',
            'updated_at': 'Updated On',
        }

        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header.keys())

        queryset = OccupationName.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header.get(f, f) for f in field_list]

        for obj in queryset:
            row = []
            for f in field_list:
                val = getattr(obj, f, "")
                if f == "country" and val:
                    val = val.full_name
                elif f == "occupationversion" and val:
                    val = val.occupation_version
                elif f == "occupationcategory" and val:
                    val = val.occupationcategory
                elif f == "occupationlevel" and val:
                    val = val.occupationlevel
                elif f == "occupationlevelcode" and val:
                    val = val.occupationlevelcode
                elif f == "occupationcode" and val:
                    val = val.occupationcode
                elif f in ["created_at", "updated_at"] and val:
                    val = timezone.localtime(val, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
                elif isinstance(val, bool):
                    val = int(val)
                row.append(val)
            dataset.append(row)

        if format_type == "csv":
            file_data = dataset.export("csv")
            response = HttpResponse(file_data, content_type="text/csv")
            response["Content-Disposition"] = 'attachment; filename="occupation_names.csv"'
        else:
            file_data = io.BytesIO(dataset.export("xlsx"))
            response = HttpResponse(file_data.getvalue(),
                                    content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            response["Content-Disposition"] = 'attachment; filename="occupation_names.xlsx"'

        return response


class OccupationNameImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get("file")
        sheet_name = request.data.get("sheet_name")

        if not file:
            return Response({"error": "No file uploaded"}, status=400)

        format_type = file.name.split(".")[-1].lower()
        required_headers = {
            "country", "occupation version", "occupation category",
            "occupation level", "occupation level code",
            "occupation code", "occupation name"
        }

        optional_headers = {"description", "mainduties"}

        parsed_data = []
        duplicate_entries = []
        skipped_rows = []
        bulk_new_objects = []

        try:
            # -------- XLSX --------
            if format_type == "xlsx":
                wb = openpyxl.load_workbook(file, read_only=True)
                if sheet_name not in wb.sheetnames:
                    return Response({"error": "Invalid sheet_name"}, status=400)

                ws = wb[sheet_name]
                headers = [str(c.value).strip().lower() for c in next(ws.iter_rows(min_row=1, max_row=1))]

                if not required_headers.issubset(headers):
                    return Response({"error": f"Missing required headers: {required_headers}"}, status=400)

                for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    row_dict = dict(zip(headers, row))
                    row_dict["_row_number"] = idx
                    parsed_data.append(row_dict)

            # -------- CSV --------
            elif format_type == "csv":
                dataset = Dataset()
                dataset.load(file.read().decode("utf-8"), format="csv")
                for idx, row in enumerate(dataset.dict, start=2):
                    r = {k.strip().lower(): v for k, v in row.items()}
                    r["_row_number"] = idx
                    parsed_data.append(r)
            else:
                return Response({"error": "Only xlsx/csv supported"}, status=400)

            imported_count = 0

            # -------- PROCESS BOTTOM TO TOP --------
            for row in reversed(parsed_data):
                row_num = row.get("_row_number", "Unknown")
                country_name = str(row.get("country", "")).strip()
                version_name = str(row.get("occupation version", "")).strip()
                category_name = str(row.get("occupation category", "")).strip()
                level_name = str(row.get("occupation level", "")).strip()
                level_code = str(row.get("occupation level code", "")).strip()
                occ_code = str(row.get("occupation code", "")).strip()
                occ_name = str(row.get("occupation name", "")).strip()
                desc = row.get("description", "")
                duties = row.get("mainduties", "")

                # Mandatory fields
                if not all([country_name, version_name, category_name, level_name, level_code, occ_code, occ_name]):
                    skipped_rows.append({"row": row_num,
                                        "Country": country_name,
                                        "Occupation Version": version_name,
                                        "Occupation Category": category_name,
                                        "Occupation Level": level_name,
                                        "Occupation Level Code": level_code,
                                        "Occupation Code": occ_code,
                                        "Occupation Name": occ_name,
                                        "Description":desc,
                                        "Mainduties":duties,
                                        "Reason": "Mandatory fields missing"})
                    continue

                # Fetch related objects
                country_obj = RepresentingCountry.objects.filter(full_name__iexact=country_name).first()
                if not country_obj:
                    skipped_rows.append({"row": row_num,"Country": country_name,
                                        "Occupation Version": version_name,
                                        "Occupation Category": category_name,
                                        "Occupation Level": level_name,
                                        "Occupation Level Code": level_code,
                                        "Occupation Code": occ_code,
                                        "Occupation Name": occ_name,
                                        "Description":desc,
                                        "Mainduties":duties,
                                        "Reason": "Country not found"})
                    continue

                version_obj = OccupationVersion.objects.filter(
                    country=country_obj, occupation_version__iexact=version_name
                ).first()
                if not version_obj:
                    skipped_rows.append({"row": row_num, "Country": country_name,
                                        "Occupation Version": version_name,
                                        "Occupation Category": category_name,
                                        "Occupation Level": level_name,
                                        "Occupation Level Code": level_code,
                                        "Occupation Code": occ_code,
                                        "Occupation Name": occ_name,
                                        "Description":desc,
                                        "Mainduties":duties,
                                        "Reason": "Version not found"})
                    continue

                category_obj = OccupationCategory.objects.filter(
                    country=country_obj,
                    occupation_version=version_obj,
                    occupationcategory__iexact=category_name
                ).first()
                if not category_obj:
                    skipped_rows.append({"row": row_num, 
                                        "Country": country_name,
                                        "Occupation Version": version_name,
                                        "Occupation Category": category_name,
                                        "Occupation Level": level_name,
                                        "Occupation Level Code": level_code,
                                        "Occupation Code": occ_code,
                                        "Occupation Name": occ_name,
                                        "Description":desc,
                                        "Mainduties":duties,"Reason": "Category not found"})
                    continue

                level_obj = OccupationLevel.objects.filter(
                    country=country_obj,
                    occupationversion=version_obj,
                    occupationcategory=category_obj,
                    occupationlevel__iexact=level_name
                ).first()
                if not level_obj:
                    skipped_rows.append({"row": row_num,"Country": country_name,
                                        "Occupation Version": version_name,
                                        "Occupation Category": category_name,
                                        "Occupation Level": level_name,
                                        "Occupation Level Code": level_code,
                                        "Occupation Code": occ_code,
                                        "Occupation Name": occ_name,
                                        "Description":desc,
                                        "Mainduties":duties,
                                          "Reason": "Level not found"})
                    continue

                level_code_obj = OccupationLevelCode.objects.filter(
                    country=country_obj,
                    occupation_version=version_obj,
                    occupationlevelcode__iexact=level_code
                ).first()
                if not level_code_obj:
                    skipped_rows.append({"row": row_num,"Country": country_name,
                                        "Occupation Version": version_name,
                                        "Occupation Category": category_name,
                                        "Occupation Level": level_name,
                                        "Occupation Level Code": level_code,
                                        "Occupation Code": occ_code,
                                        "Occupation Name": occ_name,
                                        "Description":desc,
                                        "Mainduties":duties,
                                        "Reason": "Level code not found"})
                    continue

                occupation_code_obj = OccupationCode.objects.filter(
                    country=country_obj,
                    occupationversion=version_obj,
                    occupationlevelcode=level_code_obj,
                    occupationcode__iexact=occ_code
                ).first()
                if not occupation_code_obj:
                    skipped_rows.append({"row": row_num, "Reason": "Occupation code not found"})
                    continue

                # Check for duplicates
                existing = OccupationName.objects.filter(
                    country=country_obj,
                    occupationversion=version_obj,
                    occupationcategory=category_obj,
                    occupationlevel=level_obj,
                    occupationlevelcode=level_code_obj,
                    occupationcode=occupation_code_obj,
                    occupationname__iexact=occ_name
                ).first()

                if existing:
                    if not existing.is_deleted:
                        duplicate_entries.append({
                            "row": row_num,
                            "Country": country_name,
                            "Occupation Version": version_name,
                            "Occupation Category": category_name,
                            "Occupation Level": level_name,
                            "Occupation Level Code": level_code,
                            "Occupation Code": occ_code,
                            "Occupation Name": occ_name,
                            "Description":desc,
                            "Mainduties":duties,
                            "Reason": "Duplicate entry"
                        })
                        continue

                    # Revive deleted record
                    existing.description = desc
                    existing.Mainduties = duties
                    existing.is_deleted = False
                    existing.save()
                    imported_count += 1
                    continue

                # New object → add to bulk list
                bulk_new_objects.append(
                    OccupationName(
                        country=country_obj,
                        occupationversion=version_obj,
                        occupationcategory=category_obj,
                        occupationlevel=level_obj,
                        occupationlevelcode=level_code_obj,
                        occupationcode=occupation_code_obj,
                        occupationname=occ_name,
                        description=desc,
                        Mainduties=duties,
                        is_deleted=False
                    )
                )

            # BULK CREATE
            if bulk_new_objects:
                OccupationName.objects.bulk_create(bulk_new_objects)
                imported_count += len(bulk_new_objects)

        except Exception as e:
            return Response({"error": str(e)}, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": list(reversed(duplicate_entries)),
            "skipped_rows": list(reversed(skipped_rows)),
            
        })




class RelatedOccupationListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['relatedoccupation', 'created_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = RelatedOccupation.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(relatedoccupation__istartswith=search) |
                Q(description__istartswith=search) |
                Q(country__country_name__istartswith=search) |
                Q(occupationversion__occupation_version__istartswith=search) |
                Q(occupationcode__occupationcode__istartswith=search) |
                Q(occupationname__occupationname__istartswith=search)
            )

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = RelatedOccupationSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class RelatedOccupationCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        data = request.data.copy()

        # -------------------- Validate foreign keys -------------------- #
        fk_fields = {
            "country_id": Country,
            "occupationversion_id": OccupationVersion,
            "occupationcode_id": OccupationCode,
            "occupationname_id": OccupationName,
        }

        fk_objects = {}
        for field, model in fk_fields.items():
            uuid_val = data.get(field)
            if uuid_val:
                try:
                    fk_objects[field] = model.objects.get(uuid=uuid_val)
                except model.DoesNotExist:
                    return Response({
                        "statusCode": 400, "status": False,
                        "message": f"Invalid {field.replace('_id', '')} UUID."
                    }, status=400)
            else:
                fk_objects[field] = None

        # -------------------- Mandatory field -------------------- #
        relatedoccupation = request.data.get("relatedoccupation")
        if not relatedoccupation:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Mandatory field missing: relatedoccupation"
            }, status=400)

        # -------------------- Duplicate Check -------------------- #
        existing = RelatedOccupation.objects.filter(
            country=fk_objects["country_id"],
            occupationversion=fk_objects["occupationversion_id"],
            occupationcode=fk_objects["occupationcode_id"],
            occupationname=fk_objects["occupationname_id"],
            relatedoccupation__iexact=relatedoccupation,
            is_deleted=False
        ).first()

        if existing:
            return Response({
                "statusCode": 400, "status": False,
                "message": "Related occupation already exists for this combination."
            }, status=400)

        # Fill FK UUIDs again
        for field, obj in fk_objects.items():
            if obj:
                data[field] = obj.uuid

        serializer = RelatedOccupationSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Related occupation created successfully",
                "data": serializer.data
            })

        error_message = " ".join([msg for msgs in serializer.errors.values() for msg in msgs])
        return Response({"statusCode": 400, "status": False, "message": error_message}, status=400)


class RelatedOccupationRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = RelatedOccupation.objects.get(uuid=uuid, is_deleted=False)
        except RelatedOccupation.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "Not found"}, status=404)

        serializer = RelatedOccupationSerializer(obj)
        return Response({"statusCode": 200, "status": True, "data": serializer.data})


class RelatedOccupationUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = RelatedOccupation.objects.get(uuid=uuid, is_deleted=False)
        except RelatedOccupation.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "Not found"}, status=404)

        serializer = RelatedOccupationSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Updated successfully",
                "data": serializer.data
            })

        err = " ".join([msg for msgs in serializer.errors.values() for msg in msgs])
        return Response({"statusCode": 400, "status": False, "message": err}, status=400)


class RelatedOccupationDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        ids = request.data.get('id')

        if not ids:
            return Response({"status": False, "message": "Provide 'id' field"}, status=400)

        if ids == "all":
            objs = RelatedOccupation.objects.filter(is_deleted=False)
            count = objs.count()
            objs.update(is_deleted=True)
            return Response({"status": True, "message": f"All {count} records deleted"})

        if not isinstance(ids, list):
            return Response({"status": False, "message": "Send list of UUIDs"}, status=400)

        valid, invalid = [], []
        for u in ids:
            try:
                valid.append(UUID(u))
            except:
                invalid.append(u)

        objs = RelatedOccupation.objects.filter(uuid__in=valid, is_deleted=False)
        count = objs.count()
        objs.update(is_deleted=True)

        return Response({
            "status": True,
            "message": f"{count} record(s) deleted",
            "invalid_uuids": invalid if invalid else None
        })


class RelatedOccupationExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get("format", "xlsx").lower()
        fields = request.GET.get("fields")
        uuids = request.GET.get("uuids", "")
        uuids = [u for u in uuids.split(",") if u]

        field_header = {
            'uuid': 'UUID',
            'country': 'Country',
            'occupationversion': 'Occupation Version',
            'occupationcode': 'Occupation Code',
            'occupationname': 'Occupation Name',
            'relatedoccupation': 'Related Occupation',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'created_at': 'Created On',
            'updated_at': 'Updated On',
        }

        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header.keys())

        queryset = RelatedOccupation.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header.get(f, f) for f in field_list]

        for obj in queryset:
            row = []
            for f in field_list:
                val = getattr(obj, f, "")
                if f == "country" and val:
                    val = val.name
                elif f == "occupationversion" and val:
                    val = val.occupation_version
                elif f == "occupationcode" and val:
                    val = val.occupationcode
                elif f == "occupationname" and val:
                    val = val.occupationname
                elif f in ["created_at", "updated_at"] and val:
                    val = timezone.localtime(val, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
                elif isinstance(val, bool):
                    val = int(val)
                row.append(val)
            dataset.append(row)

        if format_type == "csv":
            file_data = dataset.export("csv")
            response = HttpResponse(file_data, content_type="text/csv")
            response["Content-Disposition"] = 'attachment; filename="related_occupations.csv"'
        else:
            file_data = io.BytesIO(dataset.export("xlsx"))
            response = HttpResponse(file_data.getvalue(),
                                    content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            response["Content-Disposition"] = 'attachment; filename="related_occupations.xlsx"'

        return response


class RelatedOccupationImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=400)

        format_type = file.name.split('.')[-1].lower()
        duplicate_entries = []
        skipped_rows = []
        required_headers = {'country', 'occupation version', 'occupation code', 'occupation name', 'related occupation'}
        optional_headers = {'description'}

        try:
            data = []

            # -------- XLSX --------
            if format_type == 'xlsx':
                wb = openpyxl.load_workbook(file, read_only=True)
                if not sheet_name:
                    return Response({'error': 'Provide sheet_name', 'available_sheets': wb.sheetnames}, status=400)
                if sheet_name not in wb.sheetnames:
                    return Response({'error': f'Sheet "{sheet_name}" not found', 'available_sheets': wb.sheetnames}, status=400)

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
                    row_dict["_row_number"] = idx
                    data.append(row_dict)

            # -------- CSV --------
            elif format_type == 'csv':
                dataset = Dataset()
                dataset.load(file.read().decode('utf-8'), format='csv')
                for idx, row in enumerate(dataset.dict, start=2):
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({'error': f'Missing required headers. Required: {required_headers}'}, status=400)
                    row_lower["_row_number"] = idx
                    data.append(row_lower)
            else:
                return Response({'error': 'Unsupported file format. Use .xlsx or .csv'}, status=400)

            # -------- Validate and prepare for bulk create --------
            bulk_list = []
            imported_count = 0

            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")
                country_name = str(row.get('country') or "").strip()
                version_name = str(row.get('occupation version') or "").strip()
                code_name = str(row.get('occupation code') or "").strip()
                occ_name = str(row.get('occupation name') or "").strip()
                related_occ = str(row.get('related occupation') or "").strip()
                description = row.get('description', '')

                if not (country_name and version_name and code_name and occ_name and related_occ):
                    skipped_rows.append({
                        'Row': row_number,
                        'Country': country_name,
                        'Occupation Version': version_name,
                        'Occupation Code': code_name,
                        'Occupation Name': occ_name,
                        'Related Occupation': related_occ,
                        'Reason': 'Mandatory fields missing'
                    })
                    continue

                # -------- Foreign keys --------
                try:
                    country_obj = Country.objects.get(country_name__iexact=country_name)
                except Country.DoesNotExist:
                    skipped_rows.append({'Row': row_number, 'Country': country_name,
                        'Occupation Version': version_name,
                        'Occupation Code': code_name,
                        'Occupation Name': occ_name,
                        'Related Occupation': related_occ,
                          'Reason': 'Country not found'})
                    continue
                try:
                    version_obj = OccupationVersion.objects.get(country=country_obj, occupation_version__iexact=version_name)
                except OccupationVersion.DoesNotExist:
                    skipped_rows.append({'Row': row_number, 'Country': country_name,
                        'Occupation Version': version_name,
                        'Occupation Code': code_name,
                        'Occupation Name': occ_name,
                        'Related Occupation': related_occ,
                          'Reason': 'Occupation version not found'})
                    continue
                try:
                    code_obj = OccupationCode.objects.get(country=country_obj, occupationversion=version_obj, occupationcode__iexact=code_name)
                except OccupationCode.DoesNotExist:
                    skipped_rows.append({'Row': row_number, 'Country': country_name,
                        'Occupation Version': version_name,
                        'Occupation Code': code_name,
                        'Occupation Name': occ_name,
                        'Related Occupation': related_occ,
                        'Reason': 'Occupation code not found'})
                    continue
                try:
                    occ_obj = OccupationName.objects.get(country=country_obj, occupationversion=version_obj, occupationcode=code_obj, occupationname__iexact=occ_name)
                except OccupationName.DoesNotExist:
                    skipped_rows.append({'Row': row_number, 'Country': country_name,
                        'Occupation Version': version_name,
                        'Occupation Code': code_name,
                        'Occupation Name': occ_name,
                        'Related Occupation': related_occ,
                          'Reason': 'Occupation name not found'})
                    continue

                # -------- Duplicate check --------
                if RelatedOccupation.objects.filter(
                    country=country_obj,
                    occupationversion=version_obj,
                    occupationcode=code_obj,
                    occupationname=occ_obj,
                    relatedoccupation__iexact=related_occ
                ).exists():
                    duplicate_entries.append({
                        'Row': row_number,
                        'Country': country_name,
                        'Occupation Version': version_name,
                        'Occupation Code': code_name,
                        'Occupation Name': occ_name,
                        'Related Occupation': related_occ,
                        'Reason': 'Duplicate entry'
                    })
                    continue

                # -------- Prepare for bulk --------
                bulk_list.append(
                    RelatedOccupation(
                        country=country_obj,
                        occupationversion=version_obj,
                        occupationcode=code_obj,
                        occupationname=occ_obj,
                        relatedoccupation=related_occ,
                        description=description,
                        is_deleted=False
                    )
                )
                imported_count += 1

            # -------- Bulk create --------
            if bulk_list:
                RelatedOccupation.objects.bulk_create(bulk_list)

        except Exception as e:
            return Response({'error': str(e)}, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": list(reversed(duplicate_entries)),
            "skipped_rows": list(reversed(skipped_rows)),
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count
        }, status=200)


class OccupationToOccupationListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['created_at', 'description']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = OccupationToOccupation.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(description__istartswith=search) |
                Q(country__country_name__istartswith=search) |
                Q(occupationversion__occupation_version__istartswith=search) |
                Q(occupationcode__occupationcode__istartswith=search) |
                Q(occupationname__occupationname__istartswith=search) |
                Q(comparecountry__country_name__istartswith=search) |
                Q(compareoccupationversion__occupation_version__istartswith=search) |
                Q(compareoccupationcode__occupationcode__istartswith=search) |
                Q(compareoccupationname__occupationname__istartswith=search)
            )

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = OccupationToOccupationSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class OccupationToOccupationCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        data = request.data.copy()

        # -------------------- Foreign Key Validation -------------------- #
        fk_fields = {
            "country_id": Country,
            "occupationversion_id": OccupationVersion,
            "occupationcode_id": OccupationCode,
            "occupationname_id": OccupationName,
            "comparecountry_id": Country,
            "compareoccupationversion_id": OccupationVersion,
            "compareoccupationcode_id": OccupationCode,
            "compareoccupationname_id": OccupationName,
        }

        fk_objects = {}
        for field, model in fk_fields.items():
            uuid_val = data.get(field)
            if uuid_val:
                try:
                    fk_objects[field] = model.objects.get(uuid=uuid_val)
                except model.DoesNotExist:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f"Invalid {field.replace('_id', '')} UUID."
                    }, status=400)
            else:
                fk_objects[field] = None

        # -------------------- Mandatory field -------------------- #
        if not data.get("description"):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Mandatory field missing: description"
            }, status=400)

        # -------------------- Duplicate Check -------------------- #
        existing = OccupationToOccupation.objects.filter(
            country=fk_objects["country_id"],
            occupationversion=fk_objects["occupationversion_id"],
            occupationcode=fk_objects["occupationcode_id"],
            occupationname=fk_objects["occupationname_id"],
            comparecountry=fk_objects["comparecountry_id"],
            compareoccupationversion=fk_objects["compareoccupationversion_id"],
            compareoccupationcode=fk_objects["compareoccupationcode_id"],
            compareoccupationname=fk_objects["compareoccupationname_id"],
            description__iexact=data.get("description"),
            is_deleted=False
        ).first()

        if existing:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "This occupation comparison already exists."
            }, status=400)

        # Fill UUIDs again
        for field, obj in fk_objects.items():
            if obj:
                data[field] = obj.uuid

        serializer = OccupationToOccupationSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Occupation comparison created successfully",
                "data": serializer.data
            })

        error_message = " ".join([msg for msgs in serializer.errors.values() for msg in msgs])
        return Response({"statusCode": 400, "status": False, "message": error_message}, status=400)


class OccupationToOccupationRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = OccupationToOccupation.objects.get(uuid=uuid, is_deleted=False)
        except OccupationToOccupation.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "Not found"}, status=404)

        serializer = OccupationToOccupationSerializer(obj)
        return Response({"statusCode": 200, "status": True, "data": serializer.data})


class OccupationToOccupationUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = OccupationToOccupation.objects.get(uuid=uuid, is_deleted=False)
        except OccupationToOccupation.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "Not found"}, status=404)

        serializer = OccupationToOccupationSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Updated successfully",
                "data": serializer.data
            })

        err = " ".join([msg for msgs in serializer.errors.values() for msg in msgs])
        return Response({"statusCode": 400, "status": False, "message": err}, status=400)


class OccupationToOccupationDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        ids = request.data.get('id')

        if not ids:
            return Response({"status": False, "message": "Provide 'id' field"}, status=400)

        if ids == "all":
            objs = OccupationToOccupation.objects.filter(is_deleted=False)
            count = objs.count()
            objs.update(is_deleted=True)
            return Response({"status": True, "message": f"All {count} records deleted"})

        if not isinstance(ids, list):
            return Response({"status": False, "message": "Send list of UUIDs"}, status=400)

        valid, invalid = [], []
        for u in ids:
            try:
                valid.append(UUID(u))
            except:
                invalid.append(u)

        objs = OccupationToOccupation.objects.filter(uuid__in=valid, is_deleted=False)
        count = objs.count()
        objs.update(is_deleted=True)

        return Response({
            "status": True,
            "message": f"{count} record(s) deleted",
            "invalid_uuids": invalid if invalid else None
        })


class OccupationToOccupationExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get("format", "xlsx").lower()
        fields = request.GET.get("fields")
        uuids = request.GET.get("uuids", "")
        uuids = [u for u in uuids.split(",") if u]

        field_header = {
            'uuid': 'UUID',
            'country': 'Country',
            'occupationversion': 'Occupation Version',
            'occupationcode': 'Occupation Code',
            'occupationname': 'Occupation Name',
            'comparecountry': 'Compare Country',
            'compareoccupationversion': 'Compare Occupation Version',
            'compareoccupationcode': 'Compare Occupation Code',
            'compareoccupationname': 'Compare Occupation Name',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'created_at': 'Created On',
            'updated_at': 'Updated On',
        }

        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header.keys())

        queryset = OccupationToOccupation.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header.get(f, f) for f in field_list]

        for obj in queryset:
            row = []
            for f in field_list:
                val = getattr(obj, f, "")
                if f == "country" and val:
                    val = val.name
                elif f == "occupationversion" and val:
                    val = val.occupation_version
                elif f == "occupationcode" and val:
                    val = val.occupationcode
                elif f == "occupationname" and val:
                    val = val.occupationname
                elif f == "comparecountry" and val:
                    val = val.name
                elif f == "compareoccupationversion" and val:
                    val = val.occupation_version
                elif f == "compareoccupationcode" and val:
                    val = val.occupationcode
                elif f == "compareoccupationname" and val:
                    val = val.occupationname
                elif f in ["created_at", "updated_at"] and val:
                    val = timezone.localtime(val, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
                elif isinstance(val, bool):
                    val = int(val)
                row.append(val)
            dataset.append(row)

        if format_type == "csv":
            file_data = dataset.export("csv")
            response = HttpResponse(file_data, content_type="text/csv")
            response["Content-Disposition"] = 'attachment; filename="occupation_to_occupation.csv"'
        else:
            file_data = io.BytesIO(dataset.export("xlsx"))
            response = HttpResponse(file_data.getvalue(),
                                    content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            response["Content-Disposition"] = 'attachment; filename="occupation_to_occupation.xlsx"'

        return response



class OccupationToOccupationImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=400)

        format_type = file.name.split('.')[-1].lower()
        duplicate_entries = []
        skipped_rows = []
        required_headers = {
            'country', 'occupation version', 'occupation code', 'occupation name',
            'compare country', 'compare occupation version', 'compare occupation code', 'compare occupation name'
        }
        optional_headers = {'description'}

        try:
            data = []

            # -------- XLSX --------
            if format_type == 'xlsx':
                wb = openpyxl.load_workbook(file, read_only=True)
                if not sheet_name:
                    return Response({'error': 'Provide sheet_name', 'available_sheets': wb.sheetnames}, status=400)
                if sheet_name not in wb.sheetnames:
                    return Response({'error': f'Sheet "{sheet_name}" not found', 'available_sheets': wb.sheetnames}, status=400)

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
                    row_dict['_row_number'] = idx
                    data.append(row_dict)

            # -------- CSV --------
            elif format_type == 'csv':
                dataset = Dataset()
                dataset.load(file.read().decode('utf-8'), format='csv')
                for idx, row in enumerate(dataset.dict, start=2):
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({'error': f'Missing required headers. Required: {required_headers}'}, status=400)
                    row_lower['_row_number'] = idx
                    data.append(row_lower)
            else:
                return Response({'error': 'Unsupported file format. Use .xlsx or .csv'}, status=400)

            # -------- Validate and prepare for bulk create --------
            bulk_list = []
            imported_count = 0

            for row in reversed(data):
                row_number = row.get('_row_number', 'Unknown')
                country_name = str(row.get('country') or '').strip()
                version_name = str(row.get('occupation version') or '').strip()
                code_name = str(row.get('occupation code') or '').strip()
                occ_name = str(row.get('occupation name') or '').strip()

                compare_country_name = str(row.get('compare country') or '').strip()
                compare_version_name = str(row.get('compare occupation version') or '').strip()
                compare_code_name = str(row.get('compare occupation code') or '').strip()
                compare_occ_name = str(row.get('compare occupation name') or '').strip()

                description = row.get('description', '')

                # Mandatory check
                if not all([country_name, version_name, code_name, occ_name,
                            compare_country_name, compare_version_name, compare_code_name, compare_occ_name]):
                    skipped_rows.append({
                        'Row': row_number,
                        'Reason': 'Mandatory fields missing',
                        'Country': country_name,
                        'Occupation Version': version_name,
                        'Occupation Code': code_name,
                        'Occupation Name': occ_name,
                        'Compare Country': compare_country_name,
                        'Compare Occupation Version': compare_version_name,
                        'Compare Occupation Code': compare_code_name,
                        'Compare Occupation Name': compare_occ_name
                    })
                    continue

                # -------- Foreign key retrieval --------
                try:
                    country_obj = Country.objects.get(country_name__iexact=country_name)
                    version_obj = OccupationVersion.objects.get(country=country_obj, occupation_version__iexact=version_name)
                    code_obj = OccupationCode.objects.get(country=country_obj, occupationversion=version_obj, occupationcode__iexact=code_name)
                    occ_obj = OccupationName.objects.get(country=country_obj, occupationversion=version_obj, occupationcode=code_obj, occupationname__iexact=occ_name)

                    compare_country_obj = Country.objects.get(country_name__iexact=compare_country_name)
                    compare_version_obj = OccupationVersion.objects.get(country=compare_country_obj, occupation_version__iexact=compare_version_name)
                    compare_code_obj = OccupationCode.objects.get(country=compare_country_obj, occupationversion=compare_version_obj, occupationcode__iexact=compare_code_name)
                    compare_occ_obj = OccupationName.objects.get(country=compare_country_obj, occupationversion=compare_version_obj, occupationcode=compare_code_obj, occupationname__iexact=compare_occ_name)
                except Country.DoesNotExist:
                    skipped_rows.append({'Row': row_number,'Country': country_name,
                        'Occupation Version': version_name,
                        'Occupation Code': code_name,
                        'Occupation Name': occ_name,
                        'Compare Country': compare_country_name,
                        'Compare Occupation Version': compare_version_name,
                        'Compare Occupation Code': compare_code_name,
                        'Compare Occupation Name': compare_occ_name,
                          'Reason': 'Country not found'})
                    continue
                except OccupationVersion.DoesNotExist:
                    skipped_rows.append({'Row': row_number, 'Country': country_name,
                        'Occupation Version': version_name,
                        'Occupation Code': code_name,
                        'Occupation Name': occ_name,
                        'Compare Country': compare_country_name,
                        'Compare Occupation Version': compare_version_name,
                        'Compare Occupation Code': compare_code_name,
                        'Compare Occupation Name': compare_occ_name,
                        'Reason': 'Occupation version not found'})
                    continue
                except OccupationCode.DoesNotExist:
                    skipped_rows.append({'Row': row_number,
                                          'Reason': 'Occupation code not found'})
                    continue
                except OccupationName.DoesNotExist:
                    skipped_rows.append({'Row': row_number,'Country': country_name,
                        'Occupation Version': version_name,
                        'Occupation Code': code_name,
                        'Occupation Name': occ_name,
                        'Compare Country': compare_country_name,
                        'Compare Occupation Version': compare_version_name,
                        'Compare Occupation Code': compare_code_name,
                        'Compare Occupation Name': compare_occ_name,
                          'Reason': 'Occupation name not found'})
                    continue

                # -------- Duplicate check --------
                if OccupationToOccupation.objects.filter(
                    country=country_obj,
                    occupationversion=version_obj,
                    occupationcode=code_obj,
                    occupationname=occ_obj,
                    comparecountry=compare_country_obj,
                    compareoccupationversion=compare_version_obj,
                    compareoccupationcode=compare_code_obj,
                    compareoccupationname=compare_occ_obj
                ).exists():
                    duplicate_entries.append({
                        'Row': row_number,
                        'Country': country_name,
                        'Occupation Version': version_name,
                        'Occupation Code': code_name,
                        'Occupation Name': occ_name,
                        'Compare Country': compare_country_name,
                        'Compare Occupation Version': compare_version_name,
                        'Compare Occupation Code': compare_code_name,
                        'Compare Occupation Name': compare_occ_name,
                        "Reason": "Already exists in database"
                    })
                    continue

                # -------- Prepare for bulk create --------
                bulk_list.append(
                    OccupationToOccupation(
                        country=country_obj,
                        occupationversion=version_obj,
                        occupationcode=code_obj,
                        occupationname=occ_obj,
                        comparecountry=compare_country_obj,
                        compareoccupationversion=compare_version_obj,
                        compareoccupationcode=compare_code_obj,
                        compareoccupationname=compare_occ_obj,
                        description=description,
                        is_deleted=False
                    )
                )
                imported_count += 1

            # -------- Bulk insert --------
            if bulk_list:
                OccupationToOccupation.objects.bulk_create(bulk_list)

        except Exception as e:
            return Response({'error': str(e)}, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": list(reversed(duplicate_entries)),
            "skipped_rows": list(reversed(skipped_rows)),
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count
        }, status=200)


class DesignationListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['designation', 'created_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = Designation.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(designation__istartswith=search) |
                Q(description__istartswith=search) |
                Q(country__name__istartswith=search) |
                Q(occupationversion__occupation_version__istartswith=search) |
                Q(occupationname__occupationname__istartswith=search) |
                Q(occupationcode__occupationcode__istartswith=search)
            )

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = DesignationSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


# -------------------- CREATE API -------------------- #
class DesignationCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        data = request.data.copy()

        # Validate foreign keys
        fk_fields = {
            "country_id": RepresentingCountry,
            "occupationversion_id": OccupationVersion,
            "occupationname_id": OccupationName,
            "occupationcode_id": OccupationCode,
        }

        fk_objects = {}
        for field, model in fk_fields.items():
            uuid_val = data.get(field)
            if uuid_val:
                try:
                    fk_objects[field] = model.objects.get(uuid=uuid_val)
                except model.DoesNotExist:
                    return Response({
                        "statusCode": 400, "status": False,
                        "message": f"Invalid {field.replace('_id', '')} UUID."
                    }, status=400)
            else:
                fk_objects[field] = None

        # Mandatory field
        designation_name = request.data.get("designation")
        if not designation_name:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Mandatory field missing: designation"
            }, status=400)

        # Duplicate check
        existing = Designation.objects.filter(
            country=fk_objects["country_id"],
            occupationversion=fk_objects["occupationversion_id"],
            occupationname=fk_objects["occupationname_id"],
            occupationcode=fk_objects["occupationcode_id"],
            designation__iexact=designation_name,
            is_deleted=False
        ).first()

        if existing:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Designation already exists for this combination."
            }, status=400)

        # Fill FK UUIDs again
        for field, obj in fk_objects.items():
            if obj:
                data[field] = obj.uuid

        serializer = DesignationSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Designation created successfully",
                "data": serializer.data
            })

        error_message = " ".join([msg for msgs in serializer.errors.values() for msg in msgs])
        return Response({"statusCode": 400, "status": False, "message": error_message}, status=400)


# -------------------- RETRIEVE API -------------------- #
class DesignationRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = Designation.objects.get(uuid=uuid, is_deleted=False)
        except Designation.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "Not found"}, status=404)

        serializer = DesignationSerializer(obj)
        return Response({"statusCode": 200, "status": True, "data": serializer.data})


# -------------------- UPDATE API -------------------- #
class DesignationUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = Designation.objects.get(uuid=uuid, is_deleted=False)
        except Designation.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "Not found"}, status=404)

        serializer = DesignationSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Updated successfully",
                "data": serializer.data
            })

        err = " ".join([msg for msgs in serializer.errors.values() for msg in msgs])
        return Response({"statusCode": 400, "status": False, "message": err}, status=400)


# -------------------- DELETE API -------------------- #
class DesignationDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        ids = request.data.get('id')

        if not ids:
            return Response({"status": False, "message": "Provide 'id' field"}, status=400)

        if ids == "all":
            objs = Designation.objects.filter(is_deleted=False)
            count = objs.count()
            objs.update(is_deleted=True)
            return Response({"status": True, "message": f"All {count} records deleted"})

        if not isinstance(ids, list):
            return Response({"status": False, "message": "Send list of UUIDs"}, status=400)

        valid, invalid = [], []
        for u in ids:
            try:
                valid.append(UUID(u))
            except:
                invalid.append(u)

        objs = Designation.objects.filter(uuid__in=valid, is_deleted=False)
        count = objs.count()
        objs.update(is_deleted=True)

        return Response({
            "status": True,
            "message": f"{count} record(s) deleted",
            "invalid_uuids": invalid if invalid else None
        })


# -------------------- EXPORT API -------------------- #
class DesignationExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get("format", "xlsx").lower()
        fields = request.GET.get("fields")
        uuids = request.GET.get("uuids", "")
        uuids = [u for u in uuids.split(",") if u]

        field_header = {
            'uuid': 'UUID',
            'country': 'Country',
            'occupationversion': 'Occupation Version',
            'occupationname': 'Occupation Name',
            'occupationcode': 'Occupation Code',
            'designation': 'Designation',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'created_at': 'Created On',
            'updated_at': 'Updated On',
        }

        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header.keys())

        queryset = Designation.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header.get(f, f) for f in field_list]

        for obj in queryset:
            row = []
            for f in field_list:
                val = getattr(obj, f, "")
                if f == "country" and val:
                    val = val.full_name
                elif f == "occupationversion" and val:
                    val = val.occupation_version
                elif f == "occupationname" and val:
                    val = val.occupationname
                elif f == "occupationcode" and val:
                    val = val.occupationcode
                elif f in ["created_at", "updated_at"] and val:
                    val = timezone.localtime(val, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
                elif isinstance(val, bool):
                    val = int(val)
                row.append(val)
            dataset.append(row)

        if format_type == "csv":
            file_data = dataset.export("csv")
            response = HttpResponse(file_data, content_type="text/csv")
            response["Content-Disposition"] = 'attachment; filename="designations.csv"'
        else:
            file_data = io.BytesIO(dataset.export("xlsx"))
            response = HttpResponse(file_data.getvalue(),
                                    content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            response["Content-Disposition"] = 'attachment; filename="designations.xlsx"'

        return response


# -------------------- IMPORT API -------------------- #
class DesignationImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get("file")
        sheet_name = request.data.get("sheet_name")

        if not file:
            return Response({"error": "No file uploaded"}, status=400)

        format_type = file.name.split(".")[-1].lower()
        required_headers = {
            "country", "occupation version", "occupation name",
            "occupation code", "designation"
        }
        optional_headers = {"description"}

        parsed_data = []

        try:
            # -------- XLSX --------
            if format_type == "xlsx":
                wb = openpyxl.load_workbook(file, read_only=True)
                if sheet_name not in wb.sheetnames:
                    return Response({"error": "Invalid sheet_name"}, status=400)
                ws = wb[sheet_name]
                headers = [str(c.value).strip().lower() for c in next(ws.iter_rows(min_row=1, max_row=1))]
                if not required_headers.issubset(headers):
                    return Response({"error": f"Missing required headers: {required_headers}"}, status=400)
                for index, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    row_dict = dict(zip(headers, row))
                    parsed_data.append((index, row_dict))

            # -------- CSV --------
            elif format_type == "csv":
                dataset = Dataset()
                dataset.load(file.read().decode("utf-8"), format="csv")
                for idx, row in enumerate(dataset.dict, start=2):
                    r = {k.strip().lower(): v for k, v in row.items()}
                    if not required_headers.issubset(r.keys()):
                        return Response({"error": f"Missing required headers: {required_headers}"})
                    parsed_data.append((idx, r))

            else:
                return Response({"error": "Only xlsx/csv supported"}, status=400)

            duplicate = []
            skipped = []
            imported_count = 0
            bulk_objects = []

            for row_num, row in reversed(parsed_data):
                country_name = str(row.get("country", "") or "").strip()
                version_name = str(row.get("occupation version", "") or "").strip()
                occ_name = str(row.get("occupation name", "") or "").strip()
                occ_code = str(row.get("occupation code", "") or "").strip()
                designation_name = str(row.get("designation", "") or "").strip()
                desc = row.get("description", "")

                # Mandatory check
                if not (country_name and version_name and occ_name and occ_code and designation_name):
                    skipped.append({
                        "row": row_num,
                        "Country": country_name,
                        "Occupation Version": version_name,
                        "Occupation Name": occ_name,
                        "Occupation Code": occ_code,
                        "Designation": designation_name,
                        "Description":desc,
                        "Reason": "Mandatory fields missing"
                    })
                    continue

                # Country lookup
                country_obj = RepresentingCountry.objects.filter(full_name__iexact=country_name).first()
                if not country_obj:
                    skipped.append({
                        "row": row_num,
                        "Country": country_name,
                        "Occupation Version": version_name,
                        "Occupation Name": occ_name,
                        "Occupation Code": occ_code,
                        "Designation": designation_name,
                        "Description":desc,
                        "Reason": "Country not found"
                    })
                    continue

                # Occupation Version lookup
                occupation_version_obj = OccupationVersion.objects.filter(country=country_obj, occupation_version__iexact=version_name).first()
                if not occupation_version_obj:
                    skipped.append({
                        "row": row_num,
                        "Country": country_name,
                        "Occupation Version": version_name,
                        "Occupation Name": occ_name,
                        "Occupation Code": occ_code,
                        "Designation": designation_name,
                        "Description":desc,
                        "Reason": "Version not found"
                    })
                    continue

                # Occupation Name lookup
                occupation_obj = OccupationName.objects.filter(country=country_obj, occupationversion=occupation_version_obj, occupationname__iexact=occ_name).first()
                if not occupation_obj:
                    skipped.append({
                        "row": row_num,
                        "Country": country_name,
                        "Occupation Version": version_name,
                        "Occupation Name": occ_name,
                        "Occupation Code": occ_code,
                        "Designation": designation_name,
                        "Description":desc,
                        "Reason": "Occupation not found"
                    })
                    continue

                # Occupation Code lookup
                occupation_code_obj = OccupationCode.objects.filter(country=country_obj, occupationversion=occupation_version_obj, occupationcode__iexact=occ_code).first()
                if not occupation_code_obj:
                    skipped.append({
                        "row": row_num,
                        "Country": country_name,
                        "Occupation Version": version_name,
                        "Occupation Name": occ_name,
                        "Occupation Code": occ_code,
                        "Designation": designation_name,
                        "Description":desc,
                        "Reason": "Occupation code not found"
                    })
                    continue

                # Duplicate check
                existing = Designation.objects.filter(
                    country=country_obj,
                    occupationversion=occupation_version_obj,
                    occupationname=occupation_obj,
                    occupationcode=occupation_code_obj,
                    designation__iexact=designation_name
                ).first()

                if existing:
                    if not existing.is_deleted:
                        duplicate.append({
                            "row": row_num,
                            "Country": country_name,
                            "Occupation Version": version_name,
                            "Occupation Name": occ_name,
                            "Occupation Code": occ_code,
                            "Designation": designation_name,
                            "Description":desc,
                            "Reason": "Duplicate entry"
                        })
                        continue
                    else:
                        existing.description = desc
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    # Add to bulk create list
                    bulk_objects.append(Designation(
                        country=country_obj,
                        occupationversion=occupation_version_obj,
                        occupationname=occupation_obj,
                        occupationcode=occupation_code_obj,
                        designation=designation_name,
                        description=desc,
                        is_deleted=False
                    ))

            # Bulk create new Designations
            if bulk_objects:
                Designation.objects.bulk_create(bulk_objects)
                imported_count += len(bulk_objects)

        except Exception as e:
            return Response({"error": str(e)}, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": list(reversed(duplicate)),
            "skipped_rows": list(reversed(skipped)),
        })



