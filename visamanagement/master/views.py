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
from django.db import IntegrityError
import csv
import io
import pytz
from django.utils import timezone
import unicodedata

india_tz = pytz.timezone('Asia/Kolkata')

class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_superuser)
    

class MasterTokenLoginAPIView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = AdminUserLoginSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            # Safe extraction of error message
            if isinstance(e.detail, dict):
                message = next(iter(e.detail.values()))[0]
            elif isinstance(e.detail, list):
                message = e.detail[0]
            else:
                message = str(e.detail)

            return Response({
                "status": False,
                "statusCode": status.HTTP_401_UNAUTHORIZED,
                "message": message
            }, status=status.HTTP_401_UNAUTHORIZED)

        user = serializer.validated_data['user']

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        refresh["email"] = user.email
        refresh["role"] = user.role.name if getattr(user, "role", None) else None
        refresh["user_type"] = "admin"
        refresh["admin_id"] = user.id

        return Response({
            "status": True,
            "statusCode": status.HTTP_200_OK,
            "message": "Login successful",
            "data": {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "name": getattr(user, "name", ""),
                    "email": user.email,
                    "role": user.role.name if getattr(user, "role", None) else None,
                    "user_type": "admin",
                    "is_master": user.is_superuser
                }
            }
        }, status=status.HTTP_200_OK)




class AdminLogoutView(APIView):
    authentication_classes = [JWTAuthentication] 
    permission_classes = [IsAuthenticated]  

    def post(self, request):
        ip = request.META.get("REMOTE_ADDR")
        user_agent = request.META.get("HTTP_USER_AGENT", "unknown")
        user = request.user

        try:
            refresh_token = request.data.get("refresh_token")  

           
            if not refresh_token:
                return Response(
                    {"statusCode": 400, "status": False, "message": "Refresh token is required"},
                    status=status.HTTP_200_OK
                )

            token = RefreshToken(refresh_token)
            token.blacklist()  

            return Response(
                    {"statusCode": 200, "status": True, "message": "Successfully logged out"},
                    status=status.HTTP_200_OK
                )

        except TokenError as e:
            return Response(
                {"statusCode": 400, "status": False, "message": "Invalid or expired refresh token"},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"statusCode": 500, "status": False, "message": "An unexpected error occurred", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



class GenderListAPIView(APIView):
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'asc')

        allowed_sort_fields = ['name', 'description', 'created_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = Gender.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )

        queryset = queryset.order_by(sort_by)

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = GenderSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)


class GenderCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        name = request.data.get("name", "").strip()
        if not name:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Name is required.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check duplicate
        if Gender.objects.filter(name__iexact=name, is_deleted=False).exists():
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Gender with this name already exists.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        data = request.data.copy()
        data['name'] = name

        serializer = GenderSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Gender created successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        messages = []
        for field, msgs in serializer.errors.items():
            messages.extend(msgs)
        return Response({
            "statusCode": 400,
            "status": False,
            "message": " ".join(messages),
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)


class GenderDetailAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            gender = Gender.objects.get(uuid=uuid, is_deleted=False)
        except Gender.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Gender not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = GenderSerializer(gender)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Gender retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class GenderUpdateAPIView(APIView):
    def put(self, request, uuid):
        try:
            gender = Gender.objects.get(uuid=uuid, is_deleted=False)
        except Gender.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Gender not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = GenderSerializer(gender, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Gender updated successfully",
                "data": serializer.data
            })


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


class GenderDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        ids = request.data.get('id', None)

        if not ids:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide 'id' field (UUID list or 'all').",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        # If client requests all records to be deleted
        if ids == "all":
            genders = Gender.objects.filter(is_deleted=False)
            count = genders.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No genders found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
            genders.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} gender(s) deleted successfully.",
                "data": None
            }, status=status.HTTP_200_OK)

        # Otherwise, treat it as a list of UUIDs
        if not isinstance(ids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide a list of UUIDs in 'id' field or 'all'.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate UUIDs
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

        genders = Gender.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = genders.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching genders found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_404_NOT_FOUND)

        genders.delete()

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} gender(s) deleted successfully.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        }, status=status.HTTP_200_OK)




class GenderExportAPIView(APIView):
    """
    Export Gender data to CSV or XLSX.
    """
    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')  # comma-separated
        uuids_param = request.GET.get('uuids', '')  # comma-separated UUIDs

        uuids = [u.strip() for u in uuids_param.split(',') if u]

        # --- Field to header mapping ---
        field_header_map = {
            'uuid': 'UUID',
            'name': 'Gender',
            'description': 'Description',
            'is_active': 'Active',
            'is_deleted': 'Deleted',
            'updated_at': 'Modified On',
        }

        # --- Determine export fields ---
        if fields:
            field_list = [f.strip() for f in fields.split(',')]
        else:
            field_list = list(field_header_map.keys())

        # --- Fetch queryset ---
        queryset = Gender.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        # --- Prepare dataset ---
        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title="Gender"

        for gender in queryset:
            row = []
            for field in field_list:
                value = getattr(gender, field, '')
                if field in ['created_at', 'updated_at'] and value:
                    value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
                elif isinstance(value, bool):
                    value = int(value)
                row.append(value if value is not None else '')
            dataset.append(row)

        # --- Export file ---
        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'genders.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'genders.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


class GenderImportAPIView(APIView):
    """
    Import Gender data from CSV or XLSX.
    """
    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicate_names = []

        required_headers = {'gender'}       # Required header name
        optional_headers = {'description', 'is_active'}  # Optional

        try:
            data = []

            # --- XLSX ---
            if format_type == 'xlsx':
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({
                        'error': 'Please provide sheet_name',
                        'available_sheets': available_sheets
                    }, status=status.HTTP_400_BAD_REQUEST)

                if sheet_name not in available_sheets:
                    return Response({
                        'error': f'Sheet "{sheet_name}" not found',
                        'available_sheets': available_sheets
                    }, status=status.HTTP_400_BAD_REQUEST)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'Sheet "{sheet_name}" is empty.'
                    }, status=status.HTTP_400_BAD_REQUEST)

                headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]

                if not required_headers.issubset(set(headers)):
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'Missing required headers. Required: {required_headers}, Found: {set(headers)}'
                    }, status=status.HTTP_400_BAD_REQUEST)

                for row in ws.iter_rows(min_row=2, values_only=True):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    data.append(row_dict)

                if not data:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'Sheet "{sheet_name}" has no data rows.'
                    }, status=status.HTTP_400_BAD_REQUEST)

            # --- CSV ---
            elif format_type == 'csv':
                decoded_file = file.read().decode('utf-8')
                dataset = Dataset()
                dataset.load(decoded_file, format='csv')

                for row in dataset.dict:
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({
                            "statusCode": 400,
                            "status": False,
                            "message": (
                                f'Missing required headers. Required: {", ".join(required_headers)}. '
                                f'Found: {", ".join(row_lower.keys())}'
                            )
                        }, status=status.HTTP_400_BAD_REQUEST)
                    data.append(row_lower)

                if not data:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": "CSV file is empty."
                    }, status=status.HTTP_400_BAD_REQUEST)

            else:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": 'Unsupported file format. Use .xlsx or .csv'
                }, status=status.HTTP_400_BAD_REQUEST)

            # --- Process import data ---
            imported_count = 0
            for row in  reversed(data):
                name = str(row.get('gender')).strip() if row.get('gender') else None
                description = str(row.get('description')).strip() if row.get('description') else ''
                is_active = row.get('is_active')
                is_active = bool(int(is_active)) if str(is_active).isdigit() else True

                if not name:
                    continue

                existing = Gender.objects.filter(name__iexact=name).first()

                if existing:
                    if not existing.is_deleted:
                        duplicate_names.append(name)
                        continue
                    else:
                        existing.description = description
                        existing.is_active = is_active
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    Gender.objects.create(
                        name=name,
                        description=description,
                        is_active=is_active,
                        is_deleted=False
                    )
                    imported_count += 1

        except Exception as e:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": list(set(duplicate_names)),
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count
        }, status=status.HTTP_200_OK)





#-------------------------------maritalstatus--------------------------------
class MaritalstatusListAPIView(APIView):
    def get(self, request):
        try:
            search = request.GET.get('search', '').strip()
            sort_by = request.GET.get('sortBy', 'created_at')
            sort_order = request.GET.get('sortOrder', 'asc')

            # Allowed fields to sort
            allowed_sort_fields = ['text', 'description', 'created_at']
            if sort_by not in allowed_sort_fields:
                sort_by = 'created_at'
            if sort_order == 'desc':
                sort_by = f'-{sort_by}'

            # Filter out deleted entries
            queryset = Maritalstatus.objects.filter(is_deleted=False)

            # Apply search filter
            if search:
                queryset = queryset.filter(
                    Q(name__icontains=search) |
                    Q(description__icontains=search)
                )

            # Apply ordering
            queryset = queryset.order_by(sort_by)

            # Pagination
            paginator = CustomPagination()
            result_page = paginator.paginate_queryset(queryset, request)
            serializer = MaritalstatusSerializer(result_page, many=True)

            return paginator.get_paginated_response(serializer.data)

        except Exception as e:
            return Response({
                "statusCode": 500,
                "status": False,
                "message": str(e),
                "data": None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MaritalstatusCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        name = request.data.get("name", "").strip()
        if not name:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Name is required.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check for duplicate (case-insensitive)
        if Maritalstatus.objects.filter(name__iexact=name, is_deleted=False).exists():
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Marital status with this name already exists.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        # Cleaned data for serializer
        data = request.data.copy()
        data['name'] = name

        serializer = MaritalstatusSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Marital status created successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        # Collect validation errors
        messages = []
        for field, msgs in serializer.errors.items():
            messages.extend(msgs)
        return Response({
            "statusCode": 400,
            "status": False,
            "message": " ".join(messages),
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)


class MaritalstatusDetailAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            marital = Maritalstatus.objects.get(uuid=uuid, is_deleted=False)
        except Maritalstatus.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Maritalstatus not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = MaritalstatusSerializer(marital)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Maritalstatus retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    

class MaritalstatusUpdateAPIView(APIView):
    def put(self, request, uuid):
        try:
            marital = Maritalstatus.objects.get(uuid=uuid, is_deleted=False)
        except Maritalstatus.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Maritalstatus not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = MaritalstatusSerializer(marital, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Maritalstatus updated successfully",
                "data": serializer.data
            })


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

class MaritalstatusDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        ids = request.data.get('id', None)

        if not ids:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide 'id' field (UUID list or 'all').",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        # Delete all records
        if ids == "all":
            maritalstatuses = Maritalstatus.objects.filter(is_deleted=False)
            count = maritalstatuses.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No marital statuses found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

            maritalstatuses.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} marital status(es) deleted successfully.",
                "data": None
            }, status=status.HTTP_200_OK)

        # Otherwise, treat as list of UUIDs
        if not isinstance(ids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide a list of UUIDs in 'id' field or 'all'.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate UUIDs
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

        maritalstatuses = Maritalstatus.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = maritalstatuses.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching marital statuses found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_404_NOT_FOUND)

        maritalstatuses.delete()

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} marital status(es) deleted successfully.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        }, status=status.HTTP_200_OK)

class MaritalstatusExportAPIView(APIView):
    """
    Export Maritalstatus data to CSV or XLSX.
    """
    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')  # comma-separated
        uuids_param = request.GET.get('uuids', '')  # comma-separated UUIDs

        uuids = [u.strip() for u in uuids_param.split(',') if u]

        # Field to header mapping
        field_header_map = {
            'uuid': 'UUID',
            'name': 'Marital Status',
            'description': 'Description',
            'is_active': 'Active',
            'is_deleted': 'Deleted',
            'updated_at': 'Modified On',
        }

        # Determine export fields
        if fields:
            field_list = [f.strip() for f in fields.split(',')]
        else:
            field_list = list(field_header_map.keys())

        # Fetch queryset
        queryset = Maritalstatus.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')


        # Prepare dataset
        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title="MaritalStatus"

        for item in queryset:
            row = []
            for field in field_list:
                value = getattr(item, field, '')
                if field in ['created_at', 'updated_at'] and value:
                    value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
                elif isinstance(value, bool):
                    value = int(value)
                row.append(value if value is not None else '')
            dataset.append(row)

        # Export file
        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'maritalstatus.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'maritalstatus.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response

class MaritalstatusImportAPIView(APIView):
    """
    Import Maritalstatus data from CSV or XLSX.
    """
    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicate_names = []

        required_headers = {'marital status'}       # Required header name
        optional_headers = {'description', 'is_active'}  # Optional headers

        try:
            data = []

            # XLSX
            if format_type == 'xlsx':
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({
                        'error': 'Please provide sheet_name',
                        'available_sheets': available_sheets
                    }, status=status.HTTP_400_BAD_REQUEST)

                if sheet_name not in available_sheets:
                    return Response({
                        'error': f'Sheet "{sheet_name}" not found',
                        'available_sheets': available_sheets
                    }, status=status.HTTP_400_BAD_REQUEST)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'Sheet "{sheet_name}" is empty.'
                    }, status=status.HTTP_400_BAD_REQUEST)

                headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                if not required_headers.issubset(set(headers)):
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'Missing required headers. Required: {required_headers}, Found: {set(headers)}'
                    }, status=status.HTTP_400_BAD_REQUEST)

                for row in ws.iter_rows(min_row=2, values_only=True):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    data.append(row_dict)

                if not data:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'Sheet "{sheet_name}" has no data rows.'
                    }, status=status.HTTP_400_BAD_REQUEST)

            # CSV
            elif format_type == 'csv':
                decoded_file = file.read().decode('utf-8')
                dataset = Dataset()
                dataset.load(decoded_file, format='csv')

                for row in dataset.dict:
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({
                            "statusCode": 400,
                            "status": False,
                            "message": (
                                f'Missing required headers. Required: {", ".join(required_headers)}. '
                                f'Found: {", ".join(row_lower.keys())}'
                            )
                        }, status=status.HTTP_400_BAD_REQUEST)
                    data.append(row_lower)

                if not data:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": "CSV file is empty."
                    }, status=status.HTTP_400_BAD_REQUEST)

            else:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": 'Unsupported file format. Use .xlsx or .csv'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Process import data
            imported_count = 0
            for row in  reversed(data):
                name = str(row.get('marital status')).strip() if row.get('marital status') else None
                description = str(row.get('description')).strip() if row.get('description') else ''
                is_active = row.get('is_active')
                is_active = bool(int(is_active)) if str(is_active).isdigit() else True

                if not name:
                    continue

                existing = Maritalstatus.objects.filter(name__iexact=name).first()
                if existing:
                    if not existing.is_deleted:
                        duplicate_names.append(name)
                        continue
                    else:
                        existing.description = description
                        existing.is_active = is_active
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    Maritalstatus.objects.create(
                        name=name,
                        description=description,
                        is_active=is_active,
                        is_deleted=False
                    )
                    imported_count += 1

        except Exception as e:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": list(set(duplicate_names)),
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count
        }, status=status.HTTP_200_OK)



#-------------------------------continents--------------------------------
class ContinentListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'updated_at')
        sort_order = request.GET.get('sortOrder', 'desc')
        allowed_sort_fields = ['name', 'description', 'updated_at']

        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = Continents.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = ContinentSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class ContinentCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        name = request.data.get("name", "").strip()
        existing = Continents.objects.filter(name__iexact=name, is_deleted=False).first()
        if existing:
            return Response({"statusCode": 400, "status": False, "message": "Continent with this name already exists."}, status=400)

        serializer = ContinentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"statusCode": 200, "status": True, "message": "Continent created successfully", "data": serializer.data})
        errors = " ".join([msg for msgs in serializer.errors.values() for msg in msgs])
        return Response({"statusCode": 400, "status": False, "message": errors}, status=400)



class ContinentRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = Continents.objects.get(uuid=uuid, is_deleted=False)
        except Continents.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "Not found"}, status=404)
        serializer = ContinentSerializer(obj)
        return Response({"statusCode": 200, "status": True, "message": "Retrieved successfully", "data": serializer.data})


class ContinentUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = Continents.objects.get(uuid=uuid, is_deleted=False)
        except Continents.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "Not found"}, status=404)

        serializer = ContinentSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"statusCode": 200, "status": True, "message": "Continent updated successfully", "data": serializer.data})
        errors = " ".join([msg for msgs in serializer.errors.values() for msg in msgs])
        return Response({"statusCode": 400, "status": False, "message": errors}, status=400)


class ContinentDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get('id', None)

        # Single delete via URL parameter
        if uuid:
            try:
                continent = Continents.objects.get(uuid=uuid)
                continent.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "Continent permanently deleted.",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            except Continents.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Continent not found.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        # Delete all continents
        if ids == "all":
            continents = Continents.objects.all()
            count = continents.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No continents found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
            continents.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} continent(s) permanently deleted.",
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
        continents = Continents.objects.filter(uuid__in=valid_uuids)
        count = continents.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching continents found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_404_NOT_FOUND)

        continents.delete()

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} continent(s) permanently deleted.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        }, status=status.HTTP_200_OK)




class ContinentExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        # --- Get query params ---
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')  # comma-separated fields
        uuids_param = request.GET.get('uuids', '')  # comma-separated UUIDs
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        # --- Field to header mapping ---
        field_header_map = {
            'uuid': 'UUID',
            'name': 'Continent',
            'description': 'Description',
            'is_active': 'Active',
            'is_deleted': 'Deleted',
            'created_at': 'Created On',
            'updated_at': 'Modified On',
        }

        # --- Determine which fields to export ---
        if fields:
            field_list = [f.strip() for f in fields.split(',')]
        else:
            field_list = list(field_header_map.keys())

        # --- Fetch queryset ---
        queryset = Continents.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        # --- Prepare dataset ---
        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'Continents'

        for obj in queryset:
            row = []
            for field in field_list:
                value = getattr(obj, field, '')

                if field in ['created_at', 'updated_at'] and value:
                    # Convert UTC to IST
                    value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
                elif isinstance(value, bool):
                    value = int(value)

                row.append(value if value is not None else '')
            dataset.append(row)

        # --- Export data ---
        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'continents.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'continents.xlsx'

        # --- Return response ---
        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response



class ContinentImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicate_names = []

        # Required and optional headers
        required_headers = {'continent'}
        optional_headers = {'description'}

        try:
            data = []
            headers = []

            # ---------- XLSX Handling ----------
            if format_type == 'xlsx':
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({
                        'error': 'Please provide sheet_name',
                        'available_sheets': available_sheets
                    }, status=status.HTTP_400_BAD_REQUEST)

                if sheet_name not in available_sheets:
                    return Response({
                        'error': f'Sheet "{sheet_name}" not found in uploaded file',
                        'available_sheets': available_sheets
                    }, status=status.HTTP_400_BAD_REQUEST)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'The uploaded XLSX file (sheet: "{sheet_name}") is empty. Please provide at least one data row.'
                    }, status=status.HTTP_400_BAD_REQUEST)

                headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]

                # Validate required headers
                if not required_headers.issubset(set(headers)):
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        'message': f'Missing required headers. Required: {required_headers}, Found: {set(headers)}'
                    }, status=status.HTTP_400_BAD_REQUEST)

                for row in ws.iter_rows(min_row=2, values_only=True):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    data.append(row_dict)

                if not data:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'The uploaded XLSX file (sheet: "{sheet_name}") is empty. Please provide at least one data row.'
                    }, status=status.HTTP_400_BAD_REQUEST)

            # ---------- CSV Handling ----------
            elif format_type == 'csv':
                decoded_file = file.read().decode('utf-8')
                dataset = Dataset()
                dataset.load(decoded_file, format='csv')

                for row in dataset.dict:
                    row_lower = {k.strip().lower(): v for k, v in row.items()}

                    # Validate required headers
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({
                            "statusCode": 400,
                            "status": False,
                            "message": (
                                f'Missing required headers. Required: {", ".join(required_headers)}. '
                                f'Found headers in the file: {", ".join(row_lower.keys())}.'
                            )
                        }, status=status.HTTP_400_BAD_REQUEST)

                    data.append(row_lower)

                if not data:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": "The uploaded CSV file is empty. Please provide at least one data row."
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    'error': 'Unsupported file format. Use .xlsx or .csv'
                }, status=status.HTTP_400_BAD_REQUEST)

            imported_count = 0

            # ---------- Import Rows ----------
            for row in  reversed(data):
                name = str(row.get('continent')).strip() if row.get('continent') else None
                description = str(row.get('description')).strip() if row.get('description') else ''
                
                if not name:
                    continue  # skip rows without name

                existing = Continents.objects.filter(name__iexact=name).first()
                if existing:
                    if existing.is_deleted:
                        existing.is_deleted = False
                        existing.description = description
                       
                        existing.save()
                        imported_count += 1
                    else:
                        duplicate_names.append(name)
                        continue
                else:
                    Continents.objects.create(
                        name=name,
                        description=description,
                       
                        is_deleted=False
                    )
                    imported_count += 1

        except Exception as e:
            return Response({
                "statusCode": 400,
                "status": False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": list(set(duplicate_names)),
            "imported_count": imported_count,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful"
        }, status=status.HTTP_200_OK)

#-------------------------------------------country---------------------------------


class CountryListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'updated_at')
        sort_order = request.GET.get('sortOrder', 'desc')
        allowed_sort_fields = ['name', 'shortName', 'fullName', 'capitalCity', 'created_at']

        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = Country.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(shortName__icontains=search) |
                Q(fullName__icontains=search) |
                Q(capitalCity__icontains=search)
            )

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = CountrySerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

class CountryCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        name = request.data.get("name", "").strip()
        existing = Country.objects.filter(name__iexact=name, is_deleted=False).first()
        if existing:
            return Response({"statusCode": 400, "status": False, "message": "Country with this name already exists."}, status=400)

        serializer = CountrySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"statusCode": 200, "status": True, "message": "Country created successfully", "data": serializer.data})
        errors = " ".join([msg for msgs in serializer.errors.values() for msg in msgs])
        return Response({"statusCode": 400, "status": False, "message": errors}, status=400)


class CountryRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = Country.objects.get(uuid=uuid, is_deleted=False)
        except Country.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "Country not found"}, status=404)
        serializer = CountrySerializer(obj)
        return Response({"statusCode": 200, "status": True, "message": "Retrieved successfully", "data": serializer.data})


class CountryUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = Country.objects.get(uuid=uuid, is_deleted=False)
        except Country.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "Country not found"}, status=404)

        serializer = CountrySerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"statusCode": 200, "status": True, "message": "Country updated successfully", "data": serializer.data})
        errors = " ".join([msg for msgs in serializer.errors.values() for msg in msgs])
        return Response({"statusCode": 400, "status": False, "message": errors}, status=400)


class CountryDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        ids = request.data.get('id', None)

        if not ids:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide 'id' field (UUID list or 'all').",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        # Delete all
        if ids == "all":
            countries = Country.objects.filter(is_deleted=False)
            count = countries.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No countries found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

            countries.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} country(s) deleted successfully.",
                "data": None
            }, status=status.HTTP_200_OK)

        # Validate list of UUIDs
        if not isinstance(ids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide a list of UUIDs in 'id' field or 'all'.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

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
            }, status=status.HTTP_400_BAD_REQUEST)

        countries = Country.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = countries.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching countries found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_404_NOT_FOUND)

        countries.delete()

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} country(s) deleted successfully.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        }, status=status.HTTP_200_OK)


class CountryExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')  # comma-separated fields
        uuids_param = request.GET.get('uuids', '')  # comma-separated UUIDs
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        # --- Field to header mapping ---
        field_header_map = {
            'uuid': 'UUID',
            'name': 'Country Name',
            'continent': 'Continent',
            'shortName': 'Country Short Name',
            'fullName': 'Country Official Name',
            'officialName': 'Country Official Name',
            'capitalCity': 'Capital City',
            'dialCodes': 'Country Calling Code',
            'currencyfullname':'Currency Full Name',
            'currencyshortname':'Currency Short Name',
            'currencyCode': 'Currency Code',
            'description':'Description',
            'status': 'Status',
            'is_active': 'Active',
            'is_deleted': 'Deleted',
            'created_at': 'Created On',
            'updated_at': 'Modified On'
        }

        if fields:
            field_list = [f.strip() for f in fields.split(',')]
        else:
            field_list = list(field_header_map.keys())

        queryset = Country.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'Country'
        for obj in queryset:
            row = []
            for field in field_list:
                value = getattr(obj, field, '')

                if field == 'continent' and obj.continent:
                    value = obj.continent.name
                elif field in ['created_at', 'updated_at'] and value:
                    value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
                elif isinstance(value, bool):
                    value = int(value)

                row.append(value if value is not None else '')
            dataset.append(row)

        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv; charset=utf-8'
            file_name = 'countries.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'countries.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


class CountryImportAPIView(APIView):

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicate_names = []
        skipped_rows = []

        required_headers = {'country name','continent'}
        optional_headers = {
            'country short name', 'country full name', 'country official name', 'capital city',
            'country calling code', 'currency full name', 'currency short name', 'currency code', 'description',
        }

        try:
            data = []
            headers = []

            if format_type == 'xlsx':
                import openpyxl
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({'error': 'Please provide sheet_name', 'available_sheets': available_sheets}, status=400)
                if sheet_name not in available_sheets:
                    return Response({'error': f'Sheet "{sheet_name}" not found', 'available_sheets': available_sheets}, status=400)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'The uploaded XLSX sheet "{sheet_name}" is empty.'
                    }, status=400)

                headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                if not required_headers.issubset(set(headers)):
                    return Response({
                        "statusCode": 400,
                        "status": True,
                        "message": f'Missing required headers. Required: {required_headers}, Found: {set(headers)}'
                    }, status=400)

                for row in ws.iter_rows(min_row=2, values_only=True):
                    if not any(row):
                        continue
                    data.append(dict(zip(headers, row)))

            elif format_type == 'csv':
                
                decoded_file = file.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(decoded_file))
                for row in reader:
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({
                            "statusCode": 400,
                            "status": True,
                            "message": f'Missing required headers. Required: {required_headers}. Found: {set(row_lower.keys())}'
                        }, status=400)
                    data.append(row_lower)
            else:
                return Response({
                    "statusCode": 400,
                    "status": True,
                    'error': 'Unsupported file format. Use .xlsx or .csv'
                }, status=400)

            imported_count = 0
            for row in reversed(data):
                country_name = str(row.get('country name')).strip() if row.get('country name') else None
                if not country_name:
                    skipped_rows.append({
                        "Country Name": "Unknown",
                        "Reason": "Missing required field: country name"
                    })
                    continue
                continent_name = str(row.get('continent')).strip() if row.get('continent') else ''
                short_name = str(row.get('country short name')).strip() if row.get('country short name') else ''
                full_name = str(row.get('country full name')).strip() if row.get('country full name') else ''
                official_name = str(row.get('country official name')).strip() if row.get('country official name') else ''
                capital_city = str(row.get('capital city')).strip() if row.get('capital city') else ''
                dial_codes = row.get('dial codes')
                currency_full_name = str(row.get('currency full name')).strip() if row.get('currency full name') else ''
                currency_short_name = str(row.get('currency short name')).strip() if row.get('currency short name') else ''
                currency_code = str(row.get('currency code')).strip() if row.get('currency code') else ''
                description = str(row.get('description')).strip() if row.get('description') else ''
                                

                # Parse JSON field safely
                if dial_codes:
                    import json
                    try:
                        dial_codes = json.loads(dial_codes) if isinstance(dial_codes, str) else dial_codes
                    except Exception:
                        dial_codes = [str(dial_codes)]


                continent_obj = None
                if continent_name:
                    continent_obj = Continents.objects.filter(name__iexact=continent_name).first()
                    if not continent_obj:
                        skipped_rows.append({
                            "Country Name": country_name,
                            "Continent": continent_name,
                            "Reason": "Invalid continent name"
                        })
                        continue

                existing = Country.objects.filter(name__iexact=country_name).first()
                if existing:
                    if not getattr(existing, "is_deleted", False):
                        duplicate_names.append({
                            "Country Name": existing.name,
                            "Continent": existing.continent.name if existing.continent else None 
                        })
                        continue
                    else:
                        existing.continent = continent_obj
                        existing.shortName = short_name
                        existing.fullName = full_name
                        existing.officialName = official_name
                        existing.capitalCity = capital_city
                        existing.dialCodes = dial_codes
                        existing.currencyfullname = currency_full_name
                        existing.currencyshortname = currency_short_name
                        existing.currencyCode = currency_code
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    try:
                        Country.objects.create(
                            name=country_name,
                            continent=continent_obj,
                            shortName=short_name,
                            fullName=full_name,
                            officialName=official_name,
                            capitalCity=capital_city,
                            dialCodes=dial_codes,
                            currencyfullname=currency_full_name,
                            currencyshortname=currency_short_name,
                            currencyCode=currency_code,
                            description=description,
                            is_deleted=False
                        )
                        imported_count += 1
                    except IntegrityError:
                        duplicate_names.append({
                            "Country Name": country_name,
                            "Continent": continent_obj.name if continent_obj else ""
                        })

        except Exception as e:
            return Response({
                "statusCode": 400,
                "status": True,
                'message': str(e)
            }, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": duplicate_names,
            "skipped_rows": skipped_rows,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count
        }, status=200)




class CountriesByContinentAPIView(APIView):
    def get(self, request):
        continent_id = request.GET.get("continent_id")
        if not continent_id:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "continent_id is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            continent_uuid = uuid.UUID(continent_id)
        except ValueError:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Invalid UUID format for continent_id"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            continent = Continents.objects.get(id=continent_id)
        except Continents.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Invalid Continent ID"
            }, status=status.HTTP_404_NOT_FOUND)

        countries = Country.objects.filter(continent=continent)
        data = []
        for country in countries:
            data.append({
                "id": str(country.uuid),
                "name": country.name,
                "shortName": country.shortName,
                "fullName": country.fullName
            })

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"Countries for continent '{continent.name}' fetched successfully",
            "data": data
        }, status=status.HTTP_200_OK)



#-------------------------------------------state---------------------------------

class StateListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'updated_at')
        sort_order = request.GET.get('sortOrder', 'desc')
        allowed_sort_fields = ['stateName', 'stateshortName', 'updated_at']

        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = State.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(
                Q(stateName__icontains=search) |
                Q(stateshortName__icontains=search) |
                Q(description__icontains=search) |
                Q(countryName__name__icontains=search)
            )

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = StateSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class StateCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        state_name = request.data.get("stateName", "").strip()
        country_id = request.data.get("country_id")

        existing = State.objects.filter(stateName__iexact=state_name, countryName_id=country_id, is_deleted=False).first()
        if existing:
            return Response({"statusCode": 400, "status": False, "message": "State with this name already exists for this country."}, status=400)

        serializer = StateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"statusCode": 200, "status": True, "message": "State created successfully", "data": serializer.data})
        errors = " ".join([msg for msgs in serializer.errors.values() for msg in msgs])
        return Response({"statusCode": 400, "status": False, "message": errors}, status=400)


class StateRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = State.objects.get(uuid=uuid, is_deleted=False)
        except State.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "State not found"}, status=404)
        serializer = StateSerializer(obj)
        return Response({"statusCode": 200, "status": True, "message": "Retrieved successfully", "data": serializer.data})


class StateUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = State.objects.get(uuid=uuid, is_deleted=False)
        except State.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "State not found"}, status=404)

        serializer = StateSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"statusCode": 200, "status": True, "message": "State updated successfully", "data": serializer.data})
        errors = " ".join([msg for msgs in serializer.errors.values() for msg in msgs])
        return Response({"statusCode": 400, "status": False, "message": errors}, status=400)


class StateDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        ids = request.data.get('id', None)

        if not ids:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide 'id' field (UUID list or 'all').",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        # Delete all states
        if ids == "all":
            states = State.objects.filter(is_deleted=False)
            count = states.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No states found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

            states.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} state(s) deleted successfully.",
                "data": None
            }, status=status.HTTP_200_OK)

        # Validate list of UUIDs
        if not isinstance(ids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide a list of UUIDs in 'id' field or 'all'.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

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
            }, status=status.HTTP_400_BAD_REQUEST)

        states = State.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = states.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching states found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_404_NOT_FOUND)

        states.delete()

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} state(s) deleted successfully.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        }, status=status.HTTP_200_OK)


class StateExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        # Header map for export
        field_header_map = {
            'uuid': 'UUID',
            'countryName': 'Country Name',
            'stateName': 'State Name',
            'stateshortName': 'State Short Name',
            'state':'State / Territory',
            'description': 'Description',
            'is_active': 'Active',
            'is_deleted': 'Deleted',
            'created_at': 'Created On',
            'updated_at': 'Modified On',
        }

        # Choose fields
        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())

        # Fetch queryset
        queryset = State.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        # Prepare dataset
        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'State'

        for obj in queryset:
            row = []
            for field in field_list:
                if field == 'country_name':
                    value = obj.countryName.name if obj.countryName else ''
                else:
                    value = getattr(obj, field, '')
                
                # Convert state/territory to Title Case
                if field == 'state' and value:
                    value = value.capitalize()  # STATE -> State, TERRITORY -> Territory

                # Format date/time fields
                if field in ['created_at', 'updated_at'] and value:
                    value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
                elif isinstance(value, bool):
                    value = int(value)
                
                row.append(value if value is not None else '')
            dataset.append(row)

        # Export file
        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'states.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'states.xlsx'

        # Build response
        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response

class StateImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicate_names = []
        skipped_rows = []

        required_headers = {'state name', 'country name'}
        optional_headers = { 'state / territory','state short name', 'description'}

        try:
            data = []
            headers = []

            # ---------------- XLSX Import ----------------
            if format_type == 'xlsx':
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({
                        'error': 'Please provide sheet_name',
                        'available_sheets': available_sheets
                    }, status=400)

                if sheet_name not in available_sheets:
                    return Response({
                        'error': f'Sheet "{sheet_name}" not found',
                        'available_sheets': available_sheets
                    }, status=400)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'The uploaded XLSX sheet "{sheet_name}" is empty.'
                    }, status=400)

                headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]

                if not required_headers.issubset(set(headers)):
                    return Response({
                        "statusCode": 400,
                        "status": True,
                        "message": f'Missing required headers. Required: {required_headers}, Found: {set(headers)}'
                    }, status=400)

                for row in ws.iter_rows(min_row=2, values_only=True):
                    if not any(row):
                        continue
                    data.append(dict(zip(headers, row)))

            # ---------------- CSV Import ----------------
            elif format_type == 'csv':
                decoded_file = file.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(decoded_file))
                for row in reader:
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({
                            "statusCode": 400,
                            "status": True,
                            "message": f'Missing required headers. Required: {required_headers}. Found: {set(row_lower.keys())}'
                        }, status=400)
                    data.append(row_lower)
            else:
                return Response({
                    "statusCode": 400,
                    "status": True,
                    'error': 'Unsupported file format. Use .xlsx or .csv'
                }, status=400)

            # ---------------- Data Processing ----------------
            imported_count = 0
            for row in  reversed(data):
                state_name = str(row.get('state name')).strip() if row.get('state name') else None
                country_name = str(row.get('country name')).strip() if row.get('country name') else None
                short_name = str(row.get('state short name')).strip() if row.get('state short name') else ''
                description = str(row.get('description')).strip() if row.get('description') else ''
                state_type = str(row.get('state / territory')).strip().upper() if row.get('state / territory') else None
          

                if not state_name or not country_name or not state_type:
                    skipped_rows.append({
                        "State Name": state_name or "Unknown",
                        "Country Name": country_name or "Unknown",
                        "State / Territory":state_type or "Unknown",
                        "Reason": "Missing required field or Invalid state type: Use (State, Territory)"
                    })
                    continue

                if state_type not in ['STATE', 'TERRITORY']:
                    skipped_rows.append({
                        "State Name": state_name,
                        "Country Name": country_name,
                        "State / Territory":state_type or "Unknown",
                        "Reason": f'Invalid state type: Use (State, Territory)'
                    })
                    continue

                # Get related Country object
                country_obj = Country.objects.filter(name__iexact=country_name).first()
                if not country_obj:
                    skipped_rows.append({
                        "State Name": state_name,
                        "Country Name": country_name,
                        "State / Territory":state_type or "Unknown",
                        "Reason": "Country not found"
                    })
                    continue

                # Check for existing state
                existing = State.objects.filter(stateName__iexact=state_name, countryName=country_obj).first()
                if existing:
                    if not existing.is_deleted:
                        duplicate_names.append({
                            "State Name": existing.stateName,
                            "Country Name": country_obj.name
                        })
                        continue
                    else:
                        # Restore deleted record
                        existing.stateshortName = short_name
                        existing.description = description
                        existing.countryName = country_obj
                        existing.state = state_type  # set uppercase value
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    State.objects.create(
                        stateName=state_name,
                        stateshortName=short_name,
                        description=description,
                        countryName=country_obj,
                        state=state_type,  # set uppercase value
                        is_deleted=False
                    )
                    imported_count += 1

        except Exception as e:
            return Response({
                "statusCode": 400,
                "status": True,
                'message': str(e)
            }, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": duplicate_names,
            "skipped_rows": skipped_rows,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count
        }, status=200)

class StateByCountryAPIView(APIView):
    def get(self, request):
        country_id = request.GET.get("country_id")
        if not country_id:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "country_id is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        

        try:
            country_uuid = uuid.UUID(country_id)
        except ValueError:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Invalid UUID format for country_id"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            country = Country.objects.get(uuid=country_uuid)

        except Country.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Invalid Country ID"
            }, status=status.HTTP_404_NOT_FOUND)

        states = State.objects.filter(countryName=country)
        data = []
        for state in states:
            data.append({
                "uuid": str(state.uuid),
                "name": state.stateName,
                "shortName": state.stateshortName,
                "fullName": state.description
            })

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"State for country '{state.stateName}' fetched successfully",
            "data": data
        }, status=status.HTTP_200_OK)







#-------------------------------------------district---------------------------------
class DistrictListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'updated_at')
        sort_order = request.GET.get('sortOrder', 'desc')
        allowed_sort_fields = ['districtName', 'created_at']

        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = District.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(
                Q(districtName__icontains=search) |
                Q(description__icontains=search) |
                Q(stateName__stateName__icontains=search) |
                Q(countryName__name__icontains=search)
            )

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = DistrictSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


# -------------------- Create -------------------- #
class DistrictCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        district_name = request.data.get("districtName", "").strip()
        country_id = request.data.get("country_id")
        state_id = request.data.get("state_id")

        existing = District.objects.filter(
            districtName__iexact=district_name,
            countryName_id=country_id,
            stateName_id=state_id,
            is_deleted=False
        ).first()
        if existing:
            return Response({"statusCode": 400, "status": False, "message": "District with this name already exists in the selected state and country."}, status=400)

        serializer = DistrictSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"statusCode": 200, "status": True, "message": "District created successfully", "data": serializer.data})
        errors = " ".join([msg for msgs in serializer.errors.values() for msg in msgs])
        return Response({"statusCode": 400, "status": False, "message": errors}, status=400)


# -------------------- Retrieve -------------------- #
class DistrictRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = District.objects.get(uuid=uuid, is_deleted=False)
        except District.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "District not found"}, status=404)
        serializer = DistrictSerializer(obj)
        return Response({"statusCode": 200, "status": True, "message": "Retrieved successfully", "data": serializer.data})


# -------------------- Update -------------------- #
class DistrictUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = District.objects.get(uuid=uuid, is_deleted=False)
        except District.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "District not found"}, status=404)

        serializer = DistrictSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"statusCode": 200, "status": True, "message": "District updated successfully", "data": serializer.data})
        errors = " ".join([msg for msgs in serializer.errors.values() for msg in msgs])
        return Response({"statusCode": 400, "status": False, "message": errors}, status=400)


# -------------------- Delete -------------------- #
class DistrictDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        ids = request.data.get('id', None)

        if not ids:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide 'id' field (UUID list or 'all').",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        # Delete all districts
        if ids == "all":
            districts = District.objects.filter(is_deleted=False)
            count = districts.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No districts found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

            districts.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} district(s) deleted successfully.",
                "data": None
            }, status=status.HTTP_200_OK)

        # Validate list of UUIDs
        if not isinstance(ids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide a list of UUIDs in 'id' field or 'all'.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

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
            }, status=status.HTTP_400_BAD_REQUEST)

        districts = District.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = districts.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching districts found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_404_NOT_FOUND)

        districts.delete()

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} district(s) deleted successfully.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        }, status=status.HTTP_200_OK)




# -------------------- Export -------------------- 

class DistrictExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        # Header map for better readability
        field_header_map = {
            'uuid': 'UUID',
            'countryName': 'Country Name',
            'stateName': 'State Name',
            'districtName': 'District Name',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'created_at': 'Created On',
            'updated_at': 'Modified On',
        }

        # Select fields to include in export
        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())

        # Queryset with filtering and ordering
        queryset = District.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        # Initialize dataset
        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'District'

        for obj in queryset:
            row = []
            for field in field_list:
                if field == 'country_name':
                    value = obj.countryName.name if obj.countryName else ''
                elif field == 'state_name':
                    value = obj.stateName.stateName if obj.stateName else ''
                else:
                    value = getattr(obj, field, '')
                # Format timestamps
                if field in ['created_at', 'updated_at'] and value:
                    value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
                elif isinstance(value, bool):
                    value = int(value)
                row.append(value if value is not None else '')
            dataset.append(row)

        # Export file based on requested format
        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'districts.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'districts.xlsx'

        # Prepare response
        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response




# -------------------- Import -------------------- 
class DistrictImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicate_names = []
        skipped_rows = []

        required_headers = {'district name', 'country name'}
        optional_headers = {'description','state name'}

        try:
            data = []
            headers = []

            # ---------------- XLSX Import ----------------
            if format_type == 'xlsx':
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({
                        'error': 'Please provide sheet_name',
                        'available_sheets': available_sheets
                    }, status=400)

                if sheet_name not in available_sheets:
                    return Response({
                        'error': f'Sheet "{sheet_name}" not found',
                        'available_sheets': available_sheets
                    }, status=400)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'The uploaded XLSX sheet "{sheet_name}" is empty.'
                    }, status=400)

                headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                if not required_headers.issubset(set(headers)):
                    return Response({
                        "statusCode": 400,
                        "status": True,
                        "message": f'Missing required headers. Required: {required_headers}, Found: {set(headers)}'
                    }, status=400)

                for row in ws.iter_rows(min_row=2, values_only=True):
                    if not any(row):
                        continue
                    data.append(dict(zip(headers, row)))

            # ---------------- CSV Import ----------------
            elif format_type == 'csv':
                decoded_file = file.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(decoded_file))
                for row in reader:
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({
                            "statusCode": 400,
                            "status": True,
                            "message": f'Missing required headers. Required: {required_headers}. Found: {set(row_lower.keys())}'
                        }, status=400)
                    data.append(row_lower)
            else:
                return Response({
                    "statusCode": 400,
                    "status": True,
                    'error': 'Unsupported file format. Use .xlsx or .csv'
                }, status=400)

            # ---------------- Data Processing ----------------
            imported_count = 0
            existing_in_file = set()
            for row in  reversed(data):
                district_name = str(row.get('district name')).strip() if row.get('district name') else None
                state_name = str(row.get('state name')).strip() if row.get('state name') else None
                country_name = str(row.get('country name')).strip() if row.get('country name') else None
                description = str(row.get('description')).strip() if row.get('description') else ''
                
                key = (district_name.lower(), state_name.lower(), country_name.lower())


                if not district_name or not country_name:
                    skipped_rows.append({
                        "District Name": district_name or "Unknown",
                        "Country Name": country_name or "Unknown",
                        "State Name":state_name or "Unknown",
                        "Reason": "Missing required field"
                    })
                    continue

                country_obj = Country.objects.filter(name__iexact=country_name).first()
                if not country_obj:
                    skipped_rows.append({
                        "District Name": district_name,
                        "Country Name": country_name,
                        "State Name": state_name or "Unknown",
                        "Reason": "Country not found"
                    })
                    continue

                # Fetch state if provided
                state_obj = None
                if state_name:
                    state_obj = State.objects.filter(stateName__iexact=state_name, countryName=country_obj).first()
                    if not state_obj:
                        skipped_rows.append({
                            "District Name": district_name,
                            "State Name": state_name,
                            "Country Name": country_name,
                            "Reason": "State not found for this country"
                        })
                        continue
                

                existing = District.objects.filter(
                    districtName__iexact=district_name,
                    stateName=state_obj, 
                    countryName=country_obj
                ).first()

                if existing or key in existing_in_file:
                        duplicate_names.append({
                            "District Name": existing.districtName,
                            "State Name": state_obj.stateName if state_obj else None,
                            "Country Name": country_obj.name
                        })
                        continue
                    
                try:
                    District.objects.create(
                        districtName=district_name,
                        stateName=state_obj,
                        countryName=country_obj,
                        description=description,
                        is_deleted=False
                    )
                    imported_count += 1
                    existing_in_file.add(key)
                except IntegrityError:
                    duplicate_names.append({
                        "District Name": existing.districtName,
                        "State Name": state_obj.stateName if state_obj else None,
                        "Country Name": country_obj.name
                    })   
                    
        except Exception as e:
            return Response({
                "statusCode": 400,
                "status": True,
                'message': str(e)
            }, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": duplicate_names,
            "skipped_rows": skipped_rows,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count
        }, status=200)



class DistrictByFilterAPIView(APIView):
    def get(self, request):
        country_id = request.GET.get("country_id")
        state_id = request.GET.get("state_id")


        if country_id:
            try:
                country_uuid = uuid.UUID(country_id)
            except ValueError:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Invalid UUID format for country_id"
                }, status=status.HTTP_400_BAD_REQUEST)
            try:
                country = Country.objects.get(uuid=country_uuid)
            except Country.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Country not found"
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            country = None

        if state_id:
            try:
                state_uuid = uuid.UUID(state_id)
            except ValueError:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Invalid UUID format for state_id"
                }, status=status.HTTP_400_BAD_REQUEST)
            try:
                state = State.objects.get(uuid=state_uuid)
            except State.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "State not found"
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            state = None


        districts = District.objects.filter(is_deleted=False)
        if country:
            districts = districts.filter(countryName=country)
        if state:
            districts = districts.filter(stateName=state)

        data = []
        for district in districts:
            data.append({
                "uuid": str(district.uuid),
                "districtName": district.districtName,
                "country": district.countryName.name if district.countryName else None,
                "state": district.stateName.stateName if district.stateName else None,
                "description": district.description
            })

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{len(data)} districts fetched successfully",
            "data": data
        }, status=status.HTTP_200_OK)




#--------------------------city--------------------
class CityListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'updated_at')
        sort_order = request.GET.get('sortOrder', 'desc')
        allowed_sort_fields = ['cityName', 'created_at']

        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = City.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(
                Q(cityName__icontains=search) |
                Q(description__icontains=search) |
                Q(districtName__districtName__icontains=search) |
                Q(stateName__stateName__icontains=search) |
                Q(countryName__name__icontains=search)
            )

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = CitySerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


# -------------------- City -------------------- 
class CityCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        city_name = request.data.get("cityName", "").strip()
        country_id = request.data.get("country_id")
        state_id = request.data.get("state_id")
        district_id = request.data.get("district_id")

        existing = City.objects.filter(
            cityName__iexact=city_name,
            countryName_id=country_id,
            stateName_id=state_id,
            districtName_id=district_id,
            is_deleted=False
        ).first()
        if existing:
            return Response({"statusCode": 400, "status": False, "message": "City with this name already exists in the selected district/state/country."}, status=400)

        serializer = CitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"statusCode": 200, "status": True, "message": "City created successfully", "data": serializer.data})
        errors = " ".join([msg for msgs in serializer.errors.values() for msg in msgs])
        return Response({"statusCode": 400, "status": False, "message": errors}, status=400)


class CityRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = City.objects.get(uuid=uuid, is_deleted=False)
        except City.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "City not found"}, status=404)
        serializer = CitySerializer(obj)
        return Response({"statusCode": 200, "status": True, "message": "Retrieved successfully", "data": serializer.data})


class CityUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = City.objects.get(uuid=uuid, is_deleted=False)
        except City.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "City not found"}, status=404)

        serializer = CitySerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"statusCode": 200, "status": True, "message": "City updated successfully", "data": serializer.data})
        errors = " ".join([msg for msgs in serializer.errors.values() for msg in msgs])
        return Response({"statusCode": 400, "status": False, "message": errors}, status=400)



class CityDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        ids = request.data.get('id', None)

        if not ids:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide 'id' field (UUID list or 'all').",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        # Delete all cities
        if ids == "all":
            cities = City.objects.filter(is_deleted=False)
            count = cities.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No cities found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

            cities.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} city(s) deleted successfully.",
                "data": None
            }, status=status.HTTP_200_OK)

        # Validate list of UUIDs
        if not isinstance(ids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide a list of UUIDs in 'id' field or 'all'.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

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
            }, status=status.HTTP_400_BAD_REQUEST)

        cities = City.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = cities.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching cities found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_404_NOT_FOUND)

        cities.delete()

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} city(s) deleted successfully.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        }, status=status.HTTP_200_OK)



class CityExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        # Field to header mapping
        field_header_map = {
            'uuid': 'UUID',
            'countryName': 'Country Name',
            'stateName': 'State Name',
            'districtName': 'District Name',
            'cityName': 'City Name',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'created_at': 'Created On',
            'updated_at': 'Modified On'
        }

        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())

        queryset = City.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'City'

        for city in queryset:
            row = []
            for field in field_list:
                value = getattr(city, field, '')

                # Handle foreign keys by name
                if field == 'countryName' and city.countryName:
                    value = city.countryName.name
                elif field == 'stateName' and city.stateName:
                    value = city.stateName.stateName
                elif field == 'districtName' and city.districtName:
                    value = city.districtName.districtName

                # Format datetime
                if field in ['created_at', 'updated_at'] and value:
                    value = timezone.localtime(value).strftime("%d-%m-%Y %I:%M:%S %p")
                # Convert bool to int
                if isinstance(value, bool):
                    value = int(value)

                row.append(value if value is not None else '')
            dataset.append(row)

        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'cities.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'city.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


class CityImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicate_names = []
        skipped_rows = []

        required_headers = {'city name', 'country name'}
        optional_headers = {'state name', 'district name','description'}

        try:
            data = []
            headers = []

            # ---------------- XLSX Import ----------------
            if format_type == 'xlsx':
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({
                        'error': 'Please provide sheet_name',
                        'available_sheets': available_sheets
                    }, status=400)

                if sheet_name not in available_sheets:
                    return Response({
                        'error': f'Sheet "{sheet_name}" not found',
                        'available_sheets': available_sheets
                    }, status=400)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'The uploaded XLSX sheet "{sheet_name}" is empty.'
                    }, status=400)

                headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                if not required_headers.issubset(set(headers)):
                    return Response({
                        "statusCode": 400,
                        "status": True,
                        "message": f'Missing required headers. Required: {required_headers}, Found: {set(headers)}'
                    }, status=400)

                for row in ws.iter_rows(min_row=2, values_only=True):
                    if not any(row):
                        continue
                    data.append(dict(zip(headers, row)))

            # ---------------- CSV Import ----------------
            elif format_type == 'csv':
                decoded_file = file.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(decoded_file))
                for row in reader:
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({
                            "statusCode": 400,
                            "status": True,
                            "message": f'Missing required headers. Required: {required_headers}. Found: {set(row_lower.keys())}'
                        }, status=400)
                    data.append(row_lower)
            else:
                return Response({
                    "statusCode": 400,
                    "status": True,
                    'error': 'Unsupported file format. Use .xlsx or .csv'
                }, status=400)

            # ---------------- Data Processing ----------------
            imported_count = 0
            existing_in_file = set()
            for row in  reversed(data):
                city_name = str(row.get('city name')).strip() if row.get('city name') else None
                country_name = str(row.get('country name')).strip() if row.get('country name') else None
                state_name = str(row.get('state name')).strip() if row.get('state name') else None
                district_name = str(row.get('district name')).strip() if row.get('district name') else None
                description = str(row.get('description')).strip() if row.get('description') else ''
                
                key = (city_name.lower(), district_name.lower(), state_name.lower(), country_name.lower())


                if not city_name or not state_name or not district_name or not country_name:
                    skipped_rows.append({
                        "City Name": city_name or "Unknown",
                        "State Name": state_name or "Unknown",
                        "District Name": district_name or "Unknown",
                        "Country Name": country_name or "Unknown",
                        "Reason": "Missing required field"
                    })
                    continue

                # Fetch related objects
                country_obj = Country.objects.filter(name__iexact=country_name).first()
                if not country_obj:
                    skipped_rows.append({
                        "City Name": city_name,
                        "District Name": district_name,
                        "State Name": state_name,
                        "Country Name": country_name,
                        "Reason": "Country not found"
                    })
                    continue

                state_obj = State.objects.filter(stateName__iexact=state_name, countryName=country_obj).first()
                if not state_obj:
                    skipped_rows.append({
                        "City Name": city_name,
                        "District Name": district_name,
                        "State Name": state_name,
                        "Country Name": country_name,
                        "Reason": "State not found"
                    })
                    continue

                district_obj = District.objects.filter(
                    districtName__iexact=district_name,
                    stateName=state_obj,
                    countryName=country_obj
                ).first()
                if not district_obj:
                    skipped_rows.append({
                        "City Name": city_name,
                        "District Name": district_name,
                        "State Name": state_name,
                        "Country Name": country_name,
                        "Reason": "District not found"
                    })
                    continue

                
                existing = City.objects.filter(
                    cityName__iexact=city_name,
                    districtName=district_obj,
                    stateName=state_obj,
                    countryName=country_obj
                ).first()

                if existing or key in existing_in_file:
                    duplicate_names.append({
                        "City Name": city_name,
                        "District Name": district_obj.districtName,
                        "State Name": state_obj.stateName,
                        "Country Name": country_obj.name
                    })
                    continue

                try:
                    City.objects.create(
                        cityName=city_name,
                        districtName=district_obj,
                        stateName=state_obj,
                        countryName=country_obj,
                        description=description,
                        is_deleted=False
                    )
                    imported_count += 1
                    existing_in_file.add(key)
                except IntegrityError:
                    duplicate_names.append({
                        "City Name": city_name,
                        "District Name": district_obj.districtName,
                        "State Name": state_obj.stateName,
                        "Country Name": country_obj.name
                    })

        except Exception as e:
            return Response({
                "statusCode": 400,
                "status": True,
                'message': str(e)
            }, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": duplicate_names,
            "skipped_rows": skipped_rows,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count
        }, status=200)

        
#--------------------------- Realtion -----------------------
class RelationListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'updated_at')
        sort_order = request.GET.get('sortOrder', 'desc')
        allowed_sort_fields = ['name', 'description', 'updated_at']

        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = Relation.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = RelationSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


# -------------------- Create -------------------- #
class RelationCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        relation_name = request.data.get("name", "").strip()
        existing = Relation.objects.filter(name__iexact=relation_name, is_deleted=False).first()

        if existing:
            return Response({"statusCode": 400, "status": False, "message": "Relation with this name already exists."}, status=400)

        serializer = RelationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"statusCode": 200, "status": True, "message": "Relation created successfully", "data": serializer.data})
        errors = " ".join([msg for msgs in serializer.errors.values() for msg in msgs])
        return Response({"statusCode": 400, "status": False, "message": errors}, status=400)


# -------------------- Retrieve -------------------- #
class RelationRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = Relation.objects.get(uuid=uuid, is_deleted=False)
        except Relation.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "Relation not found"}, status=404)
        serializer = RelationSerializer(obj)
        return Response({"statusCode": 200, "status": True, "message": "Retrieved successfully", "data": serializer.data})


# -------------------- Update -------------------- #
class RelationUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = Relation.objects.get(uuid=uuid, is_deleted=False)
        except Relation.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "Relation not found"}, status=404)

        serializer = RelationSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"statusCode": 200, "status": True, "message": "Relation updated successfully", "data": serializer.data})
        errors = " ".join([msg for msgs in serializer.errors.values() for msg in msgs])
        return Response({"statusCode": 400, "status": False, "message": errors}, status=400)


# -------------------- Delete -------------------- #
class RelationDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        ids = request.data.get('id', None)

        if not ids:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide 'id' field (UUID list or 'all').",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        # Delete all relations
        if ids == "all":
            relations = Relation.objects.filter(is_deleted=False)
            count = relations.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No relations found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

            relations.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} relation(s) deleted successfully.",
                "data": None
            }, status=status.HTTP_200_OK)

        # Validate list of UUIDs
        if not isinstance(ids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide a list of UUIDs in 'id' field or 'all'.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

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
            }, status=status.HTTP_400_BAD_REQUEST)

        relations = Relation.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = relations.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching relations found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_404_NOT_FOUND)

        relations.delete()

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} relation(s) deleted successfully.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        }, status=status.HTTP_200_OK)

# -------------------- Export -------------------- #
class RelationExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')  # comma-separated fields
        uuids_param = request.GET.get('uuids', '')  # comma-separated UUIDs
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        # --- Field to header mapping ---
        field_header_map = {
            'uuid': 'UUID',
            'name': 'Relation',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'created_at': 'Created On',
            'updated_at': 'Modified On'
        }

        # --- Determine which fields to export ---
        if fields:
            field_list = [f.strip() for f in fields.split(',')]
        else:
            field_list = list(field_header_map.keys())

        # --- Fetch queryset ---
        queryset = Relation.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        # --- Prepare dataset ---
        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]

        for obj in queryset:
            row = []
            for field in field_list:
                value = getattr(obj, field, '')

                if field in ['created_at', 'updated_at'] and value:
                    # Convert to IST and format
                    value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
                elif isinstance(value, bool):
                    value = int(value)

                row.append(value if value is not None else '')
            dataset.append(row)

        # --- Export data ---
        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv; charset=utf-8'
            file_name = 'relations.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'relations.xlsx'

        # --- Return response ---
        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


# -------------------- Import -------------------- #
class RelationImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicate_names = []

        # Define required and optional headers
        required_headers = {'relation'}       # must be present
        optional_headers = {'description'}    # optional

        try:
            data = []
            headers = []

            # ---------- XLSX Handling ----------
            if format_type == 'xlsx':
                import openpyxl
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                # Validate sheet name
                if not sheet_name:
                    return Response({
                        'error': 'Please provide sheet_name',
                        'available_sheets': available_sheets
                    }, status=status.HTTP_400_BAD_REQUEST)

                if sheet_name not in available_sheets:
                    return Response({
                        'error': f'Sheet "{sheet_name}" not found in uploaded file',
                        'available_sheets': available_sheets
                    }, status=status.HTTP_400_BAD_REQUEST)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'The uploaded XLSX file (sheet: "{sheet_name}") is empty. Please provide at least one data row.'
                    }, status=status.HTTP_400_BAD_REQUEST)

                headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]

                # Validate required headers
                if not required_headers.issubset(set(headers)):
                    return Response({
                        "statusCode": 400,
                        "status": True,
                        'message': f'Missing required headers. Required: {required_headers}, Found: {set(headers)}'
                    }, status=status.HTTP_400_BAD_REQUEST)

                for row in ws.iter_rows(min_row=2, values_only=True):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    data.append(row_dict)

                if not data:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'The uploaded XLSX file (sheet: "{sheet_name}") is empty. Please provide at least one data row.'
                    }, status=status.HTTP_400_BAD_REQUEST)

            # ---------- CSV Handling ----------
            elif format_type == 'csv':
                from tablib import Dataset
                decoded_file = file.read().decode('utf-8')
                dataset = Dataset()
                dataset.load(decoded_file, format='csv')

                for row in dataset.dict:
                    row_lower = {k.strip().lower(): v for k, v in row.items()}

                    # Validate required headers
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({
                            "statusCode": 400,
                            "status": True,
                            "message": (
                                f'Missing required headers. Required: {", ".join(required_headers)}. '
                                f'Found headers in the file: {", ".join(row_lower.keys())}.'
                            )
                        }, status=status.HTTP_400_BAD_REQUEST)

                    data.append(row_lower)

                if not data:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": "The uploaded CSV file is empty. Please provide at least one data row."
                    }, status=status.HTTP_400_BAD_REQUEST)

            else:
                return Response({
                    "statusCode": 400,
                    "status": True,
                    'error': 'Unsupported file format. Use .xlsx or .csv'
                }, status=status.HTTP_400_BAD_REQUEST)

            imported_count = 0

            # ---------- Import Rows ----------
            for row in  reversed(data):
                name = str(row.get('relation')).strip() if row.get('relation') else None
                description = str(row.get('description')).strip() if row.get('description') else ''

                if not name:
                    continue  # skip rows without relation name

                existing = Relation.objects.filter(name__iexact=name).first()

                if existing:
                    if not existing.is_deleted:
                        duplicate_names.append(name)
                        continue
                    else:
                        # Reactivate if previously deleted
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    Relation.objects.create(
                        name=name,
                        description=description,
                        is_deleted=False
                    )
                    imported_count += 1

        except Exception as e:
            return Response({
                "statusCode": 400,
                "status": True,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": list(set(duplicate_names)),
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count
        }, status=status.HTTP_200_OK)


#-----------------------TimeZone---------------

class TimezoneListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'updated_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['Timezone', 'description', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = Timezone.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(Timezone__icontains=search) |
                Q(description__icontains=search) |
                Q(countryName__name__icontains=search) |
                Q(stateName__stateName__icontains=search)
            )

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = TimezoneSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class TimezoneCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        timezone_name = request.data.get("timezone", "").strip()

        existing = Timezone.objects.filter(Timezone__iexact=timezone_name, is_deleted=False).first()
        if existing:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Timezone with this name already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = TimezoneSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Timezone created successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        errors = serializer.errors
        messages = []
        for field, msgs in errors.items():
            messages.extend(msgs)
        return Response({
            "statusCode": 400,
            "status": False,
            "message": " ".join(messages),
        }, status=status.HTTP_400_BAD_REQUEST)


class TimezoneRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            tz = Timezone.objects.get(uuid=uuid, is_deleted=False)
        except Timezone.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Timezone not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = TimezoneSerializer(tz)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Timezone retrieved successfully",
            "data": serializer.data
        })


class TimezoneUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            tz = Timezone.objects.get(uuid=uuid, is_deleted=False)
        except Timezone.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Timezone not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = TimezoneSerializer(tz, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Timezone updated successfully",
                "data": serializer.data
            })

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


class TimezoneDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get('id', None)

        if uuid:
            try:
                tz = Timezone.objects.get(uuid=uuid)
                tz.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "Timezone permanently deleted.",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            except Timezone.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Timezone not found.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        if ids == "all":
            tzs = Timezone.objects.all()
            count = tzs.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No timezones found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
            tzs.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} timezone(s) permanently deleted.",
                "data": None
            }, status=status.HTTP_200_OK)

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

        tzs = Timezone.objects.filter(uuid__in=valid_uuids)
        count = tzs.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching timezones found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_404_NOT_FOUND)

        tzs.delete()
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} timezone(s) permanently deleted.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        }, status=status.HTTP_200_OK)


class TimezoneExportAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'countryName': 'Country',
            'stateName': 'State',
            'Timezone': 'Time Zone',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'updated_at': 'Modified On'
        }

        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())

        queryset = Timezone.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'Timezone'

        for tz in queryset:
            row = []
            for field in field_list:
                value = getattr(tz, field, '')
                if field in ['created_at', 'updated_at'] and value:
                    value = timezone.localtime(value).strftime("%d-%m-%Y %I:%M:%S %p")
                elif isinstance(value, bool):
                    value = int(value)
                row.append(value if value is not None else '')
            dataset.append(row)

        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'timezones.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'timezones.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


class TimezoneImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicate_names = []

        required_headers = {'time zone'}
        optional_headers = {'country', 'state', 'description'}

        try:
            data = []
            headers = []

            # XLSX Handling
            if format_type == 'xlsx':
                import openpyxl
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({'error': 'Please provide sheet_name', 'available_sheets': available_sheets}, status=400)
                if sheet_name not in available_sheets:
                    return Response({'error': f'Sheet "{sheet_name}" not found', 'available_sheets': available_sheets}, status=400)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({'error': f'Sheet "{sheet_name}" is empty'}, status=400)

                headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                if not required_headers.issubset(set(headers)):
                    return Response({'error': f'Missing required headers: {required_headers}'}, status=400)

                for row in ws.iter_rows(min_row=2, values_only=True):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    data.append(row_dict)

            # CSV Handling
            elif format_type == 'csv':
                from tablib import Dataset
                decoded_file = file.read().decode('utf-8')
                dataset = Dataset()
                dataset.load(decoded_file, format='csv')

                for row in dataset.dict:
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({'error': f'Missing required headers: {required_headers}'}, status=400)
                    data.append(row_lower)

            else:
                return Response({'error': 'Unsupported file format. Use .xlsx or .csv'}, status=400)

            imported_count = 0

            for row in  reversed(data):
                tz_name = str(row.get('time zone')).strip() if row.get('time zone') else None
                if not tz_name:
                    continue

                # Fetch or create related Country and State
                country_obj = None
                state_obj = None

                country_name = str(row.get('country')).strip() if row.get('country') else None
                state_name = str(row.get('state')).strip() if row.get('state') else None

                if country_name:
                    country_obj = Country.objects.filter(name__iexact=country_name, is_deleted=False).first()
                    if not country_obj:
                        country_obj = Country.objects.create(name=country_name, description='', is_deleted=False)

                if state_name:
                    state_obj = State.objects.filter(stateName__iexact=state_name, is_deleted=False).first()
                    if not state_obj:
                        state_obj = State.objects.create(stateName=state_name, countryName=country_obj, description='', is_deleted=False)

                description = str(row.get('description')).strip() if row.get('description') else ''

                existing = Timezone.objects.filter(Timezone__iexact=tz_name).first()
                if existing:
                    if not existing.is_deleted:
                        duplicate_names.append(tz_name)
                        continue
                    else:
                        existing.description = description
                        existing.countryName = country_obj
                        existing.stateName = state_obj
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    Timezone.objects.create(
                        Timezone=tz_name,
                        description=description,
                        countryName=country_obj,
                        stateName=state_obj,
                        is_deleted=False
                    )
                    imported_count += 1

        except Exception as e:
            return Response({
                "statusCode": 400,
                "status": False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": list(set(duplicate_names)),
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count
        }, status=status.HTTP_200_OK)



class CivilIdNameCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
 
    def post(self, request):
        serializer = CivilIdNameSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Civil ID created successfully",
                "data": serializer.data
            })
 
        msg = " ".join([m for v in serializer.errors.values() for m in v])
        return Response({
            "statusCode": 400,
            "status": False,
            "message": msg
        }, status=status.HTTP_400_BAD_REQUEST)
 
 
class CivilIdNameListAPIView(APIView):
    def get(self, request):
        search = request.GET.get("search", "").strip()
        sort_by = request.GET.get("sortBy", "created_at")
        sort_order = request.GET.get("sortOrder", "desc")
 
        allowed_sort_fields = [
            "civil_id_name",
            "authority_full_name",
            "authority_short_name",
            "created_at",
        ]
 
        if sort_by not in allowed_sort_fields:
            sort_by = "created_at"
 
        if sort_order == "desc":
            sort_by = f"-{sort_by}"
 
        queryset = CivilIdName.objects.filter(is_deleted=False)
 
        if search:
            queryset = queryset.filter(
                Q(civil_id_name__icontains=search) |
                Q(authority_full_name__icontains=search) |
                Q(authority_short_name__icontains=search) |
                Q(description__icontains=search)
            )
 
        queryset = queryset.order_by(sort_by)
 
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
 
        serializer = CivilIdNameSerializer(result_page, many=True)
 
        return paginator.get_paginated_response(serializer.data)
 
 
class CivilIdNameRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
 
    def get(self, request, uuid):
        try:
            obj = CivilIdName.objects.get(uuid=uuid)
        except CivilIdName.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Civil ID not found",
                "data": None
            })
 
        serializer = CivilIdNameSerializer(obj)
 
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Civil ID retrieved successfully",
            "data": serializer.data
        })
 
 
class CivilIdNameUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
 
    def put(self, request, uuid):
        try:
            civil = CivilIdName.objects.get(uuid=uuid)
        except CivilIdName.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Civil ID not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)
 
        serializer = CivilIdNameSerializer(civil, data=request.data, partial=True)   # ✅ FIX HERE
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Civil ID updated successfully",
                "data": serializer.data
            })
 
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
 
 
class CivilIdNameDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
 
    def delete(self, request, uuid=None):
        ids = request.data.get("id", None)
 
        if uuid:
            try:
                CivilIdName.objects.get(uuid=uuid).delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "Civil ID deleted successfully",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
 
            except CivilIdName.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Civil ID not found",
                    "data": None
                })
 
        if ids == "all":
            count = CivilIdName.objects.count()
            CivilIdName.objects.all().delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} Civil ID(s) deleted",
                "data": None
            })
 
        if not ids or not isinstance(ids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Provide list of UUIDs in 'id' or use 'all'",
                "data": None
            })
 
        valid = []
        invalid = []
 
        for u in ids:
            try:
                valid.append(UUID(u))
            except:
                invalid.append(u)
 
        queryset = CivilIdName.objects.filter(uuid__in=valid)
        count = queryset.count()
        queryset.delete()
 
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} Civil ID(s) deleted",
            "data": {"invalid_uuids": invalid} if invalid else None
        })
 
 
 
 
 
