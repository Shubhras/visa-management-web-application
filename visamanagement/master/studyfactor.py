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
from django.db import IntegrityError, transaction
from django.db import DatabaseError
import csv
import io
import pytz
from django.utils import timezone
import unicodedata

india_tz = pytz.timezone('Asia/Kolkata')


class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_superuser)
    



class FactorForListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['name', 'description', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = FactorFor.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(Q(name__istartswith=search))

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = FactorForSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)


# ---------------- CREATE ----------------
class FactorForCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        name = request.data.get("name", "").strip()
        existing = FactorFor.objects.filter(name__iexact=name, is_deleted=False).first()

        if existing:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "FactorFor with this name already exists."
            }, status=400)

        serializer = FactorForSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "FactorFor created successfully",
                "data": serializer.data
            })
        else:
            messages = []
            for field, msgs in serializer.errors.items():
                messages.extend(msgs)
            return Response({
                "statusCode": 400,
                "status": False,
                "message": " ".join(messages)
            }, status=400)


# ---------------- RETRIEVE ----------------
class FactorForRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = FactorFor.objects.get(uuid=uuid, is_deleted=False)
        except FactorFor.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "FactorFor not found",
                "data": None
            }, status=404)

        serializer = FactorForSerializer(obj)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "FactorFor retrieved successfully",
            "data": serializer.data
        })


# ---------------- UPDATE ----------------
class FactorForUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = FactorFor.objects.get(uuid=uuid, is_deleted=False)
        except FactorFor.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "FactorFor not found",
                "data": None
            }, status=404)

        serializer = FactorForSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "FactorFor updated successfully",
                "data": serializer.data
            })
        else:
            messages = []
            for field, msgs in serializer.errors.items():
                messages.extend(msgs)
            return Response({
                "statusCode": 400,
                "status": False,
                "message": " ".join(messages),
                "data": None
            }, status=400)


# ---------------- DELETE ----------------
class FactorForDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get('id', None)

        if uuid:
            try:
                obj = FactorFor.objects.get(uuid=uuid)
                obj.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "FactorFor permanently deleted.",
                    "data": None
                }, status=204)
            except FactorFor.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "FactorFor not found.",
                    "data": None
                }, status=404)

        if ids == "all":
            objs = FactorFor.objects.all()
            count = objs.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No FactorFor found to delete.",
                    "data": None
                }, status=404)
            objs.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} FactorFor permanently deleted.",
                "data": None
            })

        if not ids or not isinstance(ids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide a list of UUIDs in 'id' field or 'all'.",
                "data": None
            }, status=400)

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
            }, status=400)

        objs = FactorFor.objects.filter(uuid__in=valid_uuids)
        count = objs.count()
        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching FactorFor found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=404)

        objs.delete()
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} FactorFor(s) permanently deleted.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        })


# ---------------- EXPORT ----------------
class FactorForExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'name': 'Factor For',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'updated_at': 'Modified On',
        }

        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())
        queryset = FactorFor.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'FactorFor'

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
            file_name = 'factorfor.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'factorfor.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


# ---------------- IMPORT ----------------
class FactorForImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get("file")
        sheet_name = request.data.get("sheet_name")

        if not file:
            return Response({"error": "No file uploaded"}, status=400)

        format_type = file.name.split(".")[-1].lower()
        duplicates = []
        skipped_rows = []
        required_headers = {"factor for"}
        optional_headers = {"description"}

        try:
            data = []

            if format_type == "xlsx":
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({
                        "error": "Please provide sheet_name",
                        "available_sheets": available_sheets,
                    }, status=400)

                if sheet_name not in available_sheets:
                    return Response({
                        "error": f'Sheet "{sheet_name}" not found',
                        "available_sheets": available_sheets,
                    }, status=400)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'Sheet "{sheet_name}" is empty.'
                    }, status=400)

                headers = [str(cell.value).strip().lower() if cell.value else "" for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                if not required_headers.issubset(set(headers)):
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f"Missing required headers. Required: {required_headers}, Found: {set(headers)}"
                    }, status=400)

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
                        return Response({
                            "statusCode": 400,
                            "status": False,
                            "message": f"Missing required headers. Required: {', '.join(required_headers)}. Found: {', '.join(row_lower.keys())}."
                        }, status=400)
                    data.append(row_lower)

            else:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Unsupported file format. Use .xlsx or .csv",
                }, status=400)

            imported_count = 0
            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")
                name = str(row.get("factor for")).strip() if row.get("factor for") else None
                description = str(row.get("description")).strip() if row.get("description") else ""

                if not name:
                    skipped_rows.append({"Row": row_number, "Reason": "Missing name"})
                    continue

                existing = FactorFor.objects.filter(name__iexact=name).first()
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({"Row": row_number, "Factor For": name, "Reason": "Already exists"})
                        continue
                    else:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    FactorFor.objects.create(name=name, description=description, is_deleted=False)
                    imported_count += 1

        except Exception as e:
            return Response({"statusCode": 400, "status": False, "message": str(e)}, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": duplicates,
            "skipped_rows": skipped_rows
        }, status=200)
    




class AgeGroupListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['name', 'description', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = AgeGroup.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(Q(name__istartswith=search))

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = AgeGroupSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


# ---------------- CREATE ----------------
class AgeGroupCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        name = request.data.get("name", "").strip()
        existing = AgeGroup.objects.filter(name__iexact=name, is_deleted=False).first()
        if existing:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "AgeGroup with this name already exists."
            }, status=400)

        serializer = AgeGroupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "AgeGroup created successfully",
                "data": serializer.data
            })
        else:
            messages = []
            for field, msgs in serializer.errors.items():
                messages.extend(msgs)
            return Response({
                "statusCode": 400,
                "status": False,
                "message": " ".join(messages)
            }, status=400)


# ---------------- RETRIEVE ----------------
class AgeGroupRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = AgeGroup.objects.get(uuid=uuid, is_deleted=False)
        except AgeGroup.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "AgeGroup not found",
                "data": None
            }, status=404)

        serializer = AgeGroupSerializer(obj)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "AgeGroup retrieved successfully",
            "data": serializer.data
        })


# ---------------- UPDATE ----------------
class AgeGroupUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = AgeGroup.objects.get(uuid=uuid, is_deleted=False)
        except AgeGroup.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "AgeGroup not found",
                "data": None
            }, status=404)

        serializer = AgeGroupSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "AgeGroup updated successfully",
                "data": serializer.data
            })
        else:
            messages = []
            for field, msgs in serializer.errors.items():
                messages.extend(msgs)
            return Response({
                "statusCode": 400,
                "status": False,
                "message": " ".join(messages),
                "data": None
            }, status=400)


# ---------------- DELETE ----------------
class AgeGroupDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get('id', None)

        if uuid:
            try:
                obj = AgeGroup.objects.get(uuid=uuid)
                obj.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "AgeGroup permanently deleted.",
                    "data": None
                }, status=204)
            except AgeGroup.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "AgeGroup not found.",
                    "data": None
                }, status=404)

        if ids == "all":
            objs = AgeGroup.objects.all()
            count = objs.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No AgeGroup found to delete.",
                    "data": None
                }, status=404)
            objs.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} AgeGroup permanently deleted.",
                "data": None
            })

        if not ids or not isinstance(ids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide a list of UUIDs in 'id' field or 'all'.",
                "data": None
            }, status=400)

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
            }, status=400)

        objs = AgeGroup.objects.filter(uuid__in=valid_uuids)
        count = objs.count()
        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching AgeGroup found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=404)

        objs.delete()
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} AgeGroup(s) permanently deleted.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        })


# ---------------- EXPORT ----------------
class AgeGroupExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'name': 'Age Group',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'updated_at': 'Modified On',
        }

        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())
        queryset = AgeGroup.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'AgeGroup'

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
            file_name = 'agegroup.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'agegroup.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


# ---------------- IMPORT ----------------
class AgeGroupImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get("file")
        sheet_name = request.data.get("sheet_name")

        if not file:
            return Response({"error": "No file uploaded"}, status=400)

        format_type = file.name.split(".")[-1].lower()
        duplicates = []
        skipped_rows = []
        required_headers = {"age group"}
        optional_headers = {"description"}

        try:
            data = []

            if format_type == "xlsx":
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({
                        "error": "Please provide sheet_name",
                        "available_sheets": available_sheets,
                    }, status=400)

                if sheet_name not in available_sheets:
                    return Response({
                        "error": f'Sheet "{sheet_name}" not found',
                        "available_sheets": available_sheets,
                    }, status=400)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'Sheet "{sheet_name}" is empty.'
                    }, status=400)

                headers = [str(cell.value).strip().lower() if cell.value else "" for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                if not required_headers.issubset(set(headers)):
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f"Missing required headers. Required: {required_headers}, Found: {set(headers)}"
                    }, status=400)

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
                        return Response({
                            "statusCode": 400,
                            "status": False,
                            "message": f"Missing required headers. Required: {', '.join(required_headers)}. Found: {', '.join(row_lower.keys())}."
                        }, status=400)
                    data.append(row_lower)

            else:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Unsupported file format. Use .xlsx or .csv",
                }, status=400)

            imported_count = 0
            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")
                name = str(row.get("age group")).strip() if row.get("age group") else None
                description = str(row.get("description")).strip() if row.get("description") else ""

                if not name:
                    skipped_rows.append({"Row": row_number, "Reason": "Missing name"})
                    continue

                existing = AgeGroup.objects.filter(name__iexact=name).first()
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({"Row": row_number, "Age  Group": name, "Reason": "Already exists"})
                        continue
                    else:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    AgeGroup.objects.create(name=name, description=description, is_deleted=False)
                    imported_count += 1

        except Exception as e:
            return Response({"statusCode": 400, "status": False, "message": str(e)}, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": duplicates,
            "skipped_rows": skipped_rows
        }, status=200)











class AcademicResultGroupListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['name', 'description', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = AcademicResultGroup.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(Q(name__istartswith=search))

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = AcademicResultGroupSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


# ---------------- CREATE ----------------
class AcademicResultGroupCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        name = request.data.get("name", "").strip()
        existing = AcademicResultGroup.objects.filter(name__iexact=name, is_deleted=False).first()
        if existing:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "AcademicResultGroup with this name already exists."
            }, status=400)

        serializer = AcademicResultGroupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "AcademicResultGroup created successfully",
                "data": serializer.data
            })
        else:
            messages = []
            for field, msgs in serializer.errors.items():
                messages.extend(msgs)
            return Response({
                "statusCode": 400,
                "status": False,
                "message": " ".join(messages)
            }, status=400)


# ---------------- RETRIEVE ----------------
class AcademicResultGroupRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = AcademicResultGroup.objects.get(uuid=uuid, is_deleted=False)
        except AcademicResultGroup.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "AcademicResultGroup not found",
                "data": None
            }, status=404)

        serializer = AcademicResultGroupSerializer(obj)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "AcademicResultGroup retrieved successfully",
            "data": serializer.data
        })


# ---------------- UPDATE ----------------
class AcademicResultGroupUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = AcademicResultGroup.objects.get(uuid=uuid, is_deleted=False)
        except AcademicResultGroup.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "AcademicResultGroup not found",
                "data": None
            }, status=404)

        serializer = AcademicResultGroupSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "AcademicResultGroup updated successfully",
                "data": serializer.data
            })
        else:
            messages = []
            for field, msgs in serializer.errors.items():
                messages.extend(msgs)
            return Response({
                "statusCode": 400,
                "status": False,
                "message": " ".join(messages),
                "data": None
            }, status=400)


