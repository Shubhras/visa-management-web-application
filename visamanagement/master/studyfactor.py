from django.shortcuts import render
from  .models  import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import  *
from django.core.paginator import Paginator
from django.db.models import Q, F
from django.db.models.functions import Lower, Cast
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
                    skipped_rows.append({"Row": row_number,"Academic Result": name or "","Description":description, "Reason": "Missing name"})
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
            "duplicates": list(reversed(duplicates)),
            "skipped_rows": list(reversed(skipped_rows)),
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
# class StudyFactorAgeListAPIView(APIView):
#     permission_classes = [IsAuthenticated, IsAdminUser]

#     def get(self, request):
#         search = request.GET.get('search', '').strip()
#         sort_by = request.GET.get('sortBy', 'created_at')
#         sort_order = request.GET.get('sortOrder', 'desc')

#         allowed_sort_fields = [
#             'minimum_age_months', 
#             'maximum_age_months',
#             'updated_at'
#         ]
        
#         if sort_by not in allowed_sort_fields:
#             sort_by = 'created_at'

#         if sort_order == 'desc':
#             sort_by = f'-{sort_by}'

#         queryset = StudyFactorAge.objects.filter(is_deleted=False)

#         if search:
#             queryset = queryset.filter(
#                 Q(study_age_group__name__istartswith=search) |
#                 Q(factor_for__name__istartswith=search)
#             )

#         queryset = queryset.order_by(sort_by)
#         paginator = CustomPagination()
#         result_page = paginator.paginate_queryset(queryset, request)
#         serializer = StudyFactorAgeSerializer(result_page, many=True)

#         return paginator.get_paginated_response(serializer.data)


class StudyFactorAgeListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        custom_sort = request.GET.get('customSort')  # e.g., minimum_age_months:asc,updated_at:desc

        # Allowed sortable fields (same pattern as Department)
        allowed_sort_fields = [
            'minimum_age_months',
            'maximum_age_months',
            'created_at',
            'updated_at'
        ]

        queryset = StudyFactorAge.objects.filter(is_deleted=False)

        # -------------------------------------
        # SEARCH (ONLY on factor_for.name)
        # -------------------------------------
        if search:
            queryset = queryset.filter(
                Q(factor_for__name__istartswith=search)
            )

        # Mapping sortable fields to ORM fields
        sort_field_map = {
            'minimum_age_months': 'minimum_age_months',
            'maximum_age_months': 'maximum_age_months',
            'created_at': 'created_at',
            'updated_at': 'updated_at',
        }

        sort_fields = []

        # -------------------------------------
        # CUSTOM SORT LOGIC (Exactly same as Department)
        # -------------------------------------
        if custom_sort:
            for rule in custom_sort.split(','):
                try:
                    field, order = rule.split(':')
                    field = field.strip()
                    order = order.strip().lower()

                    if field not in sort_field_map:
                        continue

                    orm_field = sort_field_map[field]

                    # If the field is string (none here), use Lower
                    if field in []:  # No string fields in StudyFactorAge sorting
                        f = Lower(orm_field)
                    else:
                        f = F(orm_field)

                    sort_fields.append(
                        f.asc(nulls_last=True) if order == 'asc'
                        else f.desc(nulls_last=True)
                    )

                except ValueError:
                    continue

        else:
            # Fallback sorting (same as Department)
            sort_by = request.GET.get('sortBy', 'created_at')
            sort_order = request.GET.get('sortOrder', 'desc')

            orm_field = sort_field_map.get(sort_by, 'created_at')
            f = F(orm_field)

            sort_fields = [
                f.asc(nulls_last=True) if sort_order == 'asc'
                else f.desc(nulls_last=True)
            ]

        queryset = queryset.order_by(*sort_fields)

        # Pagination (same as Department)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)

        serializer = StudyFactorAgeSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)



# -------------------- Age Create API --------------------

# class StudyFactorAgeCreateAPIView(APIView):
#     permission_classes = [IsAuthenticated, IsAdminUser]

#     @transaction.atomic
#     def post(self, request):
#         try:
#             data = request.data

#             # Required fields validation
#             factor_for_uuid = data.get("factor_for")
#             age_group_uuid = data.get("study_age_group")
#             min_age = data.get("minimum_age_months")
#             max_age = data.get("maximum_age_months")
#             country_uuids = data.get("country", [])
#             course_level_uuids = data.get("course_level", [])

#             missing_fields = []
#             if not factor_for_uuid:
#                 missing_fields.append("factor_for")
#             if not age_group_uuid:
#                 missing_fields.append("study_age_group")
#             if min_age is None:
#                 missing_fields.append("minimum_age_months")
#             if max_age is None:
#                 missing_fields.append("maximum_age_months")

#             if missing_fields:
#                 return Response({
#                     "statusCode": 400,
#                     "status": False,
#                     "message": f"Missing required fields: {', '.join(missing_fields)}"
#                 }, status=400)

#             # Convert ages safely
#             try:
#                 min_age = int(min_age)
#                 max_age = int(max_age)
#             except ValueError:
#                 return Response({
#                     "statusCode": 400,
#                     "status": False,
#                     "message": "minimum_age_months and maximum_age_months must be integers."
#                 }, status=400)

#             # Fetch FK using UUIDs
#             try:
#                 factor_for = FactorFor.objects.get(uuid=factor_for_uuid, is_deleted=False)
#             except FactorFor.DoesNotExist:
#                 return Response({
#                     "statusCode": 400,
#                     "status": False,
#                     "message": "Invalid factor_for UUID"
#                 }, status=400)

#             try:
#                 age_group = AgeGroup.objects.get(uuid=age_group_uuid, is_deleted=False)
#             except AgeGroup.DoesNotExist:
#                 return Response({
#                     "statusCode": 400,
#                     "status": False,
#                     "message": "Invalid study_age_group UUID"
#                 }, status=400)

#             # Duplicate check
#             if StudyFactorAge.objects.filter(
#                 factor_for=factor_for,
#                 study_age_group=age_group,
#                 minimum_age_months=min_age,
#                 maximum_age_months=max_age,
#                 is_deleted=False
#             ).exists():
#                 return Response({
#                     "statusCode": 400,
#                     "status": False,
#                     "message": "Age entry already exists with these details."
#                 }, status=400)

#             # Atomic transaction begins
#             with transaction.atomic():

#                 obj = StudyFactorAge.objects.create(
#                     factor_for=factor_for,
#                     study_age_group=age_group,
#                     minimum_age_months=min_age,
#                     maximum_age_months=max_age,
#                     description=data.get("description", "")
#                 )

#                 # Assign Countries
#                 if country_uuids:
#                     valid_countries = Country.objects.filter(uuid__in=country_uuids)
#                     if valid_countries.count() != len(country_uuids):
#                         return Response({
#                             "statusCode": 400,
#                             "status": False,
#                             "message": "One or more country UUIDs are invalid."
#                         }, status=400)
#                     obj.country.set(valid_countries)

#                 # Assign Course Levels
#                 if course_level_uuids:
#                     valid_levels = CourseLevel.objects.filter(uuid__in=course_level_uuids)
#                     if valid_levels.count() != len(course_level_uuids):
#                         return Response({
#                             "statusCode": 400,
#                             "status": False,
#                             "message": "One or more course_level UUIDs are invalid."
#                         }, status=400)
#                     obj.course_level.set(valid_levels)

#                 obj.save()

#             # Final response
#             serializer = StudyFactorAgeSerializer(obj)

#             return Response({
#                 "statusCode": 200,
#                 "status": True,
#                 "message": "Age created successfully",
#                 "data": serializer.data
#             })

#         except Exception as e:
#             # Debug-friendly but safe
#             return Response({
#                 "statusCode": 500,
#                 "status": False,
#                 "message": "Internal server error",
#                 "error": str(e)  
#             }, status=500)


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

# class StudyFactorAgeRetrieveAPIView(APIView):
#     permission_classes = [IsAuthenticated, IsAdminUser]

#     def get(self, request):
#         try:
#             search = request.GET.get('search', '').strip()
#             sort_by = request.GET.get('sortBy', 'created_at')
#             sort_order = request.GET.get('sortOrder', 'desc')

#             # Allowed sort fields
#             allowed_sort_fields = [
#                 'minimum_age_months',
#                 'maximum_age_months',
#                 'created_at',
#                 'updated_at',
#             ]

#             # Validate sortBy
#             if sort_by not in allowed_sort_fields:
#                 sort_by = 'created_at'

#             # Apply desc/asc
#             if sort_order == 'desc':
#                 sort_by = f'-{sort_by}'

#             # Base queryset
#             queryset = StudyFactorAge.objects.filter(is_deleted=False)

#             # Search
#             if search:
#                 queryset = queryset.filter(
#                     Q(study_age_group__name__icontains=search) |
#                     Q(factor_for__name__icontains=search)
#                 )

#             # Sorting
#             queryset = queryset.order_by(sort_by)

#             # Pagination
#             paginator = CustomPagination()
#             paginated_queryset = paginator.paginate_queryset(queryset, request)

#             # Serialization
#             serializer = StudyFactorAgeSerializer(paginated_queryset, many=True)

#             return paginator.get_paginated_response(serializer.data)

#         except ValidationError as ve:
#             return Response({
#                 "status": False,
#                 "message": "Validation error",
#                 "error": str(ve),
#             }, status=status.HTTP_400_BAD_REQUEST)

#         except DatabaseError as db_err:
#             return Response({
#                 "status": False,
#                 "message": "Database error occurred",
#                 "error": str(db_err),
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#         except Exception as e:
#             # Catch-all for unexpected issues
#             return Response({
#                 "status": False,
#                 "message": "Something went wrong",
#                 "error": str(e),
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class StudyFactorAgeRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = [
            'minimum_age_months',
            'maximum_age_months',
            'created_at',
            'updated_at',
        ]

        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = StudyFactorAge.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(study_age_group__name__icontains=search) |
                Q(factor_for__name__icontains=search)
            )

        queryset = queryset.order_by(sort_by)

        paginator = CustomPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)

        serializer = StudyFactorAgeSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)
    

# -------------------- Age Update API--------------------
# class StudyFactorAgeUpdateAPIView(APIView):
#     permission_classes = [IsAuthenticated, IsAdminUser]

#     @transaction.atomic
#     def patch(self, request, uuid):
#         # Fetch object
#         try:
#             obj = StudyFactorAge.objects.get(uuid=uuid, is_deleted=False)
#         except StudyFactorAge.DoesNotExist:
#             return Response({
#                 "statusCode": 404,
#                 "status": False,
#                 "message": "Age entry not found",
#                 "data": None
#             }, status=404)