class CivilIdNameExportAPIView(APIView):
    permission_classes = []  # Add IsAuthenticated if required
 
    def get(self, request):
        format_type = request.GET.get("format", "xlsx").lower()
        fields = request.GET.get("fields")
        uuids_param = request.GET.get("uuids", "")
 
        # Convert UUID strings to Python UUID objects
        uuids = []
        invalid_uuids = []
        for u in [u.strip() for u in uuids_param.split(",") if u]:
            try:
                uuids.append(UUID(u))
            except ValueError:
                invalid_uuids.append(u)
 
        field_header_map = {
            "uuid": "UUID",
            "civil_id_name": "Civil ID Name",
            "authority_full_name": "Authority Full Name",
            "authority_short_name": "Authority Short Name",
            "valid_type": "Civil ID Valid Upto",
            "valid_date":"Civil ID Valid Date",
            "valid_duration_value": "Civil ID Valid Duration Value",
            "valid_duration_unit": "Civil ID Valid Duration Unit",
            "description": "Description",
            "created_at": "Created On",
            "updated_at": "Modified On",
        }
 
        field_list = [f.strip() for f in fields.split(",")] if fields else list(field_header_map.keys())
 
        queryset = CivilIdName.objects.all()
 
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
 
        queryset = queryset.order_by("-created_at")
 
        # Handle empty queryset
        if not queryset.exists():
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No Civil ID records found for export"
            }, status=404)
 
        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = "CivilIdName"
 
        for obj in queryset:
            row = []
            for field in field_list:
                value = getattr(obj, field, "")
 
                # display choice labels
                if field == "valid_type" and obj.valid_type:
                    value = obj.get_valid_type_display()
                
 
                if field == "valid_duration_unit" and obj.valid_duration_unit:
                    value = obj.get_valid_duration_unit_display()
 
                # Format date
                if field in ["created_at", "updated_at"] and value:
                    value = timezone.localtime(value).strftime("%d-%m-%Y %I:%M:%S %p")
                
                if field == "valid_date" and value:
                    value = value.strftime("%d-%m-%Y")
 
                row.append(value if value is not None else "")
            dataset.append(row)
 
        if format_type == "csv":
            file_data = dataset.export("csv")
            content_type = "text/csv"
            file_name = "civil_id_names.csv"
        else:
            file_data = io.BytesIO(dataset.export("xlsx"))
            content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            file_name = "civil_id_names.xlsx"
 
        response = HttpResponse(
            file_data if format_type == "csv" else file_data.getvalue(),
            content_type=content_type
        )
        response["Content-Disposition"] = f'attachment; filename="{file_name}"'
        return response
 
 
class CivilIdNameImportAPIView(APIView):
    def post(self, request):
        file = request.FILES.get("file")
        sheet_name = request.data.get("sheet_name")
 
        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)
 
        format_type = file.name.split(".")[-1].lower()
        duplicate_names = []
        skipped_rows = []

        required_headers = {"civil id name"}
        optional_headers = {
            "authority full name",
            "authority short name",
            "civil id valid type",
            "civil id valid date",
            "civil id valid duration value",
            "civil id valid duration unit",
            "description"
        }

        try:
            data = []
            headers = []

            # ---------- XLSX ----------
            if format_type == "xlsx":
                import openpyxl
                wb = openpyxl.load_workbook(file, read_only=True)

                if not sheet_name:
                    return Response(
                        {"error": "Provide sheet_name", "available_sheets": wb.sheetnames},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                if sheet_name not in wb.sheetnames:
                    return Response(
                        {"error": f'Sheet "{sheet_name}" not found', "available_sheets": wb.sheetnames},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response(
                        {"statusCode": 400, "status": False, "message": "Sheet is empty"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                headers = []
                for cell in next(ws.iter_rows(min_row=1, max_row=1)):
                    header = str(cell.value).strip().lower().replace("_", " ").replace("-", " ") if cell.value else ""
                    headers.append(header)
                if not required_headers.issubset(set(headers)):
                    missing = required_headers - set(headers)
                    return Response(
                        {"statusCode": 400, "status": False, "message": f"Missing required headers: {missing}"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                for row in ws.iter_rows(min_row=2, values_only=True):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    data.append(row_dict)

            # ---------- CSV ----------
            elif format_type == "csv":
                decoded_file = file.read().decode("utf-8")
                dataset = Dataset()
                dataset.load(decoded_file, format="csv")

                for row in dataset.dict:
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    if not required_headers.issubset(set(row_lower.keys())):
                        missing = required_headers - set(row_lower.keys())
                        return Response(
                            {"statusCode": 400, "status": False, "message": f"Missing required headers: {missing}"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    data.append(row_lower)

            else:
                return Response(
                    {"statusCode": 400, "status": False, "error": "Unsupported file format"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # ---------- Import Data ----------
            ALLOWED_VALID_TYPES = ["Permanent", "Valid Upto", "Date"]
            ALLOWED_VALID_UNITS = ["Months", "Weeks", "Years"]
            imported_count = 0

            for row in reversed(data):  # Import in reversed order
                civil_id_name = str(row.get("civil id name")).strip() if row.get("civil id name") else None
                authority_full_name = str(row.get("authority full name")).strip() if row.get("authority full name") else None
                authority_short_name = str(row.get("authority short name")).strip() if row.get("authority short name") else ""
                valid_type = str(row.get("civil id valid upto")).strip() if row.get("civil id valid upto") else None
                valid_duration_value = row.get("civil id valid duration value") or None
                valid_duration_unit = str(row.get("civil id valid duration unit")).strip() if row.get("civil id valid duration unit") else None
                description = str(row.get("description")).strip() if row.get("description") else ""
                valid_date_raw = row.get('civil id valid date')
                valid_date = None
                if valid_date_raw:
                    if isinstance(valid_date_raw, datetime):
                        valid_date = valid_date_raw.date()
                    else:
                        date_str = str(valid_date_raw).strip()
                        for fmt in ("%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d"):
                            try:
                                valid_date = datetime.strptime(date_str, fmt).date()
                                break
                            except ValueError:
                                continue
                        if not valid_date:
                            skipped_rows.append({
                                "Civil ID Name": civil_id_name or " ",
                                'Reason': f"Invalid date format '{valid_date_raw}'. Expected formats: dd-mm-yyyy, dd/mm/yyyy"
                            })
                            continue
                if not civil_id_name:
                    skipped_rows.append({
                        "Civil ID Name": civil_id_name or "Unknown",
                        "Reason": f"Missing required fields. Required: {', '.join(required_headers)}"
                    })
                    continue

                if valid_type and valid_type not in ALLOWED_VALID_TYPES:
                    skipped_rows.append({
                        "Civil ID Name": civil_id_name,
                        "Reason": f"Invalid valid_type='{valid_type}'. Allowed: {ALLOWED_VALID_TYPES}"
                    })
                    continue

                if valid_type == "Valid Upto":
                    # Duration value check
                    if valid_duration_value is None:
                        skipped_rows.append({
                            "Civil ID Name": civil_id_name,
                            "Reason": "Valid Upto type requires numeric 'valid duration value' and 'valid duration unit'"
                        })
                        continue
                    try:
                        valid_duration_value = int(valid_duration_value)
                        if valid_duration_value <= 0:
                            raise ValueError
                    except (ValueError, TypeError):
                        skipped_rows.append({
                            "Civil ID Name": civil_id_name,
                            "Reason": "Invalid 'valid duration value'. Use positive numeric value."
                        })
                        continue
                    # Unit check
                    if not valid_duration_unit or valid_duration_unit not in ALLOWED_VALID_UNITS:
                        skipped_rows.append({
                            "Civil ID Name": civil_id_name,
                            "Reason": f"Invalid 'valid duration unit'. Allowed: {ALLOWED_VALID_UNITS}"
                        })
                        continue
                elif valid_type == 'Date' and not valid_date:
                    skipped_rows.append({
                        "Civil ID Name": civil_id_name,
                        'Reason': "Civil ID Valid Date  requires valid_date formate DD-MM_YYY"
                    })
                    continue

                if valid_duration_unit and valid_duration_unit not in ALLOWED_VALID_UNITS:
                    skipped_rows.append({
                        "Civil ID Name": civil_id_name,
                        'Reason': f"Invalid 'Civil ID Valid Unit'='{valid_duration_unit}'. Please use one of: Months, Weeks, Years"
                    })
                    continue


                existing = CivilIdName.objects.filter(
                    civil_id_name__iexact=civil_id_name
                ).first()

                if existing:
                    if not getattr(existing, "is_deleted", False):
                        duplicate_names.append(civil_id_name)
                        continue
                    else:
                        # Restore soft-deleted record
                        existing.authority_full_name = authority_full_name
                        existing.authority_short_name = authority_short_name
                        existing.valid_type = valid_type
                        existing.valid_duration_value = valid_duration_value
                        existing.valid_duration_unit = valid_duration_unit
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                        continue

                # Create new entry
                try:
                    CivilIdName.objects.create(
                        civil_id_name=civil_id_name,
                        authority_full_name=authority_full_name,
                        authority_short_name=authority_short_name,
                        valid_type=valid_type,
                        valid_duration_value=valid_duration_value,
                        valid_duration_unit=valid_duration_unit,
                        description=description,
                        is_deleted=False
                    )
                    imported_count += 1
                except IntegrityError:
                    duplicate_names.append(civil_id_name)

        except Exception as e:
            return Response({"statusCode": 400, "status": False, "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": list(set(duplicate_names)),
            "skipped_rows": skipped_rows,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count
        }, status=status.HTTP_200_OK)






class DepartmentListAPIView(APIView):
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'updated_at')
        sort_order = request.GET.get('sortOrder', 'desc')  

        allowed_sort_fields = ['name', 'description', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        # Apply descending order for 'desc'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = Department.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )

        # Apply dynamic ordering
        queryset = queryset.order_by(sort_by)

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = DepartmentSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)


class DepartmentCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        name = request.data.get("name").strip()


        existing = Department.objects.filter(name__iexact=name, is_deleted=False).first()

        if existing:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Department with this name already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        # If no active department exists, create new (even if soft-deleted exists)
        serializer = DepartmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Department created successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        else:
            errors = serializer.errors
            messages = []
            for field, msgs in errors.items():
                messages.extend(msgs)
            message_text = " ".join(messages)

            return Response({
                "statusCode": 400,
                "status": False,
                "message": message_text,
            }, status=status.HTTP_400_BAD_REQUEST)

class DepartmentRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    def get(self, request, uuid):
        try:
            department = Department.objects.get(uuid=uuid, is_deleted=False)
        except Department.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Department not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = DepartmentSerializer(department)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Department retrieved successfully",
            "data": serializer.data
        })


class DepartmentUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    def put(self, request, uuid):
        try:
            department = Department.objects.get(uuid=uuid, is_deleted=False)
        except Department.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Department not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = DepartmentSerializer(department, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Department updated successfully",
                "data": serializer.data
            })


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


class DepartmentDeleteAPIView(APIView): 
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get('id', None)

        # Single delete via URL parameter
        if uuid:
            try:
                department = Department.objects.get(uuid=uuid)
                department.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "Department permanently deleted.",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            except Department.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Department not found.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        # Delete all departments
        if ids == "all":
            departments = Department.objects.all()
            count = departments.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No departments found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
            departments.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} department(s) permanently deleted.",
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
        departments = Department.objects.filter(uuid__in=valid_uuids)
        count = departments.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching departments found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_404_NOT_FOUND)

        departments.delete()

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} department(s) permanently deleted.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        }, status=status.HTTP_200_OK)


class DepartmentExportAPIView(APIView):
    

    def get(self, request):
        # --- Get query params ---
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')  # comma-separated fields
        uuids_param = request.GET.get('uuids', '')  # comma-separated UUIDs

        uuids = [u.strip() for u in uuids_param.split(',') if u]

        # --- Field to header mapping ---
        field_header_map = {
            'uuid': 'UUID',
            'name': 'Department',  # Custom header
            'description': 'Description',
            'is_deleted': 'Deleted',
            'updated_at': 'Modified On',
            
        }

        # --- Determine which fields to export ---
        if fields:
            field_list = [f.strip() for f in fields.split(',')]
        else:
            field_list = list(field_header_map.keys())

        # --- Fetch queryset ---
        queryset = Department.objects.filter(is_deleted=False) 
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')


        # --- Prepare dataset ---
        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'Department'

        for dept in queryset:
            row = []
            for field in field_list:
                value = getattr(dept, field, '')

                if field in ['created_at', 'updated_at'] and value:
                    # Convert the stored UTC datetime to IST and format it
                    value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
                elif isinstance(value, bool):
                    value = int(value)

                row.append(value if value is not None else '')
            dataset.append(row)
        # --- Export data ---
        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'departments.csv'
        else:
            # XLSX export with BytesIO
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'departments.xlsx'

        # --- Return response ---
        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response

class DepartmentImportAPIView(APIView):
    
    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicate_names = []

        # Define required and optional headers
        required_headers = {'department'}       # must be present
        optional_headers = {'description'}      # optional

        try:
            data = []
            headers = []

            # ---------- XLSX Handling ----------
            if format_type == 'xlsx':
                import openpyxl
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                # Validate sheet name
                if not sheet_name:
                    return Response({
                        'error': 'Please provide sheet_name',
                        'available_sheets': available_sheets
                    }, status=status.HTTP_400_BAD_REQUEST)

                if sheet_name not in available_sheets:
                    return Response({
                        'error': f'Sheet "{sheet_name}" not found in uploaded file',
                        'available_sheets': available_sheets
                    }, status=status.HTTP_400_BAD_REQUEST)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'The uploaded XLSX file (sheet: "{sheet_name}") is empty. Please provide at least one data row.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]

                # Validate only required headers
                if not required_headers.issubset(set(headers)):
                    return Response({
                        "statusCode": 400,
                        "status": True,
                        'message': f'Missing required headers. Required: {required_headers}, Found: {set(headers)}'
                    }, status=status.HTTP_400_BAD_REQUEST)

                for row in ws.iter_rows(min_row=2, values_only=True):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    data.append(row_dict)

                if not data:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'The uploaded XLSX file (sheet: "{sheet_name}") is empty. Please provide at least one data row.'
                    }, status=status.HTTP_400_BAD_REQUEST)

            # ---------- CSV Handling ----------
            elif format_type == 'csv':
                decoded_file = file.read().decode('utf-8')
                dataset = Dataset()
                dataset.load(decoded_file, format='csv')

                for row in dataset.dict:
                    row_lower = {k.strip().lower(): v for k, v in row.items()}

                    # Validate only required headers
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({
                            "statusCode": 400,
                            "status": True,
                            "message": (
                                f'Missing required headers. Required: {", ".join(required_headers)}. '
                                f'Found headers in the file: {", ".join(row_lower.keys())}.'
                            )
                        }, status=status.HTTP_400_BAD_REQUEST)

                    data.append(row_lower)
                
                if not data:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": "The uploaded CSV file is empty. Please provide at least one data row."
                    }, status=status.HTTP_400_BAD_REQUEST)

            else:
                return Response({
                    "statusCode": 400,
                    "status": True,
                    'error': 'Unsupported file format. Use .xlsx or .csv'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            imported_count = 0

            # ---------- Import Rows ----------
            for row in  reversed(data):
                name = str(row.get('department')).strip() if row.get('department') else None
                description = str(row.get('description')).strip() if row.get('description') else ''

                if not name:
                    continue  # skip rows without department name

                existing = Department.objects.filter(name__iexact=name).first()

                if existing:
                    # Skip if not deleted
                    if not existing.is_deleted:
                        duplicate_names.append(name)
                        continue
                    else:
                        # Reactivate if previously deleted
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    Department.objects.create(
                        name=name,
                        description=description,
                        is_deleted=False
                    )
                    imported_count += 1

        except Exception as e:
            return Response({
                "statusCode": 400,
                "status": True,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": list(set(duplicate_names)),
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count
        }, status=status.HTTP_200_OK)






# -----------------------employeeType---------------------------------
class EmployeeTypeListAPIView(APIView):    

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'updated_at')
        sort_order = request.GET.get('sortOrder', 'desc')  # default to newest first

        allowed_sort_fields = ['name', 'description', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        # Apply descending order for 'desc'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = EmployeeType.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )

        queryset = queryset.order_by(sort_by)

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = EmployeeTypeSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)


class EmployeeTypeCreateAPIView(APIView):
    def post(self, request):
        serializer = EmployeeTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Employee type created successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        else:

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


class EmployeeTypeRetrieveAPIView(APIView):
    def get(self, request, uuid):
        try:
            emp_type = EmployeeType.objects.get(uuid=uuid, is_deleted=False)
        except EmployeeType.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Employee type not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = EmployeeTypeSerializer(emp_type)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Employee type retrieved successfully",
            "data": serializer.data
        })


class EmployeeTypeUpdateAPIView(APIView):
    def put(self, request, uuid):
        try:
            emp_type = EmployeeType.objects.get(uuid=uuid, is_deleted=False)
        except EmployeeType.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Employee type not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = EmployeeTypeSerializer(emp_type, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Employee type updated successfully",
                "data": serializer.data
            })


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


class EmployeeTypeDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        uuids = request.data.get('id', None)

        # Single delete via URL parameter
        if uuid:
            try:
                emp_type = EmployeeType.objects.get(uuid=uuid, is_deleted=False)
                emp_type.is_deleted = True
                emp_type.save()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "Employee type deleted successfully",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            except EmployeeType.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Employee type not found",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        # Delete all if "all" is sent
        if uuids == "all":
            emp_types = EmployeeType.objects.filter(is_deleted=False)
            count = emp_types.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No employee types found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
            emp_types.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} employee type(s) deleted successfully.",
                "data": None
            }, status=status.HTTP_200_OK)

        # Validate bulk UUIDs
        if not uuids or not isinstance(uuids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide a list of UUIDs in 'id' field or 'all'.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        valid_uuids = []
        invalid_uuids = []
        for u in uuids:
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
        emp_types = EmployeeType.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = emp_types.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching employee types found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_404_NOT_FOUND)

        emp_types.delete()

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} employee type(s) deleted successfully.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        }, status=status.HTTP_200_OK)
    

class EmployeeTypeExportAPIView(APIView):
    # permission_classes = [IsAuthenticated]  

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')  
        uuids_param = request.GET.get('uuids', '') 


        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'name': 'Employee Type',  
            'description': 'Description',
            'is_deleted': 'Deleted',
            'updated_at': 'Modified On',
            
        }


        if fields:
            field_list = [f.strip() for f in fields.split(',')]
        else:
            field_list = list(field_header_map.keys())

        queryset = EmployeeType.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'EmployeeType'

        for dept in queryset:
            row = []
            for field in field_list:
                value = getattr(dept, field, '')

                if field in ['created_at', 'updated_at'] and value:
                    # Convert the stored UTC datetime to IST and format it
                    value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
                elif isinstance(value, bool):
                    value = int(value)

                row.append(value if value is not None else '')
            dataset.append(row)

        # --- Export data ---
        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'employeetype.csv'
        else:
            # XLSX export with BytesIO
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'employeetype.xlsx'

        # --- Return response ---
        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


class EmployeeTypeImportAPIView(APIView):
    
    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicate_names = []

        # Define required and optional headers
        required_headers = {'employee type'}   # mandatory
        optional_headers = {'description'}     # optional

        try:
            data = []
            headers = []

            # ---------- XLSX Handling ----------
            if format_type == 'xlsx':
                import openpyxl
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                # Validate sheet name
                if not sheet_name:
                    return Response({
                        'error': 'Please provide sheet_name',
                        'available_sheets': available_sheets
                    }, status=status.HTTP_400_BAD_REQUEST)

                if sheet_name not in available_sheets:
                    return Response({
                        'error': f'Sheet "{sheet_name}" not found in uploaded file',
                        'available_sheets': available_sheets
                    }, status=status.HTTP_400_BAD_REQUEST)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'The uploaded XLSX file (sheet: "{sheet_name}") is empty. Please provide at least one data row.'
                    }, status=status.HTTP_400_BAD_REQUEST)

                headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]

                # Validate only required headers
                if not required_headers.issubset(set(headers)):
                    return Response({
                        "statusCode": 400,
                        "status": True,
                        'message': f'Missing required headers. Required: {required_headers}, Found: {set(headers)}'
                    }, status=status.HTTP_400_BAD_REQUEST)

                for row in ws.iter_rows(min_row=2, values_only=True):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    data.append(row_dict)

                if not data:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'The uploaded XLSX file (sheet: "{sheet_name}") is empty. Please provide at least one data row.'
                    }, status=status.HTTP_400_BAD_REQUEST)

            # ---------- CSV Handling ----------
            elif format_type == 'csv':
                decoded_file = file.read().decode('utf-8')
                dataset = Dataset()
                dataset.load(decoded_file, format='csv')

                for row in dataset.dict:
                    row_lower = {k.strip().lower(): v for k, v in row.items()}

                    # Validate only required headers
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({
                            "statusCode": 400,
                            "status": True,
                            "message": (
                                f'Missing required headers. Required: {", ".join(required_headers)}. '
                                f'Found headers in the file: {", ".join(row_lower.keys())}.'
                            )
                        }, status=status.HTTP_400_BAD_REQUEST)

                    if not any(row_lower.values()):
                        continue
                    data.append(row_lower)

                if not data:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": "The uploaded CSV file is empty. Please provide at least one data row."
                    }, status=status.HTTP_400_BAD_REQUEST)

            else:
                return Response({
                    "statusCode": 400,
                    "status": True,
                    'error': 'Unsupported file format. Use .xlsx or .csv'
                }, status=status.HTTP_400_BAD_REQUEST)

            imported_count = 0
            # ---------- Import Rows ----------
            for row in  reversed(data):
                name = str(row.get('employee type')).strip() if row.get('employee type') else None
                description = str(row.get('description')).strip() if row.get('description') else ''  # optional

                if not name:
                    continue

                existing = EmployeeType.objects.filter(name__iexact=name).first()

                if existing:
                    if existing.is_deleted:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                    else:
                        duplicate_names.append(name)
                        continue
                else:
                    EmployeeType.objects.create(
                        name=name,
                        description=description,
                        is_deleted=False
                    )
                    imported_count += 1

        except Exception as e:
            return Response({
                "statusCode": 400,
                "status": True,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": list(set(duplicate_names)),
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count
        }, status=status.HTTP_200_OK)


#--------------------------companyType------------------------
class CompanyTypeListAPIView(APIView):    
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'updated_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['name', 'description', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        # Apply descending order for 'desc'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = CompanyType.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )

        queryset = queryset.order_by(sort_by)

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = CompanyTypeSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)

class CompanyTypeCreateAPIView(APIView):
    def post(self, request):
        serializer = CompanyTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Company type created successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

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

class CompanyTypeDetailAPIView(APIView):
    def get(self, request, uuid):
        try:
            company_type = CompanyType.objects.get(uuid=uuid, is_deleted=False)
        except CompanyType.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Company type not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = CompanyTypeSerializer(company_type)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Company type retrieved successfully",
            "data": serializer.data
        })

class CompanyTypeUpdateAPIView(APIView):
    def put(self, request, uuid):
        try:
            company_type = CompanyType.objects.get(uuid=uuid, is_deleted=False)
        except CompanyType.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Company type not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = CompanyTypeSerializer(company_type, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Company type updated successfully",
                "data": serializer.data
            })

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


class CompanyTypeDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get('id', None)

        #  Case 1: Single delete (UUID passed in URL)
        if uuid:
            try:
                company_type = CompanyType.objects.get(uuid=uuid, is_deleted=False)
                company_type.is_deleted = True
                company_type.save()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "Company type deleted successfully",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            except CompanyType.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Company type not found",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        #  Case 2: Delete all
        if ids == "all":
            company_types = CompanyType.objects.filter(is_deleted=False)
            count = company_types.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No company types found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
            company_types.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} company type(s) deleted successfully.",
                "data": None
            }, status=status.HTTP_200_OK)

        #  Case 3: Multiple delete (UUIDs in request body)
        if not ids or not isinstance(ids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide a list of UUIDs in 'id' field or 'all'.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate UUIDs
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

        # Fetch company types that exist and are not deleted
        company_types = CompanyType.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = company_types.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching company types found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_404_NOT_FOUND)

        # Soft delete
        company_types.delete()

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} company type(s) deleted successfully.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        }, status=status.HTTP_200_OK)
    

class CompanyTypeExportAPIView(APIView):
    # permission_classes = [IsAuthenticated]  
    def get(self, request):

        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')  # comma-separated fields
        uuids_param = request.GET.get('uuids', '')  # comma-separated UUIDs

        uuids = [u.strip() for u in uuids_param.split(',') if u]

        # --- Field to header mapping ---
        field_header_map = {
            'uuid': 'UUID',
            'name': 'Company Type',  # Custom header
            'description': 'Description',
            'is_deleted': 'Deleted',
            'updated_at': 'Modified On',
            
        }

        # --- Determine which fields to export ---
        if fields:
            field_list = [f.strip() for f in fields.split(',')]
        else:
            field_list = list(field_header_map.keys())

        queryset = CompanyType.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')


        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        
        dataset.title = 'CompanyType'
        

        for dept in queryset:
            row = []
            for field in field_list:
                value = getattr(dept, field, '')

                if field in ['created_at', 'updated_at'] and value:
                    # Convert the stored UTC datetime to IST and format it
                    value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
                elif isinstance(value, bool):
                    value = int(value)

                row.append(value if value is not None else '')
            dataset.append(row)

        # --- Export data ---
        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'CompanyType.csv'
        else:
            # XLSX export with BytesIO
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'CompanyType.xlsx'

        # --- Return response ---
        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response

class CompanyTypeImportAPIView(APIView):
    """
    API to import Company Types from CSV or XLSX.
    """
    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicate_names = []

        # Define required and optional headers
        required_headers = {'company type'}   # mandatory
        optional_headers = {'description'}    # optional

        try:
            data = []

            # ---------- XLSX Handling ----------
            if format_type == 'xlsx':
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({
                        'error': 'Please provide sheet_name',
                        'available_sheets': available_sheets
                    }, status=status.HTTP_400_BAD_REQUEST)

                if sheet_name not in available_sheets:
                    return Response({
                        'error': f'Sheet "{sheet_name}" not found in uploaded file',
                        'available_sheets': available_sheets
                    }, status=status.HTTP_400_BAD_REQUEST)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'The uploaded XLSX file (sheet: "{sheet_name}") is empty. Please provide at least one data row.'
                    }, status=status.HTTP_400_BAD_REQUEST)

                headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]

                # Validate required headers only
                if not required_headers.issubset(set(headers)):
                    return Response({
                        "statusCode": 400,
                        "status": True,
                        'message': f'Missing required headers. Required: {required_headers}, Found: {set(headers)}'
                    }, status=status.HTTP_400_BAD_REQUEST)

                for row in ws.iter_rows(min_row=2, values_only=True):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    data.append(row_dict)

                if not data:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'The uploaded XLSX file (sheet: "{sheet_name}") is empty. Please provide at least one data row.'
                    }, status=status.HTTP_400_BAD_REQUEST)

            # ---------- CSV Handling ----------
            elif format_type == 'csv':
                decoded_file = file.read().decode('utf-8')
                dataset = Dataset()
                dataset.load(decoded_file, format='csv')

                for row in dataset.dict:
                    row_lower = {k.strip().lower(): v for k, v in row.items()}

                    # Validate only required headers
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({
                            "statusCode": 400,
                            "status": True,
                            "message": f'Missing required headers. Required: {required_headers}. Found: {set(row_lower.keys())}.'
                        }, status=status.HTTP_400_BAD_REQUEST)

                    if not any(row_lower.values()):
                        continue
                    data.append(row_lower)

            else:
                return Response({'error': 'Unsupported file format. Use .xlsx or .csv'}, status=status.HTTP_400_BAD_REQUEST)

            # ---------- Process Each Row ----------
            for row in  reversed(data):
                name = str(row.get('company type')).strip() if row.get('company type') else None
                description = str(row.get('description')).strip() if row.get('description') else ''  
                if not name:
                    continue

                existing = CompanyType.objects.filter(name__iexact=name).first()

                if existing:
                    if existing.is_deleted:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                    else:
                        duplicate_names.append(name)
                        continue
                else:
                    CompanyType.objects.create(
                        name=name,
                        description=description,
                        is_deleted=False
                    )

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": list(set(duplicate_names)),
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful"
        }, status=status.HTTP_200_OK)


class OwnershipTypeListAPIView(APIView):    
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'updated_at')
        sort_order = request.GET.get('sortOrder', 'desc')  # default to newest first

        allowed_sort_fields = ['name', 'description', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        # Apply descending order for 'desc'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = OwnershipType.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )

        queryset = queryset.order_by(sort_by)

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = OwnershipTypeSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)

class OwnershipTypeCreateAPIView(APIView):
    def post(self, request):
        serializer = OwnershipTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Ownership type created successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

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

class OwnershipTypeDetailAPIView(APIView):
    def get(self, request, uuid):
        try:
            ownership = OwnershipType.objects.get(uuid=uuid, is_deleted=False)
        except OwnershipType.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Ownership type not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = OwnershipTypeSerializer(ownership)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Ownership type retrieved successfully",
            "data": serializer.data
        })

class OwnershipTypeUpdateAPIView(APIView):
    def put(self, request, uuid):
        try:
            ownership = OwnershipType.objects.get(uuid=uuid, is_deleted=False)
        except OwnershipType.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Ownership type not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = OwnershipTypeSerializer(ownership, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Ownership type updated successfully",
                "data": serializer.data
            })

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

class OwnershipTypeDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get('id', [])

        #  Case 1: Single delete (UUID in URL)
        if uuid:
            try:
                ownership = OwnershipType.objects.get(uuid=uuid, is_deleted=False)
                ownership.delete()
               
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "Ownership type deleted successfully",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            except OwnershipType.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Ownership type not found",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
        
        if ids == "all":
            ownership = OwnershipType.objects.get(uuid=uuid, is_deleted=False)
            
            count = ownership.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No departments found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
            ownership.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} department(s) permanently deleted.",
                "data": None
            }, status=status.HTTP_200_OK)

        #  Case 2: Multiple delete (UUIDs in request body)
        if not ids or not isinstance(ids, list):
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Please provide a list of UUIDs in 'id' field or 'all'.",
                    "data": None
                }, status=status.HTTP_400_BAD_REQUEST)

        # Validate UUIDs
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

        # Fetch ownership types that exist and are not deleted
        ownerships = OwnershipType.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = ownerships.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching ownership types found.",
                "data": {"invalid_uuids": invalid_uuids}
            }, status=status.HTTP_404_NOT_FOUND)

        # Soft delete
        ownerships.delete()

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} ownership type(s) deleted successfully.",
            "data": {"invalid_uuids": invalid_uuids}
        }, status=status.HTTP_200_OK)


class OwnershipTypeExportAPIView(APIView):
    """
    Export OwnershipType data to XLSX or CSV with company_type info.
    """

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')  # comma-separated fields
        uuids_param = request.GET.get('uuids', '')  # comma-separated UUIDs
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'company_type_name': 'Company Type',
            'name': 'Ownership Type',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'created_at': 'Created On',
            'updated_at': 'Modified On',
        }

        # Determine fields to export
        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())

        queryset = OwnershipType.objects.all()
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'OwnershipType'

        for obj in queryset:
            row = []
            for field in field_list:
                if field == 'company_type_name':
                    value = obj.company_type.name if obj.company_type else ''
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
            file_name = 'ownership_types.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'ownership_types.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


    class OwnershipTypeImportAPIView(APIView):
        """
        Import OwnershipType data from XLSX or CSV.
        Matches `company_type` by name instead of ID.
        """

        def post(self, request):
            file = request.FILES.get('file')
            sheet_name = request.data.get('sheet_name')
            if not file:
                return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

            format_type = file.name.split('.')[-1].lower()
            duplicate_names = []
            required_headers = {'ownership type'}  # Ownership type name is required
            optional_headers = {'description', 'company type'}  # company_type optional

            try:
                data = []

                # XLSX
                if format_type == 'xlsx':
                    import openpyxl
                    wb = openpyxl.load_workbook(file, read_only=True)
                    available_sheets = wb.sheetnames

                    if not sheet_name:
                        return Response({'error': 'Please provide sheet_name', 'available_sheets': available_sheets},
                                        status=status.HTTP_400_BAD_REQUEST)
                    if sheet_name not in available_sheets:
                        return Response({'error': f'Sheet "{sheet_name}" not found', 'available_sheets': available_sheets},
                                        status=status.HTTP_400_BAD_REQUEST)

                    ws = wb[sheet_name]
                    headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                    if not required_headers.issubset(set(headers)):
                        return Response({'statusCode': 400, 'status': True,
                                        'message': f'Missing required headers. Required: {required_headers}, Found: {set(headers)}'},
                                        status=status.HTTP_400_BAD_REQUEST)

                    for row in ws.iter_rows(min_row=2, values_only=True):
                        if not any(row):
                            continue
                        row_dict = dict(zip(headers, row))
                        data.append(row_dict)

                # CSV
                elif format_type == 'csv':
                    decoded_file = file.read().decode('utf-8')
                    dataset = Dataset()
                    dataset.load(decoded_file, format='csv')
                    for row in dataset.dict:
                        row_lower = {k.strip().lower(): v for k, v in row.items()}
                        if not required_headers.issubset(set(row_lower.keys())):
                            return Response({'statusCode': 400, 'status': True,
                                            'message': f'Missing required headers. Required: {", ".join(required_headers)}. Found headers: {", ".join(row_lower.keys())}'},
                                            status=status.HTTP_400_BAD_REQUEST)
                        data.append(row_lower)
                else:
                    return Response({'statusCode': 400, 'status': True, 'error': 'Unsupported file format. Use .xlsx or .csv'},
                                    status=status.HTTP_400_BAD_REQUEST)

                imported_count = 0
                for row in  reversed(data):
                    name = str(row.get('ownership  type')).strip() if row.get('ownership type') else None
                    description = str(row.get('description')).strip() if row.get('description') else ''
                    company_type_name = str(row.get('company type')).strip() if row.get('company type') else None

                    if not name:
                        continue

                    
                    company_type = None
                    if company_type_name:
                        company_type = CompanyType.objects.filter(name__iexact=company_type_name).first()

                    existing = OwnershipType.objects.filter(name__iexact=name).first()
                    if existing:
                        if not existing.is_deleted:
                            duplicate_names.append(name)
                            continue
                        else:
                            existing.description = description
                            existing.company_type = company_type
                            existing.is_deleted = False
                            existing.save()
                            imported_count += 1
                    else:
                        OwnershipType.objects.create(
                            name=name,
                            description=description,
                            company_type=company_type,
                            is_deleted=False
                        )
                        imported_count += 1

            except Exception as e:
                return Response({'statusCode': 400, 'status': True, 'message': str(e)},
                                status=status.HTTP_400_BAD_REQUEST)

            return Response({
                'statusCode': 200,
                'status': True,
                'duplicates': list(set(duplicate_names)),
                'message': f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
                'imported_count': imported_count
            }, status=status.HTTP_200_OK)


