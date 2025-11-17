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
                Q(name__istartswith=search)
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
    Import Gender data from CSV or XLSX with skip and duplicate tracking.
    """
    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicates = []
        skipped_rows = []

        required_headers = {'gender'}
        optional_headers = {'description', 'is_active'}

        try:
            data = []

            # ---------------- XLSX ----------------
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

                for row in ws.iter_rows(min_row=2, values_only=True):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    data.append(row_dict)

            # ---------------- CSV ----------------
            elif format_type == 'csv':
                decoded_file = file.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(decoded_file))
                for row in reader:
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    data.append(row_lower)
            else:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": 'Unsupported file format. Use .xlsx or .csv'
                }, status=status.HTTP_400_BAD_REQUEST)

            # ---------------- Process Data ----------------
            imported_count = 0
            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")
                name = str(row.get('gender')).strip() if row.get('gender') else None
                description = str(row.get('description')).strip() if row.get('description') else ''
                
                if not name:
                    skipped_rows.append({
                        "Row": row_number,
                        "Reason": "Missing gender name"
                    })
                    continue

                existing = Gender.objects.filter(name__iexact=name).first()

                if existing:
                    if not existing.is_deleted:
                        duplicates.append({
                            "Row": row_number,
                            "Gender": name,
                            "Reason": "Already exists in database"
                        })
                        continue
                    else:
                        # Reactivate deleted
                        existing.description = description 
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    Gender.objects.create(
                        name=name,
                        description=description,
                       
                        is_deleted=False
                    )
                    imported_count += 1

        except Exception as e:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        # ---------------- Response ----------------
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": duplicates,
            "skipped_rows": skipped_rows
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
                    Q(name__istartswith=search)
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
    Import Maritalstatus data from CSV or XLSX with skip and duplicate tracking.
    """
    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicates = []
        skipped_rows = []

        required_headers = {'marital status'}
        optional_headers = {'description', 'is_active'}

        try:
            data = []

            # ---------------- XLSX ----------------
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

                for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    row_dict["_row_number"] = idx
                    data.append(row_dict)

            # ---------------- CSV ----------------
            elif format_type == 'csv':
                decoded_file = file.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(decoded_file))
                for idx, row in enumerate(reader, start=2):
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    row_lower["_row_number"] = idx
                    data.append(row_lower)
            else:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": 'Unsupported file format. Use .xlsx or .csv'
                }, status=status.HTTP_400_BAD_REQUEST)

            # ---------------- Process Data ----------------
            imported_count = 0
            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")
                name = str(row.get('marital status')).strip() if row.get('marital status') else None
                description = str(row.get('description')).strip() if row.get('description') else ''
                
                if not name:
                    skipped_rows.append({
                        "Row": row_number,
                        "Reason": "Missing marital status name"
                    })
                    continue

                existing = Maritalstatus.objects.filter(name__iexact=name).first()
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({
                            "Row": row_number,
                            "Marital Status": name,
                            "Reason": "Already exists in database"
                        })
                        continue
                    else:
                        # Reactivate deleted
                        existing.description = description
                        
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    Maritalstatus.objects.create(
                        name=name,
                        description=description,
                       
                        is_deleted=False
                    )
                    imported_count += 1

        except Exception as e:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        # ---------------- Response ----------------
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": duplicates,
            "skipped_rows": skipped_rows
        }, status=status.HTTP_200_OK)







#-------------------------------continents--------------------------------
class ContinentListAPIView(APIView):
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

        queryset = Continents.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(
                Q(name__istartswith=search) 
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
        duplicates = []
        skipped_rows = []

        required_headers = {'continent'}
        optional_headers = {'description'}

        try:
            data = []

            # ---------------- XLSX ----------------
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
                        "message": f'The uploaded XLSX file (sheet: "{sheet_name}") is empty.'
                    }, status=status.HTTP_400_BAD_REQUEST)

                headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]

                for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    row_dict["_row_number"] = idx
                    data.append(row_dict)

            # ---------------- CSV ----------------
            elif format_type == 'csv':
                decoded_file = file.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(decoded_file))
                for idx, row in enumerate(reader, start=2):
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    row_lower["_row_number"] = idx
                    data.append(row_lower)
            else:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    'error': 'Unsupported file format. Use .xlsx or .csv'
                }, status=status.HTTP_400_BAD_REQUEST)

            # ---------------- Process Data ----------------
            imported_count = 0
            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")
                name = str(row.get('continent')).strip() if row.get('continent') else None
                description = str(row.get('description')).strip() if row.get('description') else ''

                if not name:
                    skipped_rows.append({
                        "Row": row_number,
                        "Reason": "Missing continent name"
                    })
                    continue

                existing = Continents.objects.filter(name__iexact=name).first()
                if existing:
                    if existing.is_deleted:
                        existing.is_deleted = False
                        existing.description = description
                        existing.save()
                        imported_count += 1
                    else:
                        duplicates.append({
                            "Row": row_number,
                            "Continent": name,
                            "Reason": "Already exists in database"
                        })
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
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": duplicates,
            "skipped_rows": skipped_rows
        }, status=status.HTTP_200_OK)

#-------------------------------------------country---------------------------------


class CountryListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')
        allowed_sort_fields = ['name', 'shortName', 'fullName', 'capitalCity', 'created_at']

        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = Country.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(
                Q(name__istartswith=search) 
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
        continent_id = request.data.get("continent_id")  # Continent select kar rahe ho
        if not continent_id:
            return Response({"statusCode": 400, "status": False, "message": "continent_id is required."}, status=400)

        # Check for existing country in same continent
        existing = Country.objects.filter(
            name__iexact=name,
            continent_id=continent_id,
            is_deleted=False
        ).first()

        if existing:
            return Response({"statusCode": 400, "status": False, "message": "Country with this name already exists in the selected continent."}, status=400)

        serializer = CountrySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Country created successfully",
                "data": serializer.data
            })
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

                existing = Country.objects.filter(name__iexact=country_name, continent=continent_obj).first()
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
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')
        allowed_sort_fields = ['stateName', 'stateshortName', 'created_at', 'updated_at']

        # Validate sort field
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        # Helper: parse comma-separated or multiple params
        def parse_ids(param_name):
            raw = request.GET.get(param_name, '')
            if raw:
                items = [x.strip() for x in raw.split(',') if x.strip()]
            else:
                items = request.GET.getlist(param_name)
            return items

        # Helper: filter valid UUIDs
        def validate_uuid_list(uuid_list):
            valid_uuids = []
            for u in uuid_list:
                try:
                    valid_uuids.append(UUID(u))
                except ValueError:
                    pass
            return valid_uuids

        country_list = validate_uuid_list(parse_ids('country'))
        state_list = validate_uuid_list(parse_ids('state'))

        queryset = State.objects.filter(is_deleted=False)

        # ---------------------------
        # HIERARCHICAL FILTERING
        # ---------------------------
        if state_list:
            queryset = queryset.filter(uuid__in=state_list)
        elif country_list:
            queryset = queryset.filter(countryName__uuid__in=country_list)

        # ---------------------------
        # TEXT SEARCH (STATE)
        # ---------------------------
        if search:
            queryset = queryset.filter(
                Q(stateName__istartswith=search)
            )

        # Apply sorting
        queryset = queryset.order_by(sort_by)

        # Pagination
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
        country_param = request.GET.get("country_id", "")
        search_term = request.GET.get("search", "")
        sort_by = request.GET.get("sort_by", "stateName")

        # If 'all' → return all states
        if country_param.lower() == "all":
            states = State.objects.all()
        else:
            # Get comma-separated country IDs
            country_ids = [cid.strip() for cid in country_param.split(",") if cid.strip()]
            
            if not country_ids:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "country_id is required"
                }, status=status.HTTP_400_BAD_REQUEST)

            # Validate country UUIDs
            valid_countries = []
            invalid_countries = []

            for country_id in country_ids:
                try:
                    country_uuid = uuid.UUID(country_id)
                    country = Country.objects.get(uuid=country_uuid)
                    valid_countries.append(country)
                except (ValueError, Country.DoesNotExist):
                    invalid_countries.append(country_id)

            if invalid_countries:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": f"Invalid or non-existent country IDs: {', '.join(invalid_countries)}"
                }, status=status.HTTP_400_BAD_REQUEST)

            # Filter states by valid countries
            states = State.objects.filter(countryName__in=valid_countries)

        # Search
        if search_term:
            states = states.filter(stateName__icontains=search_term)

        # Sorting (safe fields)
        allowed_sort_fields = ["stateName", "created_at", "updated_at"]
        if sort_by not in allowed_sort_fields:
            sort_by = "stateName"
        states = states.order_by(sort_by)

        # Pagination
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(states, request)

        # Response
        data = [
            {
                "uuid": str(state.uuid),
                "name": state.stateName,
                "shortName": state.stateshortName,
                "fullName": state.description,
                "country": state.countryName.name
            }
            for state in result_page
        ]

        return paginator.get_paginated_response(data)