#         # Partial update
#         serializer = StudyFactorAgeSerializer(obj, data=request.data, partial=True)

#         if serializer.is_valid():
#             try:
#                 serializer.save()  # atomic
#             except Exception as e:
#                 transaction.set_rollback(True)
#                 return Response({
#                     "statusCode": 500,
#                     "status": False,
#                     "message": f"Update failed: {str(e)}",
#                     "data": None
#                 }, status=500)

#             return Response({
#                 "statusCode": 200,
#                 "status": True,
#                 "message": "Age updated successfully",
#                 "data": serializer.data
#             })

#         # Flatten validation errors
#         errors = []
#         for field, msgs in serializer.errors.items():
#             errors.extend(msgs)

#         return Response({
#             "statusCode": 400,
#             "status": False,
#             "message": " ".join(errors),
#             "data": None
#         }, status=400)
    

class StudyFactorAgeUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    @transaction.atomic
    def patch(self, request, uuid):
        try:
            obj = StudyFactorAge.objects.get(uuid=uuid, is_deleted=False)
        except StudyFactorAge.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Age entry not found."
            }, status=404)

        serializer = StudyFactorAgeSerializer(obj, data=request.data, partial=True)

        if serializer.is_valid():
            try:
                serializer.save()
            except Exception as e:
                transaction.set_rollback(True)
                return Response({
                    "statusCode": 500,
                    "status": False,
                    "message": f"Update failed: {str(e)}"
                }, status=500)

            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Age updated successfully.",
                "data": serializer.data
            }, status=200)

        # Format validation error messages same as Department API
        error_list = []
        for field, msgs in serializer.errors.items():
            error_list.extend(msgs)

        return Response({
            "statusCode": 400,
            "status": False,
            "message": " ".join(error_list)
        }, status=400)
    

# -------------------- Age Delete API --------------------

class StudyFactorAgeDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get("id", None)

        # ---------- SINGLE DELETE ----------
        if uuid:
            try:
                obj = StudyFactorAge.objects.get(uuid=uuid)
                obj.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "Age entry permanently deleted."
                }, status=204)
            except StudyFactorAge.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Age entry not found."
                }, status=404)

        # ---------- DELETE ALL ----------
        if ids == "all":
            qs = StudyFactorAge.objects.all()
            count = qs.count()

            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No Age entries found to delete."
                }, status=404)

            qs.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} Age entries permanently deleted."
            }, status=200)

        # ---------- MULTIPLE DELETE ----------
        if not ids or not isinstance(ids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Provide list of UUIDs in 'id' field or 'all'."
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

        qs = StudyFactorAge.objects.filter(uuid__in=valid_uuids)
        count = qs.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching Age entries found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=404)

        qs.delete()

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} Age entries permanently deleted.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        }, status=200)
    



    
# ---------------- Age EXPORT ----------------
class StudyFactorAgeExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):

        # --- Query params ---
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        search = request.GET.get('search', '').strip()
        custom_sort = request.GET.get('customSort')

        uuids = [u.strip() for u in uuids_param.split(',') if u]

        # --- Field → Header Mapping ---
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
            'created_at': 'Created On',
            'updated_at': 'Modified On',
        }

        # --- Determine Export Fields ---
        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())

        # --- Base Queryset ---
        queryset = StudyFactorAge.objects.filter(is_deleted=False)

        # --- UUID filter ---
        if uuids:
            valid_uuids = []
            for u in uuids:
                try:
                    valid_uuids.append(UUID(u))
                except:
                    pass
            if valid_uuids:
                queryset = queryset.filter(uuid__in=valid_uuids)

        # --- Search ---
        if search:
            queryset = queryset.filter(
                Q(factor_for__name__icontains=search) |
                Q(study_age_group__name__icontains=search) |
                Q(description__icontains=search)
            )

        # --- SORTING LOGIC (exactly like DepartmentExport) ---
        sort_field_map = {
            'factor_for': 'factor_for__name',
            'study_age_group': 'study_age_group__name',
            'minimum_age_months': 'minimum_age_months',
            'maximum_age_months': 'maximum_age_months',
            'description': 'description',
            'created_at': 'created_at',
            'updated_at': 'updated_at',
        }

        sort_fields = []

        if custom_sort:
            for rule in custom_sort.split(','):
                try:
                    field, order = rule.split(':')
                    field = field.strip()
                    order = order.strip().lower()

                    if field not in sort_field_map:
                        continue

                    orm_field = sort_field_map[field]

                    if field in ['factor_for', 'study_age_group', 'description']:
                        f = Lower(orm_field)
                    else:
                        f = F(orm_field)

                    sort_fields.append(
                        f.asc(nulls_last=True) if order == "asc" else f.desc(nulls_last=True)
                    )

                except:
                    continue

        else:
            # Default created_at desc
            f = F('created_at')
            sort_fields = [f.desc(nulls_last=True)]

        queryset = queryset.order_by(*sort_fields)

        # --- Prepare Dataset ---
        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = "Study Factor Age"

        india_tz = pytz.timezone("Asia/Kolkata")

        for obj in queryset:
            row = []
            for field in field_list:

                if field == "factor_for":
                    value = obj.factor_for.name if obj.factor_for else ""
                elif field == "study_age_group":
                    value = obj.study_age_group.name if obj.study_age_group else ""
                elif field == "country":
                    value = ", ".join([c.name for c in obj.country.all()])
                elif field == "course_level":
                    value = ", ".join([c.name for c in obj.course_level.all()])
                else:
                    value = getattr(obj, field, "")

                # --- Date formatting ---
                if field in ['created_at', 'updated_at'] and value:
                    try:
                        value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
                    except:
                        value = str(value)

                # --- Boolean → 0/1 ---
                if isinstance(value, bool):
                    value = int(value)

                row.append(value if value is not None else "")

            dataset.append(row)

        # --- Export file ---
        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'StudyFactorAge.csv'
            response_content = file_data

        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = (
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            file_name = 'StudyFactorAge.xlsx'
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

        # ---- REQUIRED HEADERS (lowercase exactly like Excel) ----
        required_headers = {
            "factor for",
            "study age group",
            "minimum age",
            "maximum age",
            "country",
            "course level",
        }

        optional_headers = {"description"}

        try:
            data = []

            # ======================== XLSX ========================
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
                        "error": f'Sheet "{sheet_name}" not found in uploaded file',
                        "available_sheets": available_sheets,
                    }, status=400)

                ws = wb[sheet_name]

                if ws.max_row <= 1:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'Sheet "{sheet_name}" is empty.'
                    }, status=400)

                # Read header row
                headers = [
                    str(cell.value).strip().lower() if cell.value else ""
                    for cell in next(ws.iter_rows(min_row=1, max_row=1))
                ]

                # Validate required headers
                if not required_headers.issubset(set(headers)):
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": (
                            f"Missing required headers. Required: {required_headers}, "
                            f"Found: {set(headers)}"
                        )
                    }, status=400)

                # Extract data rows
                for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    row_dict["_row_number"] = idx
                    data.append(row_dict)

            # ======================== CSV ========================
            elif format_type == "csv":
                decoded = file.read().decode("utf-8")
                dataset = Dataset()
                dataset.load(decoded, format="csv")

                for idx, row in enumerate(dataset.dict, start=2):
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    row_lower["_row_number"] = idx

                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({
                            "statusCode": 400,
                            "status": False,
                            "message": (
                                f"Missing required headers. Required: {', '.join(required_headers)}. "
                                f"Found headers in file: {', '.join(row_lower.keys())}."
                            )
                        }, status=400)

                    data.append(row_lower)

            else:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Unsupported file format. Use .xlsx or .csv",
                }, status=400)

            # ======================== PROCESS ROWS ========================
            imported_count = 0

            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")

                # -------- FKs ----------
                factor_for_name = str(row.get("factor for")).strip() if row.get("factor for") else None
                age_group_name = str(row.get("study age group")).strip() if row.get("study age group") else None

                # -------- Numeric Fields ----------
                try:
                    minimum_age = int(row.get("minimum age")) if row.get("minimum age") not in (None, "") else None
                except:
                    minimum_age = None

                try:
                    maximum_age = int(row.get("maximum age")) if row.get("maximum age") not in (None, "") else None
                except:
                    maximum_age = None

                # -------- M2M Fields ----------
                country_raw = str(row.get("country")).strip() if row.get("country") else ""
                course_level_raw = str(row.get("course level")).strip() if row.get("course level") else ""
                description = str(row.get("description")).strip() if row.get("description") else ""

                # -------- VALIDATION ----------
                if not factor_for_name:
                    skipped_rows.append({"Row": row_number, "Reason": "Missing factor for"})
                    continue

                if not age_group_name:
                    skipped_rows.append({"Row": row_number, "Reason": "Missing study age group"})
                    continue

                if minimum_age is None:
                    skipped_rows.append({"Row": row_number, "Reason": "Invalid minimum age"})
                    continue

                if maximum_age is None:
                    skipped_rows.append({"Row": row_number, "Reason": "Invalid maximum age"})
                    continue

                # -------- Lookup FKs ----------
                factor_for_obj = FactorFor.objects.filter(name__iexact=factor_for_name).first()
                if not factor_for_obj:
                    skipped_rows.append({"Row": row_number, "Reason": f'FactorFor "{factor_for_name}" not found'})
                    continue

                age_group_obj = AgeGroup.objects.filter(name__iexact=age_group_name).first()
                if not age_group_obj:
                    skipped_rows.append({"Row": row_number, "Reason": f'AgeGroup "{age_group_name}" not found'})
                    continue

                # -------- Resolve M2M ----------
                country_list = [c.strip() for c in country_raw.split(",") if c.strip()]
                course_level_list = [c.strip() for c in course_level_raw.split(",") if c.strip()]

                country_objs = []
                missing_countries = []
                for cname in country_list:
                    obj = Country.objects.filter(name__iexact=cname).first()
                    if obj:
                        country_objs.append(obj)
                    else:
                        missing_countries.append(cname)

                if missing_countries:
                    skipped_rows.append({
                        "Row": row_number,
                        "Reason": f"Countries not found: {', '.join(missing_countries)}"
                    })
                    continue

                course_objs = []
                missing_levels = []
                for lvl in course_level_list:
                    obj = CourseLevel.objects.filter(name__iexact=lvl).first()
                    if obj:
                        course_objs.append(obj)
                    else:
                        missing_levels.append(lvl)

                if missing_levels:
                    skipped_rows.append({
                        "Row": row_number,
                        "Reason": f"Course levels not found: {', '.join(missing_levels)}"
                    })
                    continue

                # -------- Duplicate Detection ----------
                existing = StudyFactorAge.objects.filter(
                    factor_for=factor_for_obj,
                    study_age_group=age_group_obj,
                    minimum_age_months=minimum_age,
                    maximum_age_months=maximum_age
                ).first()

                if existing:
                    if not existing.is_deleted:
                        duplicates.append({
                            "Row": row_number,
                            "Factor For": factor_for_name,
                            "Study Age Group": age_group_name,
                            "Reason": "Already exists"
                        })
                        continue

                    # revive deleted record
                    existing.description = description
                    existing.is_deleted = False
                    existing.save()
                    existing.country.set(country_objs)
                    existing.course_level.set(course_objs)
                    imported_count += 1
                    continue

                # -------- Create New ----------
                new_obj = StudyFactorAge.objects.create(
                    factor_for=factor_for_obj,
                    study_age_group=age_group_obj,
                    minimum_age_months=minimum_age,
                    maximum_age_months=maximum_age,
                    description=description,
                    is_deleted=False
                )
                new_obj.country.set(country_objs)
                new_obj.course_level.set(course_objs)

                imported_count += 1

        except Exception as e:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": str(e)
            }, status=400)

        # ======================== RESPONSE ========================
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": duplicates,
            "skipped_rows": skipped_rows,
        }, status=200)