class OwnershipTypeImportAPIView(APIView):
    
    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')
        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicate_names = []
        required_headers = {'ownership type'}  # Ownership type name is required
        optional_headers = {'description', 'company type'}  # optional fields

        try:
            data = []

            # XLSX import
            if format_type == 'xlsx':
                import openpyxl
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({'error': 'Please provide sheet_name', 'available_sheets': available_sheets},
                                    status=status.HTTP_400_BAD_REQUEST)
                if sheet_name not in available_sheets:
                    return Response({'error': f'Sheet "{sheet_name}" not found', 'available_sheets': available_sheets},
                                    status=status.HTTP_400_BAD_REQUEST)

                ws = wb[sheet_name]
                headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                if not required_headers.issubset(set(headers)):
                    return Response({'statusCode': 400, 'status': False,
                                     'message': f'Missing required headers. Required: {required_headers}, Found: {set(headers)}'},
                                    status=status.HTTP_400_BAD_REQUEST)

                for row in ws.iter_rows(min_row=2, values_only=True):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    data.append(row_dict)

            # CSV import
            elif format_type == 'csv':
                decoded_file = file.read().decode('utf-8')
                dataset = Dataset()
                dataset.load(decoded_file, format='csv')
                for row in dataset.dict:
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({'statusCode': 400, 'status': False,
                                         'message': f'Missing required headers. Required: {", ".join(required_headers)}. Found: {", ".join(row_lower.keys())}'},
                                        status=status.HTTP_400_BAD_REQUEST)
                    data.append(row_lower)
            else:
                return Response({'statusCode': 400, 'status': False, 'error': 'Unsupported file format. Use .xlsx or .csv'},
                                status=status.HTTP_400_BAD_REQUEST)

            # Import data
            imported_count = 0
            for row in  reversed(data):
                name = str(row.get('ownership type')).strip() if row.get('ownership type') else None
                description = str(row.get('description')).strip() if row.get('description') else ''
                company_type_name = str(row.get('company type')).strip() if row.get('company type') else None

                if not name:
                    continue

                # Match company_type by name
                company_type = None
                if company_type_name:
                    company_type = CompanyType.objects.filter(name__iexact=company_type_name).first()

                existing = OwnershipType.objects.filter(name__iexact=name).first()
                if existing:
                    if not existing.is_deleted:
                        duplicate_names.append(name)
                        continue
                    else:
                        existing.description = description
                        existing.company_type = company_type
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    OwnershipType.objects.create(
                        name=name,
                        description=description,
                        company_type=company_type,
                        is_deleted=False
                    )
                    imported_count += 1

        except Exception as e:
            return Response({'statusCode': 400, 'status': False, 'message': str(e)},
                            status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'statusCode': 200,
            'status': True,
            'duplicates': list(set(duplicate_names)),
            'message': f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            'imported_count': imported_count
        }, status=status.HTTP_200_OK)


#-------------------------stakeholder----------------------------

class StakeholderCategoryCreateAPIView(APIView):
    def post(self, request):
        serializer = StakeholderCategorySerializer(data=request.data)
        if serializer.is_valid():
            if StakeholderCategory.objects.filter(name=serializer.validated_data["name"],is_deleted=False).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Stakeholder Category with this name already exists"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Stakeholder Category created successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        

        return Response({
            "statusCode": 400,
            "status": False,
            "message": next(iter(serializer.errors.values()))[0]
        }, status=status.HTTP_400_BAD_REQUEST)


class StakeholderCategoryListAPIView(APIView):    
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'updated_at')
        sort_order = request.GET.get('sortOrder', 'desc')  # default to newest first

        allowed_sort_fields = ['name', 'description', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        # Apply descending order for 'desc'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = StakeholderCategory.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )

        queryset = queryset.order_by(sort_by)

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = StakeholderCategorySerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)



class StakeholderCategoryDetailAPIView(APIView):
    def get(self, request, uuid):
        category = get_object_or_404(StakeholderCategory, uuid=uuid, is_deleted=False)
        serializer = StakeholderCategorySerializer(category)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Stakeholder Category retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class StakeholderCategoryUpdateAPIView(APIView):
    def put(self, request, uuid):
        category = get_object_or_404(StakeholderCategory, uuid=uuid, is_deleted=False)
        serializer = StakeholderCategorySerializer(category, data=request.data, partial=True)

        if serializer.is_valid():
            new_name = serializer.validated_data.get("name", category.name)
            if StakeholderCategory.objects.filter(name=new_name).exclude(uuid=uuid).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Stakeholder Category with this name already exists"
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Stakeholder Category updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "statusCode": 400,
            "status": False,
            "message": next(iter(serializer.errors.values()))[0]
        }, status=status.HTTP_400_BAD_REQUEST)


class StakeholderCategoryDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get('id', None)

        if not ids:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide 'id' field (UUID list or 'all').",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
    
        if ids == "all":
            Stakeholdercategory = StakeholderCategory.objects.filter(is_deleted=False)
            count = Stakeholdercategory.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No StakeholderCategory found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
            Stakeholdercategory.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} StakeholderCategory(s) deleted successfully.",
                "data": None
            }, status=status.HTTP_200_OK)

        # Otherwise, treat as list of UUIDs
        if not isinstance(ids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide a list of UUIDs in 'id' field or 'all'.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate UUIDs
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

        # Fetch departments that exist and are not deleted
        Stakeholdercategory = StakeholderCategory.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = Stakeholdercategory.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching StakeholderCategory found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_404_NOT_FOUND)

        # Soft delete
        Stakeholdercategory.delete()

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} Stakeholder(s) deleted successfully.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        }, status=status.HTTP_200_OK)


class StakeholderCategoryExportAPIView(APIView):
    # permission_classes = [IsAuthenticated]  # Uncomment and adjust as needed

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')  # comma-separated fields
        uuids_param = request.GET.get('uuids', '')  # comma-separated UUIDs

        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'name': 'Stakeholder Category', 
            'description': 'Description',
            'is_deleted': 'Deleted',
            'updated_at': 'Modified On',
        }
        
        # --- Determine which fields to export ---
        if fields:
            field_list = [f.strip() for f in fields.split(',')]
        else:
            field_list = list(field_header_map.keys())

        queryset = StakeholderCategory.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')


        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'StakeholderCategory'

        for dept in queryset:
            row = []
            for field in field_list:
                value = getattr(dept, field, '')

                if field in ['created_at', 'updated_at'] and value:
                    # Convert the stored UTC datetime to IST and format it
                    value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
                elif isinstance(value, bool):
                    value = int(value)

                row.append(value if value is not None else '')
            dataset.append(row)

        if format_type == 'xlsx':
            data = XLSX().export_data(dataset)
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'StakeholderCategory.xlsx'
        else:
            data = CSV().export_data(dataset)
            content_type = 'text/csv; charset=utf-8'
            file_name = 'StakeholderCategory.csv'

        response = HttpResponse(data, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response

class StakeholderCategoryImportAPIView(APIView):
    """
    API to import Stakeholder Categories from CSV or XLSX.
    Handles headers with spaces/capitalization, ignores extra columns,
    and handles duplicates/deleted records.
    """

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicate_names = []

        # Define required and optional headers
        required_headers = {'stakeholdercategory'}  # mandatory
        optional_headers = {'description'}          # optional

        # Normalize headers: keep only alphanumeric lowercase characters
        def normalize_header(h):
            if not h:
                return ''
            return ''.join(c for c in str(h).lower() if c.isalnum())

        try:
            data = []
            headers = []

            # ---------- XLSX Handling ----------
            if format_type == 'xlsx':
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({
                        'error': 'Please provide sheet_name',
                        'available_sheets': available_sheets
                    }, status=status.HTTP_400_BAD_REQUEST)

                if sheet_name not in available_sheets:
                    return Response({
                        'error': f'Sheet "{sheet_name}" not found in uploaded file',
                        'available_sheets': available_sheets
                    }, status=status.HTTP_400_BAD_REQUEST)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'The uploaded XLSX file (sheet: "{sheet_name}") is empty. Please provide at least one data row.'
                    }, status=status.HTTP_400_BAD_REQUEST)

                headers = [normalize_header(cell.value) for cell in next(ws.iter_rows(min_row=1, max_row=1))]

                # Validate only required headers
                if not required_headers.issubset(set(headers)):
                    return Response({
                        "statusCode": 400,
                        "status": True,
                        'message': f'Missing required headers. Required: {required_headers}, Found: {set(headers)}'
                    }, status=status.HTTP_400_BAD_REQUEST)

                for row in ws.iter_rows(min_row=2, values_only=True):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    data.append(row_dict)

                if not data:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'The uploaded XLSX file (sheet: "{sheet_name}") is empty. Please provide at least one data row.'
                    }, status=status.HTTP_400_BAD_REQUEST)

            # ---------- CSV Handling ----------
            elif format_type == 'csv':
                decoded_file = file.read().decode('utf-8')
                dataset = Dataset()
                dataset.load(decoded_file, format='csv')

                for row in dataset.dict:
                    row_lower = {normalize_header(k): v for k, v in row.items()}

                    # Validate only required headers
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({
                            "statusCode": 400,
                            "status": True,
                            "message": f'Missing required headers. Required: {required_headers}. Found: {set(row_lower.keys())}.'
                        }, status=status.HTTP_400_BAD_REQUEST)

                    if not any(row_lower.values()):
                        continue
                    data.append(row_lower)

                if not data:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": "The uploaded CSV file is empty. Please provide at least one data row."
                    }, status=status.HTTP_400_BAD_REQUEST)

            else:
                return Response({'error': 'Unsupported file format. Use .xlsx or .csv'}, status=status.HTTP_400_BAD_REQUEST)

            # ---------- Process Each Row ----------
            imported_count = 0
            for row in  reversed(data):
                name = str(row.get('stakeholdercategory')).strip() if row.get('stakeholdercategory') else None
                description = str(row.get('description')).strip() if row.get('description') else ''

                if not name:
                    continue

                existing = StakeholderCategory.objects.filter(name__iexact=name).first()

                if existing:
                    if existing.is_deleted:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                    else:
                        duplicate_names.append(name)
                        continue
                else:
                    StakeholderCategory.objects.create(
                        name=name,
                        description=description,
                        is_deleted=False
                    )
                    imported_count += 1

        except Exception as e:
            return Response({
                "statusCode": 400,
                "status": True,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": list(set(duplicate_names)),
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count
        }, status=status.HTTP_200_OK)




#-------------------------stakeholdertype-------------------------------
class StakeholderTypeCreateAPIView(APIView):
    def post(self, request):
        serializer = StakeholderTypeSerializer(data=request.data)
        if serializer.is_valid():
            if StakeholderType.objects.filter(name=serializer.validated_data["name"]).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Stakeholder Type with this name already exists"
                }, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Stakeholder Type created successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            "statusCode": 400,
            "status": False,
            "message": next(iter(serializer.errors.values()))[0]
        }, status=status.HTTP_400_BAD_REQUEST)



class StakeholderTypeListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'updated_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['name', 'description', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = StakeholderType.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )

        queryset = queryset.order_by(sort_by)

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = StakeholderTypeSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)

# ----------------- CREATE -----------------
class StakeholderTypeCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        name = request.data.get("name", "").strip()

        existing = StakeholderType.objects.filter(name__iexact=name, is_deleted=False).first()
        if existing:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "StakeholderType with this name already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = StakeholderTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "StakeholderType created successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        else:
            messages = [msg for msgs in serializer.errors.values() for msg in msgs]
            return Response({
                "statusCode": 400,
                "status": False,
                "message": " ".join(messages)
            }, status=status.HTTP_400_BAD_REQUEST)

# ----------------- RETRIEVE -----------------
class StakeholderTypeRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = StakeholderType.objects.get(uuid=uuid, is_deleted=False)
        except StakeholderType.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "StakeholderType not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = StakeholderTypeSerializer(obj)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "StakeholderType retrieved successfully",
            "data": serializer.data
        })

# ----------------- UPDATE -----------------
class StakeholderTypeUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = StakeholderType.objects.get(uuid=uuid, is_deleted=False)
        except StakeholderType.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "StakeholderType not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = StakeholderTypeSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "StakeholderType updated successfully",
                "data": serializer.data
            })

        messages = [msg for msgs in serializer.errors.values() for msg in msgs]
        return Response({
            "statusCode": 400,
            "status": False,
            "message": " ".join(messages),
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)

# ----------------- DELETE -----------------
class StakeholderTypeDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get('id', None)

        if uuid:
            try:
                obj = StakeholderType.objects.get(uuid=uuid)
                obj.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "StakeholderType permanently deleted.",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            except StakeholderType.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "StakeholderType not found.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        if ids == "all":
            count = StakeholderType.objects.all().count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No StakeholderTypes found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
            StakeholderType.objects.all().delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} StakeholderType(s) permanently deleted.",
                "data": None
            }, status=status.HTTP_200_OK)

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

        queryset = StakeholderType.objects.filter(uuid__in=valid_uuids)
        count = queryset.count()
        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching StakeholderTypes found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_404_NOT_FOUND)

        queryset.delete()
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} StakeholderType(s) permanently deleted.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        }, status=status.HTTP_200_OK)

# ----------------- EXPORT -----------------
class StakeholderTypeExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')  # comma-separated
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'name': 'Stakeholder Type',
            'description': 'Description',
            'category': 'Category UUID',
            'category_name': 'Stakeholder Category',
            'is_deleted': 'Deleted',
            'updated_at': 'Modified On',
            'created_at': 'Created On'
        }

        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())

        queryset = StakeholderType.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'StakeholderType'

        for obj in queryset:
            row = []
            for field in field_list:
                if field == 'category_name':
                    value = obj.category.name if obj.category else ''
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
            file_name = 'stakeholder_types.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'stakeholder_types.xlsx'

        response = HttpResponse(file_data if format_type == 'csv' else file_data.getvalue(), content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response

# ----------------- IMPORT -----------------
class StakeholderTypeImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicate_names = []

        required_headers = {'stakeholder type'}
        optional_headers = {'description', 'stakeholder category'}

        try:
            data = []
            headers = []

            # ---- XLSX Handling ----
            if format_type == 'xlsx':
                import openpyxl
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({
                        'error': 'Please provide sheet_name',
                        'available_sheets': available_sheets
                    }, status=status.HTTP_400_BAD_REQUEST)
                if sheet_name not in available_sheets:
                    return Response({
                        'error': f'Sheet "{sheet_name}" not found',
                        'available_sheets': available_sheets
                    }, status=status.HTTP_400_BAD_REQUEST)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'Sheet "{sheet_name}" is empty. Provide at least one data row.'
                    }, status=status.HTTP_400_BAD_REQUEST)

                headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                if not required_headers.issubset(set(headers)):
                    return Response({
                        "statusCode": 400,
                        "status": True,
                        'message': f'Missing required headers. Required: {required_headers}, Found: {set(headers)}'
                    }, status=status.HTTP_400_BAD_REQUEST)

                for row in ws.iter_rows(min_row=2, values_only=True):
                    if not any(row):
                        continue
                    data.append(dict(zip(headers, row)))

                if not data:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'Sheet "{sheet_name}" has no data rows.'
                    }, status=status.HTTP_400_BAD_REQUEST)

            # ---- CSV Handling ----
            elif format_type == 'csv':
                decoded_file = file.read().decode('utf-8')
                dataset = Dataset()
                dataset.load(decoded_file, format='csv')

                for row in dataset.dict:
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({
                            "statusCode": 400,
                            "status": True,
                            "message": f'Missing required headers. Required: {", ".join(required_headers)}. Found: {", ".join(row_lower.keys())}.'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    data.append(row_lower)

                if not data:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": "CSV file is empty. Provide at least one data row."
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    "statusCode": 400,
                    "status": True,
                    'error': 'Unsupported file format. Use .xlsx or .csv'
                }, status=status.HTTP_400_BAD_REQUEST)

            # ---- Import Logic ----
            imported_count = 0
            for row in  reversed(data):
                name = str(row.get('stakeholder type')).strip() if row.get('stakeholder type') else None
                description = str(row.get('description')).strip() if row.get('description') else ''
                category_name = str(row.get('stakeholder category')).strip() if row.get('stakeholder category') else None

                if not name:
                    continue

                # Resolve category name to UUID
                category_uuid = None
                if category_name:
                    category_obj = StakeholderCategory.objects.filter(name__iexact=category_name, is_deleted=False).first()
                    if category_obj:
                        category_uuid = category_obj.uuid

                existing = StakeholderType.objects.filter(name__iexact=name).first()
                if existing:
                    if not existing.is_deleted:
                        duplicate_names.append(name)
                        continue
                    else:
                        existing.description = description
                        if category_uuid:
                            existing.category_id = category_uuid
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    StakeholderType.objects.create(
                        name=name,
                        description=description,
                        category_id=category_uuid,
                        is_deleted=False
                    )
                    imported_count += 1

        except Exception as e:
            return Response({
                "statusCode": 400,
                "status": True,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": list(set(duplicate_names)),
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count
        }, status=status.HTTP_200_OK)




class AccreditationCategoryListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'updated_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['name', 'description', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = AccreditationCategory.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )

        queryset = queryset.order_by(sort_by)

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = AccreditationCategorySerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)


# ------------------ Create API ------------------
class AccreditationCategoryCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        name = request.data.get("name", "").strip()
        existing = AccreditationCategory.objects.filter(name__iexact=name, is_deleted=False).first()

        if existing:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Accreditation category with this name already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = AccreditationCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Accreditation category created successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        else:
            messages = [msg for msgs in serializer.errors.values() for msg in msgs]
            return Response({
                "statusCode": 400,
                "status": False,
                "message": " ".join(messages)
            }, status=status.HTTP_400_BAD_REQUEST)


# ------------------ Retrieve API ------------------
class AccreditationCategoryRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = AccreditationCategory.objects.get(uuid=uuid, is_deleted=False)
        except AccreditationCategory.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Accreditation category not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = AccreditationCategorySerializer(obj)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Accreditation category retrieved successfully",
            "data": serializer.data
        })


# ------------------ Update API ------------------
class AccreditationCategoryUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = AccreditationCategory.objects.get(uuid=uuid, is_deleted=False)
        except AccreditationCategory.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Accreditation category not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = AccreditationCategorySerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Accreditation category updated successfully",
                "data": serializer.data
            })

        messages = [msg for msgs in serializer.errors.values() for msg in msgs]
        return Response({
            "statusCode": 400,
            "status": False,
            "message": " ".join(messages),
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)


# ------------------ Delete API ------------------
class AccreditationCategoryDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get('id', None)

        # Single delete via URL
        if uuid:
            try:
                obj = AccreditationCategory.objects.get(uuid=uuid)
                obj.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "Accreditation category permanently deleted.",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            except AccreditationCategory.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Accreditation category not found.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        # Delete all
        if ids == "all":
            queryset = AccreditationCategory.objects.all()
            count = queryset.count()
            queryset.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} accreditation category(s) permanently deleted.",
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

        queryset = AccreditationCategory.objects.filter(uuid__in=valid_uuids)
        count = queryset.count()
        queryset.delete()

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} accreditation category(s) permanently deleted.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        }, status=status.HTTP_200_OK)


# ------------------ Export API ------------------
class AccreditationCategoryExportAPIView(APIView):

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'name': 'Accrediation Category',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'updated_at': 'Modified On',
        }

        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())

        queryset = AccreditationCategory.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'AccreditationCategory'

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
            file_name = 'accreditation_categories.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'accreditation_categories.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


# ------------------ Import API ------------------
class AccreditationCategoryImportAPIView(APIView):

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicate_names = []
        required_headers = {'accrediation category'}
        optional_headers = {'description'}

        try:
            data = []
            headers = []

            if format_type == 'xlsx':
                import openpyxl
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({'error': 'Please provide sheet_name', 'available_sheets': available_sheets}, status=400)
                if sheet_name not in available_sheets:
                    return Response({'error': f'Sheet "{sheet_name}" not found', 'available_sheets': available_sheets}, status=400)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({"statusCode": 400, "status": False, "message": f'The uploaded XLSX sheet "{sheet_name}" is empty.'}, status=400)

                headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                if not required_headers.issubset(set(headers)):
                    return Response({"statusCode": 400, "status": True, "message": f'Missing required headers. Required: {required_headers}, Found: {set(headers)}'}, status=400)

                for row in ws.iter_rows(min_row=2, values_only=True):
                    if not any(row):
                        continue
                    data.append(dict(zip(headers, row)))

            elif format_type == 'csv':
                decoded_file = file.read().decode('utf-8')
                dataset = Dataset()
                dataset.load(decoded_file, format='csv')

                for row in dataset.dict:
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({"statusCode": 400, "status": True, "message": f'Missing required headers. Required: {required_headers}. Found: {set(row_lower.keys())}'}, status=400)
                    data.append(row_lower)
            else:
                return Response({"statusCode": 400, "status": True, 'error': 'Unsupported file format. Use .xlsx or .csv'}, status=400)

            imported_count = 0
            for row in  reversed(data):
                name = str(row.get('accrediation category')).strip() if row.get('accrediation category') else None
                description = str(row.get('description')).strip() if row.get('description') else ''

                if not name:
                    continue

                existing = AccreditationCategory.objects.filter(name__iexact=name).first()
                if existing:
                    if not existing.is_deleted:
                        duplicate_names.append(name)
                        continue
                    else:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    AccreditationCategory.objects.create(name=name, description=description, is_deleted=False)
                    imported_count += 1

        except Exception as e:
            return Response({"statusCode": 400, "status": True, 'message': str(e)}, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": list(set(duplicate_names)),
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count
        }, status=200)




#-------------------------------------------country---------------------------------

class AccreditationNameListAPIView(APIView):
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'updated_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['full_name', 'short_name', 'valid_upto', 'created_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = AccreditationName.objects.all()
        if search:
            queryset = queryset.filter(
                Q(full_name__icontains=search) |
                Q(short_name__icontains=search) |
                Q(description__icontains=search)
            )

        queryset = queryset.order_by(sort_by)

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = AccreditationNameSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


# -------------------- CREATE API --------------------
class AccreditationNameCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        serializer = AccreditationNameSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Accreditation created successfully",
                "data": serializer.data
            })
        errors = serializer.errors
        messages = []
        for field, msgs in errors.items():
            messages.extend(msgs)
        return Response({
            "statusCode": 400,
            "status": False,
            "message": " ".join(messages)
        }, status=status.HTTP_400_BAD_REQUEST)


# -------------------- RETRIEVE API --------------------
class AccreditationNameRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            accred = AccreditationName.objects.get(uuid=uuid)
        except AccreditationName.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Accreditation not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = AccreditationNameSerializer(accred)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Accreditation retrieved successfully",
            "data": serializer.data
        })


# -------------------- UPDATE API --------------------
class AccreditationNameUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            accred = AccreditationName.objects.get(uuid=uuid)
        except AccreditationName.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Accreditation not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = AccreditationNameSerializer(accred, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Accreditation updated successfully",
                "data": serializer.data
            })
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


# -------------------- DELETE API --------------------
class AccreditationNameDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get('id', None)

        if uuid:
            try:
                accred = AccreditationName.objects.get(uuid=uuid)
                accred.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "Accreditation permanently deleted",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            except AccreditationName.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Accreditation not found",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        if ids == "all":
            count = AccreditationName.objects.count()
            AccreditationName.objects.all().delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} accreditation(s) permanently deleted",
                "data": None
            })

        if not ids or not isinstance(ids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Provide a list of UUIDs in 'id' field or 'all'.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        valid_uuids = []
        invalid_uuids = []
        for u in ids:
            try:
                valid_uuids.append(UUID(u))
            except ValueError:
                invalid_uuids.append(u)

        queryset = AccreditationName.objects.filter(uuid__in=valid_uuids)
        count = queryset.count()
        queryset.delete()

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} accreditation(s) permanently deleted",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        })


# -------------------- EXPORT API --------------------

class AccreditationNameExportAPIView(APIView):
    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'country': 'Country',
            'category': 'Accrediation Category',
            'full_name': 'Accrediation Full Name',
            'short_name': 'Accrediation Short Name',
            'issuing_authority': 'Accrediation Issuing Authority Name',
            'valid_type': 'Accrediation Valid Upto',
            'valid_duration_value': 'Accrediation Valid Duration Value',
            'valid_duration_unit': 'Accrediation Valid Duration Unit',
            'valid_date': 'Accrediation Valid Date',
            'description': 'Description',
            'created_at': 'Created On',
            'updated_at': 'Modified On'
        }

        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())

        queryset = AccreditationName.objects.all()
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'AccreditationName'

        for accred in queryset:
            row = []
            for field in field_list:
                value = getattr(accred, field, '')

                # Format date fields
                if field in ['created_at', 'updated_at'] and value:
                    value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")

                # Use UUID for FK fields
                elif field == 'country' and accred.country:
                    value = accred.country.name
                elif field == 'category' and accred.category:
                    value = accred.category.name
                if field == "valid_date" and value:
                    value = value.strftime("%d-%m-%Y")

                elif isinstance(value, bool):
                    value = int(value)

                row.append(value if value is not None else '')
            dataset.append(row)

        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'accreditations.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'accreditations.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


#-------------------------------------------import---------------------------------

class AccreditationNameImportAPIView(APIView):
    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicate_names = []
        skipped_rows = []

        required_headers = {'accrediation full name', 'country', 'accrediation category'}
        optional_headers = {
            'accrediation short name',
            'accrediation issuing authority name',
            'accrediation valid upto',
            'accrediation valid duration value',
            'accrediation valid duration unit',
            'accrediation valid date',
            'description'
        }

        try:
            data = []
            headers = []

            # ---------- XLSX ----------
            if format_type == 'xlsx':
                import openpyxl
                wb = openpyxl.load_workbook(file, read_only=True)

                if not sheet_name:
                    return Response(
                        {'error': 'Provide sheet_name', 'available_sheets': wb.sheetnames},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                if sheet_name not in wb.sheetnames:
                    return Response(
                        {'error': f'Sheet "{sheet_name}" not found', 'available_sheets': wb.sheetnames},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({'statusCode': 400, 'status': False, 'message': 'Sheet is empty'},
                                    status=status.HTTP_400_BAD_REQUEST)

                headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                if not required_headers.issubset(set(headers)):
                    missing = required_headers - set(headers)
                    return Response(
                        {'statusCode': 400, 'status': False, 'message': f'Missing required headers: {missing}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                for row in ws.iter_rows(min_row=2, values_only=True):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    data.append(row_dict)

            # ---------- CSV ----------
            elif format_type == 'csv':
                decoded_file = file.read().decode('utf-8')
                dataset = Dataset()
                dataset.load(decoded_file, format='csv')

                for row in dataset.dict:
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    if not required_headers.issubset(set(row_lower.keys())):
                        missing = required_headers - set(row_lower.keys())
                        return Response(
                            {'statusCode': 400, 'status': False, 'message': f'Missing required headers: {missing}'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    data.append(row_lower)

            else:
                return Response(
                    {'statusCode': 400, 'status': False, 'error': 'Unsupported file format'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # ---------- Import Data ----------
            ALLOWED_VALID_TYPES = ['Permanent', 'Valid Upto', 'Date'] 
            ALLOWED_VALID_UNITS = ['Months', 'Weeks', 'Years']
            imported_count = 0

            for row in reversed(data):
                full_name = str(row.get('accrediation full name')).strip() if row.get('accrediation full name') else None
                country_name = str(row.get('country')).strip() if row.get('country') else None
                category_name = str(row.get('accrediation category')).strip() if row.get('accrediation category') else None
                short_name = str(row.get('accrediation short name')).strip() if row.get('accrediation short name') else ''
                issuing_authority = str(row.get('accrediation issuing authority name')).strip() if row.get('accrediation issuing authority name') else ''
                description = str(row.get('description')).strip() if row.get('description') else ''
                valid_type = str(row.get('accrediation valid upto')).strip() if row.get('accrediation valid upto') else None
                valid_duration_value = row.get('accrediation valid duration value')
                valid_duration_unit = str(row.get('accrediation valid duration unit')).strip() if row.get('accrediation valid duration unit') else None
                valid_date_raw = row.get('accrediation valid date')
                valid_date = None
                if valid_date_raw:
                    if isinstance(valid_date_raw, datetime):
                        valid_date = valid_date_raw.date()
                    else:
                        date_str = str(valid_date_raw).strip()
                        for fmt in ("%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d"):
                            try:
                                valid_date = datetime.strptime(date_str, fmt).date()
                                break
                            except ValueError:
                                continue
                        if not valid_date:
                            skipped_rows.append({
                                'full_name': full_name,
                                'country': country_name,
                                'category': category_name,
                                'reason': f"Invalid date format '{valid_date_raw}'. Expected formats: dd-mm-yyyy, dd/mm/yyyy "
                            })
                            continue

                if not full_name or not country_name or not category_name:
                    skipped_rows.append({
                        'full_name': full_name or ' ',
                        'Reason': f"Missing required fields. Required: {', '.join(required_headers)}"
                    })
                    continue

                country = Country.objects.filter(name__iexact=country_name).first()
                category = AccreditationCategory.objects.filter(name__iexact=category_name).first()

                if not full_name or not country_name or not category_name:
                    skipped_rows.append({
                        'Accrediation Full Name': full_name or 'Unknown',
                        'Country': country_name or 'Unknown',
                        'Accrediation Category': category_name or 'Unknown',
                        'Reason': 'Missing required field(s)'
                    })
                    continue

                if not country or not category:
                    skipped_rows.append({
                        'Accrediation Full Name': full_name,
                        'Country': country_name,
                        'Accrediation Category': category_name,
                        'Reason': f'Invalid country or category: {country_name}/{category_name}'
                    })
                    continue

                if valid_type and valid_type not in ALLOWED_VALID_TYPES:
                    skipped_rows.append({
                        'Accrediation Full Name': full_name,
                        'Country': country_name,
                        'Accrediation Category': category_name,
                        'Reason': f"Invalid valid_type='{valid_type}'. Allowed: Permanent, Valid Upto, Date"
                    })
                    continue

                # ---------- Valid Upto checks ----------
                if valid_type == 'Valid Upto':
                    # Check duration value
                    if valid_duration_value is None:
                        skipped_rows.append({
                            'Accrediation Full Name': full_name,
                            'Country': country_name,
                            'Accrediation Category': category_name,
                            'Reason': "Valid Upto type requires 'Accrediation Valid Duration' as numeric and 'Accrediation Valid Unit' as one of: Months, Weeks, Years"
                        })
                        continue

                    # Numeric check
                    try:
                        valid_duration_value = int(valid_duration_value)
                        if valid_duration_value <= 0:
                            raise ValueError
                    except (ValueError, TypeError):
                        skipped_rows.append({
                            'Accrediation Full Name': full_name,
                            'Country': country_name,
                            'Accrediation Category': category_name,
                            'Reason': "Invalid 'Accrediation Valid Duration'. Please use a positive numeric value."
                        })
                        continue

                    # Unit check
                    if not valid_duration_unit or valid_duration_unit not in ALLOWED_VALID_UNITS:
                        skipped_rows.append({
                            'Accrediation Full Name': full_name,
                            'Country': country_name,
                            'Accrediation Category': category_name,
                            'Reason': f"Invalid 'Accrediation Valid Unit'='{valid_duration_unit}'. Please use one of: Months, Weeks, Years"
                        })
                        continue

                elif valid_type == 'Date' and not valid_date:
                    skipped_rows.append({
                        'Accrediation Full Name': full_name,
                        'Country': country_name,
                        'Accrediation Category': category_name,
                        'Reason': "Accrediation Valid Date  requires valid_date formate DD-MM_YYY"
                    })
                    continue

                if valid_duration_unit and valid_duration_unit not in ALLOWED_VALID_UNITS:
                    skipped_rows.append({
                        'Accrediation Full Name': full_name,
                        'Country': country_name,
                        'Accrediation Category': category_name,
                        'Reason': f"Invalid 'Accrediation Valid Unit'='{valid_duration_unit}'. Please use one of: Months, Weeks, Years"
                    })
                    continue

                existing = AccreditationName.objects.filter(
                    full_name__iexact=full_name,
                    country=country,
                    category=category
                ).first()

                if existing:
                    if not existing.is_deleted:
                        duplicate_names.append({
                            'Country': country_name,
                            'Accrediation Full Name': full_name,
                            'Accrediation Category': category_name
                        })
                        continue
                    else:
                        # Restore soft-deleted record
                        existing.short_name = short_name
                        existing.issuing_authority = issuing_authority
                        existing.description = description
                        existing.valid_type = valid_type
                        existing.valid_duration_value = valid_duration_value
                        existing.valid_duration_unit = valid_duration_unit
                        existing.valid_date = valid_date
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                        continue

                # Create new entry
                try:
                    AccreditationName.objects.create(
                        full_name=full_name,
                        short_name=short_name,
                        country=country,
                        category=category,
                        issuing_authority=issuing_authority,
                        valid_type=valid_type,
                        valid_duration_value=valid_duration_value,
                        valid_duration_unit=valid_duration_unit,
                        valid_date=valid_date,
                        description=description,
                        is_deleted=False
                    )
                    imported_count += 1
                except IntegrityError:
                    duplicate_names.append({
                        'Country': country_name,
                        'Accrediation Full Name': full_name,
                        'Accrediation Category': category_name
                    })

        except Exception as e:
            return Response({'statusCode': 400, 'status': False, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": duplicate_names,
            "skipped_rows": skipped_rows,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count
        }, status=status.HTTP_200_OK)


#-----------------Bank Account-----------------------        

class BankAccountTypeCreateAPIView(APIView):
    def post(self, request):
        serializer = BankAccountTypeSerializer(data=request.data)
        if serializer.is_valid():
            if BankAccountType.objects.filter(name=serializer.validated_data['name'], is_deleted=False).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Bank Account  with this name already exists"
                }, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Bank Account created successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)


        return Response({
            "statusCode": 400,
            "status": False,
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class BankAccountTypeListAPIView(APIView):    
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'updated_at')
        sort_order = request.GET.get('sortOrder', 'desc')  # default to newest first

        allowed_sort_fields = ['name', 'description', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        # Apply descending order for 'desc'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = BankAccountType.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )

        queryset = queryset.order_by(sort_by)

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = BankAccountTypeSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)



class BankAccountTypeRetrieveAPIView(APIView):
    def get(self, request, uuid):
        try:
            bankaccount = BankAccountType.objects.get(uuid=uuid, is_deleted=False)
        except BankAccountType.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Bank Account  not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = BankAccountTypeSerializer(bankaccount)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Bank Account  retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class BankAccountTypeUpdateAPIView(APIView):
    def put(self, request, uuid):
        try:
            category = BankAccountType.objects.get(uuid=uuid, is_deleted=False)
        except BankAccountType.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Bank Account not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = BankAccountTypeSerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            new_name = serializer.validated_data.get("name", category.name)
            if BankAccountType.objects.filter(name=new_name).exclude(uuid=uuid).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Bank Account with this name already exists"
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Bank Account details updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "statusCode": 400,
            "status": False,
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class BankAccountTypeDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        uuids_param = request.data.get('id', None)

        # Single delete via URL parameter
        if uuid:
            try:
                bank_type = BankAccountType.objects.get(uuid=uuid, is_deleted=False)
                bank_type.is_deleted = True
                bank_type.save()
                return Response({
                    "statusCode": 200,
                    "status": True,
                    "message": "Bank Account Type deleted successfully.",
                    "data": None
                }, status=status.HTTP_200_OK)
            except BankAccountType.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Bank Account Type not found.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        # Delete all BankAccountTypes
        if uuids_param == "all":
            bank_types = BankAccountType.objects.filter(is_deleted=False)
            count = bank_types.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No Bank Account Types found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
            bank_types.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} Bank Account Type(s) deleted successfully.",
                "data": None
            }, status=status.HTTP_200_OK)

        # Validate bulk UUIDs
        if not uuids_param or not isinstance(uuids_param, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide a list of UUIDs in 'uuids' field or 'all'.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        valid_uuids = []
        invalid_uuids = []
        for u in uuids_param:
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

        # Bulk delete (soft delete)
        bank_types = BankAccountType.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = bank_types.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching Bank Account Types found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_404_NOT_FOUND)

        bank_types.delete()
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} Bank Account Type(s) deleted successfully.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        }, status=status.HTTP_200_OK)
class BankAccountTypeExportAPIView(APIView):
    # permission_classes = [IsAuthenticated]  # Uncomment if needed

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')  # comma-separated fields
        uuids_param = request.GET.get('uuids', '')  # comma-separated UUIDs

        uuids = [u.strip() for u in uuids_param.split(',') if u]

        # --- Field to header mapping ---
        field_header_map = {
            'uuid': 'UUID',
            'name': 'Bank Account Type',  # Custom header
            'description': 'Description',
            'is_deleted': 'Deleted',
            'updated_at': 'Modified On',
            
        }

        # --- Determine which fields to export ---
        if fields:
            field_list = [f.strip() for f in fields.split(',')]
        else:
            field_list = list(field_header_map.keys())

        queryset = BankAccountType.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')


        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title ="BankAccountType"

        for record in queryset:
            row = []
            for field in field_list:
                value = getattr(record, field, '')

                if field in ['created_at', 'updated_at'] and value:
                    # Convert UTC to IST and format
                    value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
                elif isinstance(value, bool):
                    value = int(value)

                row.append(value if value is not None else '')
            dataset.append(row)

        # --- Export data ---
        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'BankAccountType.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'BankAccountType.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


class BankAccountTypeImportAPIView(APIView):
   
    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicate_names = []
        

        # Mandatory and optional headers
        required_headers = {'bank account type'}
        optional_headers = {'description'}

        try:
            data = []
            # ---------- XLSX Handling ----------
            if format_type == 'xlsx':
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({
                        'error': 'Please provide sheet_name',
                        'available_sheets': available_sheets
                    }, status=status.HTTP_400_BAD_REQUEST)

                if sheet_name not in available_sheets:
                    return Response({
                        'error': f'Sheet "{sheet_name}" not found in uploaded file',
                        'available_sheets': available_sheets
                    }, status=status.HTTP_400_BAD_REQUEST)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'The uploaded XLSX file (sheet: "{sheet_name}") is empty. Please provide at least one data row.'
                    }, status=status.HTTP_400_BAD_REQUEST)

                headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]

                # Validate required headers only
                if not required_headers.issubset(set(headers)):
                    return Response({
                        "statusCode": 400,
                        "status": True,
                        'message': f'Missing required headers. Required: {required_headers}, Found: {set(headers)}'
                    }, status=status.HTTP_400_BAD_REQUEST)

                for row in ws.iter_rows(min_row=2, values_only=True):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    data.append(row_dict)
                
                if not data:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'The uploaded XLSX file (sheet: "{sheet_name}") is empty. Please provide at least one data row.'
                    }, status=status.HTTP_400_BAD_REQUEST)

            # ---------- CSV Handling ----------
            elif format_type == 'csv':
                decoded_file = file.read().decode('utf-8')
                dataset = Dataset()
                dataset.load(decoded_file, format='csv')

                for row in dataset.dict:
                    row_lower = {self.normalize_header(k): v for k, v in row.items()}
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({
                            "statusCode": 400,
                            "status": True,
                            "message": f'Missing required headers. Required: {required_headers}, Found: {set(row_lower.keys())}.'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    if not any(row_lower.values()):
                        continue
                    data.append(row_lower)

            else:
                return Response({'error': 'Unsupported file format. Use .xlsx or .csv'}, status=status.HTTP_400_BAD_REQUEST)

            # ---------- Process Each Row ----------
            imported_count = 0
            for row in  reversed(data):
                name = str(row.get('bank account type')).strip() if row.get('bank account type') else None
                description = str(row.get('description')).strip() if row.get('description') else ''

                if not name:
                    continue

                existing = BankAccountType.objects.filter(name__iexact=name).first()

                if existing:
                    if existing.is_deleted:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                    else:
                        duplicate_names.append(name)
                        continue
                else:
                    BankAccountType.objects.create(
                        name=name,
                        description=description,
                        is_deleted=False
                    )
                    imported_count += 1

        except Exception as e:
            return Response({
                "statusCode": 400,
                "status": True,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": list(set(duplicate_names)),
            "imported_count": imported_count,
            "message": "Import successful"
        }, status=status.HTTP_200_OK)







#-------------------------------------------LicenseName---------------------------------
class LicenseNameListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'updated_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['full_name', 'short_name', 'issuing_authority', 'valid_upto', 'created_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = LicenseName.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(full_name__icontains=search) |
                Q(short_name__icontains=search) |
                Q(issuing_authority__icontains=search) |
                Q(description__icontains=search) |
                Q(country__name__icontains=search)
            )

        queryset = queryset.order_by(sort_by)

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = LicenseNameSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)