#-------------------------------------------district---------------------------------

class DistrictListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')
        allowed_sort_fields = ['districtName', 'created_at', 'updated_at']

        # Validate sort field
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        # Helper: parse comma-separated or multiple params
        def parse_ids(param_name):
            raw = request.GET.get(param_name, '')
            if raw:
                items = [x.strip() for x in raw.split(',') if x.strip()]
            else:
                items = request.GET.getlist(param_name)
            return items

        # Helper: filter valid UUIDs
        def validate_uuid_list(uuid_list):
            valid_uuids = []
            for u in uuid_list:
                try:
                    valid_uuids.append(UUID(u))
                except ValueError:
                    pass
            return valid_uuids

        country_list = validate_uuid_list(parse_ids('country'))
        state_list = validate_uuid_list(parse_ids('state'))
        district_list = validate_uuid_list(parse_ids('district'))

        queryset = District.objects.filter(is_deleted=False)

        # ---------------------------
        # HIERARCHICAL FILTERING
        # ---------------------------
        if district_list:
            queryset = queryset.filter(uuid__in=district_list)
        else:
            if state_list:
                queryset = queryset.filter(stateName__uuid__in=state_list)
            if country_list:
                queryset = queryset.filter(countryName__uuid__in=country_list)

        # ---------------------------
        # TEXT SEARCH (DISTRICT)
        # ---------------------------
        if search:
            queryset = queryset.filter(
                Q(districtName__istartswith=search)
            )

        # Apply sorting
        queryset = queryset.order_by(sort_by)

        # Pagination
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = DistrictSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


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


class DistrictRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = District.objects.get(uuid=uuid, is_deleted=False)
        except District.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "District not found"}, status=404)
        serializer = DistrictSerializer(obj)
        return Response({"statusCode": 200, "status": True, "message": "Retrieved successfully", "data": serializer.data})


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
        optional_headers = {'description', 'state name'}

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

            for row in reversed(data):
                district_name = str(row.get('district name')).strip() if row.get('district name') else None
                state_name = str(row.get('state name')).strip() if row.get('state name') else None
                country_name = str(row.get('country name')).strip() if row.get('country name') else None
                description = str(row.get('description')).strip() if row.get('description') else ''

                if not district_name or not country_name:
                    skipped_rows.append({
                        "District Name": district_name or "Unknown",
                        "State Name": state_name or "Unknown",
                        "Country Name": country_name or "Unknown",
                        "Reason": "Missing required field"
                    })
                    continue

                # ---------------- Country Lookup ----------------
                country_obj = Country.objects.filter(name__iexact=country_name).first()
                if not country_obj:
                    skipped_rows.append({
                        "District Name": district_name,
                        "State Name": state_name or "Unknown",
                        "Country Name": country_name,
                        "Reason": "Country not found"
                    })
                    continue

                # ---------------- State Lookup ----------------
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

                # ---------------- File-level Duplicate Check ----------------
                file_key = (
                    district_name.lower(),
                    state_name.lower() if state_name else "",
                    country_name.lower()
                )
                if file_key in existing_in_file:
                    duplicate_names.append({
                        "District Name": district_name,
                        "State Name": state_name,
                        "Country Name": country_name,
                        "Reason": "Duplicate found in file"
                    })
                    continue

                # ---------------- DB-level Duplicate Check ----------------
                existing = District.objects.filter(
                    districtName__iexact=district_name,
                    countryName=country_obj
                )
                if state_obj:
                    existing = existing.filter(stateName=state_obj)
                else:
                    existing = existing.filter(stateName__isnull=True)

                if existing.exists():
                    duplicate_names.append({
                        "District Name": district_name,
                        "State Name": state_name,
                        "Country Name": country_name,
                        "Reason": "Already exists in database"
                    })
                    continue

                # ---------------- Create District ----------------
                try:
                    District.objects.create(
                        districtName=district_name,
                        stateName=state_obj,
                        countryName=country_obj,
                        description=description,
                        is_deleted=False
                    )
                    imported_count += 1
                    existing_in_file.add(file_key)
                except IntegrityError:
                    duplicate_names.append({
                        "District Name": district_name,
                        "State Name": state_name,
                        "Country Name": country_name,
                        "Reason": "Integrity Error"
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
        country_ids = request.GET.get("country_id", "").split(',')  # multiple countries
        state_ids = request.GET.get("state_id", "").split(',')      # multiple states or 'all'
        search_term = request.GET.get("search", "")                 # search by district name
        sort_by = request.GET.get("sort_by", "districtName")        # default sort

        # Helper: validate UUIDs and fetch objects
        def get_valid_objects(model, ids):
            valid_objs = []
            invalid_ids = []
            for _id in filter(None, ids):
                if _id.lower() == 'all':  # skip validation for 'all'
                    continue
                try:
                    obj_uuid = uuid.UUID(_id.strip())
                    obj = model.objects.get(uuid=obj_uuid)
                    valid_objs.append(obj)
                except (ValueError, model.DoesNotExist):
                    invalid_ids.append(_id)
            return valid_objs, invalid_ids

        # Validate countries (optional)
        valid_countries, invalid_countries = get_valid_objects(Country, country_ids)
        if invalid_countries:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": f"Invalid or non-existent country IDs: {', '.join(invalid_countries)}"
            }, status=400)

        # Validate states (optional)
        if 'all' in [s.lower() for s in state_ids]:  # if 'all' is sent, ignore state filter
            valid_states = []
        else:
            valid_states, invalid_states = get_valid_objects(State, state_ids)
            if invalid_states:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": f"Invalid or non-existent state IDs: {', '.join(invalid_states)}"
                }, status=400)

        # Fetch districts
        districts = District.objects.filter(is_deleted=False)

        if valid_countries:
            districts = districts.filter(countryName__in=valid_countries)
        if valid_states:  # filter only if valid states are sent (skip if 'all')
            districts = districts.filter(stateName__in=valid_states)

        # Search filter
        if search_term:
            districts = districts.filter(districtName__icontains=search_term)

        # Sorting
        if sort_by and hasattr(District, sort_by):
            districts = districts.order_by(sort_by)

        # Pagination
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(districts, request)

        # Prepare response
        data = [
            {
                "uuid": str(d.uuid),
                "districtName": d.districtName,
                "Country": d.countryName.name if d.countryName else None,
                "state": d.stateName.stateName if d.stateName else None,
                "description": d.description
            }
            for d in result_page
        ]

        return paginator.get_paginated_response(data)