# ---------------- LIST ----------------


class StudyFactorAcademicResultListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        custom_sort = request.GET.get('customSort')  # e.g., academic_result_group_name:asc

        # Allowed sort fields mapping
        sort_field_map = {
            'factor_for_name': 'factor_for__name',
            'academic_result_group_name': 'academic_result_group__name',
            'minimum_academic_result_required_name': 'minimum_academic_result_required__name',
            'description': 'description',
            'created_at': 'created_at',
            'updated_at': 'updated_at',
        }

        queryset = StudyFactorAcademicResult.objects.filter(is_deleted=False)

        # --------------------------
        # SEARCH BY academic_result_group only
        # --------------------------
        if search:
            queryset = queryset.filter(
                Q(academic_result_group__name__istartswith=search)
            )

        # --------------------------
        # SORTING LOGIC
        # --------------------------
        sort_fields = []

        if custom_sort:
            for rule in custom_sort.split(','):
                try:
                    field, order = rule.split(':')
                    field = field.strip()
                    order = order.strip().lower()

                    if field not in sort_field_map:
                        continue

                    orm_field = sort_field_map[field]

                    # Case-insensitive for string fields
                    if field in ['factor_for_name', 'academic_result_group_name', 'minimum_academic_result_required_name', 'description']:
                        f = Lower(orm_field)
                    else:
                        f = F(orm_field)

                    sort_fields.append(
                        f.asc(nulls_last=True) if order == 'asc' else f.desc(nulls_last=True)
                    )
                except ValueError:
                    continue
        else:
            # Fallback sorting
            sort_by = request.GET.get('sortBy', 'created_at')
            sort_order = request.GET.get('sortOrder', 'desc')
            orm_field = sort_field_map.get(sort_by, 'created_at')
            f = F(orm_field)
            sort_fields = [
                f.asc(nulls_last=True) if sort_order == 'asc' else f.desc(nulls_last=True)
            ]

        queryset = queryset.order_by(*sort_fields)

        # Pagination
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = StudyFactorAcademicResultSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)
    

# ---------------- CREATE ----------------

class StudyFactorAcademicResultCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):

        factor_for = request.data.get("factor_for")
        academic_result_group = request.data.get("academic_result_group")
        minimum_academic_result_required = request.data.get("minimum_academic_result_required")

        # ---------- 1. Basic Required Validations ----------

        if not factor_for:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "factor_for is required."
            }, status=400)

        if not academic_result_group:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "academic_result_group is required."
            }, status=400)

        if not minimum_academic_result_required:
            return Response({
                "statusCode": 400,
                "status": False,
                "status": False,
                "message": "minimum_academic_result_required (UUID) is required."
            }, status=400)

        # ---------- 2. Duplicate Check (Like Department API) ----------
        existing = StudyFactorAcademicResult.objects.filter(
            factor_for_id=factor_for,
            academic_result_group_id=academic_result_group,
            minimum_academic_result_required__uuid=minimum_academic_result_required,
            is_deleted=False
        ).first()

        if existing:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Record with these Factor For + Academic Result Group + Required Result already exists."
            }, status=400)

        # ---------- 3. Insert (Same structure as Department API) ----------
        serializer = StudyFactorAcademicResultSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Study Factor Academic Result created successfully",
                "data": serializer.data
            }, status=200)

        # ---------- 4. Collect Errors (Same style as Department API) ----------
        errors = serializer.errors
        messages = []
        for field, msgs in errors.items():
            messages.extend(msgs)
        message_text = " ".join(messages)

        return Response({
            "statusCode": 400,
            "status": False,
            "message": message_text,
        }, status=400)
    

# ---------------- RETRIEVE ----------------

class StudyFactorAcademicResultRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = StudyFactorAcademicResult.objects.get(uuid=uuid, is_deleted=False)
        except StudyFactorAcademicResult.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Study Factor Academic Result not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = StudyFactorAcademicResultSerializer(obj)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Study Factor Academic Result retrieved successfully",
            "data": serializer.data
        })



# ---------------- UPDATE ----------------

class StudyFactorAcademicResultUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = StudyFactorAcademicResult.objects.get(uuid=uuid, is_deleted=False)
        except StudyFactorAcademicResult.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Study Factor Academic Result not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = StudyFactorAcademicResultSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Study Factor Academic Result updated successfully",
                "data": serializer.data
            })

        # Collect all error messages
        errors = []
        for field, msgs in serializer.errors.items():
            errors.extend(msgs)

        return Response({
            "statusCode": 400,
            "status": False,
            "message": " ".join(errors),
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)



# ---------------- DELETE ----------------

class StudyFactorAcademicResultDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get("id", None)

        # ---- SINGLE DELETE ----
        if uuid:
            try:
                obj = StudyFactorAcademicResult.objects.get(uuid=uuid)
                obj.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "Study Factor Academic Result permanently deleted.",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            except StudyFactorAcademicResult.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Study Factor Academic Result not found.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        # ---- DELETE ALL ----
        if ids == "all":
            objs = StudyFactorAcademicResult.objects.all()
            count = objs.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No Study Factor Academic Results found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
            objs.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} Study Factor Academic Result(s) permanently deleted.",
                "data": None
            }, status=status.HTTP_200_OK)

        # ---- MULTIPLE DELETE ----
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

        objs = StudyFactorAcademicResult.objects.filter(uuid__in=valid_uuids)
        count = objs.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching Study Factor Academic Results found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_404_NOT_FOUND)

        objs.delete()
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} Study Factor Academic Result(s) permanently deleted.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        }, status=status.HTTP_200_OK)




class StudyFactorAcademicResultExportAPIView(APIView):
    """
    Export Study Factor Academic Result data to CSV or XLSX with custom sorting.
    """
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')  # comma-separated fields
        uuids_param = request.GET.get('uuids', '')
        custom_sort = request.GET.get('customSort')  # e.g., academic_result_group:asc,updated_at:desc
        search = request.GET.get('search', '').strip()
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        # --- Field to header mapping ---
        field_header_map = {
            'uuid': 'UUID',
            'factor_for': 'Factor For',
            'academic_result_group': 'Academic Result Group',
            'minimum_academic_result_required': 'Minimum Academic Result Required',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'created_at': 'Created On',
            'updated_at': 'Modified On',
        }

        # --- Determine fields to export ---
        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())

        # --- Fetch queryset ---
        queryset = StudyFactorAcademicResult.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)

        if search:
            queryset = queryset.filter(academic_result_group__name__istartswith=search)

        # --- Custom sorting logic ---
        sort_field_map = {
            'factor_for': 'factor_for__name',
            'academic_result_group': 'academic_result_group__name',
            'minimum_academic_result_required': 'minimum_academic_result_required__name',
            'description': 'description',
            'is_deleted': 'is_deleted',
            'created_at': 'created_at',
            'updated_at': 'updated_at',
        }

        sort_fields = []

        if custom_sort:
            for rule in custom_sort.split(','):
                try:
                    field, order = rule.split(':')
                    field = field.strip()
                    order = order.strip().lower()

                    if field not in sort_field_map:
                        continue

                    orm_field = sort_field_map[field]

                    # Case-insensitive sorting for string fields
                    if field in ['factor_for', 'academic_result_group', 'minimum_academic_result_required', 'description']:
                        f = Lower(orm_field)
                    else:
                        f = F(orm_field)

                    sort_fields.append(f.asc(nulls_last=True) if order == 'asc' else f.desc(nulls_last=True))
                except ValueError:
                    continue
        else:
            # Default sort by created_at desc
            sort_order = request.GET.get('sortOrder', 'desc')
            f = F('created_at')
            sort_fields = [f.desc(nulls_last=True) if sort_order == 'desc' else f.asc(nulls_last=True)]

        queryset = queryset.order_by(*sort_fields)

        # --- Prepare dataset ---
        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'StudyFactorAcademicResult'

        for obj in queryset:
            row = []
            for field in field_list:
                # Handle related fields
                if field == 'factor_for':
                    value = getattr(obj.factor_for, 'name', '') if obj.factor_for else ''
                elif field == 'academic_result_group':
                    value = getattr(obj.academic_result_group, 'name', '') if obj.academic_result_group else ''
                elif field == 'minimum_academic_result_required':
                    value = getattr(obj.minimum_academic_result_required, 'name', '') if obj.minimum_academic_result_required else ''
                else:
                    value = getattr(obj, field, '')

                if field in ['created_at', 'updated_at'] and value:
                    value = timezone.localtime(value).strftime("%d-%m-%Y %I:%M:%S %p")
                elif isinstance(value, bool):
                    value = int(value)

                row.append(value if value is not None else '')
            dataset.append(row)

        # --- Export data ---
        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'StudyFactorAcademicResult.csv'
            response_content = file_data
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'StudyFactorAcademicResult.xlsx'
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
            return Response({"statusCode": 400, "status": False, "message": "No file uploaded"}, status=400)

        format_type = file.name.split(".")[-1].lower()
        duplicates = []
        skipped_rows = []

        required_headers = {"factor for", "academic result group", "minimum academic result required"}
        optional_headers = {"description"}

        try:
            data = []

            # ---------- XLSX Handling ----------
            if format_type == "xlsx":
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": "Please provide sheet_name",
                        "available_sheets": available_sheets
                    }, status=400)

                if sheet_name not in available_sheets:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'Sheet "{sheet_name}" not found in uploaded file',
                        "available_sheets": available_sheets
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

            # ---------- CSV Handling ----------
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
                    "message": "Unsupported file format. Use .xlsx or .csv"
                }, status=400)

            # ---------- Import Rows ----------
            imported_count = 0

            # Reverse iterate to maintain order
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
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                        continue

                # Create new record
                StudyFactorAcademicResult.objects.create(
                    factor_for=factor_obj,
                    academic_result_group=group_obj,
                    minimum_academic_result_required=min_result_obj,
                    description=description,
                    is_deleted=False
                )
                imported_count += 1

        except Exception as e:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": str(e)
            }, status=400)

        # ---------- Final Response ----------
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": duplicates,
            "skipped_rows": skipped_rows
        }, status=200)