# ------------------ Create API ------------------
class LicenseNameCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        full_name = request.data.get("full_name", "").strip()
        country_id = request.data.get("country")

        existing = LicenseName.objects.filter(full_name__iexact=full_name, country_id=country_id, is_deleted=False).first()
        if existing:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "License with this name and country already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = LicenseNameSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "License created successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        messages = [msg for msgs in serializer.errors.values() for msg in msgs]
        return Response({
            "statusCode": 400,
            "status": False,
            "message": " ".join(messages)
        }, status=status.HTTP_400_BAD_REQUEST)


# ------------------ Retrieve API ------------------
class LicenseNameRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = LicenseName.objects.get(uuid=uuid, is_deleted=False)
        except LicenseName.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "License not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = LicenseNameSerializer(obj)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "License retrieved successfully",
            "data": serializer.data
        })


# ------------------ Update API ------------------
class LicenseNameUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = LicenseName.objects.get(uuid=uuid, is_deleted=False)
        except LicenseName.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "License not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = LicenseNameSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "License updated successfully",
                "data": serializer.data
            })

        messages = [msg for msgs in serializer.errors.values() for msg in msgs]
        return Response({
            "statusCode": 400,
            "status": False,
            "message": " ".join(messages),
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)


# ------------------ Delete API ------------------
class LicenseNameDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get('id', None)

        # Single delete via URL
        if uuid:
            try:
                obj = LicenseName.objects.get(uuid=uuid)
                obj.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "License permanently deleted.",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            except LicenseName.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "License not found.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        # Delete all
        if ids == "all":
            queryset = LicenseName.objects.all()
            count = queryset.count()
            queryset.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} licenses permanently deleted.",
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

        queryset = LicenseName.objects.filter(uuid__in=valid_uuids)
        count = queryset.count()
        queryset.delete()

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} license(s) permanently deleted.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        }, status=status.HTTP_200_OK)


# ------------------ Export API ------------------
class LicenseNameExportAPIView(APIView):

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'full_name': 'License Full Name',
            'short_name': 'License Short Name',
            'issuing_authority': 'License Issuing Authority Name',
            'description': 'Description',
            'valid_type': 'License Valid Upto',
            'valid_duration_value': 'License Valid Duration Value',
            'valid_duration_unit': 'License Valid Duration Unit',
            'valid_date': 'License Valid Date',
            'country': 'Country Name',
            'is_deleted': 'Deleted',
            'updated_at': 'Modified On',
        }

        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())

        queryset = LicenseName.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'LicenseName'

        for obj in queryset:
            row = []
            for field in field_list:
                if field == 'country':
                    value = obj.country.name if obj.country else ''
                else:
                    value = getattr(obj, field, '')

                if field in ['created_at', 'updated_at'] and value:
                    value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
                elif field == 'valid_date' and value:
                    value = value.strftime("%d-%m-%Y")
                elif isinstance(value, bool):
                    value = int(value)
                

                row.append(value if value is not None else '')
            dataset.append(row)

        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'licenses.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'licenses.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response




# ------------------ Import API ------------------
class LicenseNameImportAPIView(APIView):

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicate_names = []
        skipped_rows = []

        required_headers = {'license full name', 'country','license short name'}
        optional_headers = {
            'license issuing authority name',
            'description',
            'license valid upto',
            'license valid duration value',
            'license valid duration unit',
            'license valid date',
        }

        try:
            data = []
            headers = []

            # ---------- XLSX ----------
            if format_type == 'xlsx':
                import openpyxl
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({'error': 'Please provide sheet_name', 'available_sheets': available_sheets}, status=400)
                if sheet_name not in available_sheets:
                    return Response({'error': f'Sheet "{sheet_name}" not found', 'available_sheets': available_sheets}, status=400)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({"statusCode": 400, "status": False, "message": f'The uploaded XLSX sheet "{sheet_name}" is empty.'}, status=400)

                headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                if not required_headers.issubset(set(headers)):
                    missing = required_headers - set(headers)
                    return Response({"statusCode": 400, "status": False, "message": f'Missing required headers: {missing}'}, status=400)

                for row in ws.iter_rows(min_row=2, values_only=True):
                    if not any(row):
                        continue
                    data.append(dict(zip(headers, row)))

            # ---------- CSV ----------
            elif format_type == 'csv':
                import csv
                import io
                decoded_file = file.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(decoded_file))
                for row in reader:
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    if not required_headers.issubset(set(row_lower.keys())):
                        missing = required_headers - set(row_lower.keys())
                        return Response({"statusCode": 400, "status": False, "message": f"Missing required headers: {missing}"}, status=400)
                    data.append(row_lower)
            else:
                return Response({"statusCode": 400, "status": False, 'error': 'Unsupported file format. Use .xlsx or .csv'}, status=400)

            # ---------- Import Logic ----------
            ALLOWED_VALID_TYPES = ['Permanent', 'Valid Upto', 'Date']
            ALLOWED_VALID_UNITS = ['Months', 'Weeks', 'Years']
            imported_count = 0

            for row in reversed(data):
                full_name = str(row.get('license full name')).strip() if row.get('license full name') else None
                country_name = str(row.get('country')).strip() if row.get('country') else None
                short_name = str(row.get('license short name')).strip() if row.get('license short name') else ''
                issuing_authority = str(row.get('license issuing authority name')).strip() if row.get('license issuing authority name') else ''
                description = str(row.get('description')).strip() if row.get('description') else ''
                valid_duration_value = row.get('license valid duration value')
                valid_duration_unit_raw = row.get('license valid duration unit')
                valid_duration_unit = valid_duration_unit_raw.strip().title() if valid_duration_unit_raw else None
                valid_date_raw = row.get('license valid date')
                valid_date = None

                if valid_date_raw:
                    if isinstance(valid_date_raw, datetime):
                        valid_date = valid_date_raw.date()
                    else:
                        date_str = str(valid_date_raw).strip()
                        for fmt in ("%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d"):
                            try:
                                valid_date = datetime.strptime(date_str, fmt).date()
                                break
                            except ValueError:
                                continue
                        if not valid_date:
                            skipped_rows.append({
                                'License Full Name': full_name,
                                'Country': country_name,
                                'Reason': f"Invalid date format '{valid_date_raw}'. Expected formats: dd-mm-yyyy, dd/mm/yyyy "
                            })
                            continue

                if not full_name or not country_name:
                    skipped_rows.append({
                        'License Full Name': full_name or 'Unknown',
                        'Country': country_name or 'Unknown',
                        'Reason': f"Missing required fields. Required: {', '.join(required_headers)}"
                    })
                    continue

                country_obj = Country.objects.filter(name__iexact=country_name).first()
                if not country_obj:
                    skipped_rows.append({
                        'License Full Name': full_name,
                        'Country': country_name,
                        'Reason': 'Invalid country'
                    })
                    continue

                valid_type_raw = str(row.get('license valid upto')).strip() if row.get('license valid upto') else None
                valid_type = unicodedata.normalize('NFKC', valid_type_raw).title() if valid_type_raw else None

                if valid_type and valid_type not in ALLOWED_VALID_TYPES:
                    skipped_rows.append({
                        'License Full Name': full_name,
                        'Country': country_name,
                        'Reason': f"Invalid valid_type='{valid_type}'. Allowed: {', '.join(ALLOWED_VALID_TYPES)}"
                    })
                    continue

                # Valid Upto checks
                if valid_type == 'Valid Upto':
                    if valid_duration_value is None or not valid_duration_unit:
                        skipped_rows.append({
                            'License Full Name': full_name,
                            'Country': country_name,
                            'Reason': "'Valid Upto' type requires both valid_duration_value and valid_duration_unit"
                        })
                        continue

                    try:
                        valid_duration_value = int(valid_duration_value)
                        if valid_duration_value <= 0:
                            raise ValueError
                    except (ValueError, TypeError):
                        skipped_rows.append({
                            'License Full Name': full_name,
                            'Country': country_name,
                            'Reason': "Invalid 'valid_duration_value'. Must be a positive number."
                        })
                        continue

                    if valid_duration_unit not in ALLOWED_VALID_UNITS:
                        skipped_rows.append({
                            'License Full Name': full_name,
                            'Country': country_name,
                            'Reason': f"Invalid 'valid_duration_unit'='{valid_duration_unit}'. Allowed: {', '.join(ALLOWED_VALID_UNITS)}"
                        })
                        continue

                elif valid_type == 'Date' and not valid_date:
                    skipped_rows.append({
                        'License Full Name': full_name,
                        'Country': country_name,
                        'Reason': "Valid type 'Date' requires a valid 'license valid date'"
                    })
                    continue

                # Check duplicates
                existing = LicenseName.objects.filter(full_name__iexact=full_name, country=country_obj).first()
                if existing:
                    if not existing.is_deleted:
                        duplicate_names.append({
                            'Country': country_obj.name,
                            'License Full Name': full_name
                        })
                        continue
                    else:
                        # Restore soft-deleted record
                        existing.short_name = short_name
                        existing.issuing_authority = issuing_authority
                        existing.description = description
                        existing.valid_type = valid_type
                        existing.valid_duration_value = valid_duration_value
                        existing.valid_duration_unit = valid_duration_unit
                        existing.valid_date = valid_date
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                        continue

                # Create new entry
                try:
                    LicenseName.objects.create(
                        full_name=full_name,
                        country=country_obj,
                        short_name=short_name,
                        issuing_authority=issuing_authority,
                        description=description,
                        valid_type=valid_type,
                        valid_duration_value=valid_duration_value,
                        valid_duration_unit=valid_duration_unit,
                        valid_date=valid_date,
                        is_deleted=False
                    )
                    imported_count += 1
                except IntegrityError:
                    duplicate_names.append({
                        'Country': country_obj.name,
                        'License Full Name': full_name
                    })

        except Exception as e:
            return Response({"statusCode": 400, "status": False, "message": str(e)}, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": duplicate_names,
            "skipped_rows": skipped_rows,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count
        })



#-------------------------------------------LeadSource---------------------------------

class LeadSourceCreateAPIView(APIView):
    def post(self, request):
        serializer = LeadSourceSerializer(data=request.data)
        if serializer.is_valid():
            if LeadSource.objects.filter(name=serializer.validated_data['name'], is_deleted=False).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Lead Source  with this name already exists"
                }, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Lead Source created successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)


        return Response({
            "statusCode": 400,
            "status": False,
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


    

class LeadSourceListAPIView(APIView):    
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'updated_at')
        sort_order = request.GET.get('sortOrder', 'desc')  # default to newest first

        allowed_sort_fields = ['name', 'description', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        # Apply descending order for 'desc'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = LeadSource.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )

        queryset = queryset.order_by(sort_by)

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = LeadSourceSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)


class LeadSourceRetrieveAPIView(APIView):
    def get(self, request, uuid):
        try:
            leadsource = LeadSource.objects.get(uuid=uuid, is_deleted=False)
        except LeadSource.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Lead Source not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = LeadSourceSerializer(leadsource)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Lead Source retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class LeadSourceUpdateAPIView(APIView):
    def put(self, request, uuid):
        try:
            category = LeadSource.objects.get(uuid=uuid, is_deleted=False)
        except LeadSource.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Lead Source not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = LeadSourceSerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            new_name = serializer.validated_data.get("name", category.name)
            if LeadSource.objects.filter(name=new_name).exclude(uuid=uuid).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Lead Source with this name already exists"
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Lead Source details updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "statusCode": 400,
            "status": False,
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)



class LeadSourceDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        ids = request.data.get('id', None)

        if not ids:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide 'id' field (UUID list or 'all').",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        # Delete all
        if ids == "all":
            lead_sources = LeadSource.objects.filter(is_deleted=False)
            count = lead_sources.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No Lead Source Types found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
            lead_sources.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} Lead Source Type(s) deleted successfully.",
                "data": None
            }, status=status.HTTP_200_OK)

        # List of UUIDs
        if not isinstance(ids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide a list of UUIDs in 'id' field or 'all'.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate UUIDs
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

        # Fetch Lead Sources that exist and are not deleted
        lead_sources = LeadSource.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = lead_sources.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching Lead Source Types found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_404_NOT_FOUND)

        # Soft delete
        lead_sources.delete()

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} Lead Source Type(s) deleted successfully.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        }, status=status.HTTP_200_OK)

class LeadSourceExportAPIView(APIView):
    # permission_classes = [IsAuthenticated]  # Uncomment if needed

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')  # optional comma-separated fields
        uuids_param = request.GET.get('uuids', '')  # optional comma-separated uuids

        # Parse UUIDs
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        # Mapping fields to readable headers
        field_header_map = {
            'uuid': 'UUID',
            'name': 'Lead Source',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'updated_at': 'Modified On',
            
        }

        # Determine which fields to export
        if fields:
            field_list = [f.strip() for f in fields.split(',')]
        else:
            field_list = list(field_header_map.keys())

        # Filter queryset
        queryset = LeadSource.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')


        # Prepare dataset
        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title="LeadSource"


        for lead in queryset:
            row = []
            for field in field_list:
                value = getattr(lead, field, '')

                # Format datetime fields in IST
                if field in ['created_at', 'updated_at'] and value:
                    value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
                elif isinstance(value, bool):
                    value = int(value)

                row.append(value if value is not None else '')
            dataset.append(row)

        # --- Export data ---
        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'lead_sources.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'lead_sources.xlsx'

        # --- Return response ---
        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


class LeadSourceImportAPIView(APIView):
    """
    API to import Lead Sources from CSV or XLSX.
    """

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicate_names = []

        # Define required and optional headers
        required_headers = {'lead source'}  # mandatory
        optional_headers = {'description'}  # optional

        try:
            data = []
            headers = []

            # ---------- XLSX Handling ----------
            if format_type == 'xlsx':
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({
                        'error': 'Please provide sheet_name',
                        'available_sheets': available_sheets
                    }, status=status.HTTP_400_BAD_REQUEST)

                if sheet_name not in available_sheets:
                    return Response({
                        'error': f'Sheet "{sheet_name}" not found in uploaded file',
                        'available_sheets': available_sheets
                    }, status=status.HTTP_400_BAD_REQUEST)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'The uploaded XLSX file (sheet: "{sheet_name}") is empty. Please provide at least one data row.'
                    }, status=status.HTTP_400_BAD_REQUEST)

                headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]

                # Validate required headers only
                if not required_headers.issubset(set(headers)):
                    return Response({
                        "statusCode": 400,
                        "status": True,
                        'message': f'Missing required headers. Required: {required_headers}, Found: {set(headers)}'
                    }, status=status.HTTP_400_BAD_REQUEST)

                for row in ws.iter_rows(min_row=2, values_only=True):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    data.append(row_dict)

                if not data:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'The uploaded XLSX file (sheet: "{sheet_name}") is empty. Please provide at least one data row.'
                    }, status=status.HTTP_400_BAD_REQUEST)

            # ---------- CSV Handling ----------
            elif format_type == 'csv':
                decoded_file = file.read().decode('utf-8')
                dataset = Dataset()
                dataset.load(decoded_file, format='csv')

                for row in dataset.dict:
                    row_lower = {k.strip().lower(): v for k, v in row.items()}

                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({
                            "statusCode": 400,
                            "status": True,
                            "message": f'Missing required headers. Required: {required_headers}. Found: {set(row_lower.keys())}.'
                        }, status=status.HTTP_400_BAD_REQUEST)

                    if not any(row_lower.values()):
                        continue
                    data.append(row_lower)

                if not data:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": "The uploaded CSV file is empty. Please provide at least one data row."
                    }, status=status.HTTP_400_BAD_REQUEST)

            else:
                return Response({'error': 'Unsupported file format. Use .xlsx or .csv'}, status=status.HTTP_400_BAD_REQUEST)

            # ---------- Process Each Row ----------
            imported_count = 0
            for row in  reversed(data):
                name = str(row.get('lead source')).strip() if row.get('lead source') else None
                description = str(row.get('description')).strip() if row.get('description') else ''

                if not name:
                    continue

                existing = LeadSource.objects.filter(name__iexact=name).first()

                if existing:
                    if existing.is_deleted:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                    else:
                        duplicate_names.append(name)
                        continue
                else:
                    LeadSource.objects.create(
                        name=name,
                        description=description,
                        is_deleted=False
                    )
                    imported_count += 1

        except Exception as e:
            return Response({
                "statusCode": 400,
                "status": True,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": list(set(duplicate_names)),
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count
        }, status=status.HTTP_200_OK)
#-------------------------------------------InterestLevel---------------------------------



class InterestLevelCreateAPIView(APIView):
    def post(self, request):
        serializer = InterestLevelSerializer(data=request.data)
        if serializer.is_valid():
            if InterestLevel.objects.filter(name=serializer.validated_data['name'], is_deleted=False).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Interest Level  with this name already exists"
                }, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Interest Level created successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)


        return Response({
            "statusCode": 400,
            "status": False,
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class InterestLevelListAPIView(APIView):    
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'updated_at')
        sort_order = request.GET.get('sortOrder', 'desc')  # default to newest first

        allowed_sort_fields = ['name', 'description', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        # Apply descending order for 'desc'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = InterestLevel.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )

        queryset = queryset.order_by(sort_by)

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = InterestLevelSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)

class InterestLevelRetrieveAPIView(APIView):
    def get(self, request, uuid):
        try:
            interestlevel = InterestLevel.objects.get(uuid=uuid, is_deleted=False)
        except InterestLevel.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Interest Level  not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = InterestLevelSerializer(interestlevel)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Interest Level  retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class InterestLevelUpdateAPIView(APIView):
    def put(self, request, uuid):
        try:
            category = InterestLevel.objects.get(uuid=uuid, is_deleted=False)
        except InterestLevel.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Interest Level not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = InterestLevelSerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            new_name = serializer.validated_data.get("name", category.name)
            if InterestLevel.objects.filter(name=new_name).exclude(uuid=uuid).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Interest Level with this name already exists"
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Interest Level details updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "statusCode": 400,
            "status": False,
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class InterestLevelDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        ids = request.data.get('id', None)

        # Validate ID field
        if not ids:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide 'id' field (UUID list or 'all').",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        # Case 1: Delete all Interest Levels
        if ids == "all":
            interests = InterestLevel.objects.filter(is_deleted=False)
            count = interests.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No Interest Levels found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
            interests.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} Interest Level(s) deleted successfully.",
                "data": None
            }, status=status.HTTP_200_OK)

        # Case 2: Delete multiple by UUID list
        if not isinstance(ids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide a list of UUIDs in 'id' field or 'all'.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate UUIDs
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

        # Fetch existing, non-deleted Interest Levels
        interests = InterestLevel.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = interests.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching Interest Levels found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_404_NOT_FOUND)

        # Soft delete
        interests.delete()

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} Interest Level(s) deleted successfully.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        }, status=status.HTTP_200_OK)

class InterestLevelExportAPIView(APIView):
    # permission_classes = [IsAuthenticated]  # Uncomment and adjust as needed

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')  
        uuids_param = request.GET.get('uuids', '')

        uuids = [u.strip() for u in uuids_param.split(',') if u]

        # Mapping fields to readable headers
        field_header_map = {
            'uuid': 'UUID',
            'name': 'Interest Level',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'updated_at': 'Modified On',
            
        }

        if fields:
            field_list = [f.strip() for f in fields.split(',')]
        else:
            field_list = list(field_header_map.keys())


        queryset = InterestLevel.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title="InterestLevel"


        for inte in queryset:
            row = []
            for field in field_list:
                value = getattr(inte, field, '')
                if field in ['updated_at'] and value:
                    value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
                elif isinstance(value, bool):
                    value = int(value)

                row.append(value if value is not None else '')
            dataset.append(row)

        if format_type == 'xlsx':
            data = XLSX().export_data(dataset)
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'InterestLevel.xlsx'
        else:
            data = CSV().export_data(dataset)
            content_type = 'text/csv; charset=utf-8'
            file_name = 'InterestLevel.csv'

        response = HttpResponse(data, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response



class InterestLevelImportAPIView(APIView):
    """
    API to import Interest Levels from CSV or XLSX.
    Interest Level: mandatory
    Description: optional
    """

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicate_names = []
        data = []

        # Required and optional headers
        required_headers = {'interest level'}  # mandatory
        optional_headers = {'description'}    # optional

        try:
            # ---------- XLSX Handling ----------
            if format_type == 'xlsx':
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({
                        'error': 'Please provide sheet_name',
                        'available_sheets': available_sheets
                    }, status=status.HTTP_400_BAD_REQUEST)

                if sheet_name not in available_sheets:
                    return Response({
                        'error': f'Sheet "{sheet_name}" not found in uploaded file',
                        'available_sheets': available_sheets
                    }, status=status.HTTP_400_BAD_REQUEST)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'The uploaded XLSX file (sheet: "{sheet_name}") is empty. Please provide at least one data row.'
                    }, status=status.HTTP_400_BAD_REQUEST)

                headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]

                # Validate only required headers
                if not required_headers.issubset(set(headers)):
                    return Response({
                        "statusCode": 400,
                        "status": True,
                        'message': f'Missing required headers. Required: {required_headers}, Found: {set(headers)}'
                    }, status=status.HTTP_400_BAD_REQUEST)

                for row in ws.iter_rows(min_row=2, values_only=True):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    data.append(row_dict)

                if not data:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'The uploaded XLSX file (sheet: "{sheet_name}") is empty. Please provide at least one data row.'
                    }, status=status.HTTP_400_BAD_REQUEST)

            # ---------- CSV Handling ----------
            elif format_type == 'csv':
                decoded_file = file.read().decode('utf-8')
                dataset = Dataset()
                dataset.load(decoded_file, format='csv')

                for row in dataset.dict:
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    # Validate only required headers
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({
                            "statusCode": 400,
                            "status": True,
                            "message": f'Missing required headers. Required: {required_headers}. Found: {set(row_lower.keys())}.'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    if not any(row_lower.values()):
                        continue
                    data.append(row_lower)

                if not data:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": "The uploaded CSV file is empty. Please provide at least one data row."
                    }, status=status.HTTP_400_BAD_REQUEST)

            else:
                return Response({'error': 'Unsupported file format. Use .xlsx or .csv'}, status=status.HTTP_400_BAD_REQUEST)

            # ---------- Process Each Row ----------
            imported_count = 0
            for row in  reversed(data):
                name = str(row.get('interest level')).strip() if row.get('interest level') else None
                description = str(row.get('description')).strip() if row.get('description') else ''

                if not name:
                    continue  # skip empty mandatory field

                existing = InterestLevel.objects.filter(name__iexact=name).first()

                if existing:
                    if existing.is_deleted:
                        # Reactivate deleted entry
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                    else:
                        # Already active — track as duplicate
                        duplicate_names.append(name)
                        continue
                else:
                    # Create new record
                    InterestLevel.objects.create(
                        name=name,
                        description=description,
                        is_deleted=False
                    )
                    imported_count += 1

        except Exception as e:
            return Response({
                "statusCode": 400,
                "status": True,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": list(set(duplicate_names)),
            "imported_count": imported_count,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful"
        }, status=status.HTTP_200_OK)




#-------------------------------------------Priority---------------------------------


class PriorityCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        name = request.data.get("name", "").strip()

        if not name:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Name field is required."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check if an active priority already exists
        existing = Priority.objects.filter(name__iexact=name, is_deleted=False).first()
        if existing:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Priority with this name already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create new priority
        serializer = PrioritySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Priority created successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        else:
            # Collect error messages
            errors = serializer.errors
            messages = []
            for field, msgs in errors.items():
                messages.extend(msgs)
            message_text = " ".join(messages)

            return Response({
                "statusCode": 400,
                "status": False,
                "message": message_text,
            }, status=status.HTTP_400_BAD_REQUEST)


class PriorityListAPIView(APIView):    
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'updated_at')
        sort_order = request.GET.get('sortOrder', 'desc')  # default to newest first

        allowed_sort_fields = ['name', 'description', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        # Apply descending order for 'desc'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = Priority.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )

        queryset = queryset.order_by(sort_by)

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = PrioritySerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)


class PriorityRetrieveAPIView(APIView):
    def get(self, request, uuid):
        try:
            priority = Priority.objects.get(uuid=uuid, is_deleted=False)
        except Priority.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Priority  not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = PrioritySerializer(priority)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Priority  retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

class PriorityUpdateAPIView(APIView):
    def put(self, request, uuid):
        try:
            category = Priority.objects.get(uuid=uuid, is_deleted=False)
        except Priority.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Priority not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = PrioritySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            new_name = serializer.validated_data.get("name", category.name)
            if Priority.objects.filter(name=new_name).exclude(uuid=uuid).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Priority with this name already exists"
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Priority details updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "statusCode": 400,
            "status": False,
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class PriorityDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        uuids = request.data.get('id', None)

        if uuid:
            try:
                priority = Priority.objects.get(uuid=uuid, is_deleted=False)
                priority.is_deleted = True
                priority.save()
                return Response({
                    "statusCode": 200,
                    "status": True,
                    "message": "Priority deleted successfully",
                    "data": None
                }, status=status.HTTP_200_OK)
            except Priority.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Priority not found",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        # ✅ Case 2: Delete all
        if uuids == "all":
            priorities = Priority.objects.filter(is_deleted=False)
            count = priorities.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No Priorities found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
            priorities.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} Priority(s) deleted successfully.",
                "data": None
            }, status=status.HTTP_200_OK)

        # ✅ Case 3: Bulk delete via UUIDs list
        if not uuids or not isinstance(uuids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide a list of UUIDs in 'uuids' field or 'all'.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate UUIDs
        valid_uuids = []
        invalid_uuids = []
        for u in uuids:
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

        # Fetch priorities that exist and are not deleted
        priorities = Priority.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = priorities.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching Priorities found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_404_NOT_FOUND)

        # Soft delete
        priorities.delete()

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} Priority(s) deleted successfully.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        }, status=status.HTTP_200_OK)


class PriorityExportAPIView(APIView):
    # permission_classes = [IsAuthenticated]  # Uncomment if needed

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')  # optional comma-separated fields
        uuids_param = request.GET.get('uuids', '')  # optional comma-separated uuids

        # Parse UUIDs
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'name': 'Priority',  
            'description': 'Description',
            'is_deleted': 'Deleted',
            'updated_at': 'Modified On',
            
        }


        if fields:
            field_list = [f.strip() for f in fields.split(',')]
        else:
            field_list = list(field_header_map.keys())

            
        # Filter queryset
        queryset = Priority.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')


        # Prepare dataset
        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title="Priority"

        for obj in queryset:
            row = []
            for field in field_list:
                value = getattr(obj, field, '')

                if field in ['created_at', 'updated_at'] and value:
                    # Convert the stored UTC datetime to IST and format it
                    value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
                elif isinstance(value, bool):
                    value = int(value)

                row.append(value if value is not None else '')
            dataset.append(row)

        # Export
        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'priority.csv'
        else:
            # XLSX export with BytesIO
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'priority.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


class PriorityImportAPIView(APIView):
    """
    API to import Priority from CSV or XLSX.
    Priority: mandatory
    Description: optional
    """

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicate_names = []
        data = []

        # Required and optional headers
        required_headers = {'priority'}  # mandatory
        optional_headers = {'description'}  # optional

        try:
            # ---------- XLSX Handling ----------
            if format_type == 'xlsx':
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({
                        'error': 'Please provide sheet_name',
                        'available_sheets': available_sheets
                    }, status=status.HTTP_400_BAD_REQUEST)

                if sheet_name not in available_sheets:
                    return Response({
                        'error': f'Sheet "{sheet_name}" not found in uploaded file',
                        'available_sheets': available_sheets
                    }, status=status.HTTP_400_BAD_REQUEST)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'The uploaded XLSX file (sheet: "{sheet_name}") is empty. Please provide at least one data row.'
                    }, status=status.HTTP_400_BAD_REQUEST)

                headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]

                # Validate only required headers
                if not required_headers.issubset(set(headers)):
                    return Response({
                        "statusCode": 400,
                        "status": True,
                        'message': f'Missing required headers. Required: {required_headers}, Found: {set(headers)}'
                    }, status=status.HTTP_400_BAD_REQUEST)

                for row in ws.iter_rows(min_row=2, values_only=True):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    data.append(row_dict)

                if not data:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'The uploaded XLSX file (sheet: "{sheet_name}") is empty. Please provide at least one data row.'
                    }, status=status.HTTP_400_BAD_REQUEST)

            # ---------- CSV Handling ----------
            elif format_type == 'csv':
                decoded_file = file.read().decode('utf-8')
                dataset = Dataset()
                dataset.load(decoded_file, format='csv')

                for row in dataset.dict:
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    # Validate only required headers
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({
                            "statusCode": 400,
                            "status": True,
                            "message": f'Missing required headers. Required: {required_headers}. Found: {set(row_lower.keys())}.'
                        }, status=status.HTTP_400_BAD_REQUEST)

                    if not any(row_lower.values()):
                        continue
                    data.append(row_lower)

                if not data:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": "The uploaded CSV file is empty. Please provide at least one data row."
                    }, status=status.HTTP_400_BAD_REQUEST)

            else:
                return Response({'error': 'Unsupported file format. Use .xlsx or .csv'}, status=status.HTTP_400_BAD_REQUEST)

            # ---------- Process Each Row ----------
            imported_count = 0
            for row in  reversed(data):
                name = str(row.get('priority')).strip() if row.get('priority') else None
                description = str(row.get('description')).strip() if row.get('description') else ''

                if not name:
                    continue  # skip empty mandatory field

                existing = Priority.objects.filter(name__iexact=name).first()

                if existing:
                    if existing.is_deleted:
                        # Reactivate soft-deleted record
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                    else:
                        # Already active — track duplicate
                        duplicate_names.append(name)
                        continue
                else:
                    # Create new record
                    Priority.objects.create(
                        name=name,
                        description=description,
                        is_deleted=False
                    )
                    imported_count += 1

        except Exception as e:
            return Response({
                "statusCode": 400,
                "status": True,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": list(set(duplicate_names)),
            "imported_count": imported_count,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful"
        }, status=status.HTTP_200_OK)

#-------------------------------------------Tags---------------------------------



class TagsCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        name = request.data.get("name", "").strip()

        if not name:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Name field is required."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check if an active tag with this name already exists
        existing = Tags.objects.filter(name__iexact=name, is_deleted=False).first()
        if existing:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Tag with this name already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create new tag
        serializer = TagsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Tag created successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        else:
            # Collect serializer error messages
            errors = serializer.errors
            messages = []
            for field, msgs in errors.items():
                messages.extend(msgs)
            message_text = " ".join(messages)

            return Response({
                "statusCode": 400,
                "status": False,
                "message": message_text,
            }, status=status.HTTP_400_BAD_REQUEST)