#--------------------------city--------------------
class CityListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')
        allowed_sort_fields = ['cityName', 'created_at']

        # Validate sort field
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        # Helper: parse comma-separated or multiple params
        def parse_ids(param_name):
            raw = request.GET.get(param_name, '')
            if raw:
                items = [x.strip() for x in raw.split(',') if x.strip()]
            else:
                items = request.GET.getlist(param_name)
            return items

        # Helper: filter valid UUIDs
        def validate_uuid_list(uuid_list):
            valid_uuids = []
            for u in uuid_list:
                try:
                    valid_uuids.append(UUID(u))
                except ValueError:
                    pass
            return valid_uuids

        country_list = validate_uuid_list(parse_ids('country'))
        state_list = validate_uuid_list(parse_ids('state'))
        district_list = validate_uuid_list(parse_ids('district'))
        city_list = validate_uuid_list(parse_ids('city'))

        queryset = City.objects.filter(is_deleted=False)

        # ---------------------------
        # HIERARCHICAL FILTERING
        # ---------------------------
        if city_list:
            # City UUID takes absolute priority
            queryset = queryset.filter(uuid__in=city_list)
        else:
            if district_list:
                queryset = queryset.filter(districtName__uuid__in=district_list)
            if state_list:
                queryset = queryset.filter(stateName__uuid__in=state_list)
            if country_list:
                queryset = queryset.filter(countryName__uuid__in=country_list)

        # ---------------------------
        # TEXT SEARCH (CITY / COUNTRY / STATE / DISTRICT)
        # ---------------------------
        if search:
            queryset = queryset.filter(
                Q(cityName__istartswith=search) 
            )

        # Apply sorting
        queryset = queryset.order_by(sort_by)

        # Pagination
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
            return Response({'error': 'No file uploaded'}, status=400)

        format_type = file.name.split('.')[-1].lower()
        required_headers = {'city name', 'country name'}
        optional_headers = {'state name', 'district name', 'description'}

        try:
            # ------------------ Load file ------------------
            data = []

            if format_type == 'xlsx':
                wb = openpyxl.load_workbook(file, read_only=True)
                if not sheet_name or sheet_name not in wb.sheetnames:
                    return Response({
                        "error": f"Invalid sheet_name. Available: {wb.sheetnames}"
                    }, status=400)

                ws = wb[sheet_name]
                headers = [
                    str(cell.value).strip().lower() if cell.value else ''
                    for cell in next(ws.iter_rows(min_row=1, max_row=1))
                ]
                if not required_headers.issubset(set(headers)):
                    return Response({
                        "error": f"Missing required headers: {required_headers}. Found: {set(headers)}"
                    }, status=400)

                for row in ws.iter_rows(min_row=2, values_only=True):
                    if not any(row):
                        continue
                    data.append(dict(zip(headers, row)))

            elif format_type == 'csv':
                decoded = file.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(decoded))
                for row in reader:
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({
                            "error": f"Missing required headers in CSV. Required: {required_headers}. Found: {set(row_lower.keys())}"
                        }, status=400)
                    data.append(row_lower)

            else:
                return Response({'error': 'Unsupported file type. Use .xlsx or .csv'}, status=400)

            # ------------------ Preload related data ------------------
            countries = {c.name.lower(): c for c in Country.objects.all()}
            states = {
                (s.stateName.lower(), s.countryName.uuid): s for s in State.objects.all()
            }
            districts = {
                (d.districtName.lower(), d.stateName.uuid, d.countryName.uuid): d
                for d in District.objects.all()
            }

            # ------------------ Preload existing cities ------------------
            existing_city_keys = set(
                (c[0].lower(), c[1], c[2], c[3])
                for c in City.objects.values_list(
                    "cityName", "districtName", "stateName", "countryName"
                )
            )

            # ------------------ Process rows ------------------
            to_create = []
            duplicate_names = []
            skipped_rows = []
            existing_in_file = set()

            for row in reversed(data):
                city_name = str(row.get("city name") or "").strip()
                country_name = str(row.get("country name") or "").strip()
                state_name = str(row.get("state name") or "").strip()
                district_name = str(row.get("district name") or "").strip()
                description = str(row.get("description") or "").strip()

                if not (city_name and country_name and state_name and district_name):
                    skipped_rows.append({
                        "City Name": city_name or "Unknown",
                        "State Name": state_name or "Unknown",
                        "District Name": district_name or "Unknown",
                        "Country Name": country_name or "Unknown",
                        "Reason": "Missing required field"
                    })
                    continue

                country_obj = countries.get(country_name.lower())
                if not country_obj:
                    skipped_rows.append({
                        "City Name": city_name,
                        "Reason": f"Country '{country_name}' not found"
                    })
                    continue

                state_obj = states.get((state_name.lower(), country_obj.uuid))
                if not state_obj:
                    skipped_rows.append({
                        "City Name": city_name,
                        "Reason": f"State '{state_name}' not found"
                    })
                    continue

                district_obj = districts.get((district_name.lower(), state_obj.uuid, country_obj.uuid))
                if not district_obj:
                    skipped_rows.append({
                        "City Name": city_name,
                        "Reason": f"District '{district_name}' not found"
                    })
                    continue

                # ------------------ Duplicate check ------------------
                key = (city_name.lower(), district_obj, state_obj, country_obj)
                if key in existing_city_keys or key in existing_in_file:
                    duplicate_names.append({
                        "City Name": city_name,
                        "District Name": district_name,
                        "State Name": state_name,
                        "Country Name": country_name
                    })
                    continue

                existing_in_file.add(key)

                to_create.append(
                    City(
                        cityName=city_name,
                        districtName=district_obj,
                        stateName=state_obj,
                        countryName=country_obj,
                        description=description,
                        is_deleted=False
                    )
                )

            # ------------------ Bulk insert ------------------
            with transaction.atomic():
                City.objects.bulk_create(to_create, ignore_conflicts=True, batch_size=500)

            return Response({
                "statusCode": 200,
                "status": True,
                "imported_count": len(to_create),
                "duplicates": duplicate_names,
                "skipped_rows": skipped_rows,
                "message": f"Imported successfully ({len(to_create)} new cities)"
            }, status=200)

        except Exception as e:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": str(e)
            }, status=400)


 
        
#---------------------------Realtion-----------------------
class RelationListAPIView(APIView):
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

        queryset = Relation.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(
                Q(name__istartswith=search)
            )

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = RelationSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


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


class RelationRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = Relation.objects.get(uuid=uuid, is_deleted=False)
        except Relation.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "Relation not found"}, status=404)
        serializer = RelationSerializer(obj)
        return Response({"statusCode": 200, "status": True, "message": "Retrieved successfully", "data": serializer.data})


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