# ---------------- LIST ----------------

class StudyFactorBacklogsListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get("search", "").strip()
        custom_sort = request.GET.get("customSort")  # e.g., backlog_group:asc,updated_at:desc

        queryset = StudyFactorBacklogs.objects.filter(is_deleted=False)

        # --------------------------------------
        # SEARCH (Only on backlog_group columns)
        # --------------------------------------
        if search:
            queryset = queryset.filter(
                Q(backlog_group__name__istartswith=search)
            )

        # --------------------------------------
        # ALLOWED SORT FIELDS
        # --------------------------------------
        allowed_sort_fields = [
            "factor_for__name",
            "backlog_group__name",
            "created_at",
            "updated_at"
        ]

        # Map readable names to ORM fields
        sort_field_map = {
            "factor_for": "factor_for__name",
            "backlog_group": "backlog_group__name",
            "created_at": "created_at",
            "updated_at": "updated_at",
        }

        sort_fields = []

        # --------------------------------------
        # CUSTOM SORT (Same as Department API)
        # --------------------------------------
        if custom_sort:
            for rule in custom_sort.split(','):
                try:
                    field, order = rule.split(':')
                    field = field.strip()
                    order = order.strip().lower()

                    if field not in sort_field_map:
                        continue

                    orm_field = sort_field_map[field]

                    # Case-insensitive sorting
                    if field in ["factor_for", "backlog_group"]:
                        f = Lower(orm_field)
                    else:
                        f = F(orm_field)

                    sort_fields.append(
                        f.asc(nulls_last=True) if order == "asc" else f.desc(nulls_last=True)
                    )
                except ValueError:
                    continue

        else:
            # --------------------------------------
            # NORMAL sortBy & sortOrder fallback
            # --------------------------------------
            sort_by = request.GET.get("sortBy", "created_at")
            sort_order = request.GET.get("sortOrder", "desc")

            orm_field = sort_field_map.get(sort_by, "created_at")
            f = F(orm_field)

            sort_fields = [
                f.asc(nulls_last=True) if sort_order == "asc" else f.desc(nulls_last=True)
            ]

        queryset = queryset.order_by(*sort_fields)

        # --------------------------------------
        # PAGINATION
        # --------------------------------------
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = StudyFactorBacklogsSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)


class StudyFactorBacklogsCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        # Use serializer directly — it already accepts UUID
        serializer = StudyFactorBacklogsSerializer(data=request.data)

        if serializer.is_valid():
            # Duplicate check
            factor_for_obj = serializer.validated_data['factor_for']
            backlog_group_obj = serializer.validated_data['backlog_group']

            exists = StudyFactorBacklogs.objects.filter(
                factor_for=factor_for_obj,
                backlog_group=backlog_group_obj,
                is_deleted=False
            ).first()

            if exists:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Entry already exists for this FactorFor & BacklogGroup."
                }, status=400)

            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Study Factor Backlogs created successfully",
                "data": serializer.data
            }, status=200)

        # Return validation errors
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
        obj = StudyFactorBacklogs.objects.filter(uuid=uuid, is_deleted=False).first()

        if not obj:
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
        }, status=200)


class StudyFactorBacklogsUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        obj = StudyFactorBacklogs.objects.filter(uuid=uuid, is_deleted=False).first()

        if not obj:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "StudyFactorBacklogs not found",
                "data": None
            }, status=404)

        # If you track updated_by field uncomment this:
        # request.data["updated_by"] = request.user.id

        serializer = StudyFactorBacklogsSerializer(obj, data=request.data, partial=True)

        if not serializer.is_valid():
            messages = []
            for field, errors in serializer.errors.items():
                messages.extend(errors)

            return Response({
                "statusCode": 400,
                "status": False,
                "message": " ".join(messages),
                "data": None
            }, status=400)

        serializer.save()

        return Response({
            "statusCode": 200,
            "status": True,
            "message": "StudyFactorBacklogs updated successfully",
            "data": serializer.data
        }, status=200)


class StudyFactorBacklogsDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get("id", None)

        # ------------------------------
        # 1. SINGLE DELETE (via URL UUID)
        # ------------------------------
        if uuid:
            try:
                obj = StudyFactorBacklogs.objects.get(uuid=uuid)
                obj.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "StudyFactorBacklogs permanently deleted.",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            except StudyFactorBacklogs.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "StudyFactorBacklogs not found.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        # ------------------------------
        # 2. DELETE ALL
        # ------------------------------
        if ids == "all":
            objs = StudyFactorBacklogs.objects.all()
            count = objs.count()

            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No StudyFactorBacklogs found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

            objs.delete()

            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} StudyFactorBacklogs permanently deleted.",
                "data": None
            }, status=status.HTTP_200_OK)

        # ------------------------------
        # 3. BULK DELETE (multiple UUIDs)
        # ------------------------------
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

        objs = StudyFactorBacklogs.objects.filter(uuid__in=valid_uuids)
        count = objs.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching StudyFactorBacklogs found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_404_NOT_FOUND)

        objs.delete()

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} StudyFactorBacklogs permanently deleted.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        }, status=status.HTTP_200_OK)
    

class StudyFactorBacklogsExportAPIView(APIView):

    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        # --- Query Parameters ---
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        custom_sort = request.GET.get('customSort')
        search = request.GET.get('search', '').strip()

        uuids = [u.strip() for u in uuids_param.split(',') if u]

        # --- Field to Header Mapping ---
        field_header_map = {
            "uuid": "UUID",
            "factor_for_name": "Factor For",
            "backlog_group_name": "Backlog Group",
            "backlog_accepted": "Backlog Accepted",
            "max_backlogs": "Max Backlogs",
            "description": "Description",
            "is_deleted": "Deleted",
            "created_at": "Created On",
            "updated_at": "Modified On",
        }

        # Determine fields to export
        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())

        # --- Base Queryset ---
        queryset = StudyFactorBacklogs.objects.filter(is_deleted=False)

        if uuids:
            queryset = queryset.filter(uuid__in=uuids)

        if search:
            queryset = queryset.filter(
                backlog_group__name__istartswith=search
            )

        # --- Custom Sorting Logic (Exact Department Logic) ---
        sort_field_map = {
            "factor_for_name": "factor_for__name",
            "backlog_group_name": "backlog_group__name",
            "backlog_accepted": "backlog_accepted",
            "max_backlogs": "max_backlogs",
            "description": "description",
            "is_deleted": "is_deleted",
            "created_at": "created_at",
            "updated_at": "updated_at",
        }

        sort_fields = []

        if custom_sort:
            for rule in custom_sort.split(','):
                try:
                    field, order = rule.split(':')
                    field = field.strip()
                    order = order.strip().lower()

                    if field not in sort_field_map:
                        continue

                    orm_field = sort_field_map[field]

                    if field in ["factor_for_name", "backlog_group_name", "description"]:
                        f = Lower(orm_field)
                    else:
                        f = F(orm_field)

                    sort_fields.append(
                        f.asc(nulls_last=True) if order == "asc" else f.desc(nulls_last=True)
                    )

                except ValueError:
                    continue

        else:
            # Default sorting
            sort_order = request.GET.get("sortOrder", "desc")
            f = F("created_at")
            sort_fields = [f.desc(nulls_last=True) if sort_order == "desc" else f.asc(nulls_last=True)]

        # Apply sorting
        queryset = queryset.order_by(*sort_fields)

        # --- Prepare Dataset ---
        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'StudyFactorBacklogs'


        for obj in queryset:
            row = []

            for field in field_list:
                # Handle readable fields
                if field == "factor_for_name":
                    value = obj.factor_for.name if obj.factor_for else ""
                elif field == "backlog_group_name":
                    value = obj.backlog_group.name if obj.backlog_group else ""
                else:
                    value = getattr(obj, field, "")

                # Format timestamps
                if field in ["created_at", "updated_at"] and value:
                    value = timezone.localtime(value).strftime("%d-%m-%Y %I:%M:%S %p")

                # Boolean to int
                if isinstance(value, bool):
                    value = int(value)

                row.append(value if value is not None else "")

            dataset.append(row)

        # --- Export ---
        if format_type == "csv":
            file_data = dataset.export("csv")
            content_type = "text/csv"
            file_name = "StudyFactorBacklogs.csv"
            output = file_data
        else:
            file_data = io.BytesIO(dataset.export("xlsx"))
            content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            file_name = "StudyFactorBacklogs.xlsx"
            output = file_data.getvalue()

        # --- Response ---
        response = HttpResponse(output, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response



class StudyFactorBacklogsImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]


    REQUIRED_HEADERS = {"factor for", "backlog group"}
    OPTIONAL_HEADERS = {"backlog accepted", "maximum backlogs accepted", "description"}

    def post(self, request):
        file = request.FILES.get("file")
        sheet_name = request.data.get("sheet_name")

        if not file:
            return Response({"statusCode": 400, "status": False, "message": "No file uploaded"}, status=400)

        format_type = file.name.split(".")[-1].lower()
        duplicates = []
        skipped_rows = []
        imported_count = 0
        data = []

        try:
            # ---------- XLSX Handling ----------
            if format_type == "xlsx":
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": "Please provide sheet_name",
                        "available_sheets": available_sheets
                    }, status=400)

                if sheet_name not in available_sheets:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'Sheet "{sheet_name}" not found in uploaded file',
                        "available_sheets": available_sheets
                    }, status=400)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'Sheet "{sheet_name}" is empty.'
                    }, status=400)

                headers = [
                    str(cell.value).strip().lower() if cell.value else ""
                    for cell in next(ws.iter_rows(min_row=1, max_row=1))
                ]

                if not self.REQUIRED_HEADERS.issubset(set(headers)):
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f"Missing required headers. Required: {self.REQUIRED_HEADERS}, Found: {set(headers)}"
                    }, status=400)

                for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    row_dict["_row_number"] = idx
                    data.append(row_dict)

            # ---------- CSV Handling ----------
            elif format_type == "csv":
                decoded_file = file.read().decode("utf-8")
                dataset = Dataset()
                dataset.load(decoded_file, format="csv")

                for idx, row in enumerate(dataset.dict, start=2):
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    row_lower["_row_number"] = idx

                    if not self.REQUIRED_HEADERS.issubset(set(row_lower.keys())):
                        return Response({
                            "statusCode": 400,
                            "status": False,
                            "message": (
                                f"Missing required headers. Required: {', '.join(self.REQUIRED_HEADERS)}. "
                                f"Found headers: {', '.join(row_lower.keys())}."
                            )
                        }, status=400)

                    data.append(row_lower)
            else:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Unsupported file format. Use .xlsx or .csv"
                }, status=400)

            # ---------- Import Rows ----------
            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")
                factor_for_name = str(row.get("factor for")).strip() if row.get("factor for") else None
                backlog_group_name = str(row.get("backlog group")).strip() if row.get("backlog group") else None
                backlog_accepted = bool(row.get("backlog accepted", False))
                max_backlogs = int(row.get("maximum backlogs accepted", 0) or 0)
                description = str(row.get("description") or "")

                if not factor_for_name or not backlog_group_name:
                    skipped_rows.append({"Row": row_number, "Reason": "Missing required values"})
                    continue

                try:
                    factor_for_fk = FactorFor.objects.get(name__iexact=factor_for_name)
                    backlog_group_fk = BacklogsGroup.objects.get(name__iexact=backlog_group_name)
                except (FactorFor.DoesNotExist, BacklogsGroup.DoesNotExist):
                    skipped_rows.append({"Row": row_number, "Reason": "Invalid FactorFor or BacklogGroup"})
                    continue

                existing = StudyFactorBacklogs.objects.filter(
                    factor_for=factor_for_fk,
                    backlog_group=backlog_group_fk,
                    is_deleted=False
                ).first()

                if existing:
                    duplicates.append({"Row": row_number, "Factor For": factor_for_name, "Backlog Group": backlog_group_name})
                    continue

                StudyFactorBacklogs.objects.create(
                    factor_for=factor_for_fk,
                    backlog_group=backlog_group_fk,
                    backlog_accepted=backlog_accepted,
                    max_backlogs=max_backlogs,
                    description=description
                )
                imported_count += 1

        except Exception as e:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": str(e)
            }, status=400)

        # ---------- Final Response ----------
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": duplicates,
            "skipped_rows": skipped_rows
        }, status=200)
    


class StudyFactorGAPListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        custom_sort = request.GET.get('customSort')

        # Allowed sorting fields for this model
        allowed_sort_fields = ['study_gap_group', 'factor_for', 'created_at', 'updated_at']

        queryset = StudyFactorGAP.objects.filter(is_deleted=False)

        # ---------------------------------------
        # SEARCH — ONLY ON GAP GROUP COLUMN
        # ---------------------------------------
        if search:
            queryset = queryset.filter(
                Q(study_gap_group__name__istartswith=search)
            )

        # Mapping sort fields from request → ORM fields
        sort_field_map = {
            'study_gap_group': 'study_gap_group__name',
            'factor_for': 'factor_for__name',
            'created_at': 'created_at',
            'updated_at': 'updated_at',
        }

        sort_fields = []

        # ---------------------------------------
        # CUSTOM SORT LOGIC (same as department)
        # ---------------------------------------
        if custom_sort:
            for rule in custom_sort.split(','):
                try:
                    field, order = rule.split(':')
                    field = field.strip()
                    order = order.strip().lower()

                    if field not in sort_field_map:
                        continue

                    orm_field = sort_field_map[field]

                    # Case-insensitive sorting for string fields
                    if field in ['study_gap_group', 'factor_for']:
                        f = Lower(orm_field)
                    else:
                        f = F(orm_field)

                    sort_fields.append(
                        f.asc(nulls_last=True) if order == 'asc' else f.desc(nulls_last=True)
                    )

                except ValueError:
                    continue

        else:
            # ---------------------------------------
            # FALLBACK SORTING   (sortBy + sortOrder)
            # ---------------------------------------
            sort_by = request.GET.get('sortBy', 'created_at')
            sort_order = request.GET.get('sortOrder', 'desc')

            orm_field = sort_field_map.get(sort_by, 'created_at')

            f = F(orm_field)

            sort_fields = [
                f.asc(nulls_last=True) if sort_order == 'asc' else f.desc(nulls_last=True)
            ]

        queryset = queryset.order_by(*sort_fields)

        # Pagination
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = StudyFactorGAPSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)



class StudyFactorGAPCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    @transaction.atomic
    def post(self, request):
        serializer = StudyFactorGAPSerializer(data=request.data)
        if serializer.is_valid():
            factor_for_obj = serializer.validated_data["factor_for"]
            gap_group_obj = serializer.validated_data["study_gap_group"]

            # Duplicate check
            if StudyFactorGAP.objects.filter(
                factor_for=factor_for_obj,
                study_gap_group=gap_group_obj,
                is_deleted=False
            ).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Study Factor GAP already exists for this Factor For & GAP Group."
                }, status=400)

            instance = serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Study Factor GAP created successfully",
                "data": StudyFactorGAPSerializer(instance).data
            }, status=200)

        # Handle errors
        messages = [msg for msgs in serializer.errors.values() for msg in msgs]
        return Response({
            "statusCode": 400,
            "status": False,
            "message": " ".join(messages)
        }, status=400)


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
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = StudyFactorGAPSerializer(obj)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Study Factor GAP retrieved successfully",
            "data": serializer.data
        })
    

class StudyFactorGAPUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = StudyFactorGAP.objects.get(uuid=uuid, is_deleted=False)
        except StudyFactorGAP.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Study Factor GAP not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = StudyFactorGAPSerializer(obj, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Study Factor GAP updated successfully",
                "data": serializer.data
            })

        # Collect error messages like Department API
        errors = serializer.errors
        messages = []
        for field, msgs in errors.items():
            messages.extend(msgs)

        return Response({
            "statusCode": 400,
            "status": False,
            "message": " ".join(messages),
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)
    

class StudyFactorGAPDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get('id', None)

        # ----------------------------------
        # SINGLE DELETE (via /uuid/)
        # ----------------------------------
        if uuid:
            try:
                obj = StudyFactorGAP.objects.get(uuid=uuid)
                obj.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "Study Factor GAP permanently deleted.",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)

            except StudyFactorGAP.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Study Factor GAP not found.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        # ----------------------------------
        # DELETE ALL RECORDS
        # ----------------------------------
        if ids == "all":
            objs = StudyFactorGAP.objects.all()
            count = objs.count()

            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No Study Factor GAP records found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

            objs.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} Study Factor GAP record(s) permanently deleted.",
                "data": None
            }, status=status.HTTP_200_OK)

        # ----------------------------------
        # VALIDATE BULK UUID LIST
        # ----------------------------------
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

        # ----------------------------------
        # BULK DELETE
        # ----------------------------------
        objs = StudyFactorGAP.objects.filter(uuid__in=valid_uuids)
        count = objs.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching Study Factor GAP records found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_404_NOT_FOUND)

        objs.delete()

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} Study Factor GAP record(s) permanently deleted.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        }, status=status.HTTP_200_OK)
    


# ---------------- EXPORT ----------------

class StudyFactorGAPExportAPIView(APIView):
    """
    Export StudyFactorGAP data to CSV or XLSX with custom sorting.
    """
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        # --- Query params ---
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        custom_sort = request.GET.get('customSort')
        search = request.GET.get('search', '').strip()

        uuids = [u.strip() for u in uuids_param.split(',') if u]

        # --- Field → header mapping ---
        field_header_map = {
            'uuid': 'UUID',
            'factor_for': 'Factor For',
            'study_gap_group': 'Study GAP Group',
            'maximum_gap_accepted': 'Maximum GAP Accepted',
            'country_for_admission': 'Country For Admission',
            'institute_type': 'Institute Type',
            'course_level': 'Course Level',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'created_at': 'Created On',
            'updated_at': 'Modified On',
        }

        # --- Determine fields to export ---
        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())

        # --- Fetch queryset ---
        queryset = StudyFactorGAP.objects.filter(is_deleted=False)

        if uuids:
            queryset = queryset.filter(uuid__in=uuids)

        if search:
            queryset = queryset.filter(
                Q(factor_for__name__istartswith=search) |
                Q(study_gap_group__name__istartswith=search)
            )

        # --- Custom SORT mapping ---
        sort_field_map = {
            'factor_for': 'factor_for__name',
            'study_gap_group': 'study_gap_group__name',
            'maximum_gap_accepted': 'maximum_gap_accepted',
            'description': 'description',
            'created_at': 'created_at',
            'updated_at': 'updated_at',
            'is_deleted': 'is_deleted',
        }

        sort_fields = []

        # --- Custom Sort Logic ---
        if custom_sort:
            for rule in custom_sort.split(','):
                try:
                    field, order = rule.split(':')
                    field = field.strip()
                    order = order.strip().lower()

                    if field not in sort_field_map:
                        continue

                    orm_field = sort_field_map[field]

                    if field in ['factor_for', 'study_gap_group', 'description']:
                        f = Lower(orm_field)
                    else:
                        f = F(orm_field)

                    sort_fields.append(f.asc(nulls_last=True) if order == 'asc' else f.desc(nulls_last=True))

                except ValueError:
                    continue
        else:
            sort_order = request.GET.get('sortOrder', 'desc')
            f = F('created_at')
            sort_fields = [f.desc(nulls_last=True) if sort_order == 'desc' else f.asc(nulls_last=True)]

        queryset = queryset.order_by(*sort_fields)

        # --- Prepare dataset ---
        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = "StudyFactorGAP"

        for obj in queryset:
            row = []

            for field in field_list:
                value = getattr(obj, field, '')

                # Many-to-many mapping (UPDATED)
                if field == "country_for_admission":
                    value = ", ".join(obj.country_for_admission.values_list("full_name", flat=True))

                elif field == "institute_type":
                    value = ", ".join(obj.institute_type.values_list("name", flat=True))

                elif field == "course_level":
                    value = ", ".join(obj.course_level.values_list("name", flat=True))

                # Date formatting
                elif field in ["created_at", "updated_at"] and value:
                    value = timezone.localtime(value).strftime("%d-%m-%Y %I:%M:%S %p")

                # Bool → int
                elif isinstance(value, bool):
                    value = int(value)

                # FKs
                elif field in ["factor_for", "study_gap_group"] and value:
                    value = str(value)

                row.append(value if value is not None else '')

            dataset.append(row)

        # --- EXPORT ---
        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'StudyFactorGAP.csv'

        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'StudyFactorGAP.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response
    

