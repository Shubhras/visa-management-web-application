from django.shortcuts import render
from  .models  import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import  *
from django.core.paginator import Paginator
from django.db.models import Q, F, IntegerField
import uuid
from django.db.models.functions import Lower, Cast
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
    



# -------------------- EducationLevelCode -------------------- #
class EducationLevelCodeListAPIView(APIView):
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')
        allowed_sort_fields = ['Levelcode', 'created_at']

        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = EducationLevelCode.objects.all()
        if search:
            queryset = queryset.filter(
                Q(Levelcode__istartswith=search)
            )

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = EducationLevelCodeSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


# ------------------ CREATE ------------------
# class EducationLevelCodeListAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         search = request.GET.get('search', '').strip()
#         sort_by = request.GET.get('sortBy', 'created_at')
#         sort_order = request.GET.get('sortOrder', 'desc')

#         allowed_sort_fields = ['name', 'description', 'updated_at']
#         if sort_by not in allowed_sort_fields:
#             sort_by = 'created_at'

#         if sort_order == 'desc':
#             sort_by = f'-{sort_by}'

#         queryset = EducationLevelCode.objects.filter(is_deleted=False)

#         if search:
#             queryset = queryset.filter(
#                 Q(name__istartswith=search)
#             )

#         queryset = queryset.order_by(sort_by)

#         paginator = CustomPagination()
#         result_page = paginator.paginate_queryset(queryset, request)
#         serializer = EducationLevelCodeSerializer(result_page, many=True)

#         return paginator.get_paginated_response(serializer.data)


class EducationLevelCodeListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        custom_sort = request.GET.get('customSort')  # new custom sort param
        uuids_param = request.GET.get('uuids', '')


        uuid_list = []
        if uuids_param:
            for u in uuids_param.split(','):
                u = u.strip()
                try:
                    uuid_list.append(UUID(u))
                except:
                    pass  # ignore invalid UUIDs


        # Allowed fields for sorting
        sort_field_map = {
            'name': 'name',
            'description': 'description',
            'updated_at': 'updated_at',
            'created_at': 'created_at',
        }

        queryset = EducationLevelCode.objects.filter(is_deleted=False)



        # -------------------------------------
        # UUID Filter
        # -------------------------------------
        if uuid_list:
            queryset = queryset.filter(uuid__in=uuid_list)

        # -------------------------------------
        # Search
        # -------------------------------------

        if search:
            queryset = queryset.filter(
                Q(name__istartswith=search)
            )

        # -------------------------------------
        # Custom Sort Logic
        # -------------------------------------
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

                    # Correct type-based sorting
                    if field == 'name':
                        # name numeric sort
                        f = Cast(orm_field, IntegerField())
                    
                    elif field == 'description':
                        # proper alphabetical sorting
                        f = Lower(orm_field)

                    else:
                        f = F(orm_field)

                    sort_fields.append(
                        f.asc(nulls_last=True) if order == 'asc' else f.desc(nulls_last=True)
                    )

                except ValueError as v:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "error": str(v),
                        "message": "ValueError."
                    }, status=status.HTTP_400_BAD_REQUEST)

        
        else:
            # Fallback to simple sorting
            sort_by = request.GET.get('sortBy', 'created_at')
            sort_order = request.GET.get('sortOrder', 'desc')

            if sort_by not in sort_field_map:
                sort_by = 'created_at'

            orm_field = sort_field_map[sort_by]
            f = F(orm_field)

            sort_fields = [
                f.desc(nulls_last=True) if sort_order == 'desc' else f.asc(nulls_last=True)
            ]


        queryset = queryset.order_by(*sort_fields)

        # -------------------------------------
        # Pagination
        # -------------------------------------
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = EducationLevelCodeSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)


class EducationLevelCodeCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        try:
            name = request.data.get("name")

            # Validate: name must exist
            if name is None:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Name field is required."
                }, status=status.HTTP_400_BAD_REQUEST)

            # Validate: name must be an integer
            try:
                name_int = int(name)
            except (ValueError, TypeError):
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Name must be an integer."
                }, status=status.HTTP_400_BAD_REQUEST)

            # Check existing record (use int match instead of iexact)
            existing = EducationLevelCode.objects.filter(
                name=name_int,
                is_deleted=False
            ).first()

            if existing:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Education level code with this name already exists."
                }, status=status.HTTP_400_BAD_REQUEST)

            # Inject cleaned field into request
            data = request.data.copy()
            data['name'] = name_int

            serializer = EducationLevelCodeSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "statusCode": 200,
                    "status": True,
                    "message": "Education level code created successfully",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)

            # Collect serializer errors
            messages = [msg for msgs in serializer.errors.values() for msg in msgs]
            return Response({
                "statusCode": 400,
                "status": False,
                "message": " ".join(messages)
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Catch unexpected errors
            return Response({
                "statusCode": 500,
                "status": False,
                "message": f"Internal server error: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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

    def delete(self, request):
        try:
            ids = request.data.get("id", None)

            # Validate if IDs are provided
            if not ids or not isinstance(ids, list):
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Please provide a list of UUIDs in the 'id' field.",
                    "data": None
                }, status=status.HTTP_400_BAD_REQUEST)

            valid_uuids = []
            invalid_uuids = []

            # Validate UUIDs
            for u in ids:
                try:
                    valid_uuids.append(UUID(u))
                except (ValueError, TypeError):
                    invalid_uuids.append(u)

            if not valid_uuids:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "No valid UUIDs provided.",
                    "data": {"invalid_uuids": invalid_uuids}
                }, status=status.HTTP_400_BAD_REQUEST)

            # Delete valid UUIDs
            queryset = EducationLevelCode.objects.filter(uuid__in=valid_uuids)
            count = queryset.count()
            queryset.delete()

            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"{count} education level code(s) permanently deleted.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "statusCode": 500,
                "status": False,
                "message": f"Internal server error: {str(e)}",
                "data": None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ------------------ Export API ------------------
# class EducationLevelCodeExportAPIView(APIView):

#     def get(self, request):
#         format_type = request.GET.get('format', 'xlsx').lower()
#         fields = request.GET.get('fields')  # comma-separated
#         uuids_param = request.GET.get('uuids', '')
        
#         uuids = [u.strip() for u in uuids_param.split(',') if u]

#         field_header_map = {
#             'uuid': 'UUID',
#             'name': 'Education Level Code',
#             'description': 'Description',
#             'is_deleted': 'Deleted',
#             'updated_at': 'Modified On',
#         }

#         field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())

#         queryset = EducationLevelCode.objects.filter(is_deleted=False)
#         if uuids:
#             queryset = queryset.filter(uuid__in=uuids)
#         queryset = queryset.order_by('-created_at')

#         dataset = Dataset()
#         dataset.headers = [field_header_map.get(f, f) for f in field_list]
#         dataset.title = 'EducationLevelCode'

#         for edu in queryset:
#             row = []
#             for field in field_list:
#                 value = getattr(edu, field, '')
#                 if field in ['created_at', 'updated_at'] and value:
#                     value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
#                 elif isinstance(value, bool):
#                     value = int(value)
#                 row.append(value if value is not None else '')
#             dataset.append(row)

#         if format_type == 'csv':
#             file_data = dataset.export('csv')
#             content_type = 'text/csv'
#             file_name = 'education_level_codes.csv'
#         else:
#             file_data = io.BytesIO(dataset.export('xlsx'))
#             content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
#             file_name = 'education_level_codes.xlsx'