# ---------------- DELETE ----------------
class AcademicResultGroupDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get('id', None)

        if uuid:
            try:
                obj = AcademicResultGroup.objects.get(uuid=uuid)
                obj.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "AcademicResultGroup permanently deleted.",
                    "data": None
                }, status=204)
            except AcademicResultGroup.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "AcademicResultGroup not found.",
                    "data": None
                }, status=404)

        if ids == "all":
            objs = AcademicResultGroup.objects.all()
            count = objs.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No AcademicResultGroup found to delete.",
                    "data": None
                }, status=404)
            objs.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} AcademicResultGroup permanently deleted.",
                "data": None
            })

        if not ids or not isinstance(ids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide a list of UUIDs in 'id' field or 'all'.",
                "data": None
            }, status=400)

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
            }, status=400)

        objs = AcademicResultGroup.objects.filter(uuid__in=valid_uuids)
        count = objs.count()
        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching AcademicResultGroup found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=404)

        objs.delete()
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} AcademicResultGroup(s) permanently deleted.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        })


# ---------------- EXPORT ----------------
class AcademicResultGroupExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'name': 'Academic Result',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'updated_at': 'Modified On',
        }

        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())
        queryset = AcademicResultGroup.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'AcademicResultGroup'

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
            file_name = 'academicresultgroup.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'academicresultgroup.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


# ---------------- IMPORT ----------------
class AcademicResultGroupImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get("file")
        sheet_name = request.data.get("sheet_name")

        if not file:
            return Response({"error": "No file uploaded"}, status=400)

        format_type = file.name.split(".")[-1].lower()
        duplicates = []
        skipped_rows = []
        required_headers = {"academic result"}
        optional_headers = {"description"}

        try:
            data = []

            if format_type == "xlsx":
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({
                        "error": "Please provide sheet_name",
                        "available_sheets": available_sheets,
                    }, status=400)

                if sheet_name not in available_sheets:
                    return Response({
                        "error": f'Sheet "{sheet_name}" not found',
                        "available_sheets": available_sheets,
                    }, status=400)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'Sheet "{sheet_name}" is empty.'
                    }, status=400)

                headers = [str(cell.value).strip().lower() if cell.value else "" for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                if not required_headers.issubset(set(headers)):
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f"Missing required headers. Required: {required_headers}, Found: {set(headers)}"
                    }, status=400)

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
                        return Response({
                            "statusCode": 400,
                            "status": False,
                            "message": f"Missing required headers. Required: {', '.join(required_headers)}. Found: {', '.join(row_lower.keys())}."
                        }, status=400)
                    data.append(row_lower)

            else:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Unsupported file format. Use .xlsx or .csv",
                }, status=400)

            imported_count = 0
            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")
                name = str(row.get("academic result")).strip() if row.get("academic result") else None
                description = str(row.get("description")).strip() if row.get("description") else ""

                if not name:
                    skipped_rows.append({"Row": row_number, "Reason": "Missing name"})
                    continue

                existing = AcademicResultGroup.objects.filter(name__iexact=name).first()
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({"Row": row_number, "Academic Result": name, "Reason": "Already exists"})
                        continue
                    else:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    AcademicResultGroup.objects.create(name=name, description=description, is_deleted=False)
                    imported_count += 1

        except Exception as e:
            return Response({"statusCode": 400, "status": False, "message": str(e)}, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": duplicates,
            "skipped_rows": skipped_rows
        }, status=200)


        

class BacklogsGroupListAPIView(APIView):
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['name', 'description', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = BacklogsGroup.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(Q(name__istartswith=search))

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = BacklogsGroupSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


# -------------------- Create API --------------------
class BacklogsGroupCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        name = request.data.get("name", "").strip()
        existing = BacklogsGroup.objects.filter(name__iexact=name, is_deleted=False).first()

        if existing:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "BacklogsGroup with this name already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = BacklogsGroupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "BacklogsGroup created successfully",
                "data": serializer.data
            })
        else:
            messages = []
            for field, msgs in serializer.errors.items():
                messages.extend(msgs)
            return Response({
                "statusCode": 400,
                "status": False,
                "message": " ".join(messages)
            }, status=status.HTTP_400_BAD_REQUEST)


# -------------------- Retrieve API --------------------
class BacklogsGroupRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            group = BacklogsGroup.objects.get(uuid=uuid, is_deleted=False)
        except BacklogsGroup.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "BacklogsGroup not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = BacklogsGroupSerializer(group)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "BacklogsGroup retrieved successfully",
            "data": serializer.data
        })


# -------------------- Update API --------------------
class BacklogsGroupUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            group = BacklogsGroup.objects.get(uuid=uuid, is_deleted=False)
        except BacklogsGroup.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "BacklogsGroup not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = BacklogsGroupSerializer(group, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "BacklogsGroup updated successfully",
                "data": serializer.data
            })
        else:
            messages = []
            for field, msgs in serializer.errors.items():
                messages.extend(msgs)
            return Response({
                "statusCode": 400,
                "status": False,
                "message": " ".join(messages),
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)


# -------------------- Delete API --------------------
class BacklogsGroupDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get('id', None)

        if uuid:
            try:
                group = BacklogsGroup.objects.get(uuid=uuid)
                group.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "BacklogsGroup permanently deleted.",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            except BacklogsGroup.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "BacklogsGroup not found.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        if ids == "all":
            groups = BacklogsGroup.objects.all()
            count = groups.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No BacklogsGroups found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
            groups.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} BacklogsGroups permanently deleted.",
                "data": None
            })

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

        groups = BacklogsGroup.objects.filter(uuid__in=valid_uuids)
        count = groups.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching BacklogsGroups found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_404_NOT_FOUND)

        groups.delete()

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} BacklogsGroup(s) permanently deleted.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        })


# -------------------- Export API --------------------
class BacklogsGroupExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'name': 'BackLogs',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'updated_at': 'Modified On',
            'created_at': 'Created On',
        }

        if fields:
            field_list = [f.strip() for f in fields.split(',')]
        else:
            field_list = list(field_header_map.keys())

        queryset = BacklogsGroup.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'BacklogsGroup'

        for bg in queryset:
            row = []
            for field in field_list:
                value = getattr(bg, field, '')
                if field in ['created_at', 'updated_at'] and value:
                    value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
                elif isinstance(value, bool):
                    value = int(value)
                row.append(value if value is not None else '')
            dataset.append(row)

        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'backlogsgroups.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'backlogsgroups.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


# -------------------- Import API --------------------
class BacklogsGroupImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get("file")
        sheet_name = request.data.get("sheet_name")

        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split(".")[-1].lower()
        duplicates = []
        skipped_rows = []
        required_headers = {"backlogs"}  # adjust as needed
        optional_headers = {"description"}

        try:
            data = []

            if format_type == "xlsx":
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({
                        "error": "Please provide sheet_name",
                        "available_sheets": available_sheets,
                    }, status=400)

                if sheet_name not in available_sheets:
                    return Response({
                        "error": f'Sheet "{sheet_name}" not found',
                        "available_sheets": available_sheets,
                    }, status=400)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'Sheet "{sheet_name}" is empty.'
                    }, status=400)

                headers = [str(cell.value).strip().lower() if cell.value else "" for cell in next(ws.iter_rows(min_row=1, max_row=1))]

                if not required_headers.issubset(set(headers)):
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f"Missing required headers. Required: {required_headers}, Found: {set(headers)}"
                    }, status=400)

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
                        return Response({
                            "statusCode": 400,
                            "status": False,
                            "message": f"Missing required headers. Required: {', '.join(required_headers)}. Found: {', '.join(row_lower.keys())}."
                        }, status=400)
                    data.append(row_lower)
            else:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Unsupported file format. Use .xlsx or .csv",
                }, status=400)

            imported_count = 0
            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")
                name = str(row.get("backlogs")) if row.get("backlogs") else None
                description = str(row.get("description")).strip() if row.get("description") else ""

                if not name:
                    skipped_rows.append({"Row": row_number, "Reason": "Missing name"})
                    continue

                existing = BacklogsGroup.objects.filter(name__iexact=name).first()
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({"Row": row_number, "Backlogs": name, "Reason": "Already exists"})
                        continue
                    else:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    BacklogsGroup.objects.create(name=name, description=description, is_deleted=False)
                    imported_count += 1

        except Exception as e:
            return Response({"statusCode": 400, "status": False, "message": str(e)}, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": duplicates,
            "skipped_rows": skipped_rows
        }, status=200)




# -------------------- List API --------------------
class GAPGroupListAPIView(APIView):
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['name', 'description', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = GAPGroup.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(Q(name__istartswith=search))

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = GAPGroupSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


# -------------------- Create API --------------------
class GAPGroupCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        name = request.data.get("name", "").strip()
        existing = GAPGroup.objects.filter(name__iexact=name, is_deleted=False).first()

        if existing:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "GAPGroup with this name already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = GAPGroupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "GAPGroup created successfully",
                "data": serializer.data
            })
        else:
            messages = []
            for field, msgs in serializer.errors.items():
                messages.extend(msgs)
            return Response({
                "statusCode": 400,
                "status": False,
                "message": " ".join(messages)
            }, status=status.HTTP_400_BAD_REQUEST)


# -------------------- Retrieve API --------------------
class GAPGroupRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            group = GAPGroup.objects.get(uuid=uuid, is_deleted=False)
        except GAPGroup.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "GAPGroup not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = GAPGroupSerializer(group)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "GAPGroup retrieved successfully",
            "data": serializer.data
        })


# -------------------- Update API --------------------
class GAPGroupUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            group = GAPGroup.objects.get(uuid=uuid, is_deleted=False)
        except GAPGroup.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "GAPGroup not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = GAPGroupSerializer(group, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "GAPGroup updated successfully",
                "data": serializer.data
            })
        else:
            messages = []
            for field, msgs in serializer.errors.items():
                messages.extend(msgs)
            return Response({
                "statusCode": 400,
                "status": False,
                "message": " ".join(messages),
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)


# -------------------- Delete API --------------------
class GAPGroupDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get('id', None)

        if uuid:
            try:
                group = GAPGroup.objects.get(uuid=uuid)
                group.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "GAPGroup permanently deleted.",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            except GAPGroup.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "GAPGroup not found.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        if ids == "all":
            groups = GAPGroup.objects.all()
            count = groups.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No GAPGroups found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
            groups.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} GAPGroups permanently deleted.",
                "data": None
            })

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

        groups = GAPGroup.objects.filter(uuid__in=valid_uuids)
        count = groups.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching GAPGroups found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_404_NOT_FOUND)

        groups.delete()

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} GAPGroup(s) permanently deleted.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        })


# -------------------- Export API --------------------
class GAPGroupExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'name': 'GAP Group',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'updated_at': 'Modified On',
            'created_at': 'Created On',
        }

        if fields:
            field_list = [f.strip() for f in fields.split(',')]
        else:
            field_list = list(field_header_map.keys())

        queryset = GAPGroup.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'GAPGroup'

        for group in queryset:
            row = []
            for field in field_list:
                value = getattr(group, field, '')
                if field in ['created_at', 'updated_at'] and value:
                    value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
                elif isinstance(value, bool):
                    value = int(value)
                row.append(value if value is not None else '')
            dataset.append(row)

        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'gapgroups.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'gapgroups.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


