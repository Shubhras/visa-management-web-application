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
    



class InstituteTypeListAPIView(APIView):
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['name', 'description', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = InstituteType.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(Q(name__istartswith=search))

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = InstituteTypeSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

# -------------------- CREATE API --------------------
class InstituteTypeCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        name = request.data.get("name", "").strip()
        existing = InstituteType.objects.filter(name__iexact=name, is_deleted=False).first()

        if existing:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "InstituteType with this name already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = InstituteTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "InstituteType created successfully",
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

# -------------------- RETRIEVE API --------------------
class InstituteTypeRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            inst_type = InstituteType.objects.get(uuid=uuid, is_deleted=False)
        except InstituteType.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "InstituteType not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = InstituteTypeSerializer(inst_type)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "InstituteType retrieved successfully",
            "data": serializer.data
        })

# -------------------- UPDATE API --------------------
class InstituteTypeUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            inst_type = InstituteType.objects.get(uuid=uuid, is_deleted=False)
        except InstituteType.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "InstituteType not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = InstituteTypeSerializer(inst_type, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "InstituteType updated successfully",
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

# -------------------- DELETE API --------------------
class InstituteTypeDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get('id', None)

        if uuid:
            try:
                inst_type = InstituteType.objects.get(uuid=uuid)
                inst_type.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "InstituteType permanently deleted.",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            except InstituteType.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "InstituteType not found.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        if ids == "all":
            inst_types = InstituteType.objects.all()
            count = inst_types.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No InstituteTypes found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
            inst_types.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} InstituteTypes permanently deleted.",
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

        inst_types = InstituteType.objects.filter(uuid__in=valid_uuids)
        count = inst_types.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching InstituteTypes found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_404_NOT_FOUND)

        inst_types.delete()
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} InstituteType(s) permanently deleted.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        })

# -------------------- EXPORT API --------------------
class InstituteTypeExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'name': 'Institute Type',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'updated_at': 'Modified On',
        }

        if fields:
            field_list = [f.strip() for f in fields.split(',')]
        else:
            field_list = list(field_header_map.keys())

        queryset = InstituteType.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'InstituteType'

        for inst_type in queryset:
            row = []
            for field in field_list:
                value = getattr(inst_type, field, '')
                if field in ['created_at', 'updated_at'] and value:
                    value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
                elif isinstance(value, bool):
                    value = int(value)
                row.append(value if value is not None else '')
            dataset.append(row)

        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'institutetypes.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'institutetypes.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response

# -------------------- IMPORT API --------------------
class InstituteTypeImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get("file")
        sheet_name = request.data.get("sheet_name")

        if not file:
            return Response({"error": "No file uploaded"}, status=400)

        format_type = file.name.split(".")[-1].lower()
        duplicates = []
        skipped_rows = []
        required_headers = {"institute type"}
        optional_headers = {"description"}

        try:
            data = []

            # -------- XLSX --------
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

            # -------- CSV --------
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

            # -------- Prepare for bulk create --------
            bulk_list = []
            imported_count = 0

            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")
                name = str(row.get("institute type")).strip() if row.get("institute type") else None
                description = str(row.get("description")).strip() if row.get("description") else ""

                if not name:
                    skipped_rows.append({"Row": row_number, "Institute Type": name or "", "Description":description or "","Reason": "Missing InstituteType name"})
                    continue

                existing = InstituteType.objects.filter(name__iexact=name).first()
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({"Row": row_number, "Institute Type": name, "Description":description or "", "Reason": "Already exists"})
                        continue
                    else:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    bulk_list.append(InstituteType(name=name, description=description, is_deleted=False))
                    imported_count += 1

            # Bulk insert new records
            if bulk_list:
                InstituteType.objects.bulk_create(bulk_list)

        except Exception as e:
            return Response({"statusCode": 400, "status": False, "message": str(e)}, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": list(reversed(duplicates)),
            "skipped_rows": list(reversed(skipped_rows))
        }, status=200)



class InstituteGroupNameListAPIView(APIView):
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['name', 'description', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = InstituteGroupName.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(Q(name__istartswith=search))

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = InstituteGroupNameSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

# -------------------- CREATE API --------------------
class InstituteGroupNameCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        name = request.data.get("name", "").strip()
        existing = InstituteGroupName.objects.filter(name__iexact=name, is_deleted=False).first()

        if existing:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "InstituteGroupName with this name already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = InstituteGroupNameSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "InstituteGroupName created successfully",
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

# -------------------- RETRIEVE API --------------------
class InstituteGroupNameRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            inst_group = InstituteGroupName.objects.get(uuid=uuid, is_deleted=False)
        except InstituteGroupName.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "InstituteGroupName not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = InstituteGroupNameSerializer(inst_group)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "InstituteGroupName retrieved successfully",
            "data": serializer.data
        })

# -------------------- UPDATE API --------------------
class InstituteGroupNameUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            inst_group = InstituteGroupName.objects.get(uuid=uuid, is_deleted=False)
        except InstituteGroupName.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "InstituteGroupName not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = InstituteGroupNameSerializer(inst_group, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "InstituteGroupName updated successfully",
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

# -------------------- DELETE API --------------------
class InstituteGroupNameDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get('id', None)

        if uuid:
            try:
                inst_group = InstituteGroupName.objects.get(uuid=uuid)
                inst_group.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "InstituteGroupName permanently deleted.",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            except InstituteGroupName.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "InstituteGroupName not found.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        if ids == "all":
            inst_groups = InstituteGroupName.objects.all()
            count = inst_groups.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No InstituteGroupNames found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
            inst_groups.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} InstituteGroupNames permanently deleted.",
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

        inst_groups = InstituteGroupName.objects.filter(uuid__in=valid_uuids)
        count = inst_groups.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching InstituteGroupNames found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_404_NOT_FOUND)

        inst_groups.delete()
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} InstituteGroupName(s) permanently deleted.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        })

# -------------------- EXPORT API --------------------
class InstituteGroupNameExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'name': 'Institute Group Name',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'updated_at': 'Modified On',
        }

        if fields:
            field_list = [f.strip() for f in fields.split(',')]
        else:
            field_list = list(field_header_map.keys())

        queryset = InstituteGroupName.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'InstituteGroupName'

        for inst_group in queryset:
            row = []
            for field in field_list:
                value = getattr(inst_group, field, '')
                if field in ['created_at', 'updated_at'] and value:
                    value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
                elif isinstance(value, bool):
                    value = int(value)
                row.append(value if value is not None else '')
            dataset.append(row)

        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'institutegroupnames.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'institutegroupnames.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response

# -------------------- IMPORT API --------------------
class InstituteGroupNameImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get("file")
        sheet_name = request.data.get("sheet_name")

        if not file:
            return Response({"error": "No file uploaded"}, status=400)

        format_type = file.name.split(".")[-1].lower()
        duplicates = []
        skipped_rows = []
        required_headers = {"institute group name"}
        optional_headers = {"description"}

        try:
            data = []

            # -------- XLSX --------
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

            # -------- CSV --------
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

            # -------- Prepare for bulk create --------
            bulk_list = []
            imported_count = 0

            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")
                name = str(row.get("institute group name")).strip() if row.get("institute group name") else None
                description = str(row.get("description")).strip() if row.get("description") else ""

                if not name:
                    skipped_rows.append({"Row": row_number,"Institute Group Name": name or "", "Description":description or "", "Reason": "Missing Group Name"})
                    continue

                existing = InstituteGroupName.objects.filter(name__iexact=name).first()
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({"Row": row_number, "Institute Group Name": name,"Description":description or "", "Reason": "Already exists"})
                        continue
                    else:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    bulk_list.append(InstituteGroupName(name=name, description=description, is_deleted=False))
                    imported_count += 1

            # Bulk insert new records
            if bulk_list:
                InstituteGroupName.objects.bulk_create(bulk_list)

        except Exception as e:
            return Response({"statusCode": 400, "status": False, "message": str(e)}, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": list(reversed(duplicates)),
            "skipped_rows": list(reversed(skipped_rows))
        }, status=200)