#
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
        dataset.title="Relation"

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
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['Timezone', 'description', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = Timezone.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(Timezone__istartswith=search) 
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
        duplicates = []
        skipped_rows = []

        required_headers = {'time zone','country'}
        optional_headers = {'state', 'description'}

        try:
            data = []

            # ---------------- XLSX ----------------
            if format_type == 'xlsx':
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
                for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    row_dict["_row_number"] = idx
                    data.append(row_dict)

            # ---------------- CSV ----------------
            elif format_type == 'csv':
                decoded_file = file.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(decoded_file))
                for idx, row in enumerate(reader, start=2):
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    row_lower["_row_number"] = idx
                    data.append(row_lower)
            else:
                return Response({'error': 'Unsupported file format. Use .xlsx or .csv'}, status=400)

            # ---------------- Process Data ----------------
            imported_count = 0
            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")
                tz_name = str(row.get('time zone')).strip() if row.get('time zone') else None
                country_name = str(row.get('country')).strip() if row.get('country') else None
                state_name = str(row.get('state')).strip() if row.get('state') else None
                description = str(row.get('description')).strip() if row.get('description') else ''

                # Skip if timezone is missing
                if not tz_name:
                    skipped_rows.append({
                        "Row": row_number,
                        "Reason": "Missing time zone"
                    })
                    continue

                # Skip if country is missing
                if not country_name:
                    skipped_rows.append({
                        "Row": row_number,
                        "Reason": "Invalid or missing country"
                    })
                    continue

                # Check country exists in DB
                country_obj = Country.objects.filter(name__iexact=country_name, is_deleted=False).first()
                if not country_obj:
                    skipped_rows.append({
                        "Row": row_number,
                        "Reason": "Invalid or missing country"
                    })
                    continue

                # Handle state if provided
                state_obj = None
                if state_name:
                    state_obj = State.objects.filter(stateName__iexact=state_name, is_deleted=False).first()
                    if not state_obj:
                        state_obj = State.objects.create(
                            stateName=state_name,
                            countryName=country_obj,
                            description='',
                            is_deleted=False
                        )

                # Check duplicates
                existing = Timezone.objects.filter(
                    Timezone__iexact=tz_name,
                    countryName=country_obj
                ).first()

                if existing:
                    if not existing.is_deleted:
                        duplicates.append({
                            "Row": row_number,
                            "Timezone": tz_name,
                            "Reason": "Already exists in database"
                        })
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
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": duplicates,
            "skipped_rows": skipped_rows
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
                Q(civil_id_name__istartswith=search) 
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




# -----------------------department---------------------------------