# ---------------- IMPORT ----------------

class StudyFactorGAPImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get("file")
        sheet_name = request.data.get("sheet_name")

        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split(".")[-1].lower()
        duplicates = []
        skipped_rows = []

        # headers expected in the file (lowercased)
        required_headers = {
            "factor for",
            "study gap group",                   # UPDATED
            "maximum gap accepted",
            "country for admission",             # UPDATED
            "institute type",                    # UPDATED
            "course level",                      # UPDATED
        }
        optional_headers = {"description"}

        try:
            data = []

            # ---------- XLSX Handling ----------
            if format_type == "xlsx":
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({
                        "error": "Please provide sheet_name",
                        "available_sheets": available_sheets,
                    }, status=status.HTTP_400_BAD_REQUEST)

                if sheet_name not in available_sheets:
                    return Response({
                        "error": f'Sheet "{sheet_name}" not found in uploaded file',
                        "available_sheets": available_sheets,
                    }, status=status.HTTP_400_BAD_REQUEST)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'Sheet "{sheet_name}" is empty.'
                    }, status=status.HTTP_400_BAD_REQUEST)

                headers = [
                    str(cell.value).strip().lower() if cell.value else ""
                    for cell in next(ws.iter_rows(min_row=1, max_row=1))
                ]

                if not required_headers.issubset(set(headers)):
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f"Missing required headers. Required: {required_headers}, Found: {set(headers)}"
                    }, status=status.HTTP_400_BAD_REQUEST)

                for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    row_dict["_row_number"] = idx
                    data.append(row_dict)

            # ---------- CSV Handling ----------
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
                            "message": (
                                f"Missing required headers. Required: {', '.join(required_headers)}. "
                                f"Found headers in the file: {', '.join(row_lower.keys())}."
                            )
                        }, status=status.HTTP_400_BAD_REQUEST)

                    data.append(row_lower)

            else:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "error": "Unsupported file format. Use .xlsx or .csv",
                }, status=status.HTTP_400_BAD_REQUEST)

            # ---------- Import Rows ----------
            imported_count = 0

            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")

                factor_for_name = str(row.get("factor for") or "").strip()
                study_gap_group_name = str(row.get("study gap group") or "").strip()     # UPDATED
                max_gap = row.get("maximum gap accepted (months)")
                description = str(row.get("description") or "").strip()

                country_names = [
                    c.strip() for c in str(row.get("country for admission") or "").split(",") if c.strip()
                ]   # UPDATED

                institute_type_names = [
                    i.strip() for i in str(row.get("institute type") or "").split(",") if i.strip()
                ]   # UPDATED

                course_level_names = [
                    c.strip() for c in str(row.get("course level") or "").split(",") if c.strip()
                ]   # UPDATED

                if not (factor_for_name and study_gap_group_name and (max_gap is not None)):
                    skipped_rows.append({
                        "Row": row_number,
                        "Reason": "Missing required fields"
                    })
                    continue

                factor_for_obj = FactorFor.objects.filter(name__iexact=factor_for_name).first()
                study_gap_group_obj = GAPGroup.objects.filter(name__iexact=study_gap_group_name).first()

                if not factor_for_obj or not study_gap_group_obj:
                    skipped_rows.append({
                        "Row": row_number,
                        "Reason": "Invalid FK values"
                    })
                    continue

                existing = StudyFactorGAP.objects.filter(
                    factor_for=factor_for_obj,
                    study_gap_group=study_gap_group_obj,
                    maximum_gap_accepted=max_gap
                ).first()

                if existing:
                    if not existing.is_deleted:
                        duplicates.append({
                            "Row": row_number,
                            "Reason": "Record already exists"
                        })
                        continue
                    else:
                        obj = existing
                        obj.is_deleted = False
                        obj.description = description
                        obj.save()
                else:
                    obj = StudyFactorGAP.objects.create(
                        factor_for=factor_for_obj,
                        study_gap_group=study_gap_group_obj,
                        maximum_gap_accepted=max_gap,
                        description=description
                    )

                if country_names:
                    countries = RepresentingCountry.objects.filter(name__in=country_names)
                    obj.country_for_admission.set(countries)   # UPDATED
                else:
                    obj.country_for_admission.clear()

                if institute_type_names:
                    institutes = InstituteType.objects.filter(name__in=institute_type_names)
                    obj.institute_type.set(institutes)         # UPDATED
                else:
                    obj.institute_type.clear()

                if course_level_names:
                    courses = CourseLevel.objects.filter(name__in=course_level_names)
                    obj.course_level.set(courses)              # UPDATED
                else:
                    obj.course_level.clear()

                imported_count += 1

        except Exception as e:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": str(e),
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": duplicates,
            "skipped_rows": skipped_rows,
        }, status=status.HTTP_200_OK)




#--------------------LanguageAbility----------------------

class StudyFactorLanguageAbilityCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    # ----------------------------------------------------
    # UUID ONLY Foreign Key Resolver
    # ----------------------------------------------------
    def resolve_fk(self, model, value):
        if not value:
            return None
        try:
            return model.objects.get(uuid=value)
        except model.DoesNotExist:
            return None

    # ----------------------------------------------------
    # POST - Create API
    # ----------------------------------------------------
    def post(self, request):
        data = request.data.copy()

        # Correct FK mapping (UUID → actual model)
        fk_map = {
            "factor_for": FactorFor,
            "language_ability_group": LanguageAbilityGroup,
            "language_test_name": LanguageTest,
            "module_name": LanguagetestmoduleName,
            "minimum_overall_score": LanguageTestResult,
            "not_less_than": LanguageTestResult,
        }

        # Resolve UUID fields → internal model IDs
        for field, model in fk_map.items():
            value = data.get(field)

            resolved = self.resolve_fk(model, value)
            if not resolved:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": f"Invalid {field.replace('_', ' ').title()}"
                }, status=400)

            # Convert FK from UUID → ID for save()
            data[field] = resolved.id

        # Serialize & save
        serializer = StudyFactorLanguageAbilitySerializer(data=data)

        if serializer.is_valid():
            obj = serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Study Factor Language Ability created successfully",
                "data": StudyFactorLanguageAbilitySerializer(obj).data
            }, status=200)

        # Flatten error messages
        messages = []
        for field, errs in serializer.errors.items():
            messages.extend(errs)

        return Response({
            "statusCode": 400,
            "status": False,
            "message": " ".join(messages)
        }, status=400)
    

class StudyFactorLanguageAbilityListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]


    def get(self, request):
        search = request.GET.get('search', '').strip()
        custom_sort = request.GET.get('customSort')  # e.g., language_ability_group:asc,created_at:desc

        allowed_sort_fields = ['language_ability_group', 'in_no_of_modules', 'created_at', 'updated_at']

        queryset = StudyFactorLanguageAbility.objects.filter(is_deleted=False)

        # --------------------------
        # SEARCH FILTER (ONLY Language Ability Group)
        # --------------------------
        if search:
            queryset = queryset.filter(Q(language_ability_group__name__istartswith=search))

        # --------------------------
        # SORTING LOGIC
        # --------------------------
        sort_field_map = {
            'language_ability_group': 'language_ability_group__name',
            'in_no_of_modules': 'in_no_of_modules',
            'created_at': 'created_at',
            'updated_at': 'updated_at',
        }

        sort_fields = []

        if custom_sort:
            for rule in custom_sort.split(','):
                try:
                    field, order = rule.split(':')
                    field = field.strip()
                    order = order.strip().lower()

                    if field not in sort_field_map:
                        continue

                    orm_field = sort_field_map[field]

                    # Case-insensitive ordering for string fields
                    if field in ['language_ability_group']:
                        f = Lower(orm_field)
                    else:
                        f = F(orm_field)

                    sort_fields.append(f.asc(nulls_last=True) if order == 'asc' else f.desc(nulls_last=True))
                except ValueError:
                    continue
        else:
            # Fallback sorting
            sort_by = request.GET.get('sortBy', 'created_at')
            sort_order = request.GET.get('sortOrder', 'desc')
            orm_field = sort_field_map.get(sort_by, 'created_at')
            f = F(orm_field)
            sort_fields = [f.asc(nulls_last=True) if sort_order == 'asc' else f.desc(nulls_last=True)]

        queryset = queryset.order_by(*sort_fields)

        # --------------------------
        # PAGINATION
        # --------------------------
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
            }, status=status.HTTP_404_NOT_FOUND)

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
            }, status=status.HTTP_404_NOT_FOUND)

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
                    }, status=status.HTTP_400_BAD_REQUEST)
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
            "message": " ".join(messages),
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)


class StudyFactorLanguageAbilityDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get("id")

        # Single delete via URL parameter
        if uuid:
            try:
                obj = StudyFactorLanguageAbility.objects.get(uuid=uuid)
                obj.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "Study Factor Language Ability permanently deleted.",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            except StudyFactorLanguageAbility.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Study Factor Language Ability not found.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        # Delete all
        if ids == "all":
            objs = StudyFactorLanguageAbility.objects.all()
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
                "message": f"All {count} Study Factor Language Ability record(s) permanently deleted.",
                "data": None
            }, status=status.HTTP_200_OK)

        # Bulk delete validation
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

        objs = StudyFactorLanguageAbility.objects.filter(uuid__in=valid_uuids)
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
            "message": f"{count} Study Factor Language Ability record(s) permanently deleted.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        }, status=status.HTTP_200_OK)
    