class InstituteStatusListAPIView(APIView):
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['name', 'description', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = InstituteStatus.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(Q(name__istartswith=search))

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = InstituteStatusSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

# -------------------- CREATE API --------------------
class InstituteStatusCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        name = request.data.get("name", "").strip()
        existing = InstituteStatus.objects.filter(name__iexact=name, is_deleted=False).first()

        if existing:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "InstituteStatus with this name already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = InstituteStatusSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "InstituteStatus created successfully",
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

# -------------------- RETRIEVE API --------------------
class InstituteStatusRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            inst_status = InstituteStatus.objects.get(uuid=uuid, is_deleted=False)
        except InstituteStatus.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "InstituteStatus not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = InstituteStatusSerializer(inst_status)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "InstituteStatus retrieved successfully",
            "data": serializer.data
        })

# -------------------- UPDATE API --------------------
class InstituteStatusUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            inst_status = InstituteStatus.objects.get(uuid=uuid, is_deleted=False)
        except InstituteStatus.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "InstituteStatus not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = InstituteStatusSerializer(inst_status, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "InstituteStatus updated successfully",
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

# -------------------- DELETE API --------------------
class InstituteStatusDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get('id', None)

        if uuid:
            try:
                inst_status = InstituteStatus.objects.get(uuid=uuid)
                inst_status.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "InstituteStatus permanently deleted.",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            except InstituteStatus.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "InstituteStatus not found.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        if ids == "all":
            inst_statuses = InstituteStatus.objects.all()
            count = inst_statuses.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No InstituteStatus found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
            inst_statuses.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} InstituteStatus permanently deleted.",
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

        inst_statuses = InstituteStatus.objects.filter(uuid__in=valid_uuids)
        count = inst_statuses.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching InstituteStatus found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_404_NOT_FOUND)

        inst_statuses.delete()
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} InstituteStatus(es) permanently deleted.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        })

# -------------------- EXPORT API --------------------
class InstituteStatusExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'name': 'Institute Status Name',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'updated_at': 'Modified On',
        }

        if fields:
            field_list = [f.strip() for f in fields.split(',')]
        else:
            field_list = list(field_header_map.keys())

        queryset = InstituteStatus.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'InstituteStatus'

        for inst_status in queryset:
            row = []
            for field in field_list:
                value = getattr(inst_status, field, '')
                if field in ['created_at', 'updated_at'] and value:
                    value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
                elif isinstance(value, bool):
                    value = int(value)
                row.append(value if value is not None else '')
            dataset.append(row)

        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'institutestatus.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'institutestatus.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response

# -------------------- IMPORT API --------------------
class InstituteStatusImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get("file")
        sheet_name = request.data.get("sheet_name")

        if not file:
            return Response({"error": "No file uploaded"}, status=400)

        format_type = file.name.split(".")[-1].lower()
        duplicates = []
        skipped_rows = []
        required_headers = {"institute status name"}
        optional_headers = {"description"}

        try:
            data = []

            # -------- XLSX --------
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

            # -------- CSV --------
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

            # -------- Prepare for bulk_create --------
            bulk_list = []
            imported_count = 0

            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")
                name = str(row.get("institute status name")).strip() if row.get("institute status name") else None
                description = str(row.get("description")).strip() if row.get("description") else ""

                if not name:
                    skipped_rows.append({"Row": row_number,"Institute Status Name": name or "", "Description":description or "", "Reason": "Missing Status Name"})
                    continue

                existing = InstituteStatus.objects.filter(name__iexact=name).first()
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({"Row": row_number, "Institute Status Name": name, "Description":description or "", "Reason": "Already exists"})
                        continue
                    else:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    bulk_list.append(InstituteStatus(name=name, description=description, is_deleted=False))
                    imported_count += 1

            # Bulk insert
            if bulk_list:
                InstituteStatus.objects.bulk_create(bulk_list)

        except Exception as e:
            return Response({"statusCode": 400, "status": False, "message": str(e)}, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": list(reversed(duplicates)),
            "skipped_rows": list(reversed(skipped_rows))
        }, status=200)


class InstitutePriorityListAPIView(APIView):
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['name', 'description', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = InstitutePriority.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(Q(name__istartswith=search))

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = InstitutePrioritySerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

# -------------------- CREATE API --------------------
class InstitutePriorityCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        name = request.data.get("name", "").strip()
        existing = InstitutePriority.objects.filter(name__iexact=name, is_deleted=False).first()

        if existing:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "InstitutePriority with this name already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = InstitutePrioritySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "InstitutePriority created successfully",
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

# -------------------- RETRIEVE API --------------------
class InstitutePriorityRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            priority = InstitutePriority.objects.get(uuid=uuid, is_deleted=False)
        except InstitutePriority.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "InstitutePriority not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = InstitutePrioritySerializer(priority)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "InstitutePriority retrieved successfully",
            "data": serializer.data
        })

# -------------------- UPDATE API --------------------
class InstitutePriorityUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            priority = InstitutePriority.objects.get(uuid=uuid, is_deleted=False)
        except InstitutePriority.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "InstitutePriority not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = InstitutePrioritySerializer(priority, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "InstitutePriority updated successfully",
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

# -------------------- DELETE API --------------------
class InstitutePriorityDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get('id', None)

        if uuid:
            try:
                priority = InstitutePriority.objects.get(uuid=uuid)
                priority.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "InstitutePriority permanently deleted.",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            except InstitutePriority.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "InstitutePriority not found.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        if ids == "all":
            priorities = InstitutePriority.objects.all()
            count = priorities.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No InstitutePriority found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
            priorities.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} InstitutePriority permanently deleted.",
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

        priorities = InstitutePriority.objects.filter(uuid__in=valid_uuids)
        count = priorities.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching InstitutePriority found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_404_NOT_FOUND)

        priorities.delete()
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} InstitutePriority(es) permanently deleted.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        })

# -------------------- EXPORT API --------------------
class InstitutePriorityExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'name': 'Institute Priority Name',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'updated_at': 'Modified On',
        }

        if fields:
            field_list = [f.strip() for f in fields.split(',')]
        else:
            field_list = list(field_header_map.keys())

        queryset = InstitutePriority.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'InstitutePriority'

        for priority in queryset:
            row = []
            for field in field_list:
                value = getattr(priority, field, '')
                if field in ['created_at', 'updated_at'] and value:
                    value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
                elif isinstance(value, bool):
                    value = int(value)
                row.append(value if value is not None else '')
            dataset.append(row)

        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'institutepriority.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'institutepriority.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response

# -------------------- IMPORT API --------------------
class InstitutePriorityImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get("file")
        sheet_name = request.data.get("sheet_name")

        if not file:
            return Response({"error": "No file uploaded"}, status=400)

        format_type = file.name.split(".")[-1].lower()
        duplicates = []
        skipped_rows = []
        required_headers = {"institute priority name"}
        optional_headers = {"description"}

        try:
            data = []

            # -------- XLSX --------
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

            # -------- CSV --------
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

            # -------- Prepare for bulk_create --------
            bulk_list = []
            imported_count = 0

            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")
                name = str(row.get("institute priority name")).strip() if row.get("institute priority name") else None
                description = str(row.get("description")).strip() if row.get("description") else ""

                if not name:
                    skipped_rows.append({"Row": row_number,"Institute Priority Name": name or "","Description":description or "", "Reason": "Missing Priority Name"})
                    continue

                existing = InstitutePriority.objects.filter(name__iexact=name).first()
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({"Row": row_number, "Institute Priority Name": name,"Description":description or "", "Reason": "Already exists"})
                        continue
                    else:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    bulk_list.append(InstitutePriority(name=name, description=description, is_deleted=False))
                    imported_count += 1

            # Bulk insert
            if bulk_list:
                InstitutePriority.objects.bulk_create(bulk_list)

        except Exception as e:
            return Response({"statusCode": 400, "status": False, "message": str(e)}, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": list(reversed(duplicates)),
            "skipped_rows": list(reversed(skipped_rows))
        }, status=200)