class TagsListAPIView(APIView):    
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'updated_at')
        sort_order = request.GET.get('sortOrder', 'desc')  # default to newest first

        allowed_sort_fields = ['name', 'description', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        # Apply descending order for 'desc'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = Tags.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )

        queryset = queryset.order_by(sort_by)

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = TagsSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)


class TagsRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    def get(self, request, uuid):
        try:
            tag = Tags.objects.get(uuid=uuid, is_deleted=False)
        except Tags.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Tags  not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = TagsSerializer(tag)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Tags  retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class TagsUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    def put(self, request, uuid):
        try:
            category = Tags.objects.get(uuid=uuid, is_deleted=False)
        except Tags.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Tags not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = TagsSerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            new_name = serializer.validated_data.get("name", category.name)
            if Tags.objects.filter(name=new_name).exclude(uuid=uuid).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Tags with this name already exists"
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Tags details updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "statusCode": 400,
            "status": False,
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class TagsDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        uuids = request.data.get('id', None)

        # Single delete via URL parameter
        if uuid:
            try:
                tag = Tags.objects.get(uuid=uuid, is_deleted=False)
                tag.is_deleted = True
                tag.save()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "Tag deleted successfully",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            except Tags.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Tag not found",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        # Delete all if "all" is sent
        if uuids == "all":
            tags = Tags.objects.filter(is_deleted=False)
            count = tags.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No tags found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
            tags.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} tag(s) deleted successfully.",
                "data": None
            }, status=status.HTTP_200_OK)

        # Validate bulk UUIDs
        if not uuids or not isinstance(uuids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide a list of UUIDs in 'id' field or 'all'.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        valid_uuids = []
        invalid_uuids = []
        for u in uuids:
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
        tags = Tags.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = tags.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching tags found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_404_NOT_FOUND)

        tags.delete()

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} tag(s) deleted successfully.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        }, status=status.HTTP_200_OK) 

class TagsExportAPIView(APIView):
    # permission_classes = [IsAuthenticated]  # Uncomment and adjust as needed

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')  
        uuids_param = request.GET.get('uuids', '')

        uuids = [u.strip() for u in uuids_param.split(',') if u]

        # Default fields if none provided
        field_header_map = {
            'uuid': 'UUID',
            'name': 'Tags ',  
            'description': 'Description',
            'is_deleted': 'Deleted',
            'updated_at': 'Modified On',
            
        }

        if fields:
            field_list = [f.strip() for f in fields.split(',')]
        else:
            field_list = list(field_header_map.keys())

        queryset = Tags.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title("Tags")

        for dept in queryset:
            row = []
            for field in field_list:
                value = getattr(dept, field, '')

                if field in ['created_at', 'updated_at'] and value:
                    # Convert the stored UTC datetime to IST and format it
                    value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
                elif isinstance(value, bool):
                    value = int(value)

                row.append(value if value is not None else '')
            dataset.append(row)

        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'tags.csv'
        else:
        # XLSX export with BytesIO
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'tags.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


class TagsImportAPIView(APIView):
    """
    API to import Tags from CSV or XLSX.
    Tags: mandatory
    Description: optional
    """

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')  # optional, for XLSX

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicate_names = []
        data = []

        required_headers = {'tags'}       # mandatory
        optional_headers = {'description'}  # optional

        try:
            # ---------- XLSX Handling ----------
            if format_type == 'xlsx':
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({
                        'error': 'Please provide sheet_name',
                        'available_sheets': available_sheets
                    }, status=status.HTTP_400_BAD_REQUEST)

                if sheet_name not in available_sheets:
                    return Response({
                        'error': f'Sheet "{sheet_name}" not found in uploaded file',
                        'available_sheets': available_sheets
                    }, status=status.HTTP_400_BAD_REQUEST)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'The uploaded XLSX file (sheet: "{sheet_name}") is empty. Provide at least one data row.'
                    }, status=status.HTTP_400_BAD_REQUEST)

                headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]

                if not required_headers.issubset(set(headers)):
                    return Response({
                        "statusCode": 400,
                        "status": True,
                        'message': f'Missing required headers. Required: {required_headers}, Found: {set(headers)}'
                    }, status=status.HTTP_400_BAD_REQUEST)

                for row in ws.iter_rows(min_row=2, values_only=True):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    data.append(row_dict)

            # ---------- CSV Handling ----------
            elif format_type == 'csv':
                decoded_file = file.read().decode('utf-8')
                dataset = Dataset()
                dataset.load(decoded_file, format='csv')

                for row in dataset.dict:
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({
                            "statusCode": 400,
                            "status": True,
                            "message": f'Missing required headers. Required: {required_headers}. Found: {set(row_lower.keys())}.'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    if not any(row_lower.values()):
                        continue
                    data.append(row_lower)

            else:
                return Response({'error': 'Unsupported file format. Use .xlsx or .csv'}, status=status.HTTP_400_BAD_REQUEST)

            # ---------- Process Each Row ----------
            imported_count = 0
            for row in  reversed(data):
                name = str(row.get('tags')).strip() if row.get('tags') else None
                description = str(row.get('description')).strip() if row.get('description') else ''

                if not name:
                    continue  # skip empty mandatory field

                existing = Tags.objects.filter(name__iexact=name).first()

                if existing:
                    if existing.is_deleted:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                    else:
                        duplicate_names.append(name)
                        continue
                else:
                    Tags.objects.create(
                        name=name,
                        description=description,
                        is_deleted=False
                    )
                    imported_count += 1

        except Exception as e:
            return Response({
                "statusCode": 400,
                "status": True,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": list(set(duplicate_names)),
            "imported_count": imported_count,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful"
        }, status=status.HTTP_200_OK)
#-------------------------------------------ActivityType---------------------------------




class ActivityTypeCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        name = request.data.get("name", "").strip()

        if not name:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Name field is required."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check if an active ActivityType with this name already exists
        existing = ActivityType.objects.filter(name__iexact=name, is_deleted=False).first()
        if existing:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Activity Type with this name already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create new ActivityType
        serializer = ActivityTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Activity Type created successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        else:
            # Collect serializer error messages
            errors = serializer.errors
            messages = []
            for field, msgs in errors.items():
                messages.extend(msgs)
            message_text = " ".join(messages)

            return Response({
                "statusCode": 400,
                "status": False,
                "message": message_text,
            }, status=status.HTTP_400_BAD_REQUEST)


class ActivityTypeListAPIView(APIView):    
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'updated_at')
        sort_order = request.GET.get('sortOrder', 'desc')  # default to newest first

        allowed_sort_fields = ['name', 'description', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        # Apply descending order for 'desc'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = ActivityType.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )

        queryset = queryset.order_by(sort_by)

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = ActivityTypeSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)
    
class ActivityTypeRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    def get(self, request, uuid):
        try:
            activitytype = ActivityType.objects.get(uuid=uuid, is_deleted=False)
        except ActivityType.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Activity Type  not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = ActivityTypeSerializer(activitytype)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Activity Type  retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class ActivityTypeUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    def put(self, request, uuid):
        try:
            category = ActivityType.objects.get(uuid=uuid, is_deleted=False)
        except ActivityType.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Activity Type not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = ActivityTypeSerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            new_name = serializer.validated_data.get("name", category.name)
            if ActivityType.objects.filter(name=new_name).exclude(uuid=uuid).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Activity Type with this name already exists"
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Activity Type details updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "statusCode": 400,
            "status": False,
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class ActivityTypeDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        uuids = request.data.get('id', None)

        if uuid:
            try:
                activity = ActivityType.objects.get(uuid=uuid, is_deleted=False)
                activity.is_deleted = True
                activity.save()
                return Response({
                    "statusCode": 200,
                    "status": True,
                    "message": "Activity Type deleted successfully",
                    "data": None
                }, status=status.HTTP_200_OK)
            except ActivityType.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Activity Type not found",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        if uuids == "all":
            activities = ActivityType.objects.filter(is_deleted=False)
            count = activities.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No Activity Types found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
            activities.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} Activity Type(s) deleted successfully.",
                "data": None
            }, status=status.HTTP_200_OK)

        # ✅ Case 3: Bulk delete via UUIDs list
        if not uuids or not isinstance(uuids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide a list of UUIDs in 'uuids' field or 'all'.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate UUIDs
        valid_uuids = []
        invalid_uuids = []
        for u in uuids:
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

        # Fetch ActivityType entries that exist and are not deleted
        activities = ActivityType.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = activities.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching Activity Types found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_404_NOT_FOUND)

        # Soft delete
        activities.delete()

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} Activity Type(s) deleted successfully.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        }, status=status.HTTP_200_OK)


class ActivityTypeExportAPIView(APIView):
    # permission_classes = [IsAuthenticated]  # Uncomment and adjust as needed

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')  
        uuids_param = request.GET.get('uuids', '')

        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'name': 'Activity Type',  
            'description': 'Description',
            'is_deleted': 'Deleted',
            'updated_at': 'Modified On',
            
        }

        # Default fields if none provided
        if fields:
            field_list = [f.strip() for f in fields.split(',')]
        else:
            field_list = list(field_header_map.keys())

        queryset = ActivityType.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')


        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title="ActivityType"


        for dept in queryset:
            row = []
            for field in field_list:
                value = getattr(dept, field, '')

                if field in ['created_at', 'updated_at'] and value:
                    # Convert the stored UTC datetime to IST and format it
                    value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
                elif isinstance(value, bool):
                    value = int(value)

                row.append(value if value is not None else '')
            dataset.append(row)

        
        
        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'ActivityType.csv'
        else:
            # XLSX export with BytesIO
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'ActivityType.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


class ActivityTypeImportAPIView(APIView):
    """
    API to import ActivityType from CSV or XLSX files.
    Mandatory header: Activity Type
    Optional: Description
    """

    def normalize_header(self, header):
        """Normalize headers: lowercase, strip spaces, remove parentheses."""
        if not header:
            return ''
        return header.strip().lower().replace('(', '').replace(')', '')

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')  # optional for XLSX
        duplicate_names = []
        data = []

        required_headers = {'activity type'}
        optional_headers = {'description'}

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()

        try:
            # ---------- XLSX Handling ----------
            if format_type == 'xlsx':
                wb = openpyxl.load_workbook(file, read_only=True)
                ws = wb[sheet_name] if sheet_name else wb.active
                headers = [self.normalize_header(str(cell.value)) for cell in next(ws.iter_rows(min_row=1, max_row=1))]

                if not required_headers.issubset(set(headers)):
                    return Response({
                        "statusCode": 400,
                        "status": True,
                        'message': f'Missing required headers. Required: {required_headers}, Found: {set(headers)}'
                    }, status=status.HTTP_400_BAD_REQUEST)

                for row in ws.iter_rows(min_row=2, values_only=True):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    data.append(row_dict)

            # ---------- CSV Handling ----------
            elif format_type == 'csv':
                decoded_file = file.read().decode('utf-8')
                dataset = Dataset()
                dataset.load(decoded_file, format='csv')

                for row in dataset.dict:
                    row_lower = {self.normalize_header(k): v for k, v in row.items()}
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({
                            "statusCode": 400,
                            "status": True,
                            "message": f'Missing required headers. Required: {required_headers}, Found: {set(row_lower.keys())}.'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    if not any(row_lower.values()):
                        continue
                    data.append(row_lower)

            else:
                return Response({'error': 'Unsupported file format. Use .xlsx or .csv'}, status=status.HTTP_400_BAD_REQUEST)

            # ---------- Process Each Row ----------
            imported_count = 0
            for row in  reversed(data):
                name = str(row.get('activity type')).strip() if row.get('activity type') else None
                description = str(row.get('description')).strip() if row.get('description') else ''

                if not name:
                    continue

                existing = ActivityType.objects.filter(name__iexact=name).first()

                if existing:
                    if existing.is_deleted:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                    else:
                        duplicate_names.append(name)
                        continue
                else:
                    ActivityType.objects.create(
                        name=name,
                        description=description,
                        is_deleted=False
                    )
                    imported_count += 1

        except Exception as e:
            return Response({
                "statusCode": 400,
                "status": True,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": list(set(duplicate_names)),
            "imported_count": imported_count,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful"
        }, status=status.HTTP_200_OK)
#-------------------------------------------LostReasonSerializer---------------------------------
class LostReasonCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        name = request.data.get("name", "").strip()

        if not name:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Name field is required."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check if an active LostReason with this name already exists
        existing = LostReason.objects.filter(name__iexact=name, is_deleted=False).first()
        if existing:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Lost Reason with this name already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create new LostReason
        serializer = LostReasonSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Lost Reason created successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        else:
            # Collect serializer error messages
            errors = serializer.errors
            messages = []
            for field, msgs in errors.items():
                messages.extend(msgs)
            message_text = " ".join(messages)

            return Response({
                "statusCode": 400,
                "status": False,
                "message": message_text,
            }, status=status.HTTP_400_BAD_REQUEST)


        return Response({
            "statusCode": 400,
            "status": False,
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class LostReasonListAPIView(APIView):    
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'updated_at')
        sort_order = request.GET.get('sortOrder', 'desc')  # default to newest first

        allowed_sort_fields = ['name', 'description', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        # Apply descending order for 'desc'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = LostReason.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )

        queryset = queryset.order_by(sort_by)

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = LostReasonSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)

class LostReasonRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    def get(self, request, uuid):
        try:
            lostreason = LostReason.objects.get(uuid=uuid, is_deleted=False)
        except LostReason.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Lost Reason  not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = LostReasonSerializer(lostreason)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Lost Reason  retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class LostReasonUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    def put(self, request, uuid):
        try:
            category = LostReason.objects.get(uuid=uuid, is_deleted=False)
        except LostReason.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Lost Reason not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = LostReasonSerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            new_name = serializer.validated_data.get("name", category.name)
            if LostReason.objects.filter(name=new_name).exclude(uuid=uuid).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Lost Reason with this name already exists"
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Lost Reason  details updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "statusCode": 400,
            "status": False,
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class LostReasonDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        uuids = request.data.get('id', None)

        # ✅ Case 1: Single delete via URL UUID
        if uuid:
            try:
                reason = LostReason.objects.get(uuid=uuid, is_deleted=False)
                reason.is_deleted = True
                reason.save()
                return Response({
                    "statusCode": 200,
                    "status": True,
                    "message": "Lost Reason deleted successfully",
                    "data": None
                }, status=status.HTTP_200_OK)
            except LostReason.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Lost Reason not found",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        # ✅ Case 2: Delete all
        if uuids == "all":
            reasons = LostReason.objects.filter(is_deleted=False)
            count = reasons.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No Lost Reasons found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
            reasons.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} Lost Reason(s) deleted successfully.",
                "data": None
            }, status=status.HTTP_200_OK)

        # ✅ Case 3: Bulk delete via UUIDs list
        if not uuids or not isinstance(uuids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide a list of UUIDs in 'uuids' field or 'all'.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate UUIDs
        valid_uuids = []
        invalid_uuids = []
        for u in uuids:
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

        # Fetch LostReason entries that exist and are not deleted
        reasons = LostReason.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = reasons.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching Lost Reasons found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_404_NOT_FOUND)

        # Soft delete
        reasons.delete()

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} Lost Reason(s) deleted successfully.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        }, status=status.HTTP_200_OK)

class LostReasonExportAPIView(APIView):
    # permission_classes = [IsAuthenticated]  # Uncomment and adjust as needed

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')  
        uuids_param = request.GET.get('uuids', '')

        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'name': 'Lost Reason (B2C)',  
            'description': 'Description',
            'is_deleted': 'Deleted',
            'updated_at': 'Modified On',
            
        }

        if fields:
            field_list = [f.strip() for f in fields.split(',')]
        else:
            field_list = list(field_header_map.keys())

        queryset = LostReason.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title="LostReason(B2C)"

        for dept in queryset:
            row = []
            for field in field_list:
                value = getattr(dept, field, '')

                if field in ['created_at', 'updated_at'] and value:
                    # Convert the stored UTC datetime to IST and format it
                    value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
                elif isinstance(value, bool):
                    value = int(value)

                row.append(value if value is not None else '')
            dataset.append(row)
        
        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'LostReason.csv'
        else:
            # XLSX export with BytesIO
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'LostReasonB2C.xlsx'


        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


class LostReasonImportAPIView(APIView):
    """
    API to import Lost Reasons (B2C) from CSV or XLSX.
    Lost Reason (B2C): mandatory
    Description: optional
    """

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')  # optional for XLSX

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicate_names = []
        data = []

        required_headers = {'lost reason (b2c)'}  # mandatory
        optional_headers = {'description'}       # optional

        try:
            # ---------- XLSX Handling ----------
            if format_type == 'xlsx':
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({
                        'error': 'Please provide sheet_name',
                        'available_sheets': available_sheets
                    }, status=status.HTTP_400_BAD_REQUEST)

                if sheet_name not in available_sheets:
                    return Response({
                        'error': f'Sheet "{sheet_name}" not found in uploaded file',
                        'available_sheets': available_sheets
                    }, status=status.HTTP_400_BAD_REQUEST)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'The uploaded XLSX file (sheet: "{sheet_name}") is empty. Provide at least one data row.'
                    }, status=status.HTTP_400_BAD_REQUEST)

                headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]

                if not required_headers.issubset(set(headers)):
                    return Response({
                        "statusCode": 400,
                        "status": True,
                        'message': f'Missing required headers. Required: {required_headers}, Found: {set(headers)}'
                    }, status=status.HTTP_400_BAD_REQUEST)

                for row in ws.iter_rows(min_row=2, values_only=True):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    data.append(row_dict)

            # ---------- CSV Handling ----------
            elif format_type == 'csv':
                decoded_file = file.read().decode('utf-8')
                dataset = Dataset()
                dataset.load(decoded_file, format='csv')

                for row in dataset.dict:
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({
                            "statusCode": 400,
                            "status": True,
                            "message": f'Missing required headers. Required: {required_headers}. Found: {set(row_lower.keys())}.'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    if not any(row_lower.values()):
                        continue
                    data.append(row_lower)

            else:
                return Response({'error': 'Unsupported file format. Use .xlsx or .csv'}, status=status.HTTP_400_BAD_REQUEST)

            # ---------- Process Each Row ----------
            imported_count = 0
            for row in  reversed(data):
                name = str(row.get('lost reason (b2c)')).strip() if row.get('lost reason (b2c)') else None
                description = str(row.get('description')).strip() if row.get('description') else ''

                if not name:
                    continue

                existing = LostReason.objects.filter(name__iexact=name).first()

                if existing:
                    if existing.is_deleted:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                    else:
                        duplicate_names.append(name)
                        continue
                else:
                    LostReason.objects.create(
                        name=name,
                        description=description,
                        is_deleted=False
                    )
                    imported_count += 1

        except Exception as e:
            return Response({
                "statusCode": 400,
                "status": True,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": list(set(duplicate_names)),
            "imported_count": imported_count,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful"
        }, status=status.HTTP_200_OK)






#-------------------lostreasons(b2b)-----------------------

class LostReasonB2BCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    def post(self, request):
        serializer = LostReasonB2BSerializer(data=request.data)
        if serializer.is_valid():
            if LostReasonB2B.objects.filter(name=serializer.validated_data['name'], is_deleted=False).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Lost Reason  with this name already exists"
                }, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Lost Reason created successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)


        return Response({
            "statusCode": 400,
            "status": False,
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class LostReasonB2BListAPIView(APIView):    
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'updated_at')
        sort_order = request.GET.get('sortOrder', 'desc')  # default to newest first

        allowed_sort_fields = ['name', 'description', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        # Apply descending order for 'desc'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = LostReasonB2B.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )

        queryset = queryset.order_by(sort_by)

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = LostReasonB2BSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)

class LostReasonB2BRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    def get(self, request, uuid):
        try:
            lostreason = LostReasonB2B.objects.get(uuid=uuid, is_deleted=False)
        except LostReasonB2B.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Lost Reason  not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = LostReasonB2BSerializer(lostreason)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Lost Reason  retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class LostReasonB2BUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    def put(self, request, uuid):
        try:
            category = LostReasonB2B.objects.get(uuid=uuid, is_deleted=False)
        except LostReasonB2B.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Lost Reason not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = LostReasonB2BSerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            new_name = serializer.validated_data.get("name", category.name)
            if LostReasonB2B.objects.filter(name=new_name).exclude(uuid=uuid).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Lost Reason with this name already exists"
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Lost Reason  details updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "statusCode": 400,
            "status": False,
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class LostReasonB2BDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        uuids = request.data.get('id', None)

        # ✅ Case 1: Single delete via URL UUID
        if uuid:
            try:
                reason = LostReasonB2B.objects.get(uuid=uuid, is_deleted=False)
                reason.is_deleted = True
                reason.save()
                return Response({
                    "statusCode": 200,
                    "status": True,
                    "message": "Lost Reason deleted successfully",
                    "data": None
                }, status=status.HTTP_200_OK)
            except LostReasonB2B.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Lost Reason not found",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        # ✅ Case 2: Delete all
        if uuids == "all":
            reasons = LostReasonB2B.objects.filter(is_deleted=False)
            count = reasons.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No Lost Reasons found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
            reasons.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} Lost Reason(s) deleted successfully.",
                "data": None
            }, status=status.HTTP_200_OK)

        # ✅ Case 3: Bulk delete via UUIDs list
        if not uuids or not isinstance(uuids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide a list of UUIDs in 'uuids' field or 'all'.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate UUIDs
        valid_uuids = []
        invalid_uuids = []
        for u in uuids:
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

        # Fetch LostReason entries that exist and are not deleted
        reasons = LostReasonB2B.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = reasons.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching Lost Reasons found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_404_NOT_FOUND)

        # Soft delete
        reasons.delete()

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} Lost Reason(s) deleted successfully.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        }, status=status.HTTP_200_OK)



class LostReasonB2BExportAPIView(APIView):
    # permission_classes = [IsAuthenticated]  # Uncomment and adjust as needed

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')  
        uuids_param = request.GET.get('uuids', '')

        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'name': 'Lost Reason (B2B)',  
            'description': 'Description',
            'is_deleted': 'Deleted',
            'updated_at': 'Modified On',
            
        }

        # Default fields if none provided
        if fields:
            field_list = [f.strip() for f in fields.split(',')]
        else:
            field_list = list(field_header_map.keys())


        queryset = LostReasonB2B.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')


        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title="LostReason(B2B)"
        

        for dept in queryset:
            row = []
            for field in field_list:
                value = getattr(dept, field, '')

                if field in ['created_at', 'updated_at'] and value:
                    # Convert the stored UTC datetime to IST and format it
                    value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
                elif isinstance(value, bool):
                    value = int(value)

                row.append(value if value is not None else '')
            dataset.append(row)


        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'LostReasonB2B.csv'
        else:
            # XLSX export with BytesIO
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'LostReasonB2B.xlsx'

        # --- Return response ---
        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response

class LostReasonB2BImportAPIView(APIView):
    

    def normalize_header(self, header):
        """Normalize headers: lowercase, strip spaces, remove parentheses."""
        if not header:
            return ''
        return header.strip().lower().replace('(', '').replace(')', '')

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')  # optional for XLSX
        duplicate_names = []
        data = []

        required_headers = {'lost reason b2b'}
        optional_headers = {'description'}

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()

        try:
            # ---------- XLSX Handling ----------
            if format_type == 'xlsx':
                wb = openpyxl.load_workbook(file, read_only=True)
                ws = wb[sheet_name] if sheet_name else wb.active

                # Read headers and normalize
                headers = [self.normalize_header(str(cell.value)) for cell in next(ws.iter_rows(min_row=1, max_row=1))]

                if not required_headers.issubset(set(headers)):
                    return Response({
                        "statusCode": 400,
                        "status": True,
                        'message': f'Missing required headers. Required: {required_headers}, Found: {set(headers)}'
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Read rows
                for row in ws.iter_rows(min_row=2, values_only=True):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    data.append(row_dict)

            # ---------- CSV Handling ----------
            elif format_type == 'csv':
                decoded_file = file.read().decode('utf-8')
                dataset = Dataset()
                dataset.load(decoded_file, format='csv')

                for row in dataset.dict:
                    row_lower = {self.normalize_header(k): v for k, v in row.items()}
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({
                            "statusCode": 400,
                            "status": True,
                            "message": f'Missing required headers. Required: {required_headers}, Found: {set(row_lower.keys())}.'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    if not any(row_lower.values()):
                        continue
                    data.append(row_lower)

            else:
                return Response({'error': 'Unsupported file format. Use .xlsx or .csv'}, status=status.HTTP_400_BAD_REQUEST)

            # ---------- Process Each Row ----------
            for row in  reversed(data):
                name = str(row.get('lost reason b2b')).strip() if row.get('lost reason b2b') else None
                if not name:
                    continue  # skip empty names
                description = str(row.get('description')).strip() if row.get('description') else ''

                existing = LostReasonB2B.objects.filter(name__iexact=name).first()

                if existing:
                    if existing.is_deleted:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                    else:
                        duplicate_names.append(name)
                        continue
                else:
                    LostReasonB2B.objects.create(
                        name=name,
                        description=description,
                        is_deleted=False
                    )

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": list(set(duplicate_names)),
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful"
        }, status=status.HTTP_200_OK)

# -------------------- EducationLevelCode -------------------- #
class EducationLevelCodeListAPIView(APIView):
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'updated_at')
        sort_order = request.GET.get('sortOrder', 'desc')
        allowed_sort_fields = ['Levelcode', 'created_at']

        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = EducationLevelCode.objects.all()
        if search:
            queryset = queryset.filter(
                Q(Levelcode__icontains=search) |
                Q(description__icontains=search)
            )

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = EducationLevelCodeSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


# ------------------ CREATE ------------------
class EducationLevelCodeListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'updated_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['name', 'description', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = EducationLevelCode.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )

        queryset = queryset.order_by(sort_by)

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = EducationLevelCodeSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)


# ------------------ Create API ------------------
class EducationLevelCodeCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        name = request.data.get("name", "").strip()
        existing = EducationLevelCode.objects.filter(name__iexact=name, is_deleted=False).first()

        if existing:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Education level code with this name already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = EducationLevelCodeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Education level code created successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        else:
            messages = [msg for msgs in serializer.errors.values() for msg in msgs]
            return Response({
                "statusCode": 400,
                "status": False,
                "message": " ".join(messages)
            }, status=status.HTTP_400_BAD_REQUEST)


# ------------------ Retrieve API ------------------

class EducationLevelCodeRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            edu = EducationLevelCode.objects.get(uuid=uuid, is_deleted=False)
        except EducationLevelCode.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Education level code not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = EducationLevelCodeSerializer(edu)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Education level code retrieved successfully",
            "data": serializer.data
        })


# ------------------ Update API ------------------
class EducationLevelCodeUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            edu = EducationLevelCode.objects.get(uuid=uuid, is_deleted=False)
        except EducationLevelCode.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Education level code not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = EducationLevelCodeSerializer(edu, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Education level code updated successfully",
                "data": serializer.data
            })

        messages = [msg for msgs in serializer.errors.values() for msg in msgs]
        return Response({
            "statusCode": 400,
            "status": False,
            "message": " ".join(messages),
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)


# ------------------ Delete API ------------------
class EducationLevelCodeDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get('id', None)

        # Single delete via URL
        if uuid:
            try:
                edu = EducationLevelCode.objects.get(uuid=uuid)
                edu.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "Education level code permanently deleted.",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            except EducationLevelCode.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Education level code not found.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        # Delete all
        if ids == "all":
            queryset = EducationLevelCode.objects.all()
            count = queryset.count()
            queryset.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} education level code(s) permanently deleted.",
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

        queryset = EducationLevelCode.objects.filter(uuid__in=valid_uuids)
        count = queryset.count()
        queryset.delete()

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} education level code(s) permanently deleted.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        }, status=status.HTTP_200_OK)


# ------------------ Export API ------------------
class EducationLevelCodeExportAPIView(APIView):

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')  # comma-separated
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'name': 'Education Level Code',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'updated_at': 'Modified On',
        }

        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())

        queryset = EducationLevelCode.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'EducationLevelCode'

        for edu in queryset:
            row = []
            for field in field_list:
                value = getattr(edu, field, '')
                if field in ['created_at', 'updated_at'] and value:
                    value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
                elif isinstance(value, bool):
                    value = int(value)
                row.append(value if value is not None else '')
            dataset.append(row)

        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'education_level_codes.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'education_level_codes.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


# ------------------ Import API ------------------
class EducationLevelCodeImportAPIView(APIView):

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicate_names = []
        required_headers = {'education level code'}
        optional_headers = {'description'}

        try:
            data = []
            headers = []

            if format_type == 'xlsx':
                import openpyxl
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({'error': 'Please provide sheet_name', 'available_sheets': available_sheets}, status=400)
                if sheet_name not in available_sheets:
                    return Response({'error': f'Sheet "{sheet_name}" not found', 'available_sheets': available_sheets}, status=400)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({"statusCode": 400, "status": False, "message": f'The uploaded XLSX sheet "{sheet_name}" is empty.'}, status=400)

                headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                if not required_headers.issubset(set(headers)):
                    return Response({"statusCode": 400, "status": True, "message": f'Missing required headers. Required: {required_headers}, Found: {set(headers)}'}, status=400)

                for row in ws.iter_rows(min_row=2, values_only=True):
                    if not any(row):
                        continue
                    data.append(dict(zip(headers, row)))

            elif format_type == 'csv':
                decoded_file = file.read().decode('utf-8')
                dataset = Dataset()
                dataset.load(decoded_file, format='csv')

                for row in dataset.dict:
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({"statusCode": 400, "status": True, "message": f'Missing required headers. Required: {required_headers}. Found: {set(row_lower.keys())}'}, status=400)
                    data.append(row_lower)
            else:
                return Response({"statusCode": 400, "status": True, 'error': 'Unsupported file format. Use .xlsx or .csv'}, status=400)

            imported_count = 0
            for row in  reversed(data):
                name = str(row.get('education level code')).strip() if row.get('education level code') else None
                description = str(row.get('description')).strip() if row.get('description') else ''

                if not name:
                    continue

                existing = EducationLevelCode.objects.filter(name__iexact=name).first()
                if existing:
                    if not existing.is_deleted:
                        duplicate_names.append(name)
                        continue
                    else:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    EducationLevelCode.objects.create(name=name, description=description, is_deleted=False)
                    imported_count += 1

        except Exception as e:
            return Response({"statusCode": 400, "status": True, 'message': str(e)}, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": list(set(duplicate_names)),
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count
        }, status=200)




# -------------------- EducationLevel -------------------- #

class EducationLevelListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'updated_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        # Allowed sort fields
        allowed_sort_fields = ['educationlevel', 'description', 'created_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = EducationLevel.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(educationlevel__icontains=search) |
                Q(description__icontains=search)  # optional: search by level_code detail
            )

        queryset = queryset.order_by(sort_by)

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = EducationLevelSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)
    
class EducationLevelCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        educationlevel_name = request.data.get('educationlevel', '').strip()

        # Check for duplicate
        if EducationLevel.objects.filter(educationlevel__iexact=educationlevel_name).exists():
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "This Education Level with the selected Level Code already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        # If no duplicate, create new
        serializer = EducationLevelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Education Level created successfully",
                "data": serializer.data
            })

        # Handle validation errors
        errors = serializer.errors
        messages = []
        for field, msgs in errors.items():
            messages.extend(msgs)

        return Response({
            "statusCode": 400,
            "status": False,
            "message": " ".join(messages)
        }, status=status.HTTP_400_BAD_REQUEST)

class EducationLevelRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = EducationLevel.objects.get(uuid=uuid, is_deleted=False)
        except EducationLevel.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Education Level not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = EducationLevelSerializer(obj)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Education Level retrieved successfully",
            "data": serializer.data
        })


class EducationLevelUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = EducationLevel.objects.get(uuid=uuid, is_deleted=False)
        except EducationLevel.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Education Level not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = EducationLevelSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Education Level updated successfully",
                "data": serializer.data
            })
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


class EducationLevelDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        uuids = request.data.get('id', [])
        if not uuids or not isinstance(uuids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide a list of UUIDs in 'id' field.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        valid_uuids = []
        invalid_uuids = []
        for u in uuids:
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

        objs = EducationLevel.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = objs.count()
        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching Education Levels found.",
                "data": {"invalid_uuids": invalid_uuids}
            }, status=status.HTTP_404_NOT_FOUND)

        objs.delete()
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} Education Level(s) deleted successfully.",
        })


class EducationLevelExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'level_code': 'Education Level Code',
            'educationlevel': 'Education Level',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'created_at': 'Created On',
            'updated_at': 'Modified On',
        }

        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())

        queryset = EducationLevel.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'EducationLevel'

        for obj in queryset:
            row = []
            for field in field_list:
                if field == 'level_code_detail':
                    value = obj.level_code.name if obj.level_code else ''
                else:
                    value = getattr(obj, field, '')
                if field in ['created_at', 'updated_at'] and value:
                    value = timezone.localtime(value).strftime("%d-%m-%Y %I:%M:%S %p")
                elif isinstance(value, bool):
                    value = int(value)
                row.append(value if value is not None else '')
            dataset.append(row)

        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'education_levels.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'education_levels.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


# ------------------ Import API ------------------
class EducationLevelImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicate_levels = []
        required_headers = {'education level code', 'education level'}
        optional_headers = {'description', 'is_deleted'}

        try:
            data = []
            headers = []

            # ---------- XLSX Handling ----------
            if format_type == 'xlsx':
                import openpyxl
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({'error': 'Please provide sheet_name', 'available_sheets': available_sheets}, status=400)
                if sheet_name not in available_sheets:
                    return Response({'error': f'Sheet "{sheet_name}" not found', 'available_sheets': available_sheets}, status=400)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({"statusCode": 400, "status": False, "message": f'The uploaded XLSX sheet "{sheet_name}" is empty.'}, status=400)

                headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                if not required_headers.issubset(set(headers)):
                    return Response({"statusCode": 400, "status": True, "message": f'Missing required headers. Required: {required_headers}, Found: {set(headers)}'}, status=400)

                for row in ws.iter_rows(min_row=2, values_only=True):
                    if not any(row):
                        continue
                    data.append(dict(zip(headers, row)))

            # ---------- CSV Handling ----------
            elif format_type == 'csv':
                import csv
                import io
                decoded_file = file.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(decoded_file))
                for row in reader:
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({"statusCode": 400, "status": True, "message": f'Missing required headers. Required: {required_headers}. Found: {set(row_lower.keys())}'}, status=400)
                    data.append(row_lower)
            else:
                return Response({"statusCode": 400, "status": True, 'error': 'Unsupported file format. Use .xlsx or .csv'}, status=400)

            imported_count = 0
            for row in  reversed(data):
                level_code_id = row.get('education level code')
                education_level_name = str(row.get('education level')).strip() if row.get('education level') else None
                description = str(row.get('description')).strip() if row.get('description') else ''
                is_deleted = bool(int(row.get('is_deleted', 0))) if row.get('is_deleted') is not None else False

                if not level_code_id or not education_level_name:
                    continue

                # Validate LevelCode existence
                if not EducationLevelCode.objects.filter(id=level_code_id).exists():
                    continue

                existing = EducationLevel.objects.filter(level_code_id=level_code_id, educationlevel__iexact=education_level_name).first()
                if existing:
                    if not existing.is_deleted:
                        duplicate_levels.append(education_level_name)
                        continue
                    else:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    EducationLevel.objects.create(
                        level_code_id=level_code_id,
                        educationlevel=education_level_name,
                        description=description,
                        is_deleted=is_deleted
                    )
                    imported_count += 1

        except Exception as e:
            return Response({"statusCode": 400, "status": True, 'message': str(e)}, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": list(set(duplicate_levels)),
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count
        }, status=200)