class StudyFactorLanguageAbilityExportAPIView(APIView):
    permission_classes = []  # Add IsAuthenticated if required


    def get(self, request):
        # --- Get query params ---
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')  # comma-separated fields
        uuids_param = request.GET.get('uuids', '')
        custom_sort = request.GET.get('customSort')  # e.g., language_ability_group:asc,created_at:desc
        search = request.GET.get('search', '').strip()
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        # --- Field to header mapping ---
        field_header_map = {
            'uuid': 'UUID',
            'factor_for': 'Factor For',
            'language_ability_group': 'Language Ability Group',
            'language_test_name': 'Language Test Name',
            'module_name': 'Module Name',
            'minimum_overall_score': 'Minimum Overall Score',
            'not_less_than': 'Not Less Than',
            'in_no_of_modules': 'In No of Modules',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'created_at': 'Created On',
            'updated_at': 'Modified On',
        }

        # --- Determine fields to export ---
        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())

        # --- Fetch queryset ---
        queryset = StudyFactorLanguageAbility.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)

        if search:
            queryset = queryset.filter(language_ability_group__name__istartswith=search)

        # --- Custom sorting logic ---
        sort_field_map = {
            'language_ability_group': 'language_ability_group__name',
            'in_no_of_modules': 'in_no_of_modules',
            'created_at': 'created_at',
            'updated_at': 'updated_at',
        }

        sort_fields = []

        if custom_sort:
            for rule in custom_sort.split(','):
                try:
                    field, order = rule.split(':')
                    field = field.strip()
                    order = order.strip().lower()

                    if field not in sort_field_map:
                        continue

                    orm_field = sort_field_map[field]

                    # Case-insensitive sorting for string fields
                    if field in ['language_ability_group']:
                        f = Lower(orm_field)
                    else:
                        f = F(orm_field)

                    sort_fields.append(f.asc(nulls_last=True) if order == 'asc' else f.desc(nulls_last=True))

                except ValueError:
                    continue
        else:
            sort_order = request.GET.get('sortOrder', 'desc')
            f = F('created_at')
            sort_fields = [f.desc(nulls_last=True) if sort_order == 'desc' else f.asc(nulls_last=True)]

        queryset = queryset.order_by(*sort_fields)

        # --- Prepare dataset ---
        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'StudyFactorLanguageAbility'

        for obj in queryset:
            row = []
            for field in field_list:
                value = getattr(obj, field, '')
                
                # Handle foreign keys
                if field in ['factor_for', 'language_ability_group', 'language_test_name', 'module_name', 'minimum_overall_score', 'not_less_than']:
                    fk_obj = getattr(obj, field, None)
                    value = getattr(fk_obj, 'name', '') if fk_obj else ''

                if field in ['created_at', 'updated_at'] and value:
                    value = timezone.localtime(value).strftime("%d-%m-%Y %I:%M:%S %p")
                elif isinstance(value, bool):
                    value = int(value)

                row.append(value if value is not None else '')
            dataset.append(row)

        # --- Export data ---
        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'StudyFactorLanguageAbility.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'StudyFactorLanguageAbility.xlsx'

        # --- Return response ---
        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
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
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split(".")[-1].lower()
        required_headers = {
            "factor for",
            "language ability group",
            "language test name",
            "module name",
            "minimum overall score",
            "not less than",
            "in no of modules",
        }
        optional_headers = {"description"}

        data = []
        try:
            # ---------- XLSX Handling ----------
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
                        "error": f'Sheet "{sheet_name}" not found in uploaded file',
                        "available_sheets": available_sheets,
                    }, status=400)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'Sheet "{sheet_name}" is empty.'
                    }, status=status.HTTP_400_BAD_REQUEST)

                headers = [str(cell.value).strip().lower() if cell.value else "" for cell in next(ws.iter_rows(min_row=1, max_row=1))]

                if not required_headers.issubset(set(headers)):
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f"Missing required headers. Required: {required_headers}, Found: {set(headers)}"
                    }, status=status.HTTP_400_BAD_REQUEST)

                for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    row_dict["_row_number"] = idx
                    data.append(row_dict)

            # ---------- CSV Handling ----------
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
                        }, status=status.HTTP_400_BAD_REQUEST)

                    data.append(row_lower)
            else:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "error": "Unsupported file format. Use .xlsx or .csv",
                }, status=status.HTTP_400_BAD_REQUEST)

            # ---------- Import Rows ----------
            imported_count = 0
            duplicates = []
            skipped_rows = []

            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")

                # Read values
                ff = row.get("factor for")
                lag = row.get("language ability group")
                ltn = row.get("language test name")
                mn = row.get("module name")
                msc = row.get("minimum overall score")
                nlt = row.get("not less than")
                in_no_modules = row.get("in no of modules") or 0
                description = row.get("description") or ""

                # Skip if mandatory FK missing
                if not ff or not lag or not ltn or not mn:
                    skipped_rows.append({"Row": row_number, "Reason": "Missing required FK value"})
                    continue

                # Resolve FK
                resolved = {
                    "factor_for": self.resolve_fk(FactorFor, ff),
                    "language_ability_group": self.resolve_fk(LanguageAbilityGroup, lag),
                    "language_test_name": self.resolve_fk(LanguageTest, ltn),
                    "module_name": self.resolve_fk(LanguagetestmoduleName, mn),
                    "minimum_overall_score": self.resolve_fk(LanguageTestResult, msc),
                    "not_less_than": self.resolve_fk(LanguageTestResult, nlt),
                }

                if any(v is None for v in resolved.values()):
                    skipped_rows.append({"Row": row_number, "Reason": "One or more FK not found"})
                    continue

                existing = StudyFactorLanguageAbility.objects.filter(
                    factor_for=resolved["factor_for"],
                    language_test_name=resolved["language_test_name"],
                    module_name=resolved["module_name"]
                ).first()

                if existing:
                    if not existing.is_deleted:
                        duplicates.append({"Row": row_number, "Reason": "Duplicate entry"})
                        continue
                    else:
                        existing.description = description
                        existing.in_no_of_modules = in_no_modules
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    StudyFactorLanguageAbility.objects.create(
                        **resolved,
                        in_no_of_modules=in_no_modules,
                        description=description
                    )
                    imported_count += 1

        except Exception as e:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": str(e),
            }, status=status.HTTP_400_BAD_REQUEST)

        # ---------- Final Response ----------
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": duplicates,
            "skipped_rows": skipped_rows,
        }, status=status.HTTP_200_OK)
    


#--------------------EntranctestAbility--------------------



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





class StudyFactorEntranceTestAbilityCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        serializer = StudyFactorEntranceTestAbilitySerializer(data=request.data)

        if serializer.is_valid():

            # Duplicate Check
            data = serializer.validated_data
            exists = StudyFactorEntranceTestAbility.objects.filter(
                factor_for=data["factor_for"],
                entrance_test_ability_group=data["entrance_test_ability_group"],
                entrance_test_name=data["entrance_test_name"],
                minimum_score_required=data["minimum_score_required"],
                is_deleted=False
            ).first()

            if exists:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "This record already exists."
                }, status=400)

            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Record created successfully",
                "data": serializer.data
            })

        return Response({
            "statusCode": 400,
            "status": False,
            "message": " ".join([msg for msgs in serializer.errors.values() for msg in msgs])
        }, status=400)
    





class StudyFactorEntranceTestAbilityListAPIView(APIView):
    def get(self, request):
        search = request.GET.get("search", "").strip()
        custom_sort = request.GET.get("customSort")  # e.g., name:asc,created_at:desc

        allowed_sort_fields = [
            "entrance_test_ability_group",
            "minimum_required_test_ability",
            "description",
            "created_at",
            "updated_at",
        ]

        queryset = StudyFactorEntranceTestAbility.objects.filter(is_deleted=False)

        #SEARCH — only on EntranceTest Ability Group name
        if search:
            queryset = queryset.filter(
                Q(entrance_test_ability_group__name__istartswith=search)
            )

        # --------------------------
        # SORTING FIELDS MAP
        # --------------------------
        sort_field_map = {
            "entrance_test_ability_group": "entrance_test_ability_group__name",
            "minimum_required_test_ability": "minimum_required_test_ability__name",
            "description": "description",
            "created_at": "created_at",
            "updated_at": "updated_at",
        }

        sort_fields = []

        # --------------------------
        # CUSTOM SORT LOGIC
        # --------------------------
        if custom_sort:
            for rule in custom_sort.split(","):
                try:
                    field, order = rule.split(":")
                    field = field.strip()
                    order = order.strip().lower()

                    if field not in sort_field_map:
                        continue

                    orm_field = sort_field_map[field]

                    # Case-insensitive for string fields
                    if field in [
                        "entrance_test_ability_group",
                        "minimum_required_test_ability",
                        "description",
                    ]:
                        f = Lower(orm_field)
                    else:
                        f = F(orm_field)

                    sort_fields.append(
                        f.asc(nulls_last=True)
                        if order == "asc"
                        else f.desc(nulls_last=True)
                    )
                except ValueError:
                    continue
        else:
            # Default sorting
            sort_by = request.GET.get("sortBy", "created_at")
            sort_order = request.GET.get("sortOrder", "desc")
            orm_field = sort_field_map.get(sort_by, "created_at")
            f = F(orm_field)
            sort_fields = [
                f.asc(nulls_last=True)
                if sort_order == "asc"
                else f.desc(nulls_last=True)
            ]

        queryset = queryset.order_by(*sort_fields)

        # Pagination
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = StudyFactorEntranceTestAbilitySerializer(result_page, many=True)

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
            ability = StudyFactorEntranceTestAbility.objects.get(uuid=uuid, is_deleted=False)
        except StudyFactorEntranceTestAbility.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Record not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = StudyFactorEntranceTestAbilitySerializer(ability, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Record updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        # Collect error messages in same style
        errors = serializer.errors
        messages = []
        for field, msgs in errors.items():
            messages.extend(msgs)
        message_text = " ".join(messages)

        return Response({
            "statusCode": 400,
            "status": False,
            "message": message_text,
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)
    


class StudyFactorEntranceTestAbilityDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get("id", None)

        # ----------------------------
        # SINGLE DELETE
        # ----------------------------
        if uuid:
            try:
                ability = StudyFactorEntranceTestAbility.objects.get(uuid=uuid)
                ability.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "Record permanently deleted.",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            except StudyFactorEntranceTestAbility.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Record not found.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        # ----------------------------
        # DELETE ALL
        # ----------------------------
        if ids == "all":
            objects = StudyFactorEntranceTestAbility.objects.all()
            count = objects.count()

            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No records found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

            objects.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} record(s) permanently deleted.",
                "data": None
            }, status=status.HTTP_200_OK)

        # ----------------------------
        # BULK DELETE (LIST OF UUIDs)
        # ----------------------------
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

        # Find matching records
        objects = StudyFactorEntranceTestAbility.objects.filter(uuid__in=valid_uuids)
        count = objects.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching records found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_404_NOT_FOUND)

        objects.delete()

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} record(s) permanently deleted.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        }, status=status.HTTP_200_OK)