class InstituteDepartmentListAPIView(APIView):
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['name', 'description', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = InstituteDepartment.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(Q(name__istartswith=search))

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = InstituteDepartmentSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

# -------------------- CREATE API --------------------
class InstituteDepartmentCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        name = request.data.get("name", "").strip()
        existing = InstituteDepartment.objects.filter(name__iexact=name, is_deleted=False).first()

        if existing:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "InstituteDepartment with this name already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = InstituteDepartmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "InstituteDepartment created successfully",
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

# -------------------- RETRIEVE API --------------------
class InstituteDepartmentRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            department = InstituteDepartment.objects.get(uuid=uuid, is_deleted=False)
        except InstituteDepartment.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "InstituteDepartment not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = InstituteDepartmentSerializer(department)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "InstituteDepartment retrieved successfully",
            "data": serializer.data
        })

# -------------------- UPDATE API --------------------
class InstituteDepartmentUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            department = InstituteDepartment.objects.get(uuid=uuid, is_deleted=False)
        except InstituteDepartment.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "InstituteDepartment not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = InstituteDepartmentSerializer(department, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "InstituteDepartment updated successfully",
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

# -------------------- DELETE API --------------------
class InstituteDepartmentDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get('id', None)

        if uuid:
            try:
                department = InstituteDepartment.objects.get(uuid=uuid)
                department.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "InstituteDepartment permanently deleted.",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            except InstituteDepartment.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "InstituteDepartment not found.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        if ids == "all":
            departments = InstituteDepartment.objects.all()
            count = departments.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No InstituteDepartment found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
            departments.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} InstituteDepartment permanently deleted.",
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

        departments = InstituteDepartment.objects.filter(uuid__in=valid_uuids)
        count = departments.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching InstituteDepartment found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_404_NOT_FOUND)

        departments.delete()
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} InstituteDepartment(s) permanently deleted.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        })

# -------------------- EXPORT API --------------------
class InstituteDepartmentExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'name': 'Institute Department Name',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'updated_at': 'Modified On',
        }

        if fields:
            field_list = [f.strip() for f in fields.split(',')]
        else:
            field_list = list(field_header_map.keys())

        queryset = InstituteDepartment.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'InstituteDepartment'

        for dept in queryset:
            row = []
            for field in field_list:
                value = getattr(dept, field, '')
                if field in ['created_at', 'updated_at'] and value:
                    value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
                elif isinstance(value, bool):
                    value = int(value)
                row.append(value if value is not None else '')
            dataset.append(row)

        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'institutedepartment.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'institutedepartment.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response

# -------------------- IMPORT API --------------------
class InstituteDepartmentImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get("file")
        sheet_name = request.data.get("sheet_name")

        if not file:
            return Response({"error": "No file uploaded"}, status=400)

        format_type = file.name.split(".")[-1].lower()
        duplicates = []
        skipped_rows = []
        required_headers = {"institute department name"}
        optional_headers = {"description"}

        try:
            data = []

            # -------- XLSX --------
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

            # -------- CSV --------
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

            # -------- Prepare for bulk_create --------
            bulk_list = []
            imported_count = 0

            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")
                name = str(row.get("institute department name")).strip() if row.get("institute department name") else None
                description = str(row.get("description")).strip() if row.get("description") else ""

                if not name:
                    skipped_rows.append({"Row": row_number, "Institute Department Name": name or "","Description":description or "", "Reason": "Missing Department Name"})
                    continue

                existing = InstituteDepartment.objects.filter(name__iexact=name).first()
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({"Row": row_number, "Institute Department Name": name,"Description":description or "", "Reason": "Already exists"})
                        continue
                    else:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    bulk_list.append(InstituteDepartment(name=name, description=description, is_deleted=False))
                    imported_count += 1

            # Bulk insert
            if bulk_list:
                InstituteDepartment.objects.bulk_create(bulk_list)

        except Exception as e:
            return Response({"statusCode": 400, "status": False, "message": str(e)}, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": list(reversed(duplicates)),
            "skipped_rows": list(reversed(skipped_rows))
        }, status=200)

class BankAccountForListAPIView(APIView):
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['name', 'description', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = BankAccountFor.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(Q(name__istartswith=search))

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = BankAccountForSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

# -------------------- CREATE API --------------------
class BankAccountForCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        name = request.data.get("name", "").strip()
        existing = BankAccountFor.objects.filter(name__iexact=name, is_deleted=False).first()

        if existing:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "BankAccountFor with this name already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = BankAccountForSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "BankAccountFor created successfully",
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

# -------------------- RETRIEVE API --------------------
class BankAccountForRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = BankAccountFor.objects.get(uuid=uuid, is_deleted=False)
        except BankAccountFor.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "BankAccountFor not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = BankAccountForSerializer(obj)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "BankAccountFor retrieved successfully",
            "data": serializer.data
        })

# -------------------- UPDATE API --------------------
class BankAccountForUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = BankAccountFor.objects.get(uuid=uuid, is_deleted=False)
        except BankAccountFor.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "BankAccountFor not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = BankAccountForSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "BankAccountFor updated successfully",
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

# -------------------- DELETE API --------------------
class BankAccountForDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get('id', None)

        if uuid:
            try:
                obj = BankAccountFor.objects.get(uuid=uuid)
                obj.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "BankAccountFor permanently deleted.",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            except BankAccountFor.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "BankAccountFor not found.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        if ids == "all":
            objs = BankAccountFor.objects.all()
            count = objs.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No BankAccountFor found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
            objs.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} BankAccountFor permanently deleted.",
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

        objs = BankAccountFor.objects.filter(uuid__in=valid_uuids)
        count = objs.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching BankAccountFor found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_404_NOT_FOUND)

        objs.delete()
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} BankAccountFor(s) permanently deleted.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        })

# -------------------- EXPORT API --------------------
class BankAccountForExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'name': 'Bank Account',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'updated_at': 'Modified On',
        }

        if fields:
            field_list = [f.strip() for f in fields.split(',')]
        else:
            field_list = list(field_header_map.keys())

        queryset = BankAccountFor.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'BankAccountFor'

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
            file_name = 'bankaccountfor.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'bankaccountfor.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response

# -------------------- IMPORT API --------------------
class BankAccountForImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get("file")
        sheet_name = request.data.get("sheet_name")

        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split(".")[-1].lower()
        duplicates = []
        skipped_rows = []
        required_headers = {"bank account"}  # adjust to match sheet
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
                name = str(row.get("bank account")) if row.get("bank account") else None
                description = str(row.get("description")).strip() if row.get("description") else ""

                if not name:
                    skipped_rows.append({"Row": row_number,"Bank Account ": name or "","Description":description or "", "Reason": "Missing Name"})
                    continue

                existing = BankAccountFor.objects.filter(name__iexact=name).first()
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({"Row": row_number, "Bank Account ": name,"Description":description or "", "Reason": "Already exists"})
                        continue
                    else:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    BankAccountFor.objects.create(name=name, description=description, is_deleted=False)
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


class WhenCommissionIssueListAPIView(APIView):
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['name', 'description', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = WhenCommissionIssue.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(Q(name__istartswith=search))

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = WhenCommissionIssueSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

# -------------------- CREATE API --------------------
class WhenCommissionIssueCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        name = request.data.get("name", "").strip()
        existing = WhenCommissionIssue.objects.filter(name__iexact=name, is_deleted=False).first()

        if existing:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "WhenCommissionIssue with this name already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = WhenCommissionIssueSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "WhenCommissionIssue created successfully",
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

# -------------------- RETRIEVE API --------------------
class WhenCommissionIssueRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = WhenCommissionIssue.objects.get(uuid=uuid, is_deleted=False)
        except WhenCommissionIssue.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "WhenCommissionIssue not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = WhenCommissionIssueSerializer(obj)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "WhenCommissionIssue retrieved successfully",
            "data": serializer.data
        })