# -------------------- Import API --------------------
class GAPGroupImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get("file")
        sheet_name = request.data.get("sheet_name")

        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split(".")[-1].lower()
        duplicates = []
        skipped_rows = []
        required_headers = {"gap group"}  # adjust as needed
        optional_headers = {"description"}

        try:
            data = []

            if format_type == "xlsx":
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({
                        "error": "Please provide sheet_name",
                        "available_sheets": available_sheets,
                    }, status=400)

                if sheet_name not in available_sheets:
                    return Response({
                        "error": f'Sheet "{sheet_name}" not found',
                        "available_sheets": available_sheets,
                    }, status=400)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'Sheet "{sheet_name}" is empty.'
                    }, status=400)

                headers = [str(cell.value).strip().lower() if cell.value else "" for cell in next(ws.iter_rows(min_row=1, max_row=1))]

                if not required_headers.issubset(set(headers)):
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f"Missing required headers. Required: {required_headers}, Found: {set(headers)}"
                    }, status=400)

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
                        return Response({
                            "statusCode": 400,
                            "status": False,
                            "message": f"Missing required headers. Required: {', '.join(required_headers)}. Found: {', '.join(row_lower.keys())}."
                        }, status=400)
                    data.append(row_lower)
            else:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Unsupported file format. Use .xlsx or .csv",
                }, status=400)

            imported_count = 0
            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")
                name = str(row.get("gap group")) if row.get("gap group") else None
                description = str(row.get("description")).strip() if row.get("description") else ""

                if not name:
                    skipped_rows.append({"Row": row_number, "Reason": "Missing name"})
                    continue

                existing = GAPGroup.objects.filter(name__iexact=name).first()
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({"Row": row_number, "GAP Group": name, "Reason": "Already exists"})
                        continue
                    else:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    GAPGroup.objects.create(name=name, description=description, is_deleted=False)
                    imported_count += 1

        except Exception as e:
            return Response({"statusCode": 400, "status": False, "message": str(e)}, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": duplicates,
            "skipped_rows": skipped_rows
        }, status=200)




# -------------------- List API --------------------
class LanguageAbilityGroupListAPIView(APIView):
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['name', 'description', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = LanguageAbilityGroup.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(Q(name__istartswith=search))

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = LanguageAbilityGroupSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


# -------------------- Create API --------------------
class LanguageAbilityGroupCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        name = request.data.get("name", "").strip()
        existing = LanguageAbilityGroup.objects.filter(name__iexact=name, is_deleted=False).first()

        if existing:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "LanguageAbilityGroup with this name already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = LanguageAbilityGroupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "LanguageAbilityGroup created successfully",
                "data": serializer.data
            })
        else:
            messages = []
            for field, msgs in serializer.errors.items():
                messages.extend(msgs)
            return Response({
                "statusCode": 400,
                "status": False,
                "message": " ".join(messages)
            }, status=status.HTTP_400_BAD_REQUEST)


# -------------------- Retrieve API --------------------
class LanguageAbilityGroupRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            group = LanguageAbilityGroup.objects.get(uuid=uuid, is_deleted=False)
        except LanguageAbilityGroup.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "LanguageAbilityGroup not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = LanguageAbilityGroupSerializer(group)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "LanguageAbilityGroup retrieved successfully",
            "data": serializer.data
        })


# -------------------- Update API --------------------
class LanguageAbilityGroupUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            group = LanguageAbilityGroup.objects.get(uuid=uuid, is_deleted=False)
        except LanguageAbilityGroup.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "LanguageAbilityGroup not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = LanguageAbilityGroupSerializer(group, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "LanguageAbilityGroup updated successfully",
                "data": serializer.data
            })
        else:
            messages = []
            for field, msgs in serializer.errors.items():
                messages.extend(msgs)
            return Response({
                "statusCode": 400,
                "status": False,
                "message": " ".join(messages),
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)


# -------------------- Delete API --------------------
class LanguageAbilityGroupDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get('id', None)

        if uuid:
            try:
                group = LanguageAbilityGroup.objects.get(uuid=uuid)
                group.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "LanguageAbilityGroup permanently deleted.",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            except LanguageAbilityGroup.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "LanguageAbilityGroup not found.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        if ids == "all":
            groups = LanguageAbilityGroup.objects.all()
            count = groups.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No LanguageAbilityGroups found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
            groups.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} LanguageAbilityGroups permanently deleted.",
                "data": None
            })

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

        groups = LanguageAbilityGroup.objects.filter(uuid__in=valid_uuids)
        count = groups.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching LanguageAbilityGroups found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_404_NOT_FOUND)

        groups.delete()

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} LanguageAbilityGroup(s) permanently deleted.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        })


# -------------------- Export API --------------------
class LanguageAbilityGroupExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'name': 'Language Ability',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'updated_at': 'Modified On',
            'created_at': 'Created On',
        }

        if fields:
            field_list = [f.strip() for f in fields.split(',')]
        else:
            field_list = list(field_header_map.keys())

        queryset = LanguageAbilityGroup.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'LanguageAbilityGroup'

        for group in queryset:
            row = []
            for field in field_list:
                value = getattr(group, field, '')
                if field in ['created_at', 'updated_at'] and value:
                    value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
                elif isinstance(value, bool):
                    value = int(value)
                row.append(value if value is not None else '')
            dataset.append(row)

        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'languageabilitygroups.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'languageabilitygroups.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


# -------------------- Import API --------------------
class LanguageAbilityGroupImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get("file")
        sheet_name = request.data.get("sheet_name")

        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split(".")[-1].lower()
        duplicates = []
        skipped_rows = []
        required_headers = {"language ability group"}  # adjust as needed
        optional_headers = {"description"}

        try:
            data = []

            if format_type == "xlsx":
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({
                        "error": "Please provide sheet_name",
                        "available_sheets": available_sheets,
                    }, status=400)

                if sheet_name not in available_sheets:
                    return Response({
                        "error": f'Sheet "{sheet_name}" not found',
                        "available_sheets": available_sheets,
                    }, status=400)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'Sheet "{sheet_name}" is empty.'
                    }, status=400)

                headers = [str(cell.value).strip().lower() if cell.value else "" for cell in next(ws.iter_rows(min_row=1, max_row=1))]

                if not required_headers.issubset(set(headers)):
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f"Missing required headers. Required: {required_headers}, Found: {set(headers)}"
                    }, status=400)

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
                        return Response({
                            "statusCode": 400,
                            "status": False,
                            "message": f"Missing required headers. Required: {', '.join(required_headers)}. Found: {', '.join(row_lower.keys())}."
                        }, status=400)
                    data.append(row_lower)
            else:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Unsupported file format. Use .xlsx or .csv",
                }, status=400)

            imported_count = 0
            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")
                name = str(row.get("language ability group")) if row.get("language ability group") else None
                description = str(row.get("description")).strip() if row.get("description") else ""

                if not name:
                    skipped_rows.append({"Row": row_number, "Reason": "Missing name"})
                    continue

                existing = LanguageAbilityGroup.objects.filter(name__iexact=name).first()
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({"Row": row_number, "Language Ability Group": name, "Reason": "Already exists"})
                        continue
                    else:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    LanguageAbilityGroup.objects.create(name=name, description=description, is_deleted=False)
                    imported_count += 1

        except Exception as e:
            return Response({"statusCode": 400, "status": False, "message": str(e)}, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": duplicates,
            "skipped_rows": skipped_rows
        }, status=200)




# -------------------- List API --------------------
class EntranceTestAbilityGroupListAPIView(APIView):
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['name', 'description', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = EntranceTestAbilityGroup.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(Q(name__istartswith=search))

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = EntranceTestAbilityGroupSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


# -------------------- Create API --------------------
class EntranceTestAbilityGroupCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        name = request.data.get("name", "").strip()
        existing = EntranceTestAbilityGroup.objects.filter(name__iexact=name, is_deleted=False).first()

        if existing:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "EntranceTestAbilityGroup with this name already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = EntranceTestAbilityGroupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "EntranceTestAbilityGroup created successfully",
                "data": serializer.data
            })
        else:
            messages = []
            for field, msgs in serializer.errors.items():
                messages.extend(msgs)
            return Response({
                "statusCode": 400,
                "status": False,
                "message": " ".join(messages)
            }, status=status.HTTP_400_BAD_REQUEST)


# -------------------- Retrieve API --------------------
class EntranceTestAbilityGroupRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            group = EntranceTestAbilityGroup.objects.get(uuid=uuid, is_deleted=False)
        except EntranceTestAbilityGroup.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "EntranceTestAbilityGroup not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = EntranceTestAbilityGroupSerializer(group)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "EntranceTestAbilityGroup retrieved successfully",
            "data": serializer.data
        })


# -------------------- Update API --------------------
class EntranceTestAbilityGroupUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            group = EntranceTestAbilityGroup.objects.get(uuid=uuid, is_deleted=False)
        except EntranceTestAbilityGroup.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "EntranceTestAbilityGroup not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = EntranceTestAbilityGroupSerializer(group, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "EntranceTestAbilityGroup updated successfully",
                "data": serializer.data
            })
        else:
            messages = []
            for field, msgs in serializer.errors.items():
                messages.extend(msgs)
            return Response({
                "statusCode": 400,
                "status": False,
                "message": " ".join(messages),
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)


# -------------------- Delete API --------------------
class EntranceTestAbilityGroupDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get('id', None)

        if uuid:
            try:
                group = EntranceTestAbilityGroup.objects.get(uuid=uuid)
                group.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "EntranceTestAbilityGroup permanently deleted.",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            except EntranceTestAbilityGroup.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "EntranceTestAbilityGroup not found.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        if ids == "all":
            groups = EntranceTestAbilityGroup.objects.all()
            count = groups.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No EntranceTestAbilityGroups found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
            groups.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} EntranceTestAbilityGroups permanently deleted.",
                "data": None
            })

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

        groups = EntranceTestAbilityGroup.objects.filter(uuid__in=valid_uuids)
        count = groups.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching EntranceTestAbilityGroups found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_404_NOT_FOUND)

        groups.delete()

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} EntranceTestAbilityGroup(s) permanently deleted.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        })


# -------------------- Export API --------------------
class EntranceTestAbilityGroupExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'name': 'Entrance Test Ability Group',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'updated_at': 'Modified On',
            'created_at': 'Created On',
        }

        if fields:
            field_list = [f.strip() for f in fields.split(',')]
        else:
            field_list = list(field_header_map.keys())

        queryset = EntranceTestAbilityGroup.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'EntranceTestAbilityGroup'

        for group in queryset:
            row = []
            for field in field_list:
                value = getattr(group, field, '')
                if field in ['created_at', 'updated_at'] and value:
                    value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
                elif isinstance(value, bool):
                    value = int(value)
                row.append(value if value is not None else '')
            dataset.append(row)

        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'entrancetestabilitygroups.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'entrancetestabilitygroups.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