#         response = HttpResponse(
#             file_data if format_type == 'csv' else file_data.getvalue(),
#             content_type=content_type
#         )
#         response['Content-Disposition'] = f'attachment; filename="{file_name}"'
#         return response

class EducationLevelCodeExportAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # ---------------------------
            # Query Params
            # ---------------------------
            format_type = request.GET.get('format', 'xlsx').lower()
            fields = request.GET.get('fields')
            uuids_param = request.GET.get('uuids', '')
            custom_sort = request.GET.get('customSort')
            search = request.GET.get('search', '').strip()

            # Validate format
            if format_type not in ['xlsx', 'csv']:
                return Response({
                    "status": False,
                    "statusCode": 400,
                    "message": "Invalid format. Allowed: xlsx, csv"
                }, status=400)

            # ---------------------------
            # Field Mapping for Headers
            # ---------------------------
            field_header_map = {
                'uuid': 'UUID',
                'name': 'Education Level Code',
                'description': 'Description',
                'is_deleted': 'Deleted',
                'created_at': 'Created On',
                'updated_at': 'Modified On',
            }

            # Validate fields
            if fields:
                field_list = [f.strip() for f in fields.split(',')]
                invalid_fields = [f for f in field_list if f not in field_header_map]
                if invalid_fields:
                    return Response({
                        "status": False,
                        "statusCode": 400,
                        "message": f"Invalid fields: {invalid_fields}",
                    }, status=400)
            else:
                field_list = list(field_header_map.keys())

            # ---------------------------
            # UUID Processing
            # ---------------------------
            uuids = []
            if uuids_param:
                for u in uuids_param.split(','):
                    u = u.strip()
                    if not u:
                        continue
                    try:
                        uuids.append(UUID(u))
                    except:
                        return Response({
                            "status": False,
                            "statusCode": 400,
                            "message": f"Invalid UUID: {u}",
                        }, status=400)

            # ---------------------------
            # Base QuerySet
            # ---------------------------
            queryset = EducationLevelCode.objects.filter(is_deleted=False)

            if uuids:
                queryset = queryset.filter(uuid__in=uuids)

            if search:
                queryset = queryset.filter(
                    Q(name__istartswith=search)
                )

            # ---------------------------
            # Sorting Logic
            # ---------------------------
            sort_field_map = {
                'uuid': 'uuid',
                'name': 'name',
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
                            return Response({
                                "status": False,
                                "statusCode": 400,
                                "message": f"Invalid sort field: {field}",
                            }, status=400)

                        orm_field = sort_field_map[field]

                        if order not in ['asc', 'desc']:
                            return Response({
                                "status": False,
                                "statusCode": 400,
                                "message": f"Invalid sort order: {order}. Use asc/desc",
                            }, status=400)

                        # case-insensitive for description only
                        f = Lower(orm_field) if field == 'description' else F(orm_field)

                        sort_fields.append(
                            f.asc(nulls_last=True) if order == 'asc' 
                            else f.desc(nulls_last=True)
                        )
                    except ValueError:
                        return Response({
                            "status": False,
                            "statusCode": 400,
                            "message": f"Invalid sorting rule format: {rule}",
                        }, status=400)

            else:
                f = F('created_at')
                sort_order = request.GET.get('sortOrder', 'desc')

                sort_fields = [
                    f.desc(nulls_last=True) if sort_order == 'desc'
                    else f.asc(nulls_last=True)
                ]

            queryset = queryset.order_by(*sort_fields)

            # ---------------------------
            # Preparing Dataset
            # ---------------------------
            dataset = Dataset()
            dataset.headers = [field_header_map[f] for f in field_list]

            for edu in queryset:
                row = []
                for field in field_list:
                    value = getattr(edu, field, '')

                    if field in ['created_at', 'updated_at'] and value:
                        value = timezone.localtime(value).strftime("%d-%m-%Y %I:%M:%S %p")
                    elif isinstance(value, bool):
                        value = int(value)

                    row.append(value or "")

                dataset.append(row)

            # ---------------------------
            # Export File
            # ---------------------------
            if format_type == 'csv':
                file_data = dataset.export('csv')
                content_type = 'text/csv'
                file_name = 'education_level_codes.csv'
                response_content = file_data
            else:
                file_buffer = io.BytesIO(dataset.export('xlsx'))
                content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                file_name = 'education_level_codes.xlsx'
                response_content = file_buffer.getvalue()

            # Final Response
            response = HttpResponse(response_content, content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'
            return response

        except Exception as e:
            # Catch-all safety net
            return Response({
                "status": False,
                "statusCode": 500,
                "message": "Internal server error",
                "error": str(e)
            }, status=500)

# ------------------ Import API ------------------
class EducationLevelCodeImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicates = []
        skipped_rows = []

        required_headers = {'education level code'}
        optional_headers = {'description'}

        try:
            data = []

            # ---------------- XLSX ----------------
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
                missing_headers = required_headers - set(headers)
                if missing_headers:
                    return Response({'error': f'Missing required headers: {missing_headers}'}, status=400)

                for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    row_dict["_row_number"] = idx
                    data.append(row_dict)

            # ---------------- CSV ----------------
            elif format_type == 'csv':
                import csv
                import io
                decoded_file = file.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(decoded_file))
                for idx, row in enumerate(reader, start=2):
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({'error': f'Missing required headers. Required: {required_headers}, Found: {set(row_lower.keys())}'}, status=400)
                    row_lower["_row_number"] = idx
                    data.append(row_lower)
            else:
                return Response({'error': 'Unsupported file format. Use .xlsx or .csv'}, status=400)

            # ---------------- Process Data ----------------
            imported_count = 0
            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")
                name = str(row.get('education level code')).strip() if row.get('education level code') else None
                description = str(row.get('description')).strip() if row.get('description') else ''

                
                if not name:
                    skipped_rows.append({"Row": row_number, "Reason": "Missing education level code"})
                    continue

                # Check if name is numeric
                if not str(name).isnumeric():
                    skipped_rows.append({"Row": row_number, "Education Level Code": name, "Reason": "Education level code must be numeric"})
                    continue

                # Convert to int for database (optional if your model field is IntegerField)
                name = int(name)

                existing = EducationLevelCode.objects.filter(name__iexact=name).first()
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({"Row": row_number, "Education Level Code": name, "Reason": "Already exists in database"})
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

# -------------------- EducationLevel -------------------- #

# class EducationLevelListAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         search = request.GET.get('search', '').strip()
#         sort_by = request.GET.get('sortBy', 'created_at')
#         sort_order = request.GET.get('sortOrder', 'desc')

#         # Allowed sort fields
#         allowed_sort_fields = ['educationlevel', 'description', 'created_at']
#         if sort_by not in allowed_sort_fields:
#             sort_by = 'created_at'

#         if sort_order == 'desc':
#             sort_by = f'-{sort_by}'

#         queryset = EducationLevel.objects.filter(is_deleted=False)

#         if search:
#             queryset = queryset.filter(
#                 Q(educationlevel__istartswith=search) 
#             )

#         queryset = queryset.order_by(sort_by)

#         paginator = CustomPagination()
#         result_page = paginator.paginate_queryset(queryset, request)
#         serializer = EducationLevelSerializer(result_page, many=True)

#         return paginator.get_paginated_response(serializer.data)
    

class EducationLevelListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        custom_sort = request.GET.get('customSort')
        uuid_param = request.GET.get('educationLevelCode', '')

        # Allowed fields for sorting
        allowed_sort_fields = [
            'uuid', 'educationlevel', 'description', 'durations',
            'created_at', 'updated_at', 'level_code'
        ]

        queryset = EducationLevel.objects.filter(is_deleted=False)

        # ---------------------------
        # UUID Filter
        # ---------------------------
        uuid_list = []
        if uuid_param:
            for u in uuid_param.split(','):
                u = u.strip()
                try:
                    uuid_list.append(UUID(u))
                except:
                    pass

        if uuid_list:
            queryset = queryset.filter(uuid__in=uuid_list)

        # ---------------------------
        # Search filter
        # ---------------------------
        if search:
            queryset = queryset.filter(
                Q(educationlevel__icontains=search)
            )

        # ---------------------------
        # Sort field mapping
        # ---------------------------
        sort_field_map = {
            'uuid': 'uuid',
            'educationlevel': 'educationlevel',
            'description': 'description',
            'durations': 'durations',
            'created_at': 'created_at',
            'updated_at': 'updated_at',
            'level_code': 'level_code__name',  # Foreign Key field
        }

        sort_fields = []

        # ---------------------------
        # CUSTOM SORT
        # ---------------------------
        if custom_sort:
            for rule in custom_sort.split(','):
                try:
                    field, order = rule.split(':')
                    field = field.strip()
                    order = order.strip().lower()

                    if field not in sort_field_map:
                        continue

                    orm_field = sort_field_map[field]

                    # STRING fields → Lower()
                    if field in ['educationlevel', 'description', 'level_code']:
                        f = Lower(orm_field)
                    else:
                        f = F(orm_field)

                    sort_fields.append(
                        f.asc(nulls_last=True) if order == 'asc' else f.desc(nulls_last=True)
                    )

                except ValueError:
                    continue

        # ---------------------------
        # DEFAULT SORT (single field)
        # ---------------------------
        else:
            sort_by = request.GET.get('sortBy', 'created_at')
            sort_order = request.GET.get('sortOrder', 'desc')

            orm_field = sort_field_map.get(sort_by, 'created_at')
            f = F(orm_field)

            sort_fields = [
                f.asc(nulls_last=True) if sort_order.lower() == 'asc' else f.desc(nulls_last=True)
            ]

        # ---------------------------
        # APPLY SORTING
        # ---------------------------
        queryset = queryset.order_by(*sort_fields)

        # ---------------------------
        # Pagination + Response
        # ---------------------------
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = EducationLevelSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)



class EducationLevelCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        educationlevel_name = request.data.get('educationlevel', '').strip()

        # Check for duplicate based on combination of level_code and educationlevel
        existing = EducationLevel.objects.filter(
            educationlevel__iexact=educationlevel_name
            # level_code_id=level_code_id
        ).first()

        if existing:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "This Education Level with the selected Level Code already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create new record
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

    def delete(self, request, uuid=None):
        ids = request.data.get('id', None)

        # Delete by single UUID from URL
        if uuid:
            try:
                edu_level = EducationLevel.objects.get(uuid=uuid, is_deleted=False)
                edu_level.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "Education Level permanently deleted.",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            except EducationLevel.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Education Level not found.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        # Delete all Education Levels
        if ids == "all":
            objs = EducationLevel.objects.filter(is_deleted=False)
            count = objs.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No Education Levels found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
            objs.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} Education Level(s) permanently deleted.",
                "data": None
            }, status=status.HTTP_200_OK)

        # Delete multiple UUIDs
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

        objs = EducationLevel.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = objs.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching Education Levels found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_404_NOT_FOUND)

        objs.delete()
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} Education Level(s) permanently deleted.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        }, status=status.HTTP_200_OK)




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
            'durations':'Education Durations',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'created_at': 'Created On',
            'updated_at': 'Modified On',
        }

        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())

        queryset = EducationLevel.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(educationlevel__uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'EducationLevel'

        for obj in queryset:
            row = []
            for field in field_list:
                if field == 'level_code':
                    value = obj.level_code.name if obj.level_code else ''
                else:
                    value = getattr(obj, field, '')

                if field in ['created_at', 'updated_at'] and value:
                    value = timezone.localtime(value).strftime("%d-%m-%Y %I:%M:%S %p")
                elif isinstance(value, bool):
                    value = int(value)
                row.append(str(value) if value is not None else '')
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
        duplicates = []
        skipped_rows = []

        required_headers = {'education level code', 'education level','education duration'}
        optional_headers = {'description', 'is_deleted'}

        try:
            data = []

            # ---------------- XLSX ----------------
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
                missing_headers = required_headers - set(headers)
                if missing_headers:
                    return Response({'error': f'Missing required headers: {missing_headers}'}, status=400)

                for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    row_dict["_row_number"] = idx
                    data.append(row_dict)

            # ---------------- CSV ----------------
            elif format_type == 'csv':
                import csv
                import io
                decoded_file = file.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(decoded_file))
                for idx, row in enumerate(reader, start=2):
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({'error': f'Missing required headers. Required: {required_headers}, Found: {set(row_lower.keys())}'}, status=400)
                    row_lower["_row_number"] = idx
                    data.append(row_lower)
            else:
                return Response({'error': 'Unsupported file format. Use .xlsx or .csv'}, status=400)

           

            imported_count = 0
            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")
                level_code_id = row.get('education level code')
                education_level_name = str(row.get('education level')).strip() if row.get('education level') else None
                durations = str(row.get('education duration')).strip() if row.get('education duration') else None
                description = str(row.get('description')).strip() if row.get('description') else ''
                is_deleted = bool(int(row.get('is_deleted', 0))) if row.get('is_deleted') is not None else False

                # Skip if required fields are missing
                if not level_code_id or not education_level_name:
                    skipped_rows.append({"Row": row_number, "Reason": "Missing education level code or education level"})
                    continue

                # Check if level_code_id is numeric
                if not str(level_code_id).isnumeric():
                    skipped_rows.append({"Row": row_number, "Education Level Code": level_code_id, "Reason": "Education level code must be numeric"})
                    continue

                # Convert to int for querying
                level_code_id = int(level_code_id)

                # Validate LevelCode existence
                level_code_obj = EducationLevelCode.objects.filter(id=level_code_id, is_deleted=False).first()
                if not level_code_obj:
                    skipped_rows.append({"Row": row_number, "Education Level Code": level_code_id, "Reason": "Invalid education level code"})
                    continue

                

                existing = EducationLevel.objects.filter(level_code_id=level_code_id, educationlevel__iexact=education_level_name).first()
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({"Row": row_number, "Education Level": education_level_name, "Education Level Code": level_code_id,"Reason": "Already exists"})
                        continue
                    else:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    EducationLevel.objects.create(
                        level_code_id=level_code_id,
                        durations=durations,
                        educationlevel=education_level_name,
                        description=description,
                        is_deleted=is_deleted
                    )
                    imported_count += 1

        except Exception as e:
            return Response({
                "statusCode": 400,
                "status": False,
                'message': str(e)
            }, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": duplicates,
            "skipped_rows": skipped_rows
        }, status=200)

#----------------------------EducationDuration----------------------


class EducationDurationListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')  # 'asc' or 'desc'

        allowed_sort_fields = ['durations', 'description', 'created_at', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        sort_prefix = '-' if sort_order == 'desc' else ''
        queryset = EducationDuration.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(educationlevel__educationlevel__istartswith=search)
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
                if field == 'educationlevel':
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
        duplicates = []
        skipped_rows = []

        required_headers = {'education level', 'education duration'}
        optional_headers = {'description'}

        try:
            data = []

            # ---------------- XLSX ----------------
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
                missing_headers = required_headers - set(headers)
                if missing_headers:
                    return Response({'error': f'Missing required headers: {missing_headers}'}, status=400)

                for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    row_dict["_row_number"] = idx
                    data.append(row_dict)

            # ---------------- CSV ----------------
            elif format_type == 'csv':
                import csv
                import io
                decoded_file = file.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(decoded_file))
                for idx, row in enumerate(reader, start=2):
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({'error': f'Missing required headers. Required: {required_headers}, Found: {set(row_lower.keys())}'}, status=400)
                    row_lower["_row_number"] = idx
                    data.append(row_lower)
            else:
                return Response({'error': 'Unsupported file format. Use .xlsx or .csv'}, status=400)

            # ---------------- Process Data ----------------
            imported_count = 0
            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")
                educationlevel_name = str(row.get('education level')).strip() if row.get('education level') else None
                durations = str(row.get('education duration')).strip() if row.get('education duration') else None
                description = str(row.get('description')).strip() if row.get('description') else ''

                if not educationlevel_name or durations is None:
                    skipped_rows.append({"Row": row_number, "Reason": "Missing education level or education duration"})
                    continue

                # ✅ Check if duration is numeric
                if not str(durations).isnumeric():
                    skipped_rows.append({"Row": row_number, "Education Duration": durations, "Reason": "Education duration must be numeric"})
                    continue

                # Convert duration to int
                durations = int(durations)

                # Validate EducationLevel existence
                educationlevel_obj = EducationLevel.objects.filter(
                    educationlevel__iexact=educationlevel_name, is_deleted=False
                ).first()
                if not educationlevel_obj:
                    skipped_rows.append({"Row": row_number, "Education Level": educationlevel_name, "Reason": "Invalid education level"})
                    continue

                existing = EducationDuration.objects.filter(
                    educationlevel=educationlevel_obj, durations__iexact=durations
                ).first()
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({"Row": row_number, "Education Duration": durations, "Education Level": educationlevel_name, "Reason": "Already exists"})
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
            return Response({
                "statusCode": 400,
                "status": False,
                'message': str(e)
            }, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": duplicates,
            "skipped_rows": skipped_rows
        }, status=200)

# -------------------- Studymainarea -------------------- #



class StudymainareaListAPIView(APIView):
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['name', 'description', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = Studymainarea.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(Q(name__istartswith=search) 
                                       )

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
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicates = []
        skipped_rows = []

        required_headers = {'study main area'}
        optional_headers = {'description'}

        try:
            data = []

            # ---------------- XLSX ----------------
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
                missing_headers = required_headers - set(headers)
                if missing_headers:
                    return Response({'error': f'Missing required headers: {missing_headers}'}, status=400)

                for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    row_dict["_row_number"] = idx
                    data.append(row_dict)

            # ---------------- CSV ----------------
            elif format_type == 'csv':
                import csv
                import io
                decoded_file = file.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(decoded_file))
                for idx, row in enumerate(reader, start=2):
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({'error': f'Missing required headers. Required: {required_headers}, Found: {set(row_lower.keys())}'}, status=400)
                    row_lower["_row_number"] = idx
                    data.append(row_lower)
            else:
                return Response({'error': 'Unsupported file format. Use .xlsx or .csv'}, status=400)

            # ---------------- Process Data ----------------
            imported_count = 0
            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")
                name = str(row.get('study main area')).strip() if row.get('study main area') else None
                description = str(row.get('description')).strip() if row.get('description') else ''

                if not name:
                    skipped_rows.append({"Row": row_number, "Reason": "Missing study main area"})
                    continue

                existing = Studymainarea.objects.filter(name__iexact=name).first()
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({"Row": row_number, "Study Main Area": name, "Reason": "Already exists"})
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
            return Response({
                "statusCode": 400,
                "status": False,
                'message': str(e)
            }, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": duplicates,
            "skipped_rows": skipped_rows
        }, status=200)



# -------------------- Studymajor -------------------- #

class StudyMajorAreaListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['majorarea', 'description', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = Studymajorarea.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(majorarea__istartswith=search) 
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
        duplicates = []
        skipped_rows = []

        required_headers = {'study major area', 'study main area'}
        optional_headers = {'description'}

        try:
            data = []

            # ---------------- XLSX ----------------
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
                missing_headers = required_headers - set(headers)
                if missing_headers:
                    return Response({'error': f'Missing required headers: {missing_headers}'}, status=400)

                for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    row_dict["_row_number"] = idx
                    data.append(row_dict)

            # ---------------- CSV ----------------
            elif format_type == 'csv':
                import csv
                import io
                decoded_file = file.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(decoded_file))
                for idx, row in enumerate(reader, start=2):
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({'error': f'Missing required headers. Required: {required_headers}, Found: {set(row_lower.keys())}'}, status=400)
                    row_lower["_row_number"] = idx
                    data.append(row_lower)
            else:
                return Response({'error': 'Unsupported file format. Use .xlsx or .csv'}, status=400)

            # ---------------- Process Data ----------------
            imported_count = 0
            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")
                majorarea_name = str(row.get('study major area')).strip() if row.get('study major area') else None
                mainarea_name = str(row.get('study main area')).strip() if row.get('study main area') else None
                description = str(row.get('description')).strip() if row.get('description') else ''

                # Skip if required fields missing
                if not majorarea_name or not mainarea_name:
                    skipped_rows.append({"Row": row_number, "Reason": "Missing study major area or study main area"})
                    continue

                # Validate main area existence
                mainarea_obj = Studymainarea.objects.filter(name__iexact=mainarea_name, is_deleted=False).first()
                if not mainarea_obj:
                    skipped_rows.append({"Row": row_number, "Study Main Area": mainarea_name, "Reason": "Invalid study main area"})
                    continue

                existing = Studymajorarea.objects.filter(majorarea__iexact=majorarea_name, mainarea=mainarea_obj).first()
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({"Row": row_number, "Study Major Area": majorarea_name,"Study Main Area": mainarea_name, "Reason": "Already exists"})
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
            return Response({
                "statusCode": 400,
                "status": False,
                'message': str(e)
            }, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": duplicates,
            "skipped_rows": skipped_rows
        }, status=200)

# -------------------- Studyspecialisation -------------------- #


class StudySpecialisationListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['studyspecialisation', 'description', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = StudySpecialisation.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(studyspecialisation__istartswith=search) 
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
                if field == 'mainarea_name':
                    value = obj.mainarea.name if obj.mainarea else ''
                elif field == 'majorarea_name':
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
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicates = []
        skipped_rows = []

        required_headers = {'study specialisation', 'study major area', 'study main area'}
        optional_headers = {'description'}

        try:
            data = []

            # ---------------- XLSX ----------------
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
                missing_headers = required_headers - set(headers)
                if missing_headers:
                    return Response({'error': f'Missing required headers: {missing_headers}'}, status=400)

                for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    row_dict["_row_number"] = idx
                    data.append(row_dict)

            # ---------------- CSV ----------------
            elif format_type == 'csv':
                import csv
                import io
                decoded_file = file.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(decoded_file))
                for idx, row in enumerate(reader, start=2):
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({'error': f'Missing required headers. Required: {required_headers}, Found: {set(row_lower.keys())}'}, status=400)
                    row_lower["_row_number"] = idx
                    data.append(row_lower)
            else:
                return Response({'error': 'Unsupported file format. Use .xlsx or .csv'}, status=400)

            # ---------------- Process Data ----------------
            imported_count = 0
            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")
                specialisation_name = str(row.get('study specialisation')).strip() if row.get('study specialisation') else None
                majorarea_name = str(row.get('study major area')).strip() if row.get('study major area') else None
                mainarea_name = str(row.get('study main area')).strip() if row.get('study main area') else None
                description = str(row.get('description')).strip() if row.get('description') else ''

                # Skip if required fields missing
                if not specialisation_name or not majorarea_name or not mainarea_name:
                    skipped_rows.append({"Row": row_number, "Reason": "Missing required field(s)"})
                    continue

                # Validate mainarea
                mainarea_obj = Studymainarea.objects.filter(name__iexact=mainarea_name, is_deleted=False).first()
                if not mainarea_obj:
                    skipped_rows.append({"Row": row_number, "Study Main Area": mainarea_name, "Reason": "Invalid study main area"})
                    continue

                # Validate majorarea belongs to mainarea
                majorarea_obj = Studymajorarea.objects.filter(majorarea__iexact=majorarea_name, mainarea=mainarea_obj, is_deleted=False).first()
                if not majorarea_obj:
                    skipped_rows.append({"Row": row_number, "Study Major Area": majorarea_name, "Reason": "Invalid or mismatched study major area"})
                    continue

                # Existing check
                existing = StudySpecialisation.objects.filter(
                    studyspecialisation__iexact=specialisation_name,
                    majorarea=majorarea_obj
                ).first()

                if existing:
                    if not existing.is_deleted:
                        duplicates.append({"Row": row_number, "Study Specialisation": specialisation_name,"Study Main Area": mainarea_name,"Study Major Area": majorarea_name, "Reason": "Already exists"})
                        continue
                    else:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    StudySpecialisation.objects.create(
                        studyspecialisation=specialisation_name,
                        mainarea=mainarea_obj,
                        majorarea=majorarea_obj,
                        description=description,
                        is_deleted=False
                    )
                    imported_count += 1

        except Exception as e:
            return Response({"statusCode": 400, "status": False, 'message': str(e)}, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": duplicates,
            "skipped_rows": skipped_rows
        }, status=200)


class StudyMajorAreaByMainUUIDAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        main_uuid = request.GET.get('main_uuid', '').strip()
        if not main_uuid:
            return Response({
                "status": False,
                "statusCode": 400,
                "message": "main_uuid query parameter is required",
                "data": None
            }, status=400)

        # Get all major areas for the given main area UUID
        major_areas = Studymajorarea.objects.filter(mainarea__uuid=main_uuid, is_deleted=False)
        
        if major_areas.exists():
            serializer = StudyMajorAreaSerializer(major_areas, many=True)
            return Response({
                "status": True,
                "statusCode": 200,
                "message": "Major areas retrieved successfully",
                "data": serializer.data
            }, status=200)
        else:
            return Response({
                "status": False,
                "statusCode": 404,
                "message": "No major areas found for this main area",
                "data": None
            }, status=404)


# -------------------- AcademicResultType -------------------- 
class AcademicResultTypeListAPIView(APIView):
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['name', 'description', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = AcademicResultType.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(
                Q(name__istartswith=search)
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
            'datatype':'Data Type',
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

        required_headers = {'name', 'datatype'}  # datatype is required now
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
                import csv
                decoded_file = file.read().decode('utf-8').splitlines()
                reader = csv.DictReader(decoded_file)
                for row in reader:
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
            errors = []

            VALID_TYPES = ["Numeric", "Text"]

            for idx, row in enumerate(reversed(data), start=2):  # row number starts at 2 (after header)
                name = str(row.get('name')).strip() if row.get('name') else None
                datatype = str(row.get('datatype')).strip() if row.get('datatype') else None
                description = str(row.get('description')).strip() if row.get('description') else ''

                if not name or not datatype:
                    errors.append(f"Row {idx}: 'name' and 'datatype' are required.")
                    continue

                if datatype not in VALID_TYPES:
                    errors.append(f"Row {idx}: Invalid datatype '{datatype}'. Must be one of {VALID_TYPES}.")
                    continue

                # Validate based on datatype
                if datatype == "Numeric" and not name.isdigit():
                    errors.append(f"Row {idx}: Name '{name}' must be numeric for datatype 'Numeric'.")
                    continue
                elif datatype == "Text" and any(char.isdigit() for char in name):
                    errors.append(f"Row {idx}: Name '{name}' must not contain numbers for datatype 'Text'.")
                    continue

                existing = AcademicResultType.objects.filter(name__iexact=name).first()
                if existing:
                    if not existing.is_deleted:
                        duplicate_names.append(name)
                        continue
                    else:
                        existing.description = description
                        existing.datatype = datatype
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    AcademicResultType.objects.create(
                        name=name,
                        datatype=datatype,
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
            "errors": errors,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count
        }, status=status.HTTP_200_OK)

 
# -------------------- AcademicResult -------------------- #


class AcademicResultListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Optional search query parameters
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
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
                Q(Academicresult__istartwith=search) 
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

    def delete(self, request, uuid=None):
        uuids = request.data.get('id', None)

        # Single delete via URL
        if uuid:
            try:
                obj = AcademicResult.objects.get(uuid=uuid, is_deleted=False)
                obj.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "Academic Result permanently deleted.",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            except AcademicResult.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Academic Result not found.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        # Delete all
        if uuids == "all":
            queryset = AcademicResult.objects.filter(is_deleted=False)
            count = queryset.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No Academic Results found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
            queryset.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} Academic Result(s) permanently deleted.",
                "data": None
            })

        # Bulk delete via list of UUIDs
        if not uuids or not isinstance(uuids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Provide a list of UUIDs in 'id' field or 'all'.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        valid_uuids = []
        invalid_uuids = []
        for u in uuids:
            try:
                valid_uuids.append(UUID(u))
            except ValueError:
                invalid_uuids.append(u)

        queryset = AcademicResult.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = queryset.count()
        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching Academic Results found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_404_NOT_FOUND)

        queryset.delete()
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} Academic Result(s) permanently deleted.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
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
                if field == 'AcademicResulttype_id':
                    value = obj.AcademicResulttype.name if obj.AcademicResulttype else ''
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
        duplicates = []
        skipped_rows = []

        required_headers = {'academic result', 'academic result type'}
        optional_headers = {'description'}

        try:
            data = []

            # ---------------- XLSX ----------------
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
                missing_headers = required_headers - set(headers)
                if missing_headers:
                    return Response({'error': f'Missing required headers: {missing_headers}'}, status=400)

                for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    row_dict["_row_number"] = idx
                    data.append(row_dict)

            # ---------------- CSV ----------------
            elif format_type == 'csv':
                import csv
                import io
                decoded_file = file.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(decoded_file))
                for idx, row in enumerate(reader, start=2):
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({'error': f'Missing required headers. Required: {required_headers}, Found: {set(row_lower.keys())}'}, status=400)
                    row_lower["_row_number"] = idx
                    data.append(row_lower)
            else:
                return Response({'error': 'Unsupported file format. Use .xlsx or .csv'}, status=400)

            # ---------------- Process Data ----------------
            imported_count = 0
            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")
                result_name = str(row.get('academic result')).strip() if row.get('academic result') else None
                result_type_name = str(row.get('academic result type')).strip() if row.get('academic result type') else None
                description = str(row.get('description')).strip() if row.get('description') else ''

                # Skip if required fields missing
                if not result_name or not result_type_name:
                    skipped_rows.append({"Row": row_number, "Reason": "Missing required field(s)"})
                    continue

                # Validate AcademicResultType
                result_type_obj = AcademicResultType.objects.filter(name__iexact=result_type_name, is_deleted=False).first()
                if not result_type_obj:
                    skipped_rows.append({"Row": row_number, "Academic Result Type": result_type_name, "Reason": "Invalid academic result type"})
                    continue

                # Check for existing record
                existing = AcademicResult.objects.filter(
                    AcademicResulttype=result_type_obj,
                    Academicresult__iexact=result_name
                ).first()

                if existing:
                    if not existing.is_deleted:
                        duplicates.append({"Row": row_number, "Academic Result": result_name, "Academic Result Type": result_type_name, "Reason": "Already exists"})
                        continue
                    else:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    AcademicResult.objects.create(
                        AcademicResulttype=result_type_obj,
                        Academicresult=result_name,
                        description=description,
                        is_deleted=False
                    )
                    imported_count += 1

        except Exception as e:
            return Response({"statusCode": 400, "status": False, 'message': str(e)}, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": duplicates,
            "skipped_rows": skipped_rows
        }, status=200)




class AcademicResultComparisonListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['created_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = AcademicResultComparison.objects.all()

        if search:
            queryset = queryset.filter(
                Q(original_result__Academicresult__istartswith=search) 
            )

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = AcademicResultComparisonSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


# ------------------- Create API ------------------- #
class AcademicResultComparisonCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        data = request.data.copy()

        fk_fields = {
            "original_result_type": AcademicResultType,
            "original_result": AcademicResult,
            "compare_result_type": AcademicResultType,
            "compare_result": AcademicResult,
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
                        "message": f"Invalid {field} UUID."
                    }, status=400)
            else:
                fk_objects[field] = None

        # -------------------- Duplicate Check -------------------- #
        existing = AcademicResultComparison.objects.filter(
            original_result_type=fk_objects["original_result_type"],
            original_result=fk_objects["original_result"],
            compare_result_type=fk_objects["compare_result_type"],
            compare_result=fk_objects["compare_result"],
        ).first()

        if existing:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "This result comparison already exists."
            }, status=400)

        # Fill UUIDs for serializer
        for field, obj in fk_objects.items():
            if obj:
                data[field] = obj.uuid

        serializer = AcademicResultComparisonSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Academic result comparison created successfully",
                "data": serializer.data
            })

        error_message = " ".join([msg for msgs in serializer.errors.values() for msg in msgs])
        return Response({"statusCode": 400, "status": False, "message": error_message}, status=400)


# ------------------- Retrieve API ------------------- #
class AcademicResultComparisonRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = AcademicResultComparison.objects.get(uuid=uuid)
        except AcademicResultComparison.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "Not found"}, status=404)

        serializer = AcademicResultComparisonSerializer(obj)
        return Response({"statusCode": 200, "status": True, "data": serializer.data})


# ------------------- Update API ------------------- #
class AcademicResultComparisonUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = AcademicResultComparison.objects.get(uuid=uuid)
        except AcademicResultComparison.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "Not found"}, status=404)

        serializer = AcademicResultComparisonSerializer(obj, data=request.data)
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


# ------------------- Delete API ------------------- #
class AcademicResultComparisonDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        ids = request.data.get('id')

        if not ids:
            return Response({"status": False, "message": "Provide 'id' field"}, status=400)

        if ids == "all":
            objs = AcademicResultComparison.objects.all()
            count = objs.count()
            objs.delete()
            return Response({"status": True, "message": f"All {count} records deleted"})

        if not isinstance(ids, list):
            return Response({"status": False, "message": "Send list of UUIDs"}, status=400)

        valid, invalid = [], []
        for u in ids:
            try:
                valid.append(UUID(u))
            except:
                invalid.append(u)

        objs = AcademicResultComparison.objects.filter(uuid__in=valid)
        count = objs.count()
        objs.delete()

        return Response({
            "status": True,
            "message": f"{count} record(s) deleted",
            "invalid_uuids": invalid if invalid else None
        })


# ------------------- Export API ------------------- #
class AcademicResultComparisonExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get("format", "xlsx").lower()
        fields = request.GET.get("fields")
        uuids = request.GET.get("uuids", "")
        uuids = [u for u in uuids.split(",") if u]

        field_header = {
            'uuid': 'UUID',
            'original_result_type': 'Academic Result Type',
            'original_result': 'Academic Result',
            'compare_result_type': 'Compare : Academic Result Type',
            'compare_result': 'Compare : Academic Result',
            'created_at': 'Created On',
            'updated_at': 'Updated On',
        }

        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header.keys())
        queryset = AcademicResultComparison.objects.all()
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header.get(f, f) for f in field_list]

        for obj in queryset:
            row = []
            for f in field_list:
                val = getattr(obj, f, "")
                if f in ['original_result_type', 'compare_result_type'] and val:
                    val = val.name
                elif f in ['original_result', 'compare_result'] and val:
                    val = val.Academicresult
                elif f in ['created_at', 'updated_at'] and val:
                    val = timezone.localtime(val, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
                row.append(val)
            dataset.append(row)

        if format_type == "csv":
            file_data = dataset.export("csv")
            response = HttpResponse(file_data, content_type="text/csv")
            response["Content-Disposition"] = 'attachment; filename="academic_result_comparison.csv"'
        else:
            file_data = io.BytesIO(dataset.export("xlsx"))
            response = HttpResponse(file_data.getvalue(),
                                    content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            response["Content-Disposition"] = 'attachment; filename="academic_result_comparison.xlsx"'

        return response


# -------------------- EducationType CRUD -------------------- #

class EducationTypeListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
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
                Q(educationType__istartswith=search)
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
        duplicates = []
        skipped_rows = []

        required_headers = {'education type'}
        optional_headers = {'perticulars'}

        try:
            data = []

            # ---------------- XLSX ----------------
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
                missing_headers = required_headers - set(headers)
                if missing_headers:
                    return Response({'error': f'Missing required headers: {missing_headers}'}, status=400)

                for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    row_dict["_row_number"] = idx
                    data.append(row_dict)

            # ---------------- CSV ----------------
            elif format_type == 'csv':
                import csv
                import io
                decoded_file = file.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(decoded_file))
                for idx, row in enumerate(reader, start=2):
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({'error': f'Missing required headers. Required: {required_headers}, Found: {set(row_lower.keys())}'}, status=400)
                    row_lower["_row_number"] = idx
                    data.append(row_lower)

            else:
                return Response({'error': 'Unsupported file format. Use .xlsx or .csv'}, status=400)

            # ---------------- Process Data ----------------
            imported_count = 0
            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")
                name = str(row.get('education type')).strip() if row.get('education type') else None
                perticulars = str(row.get('perticulars')).strip() if row.get('perticulars') else ''

                if not name:
                    skipped_rows.append({"Row": row_number, "Reason": "Missing education type"})
                    continue

                existing = EducationType.objects.filter(educationType__iexact=name).first()
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({"Row": row_number, "Education Type": name, "Reason": "Already exists"})
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
            return Response({"statusCode": 400, "status": False, 'message': str(e)}, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": duplicates,
            "skipped_rows": skipped_rows
        }, status=200)



# -------------------- MediumofEducation CRUD -------------------- #

class MediumofEducationListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
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
                Q(name__istartswith=search) 
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
    permission_classes = [IsAuthenticated, IsAdminUser]

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

            # ---------------- XLSX Handling ----------------
            if format_type == 'xlsx':
                import openpyxl
                wb = openpyxl.load_workbook(file, read_only=True)
                sheets = wb.sheetnames

                if not sheet_name:
                    return Response({'error': 'Please provide sheet_name', 'available_sheets': sheets}, status=status.HTTP_400_BAD_REQUEST)
                if sheet_name not in sheets:
                    return Response({'error': f'Sheet "{sheet_name}" not found', 'available_sheets': sheets}, status=status.HTTP_400_BAD_REQUEST)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({'error': f'Sheet "{sheet_name}" is empty'}, status=status.HTTP_400_BAD_REQUEST)

                headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                if not required_headers.issubset(set(headers)):
                    return Response({'error': f'Missing required headers: {required_headers - set(headers)}'}, status=status.HTTP_400_BAD_REQUEST)

                for row in ws.iter_rows(min_row=2, values_only=True):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    data.append(row_dict)

            # ---------------- CSV Handling ----------------
            elif format_type == 'csv':
                decoded_file = file.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(decoded_file))
                for row in reader:
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({'error': f'Missing required headers: {required_headers - set(row_lower.keys())}'}, status=status.HTTP_400_BAD_REQUEST)
                    data.append(row_lower)

            else:
                return Response({'error': 'Unsupported file format. Use .xlsx or .csv'}, status=status.HTTP_400_BAD_REQUEST)

            imported_count = 0

            # ---------------- Process Data ----------------
            for row in reversed(data):
                name = str(row.get('medium of education')).strip() if row.get('medium of education') else None
                perticulars = str(row.get('perticulars') or '').strip()

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
            return Response({'statusCode': 400, 'status': False, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'statusCode': 200,
            'status': True,
            'duplicates': list(set(duplicate_names)),
            'message': f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            'imported_count': imported_count
        }, status=status.HTTP_200_OK)


class ECAForListAPIView(APIView):

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['name', 'perticulars', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = ECAFor.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(Q(name__istartswith=search))

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = ECAForSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)



class ECAForCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        name = request.data.get("name", "").strip()
        existing = ECAFor.objects.filter(name__iexact=name, is_deleted=False).first()

        if existing:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "ECAFor with this name already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = ECAForSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "ECAFor created successfully",
                "data": serializer.data
            })
        else:
            errors = " ".join([msg for msgs in serializer.errors.values() for msg in msgs])
            return Response({
                "statusCode": 400,
                "status": False,
                "message": errors
            }, status=status.HTTP_400_BAD_REQUEST)



class ECAForRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = ECAFor.objects.get(uuid=uuid, is_deleted=False)
        except ECAFor.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "ECAFor not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = ECAForSerializer(obj)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "ECAFor retrieved successfully",
            "data": serializer.data
        })


class ECAForUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = ECAFor.objects.get(uuid=uuid, is_deleted=False)
        except ECAFor.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "ECAFor not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = ECAForSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "ECAFor updated successfully",
                "data": serializer.data
            })
        else:
            errors = " ".join([msg for msgs in serializer.errors.values() for msg in msgs])
            return Response({
                "statusCode": 400,
                "status": False,
                "message": errors,
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)


class ECAForDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get('id', None)

        if uuid:
            try:
                obj = ECAFor.objects.get(uuid=uuid)
                obj.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "ECAFor permanently deleted.",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            except ECAFor.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "ECAFor not found.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        if ids == "all":
            objs = ECAFor.objects.all()
            count = objs.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No ECAFor found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
            objs.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} ECAFor permanently deleted.",
                "data": None
            })

        if not ids or not isinstance(ids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Provide a list of UUIDs in 'id' field or 'all'.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        valid_uuids, invalid_uuids = [], []
        for u in ids:
            try:
                valid_uuids.append(UUID(u))
            except ValueError:
                invalid_uuids.append(u)

        queryset = ECAFor.objects.filter(uuid__in=valid_uuids)
        count = queryset.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching ECAFor found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_404_NOT_FOUND)

        queryset.delete()

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} ECAFor(s) permanently deleted.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        })



class ECAForExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'name': 'ECA For',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'updated_at': 'Modified On',
        }

        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())

        queryset = ECAFor.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title='ECA For  '

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
            file_name = 'esa_for.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'esa_for.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


class ECAForImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get("file")
        sheet_name = request.data.get("sheet_name")

        if not file:
            return Response({"error": "No file uploaded"}, status=400)

        format_type = file.name.split(".")[-1].lower()
        duplicates = []
        skipped_rows = []
        required_headers = {"eca for"}
        optional_headers = {"description"}
        data = []

        try:
            if format_type == "xlsx":
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames
                if not sheet_name:
                    return Response({"error": "Provide sheet_name", "available_sheets": available_sheets}, status=400)
                if sheet_name not in available_sheets:
                    return Response({"error": f'Sheet "{sheet_name}" not found', "available_sheets": available_sheets}, status=400)
                ws = wb[sheet_name]
                headers = [str(c.value).lower().strip() if c.value else "" for c in next(ws.iter_rows(min_row=1, max_row=1))]
                if not required_headers.issubset(headers):
                    return Response({"error": "Missing required headers"}, status=400)
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
                    if not required_headers.issubset(row_lower.keys()):
                        return Response({"error": "Missing required headers"}, status=400)
                    data.append(row_lower)
            else:
                return Response({"error": "Unsupported file format"}, status=400)

            imported_count = 0
            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")
                name = str(row.get("eca for")) if row.get("eca for") else None
                description = str(row.get("description")).strip() if row.get("description") else ""

                if not name:
                    skipped_rows.append({"Row": row_number, "Reason": "Missing ECAFor name"})
                    continue

                existing = ECAFor.objects.filter(name__iexact=name).first()
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({"Row": row_number, "ECA For": name, "Reason": "Already exists"})
                        continue
                    existing.description = description
                    existing.is_deleted = False
                    existing.save()
                    imported_count += 1
                else:
                    ECAFor.objects.create(name=name, description=description, is_deleted=False)
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