#----------------------------EducationDuration----------------------


class EducationDurationListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'updated_at')
        sort_order = request.GET.get('sortOrder', 'desc')  # 'asc' or 'desc'

        allowed_sort_fields = ['durations', 'description', 'created_at', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        sort_prefix = '-' if sort_order == 'desc' else ''
        queryset = EducationDuration.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(educationlevel__educationlevel__icontains=search) |
                Q(durations__icontains=search)
            )

        queryset = queryset.order_by(f'{sort_prefix}{sort_by}')

        serializer = EducationDurationSerializer(queryset, many=True)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Education durations retrieved successfully",
            "count": queryset.count(),
            "data": serializer.data
        }, status=status.HTTP_200_OK)

class EducationDurationCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        educationlevel_uuid = request.data.get("educationlevel", "").strip()
        durations = request.data.get("durations", "").strip()

        # Get EducationLevel by UUID
        educationlevel_obj = None
        if educationlevel_uuid:
            try:
                educationlevel_obj = EducationLevel.objects.get(uuid=educationlevel_uuid)
            except EducationLevel.DoesNotExist:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Education level not found for the provided UUID."
                }, status=status.HTTP_400_BAD_REQUEST)

        # Check for duplicates
        existing = EducationDuration.objects.filter(
            educationlevel=educationlevel_obj, 
            durations__iexact=durations, 
            is_deleted=False
        ).first()
        if existing:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Education duration with this level and duration already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Save new EducationDuration
        serializer = EducationDurationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(educationlevel=educationlevel_obj)  # assign object explicitly
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Education duration created successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        messages = [msg for msgs in serializer.errors.values() for msg in msgs]
        return Response({
            "statusCode": 400,
            "status": False,
            "message": " ".join(messages)
        }, status=status.HTTP_400_BAD_REQUEST)
# ------------------ Retrieve API ------------------
class EducationDurationRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = EducationDuration.objects.get(uuid=uuid, is_deleted=False)
        except EducationDuration.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Education duration not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = EducationDurationSerializer(obj)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Education duration retrieved successfully",
            "data": serializer.data
        })


# ------------------ Update API ------------------
class EducationDurationUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = EducationDuration.objects.get(uuid=uuid, is_deleted=False)
        except EducationDuration.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Education duration not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = EducationDurationSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Education duration updated successfully",
                "data": serializer.data
            })

        messages = [msg for msgs in serializer.errors.values() for msg in msgs]
        return Response({
            "statusCode": 400,
            "status": False,
            "message": " ".join(messages),
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)


# ------------------ Delete API ------------------
class EducationDurationDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get('id', None)

        # Single delete via URL
        if uuid:
            try:
                obj = EducationDuration.objects.get(uuid=uuid)
                obj.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "Education duration permanently deleted.",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            except EducationDuration.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Education duration not found.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        # Delete all
        if ids == "all":
            queryset = EducationDuration.objects.all()
            count = queryset.count()
            queryset.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} education durations permanently deleted.",
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

        queryset = EducationDuration.objects.filter(uuid__in=valid_uuids)
        count = queryset.count()
        queryset.delete()

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} education duration(s) permanently deleted.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        }, status=status.HTTP_200_OK)


# ------------------ Export API ------------------
class EducationDurationExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'educationlevel': 'Education Level',
            'durations': 'Education Duration',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'created_at': 'Created On',
            'updated_at': 'Modified On',
        }

        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())

        queryset = EducationDuration.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'EducationDuration'

        for obj in queryset:
            row = []
            for field in field_list:
                if field == 'Education Level':
                    value = obj.educationlevel.educationlevel if obj.educationlevel else ''
                else:
                    value = getattr(obj, field, '')
                if field in ['created_at', 'updated_at'] and value:
                    value = timezone.localtime(value).strftime("%d-%m-%Y %I:%M:%S %p")
                elif isinstance(value, bool):
                    value = int(value)
                row.append(value if value is not None else '')
            dataset.append(row)

        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'education_durations.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'education_durations.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


# ------------------ Import API ------------------
class EducationDurationImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicate_durations = []
        required_headers = {'education level', 'education duration'}
        optional_headers = {'description'}

        try:
            data = []
            headers = []

            if format_type == 'xlsx':
                import openpyxl
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({'error': 'Please provide sheet_name', 'available_sheets': available_sheets}, status=400)
                if sheet_name not in available_sheets:
                    return Response({'error': f'Sheet "{sheet_name}" not found', 'available_sheets': available_sheets}, status=400)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({"statusCode": 400, "status": False, "message": f'The uploaded XLSX sheet "{sheet_name}" is empty.'}, status=400)

                headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                if not required_headers.issubset(set(headers)):
                    return Response({"statusCode": 400, "status": True, "message": f'Missing required headers. Required: {required_headers}, Found: {set(headers)}'}, status=400)

                for row in ws.iter_rows(min_row=2, values_only=True):
                    if not any(row):
                        continue
                    data.append(dict(zip(headers, row)))

            elif format_type == 'csv':
                import csv
                import io
                decoded_file = file.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(decoded_file))
                for row in reader:
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({"statusCode": 400, "status": True, "message": f'Missing required headers. Required: {required_headers}. Found: {set(row_lower.keys())}'}, status=400)
                    data.append(row_lower)
            else:
                return Response({"statusCode": 400, "status": True, 'error': 'Unsupported file format. Use .xlsx or .csv'}, status=400)

            imported_count = 0
            for row in  reversed(data):
                educationlevel_name = str(row.get('education level')).strip() if row.get('education level') else None
                durations = str(row.get('education durations')).strip() if row.get('education durations') else None
                description = str(row.get('description')).strip() if row.get('description') else ''

                if not educationlevel_name or not durations:
                    continue

                # Get education level object
                educationlevel_obj = EducationLevel.objects.filter(educationlevel__iexact=educationlevel_name).first()
                if not educationlevel_obj:
                    continue  # skip row if level not found

                existing = EducationDuration.objects.filter(
                    educationlevel=educationlevel_obj, durations__iexact=durations
                ).first()
                if existing:
                    if not existing.is_deleted:
                        duplicate_durations.append(durations)
                        continue
                    else:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    EducationDuration.objects.create(
                        educationlevel=educationlevel_obj,
                        durations=durations,
                        description=description,
                        is_deleted=False
                    )
                    imported_count += 1

        except Exception as e:
            return Response({"statusCode": 400, "status": True, 'message': str(e)}, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": list(set(duplicate_durations)),
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count
        }, status=200)

    

# -------------------- Studymainarea -------------------- #
class StudymainareaListAPIView(APIView):
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'updated_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['name', 'description', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = Studymainarea.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(description__icontains=search))

        queryset = queryset.order_by(sort_by)

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = StudymainareaSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


# -------------------- CREATE API --------------------
class StudymainareaCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        name = request.data.get("name", "").strip()
        if Studymainarea.objects.filter(name__iexact=name, is_deleted=False).exists():
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Study main area with this name already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = StudymainareaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Study main area created successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        else:
            errors = serializer.errors
            messages = []
            for field, msgs in errors.items():
                messages.extend(msgs)
            return Response({
                "statusCode": 400,
                "status": False,
                "message": " ".join(messages)
            }, status=status.HTTP_400_BAD_REQUEST)


# -------------------- RETRIEVE API --------------------
class StudymainareaRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            area = Studymainarea.objects.get(uuid=uuid, is_deleted=False)
        except Studymainarea.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Study main area not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = StudymainareaSerializer(area)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Study main area retrieved successfully",
            "data": serializer.data
        })


# -------------------- UPDATE API --------------------
class StudymainareaUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            area = Studymainarea.objects.get(uuid=uuid, is_deleted=False)
        except Studymainarea.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Study main area not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = StudymainareaSerializer(area, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Study main area updated successfully",
                "data": serializer.data
            })

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


# -------------------- DELETE API --------------------
class StudymainareaDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get('id', None)

        if uuid:
            try:
                area = Studymainarea.objects.get(uuid=uuid)
                area.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "Study main area permanently deleted.",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            except Studymainarea.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Study main area not found.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        if ids == "all":
            areas = Studymainarea.objects.all()
            count = areas.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No study main areas found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
            areas.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} study main area(s) permanently deleted.",
                "data": None
            }, status=status.HTTP_200_OK)

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

        areas = Studymainarea.objects.filter(uuid__in=valid_uuids)
        count = areas.count()
        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching study main areas found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_404_NOT_FOUND)

        areas.delete()
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} study main area(s) permanently deleted.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        }, status=status.HTTP_200_OK)


# -------------------- EXPORT API --------------------
class StudymainareaExportAPIView(APIView):
    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'name': 'Study Main Area',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'created_at': 'Created On',
            'updated_at': 'Modified On',
        }

        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())

        queryset = Studymainarea.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'StudyMainArea'

        for area in queryset:
            row = []
            for field in field_list:
                value = getattr(area, field, '')
                if field in ['created_at', 'updated_at'] and value:
                    value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
                elif isinstance(value, bool):
                    value = int(value)
                row.append(value if value is not None else '')
            dataset.append(row)

        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'studymainareas.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'studymainareas.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


# -------------------- IMPORT API --------------------
class StudymainareaImportAPIView(APIView):
    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')
        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicate_names = []

        required_headers = {'study main area'}
        optional_headers = {'description'}

        try:
            data = []
            headers = []

            # XLSX
            if format_type == 'xlsx':
                import openpyxl
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({'error': 'Please provide sheet_name', 'available_sheets': available_sheets}, status=400)
                if sheet_name not in available_sheets:
                    return Response({'error': f'Sheet "{sheet_name}" not found', 'available_sheets': available_sheets}, status=400)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({'statusCode': 400, 'status': False, 'message': 'Sheet is empty'}, status=400)

                headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                if not required_headers.issubset(set(headers)):
                    return Response({'statusCode': 400, 'status': True, 'message': f'Missing required headers: {required_headers}'}, status=400)

                for row in ws.iter_rows(min_row=2, values_only=True):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    data.append(row_dict)

            # CSV
            elif format_type == 'csv':
                decoded_file = file.read().decode('utf-8')
                dataset = Dataset()
                dataset.load(decoded_file, format='csv')
                for row in dataset.dict:
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({'statusCode': 400, 'status': True, 'message': f'Missing required headers: {required_headers}'}, status=400)
                    data.append(row_lower)
            else:
                return Response({'statusCode': 400, 'status': True, 'error': 'Unsupported file format. Use .xlsx or .csv'}, status=400)

            imported_count = 0

            for row in  reversed(data):
                name = str(row.get('study main area')).strip() if row.get('study main area') else None
                description = str(row.get('description')).strip() if row.get('description') else ''

                if not name:
                    continue

                existing = Studymainarea.objects.filter(name__iexact=name).first()
                if existing:
                    if not existing.is_deleted:
                        duplicate_names.append(name)
                        continue
                    else:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    Studymainarea.objects.create(name=name, description=description, is_deleted=False)
                    imported_count += 1

        except Exception as e:
            return Response({'statusCode': 400, 'status': True, 'message': str(e)}, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": list(set(duplicate_names)),
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count
        }, status=status.HTTP_200_OK)



# -------------------- Studymajor -------------------- #

class StudyMajorAreaListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'updated_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['majorarea', 'description', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = Studymajorarea.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(majorarea__icontains=search) |
                Q(description__icontains=search) |
                Q(mainarea__name__icontains=search)
            )

        queryset = queryset.order_by(sort_by)

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = StudyMajorAreaSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)


class StudyMajorAreaCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        majorarea = request.data.get("majorarea", "").strip()
        mainarea_uuid = request.data.get("mainarea_uuid")  # accept UUID

        # Resolve UUID to object for existence check
        mainarea_obj = None
        if mainarea_uuid:
            mainarea_obj = Studymainarea.objects.filter(uuid=mainarea_uuid).first()
            if not mainarea_obj:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Invalid main area UUID."
                }, status=status.HTTP_400_BAD_REQUEST)

        # Check duplicates
        existing = Studymajorarea.objects.filter(
            majorarea__iexact=majorarea,
            mainarea=mainarea_obj,
            is_deleted=False
        ).first()

        if existing:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Study Major Area with this name and main area already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = StudyMajorAreaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Study Major Area created successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        messages = [msg for msgs in serializer.errors.values() for msg in msgs]
        return Response({
            "statusCode": 400,
            "status": False,
            "message": " ".join(messages)
        }, status=status.HTTP_400_BAD_REQUEST)  


# ------------------ Retrieve API ------------------
class StudyMajorAreaRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = Studymajorarea.objects.get(uuid=uuid, is_deleted=False)
        except Studymajorarea.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Study Major Area not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = StudyMajorAreaSerializer(obj)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Study Major Area retrieved successfully",
            "data": serializer.data
        })


# ------------------ Update API ------------------
class StudyMajorAreaUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = Studymajorarea.objects.get(uuid=uuid, is_deleted=False)
        except Studymajorarea.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Study Major Area not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = StudyMajorAreaSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Study Major Area updated successfully",
                "data": serializer.data
            })

        messages = [msg for msgs in serializer.errors.values() for msg in msgs]
        return Response({
            "statusCode": 400,
            "status": False,
            "message": " ".join(messages),
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)


# ------------------ Delete API ------------------
class StudyMajorAreaDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get('id', None)

        # Single delete via URL
        if uuid:
            try:
                obj = Studymajorarea.objects.get(uuid=uuid)
                obj.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "Study Major Area permanently deleted.",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            except Studymajorarea.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Study Major Area not found.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        # Delete all
        if ids == "all":
            queryset = Studymajorarea.objects.all()
            count = queryset.count()
            queryset.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} study major areas permanently deleted.",
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

        queryset = Studymajorarea.objects.filter(uuid__in=valid_uuids)
        count = queryset.count()
        queryset.delete()

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} study major area(s) permanently deleted.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        }, status=status.HTTP_200_OK)


# ------------------ Export API ------------------
class StudyMajorAreaExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'mainarea': 'Study Main Area',
            'majorarea': 'Study Major Area',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'created_at': 'Created On',
            'updated_at': 'Modified On',
        }

        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())

        queryset = Studymajorarea.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'StudyMajorArea'

        for obj in queryset:
            row = []
            for field in field_list:
                if field == 'mainarea_name':
                    value = obj.mainarea.name if obj.mainarea else ''
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
            file_name = 'study_major_areas.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'study_major_areas.xlsx'

        response = io.BytesIO(file_data) if format_type == 'csv' else HttpResponse(file_data.getvalue(), content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


# ------------------ Import API ------------------
class StudyMajorAreaImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicate_names = []
        required_headers = {'study major area', 'study main area'}
        optional_headers = {'description'}

        try:
            data = []
            headers = []

            if format_type == 'xlsx':
                import openpyxl
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({'error': 'Please provide sheet_name', 'available_sheets': available_sheets}, status=400)
                if sheet_name not in available_sheets:
                    return Response({'error': f'Sheet "{sheet_name}" not found', 'available_sheets': available_sheets}, status=400)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({"statusCode": 400, "status": False, "message": f'The uploaded XLSX sheet "{sheet_name}" is empty.'}, status=400)

                headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                if not required_headers.issubset(set(headers)):
                    return Response({"statusCode": 400, "status": True, "message": f'Missing required headers. Required: {required_headers}, Found: {set(headers)}'}, status=400)

                for row in ws.iter_rows(min_row=2, values_only=True):
                    if not any(row):
                        continue
                    data.append(dict(zip(headers, row)))

            elif format_type == 'csv':
                import csv
                import io
                decoded_file = file.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(decoded_file))
                for row in reader:
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({"statusCode": 400, "status": True, "message": f'Missing required headers. Required: {required_headers}. Found: {set(row_lower.keys())}'}, status=400)
                    data.append(row_lower)
            else:
                return Response({"statusCode": 400, "status": True, 'error': 'Unsupported file format. Use .xlsx or .csv'}, status=400)

            imported_count = 0
            for row in  reversed(data):
                majorarea_name = str(row.get('study major area')).strip() if row.get('study major area') else None
                mainarea_name = str(row.get('study main area')).strip() if row.get('study main area') else None
                description = str(row.get('description')).strip() if row.get('description') else ''

                if not majorarea_name or not mainarea_name:
                    continue

                # Get mainarea object
                mainarea_obj = Studymainarea.objects.filter(name__iexact=mainarea_name).first()
                if not mainarea_obj:
                    continue  # skip row if mainarea not found

                existing = Studymajorarea.objects.filter(majorarea__iexact=majorarea_name, mainarea=mainarea_obj).first()
                if existing:
                    if not existing.is_deleted:
                        duplicate_names.append(majorarea_name)
                        continue
                    else:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    Studymajorarea.objects.create(
                        majorarea=majorarea_name,
                        mainarea=mainarea_obj,
                        description=description,
                        is_deleted=False
                    )
                    imported_count += 1

        except Exception as e:
            return Response({"statusCode": 400, "status": True, 'message': str(e)}, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": list(set(duplicate_names)),
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count
        }, status=200)

# -------------------- Studyspecialisation -------------------- #


class StudySpecialisationListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'updated_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['studyspecialisation', 'description', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = StudySpecialisation.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(studyspecialisation__icontains=search) |
                Q(description__icontains=search) |
                Q(mainarea__name__icontains=search) |
                Q(majorarea__majorarea__icontains=search)
            )

        queryset = queryset.order_by(sort_by)

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = StudySpecialisationSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)



class StudySpecialisationCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        studyspecialisation = request.data.get("studyspecialisation", "").strip()
        majorarea_uuid = request.data.get("majorarea_id")

        # validate major area UUID
        majorarea = Studymajorarea.objects.filter(uuid=majorarea_uuid, is_deleted=False).first()
        if not majorarea:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Invalid Major Area UUID."
            }, status=status.HTTP_400_BAD_REQUEST)

        # prevent duplicate within same major area
        existing = StudySpecialisation.objects.filter(
            studyspecialisation__iexact=studyspecialisation,
            majorarea=majorarea,
            is_deleted=False
        ).first()
        if existing:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Study Specialisation with this name and Major Area already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        # save normally using serializer
        serializer = StudySpecialisationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Study Specialisation created successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        # handle validation errors
        messages = [msg for msgs in serializer.errors.values() for msg in msgs]
        return Response({
            "statusCode": 400,
            "status": False,
            "message": " ".join(messages)
        }, status=status.HTTP_400_BAD_REQUEST)

# ------------------ Retrieve API ------------------
class StudySpecialisationRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = StudySpecialisation.objects.get(uuid=uuid, is_deleted=False)
        except StudySpecialisation.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Study Specialisation not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = StudySpecialisationSerializer(obj)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Study Specialisation retrieved successfully",
            "data": serializer.data
        })


# ------------------ Update API ------------------
class StudySpecialisationUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = StudySpecialisation.objects.get(uuid=uuid, is_deleted=False)
        except StudySpecialisation.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Study Specialisation not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = StudySpecialisationSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Study Specialisation updated successfully",
                "data": serializer.data
            })

        messages = [msg for msgs in serializer.errors.values() for msg in msgs]
        return Response({
            "statusCode": 400,
            "status": False,
            "message": " ".join(messages),
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)


# ------------------ Delete API ------------------
class StudySpecialisationDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get('id', None)

        # Single delete via URL
        if uuid:
            try:
                obj = StudySpecialisation.objects.get(uuid=uuid)
                obj.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "Study Specialisation permanently deleted.",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            except StudySpecialisation.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Study Specialisation not found.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        # Delete all
        if ids == "all":
            queryset = StudySpecialisation.objects.all()
            count = queryset.count()
            queryset.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} Study Specialisations permanently deleted.",
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

        queryset = StudySpecialisation.objects.filter(uuid__in=valid_uuids)
        count = queryset.count()
        queryset.delete()

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} Study Specialisation(s) permanently deleted.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        }, status=status.HTTP_200_OK)


# ------------------ Export API ------------------
class StudySpecialisationExportAPIView(APIView):

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'mainarea_name': 'Study Main Area',
            'majorarea_name': 'Study Major Area',
            'studyspecialisation': 'Study Specialisation',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'created_at': 'Created On',
            'updated_at': 'Modified On',
        }

        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())

        queryset = StudySpecialisation.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'StudySpecialisation'

        for obj in queryset:
            row = []
            for field in field_list:
                if field == 'mainarea':
                    value = obj.mainarea.name if obj.mainarea else ''
                elif field == 'majorarea':
                    value = obj.majorarea.majorarea if obj.majorarea else ''
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
            file_name = 'study_specialisations.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'study_specialisations.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


# ------------------ Import API ------------------
class StudySpecialisationImportAPIView(APIView):

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicate_names = []
        required_headers = {'study specialisation', 'study major area', 'study main area'}
        optional_headers = {'description'}

        try:
            data = []
            headers = []

            if format_type == 'xlsx':
                import openpyxl
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({'error': 'Please provide sheet_name', 'available_sheets': available_sheets}, status=400)
                if sheet_name not in available_sheets:
                    return Response({'error': f'Sheet "{sheet_name}" not found', 'available_sheets': available_sheets}, status=400)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({"statusCode": 400, "status": False, "message": f'The uploaded XLSX sheet "{sheet_name}" is empty.'}, status=400)

                headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                if not required_headers.issubset(set(headers)):
                    return Response({"statusCode": 400, "status": True, "message": f'Missing required headers. Required: {required_headers}, Found: {set(headers)}'}, status=400)

                for row in ws.iter_rows(min_row=2, values_only=True):
                    if not any(row):
                        continue
                    data.append(dict(zip(headers, row)))

            elif format_type == 'csv':
                import csv
                import io
                decoded_file = file.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(decoded_file))
                for row in reader:
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({"statusCode": 400, "status": True, "message": f'Missing required headers. Required: {required_headers}. Found: {set(row_lower.keys())}'}, status=400)
                    data.append(row_lower)
            else:
                return Response({"statusCode": 400, "status": True, 'error': 'Unsupported file format. Use .xlsx or .csv'}, status=400)

            imported_count = 0
            for row in  reversed(data):
                studyspecialisation = str(row.get('study specialisation')).strip() if row.get('study specialisation') else None
                majorarea_name = str(row.get('study major area')).strip() if row.get('study  major area') else None
                mainarea_name = str(row.get('study main area')).strip() if row.get('study main area') else None
                description = str(row.get('description')).strip() if row.get('description') else ''

                if not studyspecialisation or not majorarea_name or not mainarea_name:
                    continue

                # Fetch mainarea object
                mainarea_obj = Studymainarea.objects.filter(mainarea__iexact=mainarea_name).first()
                if not mainarea_obj:
                    continue  # skip row if main area not found

                # Fetch majorarea object and make sure it belongs to this mainarea
                majorarea_obj = Studymajorarea.objects.filter(
                    majorarea__iexact=majorarea_name,
                    mainarea=mainarea_obj
                ).first()
                if not majorarea_obj:
                    continue  # skip row if major area not found or doesn't belong to mainarea

                # Existing check
                existing = StudySpecialisation.objects.filter(
                    studyspecialisation__iexact=studyspecialisation,
                    majorarea=majorarea_obj
                ).first()

                if existing:
                    if not existing.is_deleted:
                        duplicate_names.append(studyspecialisation)
                        continue
                    else:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    StudySpecialisation.objects.create(
                        studyspecialisation=studyspecialisation,
                        majorarea=majorarea_obj,
                        description=description,
                        is_deleted=False
                    )
                    imported_count += 1

        except Exception as e:
            return Response({"statusCode": 400, "status": True, 'message': str(e)}, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": list(set(duplicate_names)),
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count
        }, status=200)


# -------------------- AcademicResultType -------------------- 
class AcademicResultTypeListAPIView(APIView):
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'updated_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['name', 'description', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = AcademicResultType.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )

        queryset = queryset.order_by(sort_by)

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = AcademicResultTypeSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


# --------------------- Create API ---------------------
class AcademicResultTypeCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        name = request.data.get("name", "").strip()
        if AcademicResultType.objects.filter(name__iexact=name, is_deleted=False).exists():
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Academic Result Type with this name already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = AcademicResultTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Academic Result Type created successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        message_text = " ".join([str(msg) for msgs in serializer.errors.values() for msg in msgs])
        return Response({
            "statusCode": 400,
            "status": False,
            "message": message_text
        }, status=status.HTTP_400_BAD_REQUEST)


# --------------------- Retrieve API ---------------------
class AcademicResultTypeRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = AcademicResultType.objects.get(uuid=uuid, is_deleted=False)
        except AcademicResultType.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Academic Result Type not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = AcademicResultTypeSerializer(obj)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Academic Result Type retrieved successfully",
            "data": serializer.data
        })


# --------------------- Update API ---------------------
class AcademicResultTypeUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = AcademicResultType.objects.get(uuid=uuid, is_deleted=False)
        except AcademicResultType.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Academic Result Type not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = AcademicResultTypeSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Academic Result Type updated successfully",
                "data": serializer.data
            })

        message_text = " ".join([str(msg) for msgs in serializer.errors.values() for msg in msgs])
        return Response({
            "statusCode": 400,
            "status": False,
            "message": message_text,
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)


# --------------------- Delete API ---------------------
class AcademicResultTypeDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get('id', None)

        # Single delete via URL
        if uuid:
            try:
                obj = AcademicResultType.objects.get(uuid=uuid)
                obj.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "Academic Result Type permanently deleted.",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            except AcademicResultType.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Academic Result Type not found.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        # Delete all
        if ids == "all":
            queryset = AcademicResultType.objects.all()
            count = queryset.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No Academic Result Types found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
            queryset.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} Academic Result Type(s) permanently deleted.",
                "data": None
            })

        # Bulk delete via list of UUIDs
        if not ids or not isinstance(ids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Provide a list of UUIDs in 'id' field or 'all'.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        valid_uuids = []
        invalid_uuids = []
        for u in ids:
            try:
                valid_uuids.append(UUID(u))
            except ValueError:
                invalid_uuids.append(u)

        queryset = AcademicResultType.objects.filter(uuid__in=valid_uuids)
        count = queryset.count()
        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching Academic Result Types found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_404_NOT_FOUND)

        queryset.delete()
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} Academic Result Type(s) permanently deleted.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        })


# --------------------- Export API ---------------------
class AcademicResultTypeExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
 
    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]
 
        field_header_map = {
            'uuid': 'UUID',
            'name': 'Academic Result Type',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'updated_at': 'Modified On',
            'created_at': 'Created On',
        }
 
        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())
 
        queryset = AcademicResultType.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')
 
        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'AcademicResultType'
 
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
            file_name = 'academic_result_types.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'academic_result_types.xlsx'
 
        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response
 
 
# --------------------- Import API ---------------------
class AcademicResultTypeImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
 
    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')
 
        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)
 
        format_type = file.name.split('.')[-1].lower()
        duplicate_names = []
 
        required_headers = {'academic result type'}
        optional_headers = {'description'}
 
        try:
            data = []
 
            if format_type == 'xlsx':
                import openpyxl
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames
 
                if not sheet_name:
                    return Response({
                        'error': 'Please provide sheet_name',
                        'available_sheets': available_sheets
                    }, status=status.HTTP_400_BAD_REQUEST)
                if sheet_name not in available_sheets:
                    return Response({
                        'error': f'Sheet "{sheet_name}" not found',
                        'available_sheets': available_sheets
                    }, status=status.HTTP_400_BAD_REQUEST)
 
                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'The uploaded XLSX file is empty.'
                    }, status=status.HTTP_400_BAD_REQUEST)
 
                headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                if not required_headers.issubset(set(headers)):
                    return Response({
                        "statusCode": 400,
                        "status": True,
                        'message': f'Missing required headers. Required: {required_headers}, Found: {set(headers)}'
                    }, status=status.HTTP_400_BAD_REQUEST)
 
                for row in ws.iter_rows(min_row=2, values_only=True):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    data.append(row_dict)
 
            elif format_type == 'csv':
                decoded_file = file.read().decode('utf-8')
                dataset = Dataset()
                dataset.load(decoded_file, format='csv')
 
                for row in dataset.dict:
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({
                            "statusCode": 400,
                            "status": True,
                            "message": f'Missing required headers. Required: {required_headers}'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    data.append(row_lower)
            else:
                return Response({
                    "statusCode": 400,
                    "status": True,
                    'error': 'Unsupported file format. Use .xlsx or .csv'
                }, status=status.HTTP_400_BAD_REQUEST)
 
            imported_count = 0
            for row in  reversed(data):
                name = str(row.get('name')).strip() if row.get('name') else None
                description = str(row.get('description')).strip() if row.get('description') else ''
 
                if not name:
                    continue
 
                existing = AcademicResultType.objects.filter(name__iexact=name).first()
                if existing:
                    if not existing.is_deleted:
                        duplicate_names.append(name)
                        continue
                    else:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    AcademicResultType.objects.create(
                        name=name,
                        description=description,
                        is_deleted=False
                    )
                    imported_count += 1
 
        except Exception as e:
            return Response({
                "statusCode": 400,
                "status": True,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
 
        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": list(set(duplicate_names)),
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count
        }, status=status.HTTP_200_OK)
 
# -------------------- AcademicResult -------------------- #


class AcademicResultListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Optional search query parameters
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'updated_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        # Allowed sort fields
        allowed_sort_fields = ['Academicresult', 'description', 'created_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        # Initial queryset filtered for non-deleted results
        queryset = AcademicResult.objects.filter(is_deleted=False)

        # Apply search filter if search query is provided
        if search:
            queryset = queryset.filter(
                Q(Academicresult__icontains=search) |
                Q(description__icontains=search) |
                Q(AcademicResulttype____icontains=search)  # Assuming you want to search by AcademicResulttype
            )

        # Sorting
        queryset = queryset.order_by(sort_by)

        # Pagination
        paginator = CustomPagination()  # CustomPagination should be implemented in your project
        result_page = paginator.paginate_queryset(queryset, request)
        
        serializer = AcademicResultSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)








class AcademicResultCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        serializer = AcademicResultSerializer(data=request.data)
        
        # Check if serializer is valid
        if serializer.is_valid():
            # Prevent duplicate: same type + result
            academic_type = serializer.validated_data.get('AcademicResulttype')
            academic_result_text = serializer.validated_data.get('Academicresult', '').strip()
            
            if AcademicResult.objects.filter(
                AcademicResulttype=academic_type,
                Academicresult__iexact=academic_result_text,
                is_deleted=False
            ).exists():
                return Response({
                    "status": False,
                    "statusCode": 400,
                    "message": "This Academic Result already exists for the selected type.",
                    "data": None
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Save the object
            academic_result_obj = serializer.save()
            
            return Response({
                "status": True,
                "statusCode": 200,
                "message": "Academic Result created successfully.",
                "data": AcademicResultSerializer(academic_result_obj).data
            }, status=status.HTTP_201_CREATED)
        
        # If serializer invalid
        return Response({
            "status": False,
            "statusCode": 400,
            "message": "Validation error",
            "data": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)



class AcademicResultRetrieveAPIView(APIView):
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
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = AcademicResultSerializer(obj)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Academic Result retrieved successfully",
            "data": serializer.data
        })


class AcademicResultUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        # 1. Fetch the AcademicResult object
        try:
            obj = AcademicResult.objects.get(uuid=uuid, is_deleted=False)
        except AcademicResult.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Academic Result not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        # 2. Get the UUID from request and fetch the corresponding AcademicResultType object
        academic_type_uuid = request.data.get('AcademicResulttype_id')
        academic_type_obj = None

        if academic_type_uuid:
            try:
                academic_type_obj = AcademicResultType.objects.get(uuid=academic_type_uuid)
            except AcademicResultType.DoesNotExist:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Invalid AcademicResultType UUID"
                }, status=status.HTTP_400_BAD_REQUEST)

        # 3. Check uniqueness
        academic_result = request.data.get('Academicresult', '').strip()
        if AcademicResult.objects.filter(
            AcademicResulttype=academic_type_obj,
            Academicresult__iexact=academic_result
        ).exclude(uuid=uuid).exists():
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "This Academic Result already exists for the selected type."
            }, status=status.HTTP_400_BAD_REQUEST)

        # 4. Serialize and save
        serializer = AcademicResultSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Academic Result updated successfully",
                "data": serializer.data
            })

        # 5. Handle validation errors
        errors = serializer.errors
        messages = []
        for field, msgs in errors.items():
            messages.extend(msgs)
        return Response({
            "statusCode": 400,
            "status": False,
            "message": " ".join(messages)
        }, status=status.HTTP_400_BAD_REQUEST)



class AcademicResultDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        uuids = request.data.get('id', [])
        if not uuids or not isinstance(uuids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide a list of UUIDs in 'id' field."
            }, status=status.HTTP_400_BAD_REQUEST)

        valid_uuids = []
        invalid_uuids = []
        for u in uuids:
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

        objs = AcademicResult.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = objs.count()
        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching Academic Results found.",
                "data": {"invalid_uuids": invalid_uuids}
            }, status=status.HTTP_404_NOT_FOUND)

        objs.delete()
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} Academic Result(s) deleted successfully."
        })


class AcademicResultExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        # Field mapping for export headers
        field_header_map = {
            'uuid': 'UUID',
            'AcademicResulttype_id': 'Academic Result Type',
            'Academicresult': 'Academic Result',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'created_at': 'Created On',
            'updated_at': 'Modified On',
        }

        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())

        queryset = AcademicResult.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'AcademicResults'

        for obj in queryset:
            row = []
            for field in field_list:
                if field == 'AcademicResulttype':
                    value = obj.AcademicResulttype.Academicresulttype if obj.AcademicResulttype else ''
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
            file_name = 'academic_results.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'academic_results.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response

class AcademicResultImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicate_results = []
        imported_count = 0

        required_headers = {'academic result', 'academic result type'}
        optional_headers = {'description', 'is_deleted'}

        try:
            data = []

            if format_type == 'xlsx':
                import openpyxl
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({'error': 'Please provide sheet_name', 'available_sheets': available_sheets}, status=400)
                if sheet_name not in available_sheets:
                    return Response({'error': f'Sheet "{sheet_name}" not found', 'available_sheets': available_sheets}, status=400)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({"statusCode": 400, "status": False, "message": f'The uploaded XLSX sheet "{sheet_name}" is empty.'}, status=400)

                headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                if not required_headers.issubset(set(headers)):
                    return Response({"statusCode": 400, "status": True, "message": f'Missing required headers. Required: {required_headers}, Found: {set(headers)}'}, status=400)

                for row in ws.iter_rows(min_row=2, values_only=True):
                    if not any(row):
                        continue
                    data.append(dict(zip(headers, row)))

            elif format_type == 'csv':
                import csv
                import io
                decoded_file = file.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(decoded_file))
                for row in reader:
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({"statusCode": 400, "status": True, "message": f'Missing required headers. Required: {required_headers}. Found: {set(row_lower.keys())}'}, status=400)
                    data.append(row_lower)
            else:
                return Response({"statusCode": 400, "status": True, 'error': 'Unsupported file format. Use .xlsx or .csv'}, status=400)

            for row in  reversed(data):
                academic_result_name = str(row.get('academic result')).strip() if row.get('academicresult') else None
                academic_type_name_or_uuid = row.get('academicresulttype')

                if not academic_result_name or not academic_type_name_or_uuid:
                    continue

                # Fetch AcademicResultType object
                academic_type_obj = None
                if self.is_valid_uuid(academic_type_name_or_uuid):
                    academic_type_obj = AcademicResultType.objects.filter(uuid=academic_type_name_or_uuid).first()
                if not academic_type_obj:
                    academic_type_obj = AcademicResultType.objects.filter(name__iexact=academic_type_name_or_uuid).first()
                if not academic_type_obj:
                    continue  # skip row if type not found

                # Check existing
                existing = AcademicResult.objects.filter(
                    AcademicResulttype=academic_type_obj,
                    Academicresult__iexact=academic_result_name
                ).first()

                if existing:
                    if not existing.is_deleted:
                        duplicate_results.append(academic_result_name)
                        continue
                    else:
                        existing.description = row.get('description', '')
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    AcademicResult.objects.create(
                        AcademicResulttype=academic_type_obj,
                        Academicresult=academic_result_name,
                        description=row.get('description', ''),
                        is_deleted=row.get('is_deleted', False)
                    )
                    imported_count += 1

        except Exception as e:
            return Response({"statusCode": 400, "status": True, 'message': str(e)}, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": list(set(duplicate_results)),
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count
        }, status=200)




# -------------------- EducationType CRUD -------------------- #

class EducationTypeListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'updated_at')
        sort_order = request.GET.get('sortOrder', 'desc')  # default to newest first

        allowed_sort_fields = ['educationType', 'Perticulars', 'created_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        # Apply descending order for 'desc'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = EducationType.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(educationType__icontains=search) |
                Q(Perticulars__icontains=search)
            )

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = EducationTypeSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    

class EducationTypeCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        name = request.data.get('educationType', '').strip()
        if EducationType.objects.filter(educationType__iexact=name, is_deleted=False).exists():
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Education Type with this name already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = EducationTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Education Type created successfully",
                "data": serializer.data
            })

        return Response({
            "statusCode": 400,
            "status": False,
            "message": " ".join([m for msgs in serializer.errors.values() for m in msgs])
        }, status=status.HTTP_400_BAD_REQUEST)


class EducationTypeRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = EducationType.objects.get(uuid=uuid, is_deleted=False)
        except EducationType.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Education Type not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = EducationTypeSerializer(obj)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Education Type retrieved successfully",
            "data": serializer.data
        })


class EducationTypeUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = EducationType.objects.get(uuid=uuid, is_deleted=False)
        except EducationType.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Education Type not found"
            }, status=status.HTTP_404_NOT_FOUND)

        name = request.data.get('educationType', '').strip()
        if EducationType.objects.filter(educationType__iexact=name).exclude(uuid=uuid).exists():
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Education Type with this name already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = EducationTypeSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Education Type updated successfully",
                "data": serializer.data
            })

        return Response({
            "statusCode": 400,
            "status": False,
            "message": " ".join([m for msgs in serializer.errors.values() for m in msgs])
        }, status=status.HTTP_400_BAD_REQUEST)


class EducationTypeDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        uuids = request.data.get('id', [])
        if not uuids or not isinstance(uuids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide a list of UUIDs in 'id'."
            }, status=status.HTTP_400_BAD_REQUEST)

        valid_uuids = []
        invalid_uuids = []
        for u in uuids:
            try:
                valid_uuids.append(UUID(u))
            except ValueError:
                invalid_uuids.append(u)

        objs = EducationType.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = objs.count()
        objs.delete()

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} Education Type(s) deleted successfully",
            "invalid_uuids": invalid_uuids
        })


class EducationTypeExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
 
    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]
 
        field_header_map = {
            'uuid': 'UUID',
            'educationType': 'Education Type',
            'Perticulars': 'Particulars',
            'is_deleted': 'Deleted',
            'created_at': 'Created On',
            'updated_at': 'Updated On',
        }
 
        if fields:
            field_list = [f.strip() for f in fields.split(',')]
        else:
            field_list = list(field_header_map.keys())
 
        queryset = EducationType.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')
 
        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'EducationType'
 
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
            file_name = 'education-type.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'education-type.xlsx'
 
        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response
 
 
class EducationTypeImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
 
    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')
 
        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)
 
        format_type = file.name.split('.')[-1].lower()
        duplicate_names = []
 
        required_headers = {'education type'}
        optional_headers = {'perticulars'}
 
        try:
            data = []
            headers = []
 
            # XLSX
            if format_type == 'xlsx':
                import openpyxl
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames
 
                if not sheet_name:
                    return Response({
                        'error': 'Please provide sheet_name',
                        'available_sheets': available_sheets
                    }, status=status.HTTP_400_BAD_REQUEST)
 
                if sheet_name not in available_sheets:
                    return Response({
                        'error': f'Sheet "{sheet_name}" not found',
                        'available_sheets': available_sheets
                    }, status=status.HTTP_400_BAD_REQUEST)
 
                ws = wb[sheet_name]
 
                headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                if not required_headers.issubset(set(headers)):
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'Missing required headers. Required: {required_headers}'
                    }, status=status.HTTP_400_BAD_REQUEST)
 
                for row in ws.iter_rows(min_row=2, values_only=True):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    data.append(row_dict)
 
            # CSV
            elif format_type == 'csv':
                decoded_file = file.read().decode('utf-8')
                dataset = Dataset()
                dataset.load(decoded_file, format='csv')
 
                for row in dataset.dict:
                    row_l = {k.strip().lower(): v for k, v in row.items()}
 
                    if not required_headers.issubset(set(row_l.keys())):
                        return Response({
                            "statusCode": 400,
                            "status": False,
                            "message": f'Missing required headers. Required: {required_headers}'
                        }, status=status.HTTP_400_BAD_REQUEST)
 
                    data.append(row_l)
 
            else:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "error": "Unsupported file format. Use .xlsx or .csv"
                }, status=status.HTTP_400_BAD_REQUEST)
 
            imported_count = 0
 
            for row in  reversed(data):
                name = str(row.get('education type')).strip() if row.get('education type') else None
                perticulars = str(row.get('perticulars')).strip() if row.get('perticulars') else ""
 
                if not name:
                    continue
 
                existing = EducationType.objects.filter(educationType__iexact=name).first()
 
                if existing:
                    if not existing.is_deleted:
                        duplicate_names.append(name)
                        continue
                    else:
                        existing.Perticulars = perticulars
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
 
                else:
                    EducationType.objects.create(
                        educationType=name,
                        Perticulars=perticulars,
                        is_deleted=False
                    )
                    imported_count += 1
 
        except Exception as e:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
 
        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": list(set(duplicate_names)),
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count
        }, status=status.HTTP_200_OK)
 
# -------------------- MediumofEducation CRUD -------------------- #

class MediumofEducationListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'updated_at')
        sort_order = request.GET.get('sortOrder', 'desc')  # default to newest first

        allowed_sort_fields = ['name', 'perticulars', 'created_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        # Apply descending order for 'desc'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = MediumofEducation.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(perticulars__icontains=search)
            )

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = MediumofEducationSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class MediumofEducationCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        name = request.data.get('name', '').strip()
        if MediumofEducation.objects.filter(name__iexact=name, is_deleted=False).exists():
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Medium of Education with this name already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = MediumofEducationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Medium of Education created successfully",
                "data": serializer.data
            })

        return Response({
            "statusCode": 400,
            "status": False,
            "message": " ".join([m for msgs in serializer.errors.values() for m in msgs])
        }, status=status.HTTP_400_BAD_REQUEST)


class MediumofEducationRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = MediumofEducation.objects.get(uuid=uuid, is_deleted=False)
        except MediumofEducation.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Medium of Education not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = MediumofEducationSerializer(obj)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Medium of Education retrieved successfully",
            "data": serializer.data
        })


class MediumofEducationUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = MediumofEducation.objects.get(uuid=uuid, is_deleted=False)
        except MediumofEducation.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Medium of Education not found"
            }, status=status.HTTP_404_NOT_FOUND)

        name = request.data.get('name', '').strip()
        if MediumofEducation.objects.filter(name__iexact=name).exclude(uuid=uuid).exists():
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Medium of Education with this name already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = MediumofEducationSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Medium of Education updated successfully",
                "data": serializer.data
            })

        return Response({
            "statusCode": 400,
            "status": False,
            "message": " ".join([m for msgs in serializer.errors.values() for m in msgs])
        }, status=status.HTTP_400_BAD_REQUEST)

class MediumofEducationDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        uuids = request.data.get('id', None)

        # Single delete via URL parameter
        if uuid:
            try:
                obj = MediumofEducation.objects.get(uuid=uuid, is_deleted=False)
                obj.is_deleted = True
                obj.save()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "Medium of Education deleted successfully",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            except MediumofEducation.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Medium of Education not found",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        # Delete all if "all" is sent
        if uuids == "all":
            objs = MediumofEducation.objects.filter(is_deleted=False)
            count = objs.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No Medium of Education records found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
            objs.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} Medium of Education record(s) deleted successfully.",
                "data": None
            }, status=status.HTTP_200_OK)

        # Validate bulk UUIDs
        if not uuids or not isinstance(uuids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide a list of UUIDs in 'id' field or 'all'.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        valid_uuids = []
        invalid_uuids = []
        for u in uuids:
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
        objs = MediumofEducation.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = objs.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching Medium of Education records found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_404_NOT_FOUND)

        objs.delete()

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} Medium of Education record(s) deleted successfully.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        }, status=status.HTTP_200_OK)


class MediumofEducationExportAPIView(APIView):

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        # Field to header mapping
        field_header_map = {
            'uuid': 'UUID',
            'name': 'Medium of Education',
            'perticulars': 'Perticulars',
            'is_deleted': 'Deleted',
            'created_at': 'Created On',
            'updated_at': 'Modified On',
        }

        # Fields to export
        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())

        queryset = MediumofEducation.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'Medium of Education'

        for obj in queryset:
            row = []
            for field in field_list:
                value = getattr(obj, field, '')

                if field in ['created_at', 'updated_at'] and value:
                    # Convert the stored UTC datetime to IST and format it
                    value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
                elif isinstance(value, bool):
                    value = int(value)
                row.append(value if value is not None else '')
            dataset.append(row)

        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'medium_of_education.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'medium_of_education.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


class MediumofEducationImportAPIView(APIView):


    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicate_names = []

        required_headers = {'medium of education'}
        optional_headers = {'perticulars'}

        try:
            data = []

            # XLSX Handling
            if format_type == 'xlsx':
                import openpyxl
                wb = openpyxl.load_workbook(file, read_only=True)
                sheets = wb.sheetnames

                if not sheet_name:
                    return Response({
                        'error': 'Please provide sheet_name',
                        'available_sheets': sheets
                    }, status=status.HTTP_400_BAD_REQUEST)

                if sheet_name not in sheets:
                    return Response({
                        'error': f'Sheet "{sheet_name}" not found',
                        'available_sheets': sheets
                    }, status=status.HTTP_400_BAD_REQUEST)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'The uploaded XLSX file (sheet: "{sheet_name}") is empty. Provide at least one data row.'
                    }, status=status.HTTP_400_BAD_REQUEST)

                headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]

                if not required_headers.issubset(set(headers)):
                    return Response({
                        "statusCode": 400,
                        "status": True,
                        'message': f'Missing required headers. Required: {required_headers}, Found: {set(headers)}'
                    }, status=status.HTTP_400_BAD_REQUEST)

                for row in ws.iter_rows(min_row=2, values_only=True):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    data.append(row_dict)

                if not data:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'The uploaded XLSX file (sheet: "{sheet_name}") is empty.'
                    }, status=status.HTTP_400_BAD_REQUEST)

            # CSV Handling
            elif format_type == 'csv':
                decoded_file = file.read().decode('utf-8')
                dataset = Dataset()
                dataset.load(decoded_file, format='csv')

                for row in dataset.dict:
                    row_lower = {k.strip().lower(): v for k, v in row.items()}

                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({
                            "statusCode": 400,
                            "status": True,
                            "message": f'Missing required headers. Required: {", ".join(required_headers)}. Found: {", ".join(row_lower.keys())}.'
                        }, status=status.HTTP_400_BAD_REQUEST)

                    data.append(row_lower)

                if not data:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": "The uploaded CSV file is empty."
                    }, status=status.HTTP_400_BAD_REQUEST)

            else:
                return Response({
                    "statusCode": 400,
                    "status": True,
                    'error': 'Unsupported file format. Use .xlsx or .csv'
                }, status=status.HTTP_400_BAD_REQUEST)

            imported_count = 0

            # Import rows
            for row in  reversed(data):
                name = str(row.get('medium of education')).strip() if row.get('medium of education') else None
                perticulars = str(row.get('Perticulars')).strip() if row.get('Perticulars') else ''

                if not name:
                    continue

                existing = MediumofEducation.objects.filter(name__iexact=name).first()

                if existing:
                    if not existing.is_deleted:
                        duplicate_names.append(name)
                        continue
                    else:
                        existing.Perticulars = perticulars
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    MediumofEducation.objects.create(
                        name=name,
                        Perticulars=perticulars,
                        is_deleted=False
                    )
                    imported_count += 1

        except Exception as e:
            return Response({
                "statusCode": 400,
                "status": True,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": list(set(duplicate_names)),
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count
        }, status=status.HTTP_200_OK)



class ECAAwardingBodyListAPIView(APIView):
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'updated_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['eca_body_full_name', 'eca_body_short_name', 'eca_valid_period', 'created_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = ECAAwardingBody.objects.all()
        if search:
            queryset = queryset.filter(
                Q(eca_body_full_name__icontains=search) |
                Q(eca_body_short_name__icontains=search) |
                Q(country__name__icontains=search)
            )

        queryset = queryset.order_by(sort_by)

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = ECAAwardingBodySerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


# -------------------- CREATE API --------------------
class ECAAwardingBodyCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        serializer = ECAAwardingBodySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "ECA Awarding Body created successfully",
                "data": serializer.data
            })
        errors = serializer.errors
        messages = []
        for field, msgs in errors.items():
            messages.extend(msgs)
        return Response({
            "statusCode": 400,
            "status": False,
            "message": " ".join(messages)
        }, status=status.HTTP_400_BAD_REQUEST)


# -------------------- RETRIEVE API --------------------
class ECAAwardingBodyRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            eca = ECAAwardingBody.objects.get(uuid=uuid)
        except ECAAwardingBody.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "ECA Awarding Body not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = ECAAwardingBodySerializer(eca)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "ECA Awarding Body retrieved successfully",
            "data": serializer.data
        })


# -------------------- UPDATE API --------------------
class ECAAwardingBodyUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            eca = ECAAwardingBody.objects.get(uuid=uuid)
        except ECAAwardingBody.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "ECA Awarding Body not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = ECAAwardingBodySerializer(eca, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "ECA Awarding Body updated successfully",
                "data": serializer.data
            })
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


# -------------------- DELETE API --------------------
class ECAAwardingBodyDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get('id', None)

        if uuid:
            try:
                eca = ECAAwardingBody.objects.get(uuid=uuid)
                eca.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "ECA Awarding Body permanently deleted",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            except ECAAwardingBody.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "ECA Awarding Body not found",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        if ids == "all":
            count = ECAAwardingBody.objects.count()
            ECAAwardingBody.objects.all().delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} ECA Awarding Body(ies) permanently deleted",
                "data": None
            })

        if not ids or not isinstance(ids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Provide a list of UUIDs in 'id' field or 'all'.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        valid_uuids = []
        invalid_uuids = []
        for u in ids:
            try:
                valid_uuids.append(UUID(u))
            except ValueError:
                invalid_uuids.append(u)

        queryset = ECAAwardingBody.objects.filter(uuid__in=valid_uuids)
        count = queryset.count()
        queryset.delete()

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} ECA Awarding Body(ies) permanently deleted",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        })


# -------------------- EXPORT API --------------------
class ECAAwardingBodyExportAPIView(APIView):
    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'country': 'Country',
            'selection_type': 'ECA For',
            'valid_duration_value': 'Valid Duration',
            'eca_body_full_name': 'ECA Body Full Name',
            'eca_body_short_name': 'ECA Body Short Name',
            'eca_valid_period': 'ECA Valid Period',
            'created_at': 'Created On',
            'updated_at': 'Modified On'
        }

        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())
        queryset = ECAAwardingBody.objects.all()
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'ECAAwardingBody'

        for eca in queryset:
            row = []
            for field in field_list:
                value = getattr(eca, field, '')
                if field == 'country' and eca.country:
                    value = eca.country.name
                elif isinstance(value, bool):
                    value = int(value)
                elif field in ['created_at', 'updated_at'] and value:
                    value = timezone.localtime(value).strftime("%d-%m-%Y %I:%M:%S %p")
                row.append(value if value is not None else '')
            dataset.append(row)

        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'eca_awarding_body.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'eca_awarding_body.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response



class ECAAwardingBodyImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name', None)

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        imported_count = 0
        skipped_rows = []
        duplicate_names = []

        # Define required and optional headers
        required_headers = {'eca body full name', 'country'}
        optional_headers = {'eca body short name', 'selection type', 'valid duration value', 'eca valid period'}

        try:
            data = []
            headers = []

            # ---------- XLSX ----------
            if format_type == 'xlsx':
                import openpyxl
                wb = openpyxl.load_workbook(file, read_only=True)

                if sheet_name:
                    if sheet_name not in wb.sheetnames:
                        return Response({
                            'statusCode': 400,
                            'status': False,
                            'message': f'Sheet "{sheet_name}" not found',
                            'available_sheets': wb.sheetnames
                        }, status=status.HTTP_400_BAD_REQUEST)
                    ws = wb[sheet_name]
                else:
                    ws = wb.active

                headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]

                # Check required headers
                if not required_headers.issubset(set(headers)):
                    return Response({
                        'statusCode': 400,
                        'status': False,
                        'message': f'Missing required headers: {required_headers - set(headers)}'
                    }, status=status.HTTP_400_BAD_REQUEST)

                for row in ws.iter_rows(min_row=2, values_only=True):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    data.append(row_dict)

            # ---------- CSV ----------
            elif format_type == 'csv':
                import csv
                decoded_file = file.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(decoded_file))
                headers = [h.strip().lower() for h in reader.fieldnames]

                # Check required headers
                if not required_headers.issubset(set(headers)):
                    return Response({
                        'statusCode': 400,
                        'status': False,
                        'message': f'Missing required headers: {required_headers - set(headers)}'
                    }, status=status.HTTP_400_BAD_REQUEST)

                for row in reader:
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    data.append(row_lower)

            else:
                return Response({'statusCode': 400, 'status': False, 'message': 'Unsupported file format'}, status=status.HTTP_400_BAD_REQUEST)

            # ---------- Import Data ----------
            for row in  reversed(data):
                full_name = str(row.get('eca body full name')).strip() if row.get('eca body full name') else None
                short_name = str(row.get('eca body short name')).strip() if row.get('eca body short name') else ''
                country_name = str(row.get('country')).strip() if row.get('country') else None
                selection_type = str(row.get('selection type')).strip() if row.get('selection type') else None
                valid_duration_value = row.get('valid duration value')
                eca_valid_period = str(row.get('eca valid period')).strip() if row.get('eca valid period') else None

                if not full_name or not country_name:
                    skipped_rows.append({'full_name': full_name or 'Unknown', 'reason': 'Missing required field(s)'})
                    continue

                # Map by country name
                country = Country.objects.filter(name__iexact=country_name).first()
                if not country:
                    skipped_rows.append({'full_name': full_name, 'reason': f'Country "{country_name}" not found'})
                    continue

                existing = ECAAwardingBody.objects.filter(eca_body_full_name__iexact=full_name, country=country).first()
                if existing:
                    duplicate_names.append(full_name)
                    continue

                # Create record
                ECAAwardingBody.objects.create(
                    eca_body_full_name=full_name,
                    eca_body_short_name=short_name,
                    country=country,
                    selection_type=selection_type,
                    valid_duration_value=valid_duration_value,
                    eca_valid_period=eca_valid_period
                )
                imported_count += 1

        except Exception as e:
            return Response({'statusCode': 400, 'status': False, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": list(set(duplicate_names)),
            "skipped_rows": skipped_rows,
            "imported_count": imported_count,
            "message": "Import successful"
        })


class DegreeAwardedByListAPIView(APIView):
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'updated_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['degree_name', 'created_at', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = DegreeAwardedBy.objects.all()
        if search:
            queryset = queryset.filter(
                Q(degree_name__icontains=search) |
                Q(description__icontains=search) |
                Q(country__name__icontains=search) |
                Q(state__name__icontains=search) |
                Q(education_level__name__icontains=search)
            )

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = DegreeAwardedBySerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


# -------------------- CREATE API --------------------
class DegreeAwardedByCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        # If UUID is provided in the payload, use it
        uuid_value = request.data.get('uuid')
        if uuid_value:
            try:
                request.data['uuid'] = UUID(uuid_value)
            except ValueError:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Invalid UUID format"
                }, status=status.HTTP_400_BAD_REQUEST)

        serializer = DegreeAwardedBySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Degree created successfully",
                "data": serializer.data
            })
        errors = serializer.errors
        messages = []
        for field, msgs in errors.items():
            messages.extend(msgs)
        return Response({
            "statusCode": 400,
            "status": False,
            "message": " ".join(messages)
        }, status=status.HTTP_400_BAD_REQUEST)

# -------------------- RETRIEVE API --------------------
class DegreeAwardedByRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            degree = DegreeAwardedBy.objects.get(uuid=uuid)
        except DegreeAwardedBy.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Degree not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = DegreeAwardedBySerializer(degree)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Degree retrieved successfully",
            "data": serializer.data
        })


# -------------------- UPDATE API --------------------
class DegreeAwardedByUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            degree = DegreeAwardedBy.objects.get(uuid=uuid)
        except DegreeAwardedBy.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Degree not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = DegreeAwardedBySerializer(degree, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Degree updated successfully",
                "data": serializer.data
            })
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


# -------------------- DELETE API --------------------
class DegreeAwardedByDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get('id', None)

        if uuid:
            try:
                degree = DegreeAwardedBy.objects.get(uuid=uuid)
                degree.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "Degree permanently deleted",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            except DegreeAwardedBy.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Degree not found",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        if ids == "all":
            count = DegreeAwardedBy.objects.count()
            DegreeAwardedBy.objects.all().delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} degree(s) permanently deleted",
                "data": None
            })

        if not ids or not isinstance(ids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Provide a list of UUIDs in 'id' field or 'all'.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        valid_uuids = []
        invalid_uuids = []
        for u in ids:
            try:
                valid_uuids.append(UUID(u))
            except ValueError:
                invalid_uuids.append(u)

        queryset = DegreeAwardedBy.objects.filter(uuid__in=valid_uuids)
        count = queryset.count()
        queryset.delete()

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} degree(s) permanently deleted",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        })


# -------------------- EXPORT API --------------------
class DegreeAwardedByExportAPIView(APIView):
    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'country': 'Country',
            'education_level': 'Education Level',
            'degree_name': 'Degree Name By',
            'description': 'Description',
            'created_at': 'Created On',
            'updated_at': 'Updated On'
        }

        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())

        queryset = DegreeAwardedBy.objects.all()
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'DegreeAwardedBy'

        for degree in queryset:
            row = []
            for field in field_list:
                value = getattr(degree, field, '')
                if field in ['created_at', 'updated_at'] and value:
                    value = value.strftime("%d-%m-%Y %I:%M:%S %p")
                elif field == 'country' and degree.country:
                    value = degree.country.name
                elif field == 'education_level' and degree.education_level:
                    value = degree.education_level.educationlevel
                elif isinstance(value, bool):
                    value = int(value)
                row.append(value if value is not None else '')
            dataset.append(row)

        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'degrees.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'degrees.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


# -------------------- IMPORT API --------------------
class DegreeAwardedByImportAPIView(APIView):

    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name', None)

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        imported_count = 0
        skipped_rows = []
        duplicate_names = []

        required_headers = {'degree awarded by', 'country', 'education level'}
        optional_headers = {'description'}

        try:
            data = []
            headers = []

            if format_type == 'xlsx':
                import openpyxl
                wb = openpyxl.load_workbook(file, read_only=True)
                ws = wb[sheet_name] if sheet_name else wb.active
                headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                if not required_headers.issubset(set(headers)):
                    return Response({'statusCode': 400, 'status': False, 'message': f'Missing required headers: {required_headers - set(headers)}'}, status=status.HTTP_400_BAD_REQUEST)
                for row in ws.iter_rows(min_row=2, values_only=True):
                    if not any(row):
                        continue
                    data.append(dict(zip(headers, row)))
            elif format_type == 'csv':
                import csv
                decoded_file = file.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(decoded_file))
                headers = [h.strip().lower() for h in reader.fieldnames]
                if not required_headers.issubset(set(headers)):
                    return Response({'statusCode': 400, 'status': False, 'message': f'Missing required headers: {required_headers - set(headers)}'}, status=status.HTTP_400_BAD_REQUEST)
                for row in reader:
                    data.append({k.strip().lower(): v for k, v in row.items()})
            else:
                return Response({'statusCode': 400, 'status': False, 'message': 'Unsupported file format'}, status=status.HTTP_400_BAD_REQUEST)

            for row in  reversed(data):
                degree_name = str(row.get('degree name')).strip() if row.get('degree name') else None
                country_name = str(row.get('country')).strip() if row.get('country') else None
                education_level_name = str(row.get('education level')).strip() if row.get('education level') else None
                description = str(row.get('description')).strip() if row.get('description') else ''

                if not degree_name or not country_name   or not education_level_name:
                    skipped_rows.append({'degree_name': degree_name or 'Unknown', 'reason': 'Missing required field(s)'})
                    continue

                country = Country.objects.filter(name__iexact=country_name).first()
                education_level = EducationLevel.objects.filter(name__iexact=education_level_name).first()

                if not country  or not education_level:
                    skipped_rows.append({'degree_name': degree_name, 'reason': 'Invalid country/state/education level'})
                    continue

                existing = DegreeAwardedBy.objects.filter(degree_name__iexact=degree_name, country=country, education_level=education_level).first()
                if existing:
                    duplicate_names.append(degree_name)
                    continue

                DegreeAwardedBy.objects.create(
                    degree_name=degree_name,
                    country=country,
                    education_level=education_level,
                    description=description
                )
                imported_count += 1

        except Exception as e:
            return Response({'statusCode': 400, 'status': False, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": list(set(duplicate_names)),
            "skipped_rows": skipped_rows,
            "imported_count": imported_count,
            "message": "Import successful"
        })


class DegreeAwardedInstituteListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'updated_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['name', 'created_at', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = DegreeAwardedInstitute.objects.all()
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(country__name__icontains=search) |
                Q(state__stateName__icontains=search) |
                Q(education_level__name__icontains=search) |
                Q(degree_awarded_by__name__icontains=search)
            )

        queryset = queryset.order_by(sort_by)
        serializer = DegreeAwardedInstituteSerializer(queryset, many=True)
        return Response({
            "statusCode": 200,
            "status": True,
            "data": serializer.data
        })


# -------------------- CREATE API --------------------
class DegreeAwardedInstituteCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        uuid_value = request.data.get('uuid')
        if uuid_value:
            try:
                request.data['uuid'] = UUID(uuid_value)
            except ValueError:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Invalid UUID format"
                }, status=status.HTTP_400_BAD_REQUEST)

        serializer = DegreeAwardedInstituteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Degree Awarded Institute created successfully",
                "data": serializer.data
            })
        errors = serializer.errors
        messages = []
        for field, msgs in errors.items():
            messages.extend(msgs)
        return Response({
            "statusCode": 400,
            "status": False,
            "message": " ".join(messages)
        }, status=status.HTTP_400_BAD_REQUEST)


# -------------------- RETRIEVE API --------------------
class DegreeAwardedInstituteRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = DegreeAwardedInstitute.objects.get(uuid=uuid)
        except DegreeAwardedInstitute.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Degree Awarded Institute not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = DegreeAwardedInstituteSerializer(obj)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Degree Awarded Institute retrieved successfully",
            "data": serializer.data
        })


# -------------------- UPDATE API --------------------
class DegreeAwardedInstituteUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = DegreeAwardedInstitute.objects.get(uuid=uuid)
        except DegreeAwardedInstitute.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Degree Awarded Institute not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = DegreeAwardedInstituteSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Degree Awarded Institute updated successfully",
                "data": serializer.data
            })
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


# -------------------- DELETE API --------------------
class DegreeAwardedInstituteDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get('id', None)

        if uuid:
            try:
                obj = DegreeAwardedInstitute.objects.get(uuid=uuid)
                obj.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "Degree Awarded Institute permanently deleted",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            except DegreeAwardedInstitute.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Degree Awarded Institute not found",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        if ids == "all":
            count = DegreeAwardedInstitute.objects.count()
            DegreeAwardedInstitute.objects.all().delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} institutes permanently deleted",
                "data": None
            })

        if not ids or not isinstance(ids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Provide a list of UUIDs in 'id' field or 'all'.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        valid_uuids = []
        invalid_uuids = []
        for u in ids:
            try:
                valid_uuids.append(UUID(u))
            except ValueError:
                invalid_uuids.append(u)

        queryset = DegreeAwardedInstitute.objects.filter(uuid__in=valid_uuids)
        count = queryset.count()
        queryset.delete()

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} institute(s) permanently deleted",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        })


# -------------------- EXPORT API --------------------
class DegreeAwardedInstituteExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'country': 'Country',
            'state': 'State',
            'education_level': 'Education Level',
            'degree_awarded_by': 'Degree Awarded By',
            'name': 'Degree Awarded Institute',
            'description': 'Description',
            'created_at': 'Created On',
            'updated_at': 'Updated On'
        }

        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())

        queryset = DegreeAwardedInstitute.objects.all()
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'DegreeAwardedInstitute'

        for obj in queryset:
            row = []
            for field in field_list:
                value = getattr(obj, field, '')
                if field in ['created_at', 'updated_at'] and value:
                    value = value.strftime("%d-%m-%Y %I:%M:%S %p")
                elif field == 'country' and obj.country:
                    value = obj.country.name
                elif field == 'state' and obj.state:
                    value = obj.state.storeName
                elif field == 'education_level' and obj.education_level:
                    value = obj.education_level.educationlevel
                elif field == 'degree_awarded_by' and obj.degree_awarded_by:
                    value = obj.degree_awarded_by.degree_name
                elif isinstance(value, bool):
                    value = int(value)
                row.append(value if value is not None else '')
            dataset.append(row)

        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'degree_awarded_institutes.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'degree_awarded_institutes.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


class DegreeAwardedInstituteImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name', None)

        if not file:
            return Response({'statusCode': 400, 'status': False, 'message': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        imported_count = 0
        skipped_rows = []
        duplicate_names = []

        # Define required and optional headers
        required_headers = {'degree awarded institute', 'degree awarded by'}
        optional_headers = {'description', 'country', 'state', 'education level'}

        try:
            data = []
            headers = []

            # ---------- XLSX ----------
            if format_type == 'xlsx':
                import openpyxl
                wb = openpyxl.load_workbook(file, read_only=True)

                if sheet_name:
                    if sheet_name not in wb.sheetnames:
                        return Response({
                            'statusCode': 400,
                            'status': False,
                            'message': f'Sheet "{sheet_name}" not found',
                            'available_sheets': wb.sheetnames
                        }, status=status.HTTP_400_BAD_REQUEST)
                    ws = wb[sheet_name]
                else:
                    ws = wb.active

                headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]

                # Check required headers
                if not required_headers.issubset(set(headers)):
                    return Response({
                        'statusCode': 400,
                        'status': False,
                        'message': f'Missing required headers: {required_headers - set(headers)}'
                    }, status=status.HTTP_400_BAD_REQUEST)

                for row in ws.iter_rows(min_row=2, values_only=True):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    data.append(row_dict)

            # ---------- CSV ----------
            elif format_type == 'csv':
                import csv
                decoded_file = file.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(decoded_file))
                headers = [h.strip().lower() for h in reader.fieldnames]

                # Check required headers
                if not required_headers.issubset(set(headers)):
                    return Response({
                        'statusCode': 400,
                        'status': False,
                        'message': f'Missing required headers: {required_headers - set(headers)}'
                    }, status=status.HTTP_400_BAD_REQUEST)

                for row in reader:
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    data.append(row_lower)

            else:
                return Response({'statusCode': 400, 'status': False, 'message': 'Unsupported file format'}, status=status.HTTP_400_BAD_REQUEST)

            # ---------- Import Data ----------
            for row in  reversed(data):
                name = str(row.get('degree awarded institute')).strip() if row.get('degree awarded institute') else None
                degree_awarded_by_name = str(row.get('degree awarded by')).strip() if row.get('degree awarded by') else None
                description = str(row.get('description')).strip() if row.get('description') else ''
                country_name = str(row.get('country')).strip() if row.get('country') else None
                state_name = str(row.get('state')).strip() if row.get('state') else None
                education_level_name = str(row.get('education level')).strip() if row.get('education level') else None

                if not name or not degree_awarded_by_name:
                    skipped_rows.append({'name': name or 'Unknown', 'reason': 'Missing required field(s)'})
                    continue

                # Map DegreeAwardedBy
                degree_awarded_by = DegreeAwardedBy.objects.filter(degree_name__iexact=degree_awarded_by_name).first()
                if not degree_awarded_by:
                    skipped_rows.append({'name': name, 'reason': f'Degree Awarded By "{degree_awarded_by_name}" not found'})
                    continue

                # Map Country, State, Education Level
                country = Country.objects.filter(name__iexact=country_name).first() if country_name else None
                state = State.objects.filter(name__iexact=state_name).first() if state_name else None
                education_level = EducationLevel.objects.filter(name__iexact=education_level_name).first() if education_level_name else None

                # Check duplicate
                existing = DegreeAwardedInstitute.objects.filter(name__iexact=name, degree_awarded_by=degree_awarded_by).first()
                if existing:
                    duplicate_names.append(name)
                    continue

                # Create record
                DegreeAwardedInstitute.objects.create(
                    name=name,
                    description=description,
                    degree_awarded_by=degree_awarded_by,
                    country=country,
                    state=state,
                    education_level=education_level
                )
                imported_count += 1

        except Exception as e:
            return Response({'statusCode': 400, 'status': False, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": list(set(duplicate_names)),
            "skipped_rows": skipped_rows,
            "imported_count": imported_count,
            "message": "Import successful"
        })