class StudyFactorEntranceTestAbilityExportAPIView(APIView):

    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        # --- Query params ---
        format_type = request.GET.get("format", "xlsx").lower()
        fields = request.GET.get("fields")
        search = request.GET.get("search", "").strip()
        custom_sort = request.GET.get("customSort")
        uuids_param = request.GET.get("uuids", "")
        uuids = [u.strip() for u in uuids_param.split(",") if u]

        # --- Field to header mapping ---
        field_header_map = {
            "uuid": "UUID",
            "factor_for": "Factor For",
            "entrance_test_ability_group": "Entrance Test Ability Group",
            "entrance_test_name": "Entrance Test Name",
            "minimum_score_required": "Minimum Score Required",
            "description": "Description",
            "created_at": "Created On",
            "updated_at": "Modified On",
        }

        # --- Determine fields ---
        field_list = (
            [f.strip() for f in fields.split(",")] if fields else list(field_header_map.keys())
        )

        # --- Fetch data ---
        queryset = StudyFactorEntranceTestAbility.objects.filter(is_deleted=False)

        if uuids:
            queryset = queryset.filter(uuid__in=uuids)

        # Search only by Entrance Test Ability Group name (per your requirement)
        if search:
            queryset = queryset.filter(
                entrance_test_ability_group__name__istartswith=search
            )

        # --- Sorting mapping ---
        sort_field_map = {
            "factor_for": "factor_for__name",
            "entrance_test_ability_group": "entrance_test_ability_group__name",
            "entrance_test_name": "entrance_test_name__fullname",   # FIXED
            "minimum_score_required": "minimum_score_required__numeric_score",  # FIXED
            "description": "description",
            "created_at": "created_at",
            "updated_at": "updated_at",
        }

        sort_fields = []

        # --- Custom sorting ---
        if custom_sort:
            for rule in custom_sort.split(","):
                try:
                    field, order = rule.split(":")
                    field = field.strip()
                    order = order.strip().lower()

                    if field not in sort_field_map:
                        continue

                    orm_field = sort_field_map[field]

                    # Case-insensitive sorting for text fields
                    if field in [
                        "factor_for",
                        "entrance_test_ability_group",
                        "entrance_test_name",
                        "description",
                    ]:
                        f = Lower(orm_field)
                    else:
                        f = F(orm_field)

                    sort_fields.append(
                        f.asc(nulls_last=True) if order == "asc" else f.desc(nulls_last=True)
                    )

                except ValueError:
                    continue
        else:
            # Default sort by created_at desc
            sort_fields = [F("created_at").desc(nulls_last=True)]

        queryset = queryset.order_by(*sort_fields)

        # --- Prepare dataset ---
        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = "StudyFactor Entrance Test Ability Data"

        # --- Row building ---
        for obj in queryset:
            row = []
            for field in field_list:

                # --- Foreign Key & Special Field Handling ---
                if field == "factor_for":
                    value = getattr(obj.factor_for, "name", "")

                elif field == "entrance_test_ability_group":
                    value = getattr(obj.entrance_test_ability_group, "name", "")

                elif field == "entrance_test_name":
                    value = getattr(obj.entrance_test_name, "fullname", "")

                elif field == "minimum_score_required":
                    msr = obj.minimum_score_required

                    if msr:
                        # If numeric_score exists show it, otherwise fallback to string
                        numeric = getattr(msr, "numeric_score", None)
                        value = str(numeric) if numeric is not None else str(msr)
                    else:
                        value = ""

                else:
                    value = getattr(obj, field, None)

                # --- Date formatting ---
                if field in ["created_at", "updated_at"] and value:
                    try:
                        value = timezone.localtime(value).strftime("%d-%m-%Y %I:%M:%S %p")
                    except:
                        pass

                row.append(value if value is not None else "")

            dataset.append(row)

        # --- Export generation ---
        if format_type == "csv":
            file_data = dataset.export("csv")
            content_type = "text/csv"
            file_name = "StudyFactorEntranceTestAbility.csv"
            response_data = file_data
        else:
            file_data = dataset.export("xlsx")
            output = io.BytesIO(file_data)
            content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            file_name = "StudyFactorEntranceTestAbility.xlsx"
            response_data = output.getvalue()

        response = HttpResponse(response_data, content_type=content_type)
        response["Content-Disposition"] = f'attachment; filename="{file_name}"'
        return response




class StudyFactorEntranceTestAbilityImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'statusCode': 400, 'status': False, 'message': 'No file uploaded'}, status=400)

        format_type = file.name.split('.')[-1].lower()

        # Required & Optional Headers
        required_headers = {
            'factor for',
            'entrance test ability group',
            'entrance test name',
            'minimum score required',
        }

        optional_headers = {
            'description'
        }

        try:
            # ---------------- Load file ----------------
            data = []

            if format_type == 'xlsx':
                wb = openpyxl.load_workbook(file, read_only=True)
                sheets = wb.sheetnames

                if not sheet_name:
                    return Response({
                        'statusCode': 400,
                        'status': False,
                        'message': 'Please provide sheet_name',
                        'available_sheets': sheets
                    }, status=400)

                if sheet_name not in sheets:
                    return Response({
                        'statusCode': 400,
                        'status': False,
                        'message': f'Sheet "{sheet_name}" not found',
                        'available_sheets': sheets
                    }, status=400)

                ws = wb[sheet_name]

                if ws.max_row <= 1:
                    return Response({
                        'statusCode': 400,
                        'status': False,
                        'message': f'Sheet "{sheet_name}" is empty'
                    }, status=400)

                headers = [
                    str(cell.value).strip().lower() if cell.value else ''
                    for cell in next(ws.iter_rows(min_row=1, max_row=1))
                ]

                if not required_headers.issubset(set(headers)):
                    return Response({
                        'statusCode': 400,
                        'status': False,
                        'message': f'Missing required headers: {required_headers - set(headers)}'
                    }, status=400)

                for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    row_dict = dict(zip(headers, row))
                    row_dict['_row_number'] = idx
                    data.append(row_dict)

            elif format_type == 'csv':
                decoded_file = file.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(decoded_file))

                for idx, row in enumerate(reader, start=2):
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    row_lower['_row_number'] = idx

                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({
                            'statusCode': 400,
                            'status': False,
                            'message': f'Missing required headers: {required_headers - set(row_lower.keys())}'
                        }, status=400)

                    data.append(row_lower)

            else:
                return Response({
                    'statusCode': 400,
                    'status': False,
                    'message': 'Unsupported file format. Use .xlsx or .csv'
                }, status=400)

            # ---------------- Preload Foreign Key Models ----------------
            factor_for_map = {x.name.strip().lower(): x for x in FactorFor.objects.all()}
            ability_group_map = {x.name.strip().lower(): x for x in EntranceTestAbilityGroup.objects.all()}
            test_name_map = {x.fullname.strip().lower(): x for x in EntranceTestName.objects.all()}
            min_score_map = {x.testresult.strip().lower(): x for x in EntranceTestResult.objects.all()}

            # Preload existing objects for duplicate checking
            existing_map = {
                (
                    obj.factor_for.name.strip().lower(),
                    obj.entrance_test_ability_group.name.strip().lower(),
                    obj.entrance_test_name.fullname.strip().lower(),
                    obj.minimum_score_required.testresult.strip().lower(),
                ): obj
                for obj in StudyFactorEntranceTestAbility.objects.all()
            }

            # ---------------- Process Rows ----------------
            to_create = []
            duplicates = []
            skipped_rows = []
            existing_in_file = set()

            for row in data:
                row_number = row.get('_row_number')

                factor_for_val = (row.get('factor for') or '').strip().lower()
                ability_group_val = (row.get('entrance test ability group') or '').strip().lower()
                test_name_val = (row.get('entrance test name') or '').strip().lower()
                min_score_val = (row.get('minimum score required') or '').strip().lower()
                description = (row.get('description') or '').strip()

                # ---- Required field check ----
                if not (factor_for_val and ability_group_val and test_name_val and min_score_val):
                    skipped_rows.append({
                        "Row": row_number,
                        "Reason": "Missing one or more required fields"
                    })
                    continue

                # ---- Resolve foreign keys ----
                factor_obj = factor_for_map.get(factor_for_val)
                group_obj = ability_group_map.get(ability_group_val)
                test_obj = test_name_map.get(test_name_val)
                min_score_obj = min_score_map.get(min_score_val)

                if not factor_obj or not group_obj or not test_obj or not min_score_obj:
                    skipped_rows.append({
                        "Row": row_number,
                        "Reason": "Foreign key value not found"
                    })
                    continue

                key = (factor_for_val, ability_group_val, test_name_val, min_score_val)

                # ---- Duplicate checks ----
                if key in existing_map and not existing_map[key].is_deleted:
                    duplicates.append({
                        "Row": row_number,
                        "Reason": "Duplicate entry already exists"
                    })
                    continue

                if key in existing_in_file:
                    duplicates.append({
                        "Row": row_number,
                        "Reason": "Duplicate inside file"
                    })
                    continue

                existing_in_file.add(key)

                # ---- Soft-delete reactivation ----
                if key in existing_map and existing_map[key].is_deleted:
                    obj = existing_map[key]
                    obj.description = description
                    obj.is_deleted = False
                    obj.save()
                    continue

                # ---- Prepare new object ----
                to_create.append(
                    StudyFactorEntranceTestAbility(
                        factor_for=factor_obj,
                        entrance_test_ability_group=group_obj,
                        entrance_test_name=test_obj,
                        minimum_score_required=min_score_obj,
                        description=description,
                        is_deleted=False
                    )
                )

            # ---------------- Bulk Create ----------------
            with transaction.atomic():
                StudyFactorEntranceTestAbility.objects.bulk_create(to_create, ignore_conflicts=True, batch_size=500)

            return Response({
                "statusCode": 200,
                "status": True,
                "imported_count": len(to_create),
                "duplicates": list(reversed(duplicates)),
                "skipped_rows": list(reversed(skipped_rows)),
                "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful"
            }, status=200)

        except Exception as e:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": str(e)
            }, status=400)