# -------------------- UPDATE API --------------------
class WhenCommissionIssueUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = WhenCommissionIssue.objects.get(uuid=uuid, is_deleted=False)
        except WhenCommissionIssue.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "WhenCommissionIssue not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = WhenCommissionIssueSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "WhenCommissionIssue updated successfully",
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

# -------------------- DELETE API --------------------
class WhenCommissionIssueDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get('id', None)

        if uuid:
            try:
                obj = WhenCommissionIssue.objects.get(uuid=uuid)
                obj.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "WhenCommissionIssue permanently deleted.",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            except WhenCommissionIssue.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "WhenCommissionIssue not found.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        if ids == "all":
            objs = WhenCommissionIssue.objects.all()
            count = objs.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No WhenCommissionIssue found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
            objs.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} WhenCommissionIssue permanently deleted.",
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

        objs = WhenCommissionIssue.objects.filter(uuid__in=valid_uuids)
        count = objs.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching WhenCommissionIssue found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_404_NOT_FOUND)

        objs.delete()
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} WhenCommissionIssue(s) permanently deleted.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        })

# -------------------- EXPORT API --------------------
class WhenCommissionIssueExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'name': 'When Commission Issue',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'updated_at': 'Modified On',
        }

        if fields:
            field_list = [f.strip() for f in fields.split(',')]
        else:
            field_list = list(field_header_map.keys())

        queryset = WhenCommissionIssue.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'WhenCommissionIssue'

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
            file_name = 'whencommissionissue.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'whencommissionissue.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response

# -------------------- IMPORT API --------------------
class WhenCommissionIssueImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get("file")
        sheet_name = request.data.get("sheet_name")

        if not file:
            return Response({"error": "No file uploaded"}, status=400)

        format_type = file.name.split(".")[-1].lower()
        duplicates = []
        skipped_rows = []
        required_headers = {"when commission issue"}
        optional_headers = {"description"}

        try:
            data = []

            # -------- XLSX --------
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

            # -------- CSV --------
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

            # -------- Prepare for bulk_create --------
            bulk_list = []
            imported_count = 0

            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")
                name = str(row.get("when commission issue")).strip() if row.get("when commission issue") else None
                description = str(row.get("description")).strip() if row.get("description") else ""

                if not name:
                    skipped_rows.append({"Row": row_number, "When Commission Issue": name or "","Description":description or "", "Reason": "Missing Name"})
                    continue

                existing = WhenCommissionIssue.objects.filter(name__iexact=name).first()
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({"Row": row_number, "When Commission Issue": name,"Description":description or "", "Reason": "Already exists"})
                        continue
                    else:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    bulk_list.append(WhenCommissionIssue(name=name, description=description, is_deleted=False))
                    imported_count += 1

            # Bulk insert
            if bulk_list:
                WhenCommissionIssue.objects.bulk_create(bulk_list)

        except Exception as e:
            return Response({"statusCode": 400, "status": False, "message": str(e)}, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": list(reversed(duplicates)),
            "skipped_rows": list(reversed(skipped_rows))
        }, status=200)


class CourseLevelCodeListAPIView(APIView):
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['name', 'description', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = CourseLevelCode.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(Q(name__istartswith=search))

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = CourseLevelCodeSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

# -------------------- CREATE API --------------------
class CourseLevelCodeCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        name = request.data.get("name", "").strip()
        existing = CourseLevelCode.objects.filter(name__iexact=name, is_deleted=False).first()

        if existing:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "CourseLevelCode with this name already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = CourseLevelCodeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "CourseLevelCode created successfully",
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

# -------------------- RETRIEVE API --------------------
class CourseLevelCodeRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = CourseLevelCode.objects.get(uuid=uuid, is_deleted=False)
        except CourseLevelCode.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "CourseLevelCode not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = CourseLevelCodeSerializer(obj)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "CourseLevelCode retrieved successfully",
            "data": serializer.data
        })

# -------------------- UPDATE API --------------------
class CourseLevelCodeUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = CourseLevelCode.objects.get(uuid=uuid, is_deleted=False)
        except CourseLevelCode.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "CourseLevelCode not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = CourseLevelCodeSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "CourseLevelCode updated successfully",
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

# -------------------- DELETE API --------------------
class CourseLevelCodeDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get('id', None)

        if uuid:
            try:
                obj = CourseLevelCode.objects.get(uuid=uuid)
                obj.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "CourseLevelCode permanently deleted.",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            except CourseLevelCode.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "CourseLevelCode not found.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        if ids == "all":
            objs = CourseLevelCode.objects.all()
            count = objs.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No CourseLevelCode found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
            objs.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} CourseLevelCode permanently deleted.",
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

        objs = CourseLevelCode.objects.filter(uuid__in=valid_uuids)
        count = objs.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching CourseLevelCode found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_404_NOT_FOUND)

        objs.delete()
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} CourseLevelCode(s) permanently deleted.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        })

# -------------------- EXPORT API --------------------
class CourseLevelCodeExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'name': 'Course Level Code',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'updated_at': 'Modified On',
        }

        if fields:
            field_list = [f.strip() for f in fields.split(',')]
        else:
            field_list = list(field_header_map.keys())

        queryset = CourseLevelCode.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'CourseLevelCode'

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
            file_name = 'courselevelcode.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'courselevelcode.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response

# -------------------- IMPORT API --------------------
class CourseLevelCodeImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get("file")
        sheet_name = request.data.get("sheet_name")

        if not file:
            return Response({"error": "No file uploaded"}, status=400)

        format_type = file.name.split(".")[-1].lower()
        duplicates = []
        skipped_rows = []
        required_headers = {"course level code"}
        optional_headers = {"description"}

        try:
            data = []

            # -------- XLSX --------
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

            # -------- CSV --------
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

            # -------- Prepare for bulk_create --------
            bulk_list = []
            imported_count = 0

            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")
                name = str(row.get("course level code")).strip() if row.get("course level code") else None
                description = str(row.get("description")).strip() if row.get("description") else ""

                if not name:
                    skipped_rows.append({"Row": row_number,"Course Level Code": name or "","Description":description or "", "Reason": "Missing Name"})
                    continue

                existing = CourseLevelCode.objects.filter(name__iexact=name).first()
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({"Row": row_number, "Course Level Code": name,"Description":description or "", "Reason": "Already exists"})
                        continue
                    else:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    bulk_list.append(CourseLevelCode(name=name, description=description, is_deleted=False))
                    imported_count += 1

            # Bulk insert
            if bulk_list:
                CourseLevelCode.objects.bulk_create(bulk_list)

        except Exception as e:
            return Response({"statusCode": 400, "status": False, "message": str(e)}, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": list(reversed(duplicates)),
            "skipped_rows": list(reversed(skipped_rows))
        }, status=200)



class CourseDividedInListAPIView(APIView):
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['name', 'description', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = CourseDividedIn.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(Q(name__istartswith=search))

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = CourseDividedInSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

# -------------------- CREATE API --------------------
class CourseDividedInCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        name = request.data.get("name", "").strip()
        existing = CourseDividedIn.objects.filter(name__iexact=name, is_deleted=False).first()

        if existing:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "CourseDividedIn with this name already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = CourseDividedInSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "CourseDividedIn created successfully",
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

# -------------------- RETRIEVE API --------------------
class CourseDividedInRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = CourseDividedIn.objects.get(uuid=uuid, is_deleted=False)
        except CourseDividedIn.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "CourseDividedIn not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = CourseDividedInSerializer(obj)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "CourseDividedIn retrieved successfully",
            "data": serializer.data
        })

# -------------------- UPDATE API --------------------
class CourseDividedInUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = CourseDividedIn.objects.get(uuid=uuid, is_deleted=False)
        except CourseDividedIn.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "CourseDividedIn not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = CourseDividedInSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "CourseDividedIn updated successfully",
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