# -------------------- Import API --------------------
class EntranceTestAbilityGroupImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get("file")
        sheet_name = request.data.get("sheet_name")

        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split(".")[-1].lower()
        duplicates = []
        skipped_rows = []
        required_headers = {"entrance test ability group"}  # adjust as needed
        optional_headers = {"description"}

        try:
            data = []

            if format_type == "xlsx":
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({
                        "error": "Please provide sheet_name",
                        "available_sheets": available_sheets,
                    }, status=400)

                if sheet_name not in available_sheets:
                    return Response({
                        "error": f'Sheet "{sheet_name}" not found',
                        "available_sheets": available_sheets,
                    }, status=400)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'Sheet "{sheet_name}" is empty.'
                    }, status=400)

                headers = [str(cell.value).strip().lower() if cell.value else "" for cell in next(ws.iter_rows(min_row=1, max_row=1))]

                if not required_headers.issubset(set(headers)):
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f"Missing required headers. Required: {required_headers}, Found: {set(headers)}"
                    }, status=400)

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
                        return Response({
                            "statusCode": 400,
                            "status": False,
                            "message": f"Missing required headers. Required: {', '.join(required_headers)}. Found: {', '.join(row_lower.keys())}."
                        }, status=400)
                    data.append(row_lower)
            else:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Unsupported file format. Use .xlsx or .csv",
                }, status=400)

            imported_count = 0
            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")
                name = str(row.get("entrance test ability group")) if row.get("entrance test ability group") else None
                description = str(row.get("description")).strip() if row.get("description") else ""

                if not name:
                    skipped_rows.append({"Row": row_number, "Reason": "Missing name"})
                    continue

                existing = EntranceTestAbilityGroup.objects.filter(name__iexact=name).first()
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({"Row": row_number, "Entrance Test Ability Group": name, "Reason": "Already exists"})
                        continue
                    else:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    EntranceTestAbilityGroup.objects.create(name=name, description=description, is_deleted=False)
                    imported_count += 1

        except Exception as e:
            return Response({"statusCode": 400, "status": False, "message": str(e)}, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": duplicates,
            "skipped_rows": skipped_rows
        }, status=200)





# -------------------- Age List API --------------------
class StudyFactorAgeListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = [
            'minimum_age_months', 
            'maximum_age_months',
            'updated_at'
        ]
        
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = StudyFactorAge.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(study_age_group__name__istartswith=search) |
                Q(factor_for__name__istartswith=search)
            )

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = StudyFactorAgeSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)



# -------------------- Age Create API --------------------

class StudyFactorAgeCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    @transaction.atomic
    def post(self, request):
        try:
            data = request.data

            # Required fields validation
            factor_for_uuid = data.get("factor_for")
            age_group_uuid = data.get("study_age_group")
            min_age = data.get("minimum_age_months")
            max_age = data.get("maximum_age_months")
            country_uuids = data.get("country", [])
            course_level_uuids = data.get("course_level", [])

            missing_fields = []
            if not factor_for_uuid:
                missing_fields.append("factor_for")
            if not age_group_uuid:
                missing_fields.append("study_age_group")
            if min_age is None:
                missing_fields.append("minimum_age_months")
            if max_age is None:
                missing_fields.append("maximum_age_months")

            if missing_fields:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": f"Missing required fields: {', '.join(missing_fields)}"
                }, status=400)

            # Convert ages safely
            try:
                min_age = int(min_age)
                max_age = int(max_age)
            except ValueError:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "minimum_age_months and maximum_age_months must be integers."
                }, status=400)

            # Fetch FK using UUIDs
            try:
                factor_for = FactorFor.objects.get(uuid=factor_for_uuid, is_deleted=False)
            except FactorFor.DoesNotExist:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Invalid factor_for UUID"
                }, status=400)

            try:
                age_group = AgeGroup.objects.get(uuid=age_group_uuid, is_deleted=False)
            except AgeGroup.DoesNotExist:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Invalid study_age_group UUID"
                }, status=400)

            # Duplicate check
            if StudyFactorAge.objects.filter(
                factor_for=factor_for,
                study_age_group=age_group,
                minimum_age_months=min_age,
                maximum_age_months=max_age,
                is_deleted=False
            ).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Age entry already exists with these details."
                }, status=400)

            # Atomic transaction begins
            with transaction.atomic():

                obj = StudyFactorAge.objects.create(
                    factor_for=factor_for,
                    study_age_group=age_group,
                    minimum_age_months=min_age,
                    maximum_age_months=max_age,
                    description=data.get("description", "")
                )

                # Assign Countries
                if country_uuids:
                    valid_countries = Country.objects.filter(uuid__in=country_uuids)
                    if valid_countries.count() != len(country_uuids):
                        return Response({
                            "statusCode": 400,
                            "status": False,
                            "message": "One or more country UUIDs are invalid."
                        }, status=400)
                    obj.country.set(valid_countries)

                # Assign Course Levels
                if course_level_uuids:
                    valid_levels = CourseLevel.objects.filter(uuid__in=course_level_uuids)
                    if valid_levels.count() != len(course_level_uuids):
                        return Response({
                            "statusCode": 400,
                            "status": False,
                            "message": "One or more course_level UUIDs are invalid."
                        }, status=400)
                    obj.course_level.set(valid_levels)

                obj.save()

            # Final response
            serializer = StudyFactorAgeSerializer(obj)

            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Age created successfully",
                "data": serializer.data
            })

        except Exception as e:
            # Debug-friendly but safe
            return Response({
                "statusCode": 500,
                "status": False,
                "message": "Internal server error",
                "error": str(e)  
            }, status=500)


# -------------------- Age Retrieve API --------------------

class StudyFactorAgeRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        try:
            search = request.GET.get('search', '').strip()
            sort_by = request.GET.get('sortBy', 'created_at')
            sort_order = request.GET.get('sortOrder', 'desc')

            # Allowed sort fields
            allowed_sort_fields = [
                'minimum_age_months',
                'maximum_age_months',
                'created_at',
                'updated_at',
            ]

            # Validate sortBy
            if sort_by not in allowed_sort_fields:
                sort_by = 'created_at'

            # Apply desc/asc
            if sort_order == 'desc':
                sort_by = f'-{sort_by}'

            # Base queryset
            queryset = StudyFactorAge.objects.filter(is_deleted=False)

            # Search
            if search:
                queryset = queryset.filter(
                    Q(study_age_group__name__icontains=search) |
                    Q(factor_for__name__icontains=search)
                )

            # Sorting
            queryset = queryset.order_by(sort_by)

            # Pagination
            paginator = CustomPagination()
            paginated_queryset = paginator.paginate_queryset(queryset, request)

            # Serialization
            serializer = StudyFactorAgeSerializer(paginated_queryset, many=True)

            return paginator.get_paginated_response(serializer.data)

        except ValidationError as ve:
            return Response({
                "status": False,
                "message": "Validation error",
                "error": str(ve),
            }, status=status.HTTP_400_BAD_REQUEST)

        except DatabaseError as db_err:
            return Response({
                "status": False,
                "message": "Database error occurred",
                "error": str(db_err),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            # Catch-all for unexpected issues
            return Response({
                "status": False,
                "message": "Something went wrong",
                "error": str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# -------------------- Age Update API--------------------

# class StudyFactorAgeUpdateAPIView(APIView):
#     permission_classes = [IsAuthenticated, IsAdminUser]

#     def put(self, request, uuid):
#         try:
#             obj = StudyFactorAge.objects.get(uuid=uuid, is_deleted=False)
#         except StudyFactorAge.DoesNotExist:
#             return Response({
#                 "statusCode": 404,
#                 "status": False,
#                 "message": "Age entry not found",
#                 "data": None
#             }, status=404)

#         serializer = StudyFactorAgeSerializer(obj, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({
#                 "statusCode": 200,
#                 "status": True,
#                 "message": "Age updated successfully",
#                 "data": serializer.data
#             })

#         messages = []
#         for field, msgs in serializer.errors.items():
#             messages.extend(msgs)

#         return Response({
#             "statusCode": 400,
#             "status": False,
#             "message": " ".join(messages),
#             "data": None
#         }, status=400)

class StudyFactorAgeUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    @transaction.atomic
    def patch(self, request, uuid):
        # Fetch object
        try:
            obj = StudyFactorAge.objects.get(uuid=uuid, is_deleted=False)
        except StudyFactorAge.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Age entry not found",
                "data": None
            }, status=404)

        # Partial update
        serializer = StudyFactorAgeSerializer(obj, data=request.data, partial=True)

        if serializer.is_valid():
            try:
                serializer.save()  # atomic
            except Exception as e:
                transaction.set_rollback(True)
                return Response({
                    "statusCode": 500,
                    "status": False,
                    "message": f"Update failed: {str(e)}",
                    "data": None
                }, status=500)

            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Age updated successfully",
                "data": serializer.data
            })

        # Flatten validation errors
        errors = []
        for field, msgs in serializer.errors.items():
            errors.extend(msgs)

        return Response({
            "statusCode": 400,
            "status": False,
            "message": " ".join(errors),
            "data": None
        }, status=400)
    
# -------------------- Age Delete API --------------------

class StudyFactorAgeDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get('id', None)

        # ---------------- SINGLE DELETE ----------------
        if uuid:
            try:
                obj = StudyFactorAge.objects.get(uuid=uuid)
                obj.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "Age entry permanently deleted.",
                    "data": None
                }, status=204)
            except StudyFactorAge.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Age entry not found.",
                    "data": None
                }, status=404)

        # ---------------- DELETE ALL ----------------
        if ids == "all":
            objs = StudyFactorAge.objects.all()
            count = objs.count()

            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No Age entries found to delete.",
                    "data": None
                }, status=404)

            objs.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} Age entries permanently deleted.",
                "data": None
            })

        # ---------------- MULTIPLE DELETE ----------------
        if not ids or not isinstance(ids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Provide list of UUIDs in 'id' field or 'all'.",
                "data": None
            }, status=400)

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
            }, status=400)

        objs = StudyFactorAge.objects.filter(uuid__in=valid_uuids)
        count = objs.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching Age entries found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=404)

        objs.delete()

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} Age entries permanently deleted.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        })