class DepartmentListAPIView(APIView):
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
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
                Q(name__istartswith=search)
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
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get("file")
        sheet_name = request.data.get("sheet_name")

        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split(".")[-1].lower()
        duplicates = []
        skipped_rows = []

        required_headers = {"department"}
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
                name = str(row.get("department")).strip() if row.get("department") else None
                description = str(row.get("description")).strip() if row.get("description") else ""

                # Skip if no department name
                if not name:
                    skipped_rows.append({
                        "Row": row_number,
                        "Reason": "Missing department name"
                    })
                    continue

                existing = Department.objects.filter(name__iexact=name).first()

                if existing:
                    if not existing.is_deleted:
                        duplicates.append({
                            "Row": row_number,
                            "Department": name,
                            "Reason": "Already exists in database"
                        })
                        continue
                    else:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    Department.objects.create(
                        name=name,
                        description=description,
                        is_deleted=False,
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



# -----------------------employeeType---------------------------------
class EmployeeTypeListAPIView(APIView):    

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
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
                Q(name__istartswith=search)
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
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get("file")
        sheet_name = request.data.get("sheet_name")

        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split(".")[-1].lower()
        duplicates = []
        skipped_rows = []

        required_headers = {"employee type"}
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
                name = str(row.get("employee type")).strip() if row.get("employee type") else None
                description = str(row.get("description")).strip() if row.get("description") else ""

                # Skip if no name
                if not name:
                    skipped_rows.append({
                        "Row": row_number,
                        "Reason": "Missing employee type name"
                    })
                    continue

                existing = EmployeeType.objects.filter(name__iexact=name).first()

                if existing:
                    if not existing.is_deleted:
                        duplicates.append({
                            "Row": row_number,
                            "Employee Type": name,
                            "Reason": "Already exists in database"
                        })
                        continue
                    else:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    EmployeeType.objects.create(
                        name=name,
                        description=description,
                        is_deleted=False,
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





#--------------------------companyType------------------------
class CompanyTypeListAPIView(APIView):    
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
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
                Q(name__istartswith=search)
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
    API to import Company Types from CSV or XLSX, with duplicate and skipped row tracking.
    """
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get("file")
        sheet_name = request.data.get("sheet_name")

        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split(".")[-1].lower()
        duplicates = []
        skipped_rows = []

        # Define headers
        required_headers = {"company type"}
        optional_headers = {"description"}

        try:
            data = []

            # ---------- XLSX Handling ----------
            if format_type == "xlsx":
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                # Check for sheet name
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

                # Extract headers
                headers = [
                    str(cell.value).strip().lower() if cell.value else ""
                    for cell in next(ws.iter_rows(min_row=1, max_row=1))
                ]

                # Validate headers
                if not required_headers.issubset(set(headers)):
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f"Missing required headers. Required: {required_headers}, Found: {set(headers)}"
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Read rows
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

                    # Validate headers
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

            # ---------- Import Logic ----------
            imported_count = 0

            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")
                name = str(row.get("company type")).strip() if row.get("company type") else None
                description = str(row.get("description")).strip() if row.get("description") else ""

                # Skip if no name provided
                if not name:
                    skipped_rows.append({
                        "Row": row_number,
                        "Reason": "Missing company type name"
                    })
                    continue

                existing = CompanyType.objects.filter(name__iexact=name).first()

                if existing:
                    if not existing.is_deleted:
                        duplicates.append({
                            "Row": row_number,
                            "Company Type": name,
                            "Reason": "Already exists in database"
                        })
                        continue
                    else:
                        # Restore deleted entry
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    # Create new entry
                    CompanyType.objects.create(
                        name=name,
                        description=description,
                        is_deleted=False,
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








class OwnershipTypeListAPIView(APIView):    
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
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
                Q(name__istartswith=search)
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
            'company_type': 'Company Type',
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
    
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get("file")
        sheet_name = request.data.get("sheet_name")

        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split(".")[-1].lower()
        duplicates = []
        skipped_rows = []

        required_headers = {"ownership type"}
        optional_headers = {"description", "company type"}

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

            # ---------- Import Logic ----------
            imported_count = 0

            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")
                ownership_name = str(row.get("ownership type")).strip() if row.get("ownership type") else None
                description = str(row.get("description")).strip() if row.get("description") else ""
                company_type_name = str(row.get("company type")).strip() if row.get("company type") else None

                if not ownership_name:
                    skipped_rows.append({
                        "Row": row_number,
                        "Reason": "Missing ownership type name"
                    })
                    continue

                if not company_type_name:
                    skipped_rows.append({
                        "Row": row_number,
                        "Ownership Type": ownership_name,
                        "Reason": "Missing company type"
                    })
                    continue

                # Find company type
                company_type = CompanyType.objects.filter(name__iexact=company_type_name).first()
                if not company_type:
                    skipped_rows.append({
                        "Row": row_number,
                        "Ownership Type": ownership_name,
                        "Reason": f'Company Type "{company_type_name}" not found'
                    })
                    continue

                # Check uniqueness on (ownership_name, company_type)
                existing = OwnershipType.objects.filter(
                    name__iexact=ownership_name,
                    company_type=company_type
                ).first()

                if existing:
                    if not existing.is_deleted:
                        duplicates.append({
                            "Row": row_number,
                            "Ownership Type": ownership_name,
                            "Company Type": company_type_name or "N/A",
                            "Reason": "Already exists in database"
                        })
                        continue
                    else:
                        # Restore deleted record
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    # Create new entry
                    OwnershipType.objects.create(
                        name=ownership_name,
                        description=description,
                        company_type=company_type,
                        is_deleted=False
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
        sort_by = request.GET.get('sortBy', 'created_at')
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
                Q(name__istartswith=search)
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
    
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicates = []
        skipped_rows = []

        required_headers = {'stakeholdercategory'}
        optional_headers = {'description'}

        def normalize_header(h):
            if not h:
                return ''
            return ''.join(c for c in str(h).lower() if c.isalnum())

        try:
            data = []

            # ---------- XLSX Handling ----------
            if format_type == 'xlsx':
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({'error': 'Please provide sheet_name', 'available_sheets': available_sheets},
                                    status=status.HTTP_400_BAD_REQUEST)
                if sheet_name not in available_sheets:
                    return Response({'error': f'Sheet "{sheet_name}" not found', 'available_sheets': available_sheets},
                                    status=status.HTTP_400_BAD_REQUEST)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({'statusCode': 400, 'status': False,
                                     'message': f'Sheet "{sheet_name}" is empty.'},
                                    status=status.HTTP_400_BAD_REQUEST)

                headers = [normalize_header(cell.value) for cell in next(ws.iter_rows(min_row=1, max_row=1))]

                if not required_headers.issubset(set(headers)):
                    return Response({'statusCode': 400, 'status': False,
                                     'message': f'Missing required headers. Required: {required_headers}, Found: {set(headers)}'},
                                    status=status.HTTP_400_BAD_REQUEST)

                for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    row_dict["_row_number"] = idx
                    data.append(row_dict)

            # ---------- CSV Handling ----------
            elif format_type == 'csv':
                decoded_file = file.read().decode('utf-8')
                dataset = Dataset()
                dataset.load(decoded_file, format='csv')

                for idx, row in enumerate(dataset.dict, start=2):
                    row_lower = {normalize_header(k): v for k, v in row.items()}
                    row_lower["_row_number"] = idx

                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({
                            "statusCode": 400,
                            "status": False,
                            "message": f'Missing required headers. Required: {required_headers}, Found: {set(row_lower.keys())}'
                        }, status=status.HTTP_400_BAD_REQUEST)

                    if not any(row_lower.values()):
                        continue
                    data.append(row_lower)

            else:
                return Response({'error': 'Unsupported file format. Use .xlsx or .csv'},
                                status=status.HTTP_400_BAD_REQUEST)

            # ---------- Import Logic ----------
            imported_count = 0
            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")
                name = str(row.get('stakeholdercategory')).strip() if row.get('stakeholdercategory') else None
                description = str(row.get('description')).strip() if row.get('description') else ''

                if not name:
                    skipped_rows.append({"Row": row_number, "Reason": "Missing stakeholder category name"})
                    continue

                existing = StakeholderCategory.objects.filter(name__iexact=name).first()
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({"Row": row_number, "Stakeholder Category": name, "Reason": "Already exists"})
                        continue
                    else:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
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
                "status": False,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": duplicates,
            "skipped_rows": skipped_rows
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
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['name', 'description', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = StakeholderType.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(name__istartswith=search)
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
        category_id = request.data.get("category")

        # Check if the stakeholder type already exists with the same name and category
        existing = StakeholderType.objects.filter(name__iexact=name, category_id=category_id, is_deleted=False).first()
        if existing:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "StakeholderType with this name and category already exists."
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
        duplicates = []
        skipped_rows = []

        def normalize_header(h):
            if not h:
                return ''
            return ''.join(c for c in str(h).lower() if c.isalnum())

        # Normalized required and optional headers
        required_headers = {normalize_header('stakeholder type'), normalize_header('stakeholder category')}
        optional_headers = {normalize_header('description')}

        try:
            data = []

            # ---------- XLSX Handling ----------
            if format_type == 'xlsx':
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({'error': 'Please provide sheet_name', 'available_sheets': available_sheets},
                                    status=status.HTTP_400_BAD_REQUEST)
                if sheet_name not in available_sheets:
                    return Response({'error': f'Sheet "{sheet_name}" not found', 'available_sheets': available_sheets},
                                    status=status.HTTP_400_BAD_REQUEST)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({'statusCode': 400, 'status': False,
                                     'message': f'Sheet "{sheet_name}" is empty.'},
                                    status=status.HTTP_400_BAD_REQUEST)

                headers = [normalize_header(cell.value) for cell in next(ws.iter_rows(min_row=1, max_row=1))]

                if not required_headers.issubset(set(headers)):
                    return Response({'statusCode': 400, 'status': False,
                                     'message': f'Missing required headers. Required: {required_headers}, Found: {set(headers)}'},
                                    status=status.HTTP_400_BAD_REQUEST)

                for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    row_dict["_row_number"] = idx
                    data.append(row_dict)

            # ---------- CSV Handling ----------
            elif format_type == 'csv':
                decoded_file = file.read().decode('utf-8')
                dataset = Dataset()
                dataset.load(decoded_file, format='csv')

                for idx, row in enumerate(dataset.dict, start=2):
                    row_lower = {normalize_header(k): v for k, v in row.items()}
                    row_lower["_row_number"] = idx

                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({
                            "statusCode": 400,
                            "status": False,
                            "message": f'Missing required headers. Required: {required_headers}, Found: {set(row_lower.keys())}'
                        }, status=status.HTTP_400_BAD_REQUEST)

                    if not any(row_lower.values()):
                        continue
                    data.append(row_lower)

            else:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    'error': 'Unsupported file format. Use .xlsx or .csv'
                }, status=status.HTTP_400_BAD_REQUEST)

            # ---------- Import Logic ----------
            imported_count = 0
            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")
                name = str(row.get('stakeholdertype')).strip() if row.get('stakeholdertype') else None
                description = str(row.get('description')).strip() if row.get('description') else ''
                category_name = str(row.get('stakeholdercategory')).strip() if row.get('stakeholdercategory') else None

                if not name:
                    skipped_rows.append({"Row": row_number, "Reason": "Missing stakeholder type name"})
                    continue

                if not category_name:
                    skipped_rows.append({"Row": row_number, "Stakeholder Type": name, "Reason": "Missing stakeholder category"})
                    continue

                category_obj = StakeholderCategory.objects.filter(name__iexact=category_name, is_deleted=False).first()
                if not category_obj:
                    skipped_rows.append({"Row": row_number, "Stakeholder Type": name, "Reason": f'Category "{category_name}" not found'})
                    continue

                existing = StakeholderType.objects.filter(
                    name__iexact=name,
                    category=category_obj
                ).first()

                if existing:
                    if not existing.is_deleted:
                        duplicates.append({"Row": row_number, "Stakeholder Type": name,
                                           "Stakeholder Category": category_name, "Reason": "Already exists"})
                        continue
                    else:
                        existing.description = description
                        existing.category = category_obj
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    StakeholderType.objects.create(
                        name=name,
                        description=description,
                        category=category_obj,
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
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": duplicates,
            "skipped_rows": skipped_rows
        }, status=status.HTTP_200_OK)



class AccreditationCategoryListAPIView(APIView):
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

        queryset = AccreditationCategory.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(name__istartswith=search)
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
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicates = []
        skipped_rows = []

        def normalize_header(h):
            if not h:
                return ''
            return ''.join(c for c in str(h).lower() if c.isalnum())

        # Normalize required and optional headers
        required_headers = {normalize_header('accrediation category')}
        optional_headers = {normalize_header('description')}

        try:
            data = []

            # ---------- XLSX Handling ----------
            if format_type == 'xlsx':
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({'error': 'Please provide sheet_name', 'available_sheets': available_sheets}, status=400)
                if sheet_name not in available_sheets:
                    return Response({'error': f'Sheet "{sheet_name}" not found', 'available_sheets': available_sheets}, status=400)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({'statusCode': 400, 'status': False, 'message': f'Sheet "{sheet_name}" is empty.'}, status=400)

                headers = [normalize_header(cell.value) for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                if not required_headers.issubset(set(headers)):
                    return Response({'statusCode': 400, 'status': False, 'message': f'Missing required headers. Required: {required_headers}, Found: {set(headers)}'}, status=400)

                for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    row_dict["_row_number"] = idx
                    data.append(row_dict)

            # ---------- CSV Handling ----------
            elif format_type == 'csv':
                decoded_file = file.read().decode('utf-8')
                dataset = Dataset()
                dataset.load(decoded_file, format='csv')

                for idx, row in enumerate(dataset.dict, start=2):
                    row_lower = {normalize_header(k): v for k, v in row.items()}
                    row_lower["_row_number"] = idx

                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({'statusCode': 400, 'status': False, 'message': f'Missing required headers. Required: {required_headers}, Found: {set(row_lower.keys())}'}, status=400)

                    if not any(row_lower.values()):
                        continue
                    data.append(row_lower)

            else:
                return Response({'error': 'Unsupported file format. Use .xlsx or .csv'}, status=400)

            # ---------- Import Logic ----------
            imported_count = 0
            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")
                name = str(row.get('accrediationcategory')).strip() if row.get('accrediationcategory') else None
                description = str(row.get('description')).strip() if row.get('description') else ''

                if not name:
                    skipped_rows.append({"Row": row_number, "Reason": "Missing accreditation category name"})
                    continue

                existing = AccreditationCategory.objects.filter(name__iexact=name).first()
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({"Row": row_number, "Accrediation Category": name, "Reason": "Already exists"})
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
            return Response({'statusCode': 400, 'status': False, 'message': str(e)}, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": duplicates,
            "skipped_rows": skipped_rows
        }, status=200)  


#-------------------------------------------accrediation Name---------------------------------

class AccreditationNameListAPIView(APIView):
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['full_name', 'short_name', 'valid_upto', 'created_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = AccreditationName.objects.all()
        if search:
            queryset = queryset.filter(
                Q(full_name__istartswith=search)
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
                                'Accrediation Full Name': full_name,
                                'country': country_name,
                                'category': category_name,
                                'Reason': f"Invalid date format '{valid_date_raw}'. Expected formats: dd-mm-yyyy, dd/mm/yyyy "
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
        sort_by = request.GET.get('sortBy', 'created_at')
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
                Q(name__istartswith=search)
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
    permission_classes = [IsAuthenticated, IsAdminUser]

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
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicates = []
        skipped_rows = []

        def normalize_header(h):
            if not h:
                return ''
            return ''.join(c for c in str(h).lower() if c.isalnum())

        # Normalize required and optional headers
        required_headers = {normalize_header('bank account type')}
        optional_headers = {normalize_header('description')}

        try:
            data = []

            # ---------- XLSX Handling ----------
            if format_type == 'xlsx':
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({'error': 'Please provide sheet_name', 'available_sheets': available_sheets}, status=400)
                if sheet_name not in available_sheets:
                    return Response({'error': f'Sheet "{sheet_name}" not found', 'available_sheets': available_sheets}, status=400)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({'statusCode': 400, 'status': False, 'message': f'Sheet "{sheet_name}" is empty.'}, status=400)

                headers = [normalize_header(cell.value) for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                if not required_headers.issubset(set(headers)):
                    return Response({'statusCode': 400, 'status': False, 'message': f'Missing required headers. Required: {required_headers}, Found: {set(headers)}'}, status=400)

                for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    row_dict["_row_number"] = idx
                    data.append(row_dict)

            # ---------- CSV Handling ----------
            elif format_type == 'csv':
                decoded_file = file.read().decode('utf-8')
                dataset = Dataset()
                dataset.load(decoded_file, format='csv')

                for idx, row in enumerate(dataset.dict, start=2):
                    row_lower = {normalize_header(k): v for k, v in row.items()}
                    row_lower["_row_number"] = idx
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({'statusCode': 400, 'status': False, 'message': f'Missing required headers. Required: {required_headers}, Found: {set(row_lower.keys())}'}, status=400)
                    if not any(row_lower.values()):
                        continue
                    data.append(row_lower)

            else:
                return Response({'error': 'Unsupported file format. Use .xlsx or .csv'}, status=400)

            # ---------- Import Logic ----------
            imported_count = 0
            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")
                name = str(row.get('bankaccounttype')).strip() if row.get('bankaccounttype') else None
                description = str(row.get('description')).strip() if row.get('description') else ''

                if not name:
                    skipped_rows.append({"Row": row_number, "Reason": "Missing bank account type name"})
                    continue

                existing = BankAccountType.objects.filter(name__iexact=name).first()
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({"Row": row_number, "Bank Account Type": name, "Reason": "Already exists"})
                        continue
                    else:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    BankAccountType.objects.create(name=name, description=description, is_deleted=False)
                    imported_count += 1

        except Exception as e:
            return Response({'statusCode': 400, 'status': False, 'message': str(e)}, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": duplicates,
            "skipped_rows": skipped_rows
        }, status=200)






#-------------------------------------------LicenseName---------------------------------
class LicenseNameListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['full_name', 'short_name', 'issuing_authority', 'valid_upto', 'created_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = LicenseName.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(full_name__istartswith=search)
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
        country_id = request.data.get("Country")

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
    permission_classes = [IsAuthenticated, IsAdminUser]
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
            'country': 'Country',
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
    permission_classes = [IsAuthenticated, IsAdminUser]

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
    permission_classes = [IsAuthenticated, IsAdminUser]
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
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
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
                Q(name__istartswith=search)
            )

        queryset = queryset.order_by(sort_by)

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = LeadSourceSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)


class LeadSourceRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
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
    permission_classes = [IsAuthenticated, IsAdminUser]
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
    permission_classes = [IsAuthenticated, IsAdminUser]

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
    permission_classes = [IsAuthenticated, IsAdminUser]
    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicates = []
        skipped_rows = []

        required_headers = {'lead source'}
        optional_headers = {'description', 'is_active'}

        try:
            data = []

            # ---------------- XLSX ----------------
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

                for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    row_dict["_row_number"] = idx
                    data.append(row_dict)

            # ---------------- CSV ----------------
            elif format_type == 'csv':
                decoded_file = file.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(decoded_file))
                for idx, row in enumerate(reader, start=2):
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    row_lower["_row_number"] = idx
                    data.append(row_lower)
            else:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": 'Unsupported file format. Use .xlsx or .csv'
                }, status=status.HTTP_400_BAD_REQUEST)

            # ---------------- Process Data ----------------
            imported_count = 0
            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")
                name = str(row.get('lead source')).strip() if row.get('lead source') else None
                description = str(row.get('description')).strip() if row.get('description') else ''
                
                if not name:
                    skipped_rows.append({
                        "Row": row_number,
                        "Reason": "Missing lead source name"
                    })
                    continue

                existing = LeadSource.objects.filter(name__iexact=name).first()
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({
                            "Row": row_number,
                            "Lead Source": name,
                            "Reason": "Already exists in database"
                        })
                        continue
                    else:
                        # Reactivate deleted
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
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
                "status": False,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        # ---------------- Response ----------------
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": duplicates,
            "skipped_rows": skipped_rows
        }, status=status.HTTP_200_OK)


#-------------------------------------------InterestLevel---------------------------------



class InterestLevelCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
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
    permission_classes = [IsAuthenticated, IsAdminUser] 
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
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
                Q(name__istartswith=search)
            )

        queryset = queryset.order_by(sort_by)

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = InterestLevelSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)

class InterestLevelRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
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
    permission_classes = [IsAuthenticated, IsAdminUser]
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
    permission_classes = [IsAuthenticated, IsAdminUser]
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
        queryset = queryset.order_by('-created_at')

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
    permission_classes = [IsAuthenticated, IsAdminUser]
    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicates = []
        skipped_rows = []

        required_headers = {'interest level'}
        optional_headers = {'description', 'is_active'}

        try:
            data = []

            # ---------------- XLSX ----------------
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

                for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    row_dict["_row_number"] = idx
                    data.append(row_dict)

            # ---------------- CSV ----------------
            elif format_type == 'csv':
                decoded_file = file.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(decoded_file))
                for idx, row in enumerate(reader, start=2):
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    row_lower["_row_number"] = idx
                    data.append(row_lower)
            else:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": 'Unsupported file format. Use .xlsx or .csv'
                }, status=status.HTTP_400_BAD_REQUEST)

            # ---------------- Process Data ----------------
            imported_count = 0
            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")
                name = str(row.get('interest level')).strip() if row.get('interest level') else None
                description = str(row.get('description')).strip() if row.get('description') else ''
                
                if not name:
                    skipped_rows.append({
                        "Row": row_number,
                        "Reason": "Missing interest level name"
                    })
                    continue

                existing = InterestLevel.objects.filter(name__iexact=name).first()
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({
                            "Row": row_number,
                            "Interest Level": name,
                            "Reason": "Already exists in database"
                        })
                        continue
                    else:
                        # Reactivate deleted
                        existing.description = description
                        
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    InterestLevel.objects.create(
                        name=name,
                        description=description,
                       
                        is_deleted=False
                    )
                    imported_count += 1

        except Exception as e:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        # ---------------- Response ----------------
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": duplicates,
            "skipped_rows": skipped_rows
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
    permission_classes = [IsAuthenticated, IsAdminUser] 
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
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
                Q(name__istartswith=search)
            )

        queryset = queryset.order_by(sort_by)

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = PrioritySerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)


class PriorityRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
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
    permission_classes = [IsAuthenticated, IsAdminUser]
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
    permission_classes = [IsAuthenticated, IsAdminUser]

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
    permission_classes = [IsAuthenticated, IsAdminUser]
    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicates = []
        skipped_rows = []

        required_headers = {'priority'}
        optional_headers = {'description', 'is_active'}

        try:
            data = []

            # ---------------- XLSX ----------------
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

                for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    row_dict["_row_number"] = idx
                    data.append(row_dict)

            # ---------------- CSV ----------------
            elif format_type == 'csv':
                decoded_file = file.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(decoded_file))
                for idx, row in enumerate(reader, start=2):
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    row_lower["_row_number"] = idx
                    data.append(row_lower)
            else:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": 'Unsupported file format. Use .xlsx or .csv'
                }, status=status.HTTP_400_BAD_REQUEST)

            # ---------------- Process Data ----------------
            imported_count = 0
            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")
                name = str(row.get('priority')).strip() if row.get('priority') else None
                description = str(row.get('description')).strip() if row.get('description') else ''
                
                if not name:
                    skipped_rows.append({
                        "Row": row_number,
                        "Reason": "Missing priority name"
                    })
                    continue

                existing = Priority.objects.filter(name__iexact=name).first()
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({
                            "Row": row_number,
                            "Priority": name,
                            "Reason": "Already exists in database"
                        })
                        continue
                    else:
                        # Reactivate deleted
                        existing.description = description
                        
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    Priority.objects.create(
                        name=name,
                        description=description,
                       
                        is_deleted=False
                    )
                    imported_count += 1

        except Exception as e:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        # ---------------- Response ----------------
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": duplicates,
            "skipped_rows": skipped_rows
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
    permission_classes = [IsAuthenticated, IsAdminUser]  
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
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
                Q(name__istartswith=search)
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
    permission_classes = [IsAuthenticated, IsAdminUser]
    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')  
        uuids_param = request.GET.get('uuids', '')

        uuids = [u.strip() for u in uuids_param.split(',') if u]

        # Default fields if none provided
        field_header_map = {
            'uuid': 'UUID',
            'name': 'Tags',  
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
        dataset.title="Tags"

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
    permission_classes = [IsAuthenticated, IsAdminUser]
    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')  # optional, for XLSX

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicates = []
        skipped_rows = []

        required_headers = {'tags'}
        optional_headers = {'description', 'is_active'}

        try:
            data = []

            # ---------------- XLSX ----------------
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

                for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    row_dict["_row_number"] = idx
                    data.append(row_dict)

            # ---------------- CSV ----------------
            elif format_type == 'csv':
                decoded_file = file.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(decoded_file))
                for idx, row in enumerate(reader, start=2):
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    row_lower["_row_number"] = idx
                    data.append(row_lower)
            else:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": 'Unsupported file format. Use .xlsx or .csv'
                }, status=status.HTTP_400_BAD_REQUEST)

            # ---------------- Process Data ----------------
            imported_count = 0
            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")
                name = str(row.get('tags')).strip() if row.get('tags') else None
                description = str(row.get('description')).strip() if row.get('description') else ''
                
                if not name:
                    skipped_rows.append({
                        "Row": row_number,
                        "Reason": "Missing tag name"
                    })
                    continue

                existing = Tags.objects.filter(name__iexact=name).first()
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({
                            "Row": row_number,
                            "Tags": name,
                            "Reason": "Already exists in database"
                        })
                        continue
                    else:
                        # Reactivate deleted
                        existing.description = description
                        
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
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
                "status": False,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        # ---------------- Response ----------------
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": duplicates,
            "skipped_rows": skipped_rows
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
    permission_classes = [IsAuthenticated, IsAdminUser]  
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
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
                Q(name__istartswith=search)
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
    permission_classes = [IsAuthenticated, IsAdminUser]
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
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def normalize_header(self, header):
        if not header:
            return ''
        return header.strip().lower().replace('(', '').replace(')', '')

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')  # optional for XLSX

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicates = []
        skipped_rows = []

        required_headers = {'activity type'}
        optional_headers = {'description', 'is_active'}
        data = []

        try:
            # ---------------- XLSX ----------------
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

                headers = [self.normalize_header(str(cell.value)) for cell in next(ws.iter_rows(min_row=1, max_row=1))]

                for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    row_dict["_row_number"] = idx
                    data.append(row_dict)

            # ---------------- CSV ----------------
            elif format_type == 'csv':
                decoded_file = file.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(decoded_file))
                for idx, row in enumerate(reader, start=2):
                    row_lower = {self.normalize_header(k): v for k, v in row.items()}
                    row_lower["_row_number"] = idx
                    data.append(row_lower)
            else:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": 'Unsupported file format. Use .xlsx or .csv'
                }, status=status.HTTP_400_BAD_REQUEST)

            # ---------------- Process Data ----------------
            imported_count = 0
            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")
                name = str(row.get('activity type')).strip() if row.get('activity type') else None
                description = str(row.get('description')).strip() if row.get('description') else ''
                
                if not name:
                    skipped_rows.append({
                        "Row": row_number,
                        "Reason": "Missing activity type name"
                    })
                    continue

                existing = ActivityType.objects.filter(name__iexact=name).first()
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({
                            "Row": row_number,
                            "Activity Type": name,
                            "Reason": "Already exists in database"
                        })
                        continue
                    else:
                        # Reactivate deleted
                        existing.description = description
                        
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
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
                "status": False,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        # ---------------- Response ----------------
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": duplicates,
            "skipped_rows": skipped_rows
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
    permission_classes = [IsAuthenticated, IsAdminUser]  
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
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
                Q(name__istartswith=search)
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
    permission_classes = [IsAuthenticated, IsAdminUser]
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
    permission_classes = [IsAuthenticated, IsAdminUser]
    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')  # optional for XLSX

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicates = []
        skipped_rows = []

        required_headers = {'lost reason (b2c)'}
        optional_headers = {'description', 'is_active'}
        data = []

        try:
            # ---------------- XLSX ----------------
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

                for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    row_dict["_row_number"] = idx
                    data.append(row_dict)

            # ---------------- CSV ----------------
            elif format_type == 'csv':
                decoded_file = file.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(decoded_file))
                for idx, row in enumerate(reader, start=2):
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    row_lower["_row_number"] = idx
                    data.append(row_lower)
            else:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": 'Unsupported file format. Use .xlsx or .csv'
                }, status=status.HTTP_400_BAD_REQUEST)

            # ---------------- Process Data ----------------
            imported_count = 0
            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")
                name = str(row.get('lost reason (b2c)')).strip() if row.get('lost reason (b2c)') else None
                description = str(row.get('description')).strip() if row.get('description') else ''
                
                if not name:
                    skipped_rows.append({
                        "Row": row_number,
                        "Reason": "Missing lost reason name"
                    })
                    continue

                existing = LostReason.objects.filter(name__iexact=name).first()
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({
                            "Row": row_number,
                            "Lost Reason (B2C)": name,
                            "Reason": "Already exists in database"
                        })
                        continue
                    else:
                        # Reactivate deleted
                        existing.description = description
                        
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
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
                "status": False,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        # ---------------- Response ----------------
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": duplicates,
            "skipped_rows": skipped_rows
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
    permission_classes = [IsAuthenticated, IsAdminUser]   
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
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
                Q(name__istartswith=search)
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
    permission_classes = [IsAuthenticated, IsAdminUser]
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
    permission_classes = [IsAuthenticated, IsAdminUser]
    def normalize_header(self, header):
        """Normalize headers: lowercase, strip spaces, remove parentheses."""
        if not header:
            return ''
        return header.strip().lower().replace('(', '').replace(')', '')

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')  # optional for XLSX

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicates = []
        skipped_rows = []
        data = []

        required_headers = {'lost reason b2b'}
        optional_headers = {'description', 'is_active'}

        try:
            # ---------------- XLSX ----------------
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

                headers = [self.normalize_header(str(cell.value)) for cell in next(ws.iter_rows(min_row=1, max_row=1))]

                for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    row_dict["_row_number"] = idx
                    data.append(row_dict)

            # ---------------- CSV ----------------
            elif format_type == 'csv':
                decoded_file = file.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(decoded_file))
                for idx, row in enumerate(reader, start=2):
                    row_lower = {self.normalize_header(k): v for k, v in row.items()}
                    row_lower["_row_number"] = idx
                    data.append(row_lower)

            else:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": 'Unsupported file format. Use .xlsx or .csv'
                }, status=status.HTTP_400_BAD_REQUEST)

            # ---------------- Process Data ----------------
            imported_count = 0
            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")
                name = str(row.get('lost reason b2b')).strip() if row.get('lost reason b2b') else None
                description = str(row.get('description')).strip() if row.get('description') else ''
                
                if not name:
                    skipped_rows.append({
                        "Row": row_number,
                        "Reason": "Missing lost reason name"
                    })
                    continue

                existing = LostReasonB2B.objects.filter(name__iexact=name).first()
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({
                            "Row": row_number,
                            "Lost Reason (B2B)": name,
                            "Reason": "Already exists in database"
                        })
                        continue
                    else:
                        # Reactivate deleted
                        existing.description = description
                        
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    LostReasonB2B.objects.create(
                        name=name,
                        description=description,
                       
                        is_deleted=False
                    )
                    imported_count += 1

        except Exception as e:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        # ---------------- Response ----------------
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": duplicates,
            "skipped_rows": skipped_rows
        }, status=status.HTTP_200_OK)


class DegreeAwardedByEducationLevelAPIView(APIView):
    def get(self, request):
        # Get the uuid from the query parameters
        uuid = request.GET.get('uuid')
        
        if not uuid:
            return Response(
                {
                    "statuscode": 400,
                    "status": False,
                    "message": "UUID parameter is required."
                },
                status=400
            )

        try:
            degrees = DegreeAwardedBy.objects.filter(education_level__uuid=uuid)

            if not degrees.exists():
                return Response(
                    {
                        "statuscode": 404,
                        "status": False,
                        "message": "No degrees found for the given Education Level."
                    },
                    status=404
                )

            serializer = DegreeAwardedBySerializer(degrees, many=True)
            return Response(
                {
                    "statuscode": 200,
                    "status": True,
                    "data": serializer.data
                },
                status=200
            )

        except Exception as e:
            return Response(
                {
                    "statuscode": 500,
                    "status": False,
                    "message": "An unexpected error occurred: " + str(e)
                },
                status=500
            )



class EntranceTestModulesAPIView(APIView):
    def get(self, request):
        entrance_test_id = request.GET.get("entrance_test_id")
        search_term = request.GET.get("search", "")       # search by module name
        sort_by = request.GET.get("sort_by", "moduleName")  # default sorting

        if not entrance_test_id:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "entrance_test_id is required"
            }, status=400)

        # Validate UUID
        try:
            test_uuid = uuid.UUID(entrance_test_id.strip())
        except ValueError:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Invalid UUID format for entrance_test_id"
            }, status=400)

        # Fetch EntranceTest
        try:
            entrance_test = EntranceTestName.objects.get(uuid=test_uuid, is_deleted=False)
        except EntranceTestName.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Entrance Test not found"
            }, status=404)

        # Fetch associated modules
        modules = EntranceTestModuleName.objects.filter(entrancetest=entrance_test, is_deleted=False)

        # Search filter
        if search_term:
            modules = modules.filter(moduleName__icontains=search_term)

        # Sorting
        if sort_by and hasattr(EntranceTestModuleName, sort_by):
            modules = modules.order_by(sort_by)

        # Pagination
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(modules, request)

        # Prepare response
        data = []
        for module in result_page:
            data.append({
                "uuid": str(module.uuid),
                "moduleName": module.moduleName,
                "description": module.description,
                "entrance_test": entrance_test.fullname
            })

        return paginator.get_paginated_response(data)


class LanguageTestsAPIView(APIView):
    def get(self, request):
        language_id = request.GET.get("language_id")
        search_term = request.GET.get("search", "")       # search by test name
        sort_by = request.GET.get("sort_by", "name")      # default sorting

        if not language_id:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "language_id is required"
            }, status=400)

        # Validate UUID
        try:
            lang_uuid = uuid.UUID(language_id.strip())
        except ValueError:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Invalid UUID format for language_id"
            }, status=400)

        # Fetch Language
        try:
            language = Language.objects.get(uuid=lang_uuid, is_deleted=False)
        except Language.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Language not found"
            }, status=404)

        # Fetch associated Language Tests
        tests = LanguageTest.objects.filter(language=language, is_deleted=False)

        # Search filter
        if search_term:
            tests = tests.filter(name__icontains=search_term)

        # Sorting
        if sort_by and hasattr(LanguageTest, sort_by):
            tests = tests.order_by(sort_by)

        # Pagination
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(tests, request)

        # Prepare response
        data = []
        for test in result_page:
            data.append({
                "uuid": str(test.uuid),
                "name": test.name,
                "fullname": test.fullname,
                "description": test.description,
                "language": language.name
            })

        return paginator.get_paginated_response(data)