# -------------------- DELETE API --------------------
class CourseDividedInDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get('id', None)

        if uuid:
            try:
                obj = CourseDividedIn.objects.get(uuid=uuid)
                obj.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "CourseDividedIn permanently deleted.",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            except CourseDividedIn.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "CourseDividedIn not found.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        if ids == "all":
            objs = CourseDividedIn.objects.all()
            count = objs.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No CourseDividedIn found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
            objs.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} CourseDividedIn permanently deleted.",
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

        objs = CourseDividedIn.objects.filter(uuid__in=valid_uuids)
        count = objs.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching CourseDividedIn found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_404_NOT_FOUND)

        objs.delete()
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} CourseDividedIn(s) permanently deleted.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        })

# -------------------- EXPORT API --------------------
class CourseDividedInExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'name': 'Course Divided In',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'updated_at': 'Modified On',
        }

        if fields:
            field_list = [f.strip() for f in fields.split(',')]
        else:
            field_list = list(field_header_map.keys())

        queryset = CourseDividedIn.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'CourseDividedIn'

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
            file_name = 'coursedividedin.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'coursedividedin.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response

# -------------------- IMPORT API --------------------
class CourseDividedInImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get("file")
        sheet_name = request.data.get("sheet_name")

        if not file:
            return Response({"error": "No file uploaded"}, status=400)

        format_type = file.name.split(".")[-1].lower()
        duplicates = []
        skipped_rows = []
        required_headers = {"course divided in"}
        optional_headers = {"description"}

        try:
            data = []

            # -------- XLSX --------
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

            # -------- CSV --------
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

            # -------- Prepare for bulk_create --------
            bulk_list = []
            imported_count = 0

            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")
                name = str(row.get("course divided in")).strip() if row.get("course divided in") else None
                description = str(row.get("description")).strip() if row.get("description") else ""

                if not name:
                    skipped_rows.append({"Row": row_number,"Course Divided In": name or "","Description":description or "", "Reason": "Missing Name"})
                    continue

                existing = CourseDividedIn.objects.filter(name__iexact=name).first()
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({"Row": row_number, "Course Divided In": name,"Description":description or "", "Reason": "Already exists"})
                        continue
                    else:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    bulk_list.append(CourseDividedIn(name=name, description=description, is_deleted=False))
                    imported_count += 1

            # Bulk insert
            if bulk_list:
                CourseDividedIn.objects.bulk_create(bulk_list)

        except Exception as e:
            return Response({"statusCode": 400, "status": False, "message": str(e)}, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": list(reversed(duplicates)),
            "skipped_rows": list(reversed(skipped_rows))
        }, status=200)

class CourseStatusListAPIView(APIView):
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['name', 'description', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = CourseStatus.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(Q(name__istartswith=search))

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = CourseStatusSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

# -------------------- CREATE API --------------------
class CourseStatusCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        name = request.data.get("name", "").strip()
        existing = CourseStatus.objects.filter(name__iexact=name, is_deleted=False).first()

        if existing:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "CourseStatus with this name already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = CourseStatusSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "CourseStatus created successfully",
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

# -------------------- RETRIEVE API --------------------
class CourseStatusRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = CourseStatus.objects.get(uuid=uuid, is_deleted=False)
        except CourseStatus.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "CourseStatus not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = CourseStatusSerializer(obj)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "CourseStatus retrieved successfully",
            "data": serializer.data
        })

# -------------------- UPDATE API --------------------
class CourseStatusUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = CourseStatus.objects.get(uuid=uuid, is_deleted=False)
        except CourseStatus.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "CourseStatus not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = CourseStatusSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "CourseStatus updated successfully",
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

# -------------------- DELETE API --------------------
class CourseStatusDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get('id', None)

        if uuid:
            try:
                obj = CourseStatus.objects.get(uuid=uuid)
                obj.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "CourseStatus permanently deleted.",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            except CourseStatus.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "CourseStatus not found.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        if ids == "all":
            objs = CourseStatus.objects.all()
            count = objs.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No CourseStatus found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
            objs.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} CourseStatus permanently deleted.",
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

        objs = CourseStatus.objects.filter(uuid__in=valid_uuids)
        count = objs.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching CourseStatus found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_404_NOT_FOUND)

        objs.delete()
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} CourseStatus(s) permanently deleted.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        })

# -------------------- EXPORT API --------------------
class CourseStatusExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'name': 'Course Status',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'updated_at': 'Modified On',
        }

        if fields:
            field_list = [f.strip() for f in fields.split(',')]
        else:
            field_list = list(field_header_map.keys())

        queryset = CourseStatus.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'CourseStatus'

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
            file_name = 'coursestatus.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'coursestatus.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response

# -------------------- IMPORT API --------------------
class CourseStatusImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get("file")
        sheet_name = request.data.get("sheet_name")

        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split(".")[-1].lower()
        duplicates = []
        skipped_rows = []
        required_headers = {"course status"}
        optional_headers = {"description"}

        try:
            data = []

            # -------- XLSX --------
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

            # -------- CSV --------
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
            bulk_objects = []

            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")
                name = str(row.get("course status")).strip() if row.get("course status") else ""
                description = str(row.get("description")).strip() if row.get("description") else ""

                # Validate mandatory field
                if not name:
                    skipped_rows.append({
                        "Row": row_number,
                        "Course Status": name,
                        "Description": description,
                        "Reason": "Missing course status name"
                    })
                    continue

                # Check for existing CourseStatus
                existing = CourseStatus.objects.filter(name__iexact=name).first()
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({
                            "Row": row_number,
                            "Course Status": name,
                            "Description": description,
                            "Reason": "Already exists in database"
                        })
                        continue
                    else:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    bulk_objects.append(
                        CourseStatus(
                            name=name,
                            description=description,
                            is_deleted=False
                        )
                    )

            # Bulk create valid records
            if bulk_objects:
                CourseStatus.objects.bulk_create(bulk_objects)
                imported_count += len(bulk_objects)

        except Exception as e:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": str(e),
            }, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": list(reversed(duplicates)),
            "skipped_rows": list(reversed(skipped_rows)),
        }, status=200)

class IntakeNameListAPIView(APIView):
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['name', 'description', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = IntakeName.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(Q(name__istartswith=search))

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = IntakeNameSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

# -------------------- CREATE API --------------------
class IntakeNameCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        name = request.data.get("name", "").strip()
        existing = IntakeName.objects.filter(name__iexact=name, is_deleted=False).first()

        if existing:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "IntakeName with this name already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = IntakeNameSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "IntakeName created successfully",
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

# -------------------- RETRIEVE API --------------------
class IntakeNameRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = IntakeName.objects.get(uuid=uuid, is_deleted=False)
        except IntakeName.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "IntakeName not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = IntakeNameSerializer(obj)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "IntakeName retrieved successfully",
            "data": serializer.data
        })

# -------------------- UPDATE API --------------------
class IntakeNameUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = IntakeName.objects.get(uuid=uuid, is_deleted=False)
        except IntakeName.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "IntakeName not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = IntakeNameSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "IntakeName updated successfully",
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

# -------------------- DELETE API --------------------
class IntakeNameDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get('id', None)

        if uuid:
            try:
                obj = IntakeName.objects.get(uuid=uuid)
                obj.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "IntakeName permanently deleted.",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            except IntakeName.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "IntakeName not found.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        if ids == "all":
            objs = IntakeName.objects.all()
            count = objs.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No IntakeName found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
            objs.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} IntakeName permanently deleted.",
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

        objs = IntakeName.objects.filter(uuid__in=valid_uuids)
        count = objs.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching IntakeName found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_404_NOT_FOUND)

        objs.delete()
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} IntakeName(s) permanently deleted.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        })

# -------------------- EXPORT API --------------------
class IntakeNameExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'name': 'Intake Name',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'updated_at': 'Modified On',
        }

        if fields:
            field_list = [f.strip() for f in fields.split(',')]
        else:
            field_list = list(field_header_map.keys())

        queryset = IntakeName.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'IntakeName'

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
            file_name = 'intakename.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'intakename.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response