# ---------------- Age EXPORT ----------------
class StudyFactorAgeExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'factor_for': 'Factor For',
            'study_age_group': 'Study Age Group',
            'minimum_age_months': 'Minimum Age',
            'maximum_age_months': 'Maximum Age',
            'country': 'Country',
            'course_level': 'Course Level',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'updated_at': 'Modified On',
        }

        # determine which fields to export
        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())

        queryset = StudyFactorAge.objects.filter(is_deleted=False)
        if uuids:
            # validate uuids
            valid_uuids = []
            for u in uuids:
                try:
                    valid_uuids.append(UUID(u))
                except Exception:
                    # ignore invalid uuid strings
                    pass
            if valid_uuids:
                queryset = queryset.filter(uuid__in=valid_uuids)

        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'Age'

        for obj in queryset:
            row = []
            for field in field_list:
                # handle special fields
                if field == 'factor_for':
                    value = obj.factor_for.name if obj.factor_for else ''
                elif field == 'study_age_group':
                    value = obj.study_age_group.name if obj.study_age_group else ''
                elif field == 'country':
                    # M2M -> comma separated names
                    value = ", ".join([c.name for c in obj.country.all()]) if obj.country.exists() else ''
                elif field == 'course_level':
                    value = ", ".join([cl.name for cl in obj.course_level.all()]) if obj.course_level.exists() else ''
                else:
                    value = getattr(obj, field, '')

                if field in ['created_at', 'updated_at'] and value:
                    try:
                        value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
                    except Exception:
                        # fallback to string representation
                        value = str(value)
                elif isinstance(value, bool):
                    value = int(value)

                row.append(value if value is not None else '')
            dataset.append(row)

        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'age.csv'
            response_content = file_data
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'age.xlsx'
            response_content = file_data.getvalue()

        response = HttpResponse(response_content, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


# ---------------- Age IMPORT ----------------
class StudyFactorAgeImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get("file")
        sheet_name = request.data.get("sheet_name")

        if not file:
            return Response({"error": "No file uploaded"}, status=400)

        format_type = file.name.split(".")[-1].lower()
        duplicates = []
        skipped_rows = []
        # required headers (lowercase) as per your confirmation
        required_headers = {
            "factor for",
            "study age group",
            "minimum age",
            "maximum age",
            "country",
            "course level"
        }
        optional_headers = {"description"}

        try:
            data = []

            if format_type == "xlsx":
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({
                        "error": "Please provide sheet_name",
                        "available_sheets": available_sheets,
                    }, status=400)

                if sheet_name not in available_sheets:
                    return Response({
                        "error": f'Sheet "{sheet_name}" not found',
                        "available_sheets": available_sheets,
                    }, status=400)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'Sheet "{sheet_name}" is empty.'
                    }, status=400)

                headers = [str(cell.value).strip().lower() if cell.value else "" for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                if not required_headers.issubset(set(headers)):
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f"Missing required headers. Required: {required_headers}, Found: {set(headers)}"
                    }, status=400)

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
                        return Response({
                            "statusCode": 400,
                            "status": False,
                            "message": f"Missing required headers. Required: {', '.join(required_headers)}. Found: {', '.join(row_lower.keys())}."
                        }, status=400)
                    data.append(row_lower)

            else:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Unsupported file format. Use .xlsx or .csv",
                }, status=400)

            imported_count = 0

            # iterate reversed to keep same import behavior as your other modules
            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")

                factor_for_name = str(row.get("factor for")).strip() if row.get("factor for") else None
                study_age_group_name = str(row.get("study age group")).strip() if row.get("study age group") else None

                # numeric fields - try to coerce to int
                try:
                    minimum_age = int(row.get("minimum age (months)")) if row.get("minimum age (months)") not in (None, "") else None
                except Exception:
                    minimum_age = None
                try:
                    maximum_age = int(row.get("maximum age (months)")) if row.get("maximum age (months)") not in (None, "") else None
                except Exception:
                    maximum_age = None

                countries_raw = str(row.get("country")).strip() if row.get("country") else ""
                course_levels_raw = str(row.get("course level")).strip() if row.get("course level") else ""
                description = str(row.get("description")).strip() if row.get("description") else ""

                # basic validations
                if not factor_for_name:
                    skipped_rows.append({"Row": row_number, "Reason": "Missing factor for"})
                    continue
                if not study_age_group_name:
                    skipped_rows.append({"Row": row_number, "Reason": "Missing study age group"})
                    continue
                if minimum_age is None:
                    skipped_rows.append({"Row": row_number, "Reason": "Missing or invalid minimum age (months)"})
                    continue
                if maximum_age is None:
                    skipped_rows.append({"Row": row_number, "Reason": "Missing or invalid maximum age (months)"})
                    continue

                # lookup foreign keys by name (case-insensitive)
                factor_for_obj = FactorFor.objects.filter(name__iexact=factor_for_name).first()
                if not factor_for_obj:
                    skipped_rows.append({"Row": row_number, "Reason": f'FactorFor "{factor_for_name}" not found'})
                    continue

                study_age_group_obj = AgeGroup.objects.filter(name__iexact=study_age_group_name).first()
                if not study_age_group_obj:
                    skipped_rows.append({"Row": row_number, "Reason": f'AgeGroup "{study_age_group_name}" not found'})
                    continue

                # parse M2M names and resolve objects
                country_names = [c.strip() for c in countries_raw.split(",") if c.strip()]
                course_level_names = [cl.strip() for cl in course_levels_raw.split(",") if cl.strip()]

                country_objs = []
                missing_countries = []
                for cn in country_names:
                    co = Country.objects.filter(name__iexact=cn).first()
                    if co:
                        country_objs.append(co)
                    else:
                        missing_countries.append(cn)

                course_level_objs = []
                missing_course_levels = []
                for cln in course_level_names:
                    clo = CourseLevel.objects.filter(name__iexact=cln).first()
                    if clo:
                        course_level_objs.append(clo)
                    else:
                        missing_course_levels.append(cln)

                if missing_countries:
                    skipped_rows.append({"Row": row_number, "Reason": f"Countries not found: {', '.join(missing_countries)}"})
                    continue

                if missing_course_levels:
                    skipped_rows.append({"Row": row_number, "Reason": f"Course Levels not found: {', '.join(missing_course_levels)}"})
                    continue

                # duplicate detection:
                existing = StudyFactorAge.objects.filter(
                    factor_for__id=factor_for_obj.id,
                    study_age_group__id=study_age_group_obj.id,
                    minimum_age_months=minimum_age,
                    maximum_age_months=maximum_age
                ).first()

                if existing:
                    if not existing.is_deleted:
                        duplicates.append({
                            "Row": row_number,
                            "Factor For": factor_for_name,
                            "Study Age Group": study_age_group_name,
                            "Reason": "Already exists"
                        })
                        continue
                    else:
                        # revive soft deleted record & update fields
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        # update m2m
                        if country_objs:
                            existing.country.set(country_objs)
                        if course_level_objs:
                            existing.course_level.set(course_level_objs)
                        imported_count += 1
                        continue

                # create new Age record
                age_obj = StudyFactorAge.objects.create(
                    factor_for=factor_for_obj,
                    study_age_group=study_age_group_obj,
                    minimum_age_months=minimum_age,
                    maximum_age_months=maximum_age,
                    description=description,
                    is_deleted=False
                )
                if country_objs:
                    age_obj.country.set(country_objs)
                if course_level_objs:
                    age_obj.course_level.set(course_level_objs)

                imported_count += 1

        except Exception as e:
            return Response({"statusCode": 400, "status": False, "message": str(e)}, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": duplicates,
            "skipped_rows": skipped_rows
        }, status=200)




# ---------------- LIST ----------------
class StudyFactorAcademicResultListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):

        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = [
            'updated_at',
        ]

        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        if sort_order == 'desc':
            sort_by = f"-{sort_by}"

        queryset = AcademicResult.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(factor_for__name__istartswith=search) |
                Q(academic_result_group__name__istartswith=search)
            )

        queryset = queryset.order_by(sort_by)

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = AcademicResultSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)


# ---------------- CREATE ----------------
class StudyFactorAcademicResultCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        factor_for = request.data.get("factor_for")
        academic_result_group = request.data.get("academic_result_group")
        min_result = request.data.get("minimum_academic_result_required")

        # Duplicate check
        existing = AcademicResult.objects.filter(
            factor_for_id=factor_for,
            academic_result_group_id=academic_result_group,
            minimum_academic_result_required_id=min_result,
            is_deleted=False
        ).first()

        if existing:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Academic Result already exists with these details."
            }, status=400)

        serializer = AcademicResultSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Academic Result created successfully",
                "data": serializer.data
            })

        errors = []
        for field, msgs in serializer.errors.items():
            errors.extend(msgs)

        return Response({
            "statusCode": 400,
            "status": False,
            "message": " ".join(errors)
        }, status=400)


# ---------------- RETRIEVE ----------------
class StudyFactorAcademicResultRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):

        try:
            obj = AcademicResult.objects.get(uuid=uuid, is_deleted=False)
        except AcademicResult.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Academic Result not found",
                "data": None
            }, status=404)

        serializer = AcademicResultSerializer(obj)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Academic Result retrieved successfully",
            "data": serializer.data
        })


# ---------------- UPDATE ----------------
class StudyFactorAcademicResultUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):

        try:
            obj = AcademicResult.objects.get(uuid=uuid, is_deleted=False)
        except AcademicResult.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Academic Result not found",
                "data": None
            }, status=404)

        serializer = AcademicResultSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()

            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Academic Result updated successfully",
                "data": serializer.data
            })

        errors = []
        for field, msgs in serializer.errors.items():
            errors.extend(msgs)

        return Response({
            "statusCode": 400,
            "status": False,
            "message": " ".join(errors),
            "data": None
        }, status=400)


# ---------------- DELETE ----------------
class StudyFactorAcademicResultDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):

        ids = request.data.get("id")

        # ---- SINGLE DELETE ----
        if uuid:
            try:
                obj = AcademicResult.objects.get(uuid=uuid)
                obj.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "Academic Result permanently deleted.",
                    "data": None
                }, status=204)
            except AcademicResult.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Academic Result not found.",
                    "data": None
                }, status=404)

        # ---- DELETE ALL ----
        if ids == "all":
            objs = AcademicResult.objects.all()
            count = objs.count()

            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No Academic Results found to delete.",
                    "data": None
                }, status=404)

            objs.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} Academic Results permanently deleted.",
                "data": None
            })

        # ---- MULTIPLE DELETE ----
        if not ids or not isinstance(ids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Provide list of UUIDs in 'id' field or 'all'.",
                "data": None
            }, status=400)

        valid = []
        invalid = []

        for v in ids:
            try:
                valid.append(UUID(v))
            except ValueError:
                invalid.append(v)

        if not valid:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "No valid UUIDs provided.",
                "data": {"invalid_uuids": invalid}
            }, status=400)

        objs = AcademicResult.objects.filter(uuid__in=valid)
        count = objs.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching Academic Results found.",
                "data": {"invalid_uuids": invalid} if invalid else None
            }, status=404)

        objs.delete()

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} Academic Result(s) permanently deleted.",
            "data": {"invalid_uuids": invalid} if invalid else None
        })


class StudyFactorAcademicResultExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        # Map model fields to friendly headers
        field_header_map = {
            'uuid': 'UUID',
            # We will export related names for these fields
            'factor_for': 'Factor For',
            'academic_result_group': 'Academic Result Group',
            'minimum_academic_result_required': 'Minimum Academic Result Required',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'updated_at': 'Modified On',
        }

        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())
        queryset = StudyFactorAcademicResult.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'StudyFactorAcademicResult'

        for obj in queryset:
            row = []
            for field in field_list:
                # handle related name fields specially
                if field == 'factor_for':
                    value = getattr(obj.factor_for, 'name', '') if obj.factor_for else ''
                elif field == 'academic_result_group':
                    value = getattr(obj.academic_result_group, 'name', '') if obj.academic_result_group else ''
                elif field == 'minimum_academic_result_required':
                    value = getattr(obj.minimum_academic_result_required, 'name', '') if obj.minimum_academic_result_required else ''
                else:
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
            file_name = 'study_factor_academic_result.csv'
            response_content = file_data
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'study_factor_academic_result.xlsx'
            response_content = file_data.getvalue()

        response = HttpResponse(response_content, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


class StudyFactorAcademicResultImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get("file")
        sheet_name = request.data.get("sheet_name")

        if not file:
            return Response({"error": "No file uploaded"}, status=400)

        format_type = file.name.split(".")[-1].lower()
        duplicates = []
        skipped_rows = []
        required_headers = {"factor for", "academic result group", "minimum academic result required"}
        optional_headers = {"description"}

        try:
            data = []

            if format_type == "xlsx":
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({
                        "error": "Please provide sheet_name",
                        "available_sheets": available_sheets,
                    }, status=400)

                if sheet_name not in available_sheets:
                    return Response({
                        "error": f'Sheet "{sheet_name}" not found',
                        "available_sheets": available_sheets,
                    }, status=400)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'Sheet "{sheet_name}" is empty.'
                    }, status=400)

                headers = [str(cell.value).strip().lower() if cell.value else "" for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                if not required_headers.issubset(set(headers)):
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f"Missing required headers. Required: {required_headers}, Found: {set(headers)}"
                    }, status=400)

                for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    # skip completely empty rows
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
                        return Response({
                            "statusCode": 400,
                            "status": False,
                            "message": f"Missing required headers. Required: {', '.join(required_headers)}. Found: {', '.join(row_lower.keys())}."
                        }, status=400)
                    data.append(row_lower)
            else:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Unsupported file format. Use .xlsx or .csv",
                }, status=400)

            imported_count = 0

            # iterate reversed to keep same ordering behavior as reference
            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")

                factor_for_val = str(row.get("factor for")).strip() if row.get("factor for") else None
                academic_group_val = str(row.get("academic result group")).strip() if row.get("academic result group") else None
                min_result_val = str(row.get("minimum academic result required")).strip() if row.get("minimum academic result required") else None
                description = str(row.get("description")).strip() if row.get("description") else ""

                if not (factor_for_val and academic_group_val and min_result_val):
                    skipped_rows.append({"Row": row_number, "Reason": "Missing required fields"})
                    continue

                # Find related objects by name (case-insensitive)
                factor_obj = FactorFor.objects.filter(name__iexact=factor_for_val).first()
                if not factor_obj:
                    skipped_rows.append({"Row": row_number, "Reason": f'Factor For "{factor_for_val}" not found'})
                    continue

                group_obj = AcademicResultGroup.objects.filter(name__iexact=academic_group_val).first()
                if not group_obj:
                    skipped_rows.append({"Row": row_number, "Reason": f'Academic Result Group "{academic_group_val}" not found'})
                    continue

                min_result_obj = AcademicResultType.objects.filter(name__iexact=min_result_val).first()
                if not min_result_obj:
                    skipped_rows.append({"Row": row_number, "Reason": f'Minimum Academic Result Required "{min_result_val}" not found'})
                    continue

                # Duplicate check
                existing = StudyFactorAcademicResult.objects.filter(
                    factor_for=factor_obj,
                    academic_result_group=group_obj,
                    minimum_academic_result_required=min_result_obj
                ).first()

                if existing:
                    if not existing.is_deleted:
                        duplicates.append({
                            "Row": row_number,
                            "Factor For": factor_for_val,
                            "Academic Result Group": academic_group_val,
                            "Minimum Academic Result Required": min_result_val,
                            "Reason": "Already exists"
                        })
                        continue
                    else:
                        # restore soft-deleted record and update description
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                        continue

                # create new record
                StudyFactorAcademicResult.objects.create(
                    factor_for=factor_obj,
                    academic_result_group=group_obj,
                    minimum_academic_result_required=min_result_obj,
                    description=description,
                    is_deleted=False
                )
                imported_count += 1

        except Exception as e:
            return Response({"statusCode": 400, "status": False, "message": str(e)}, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": duplicates,
            "skipped_rows": skipped_rows
        }, status=200)





class StudyFactorBacklogsListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get("search", "").strip()
        sort_by = request.GET.get("sortBy", "created_at")
        sort_order = request.GET.get("sortOrder", "desc")

        allowed_sort_fields = ["factor_for__name", "backlog_group__name", "updated_at"]
        if sort_by not in allowed_sort_fields:
            sort_by = "created_at"

        if sort_order == "desc":
            sort_by = f"-{sort_by}"

        queryset = StudyFactorBacklogs.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(factor_for__name__istartswith=search) |
                Q(backlog_group__name__istartswith=search)
            )

        queryset = queryset.order_by(sort_by)

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = StudyFactorBacklogsSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)


class StudyFactorBacklogsCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        factor_for = request.data.get("factor_for")
        backlog_group = request.data.get("backlog_group")

        exists = StudyFactorBacklogs.objects.filter(
            factor_for_id=factor_for,
            backlog_group_id=backlog_group,
            is_deleted=False
        ).first()

        if exists:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Entry already exists for this FactorFor & BacklogGroup."
            }, status=400)

        serializer = StudyFactorBacklogsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Study Factor Backlogs created successfully",
                "data": serializer.data
            })
        else:
            messages = []
            for field, msgs in serializer.errors.items():
                messages.extend(msgs)

            return Response({
                "statusCode": 400,
                "status": False,
                "message": " ".join(messages)
            }, status=400)


class StudyFactorBacklogsRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = StudyFactorBacklogs.objects.get(uuid=uuid, is_deleted=False)
        except StudyFactorBacklogs.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "StudyFactorBacklogs not found",
                "data": None
            }, status=404)

        serializer = StudyFactorBacklogsSerializer(obj)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "StudyFactorBacklogs retrieved successfully",
            "data": serializer.data
        })


class StudyFactorBacklogsUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = StudyFactorBacklogs.objects.get(uuid=uuid, is_deleted=False)
        except StudyFactorBacklogs.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "StudyFactorBacklogs not found",
                "data": None
            }, status=404)

        serializer = StudyFactorBacklogsSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "StudyFactorBacklogs updated successfully",
                "data": serializer.data
            })
        else:
            messages = []
            for field, msgs in serializer.errors.items():
                messages.extend(msgs)

            return Response({
                "statusCode": 400,
                "status": False,
                "message": " ".join(messages),
                "data": None
            }, status=400)


class StudyFactorBacklogsDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get("id", None)

        # Delete single by UUID
        if uuid:
            try:
                obj = StudyFactorBacklogs.objects.get(uuid=uuid)
                obj.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "StudyFactorBacklogs permanently deleted.",
                    "data": None
                }, status=204)
            except StudyFactorBacklogs.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "StudyFactorBacklogs not found.",
                    "data": None
                }, status=404)

        # Delete ALL
        if ids == "all":
            objs = StudyFactorBacklogs.objects.all()
            count = objs.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No entries found to delete.",
                    "data": None
                }, status=404)
            objs.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} StudyFactorBacklogs permanently deleted.",
                "data": None
            })

        # Delete MULTIPLE
        if not ids or not isinstance(ids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide a list of UUIDs or 'all'.",
                "data": None
            }, status=400)

        valid_uuids = []
        invalid_uuids = []
        for u in ids:
            try:
                valid_uuids.append(UUID(u))
            except ValueError:
                invalid_uuids.append(u)

        objs = StudyFactorBacklogs.objects.filter(uuid__in=valid_uuids)
        count = objs.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching records found.",
                "data": {"invalid_uuids": invalid_uuids}
            }, status=404)

        objs.delete()
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} StudyFactorBacklogs deleted.",
            "data": {"invalid_uuids": invalid_uuids}
        })


class StudyFactorBacklogsExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get("format", "xlsx").lower()
        fields = request.GET.get("fields")
        uuids_param = request.GET.get("uuids", "")

        uuids = [u.strip() for u in uuids_param.split(",") if u]

        field_header_map = {
            "uuid": "UUID",
            "factor_for_name": "Factor For",
            "backlog_group_name": "Backlog Group",
            "backlog_accepted": "Backlog Accepted",
            "max_backlogs": "Max Backlogs",
            "description": "Description",
            "updated_at": "Modified On",
        }

        field_list = [f.strip() for f in fields.split(",")] if fields else list(field_header_map.keys())
        queryset = StudyFactorBacklogs.objects.filter(is_deleted=False)

        if uuids:
            queryset = queryset.filter(uuid__in=uuids)

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]

        for obj in queryset:
            row = []
            for field in field_list:
                value = getattr(obj, field, "")

                if field == "factor_for_name":
                    value = obj.factor_for.name

                if field == "backlog_group_name":
                    value = obj.backlog_group.name

                if field == "updated_at" and value:
                    value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")

                if isinstance(value, bool):
                    value = int(value)

                row.append(value)

            dataset.append(row)

        if format_type == "csv":
            file_data = dataset.export("csv")
            content_type = "text/csv"
            file_name = "study_factor_backlogs.csv"
        else:
            file_data = io.BytesIO(dataset.export("xlsx"))
            content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            file_name = "study_factor_backlogs.xlsx"

        response = HttpResponse(
            file_data if format_type == "csv" else file_data.getvalue(),
            content_type=content_type
        )
        response["Content-Disposition"] = f'attachment; filename="{file_name}"'
        return response


class StudyFactorBacklogsImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    REQUIRED_HEADERS = {"factor for", "backlog group"}
    OPTIONAL_HEADERS = {"backlog accepted", "maximum backlogs accepted", "description"}

    def post(self, request):
        file = request.FILES.get("file")
        sheet_name = request.data.get("sheet_name")

        if not file:
            return Response({"error": "No file uploaded"}, status=400)

        format_type = file.name.split(".")[-1].lower()
        duplicates = []
        skipped = []
        data = []

        try:
            # Read file like FactorFor import
            if format_type == "xlsx":
                wb = openpyxl.load_workbook(file, read_only=True)
                sheets = wb.sheetnames

                if not sheet_name:
                    return Response({
                        "error": "Please provide sheet_name",
                        "available": sheets
                    }, status=400)

                if sheet_name not in sheets:
                    return Response({
                        "error": f"Sheet '{sheet_name}' not found",
                        "available": sheets
                    }, status=400)

                ws = wb[sheet_name]
                headers = [str(c.value).strip().lower() for c in next(ws.iter_rows(min_row=1, max_row=1))]

                if not self.REQUIRED_HEADERS.issubset(headers):
                    return Response({
                        "error": "Missing required headers",
                        "required": list(self.REQUIRED_HEADERS)
                    }, status=400)

                for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    row_dict = dict(zip(headers, row))
                    row_dict["_row"] = idx
                    data.append(row_dict)

            elif format_type == "csv":
                decoded = file.read().decode("utf-8")
                dataset = Dataset()
                dataset.load(decoded, format="csv")
                for idx, row in enumerate(dataset.dict, start=2):
                    row_lower = {k.lower(): v for k, v in row.items()}
                    row_lower["_row"] = idx
                    data.append(row_lower)

            else:
                return Response({"error": "Invalid format. Use xlsx/csv"}, status=400)

            imported = 0

            for row in data:
                row_no = row["_row"]

                factor_for = row.get("factor for")
                backlog_group = row.get("backlog group")

                if not factor_for or not backlog_group:
                    skipped.append({"row": row_no, "reason": "Missing required values"})
                    continue

                try:
                    factor_for_fk = FactorFor.objects.get(name__iexact=factor_for)
                    backlog_group_fk =BacklogsGroup.objects.get(name__iexact=backlog_group)
                except:
                    skipped.append({"row": row_no, "reason": "Invalid FK"})
                    continue

                exists = StudyFactorBacklogs.objects.filter(
                    factor_for=factor_for_fk,
                    backlog_group=backlog_group_fk,
                    is_deleted=False
                ).first()

                if exists:
                    duplicates.append({"row": row_no, "factor_for": factor_for})
                    continue

                StudyFactorBacklogs.objects.create(
                    factor_for=factor_for_fk,
                    backlog_group=backlog_group_fk,
                    backlog_accepted=bool(row.get("backlog accepted", False)),
                    max_backlogs=int(row.get("maximum backlogs accepted", 0) or 0),
                    description=row.get("description") or "",
                )

                imported += 1

            return Response({
                "status": True,
                "imported": imported,
                "duplicates": duplicates,
                "skipped": skipped
            })

        except Exception as e:
            return Response({"error": str(e)}, status=400)




class StudyFactorGAPListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = StudyFactorGAP.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(factor_for__name__istartswith=search) |
                Q(gap_group__name__istartswith=search)
            )

        queryset = queryset.order_by(sort_by)

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = StudyFactorGAPSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)


class StudyFactorGAPCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        serializer = StudyFactorGAPSerializer(data=request.data)
        if serializer.is_valid():
            obj = serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Study Factor GAP created successfully",
                "data": StudyFactorGAPSerializer(obj).data
            })
        else:
            messages = []
            for field, msgs in serializer.errors.items():
                messages.extend(msgs)
            return Response({"statusCode": 400, "status": False, "message": " ".join(messages)}, status=400)


class StudyFactorGAPRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = StudyFactorGAP.objects.get(uuid=uuid, is_deleted=False)
        except StudyFactorGAP.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Study Factor GAP not found",
                "data": None
            }, status=404)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Study Factor GAP retrieved successfully",
            "data": StudyFactorGAPSerializer(obj).data
        })

class StudyFactorGAPUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = StudyFactorGAP.objects.get(uuid=uuid, is_deleted=False)
        except StudyFactorGAP.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "Not found"}, status=404)

        serializer = StudyFactorGAPSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Study Factor GAP updated successfully",
                "data": serializer.data
            })
        messages = []
        for field, msgs in serializer.errors.items():
            messages.extend(msgs)
        return Response({"statusCode": 400, "status": False, "message": " ".join(messages)}, status=400)


class StudyFactorGAPDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get('id', None)

        if uuid:
            try:
                obj = StudyFactorGAP.objects.get(uuid=uuid)
                obj.delete()
                return Response({"statusCode": 204, "status": True, "message": "Deleted"}, status=204)
            except StudyFactorGAP.DoesNotExist:
                return Response({"statusCode": 404, "status": False, "message": "Not found"}, status=404)

        return Response({
            "statusCode": 400,
            "status": False,
            "message": "Bulk delete not implemented yet"
        }, status=400)


# ---------------- EXPORT ----------------
class StudyFactorGAPExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'factor_for': 'Factor For',
            'gap_group': 'GAP Group',
            'maximum_gap_accepted': 'Maximum GAP Accepted (Months)',
            'countries': 'Countries',
            'institute_types': 'Institute Types',
            'course_levels': 'Course Levels',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'created_at': 'Created On',
            'updated_at': 'Modified On',
        }

        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())

        queryset = StudyFactorGAP.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = "StudyFactorGAP"

        for obj in queryset:
            row = []
            for field in field_list:
                value = getattr(obj, field, "")

                # Handle many-to-many fields
                if field == "countries":
                    value = ", ".join(obj.countries.values_list("name", flat=True))

                elif field == "institute_types":
                    value = ", ".join(obj.institute_types.values_list("name", flat=True))

                elif field == "course_levels":
                    value = ", ".join(obj.course_levels.values_list("name", flat=True))

                # Handle datetime formatting
                elif field in ["created_at", "updated_at"] and value:
                    value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")

                # Booleans → int
                elif isinstance(value, bool):
                    value = int(value)

                # Foreign keys → string display
                elif field in ["factor_for", "gap_group"] and value:
                    value = str(value)

                row.append(value if value is not None else "")

            dataset.append(row)

        if format_type == "csv":
            file_data = dataset.export("csv")
            content_type = "text/csv"
            file_name = "study_factor_gap.csv"
        else:
            file_data = io.BytesIO(dataset.export("xlsx"))
            content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            file_name = "study_factor_gap.xlsx"

        response = HttpResponse(
            file_data if format_type == "csv" else file_data.getvalue(),
            content_type=content_type
        )
        response["Content-Disposition"] = f'attachment; filename="{file_name}"'
        return response

# ---------------- IMPORT ----------------
class StudyFactorGAPImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get("file")
        sheet_name = request.data.get("sheet_name")

        if not file:
            return Response({"error": "No file uploaded"}, status=400)

        format_type = file.name.split(".")[-1].lower()
        duplicates = []
        skipped_rows = []

        required_headers = {
            "factor for",
            "gap group",
            "maximum gap accepted (months)",
            "countries",
            "institute types",
            "course levels",
        }

        optional_headers = {"description"}

        try:
            data = []

            # ---------------- XLSX Handling ----------------
            if format_type == "xlsx":
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({
                        "error": "Please provide sheet_name",
                        "available_sheets": available_sheets,
                    }, status=400)

                if sheet_name not in available_sheets:
                    return Response({
                        "error": f'Sheet "{sheet_name}" not found',
                        "available_sheets": available_sheets,
                    }, status=400)

                ws = wb[sheet_name]

                if ws.max_row <= 1:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'Sheet "{sheet_name}" is empty.'
                    }, status=400)

                headers = [str(c.value).strip().lower() if c.value else "" for c in next(ws.iter_rows(min_row=1, max_row=1))]

                if not required_headers.issubset(set(headers)):
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f"Missing required headers. Required: {required_headers}, Found: {set(headers)}"
                    }, status=400)

                for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    row_dict["_row_number"] = idx
                    data.append(row_dict)

            # ---------------- CSV Handling ----------------
            elif format_type == "csv":
                decoded = file.read().decode("utf-8")
                dataset = Dataset()
                dataset.load(decoded, format="csv")

                for idx, row in enumerate(dataset.dict, start=2):
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    row_lower["_row_number"] = idx
                    if not required_headers.issubset(row_lower.keys()):
                        return Response({
                            "status": False,
                            "statusCode": 400,
                            "message": f"Missing required headers. Required: {', '.join(required_headers)}"
                        }, status=400)
                    data.append(row_lower)

            else:
                return Response({
                    "status": False,
                    "statusCode": 400,
                    "message": "Unsupported file type. Use XLSX or CSV"
                }, status=400)

            # ---------------- Import Logic ----------------
            imported_count = 0

            for row in reversed(data):
                row_num = row.get("_row_number")

                # Extract fields
                factor_for_name = str(row.get("factor for")).strip()
                gap_group_name = str(row.get("gap group")).strip()
                max_gap = row.get("maximum gap accepted (months)")
                description = str(row.get("description") or "").strip()

                # Many-To-Many CSV-style inputs
                country_names = [c.strip() for c in str(row.get("countries") or "").split(",") if c.strip()]
                institute_type_names = [i.strip() for i in str(row.get("institute types") or "").split(",") if i.strip()]
                course_level_names = [c.strip() for c in str(row.get("course levels") or "").split(",") if c.strip()]

                # Required field missing
                if not (factor_for_name and gap_group_name and max_gap is not None):
                    skipped_rows.append({"Row": row_num, "Reason": "Missing required fields"})
                    continue

                # Foreign key resolution
                factor_for = FactorFor.objects.filter(name__iexact=factor_for_name).first()
                gap_group = GAPGroup.objects.filter(name__iexact=gap_group_name).first()

                if not factor_for or not gap_group:
                    skipped_rows.append({"Row": row_num, "Reason": "Invalid FK values"})
                    continue

                # Duplicate check
                existing = StudyFactorGAP.objects.filter(
                    factor_for=factor_for,
                    gap_group=gap_group,
                    maximum_gap_accepted=max_gap,
                ).first()

                if existing and not existing.is_deleted:
                    duplicates.append({
                        "Row": row_num,
                        "Reason": "Record already exists"
                    })
                    continue

                if existing and existing.is_deleted:
                    # Reactivate
                    obj = existing
                    obj.is_deleted = False
                    obj.description = description
                    obj.save()
                else:
                    # Create new
                    obj = StudyFactorGAP.objects.create(
                        factor_for=factor_for,
                        gap_group=gap_group,
                        maximum_gap_accepted=max_gap,
                        description=description
                    )

                # Many-to-many mappings
                obj.countries.set(Country.objects.filter(name__in=country_names))
                obj.institute_types.set(InstituteType.objects.filter(name__in=institute_type_names))
                obj.course_levels.set(CourseLevel.objects.filter(name__in=course_level_names))

                imported_count += 1

        except Exception as e:
            return Response({
                "status": False,
                "statusCode": 400,
                "message": str(e)
            }, status=400)

        return Response({
            "status": True,
            "statusCode": 200,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": duplicates,
            "skipped_rows": skipped_rows,
        }, status=200)


#--------------------LanguageAbility----------------------

class StudyFactorLanguageAbilityCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def resolve_fk(self, model, value):
        if not value:
            return None
        try:
            return model.objects.get(uuid=value)
        except:
            return model.objects.filter(name__iexact=value).first()

    def post(self, request):
        data = request.data.copy()

        fk_map = {
            "factor_for": FactorFor,
            "language_ability_group": LanguageAbilityGroup,
            "language_test_name": LanguageTest,
            "module_name": LanguagetestmoduleName,
            "minimum_overall_score": LanguageTestResult,
            "not_less_than": LanguageTestResult,
        }

        for field, model in fk_map.items():
            val = data.get(field)
            resolved = self.resolve_fk(model, val)
            if not resolved:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": f"Invalid {field.replace('_', ' ').title()}"
                }, status=400)
            data[field] = resolved.id

        serializer = StudyFactorLanguageAbilitySerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Study Factor Language Ability created successfully",
                "data": serializer.data
            })

        messages = []
        for field, msgs in serializer.errors.items():
            messages.extend(msgs)

        return Response({
            "statusCode": 400,
            "status": False,
            "message": " ".join(messages)
        }, status=400)

class StudyFactorLanguageAbilityListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get("search", "").strip()
        sort_by = request.GET.get("sortBy", "created_at")
        sort_order = request.GET.get("sortOrder", "desc")

        allowed_sort_fields = [
            "updated_at",
            "created_at",
            "in_no_of_modules"
        ]

        if sort_by not in allowed_sort_fields:
            sort_by = "created_at"

        if sort_order == "desc":
            sort_by = f"-{sort_by}"

        queryset = StudyFactorLanguageAbility.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(factor_for__name__istartswith=search) |
                Q(language_test_name__name__istartswith=search)
            )

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = StudyFactorLanguageAbilitySerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)

class StudyFactorLanguageAbilityRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = StudyFactorLanguageAbility.objects.get(uuid=uuid, is_deleted=False)
        except StudyFactorLanguageAbility.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Study Factor Language Ability not found",
                "data": None
            }, status=404)

        serializer = StudyFactorLanguageAbilitySerializer(obj)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Study Factor Language Ability retrieved successfully",
            "data": serializer.data
        })

class StudyFactorLanguageAbilityUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def resolve_fk(self, model, value):
        if not value:
            return None
        try:
            return model.objects.get(uuid=value)
        except:
            return model.objects.filter(name__iexact=value).first()

    def put(self, request, uuid):
        try:
            obj = StudyFactorLanguageAbility.objects.get(uuid=uuid, is_deleted=False)
        except StudyFactorLanguageAbility.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Study Factor Language Ability not found",
                "data": None
            }, 404)

        data = request.data.copy()

        fk_map = {
            "factor_for": FactorFor,
            "language_ability_group": LanguageAbilityGroup,
            "language_test_name": LanguageTest,
            "module_name": LanguagetestmoduleName,
            "minimum_overall_score": LanguageTestResult,
            "not_less_than": LanguageTestResult,
        }

        for field, model in fk_map.items():
            if field in data:
                val = data.get(field)
                resolved = self.resolve_fk(model, val)
                if not resolved:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f"Invalid {field.replace('_', ' ').title()}"
                    }, status=400)
                data[field] = resolved.id

        serializer = StudyFactorLanguageAbilitySerializer(obj, data=data)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Study Factor Language Ability updated successfully",
                "data": serializer.data
            })

        messages = []
        for field, msgs in serializer.errors.items():
            messages.extend(msgs)

        return Response({
            "statusCode": 400,
            "status": False,
            "message": " ".join(messages)
        }, status=400)

class StudyFactorLanguageAbilityDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get("id")

        if uuid:
            try:
                obj = StudyFactorLanguageAbility.objects.get(uuid=uuid)
                obj.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "Study Factor Language Ability deleted",
                }, 204)
            except:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Not found"
                }, 404)

        if ids == "all":
            count = StudyFactorLanguageAbility.objects.count()
            StudyFactorLanguageAbility.objects.all().delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"Deleted all {count} records."
            })

        if not ids or not isinstance(ids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Provide list of UUIDs or 'all'"
            }, 400)

        valid = []
        invalid = []
        for u in ids:
            try:
                valid.append(UUID(u))
            except:
                invalid.append(u)

        objs = StudyFactorLanguageAbility.objects.filter(uuid__in=valid)
        count = objs.count()
        objs.delete()

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"Deleted {count} items",
            "invalid": invalid if invalid else None
        })

class StudyFactorLanguageAbilityExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get("format", "xlsx").lower()
        fields = request.GET.get("fields")
        uuids_param = request.GET.get("uuids", "")
        uuids = [u.strip() for u in uuids_param.split(",") if u]

        field_header_map = {
            "uuid": "UUID",
            "factor_for": "Factor For",
            "language_ability_group": "Language Ability Group",
            "language_test_name": "Language Test Name",
            "module_name": "Module Name",
            "minimum_overall_score": "Min Overall Score",
            "not_less_than": "Not Less Than",
            "in_no_of_modules": "No of Modules",
            "description": "Description",
            "updated_at": "Modified On",
        }

        field_list = (
            [f.strip() for f in fields.split(",")] if fields else list(field_header_map.keys())
        )

        queryset = StudyFactorLanguageAbility.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)

        queryset = queryset.order_by("-created_at")

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = "StudyFactorLanguageAbility"

        for obj in queryset:
            row = []
            for field in field_list:
                value = getattr(obj, field, "")

                if hasattr(value, "name"):
                    value = value.name

                row.append(value if value is not None else "")
            dataset.append(row)

        if format_type == "csv":
            file_data = dataset.export("csv")
            content_type = "text/csv"
            fname = "studyfactorlanguageability.csv"
        else:
            file_data = io.BytesIO(dataset.export("xlsx"))
            content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            fname = "studyfactorlanguageability.xlsx"

        response = HttpResponse(
            file_data if format_type == "csv" else file_data.getvalue(),
            content_type=content_type
        )
        response["Content-Disposition"] = f'attachment; filename="{fname}"'
        return response

class StudyFactorLanguageAbilityImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def resolve_fk(self, model, value):
        if not value:
            return None
        try:
            return model.objects.get(uuid=value)
        except:
            return model.objects.filter(name__iexact=value).first()

    def post(self, request):
        file = request.FILES.get("file")
        sheet_name = request.data.get("sheet_name")

        if not file:
            return Response({"error": "No file uploaded"}, status=400)

        format_type = file.name.split(".")[-1].lower()

        required_headers = {
            "factor for", "language ability group", "language test name",
            "module name", "minimum overall score", "not less than",
            "in no of modules"
        }

        optional_headers = {"description"}

        # ---- Read File ----
        data = []
        try:
            if format_type == "xlsx":
                wb = openpyxl.load_workbook(file, read_only=True)
                ws = wb[sheet_name]

                headers = [str(c.value).strip().lower() for c in next(ws.iter_rows(min_row=1, max_row=1))]

                if not required_headers.issubset(set(headers)):
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f"Missing required headers. Required: {required_headers}, Found: {set(headers)}"
                    })

                for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    row_dict = dict(zip(headers, row))
                    row_dict["_row"] = idx
                    data.append(row_dict)

            elif format_type == "csv":
                decoded = file.read().decode("utf-8")
                dataset = Dataset()
                dataset.load(decoded, format="csv")

                for idx, row in enumerate(dataset.dict, start=2):
                    row_lower = {k.lower(): v for k, v in row.items()}
                    row_lower["_row"] = idx
                    data.append(row_lower)

            else:
                return Response({"error": "Unsupported file type"}, 400)

        except Exception as e:
            return Response({"error": str(e)}, 400)

        # ---- IMPORT ----
        imported = 0
        duplicates = []
        skipped = []

        for row in reversed(data):
            rowno = row.get("_row")
            ff = row.get("factor for")
            lag = row.get("language ability group")
            ltn = row.get("language test name")
            mn = row.get("module name")
            msc = row.get("minimum overall score")
            nlt = row.get("not less than")

            if not ff:
                skipped.append({"row": rowno, "reason": "Missing factor for"})
                continue

            # Resolve FK
            try:
                resolved = {
                    "factor_for": self.resolve_fk(FactorFor, ff),
                    "language_ability_group": self.resolve_fk(LanguageAbilityGroup, lag),
                    "language_test_name": self.resolve_fk(LanguageTest, ltn),
                    "module_name": self.resolve_fk(LanguagetestmoduleName, mn),
                    "minimum_overall_score": self.resolve_fk(LanguageTestResult, msc),
                    "not_less_than": self.resolve_fk(LanguageTestResult, nlt),
                }
            except:
                skipped.append({"row": rowno, "reason": "Invalid FK value"})
                continue

            if any(v is None for v in resolved.values()):
                skipped.append({"row": rowno, "reason": "One or more FK not found"})
                continue

            record = StudyFactorLanguageAbility.objects.filter(
                factor_for=resolved["factor_for"],
                language_test_name=resolved["language_test_name"],
                module_name=resolved["module_name"]
            ).first()

            if record:
                duplicates.append({"row": rowno, "reason": "Duplicate entry"})
                continue

            StudyFactorLanguageAbility.objects.create(
                **resolved,
                in_no_of_modules=row.get("in no of modules") or 0,
                description=row.get("description") or ""
            )
            imported += 1

        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Import completed",
            "imported": imported,
            "duplicates": duplicates,
            "skipped": skipped
        })


#--------------------EntranctestAbility--------------------

class StudyFactorEntranceTestAbilityCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        serializer = StudyFactorEntranceTestAbilitySerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "StudyFactorEntranceTestAbility created successfully",
                "data": serializer.data
            })
        
        all_errors = []
        for field, msgs in serializer.errors.items():
            all_errors.extend(msgs)

        return Response({
            "statusCode": 400,
            "status": False,
            "message": " ".join(all_errors)
        }, status=400)

class StudyFactorEntranceTestAbilityListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = StudyFactorEntranceTestAbility.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(factor_for__name__istartswith=search) |
                Q(entrance_test_name__name__istartswith=search)
            )

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        page_obj = paginator.paginate_queryset(queryset, request)
        serializer = StudyFactorEntranceTestAbilitySerializer(page_obj, many=True)
        return paginator.get_paginated_response(serializer.data)

class StudyFactorEntranceTestAbilityRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = StudyFactorEntranceTestAbility.objects.get(uuid=uuid, is_deleted=False)
        except StudyFactorEntranceTestAbility.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Record not found"
            }, status=404)

        serializer = StudyFactorEntranceTestAbilitySerializer(obj)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Record retrieved successfully",
            "data": serializer.data
        })

class StudyFactorEntranceTestAbilityUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = StudyFactorEntranceTestAbility.objects.get(uuid=uuid, is_deleted=False)
        except StudyFactorEntranceTestAbility.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Record not found"
            }, status=404)

        serializer = StudyFactorEntranceTestAbilitySerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Record updated successfully",
                "data": serializer.data
            })

        errors = []
        for f, m in serializer.errors.items():
            errors.extend(m)

        return Response({
            "statusCode": 400,
            "status": False,
            "message": " ".join(errors)
        }, status=400)

class StudyFactorEntranceTestAbilityDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get("id")

        if uuid:
            try:
                obj = StudyFactorEntranceTestAbility.objects.get(uuid=uuid)
                obj.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "Deleted successfully"
                }, status=204)
            except StudyFactorEntranceTestAbility.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Record not found"
                }, status=404)

        if ids == "all":
            objects = StudyFactorEntranceTestAbility.objects.all()
            count = objects.count()
            objects.delete()

            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} records deleted"
            })

        return Response({
            "statusCode": 400,
            "status": False,
            "message": "Invalid delete request"
        }, status=400)

class StudyFactorEntranceTestAbilityExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get("format", "xlsx").lower()

        queryset = StudyFactorEntranceTestAbility.objects.filter(is_deleted=False)

        dataset = Dataset()
        dataset.headers = [
            "UUID", "Factor For", "Entrance Test Ability Group",
            "Entrance Test Name", "Minimum Score Required",
            "Description", "Created At", "Updated At"
        ]

        for obj in queryset:
            dataset.append([
                obj.uuid,
                obj.factor_for.name,
                obj.entrance_test_ability_group.name,
                obj.entrance_test_name.name,
                obj.minimum_score_required.name,
                obj.description,
                obj.created_at.strftime("%d-%m-%Y %I:%M:%S %p"),
                obj.updated_at.strftime("%d-%m-%Y %I:%M:%S %p"),
            ])

        if format_type == "csv":
            data = dataset.export("csv")
            content_type = "text/csv"
            filename = "studyfactorentrancetestability.csv"
        else:
            data = dataset.export("xlsx")
            content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            filename = "studyfactorentrancetestability.xlsx"

        response = HttpResponse(data, content_type)
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

class StudyFactorEntranceTestAbilityImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get("file")
        sheet_name = request.data.get("sheet_name")

        if not file:
            return Response({"error": "No file uploaded"}, status=400)

        format_type = file.name.split(".")[-1].lower()

        required_headers = {
            "factor for",
            "entrance test ability group",
            "entrance test name",
            "minimum score required"
        }

        data_rows = []

        try:
            if format_type == "xlsx":
                wb = openpyxl.load_workbook(file)
                sheets = wb.sheetnames

                if sheet_name not in sheets:
                    return Response({"error": "Invalid sheet name", "sheets": sheets}, status=400)

                ws = wb[sheet_name]
                headers = [str(c.value).lower().strip() for c in next(ws.rows)]

                if not required_headers.issubset(set(headers)):
                    return Response({
                        "error": f"Missing required headers {required_headers}"
                    }, status=400)

                for row in ws.iter_rows(min_row=2, values_only=True):
                    data_rows.append(dict(zip(headers, row)))

            else:
                return Response({"error": "Only xlsx import supported"}, status=400)

            imported = 0
            for row in data_rows:

                StudyFactorEntranceTestAbility.objects.create(
                    factor_for=FactorFor.objects.get(name__iexact=row["factor for"]),
                    entrance_test_ability_group=EntranceTestAbilityGroup.objects.get(name__iexact=row["entrance test ability group"]),
                    entrance_test_name=EntranceTestName.objects.get(name__iexact=row["entrance test name"]),
                    minimum_score_required=EntranceTestResult.objects.get(name__iexact=row["minimum score required"]),
                    description=row.get("description", "")
                )
                imported += 1

        except Exception as e:
            return Response({"error": str(e)}, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Import completed",
            "imported_count": imported
        })