class ECAAwardingBodyListAPIView(APIView):
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['eca_body_full_name', 'eca_body_short_name', 'eca_valid_period', 'created_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = ECAAwardingBody.objects.all()
        if search:
            queryset = queryset.filter(
                Q(eca_body_full_name__istartswith=search) 
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
            'ecafor': 'ECA For',
            'valid_duration_value': 'ECA Valid Duration',
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
        dataset.title = 'ECA Awarding Body'

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

    VALID_UNIT_CHOICES = ["Months", "Weeks", "Years"]  

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name', None)

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        imported_count = 0
        skipped_rows = []
        duplicate_names = []

        required_headers = {'eca body full name', 'country', 'eca for'}
        optional_headers = {'eca body short name', 'valid duration value', 'eca valid period'}

        try:
            data = []

            # ---------- XLSX ----------
            if format_type == 'xlsx':
                wb = openpyxl.load_workbook(file, read_only=True)
                ws = wb[sheet_name] if sheet_name else wb.active
                headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                if not required_headers.issubset(set(headers)):
                    return Response({'statusCode': 400, 'status': False, 'message': f'Missing required headers: {required_headers - set(headers)}'}, status=400)

                for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    row_dict['_row_number'] = idx
                    data.append(row_dict)

            # ---------- CSV ----------
            elif format_type == 'csv':
                decoded_file = file.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(decoded_file))
                headers = [h.strip().lower() for h in reader.fieldnames]

                if not required_headers.issubset(set(headers)):
                    return Response({'statusCode': 400, 'status': False, 'message': f'Missing required headers: {required_headers - set(headers)}'}, status=400)

                for idx, row in enumerate(reader, start=2):
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    row_lower['_row_number'] = idx
                    data.append(row_lower)

            else:
                return Response({'statusCode': 400, 'status': False, 'message': 'Unsupported file format'}, status=400)

            # ---------- Process Data ----------
            for row in reversed(data):
                row_number = row.get('_row_number', 'Unknown')
                full_name = str(row.get('eca body full name')).strip() if row.get('eca body full name') else None
                short_name = str(row.get('eca body short name') or '').strip()
                country_name = str(row.get('country')).strip() if row.get('country') else None
                eca_for_name = str(row.get('eca for')).strip() if row.get('eca for') else None
                valid_duration_value = row.get('valid duration value')
                eca_valid_period = str(row.get('eca valid period') or '').strip()

                # Required fields check
                if not full_name or not country_name or not eca_for_name:
                    skipped_rows.append({"Row": row_number, "full_name": full_name or 'Unknown', "Reason": "Missing required field(s)"})
                    continue

                # Country validation
                country = Country.objects.filter(name__iexact=country_name).first()
                if not country:
                    skipped_rows.append({"Row": row_number, "full_name": full_name, "Reason": f'Country "{country_name}" not found'})
                    continue

                # ECAFor validation
                ecafor = ECAFor.objects.filter(name__iexact=eca_for_name).first()
                if not ecafor:
                    skipped_rows.append({"Row": row_number, "full_name": full_name, "Reason": f'ECAFor "{eca_for_name}" not found'})
                    continue

      

                # Valid duration value validation
                if valid_duration_value is not None:
                    try:
                        valid_duration_value = int(valid_duration_value)
                        if valid_duration_value < 0:
                            raise ValueError
                    except:
                        skipped_rows.append({"Row": row_number, "full_name": full_name, "Reason": 'Valid duration value must be a positive integer'})
                        continue

                # Duplicate check based on unique_together
                existing = ECAAwardingBody.objects.filter(
                    eca_body_full_name__iexact=full_name,
                    country=country,
                    ecafor=ecafor
                ).first()
                if existing:
                    duplicate_names.append(full_name)
                    continue

                # Create record
                ECAAwardingBody.objects.create(
                    eca_body_full_name=full_name,
                    eca_body_short_name=short_name,
                    country=country,
                    ecafor=ecafor,
                    valid_duration_value=valid_duration_value,
                    eca_valid_period=eca_valid_period
                )
                imported_count += 1

        except Exception as e:
            return Response({'statusCode': 400, 'status': False, 'message': str(e)}, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": list(set(duplicate_names)),
            "skipped_rows": skipped_rows,
            "imported_count": imported_count,
            "message": "Import completed"
        })





class DegreeAwardedByListAPIView(APIView):
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['degree_name', 'created_at', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = DegreeAwardedBy.objects.all()
        if search:
            queryset = queryset.filter(
                Q(degree_name__istartswith=search)
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
            'education_level_name': 'Education Level',
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
                elif field == 'education_level_name' and degree.education_level:
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
        duplicate_rows = []

        required_headers = {'degree awarded by', 'country', 'education level'}
        optional_headers = {'description'}

        try:
            data = []

            # ---------- XLSX ----------
            if format_type == 'xlsx':
                wb = openpyxl.load_workbook(file, read_only=True)
                ws = wb[sheet_name] if sheet_name else wb.active
                headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                if not required_headers.issubset(set(headers)):
                    return Response({'statusCode': 400, 'status': False, 'message': f'Missing required headers: {required_headers - set(headers)}'}, status=status.HTTP_400_BAD_REQUEST)
                for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    row_dict['_row_number'] = idx
                    data.append(row_dict)

            # ---------- CSV ----------
            elif format_type == 'csv':
                decoded_file = file.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(decoded_file))
                headers = [h.strip().lower() for h in reader.fieldnames]
                if not required_headers.issubset(set(headers)):
                    return Response({'statusCode': 400, 'status': False, 'message': f'Missing required headers: {required_headers - set(headers)}'}, status=status.HTTP_400_BAD_REQUEST)
                for idx, row in enumerate(reader, start=2):
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    row_lower['_row_number'] = idx
                    data.append(row_lower)
            else:
                return Response({'statusCode': 400, 'status': False, 'message': 'Unsupported file format'}, status=status.HTTP_400_BAD_REQUEST)

            # ---------- Process Data ----------
            for row in reversed(data):
                row_number = row.get('_row_number', 'Unknown')
                degree_name = str(row.get('degree awarded by')).strip() if row.get('degree awarded by') else None
                country_name = str(row.get('country')).strip() if row.get('country') else None
                education_level_name = str(row.get('education level')).strip() if row.get('education level') else None
                description = str(row.get('description') or '').strip()

                # Required fields check
                if not degree_name or not country_name or not education_level_name:
                    skipped_rows.append({
                        "Row": row_number,
                        "Degree Awarded By": degree_name or "Unknown",
                        "Country": country_name,
                        "Education Level": education_level_name,
                        "Reason": "Missing required field(s)"
                    })
                    continue

                # Foreign key validation
                country = Country.objects.filter(name__iexact=country_name).first()
                education_level = EducationLevel.objects.filter(educationlevel__iexact=education_level_name).first()
                if not country:
                    skipped_rows.append({
                        "Row": row_number,
                        "Degree Awarded By": degree_name,
                        "Country": country_name,
                        "Education Level": education_level_name,
                        "Reason": f'Country "{country_name}" not found'
                    })
                    continue
                if not education_level:
                    skipped_rows.append({
                        "Row": row_number,
                        "Degree Awarded By": degree_name,
                        "Country": country_name,
                        "Education Level": education_level_name,
                        "Reason": f'Education Level "{education_level_name}" not found'
                    })
                    continue

                # Duplicate check
                existing = DegreeAwardedBy.objects.filter(degree_name__iexact=degree_name, country=country, education_level=education_level).first()
                if existing:
                    duplicate_rows.append({
                        "Row": row_number,
                        "Degree Awarded By": degree_name,
                        "Country": country_name,
                        "Education Level": education_level_name,
                        "Reason": "Already exists"
                    })
                    continue

                # Create record
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
            "duplicates": duplicate_rows,
            "skipped_rows": skipped_rows,
            "imported_count": imported_count,
            "message": "Import completed"
        })







        
class DegreeAwardedInstituteListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['name', 'created_at', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = DegreeAwardedInstitute.objects.all()
        if search:
            queryset = queryset.filter(
                Q(name__istartswith=search) 
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
                    value = obj.state.stateName
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
                    skipped_rows.append({'name': name or 'Unknown', 'Reason': 'Missing required field(s)'})
                    continue

                # Map DegreeAwardedBy
                degree_awarded_by = DegreeAwardedBy.objects.filter(degree_name__iexact=degree_awarded_by_name).first()
                if not degree_awarded_by:
                    skipped_rows.append({'name': name, 'Reason': f'Degree Awarded By "{degree_awarded_by_name}" not found'})
                    continue

                # Map Country, State, Education Level
                country = Country.objects.filter(name__iexact=country_name).first() if country_name else None
                state = State.objects.filter(stateName__iexact=state_name).first() if state_name else None
                education_level = EducationLevel.objects.filter(name__iexact=education_level_name).first() if education_level_name else None

                # Check duplicate
                existing = DegreeAwardedInstitute.objects.filter(name__iexact=name, degree_awarded_by=degree_awarded_by).first()
                if existing:
                    duplicate_names.append({
                        'name': name,
                        'Degree Awarded By': degree_awarded_by_name,
                        'Country': country_name,
                        'State': state_name,
                        'Education Level': education_level_name,
                        'Reason': 'Duplicate entry found'
                    })
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
            "duplicates": duplicate_names,  
            "skipped_rows": skipped_rows,
            "imported_count": imported_count,
            "message": "Import successful"
        })