# -------------------- IMPORT API --------------------
class IntakeNameImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get("file")
        sheet_name = request.data.get("sheet_name")

        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split(".")[-1].lower()
        duplicates = []
        skipped_rows = []
        required_headers = {"intake name"}
        optional_headers = {"description"}

        try:
            data = []

            # -------- XLSX --------
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

            # -------- CSV --------
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
            bulk_objects = []

            # -------- Validation & Prepare bulk_objects --------
            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")
                name = str(row.get("intake name")).strip() if row.get("intake name") else ""
                description = str(row.get("description")).strip() if row.get("description") else ""

                if not name:
                    skipped_rows.append({
                        "Row": row_number,
                        "Intake Name": name or "",
                        "Description": description or "",
                        "Reason": "Missing Intake Name"
                    })
                    continue

                existing = IntakeName.objects.filter(name__iexact=name).first()
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({
                            "Row": row_number,
                            "Intake Name": name,
                            "Description": description or "",
                            "Reason": "Already exists"
                        })
                        continue
                    else:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    bulk_objects.append(IntakeName(
                        name=name,
                        description=description,
                        is_deleted=False
                    ))

            # -------- Bulk create --------
            if bulk_objects:
                IntakeName.objects.bulk_create(bulk_objects)
                imported_count += len(bulk_objects)

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
class CourseStatusIntakeListAPIView(APIView):
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['name', 'description', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = CourseStatusIntake.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(Q(name__istartswith=search))

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = CourseStatusIntakeSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

# -------------------- CREATE API --------------------
class CourseStatusIntakeCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        name = request.data.get("name", "").strip()
        existing = CourseStatusIntake.objects.filter(name__iexact=name, is_deleted=False).first()

        if existing:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "CourseStatusIntake with this name already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = CourseStatusIntakeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "CourseStatusIntake created successfully",
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

# -------------------- RETRIEVE API --------------------
class CourseStatusIntakeRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = CourseStatusIntake.objects.get(uuid=uuid, is_deleted=False)
        except CourseStatusIntake.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "CourseStatusIntake not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = CourseStatusIntakeSerializer(obj)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "CourseStatusIntake retrieved successfully",
            "data": serializer.data
        })

# -------------------- UPDATE API --------------------
class CourseStatusIntakeUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = CourseStatusIntake.objects.get(uuid=uuid, is_deleted=False)
        except CourseStatusIntake.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "CourseStatusIntake not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = CourseStatusIntakeSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "CourseStatusIntake updated successfully",
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

# -------------------- DELETE API --------------------
class CourseStatusIntakeDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get('id', None)

        if uuid:
            try:
                obj = CourseStatusIntake.objects.get(uuid=uuid)
                obj.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "CourseStatusIntake permanently deleted.",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            except CourseStatusIntake.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "CourseStatusIntake not found.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        if ids == "all":
            objs = CourseStatusIntake.objects.all()
            count = objs.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No CourseStatusIntake found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
            objs.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} CourseStatusIntake permanently deleted.",
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

        objs = CourseStatusIntake.objects.filter(uuid__in=valid_uuids)
        count = objs.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching CourseStatusIntake found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_404_NOT_FOUND)

        objs.delete()
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} CourseStatusIntake(s) permanently deleted.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        })

# -------------------- EXPORT API --------------------
class CourseStatusIntakeExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'name': 'Course Status Intake',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'updated_at': 'Modified On',
        }

        if fields:
            field_list = [f.strip() for f in fields.split(',')]
        else:
            field_list = list(field_header_map.keys())

        queryset = CourseStatusIntake.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'CourseStatusIntake'

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
            file_name = 'coursestatusintake.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'coursestatusintake.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response

# -------------------- IMPORT API --------------------
class CourseStatusIntakeImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get("file")
        sheet_name = request.data.get("sheet_name")

        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split(".")[-1].lower()
        duplicates = []
        skipped_rows = []
        required_headers = {"course status intake"}
        optional_headers = {"description"}

        try:
            data = []

            # -------- XLSX --------
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

            # -------- CSV --------
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
            bulk_objects = []

            # -------- Validation & Prepare bulk_objects --------
            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")
                name = str(row.get("course status intake")).strip() if row.get("course status intake") else ""
                description = str(row.get("description")).strip() if row.get("description") else ""

                if not name:
                    skipped_rows.append({
                        "Row": row_number,
                        "Course Status Intake": name or "",
                        "Description": description or "",
                        "Reason": "Missing Name"
                    })
                    continue

                existing = CourseStatusIntake.objects.filter(name__iexact=name).first()
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({
                            "Row": row_number,
                            "Course Status Intake": name,
                            "Description": description or "",
                            "Reason": "Already exists"
                        })
                        continue
                    else:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    bulk_objects.append(CourseStatusIntake(
                        name=name,
                        description=description,
                        is_deleted=False
                    ))

            # -------- Bulk create --------
            if bulk_objects:
                CourseStatusIntake.objects.bulk_create(bulk_objects)
                imported_count += len(bulk_objects)

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

class ScholorshipBasedOnListAPIView(APIView):
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['name', 'description', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = ScholorshipBasedOn.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(Q(name__istartswith=search))

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = ScholorshipBasedOnSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

# -------------------- CREATE API --------------------
class ScholorshipBasedOnCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        name = request.data.get("name", "").strip()
        existing = ScholorshipBasedOn.objects.filter(name__iexact=name, is_deleted=False).first()

        if existing:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "ScholorshipBasedOn with this name already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = ScholorshipBasedOnSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "ScholorshipBasedOn created successfully",
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

# -------------------- RETRIEVE API --------------------
class ScholorshipBasedOnRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = ScholorshipBasedOn.objects.get(uuid=uuid, is_deleted=False)
        except ScholorshipBasedOn.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "ScholorshipBasedOn not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = ScholorshipBasedOnSerializer(obj)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "ScholorshipBasedOn retrieved successfully",
            "data": serializer.data
        })

# -------------------- UPDATE API --------------------
class ScholorshipBasedOnUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = ScholorshipBasedOn.objects.get(uuid=uuid, is_deleted=False)
        except ScholorshipBasedOn.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "ScholorshipBasedOn not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = ScholorshipBasedOnSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "ScholorshipBasedOn updated successfully",
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

# -------------------- DELETE API --------------------
class ScholorshipBasedOnDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get('id', None)

        if uuid:
            try:
                obj = ScholorshipBasedOn.objects.get(uuid=uuid)
                obj.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "ScholorshipBasedOn permanently deleted.",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            except ScholorshipBasedOn.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "ScholorshipBasedOn not found.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        if ids == "all":
            objs = ScholorshipBasedOn.objects.all()
            count = objs.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No ScholorshipBasedOn found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
            objs.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} ScholorshipBasedOn permanently deleted.",
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

        objs = ScholorshipBasedOn.objects.filter(uuid__in=valid_uuids)
        count = objs.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching ScholorshipBasedOn found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_404_NOT_FOUND)

        objs.delete()
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} ScholorshipBasedOn(s) permanently deleted.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        })

# -------------------- EXPORT API --------------------
class ScholorshipBasedOnExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'name': 'Scholorship Based On',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'updated_at': 'Modified On',
        }

        if fields:
            field_list = [f.strip() for f in fields.split(',')]
        else:
            field_list = list(field_header_map.keys())

        queryset = ScholorshipBasedOn.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'ScholorshipBasedOn'

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
            file_name = 'scholorshipbasedon.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'scholorshipbasedon.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response

# -------------------- IMPORT API --------------------
class ScholorshipBasedOnImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get("file")
        sheet_name = request.data.get("sheet_name")

        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split(".")[-1].lower()
        duplicates = []
        skipped_rows = []
        required_headers = {"scholorship based on"}
        optional_headers = {"description"}

        try:
            data = []

            # -------- XLSX --------
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

            # -------- CSV --------
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
            bulk_objects = []

            # -------- Validation & prepare bulk_objects --------
            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")
                name = str(row.get("scholorship based on")).strip() if row.get("scholorship based on") else ""
                description = str(row.get("description")).strip() if row.get("description") else ""

                if not name:
                    skipped_rows.append({
                        "Row": row_number,
                        "Scholorship Based On": name or "",
                        "Description": description or "",
                        "Reason": "Missing Name"
                    })
                    continue

                existing = ScholorshipBasedOn.objects.filter(name__iexact=name).first()
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({
                            "Row": row_number,
                            "Scholorship Based On": name,
                            "Description": description or "",
                            "Reason": "Already exists"
                        })
                        continue
                    else:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    bulk_objects.append(ScholorshipBasedOn(
                        name=name,
                        description=description,
                        is_deleted=False
                    ))

            # -------- Bulk create --------
            if bulk_objects:
                ScholorshipBasedOn.objects.bulk_create(bulk_objects)
                imported_count += len(bulk_objects)

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

    


class CourseLevelListAPIView(APIView):
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['name', 'description', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = CourseLevel.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(Q(name__istartswith=search))

        queryset = queryset.order_by(sort_by)

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = CourseLevelSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)

# -------------------------
# Create API
# -------------------------
class CourseLevelCreateAPIView(APIView):
    def post(self, request):
        serializer = CourseLevelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Course level created successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        errors = serializer.errors
        messages = [msg for msgs in errors.values() for msg in msgs]
        return Response({
            "statusCode": 400,
            "status": False,
            "message": " ".join(messages),
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)

# -------------------------
# Detail API
# -------------------------
class CourseLevelRetrieveAPIView(APIView):
    def get(self, request, uuid):
        try:
            course_level = CourseLevel.objects.get(uuid=uuid, is_deleted=False)
        except CourseLevel.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Course level not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = CourseLevelSerializer(course_level)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Course level retrieved successfully",
            "data": serializer.data
        })

# -------------------------
# Update API
# -------------------------
class CourseLevelUpdateAPIView(APIView):
    def put(self, request, uuid):
        try:
            course_level = CourseLevel.objects.get(uuid=uuid, is_deleted=False)
        except CourseLevel.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Course level not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = CourseLevelSerializer(course_level, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Course level updated successfully",
                "data": serializer.data
            })

        errors = serializer.errors
        messages = [msg for msgs in errors.values() for msg in msgs]
        return Response({
            "statusCode": 400,
            "status": False,
            "message": " ".join(messages),
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)

# -------------------------
# Delete API
# -------------------------
class CourseLevelDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get('id', [])

        # Single delete via URL
        if uuid:
            try:
                course_level = CourseLevel.objects.get(uuid=uuid, is_deleted=False)
                course_level.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "Course level deleted successfully",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            except CourseLevel.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Course level not found",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        if ids == "all":
            course_levels = CourseLevel.objects.filter(is_deleted=False)
            count = course_levels.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No course levels found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
            course_levels.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} course level(s) permanently deleted.",
                "data": None
            }, status=status.HTTP_200_OK)

        # Multiple delete
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

        course_levels = CourseLevel.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = course_levels.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching course levels found.",
                "data": {"invalid_uuids": invalid_uuids}
            }, status=status.HTTP_404_NOT_FOUND)

        course_levels.delete()
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} course level(s) deleted successfully.",
            "data": {"invalid_uuids": invalid_uuids}
        }, status=status.HTTP_200_OK)

# -------------------------
# Export API
# -------------------------
class CourseLevelExportAPIView(APIView):
    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'courselevelcode': 'Course Level Code',
            'name': 'Course Level',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'created_at': 'Created On',
            'updated_at': 'Modified On',
        }

        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())
        queryset = CourseLevel.objects.all()
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'CourseLevel'

        for obj in queryset:
            row = []
            for field in field_list:
                if field == 'courselevelcode':
                    value = obj.courselevelcode.name if obj.courselevelcode else ''
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
            file_name = 'course_levels.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'course_levels.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response

# -------------------------
# Import API
# -------------------------
class CourseLevelImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get("file")
        sheet_name = request.data.get("sheet_name")

        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split(".")[-1].lower()
        duplicates = []
        skipped_rows = []
        required_headers = {"course level"}
        optional_headers = {"description", "course level code"}

        try:
            data = []

            # -------- XLSX --------
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

            else:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "error": "Unsupported file format. Use .xlsx",
                }, status=400)

            imported_count = 0
            bulk_objects = []

            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")
                name = str(row.get("course level")).strip() if row.get("course level") else ""
                description = str(row.get("description")).strip() if row.get("description") else ""
                courselevelcode_name = str(row.get("course level code")).strip() if row.get("course level code") else None

                # Validate mandatory field
                if not name:
                    skipped_rows.append({
                        "Row": row_number,
                        "Course Level": name,
                        "Course Level Code": courselevelcode_name or "",
                        "Description": description,
                        "Reason": "Missing course level name"
                    })
                    continue

                # Validate CourseLevelCode
                courselevelcode = None
                if courselevelcode_name:
                    courselevelcode = CourseLevelCode.objects.filter(name__iexact=courselevelcode_name).first()
                    if not courselevelcode:
                        skipped_rows.append({
                            "Row": row_number,
                            "Course Level": name,
                            "Course Level Code": courselevelcode_name,
                            "Description": description,
                            "Reason": f'CourseLevelCode "{courselevelcode_name}" not found'
                        })
                        continue

                # Check for existing CourseLevel
                existing = CourseLevel.objects.filter(name__iexact=name).first()
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({
                            "Row": row_number,
                            "Course Level": name,
                            "Course Level Code": courselevelcode_name or "",
                            "Description": description,
                            "Reason": "Already exists in database"
                        })
                        continue
                    else:
                        existing.description = description
                        existing.courselevelcode = courselevelcode
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    # Add to bulk list
                    bulk_objects.append(
                        CourseLevel(
                            name=name,
                            description=description,
                            courselevelcode=courselevelcode,
                            is_deleted=False
                        )
                    )

            # Bulk create valid records
            if bulk_objects:
                CourseLevel.objects.bulk_create(bulk_objects)
                imported_count += len(bulk_objects)

        except Exception as e:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": str(e),
            }, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": list(reversed(duplicates)),
            "skipped_rows": list(reversed(skipped_rows)),
        }, status=200)



class CourseDurationListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')
        allowed_sort_fields = ['courselevel__name', 'valid_duration_value', 'valid_duration_unit', 'created_at']

        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = CourseDuration.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(
                Q(courselevel__name__istartswith=search) |
                Q(description__istartswith=search)
            )

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = CourseDurationSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


# -------------------- Create -------------------- #
class CourseDurationCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        courselevel_uuid = request.data.get('courselevel_id')
        valid_duration_value = request.data.get('valid_duration_value')
        valid_duration_unit = request.data.get('valid_duration_unit')

        # Validate mandatory fields
        if not courselevel_uuid or valid_duration_value is None or not valid_duration_unit:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Mandatory fields missing: courselevel_id, valid_duration_value, valid_duration_unit"
            }, status=400)

        # Validate courselevel_uuid format
        try:
            courselevel_uuid = uuid.UUID(courselevel_uuid)  # Check if it's a valid UUID
        except ValueError:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Invalid courselevel_id format."
            }, status=400)

        # Validate numeric value
        try:
            valid_duration_value = int(valid_duration_value)
        except ValueError:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "valid_duration_value must be numeric."
            }, status=400)

        # Validate unit
        if valid_duration_unit not in dict(CourseDuration.VALID_UNIT_CHOICES):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": f"valid_duration_unit must be one of {list(dict(CourseDuration.VALID_UNIT_CHOICES).keys())}"
            }, status=400)

        # Validate course level
        try:
            courselevel_obj = CourseLevel.objects.get(uuid=courselevel_uuid)
        except CourseLevelCode.DoesNotExist:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Invalid courselevel_id. No matching CourseLevelCode found."
            }, status=400)

        data = request.data.copy()
        data['courselevel_id'] = courselevel_obj.uuid
        serializer = CourseDurationSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Course duration created successfully",
                "data": serializer.data
            })

        errors = " ".join([msg for msgs in serializer.errors.values() for msg in msgs])
        return Response({
            "statusCode": 400,
            "status": False,
            "message": errors
        }, status=400)

# -------------------- Retrieve -------------------- #
class CourseDurationRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = CourseDuration.objects.get(uuid=uuid, is_deleted=False)
        except CourseDuration.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "Not found", "data": None}, status=404)
        serializer = CourseDurationSerializer(obj)
        return Response({"statusCode": 200, "status": True, "message": "Retrieved successfully", "data": serializer.data})


# -------------------- Update -------------------- #
class CourseDurationUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = CourseDuration.objects.get(uuid=uuid, is_deleted=False)
        except CourseDuration.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "Not found", "data": None}, status=404)

        valid_duration_value = request.data.get('valid_duration_value')
        valid_duration_unit = request.data.get('valid_duration_unit')

        if valid_duration_value is not None:
            try:
                request.data['valid_duration_value'] = int(valid_duration_value)
            except ValueError:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "valid_duration_value must be numeric."
                }, status=400)

        if valid_duration_unit and valid_duration_unit not in dict(CourseDuration.VALID_UNIT_CHOICES):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": f"valid_duration_unit must be one of {list(dict(CourseDuration.VALID_UNIT_CHOICES).keys())}"
            }, status=400)

        serializer = CourseDurationSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"statusCode": 200, "status": True, "message": "Updated successfully", "data": serializer.data})

        errors = " ".join([msg for msgs in serializer.errors.values() for msg in msgs])
        return Response({"statusCode": 400, "status": False, "message": errors}, status=400)


# -------------------- Delete -------------------- #
class CourseDurationDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get('id', None)

        if uuid:
            try:
                obj = CourseDuration.objects.get(uuid=uuid, is_deleted=False)
                obj.delete()
                return Response({"statusCode": 204, "status": True, "message": "CourseDuration permanently deleted.", "data": None}, status=status.HTTP_204_NO_CONTENT)
            except CourseDuration.DoesNotExist:
                return Response({"statusCode": 404, "status": False, "message": "CourseDuration not found.", "data": None}, status=status.HTTP_404_NOT_FOUND)

        if ids == "all":
            objs = CourseDuration.objects.filter(is_deleted=False)
            count = objs.count()
            if count == 0:
                return Response({"statusCode": 404, "status": False, "message": "No records found to delete.", "data": None}, status=status.HTTP_404_NOT_FOUND)
            objs.delete()
            return Response({"statusCode": 200, "status": True, "message": f"All {count} record(s) permanently deleted.", "data": None}, status=status.HTTP_200_OK)

        if not ids or not isinstance(ids, list):
            return Response({"statusCode": 400, "status": False, "message": "Please provide a list of UUIDs in 'id' field or 'all'.", "data": None}, status=status.HTTP_400_BAD_REQUEST)

        valid_uuids = []
        invalid_uuids = []
        for u in ids:
            try:
                valid_uuids.append(UUID(u))
            except ValueError:
                invalid_uuids.append(u)

        if not valid_uuids:
            return Response({"statusCode": 400, "status": False, "message": "No valid UUIDs provided.", "data": {"invalid_uuids": invalid_uuids}}, status=status.HTTP_400_BAD_REQUEST)

        objs = CourseDuration.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = objs.count()

        if count == 0:
            return Response({"statusCode": 404, "status": False, "message": "No matching records found.", "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None}, status=status.HTTP_404_NOT_FOUND)

        objs.delete()
        return Response({"statusCode": 200, "status": True, "message": f"{count} record(s) permanently deleted.", "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None}, status=status.HTTP_200_OK)



class CourseDurationExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'courselevel': 'Course Level',
            'valid_duration_value': 'Course Duration Value',
            'valid_duration_unit': 'Course Duration Unit',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'created_at': 'Created On',
            'updated_at': 'Modified On',
        }

        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())
        queryset = CourseDuration.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'Course Durations'

        for obj in queryset:
            row = []
            for field in field_list:
                value = getattr(obj, field, '')
                if field == 'courselevel' and value:
                    value = value.name  # If it's a foreign key, use the related field's name
                elif field in ['created_at', 'updated_at'] and value:
                    value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
                elif field == 'valid_duration_value' and value:
                    value = str(value)  # Ensure it's shown as a string (numeric value)
                
                row.append(value if value is not None else '')
            dataset.append(row)

        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'course_durations.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'course_durations.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response




class CourseDurationImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=400)

        format_type = file.name.split('.')[-1].lower()
        duplicates = []
        skipped_rows = []
        required_headers = {'course level', 'course duration value', 'course duration unit'}
        optional_headers = {'description'}

        try:
            data = []

            # -------- XLSX --------
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

            # -------- CSV --------
            elif format_type == 'csv':
                dataset = Dataset()
                dataset.load(file.read().decode('utf-8'), format='csv')
                for idx, row in enumerate(dataset.dict, start=2):
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    row_lower['_row_number'] = idx
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({'error': f'Missing required headers. Required: {required_headers}'}, status=400)
                    data.append(row_lower)
            else:
                return Response({'error': 'Unsupported file format. Use .xlsx or .csv'}, status=400)

            imported_count = 0
            for row in reversed(data):
                row_number = row.get('_row_number', 'Unknown')
                courselevel_name = str(row.get('course level')).strip() if row.get('course level') else ""
                duration_value = row.get('course duration value')
                duration_unit = str(row.get('course duration unit')).strip() if row.get('course duration unit') else ""
                description = str(row.get('description')).strip() if row.get('description') else ""

                # Validate mandatory fields
                if not courselevel_name or duration_value is None or not duration_unit:
                    skipped_rows.append({
                        'row': row_number,
                        "Course Level": courselevel_name,
                        "Course Duration Value": duration_value,
                        "Course Duration Unit": duration_unit,
                        "Description": description,
                        'Reason': 'Mandatory fields missing'
                    })
                    continue

                # Validate course level
                try:
                    courselevel_obj = CourseLevel.objects.get(name__iexact=courselevel_name)
                except CourseLevel.DoesNotExist:
                    skipped_rows.append({
                        'row': row_number,
                        "Course Level": courselevel_name,
                        "Course Duration Value": duration_value,
                        "Course Duration Unit": duration_unit,
                        "Description": description,
                        'Reason': 'Course Level not found'
                    })
                    continue

                # Validate numeric value
                try:
                    duration_value = int(duration_value)
                except ValueError:
                    skipped_rows.append({
                        'row': row_number,
                        "Course Level": courselevel_name,
                        "Course Duration Value": duration_value,
                        "Course Duration Unit": duration_unit,
                        "Description": description,
                        'Reason': 'Course Duration Value must be numeric'
                    })
                    continue

                # Validate duration unit
                if duration_unit not in dict(CourseDuration.VALID_UNIT_CHOICES):
                    skipped_rows.append({
                        'row': row_number,
                        "Course Level": courselevel_name,
                        "Course Duration Value": duration_value,
                        "Course Duration Unit": duration_unit,
                        "Description": description,
                        'Reason': 'Invalid Course Duration Unit'
                    })
                    continue

                # Check for existing record
                existing = CourseDuration.objects.filter(
                    courselevel=courselevel_obj,
                    valid_duration_value=duration_value,
                    valid_duration_unit=duration_unit
                ).first()

                if existing:
                    if not existing.is_deleted:
                        duplicates.append(f"{courselevel_name} - {duration_value} {duration_unit}")
                        continue
                    else:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    CourseDuration.objects.create(
                        courselevel=courselevel_obj,
                        valid_duration_value=duration_value,
                        valid_duration_unit=duration_unit,
                        description=description,
                        is_deleted=False
                    )
                    imported_count += 1

        except Exception as e:
            return Response({'error': str(e)}, status=400)

        return Response({
            'statusCode': 200,
            'status': True,
            'message': f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            'imported_count': imported_count,
            'duplicates': list(reversed(duplicates)),
            'skipped_rows': list(reversed(skipped_rows))
        }, status=200)






