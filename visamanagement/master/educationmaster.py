from django.shortcuts import render
from  .models  import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import  *
from django.core.paginator import Paginator
from django.db.models import Q, F, IntegerField, Case, When
import re
from django.db.models.functions import Lower, Cast
from rest_framework.permissions import IsAuthenticated ,AllowAny ,BasePermission 
from django.shortcuts import get_object_or_404
from .pagination import  *
import io
import io as io_lib
import io
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
from django.db import IntegrityError, transaction, DatabaseError
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
            search = request.GET.get("search", "").strip()
            ids = request.data.get("id", None)
            delete_all = request.data.get("deleteAll", False)

            # ----------------------------------
            # If id == "all" → delete entire table
            # ----------------------------------
            if ids == "all":
                count = EducationLevelCode.objects.count()
                EducationLevelCode.objects.all().delete()
                return Response({
                    "statusCode": 200,
                    "status": True,
                    "message": f"All {count} education level code(s) deleted from the table.",
                })

            # Base queryset (not deleted soft filter)
            queryset = EducationLevelCode.objects.filter(is_deleted=False)

            # -----------------------------
            # If SEARCH applied → filter list
            # -----------------------------
            if search:
                queryset = queryset.filter(Q(name__istartswith=search))

            # -----------------------------
            # deleteAll with search filter
            # -----------------------------
            if delete_all:
                count = queryset.count()
                queryset.delete()
                return Response({
                    "statusCode": 200,
                    "status": True,
                    "message": f"{count} education level code(s) deleted based on search filter.",
                })

            # -----------------------------
            # Specific UUID deletion block
            # -----------------------------
            if not ids or not isinstance(ids, list):
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Please provide a list of UUIDs in the 'id' field, or send 'all' to delete everything."
                }, status=400)

            valid_uuids = []
            invalid_uuids = []

            for u in ids:
                try:
                    valid_uuids.append(UUID(u))
                except:
                    invalid_uuids.append(u)

            queryset = queryset.filter(uuid__in=valid_uuids)
            count = queryset.count()
            queryset.delete()

            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"{count} education level code(s) deleted.",
                "invalid_uuids": invalid_uuids if invalid_uuids else None
            })

        except Exception as e:
            return Response({
                "statusCode": 500,
                "status": False,
                "message": f"Internal server error: {str(e)}"
            }, status=500)
        


# ------------------ Export API ------------------


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
                queryset = queryset.filter(uuid__in=uuids).distinct()

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
            dataset.title = 'EducationLevelCode'

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
                    skipped_rows.append(
                        {
                        "Row": row_number,
                        "Education Level Code'":name or "",
                        "Description":description or "",
                        "Reason": "Missing education level code"
                            
                            })
                    continue

                # Check if name is numeric
                if not str(name).isnumeric():
                    skipped_rows.append({"Row": row_number,
                        "Education Level Code'":name or "",
                        "Description":description or "",
                        "Reason": "Education level code must be numeric"})
                    continue

                # Convert to int for database (optional if your model field is IntegerField)
                name = int(name)

                existing = EducationLevelCode.objects.filter(name__iexact=name).first()
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({"Row": row_number,
                        "Education Level Code'":name or "",
                        "Description":description or "",
                        "Reason": "Already exists in database"})
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
            "duplicates": list(reversed(duplicates)),
            "skipped_rows": list(reversed(skipped_rows)),
        }, status=status.HTTP_200_OK)

# -------------------- EducationLevel -------------------- #

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
            queryset = queryset.filter(level_code__uuid__in=uuid_list)

        # ---------------------------
        # Search filter
        # ---------------------------
        if search:
            queryset = queryset.filter(
                Q(educationlevel__istartswith=search)
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
        level_code_id = request.data.get('level_code')

        # Check for duplicate based on combination of level_code and educationlevel
        existing = EducationLevel.objects.filter(
            educationlevel__iexact=educationlevel_name,
            level_code__uuid=level_code_id
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




# class EducationLevelDeleteAPIView(APIView):
#     permission_classes = [IsAuthenticated, IsAdminUser]

#     def delete(self, request, uuid=None):
#         search = request.GET.get('search', '').strip()
#         level_code_uuid = request.GET.get('level_code', '').strip()
#         ids = request.data.get('id', None)

#         # -----------------------------
#         # DELETE BY SINGLE UUID (URL)
#         # -----------------------------
#         if uuid:
#             try:
#                 obj = EducationLevel.objects.get(uuid=uuid, is_deleted=False)
#                 obj.delete()
#                 return Response({
#                     "statusCode": 204,
#                     "status": True,
#                     "message": "Education Level deleted successfully",
#                     "data": None
#                 }, status=status.HTTP_204_NO_CONTENT)

#             except EducationLevel.DoesNotExist:
#                 return Response({
#                     "statusCode": 404,
#                     "status": False,
#                     "message": "Education Level not found",
#                     "data": None
#                 }, status=status.HTTP_404_NOT_FOUND)

#         # -----------------------------------
#         # BUILD FILTERED QUERYSET (VERY IMPORTANT)
#         # -----------------------------------
#         queryset = EducationLevel.objects.filter(is_deleted=False)

#         if search:
#             queryset = queryset.filter(educationlevel__istartswith=search)

#         if level_code_uuid:
#             queryset = queryset.filter(level_code__uuid=level_code_uuid)

#         # -----------------------------------
#         # DELETE ALL (BUT ONLY FILTERED DATA)
#         # -----------------------------------
#         if ids == "all":
#             count = queryset.count()
#             if count == 0:
#                 return Response({
#                     "statusCode": 404,
#                     "status": False,
#                     "message": "No records found to delete for current filters.",
#                     "data": None
#                 }, status=status.HTTP_404_NOT_FOUND)

#             queryset.delete()

#             return Response({
#                 "statusCode": 200,
#                 "status": True,
#                 "message": f"{count} record(s) deleted based on current filters.",
#                 "data": None
#             }, status=status.HTTP_200_OK)

#         # -----------------------------------
#         # DELETE MULTIPLE UUIDs
#         # -----------------------------------
#         if not ids or not isinstance(ids, list):
#             return Response({
#                 "statusCode": 400,
#                 "status": False,
#                 "message": "Please provide 'id' as list or 'all'.",
#                 "data": None
#             }, status=status.HTTP_400_BAD_REQUEST)

#         valid_uuids = []
#         invalid_uuids = []

#         # Validate UUIDs
#         for u in ids:
#             try:
#                 valid_uuids.append(UUID(u))
#             except ValueError:
#                 invalid_uuids.append(u)

#         objs = queryset.filter(uuid__in=valid_uuids)
#         count = objs.count()

#         if count == 0:
#             return Response({
#                 "statusCode": 404,
#                 "status": False,
#                 "message": "No matching records found in filtered data.",
#                 "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
#             }, status=status.HTTP_404_NOT_FOUND)

#         objs.delete()

#         return Response({
#             "statusCode": 200,
#             "status": True,
#             "message": f"{count} record(s) deleted successfully.",
#             "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
#         }, status=status.HTTP_200_OK)


class EducationLevelDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        try:
            search = request.GET.get("search", "").strip()
            delete_all = request.data.get("deleteAll", False)
            ids = request.data.get("id", None)


            # ----------------------------------
            # If id == "all" → delete entire table
            # ----------------------------------
            if ids == "all":
                count = EducationLevel.objects.count()
                EducationLevel.objects.all().delete()
                return Response({
                    "statusCode": 200,
                    "status": True,
                    "message": f"All {count} education level code(s) deleted from the table.",
                })

            # ---------------------------------------------------
            # Parse comma-separated UUID list from query param
            # ---------------------------------------------------
            def parse_uuid_list(param):
                raw = request.GET.get(param, '')
                result = []
                if raw:
                    for x in raw.split(','):
                        try:
                            result.append(UUID(x.strip()))
                        except:
                            pass
                return result

            level_code_uuids = parse_uuid_list('educationLevelCode')

            # ---------------------------------------------------
            # BASE QUERYSET
            # ---------------------------------------------------
            queryset = EducationLevel.objects.filter(is_deleted=False)

            # Track active filters for response message
            applied_filters = []

            # ---------------------------------------------------
            # SEARCH FILTER
            # ---------------------------------------------------
            if search:
                queryset = queryset.filter(Q(educationlevel__istartswith=search))
                applied_filters.append("search")

            # ---------------------------------------------------
            # LEVEL CODE FILTER
            # ---------------------------------------------------
            if level_code_uuids:
                queryset = queryset.filter(level_code__uuid__in=level_code_uuids)
                applied_filters.append("educationLevelCode")

            # ---------------------------------------------------
            # DELETE ALL MATCHING FILTERED RESULTS
            # ---------------------------------------------------
            if delete_all:
                count = queryset.count()
                queryset.delete()

                # Smart response message
                if not applied_filters:
                    msg = f"All {count} education level(s) deleted."
                elif applied_filters == ["search"]:
                    msg = f"{count} education level(s) deleted based on search filter."
                elif applied_filters == ["educationLevelCode"]:
                    msg = f"{count} education level(s) deleted based on educationLevelCode filter."
                else:
                    msg = f"{count} education level(s) deleted based on search + educationLevelCode filters."

                return Response({
                    "statusCode": 200,
                    "status": True,
                    "message": msg
                }, status=200)

            # ---------------------------------------------------
            # DELETE SPECIFIC UUID LIST
            # ---------------------------------------------------
            if not ids or not isinstance(ids, list):
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Please provide a list of UUIDs in 'id'."
                }, status=400)

            valid_uuids = []
            invalid_uuids = []

            for u in ids:
                try:
                    valid_uuids.append(UUID(u))
                except:
                    invalid_uuids.append(u)

            filtered_objects = queryset.filter(uuid__in=valid_uuids)

            count = filtered_objects.count()
            filtered_objects.delete()

            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"{count} education level(s) deleted.",
                "invalid_uuids": invalid_uuids if invalid_uuids else None
            }, status=200)

        except Exception as e:
            return Response({
                "statusCode": 500,
                "status": False,
                "message": f"Internal server error: {str(e)}"
            }, status=500)




class EducationLevelExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        try:
            # Query Params
            format_type = request.GET.get('format', 'xlsx').lower()
            fields = request.GET.get('fields')
            custom_sort = request.GET.get('customSort')
            search = request.GET.get('search', '').strip()

            # Validate format
            if format_type not in ['xlsx', 'csv']:
                return Response({"status": False, "statusCode": 400, "message": "Invalid format"}, status=400)

            # Field Mapping
            field_header_map = {
                'uuid': 'UUID',
                'level_code': 'Education Level Code',
                'educationlevel': 'Education Level',
                'durations': 'Education Durations',
                'description': 'Description',
                'is_deleted': 'Deleted',
                'created_at': 'Created On',
                'updated_at': 'Modified On',
            }

            # Validate fields
            if fields:
                field_list = [f.strip() for f in fields.split(',')]
                invalid = [f for f in field_list if f not in field_header_map]
                if invalid:
                    return Response({"status": False, "statusCode": 400, "message": f"Invalid fields: {invalid}"}, status=400)
            else:
                field_list = list(field_header_map.keys())

            def parse_ids(param_name):
                raw = request.GET.get(param_name, '')
                if raw:
                    items = [x.strip() for x in raw.split(',') if x.strip()]
                else:
                    items = request.GET.getlist(param_name)
                return items

            def validate_uuid_list(uuid_list):
                valid = []
                for u in uuid_list:
                    try:
                        valid.append(UUID(u))
                    except:
                        pass
                return valid

            educationLevelCode_list = validate_uuid_list(parse_ids('educationLevelCode'))
            uuids_list = validate_uuid_list(parse_ids('uuids'))
            
            # Base Queryset
            queryset = EducationLevel.objects.filter(is_deleted=False)

            if educationLevelCode_list:
                queryset = queryset.filter(level_code__uuid__in=educationLevelCode_list)
            elif uuids_list:
                queryset = queryset.filter(uuid__in=uuids_list)

            if search:
                queryset = queryset.filter(Q(educationlevel__istartswith=search))

            # ✅ FIXED SORTING MAPPING
            sort_field_map = {
                'uuid': 'uuid',
                # 'educationLevelCode': 'level_code__name',  # FK sorting key ✅
                'educationlevelcode': 'level_code__name',  # FK sorting key ✅
                'level_code': 'level_code__name',
                'educationlevel': 'educationlevel',
                'duration': 'durations',   # User sends "duration" but model has "durations" ✅
                'durations': 'durations',
                'updated_at': 'updated_at',
                'created_at': 'created_at',
                'description': 'description',
                'is_deleted': 'is_deleted',
            }

            order_by_rules = []

            if custom_sort:
                for rule in custom_sort.split(','):
                    if ':' not in rule:
                        return Response({"status": False, "statusCode": 400, "message": f"Invalid sort rule: {rule}"}, status=400)

                    field, order = rule.split(':')
                    field = field.strip().lower()
                    print("fieldfieldfield-----",field)
                    order = order.strip().lower()
                    print("orderorderorder----",order)

                    if field not in sort_field_map:
                        return Response({"status": False, "statusCode": 400, "message": f"Invalid sort field: {field}"}, status=400)

                    orm_field = sort_field_map[field]

                    if order == 'desc':
                        order_by_rules.append(f"-{orm_field}")
                    else:
                        order_by_rules.append(orm_field)

            else:
                order_by_rules = ["-created_at"]

            queryset = queryset.order_by(*order_by_rules)  # ✅ FK + all fields sorted properly now

            # Build dataset
            dataset = Dataset()
            dataset.headers = [field_header_map[f] for f in field_list]
            dataset.title = "EducationLevel"

            # Prepare rows
            for obj in queryset:  # already sorted + filtered rows ✅
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

                    row.append(value or '')

                dataset.append(row)

            # Export
            if format_type == 'csv':
                return HttpResponse(
                    dataset.export("csv"),
                    content_type="text/csv",
                    headers={"Content-Disposition": 'attachment; filename="education_levels.csv"'}
                )
            else:
                return HttpResponse(
                    dataset.export("xlsx"),
                    content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={"Content-Disposition": 'attachment; filename="education_levels.xlsx"'}
                )

        except Exception as e:
            return Response({"status": False, "statusCode": 500, "message": "Internal Error", "error": str(e)}, status=500)




# ------------------ Import API ------------------


class EducationLevelImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=400)

        format_type = file.name.split('.')[-1].lower()
        duplicates = []        # country API jaisa
        skipped_rows = []      # country API jaisa

        required_headers = {'education level code', 'education level', 'education durations'}
        optional_headers = {'description', 'is_deleted'}

        try:
            data = []
            headers = []

            # ------------- XLSX -------------
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
                    return Response({"statusCode": 400, "status": False, "message": f'Sheet "{sheet_name}" is empty'}, status=400)

                headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                missing_headers = required_headers - set(headers)
                if missing_headers:
                    return Response({"statusCode": 400, "status": False, "message": f"Missing required headers: {missing_headers}"}, status=400)

                for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    row_dict["_row_number"] = idx
                    data.append(row_dict)

            # ------------- CSV -------------
            elif format_type == 'csv':
                import csv, io
                decoded_file = file.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(decoded_file))
                headers = [h.strip().lower() for h in reader.fieldnames]
                missing_headers = required_headers - set(headers)
                if missing_headers:
                    return Response({"statusCode": 400, "status": False, "message": f"Missing required headers: {missing_headers}"}, status=400)

                for row in reader:
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    row_lower["_row_number"] = imported_count = 0
                    data.append(row_lower)
            else:
                return Response({"statusCode": 400, "status": False, "message": "Unsupported file format. Use .xlsx or .csv"}, status=400)

            imported_count = 0

            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")

                level_code_value = row.get('education level code')
                education_level_name = str(row.get('education level')).strip() if row.get('education level') else None
                durations = row.get('education durations')
                description = str(row.get('description')).strip() if row.get('description') else ''
                is_deleted = bool(int(row.get('is_deleted', 0))) if row.get('is_deleted') not in [None, ''] else False

                # ---- Skip check (exact map Country API jaisa format response) ----
                if not level_code_value or not education_level_name or not durations:
                    skipped_rows.append({
                        "Row": row_number,
                        "Education Level Code": level_code_value,
                        "Education Level Code": level_code_int,
                        "Reason": "Missing education level code, education level, or duration"
                    })
                    continue

                # ---- Numeric validation (country logic jaisa) ----
                if not str(level_code_value).isnumeric():
                    skipped_rows.append({
                        "Row": row_number,
                        "Education Level Code": level_code_value,
                        "Education Level Code": level_code_int,
                        "Reason": "Education level code must be numeric"
                    })
                    continue

                level_code_int = int(level_code_value)

                # ---- Validate FK existence by `name` (exact country-style logic) ----
                level_code_obj = EducationLevelCode.objects.filter(name=level_code_int, is_deleted=False).first()
                if not level_code_obj:
                    skipped_rows.append({
                        "Row": row_number,
                        "Education Level Code": level_code_int,
                        "Reason": "Invalid education level code"
                    })
                    continue

                # ---- Duplicate check (bilkul country API jaisa combination logic) ----
                existing = EducationLevel.objects.filter(
                    level_code=level_code_obj,
                    educationlevel__iexact=education_level_name
                ).first()

                if existing:
                    if not existing.is_deleted:
                        duplicates.append({
                            "Row": row_number,
                            "Education Level": existing.educationlevel,
                            "Education Level Code": level_code_int,
                            "Reason": "Already exists"
                        })
                        continue
                    else:
                        existing.description = description
                        existing.durations = durations
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    try:
                        EducationLevel.objects.create(
                            level_code=level_code_obj,  # ✅ object assignment (id nahi)
                            educationlevel=education_level_name,
                            durations=durations,
                            description=description,
                            is_deleted=False
                        )
                        imported_count += 1
                    except IntegrityError:
                        duplicates.append({
                            "Row": row_number,
                            "Education Level": education_level_name,
                            "Education Level Code": level_code_int,
                            "Reason": "Already exists"
                        })

        except Exception as e:
            return Response({"statusCode": 400, "status": False, "message": str(e)}, status=400)

        # Final response (Country API style exact keys)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": list(reversed(duplicates)),
            "skipped_rows": list(reversed(skipped_rows)),
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
        optional_headers = {'description' }

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
    permission_classes = [IsAuthenticated]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        custom_sort = request.GET.get('customSort')

        queryset = Studymainarea.objects.filter(is_deleted=False)

        # ---------------------------
        # SEARCH FILTER
        # ---------------------------
        if search:
            queryset = queryset.filter(Q(name__istartswith=search))

        # ---------------------------
        # SORT FIELD MAP
        # (only persistent model fields)
        # ---------------------------
        sort_field_map = {
            'uuid': 'uuid',
            'name': 'name',
            'description': 'description',
            'created_at': 'created_at',
            'updated_at': 'updated_at',
        }

        sort_fields = []

        # ---------------------------
        # CUSTOM SORT → multiple rules
        # Example → ?customSort=name:asc,description:desc
        # ---------------------------
        if custom_sort:
            for rule in custom_sort.split(','):
                try:
                    field, order = rule.split(':')
                    field = field.strip()
                    order = order.strip().lower()

                    # if invalid field → skip (not break)
                    if field not in sort_field_map:
                        continue

                    orm_field = sort_field_map[field]

                    # STRING fields → Lower()
                    if field in ['name', 'description']:
                        f = Lower(orm_field)
                    else:
                        f = F(orm_field)

                    sort_fields.append(
                        f.asc(nulls_last=True) if order == 'asc' else f.desc(nulls_last=True)
                    )

                except ValueError:
                    continue

        # ---------------------------
        # DEFAULT SORT → single field fallback
        # ---------------------------
        else:
            sort_by = request.GET.get('sortBy', 'created_at')
            sort_order = request.GET.get('sortOrder', 'desc')

            orm_field = sort_field_map.get(sort_by, 'created_at')

            if sort_by in ['name', 'description']:
                f = Lower(orm_field)
            else:
                f = F(orm_field)

            sort_fields = [
                f.asc(nulls_last=True) if sort_order.lower() == 'asc' else f.desc(nulls_last=True)
            ]

        # ---------------------------
        # APPLY SORTING
        # ---------------------------
        queryset = queryset.order_by(*sort_fields)

        # ---------------------------
        # PAGINATION + RESPONSE
        # ---------------------------
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
# class StudymainareaDeleteAPIView(APIView):
#     permission_classes = [IsAuthenticated, IsAdminUser]

#     def delete(self, request, uuid=None):
#         ids = request.data.get('id', None)

#         if uuid:
#             try:
#                 area = Studymainarea.objects.get(uuid=uuid)
#                 area.delete()
#                 return Response({
#                     "statusCode": 204,
#                     "status": True,
#                     "message": "Study main area permanently deleted.",
#                     "data": None
#                 }, status=status.HTTP_204_NO_CONTENT)
#             except Studymainarea.DoesNotExist:
#                 return Response({
#                     "statusCode": 404,
#                     "status": False,
#                     "message": "Study main area not found.",
#                     "data": None
#                 }, status=status.HTTP_404_NOT_FOUND)

#         if ids == "all":
#             areas = Studymainarea.objects.all()
#             count = areas.count()
#             if count == 0:
#                 return Response({
#                     "statusCode": 404,
#                     "status": False,
#                     "message": "No study main areas found to delete.",
#                     "data": None
#                 }, status=status.HTTP_404_NOT_FOUND)
#             areas.delete()
#             return Response({
#                 "statusCode": 200,
#                 "status": True,
#                 "message": f"All {count} study main area(s) permanently deleted.",
#                 "data": None
#             }, status=status.HTTP_200_OK)

#         if not ids or not isinstance(ids, list):
#             return Response({
#                 "statusCode": 400,
#                 "status": False,
#                 "message": "Please provide a list of UUIDs in 'id' field or 'all'.",
#                 "data": None
#             }, status=status.HTTP_400_BAD_REQUEST)

#         valid_uuids = []
#         invalid_uuids = []
#         for u in ids:
#             try:
#                 valid_uuids.append(UUID(u))
#             except ValueError:
#                 invalid_uuids.append(u)

#         if not valid_uuids:
#             return Response({
#                 "statusCode": 400,
#                 "status": False,
#                 "message": "No valid UUIDs provided.",
#                 "data": {"invalid_uuids": invalid_uuids}
#             }, status=status.HTTP_400_BAD_REQUEST)

#         areas = Studymainarea.objects.filter(uuid__in=valid_uuids)
#         count = areas.count()
#         if count == 0:
#             return Response({
#                 "statusCode": 404,
#                 "status": False,
#                 "message": "No matching study main areas found.",
#                 "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
#             }, status=status.HTTP_404_NOT_FOUND)

#         areas.delete()
#         return Response({
#             "statusCode": 200,
#             "status": True,
#             "message": f"{count} study main area(s) permanently deleted.",
#             "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
#         }, status=status.HTTP_200_OK)



class StudymainareaDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        try:
            search = request.GET.get("search", "").strip()
            delete_all = request.data.get("deleteAll", False)
            ids = request.data.get("id", None)

            # ----------------------------------
            # If id == "all" → DELETE entire table
            # ----------------------------------
            if ids == "all":
                count = Studymainarea.objects.count()
                Studymainarea.objects.all().delete()
                return Response({
                    "statusCode": 200,
                    "status": True,
                    "message": f"All {count} study main area(s) deleted from the table.",
                }, status=200)

            # ----------------------------------
            # Base queryset
            # ----------------------------------
            queryset = Studymainarea.objects.all()

            # -----------------------------
            # Search filter
            # -----------------------------
            if search:
                queryset = queryset.filter(name__istartswith=search)

            # -----------------------------
            # deleteAll with search logic
            # -----------------------------
            if delete_all:
                count = queryset.count()
                queryset.delete()

                if search:
                    msg = f"{count} study main area(s) deleted based on search filter."
                else:
                    msg = f"All {count} study main area(s) deleted from the table."

                return Response({
                    "statusCode": 200,
                    "status": True,
                    "message": msg
                }, status=200)

            # -----------------------------
            # Specific UUID deletion
            # -----------------------------
            if not ids or not isinstance(ids, list):
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Please provide a list of UUIDs in 'id' field, or send 'all' to delete everything."
                }, status=400)

            valid_uuids = []
            invalid_uuids = []

            for u in ids:
                try:
                    valid_uuids.append(UUID(u))
                except:
                    invalid_uuids.append(u)

            filtered_objects = queryset.filter(uuid__in=valid_uuids)
            count = filtered_objects.count()
            filtered_objects.delete()

            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"{count} study main area(s) deleted.",
                "invalid_uuids": invalid_uuids if invalid_uuids else None
            }, status=200)

        except Exception as e:
            return Response({
                "statusCode": 500,
                "status": False,
                "message": f"Internal server error: {str(e)}"
            }, status=500)


# -------------------- EXPORT API --------------------

class StudymainareaExportAPIView(APIView):
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
            # Field Mapping
            # ---------------------------
            field_header_map = {
                'uuid': 'UUID',
                'name': 'Study Main Area',
                'description': 'Description',
                'is_deleted': 'Deleted',
                'created_at': 'Created On',
                'updated_at': 'Modified On',
            }

            # Validate / prepare field list
            if fields:
                field_list = [f.strip() for f in fields.split(',')]
                invalid = [f for f in field_list if f not in field_header_map]
                if invalid:
                    return Response({
                        "status": False,
                        "statusCode": 400,
                        "message": f"Invalid fields: {invalid}",
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
            # Base Queryset
            # ---------------------------
            queryset = Studymainarea.objects.filter(is_deleted=False)

            if uuids:
                queryset = queryset.filter(uuid__in=uuids).distinct()

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
                                "message": f"Invalid sort order: {order}",
                            }, status=400)

                        # For description only → case-insensitive
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
                # default sorting
                f = F('created_at')
                sort_order = request.GET.get('sortOrder', 'desc')
                sort_fields = [
                    f.desc(nulls_last=True) if sort_order == 'desc'
                    else f.asc(nulls_last=True)
                ]

            queryset = queryset.order_by(*sort_fields)

            # ---------------------------
            # Prepare Dataset
            # ---------------------------
            dataset = Dataset()
            dataset.headers = [field_header_map[f] for f in field_list]
            dataset.title = 'StudyMainArea'

            for area in queryset:
                row = []
                for field in field_list:
                    value = getattr(area, field, '')

                    if field in ['created_at', 'updated_at'] and value:
                        value = timezone.localtime(value).strftime("%d-%m-%Y %I:%M:%S %p")
                    elif isinstance(value, bool):
                        value = int(value)

                    row.append(value or "")

                dataset.append(row)

            # ---------------------------
            # File Export
            # ---------------------------
            if format_type == 'csv':
                file_data = dataset.export('csv')
                content_type = 'text/csv'
                file_name = 'studymainareas.csv'
                response_content = file_data
            else:
                file_buffer = io.BytesIO(dataset.export('xlsx'))
                content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                file_name = 'studymainareas.xlsx'
                response_content = file_buffer.getvalue()

            response = HttpResponse(response_content, content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'
            return response

        except Exception as e:
            return Response({
                "status": False,
                "statusCode": 500,
                "message": "Internal server error",
                "error": str(e)
            }, status=500)


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
                    skipped_rows.append({
                        "Row": row_number,
                        "Study Main Area": name or "",
                        "Reason": "Missing study main area"
                        })
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
            "duplicates": list(reversed(duplicates)),
            "skipped_rows": list(reversed(skipped_rows)),
        }, status=200)



# -------------------- Studymajor -------------------- #


class StudyMajorAreaListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        custom_sort = request.GET.get('customSort')
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')
        uuid_param = request.GET.get('studyMainArea', '')

        # Allowed sortable fields
        allowed_sort_fields = [
            'majorarea', 'description', 'created_at', 'updated_at', "mainarea_name"
        ]

        queryset = Studymajorarea.objects.filter(is_deleted=False)

        # --------------------------------------------------
        # UUID Filtering
        # --------------------------------------------------
        uuid_list = []
        if uuid_param:
            for u in uuid_param.split(','):
                try:
                    uuid_list.append(UUID(u.strip()))
                except:
                    pass

        if uuid_list:
            queryset = queryset.filter(mainarea__uuid__in=uuid_list)

        # --------------------------------------------------
        # Search Filter
        # --------------------------------------------------
        if search:
            queryset = queryset.filter(majorarea__icontains=search)

        # --------------------------------------------------
        # Sort field mapping
        # --------------------------------------------------
        sort_field_map = {
            'uuid': 'uuid',
            'studyMainArea': 'mainarea__name',
            'majorarea': 'majorarea',
            'description': 'description',
            'created_at': 'created_at',
            'updated_at': 'updated_at',
        }

        sort_fields = []

        # --------------------------------------------------
        # CUSTOM SORT (same as Country API)
        # --------------------------------------------------
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
                    if field in ["majorarea", "studyMainArea", "description"]:
                        f = Lower(orm_field)
                    else:
                        f = F(orm_field)

                    sort_fields.append(
                        f.asc(nulls_last=True) if order == "asc" else f.desc(nulls_last=True)
                    )
                except ValueError:
                    continue

        else:
            # --------------------------------------------------
            # DEFAULT SORT
            # --------------------------------------------------
            if sort_by not in allowed_sort_fields:
                sort_by = "created_at"

            orm_field = sort_field_map.get(sort_by, "created_at")
            f = F(orm_field)

            sort_fields = [
                f.asc(nulls_last=True) if sort_order == "asc" else f.desc(nulls_last=True)
            ]

        # --------------------------------------------------
        # Apply sorting
        # --------------------------------------------------
        queryset = queryset.order_by(*sort_fields)

        # --------------------------------------------------
        # Pagination
        # --------------------------------------------------
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
# class StudyMajorAreaDeleteAPIView(APIView):
#     permission_classes = [IsAuthenticated, IsAdminUser]

#     def delete(self, request, uuid=None):
#         ids = request.data.get('id', None)

#         # Single delete via URL
#         if uuid:
#             try:
#                 obj = Studymajorarea.objects.get(uuid=uuid)
#                 obj.delete()
#                 return Response({
#                     "statusCode": 204,
#                     "status": True,
#                     "message": "Study Major Area permanently deleted.",
#                     "data": None
#                 }, status=status.HTTP_204_NO_CONTENT)
#             except Studymajorarea.DoesNotExist:
#                 return Response({
#                     "statusCode": 404,
#                     "status": False,
#                     "message": "Study Major Area not found.",
#                     "data": None
#                 }, status=status.HTTP_404_NOT_FOUND)

#         # Delete all
#         if ids == "all":
#             queryset = Studymajorarea.objects.all()
#             count = queryset.count()
#             queryset.delete()
#             return Response({
#                 "statusCode": 200,
#                 "status": True,
#                 "message": f"All {count} study major areas permanently deleted.",
#                 "data": None
#             }, status=status.HTTP_200_OK)

#         # Bulk delete
#         if not ids or not isinstance(ids, list):
#             return Response({
#                 "statusCode": 400,
#                 "status": False,
#                 "message": "Please provide a list of UUIDs in 'id' field or 'all'.",
#                 "data": None
#             }, status=status.HTTP_400_BAD_REQUEST)

#         valid_uuids = []
#         invalid_uuids = []
#         for u in ids:
#             try:
#                 valid_uuids.append(UUID(u))
#             except ValueError:
#                 invalid_uuids.append(u)

#         queryset = Studymajorarea.objects.filter(uuid__in=valid_uuids)
#         count = queryset.count()
#         queryset.delete()

#         return Response({
#             "statusCode": 200,
#             "status": True,
#             "message": f"{count} study major area(s) permanently deleted.",
#             "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
#         }, status=status.HTTP_200_OK)

class StudyMajorAreaDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get('id', None)

        # ---------------------------------------
        # Parse filters
        # ---------------------------------------
        search = request.GET.get("search", "").strip()

        def parse_uuid_list(param):
            raw = request.GET.get(param, "")
            final = []
            if raw:
                for x in raw.split(","):
                    try:
                        final.append(UUID(x.strip()))
                    except:
                        pass
            return final

        study_main_area_uuids = parse_uuid_list("studyMainArea")

        # ---------------------------------------
        # DELETE FULL TABLE when id == "all"
        # ---------------------------------------
        if ids == "all":
            count = Studymajorarea.objects.count()
            Studymajorarea.objects.all().delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} study major area(s) deleted from the table.",
                "data": None
            }, status=200)

        # ---------------------------------------
        # Base queryset for filtered delete
        # ---------------------------------------
        queryset = Studymajorarea.objects.all()
        applied_filters = []

        # SEARCH filter
        if search:
            queryset = queryset.filter(name__istartswith=search)
            applied_filters.append("search")

        # studyMainArea FK filter
        if study_main_area_uuids:
            queryset = queryset.filter(study_main_area__uuid__in=study_main_area_uuids)
            applied_filters.append("studyMainArea")

        # ---------------------------------------
        # DELETE ALL MATCHING FILTERED RESULTS
        # ---------------------------------------
        if request.data.get("deleteAll", False):
            count = queryset.count()
            queryset.delete()

            if applied_filters == ["search"]:
                msg = f"{count} study major area(s) deleted based on search filter."
            elif applied_filters == ["studyMainArea"]:
                msg = f"{count} study major area(s) deleted based on studyMainArea filter."
            elif applied_filters:
                msg = f"{count} study major area(s) deleted based on search + studyMainArea filters."
            else:
                msg = f"All {count} study major area(s) deleted from the table."

            return Response({
                "statusCode": 200,
                "status": True,
                "message": msg,
                "data": None
            }, status=200)

        # ---------------------------------------
        # BULK DELETE via UUID LIST
        # ---------------------------------------
        if not ids or not isinstance(ids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please send UUID list in 'id' or 'all'.",
                "data": None
            }, status=400)

        valid_uuids = []
        invalid_uuids = []
        for u in ids:
            try:
                valid_uuids.append(UUID(u))
            except:
                invalid_uuids.append(u)

        bulk_qs = queryset.filter(uuid__in=valid_uuids)
        count = bulk_qs.count()
        bulk_qs.delete()

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} study major area(s) deleted.",
            "data": {
                "invalid_uuids": invalid_uuids
            } if invalid_uuids else None
        }, status=200)
    

# ------------------ Export API ------------------

class StudyMajorAreaExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        try:
            # ---------------------------
            # Query Params
            # ---------------------------
            format_type = request.GET.get('format', 'xlsx').lower()
            search = request.GET.get('search', '').strip()
            fields = request.GET.get('fields')
            custom_sort = request.GET.get('customSort')

            # Validate format
            if format_type not in ['xlsx', 'csv']:
                return Response({
                    "status": False,
                    "statusCode": 400,
                    "message": "Invalid format. Allowed: xlsx, csv"
                }, status=400)

            # ---------------------------
            # Field Mapping
            # ---------------------------
            field_header_map = {
                'uuid': 'UUID',
                'mainarea': 'Study Main Area',
                'majorarea': 'Study Major Area',
                'description': 'Description',
                'is_deleted': 'Deleted',
                'created_at': 'Created On',
                'updated_at': 'Modified On',
            }

            # Field selection
            if fields:
                field_list = [f.strip() for f in fields.split(',')]
                invalid = [f for f in field_list if f not in field_header_map]
                if invalid:
                    return Response({
                        "status": False,
                        "statusCode": 400,
                        "message": f"Invalid fields: {invalid}",
                    }, status=400)
            else:
                field_list = list(field_header_map.keys())

            # ---------------------------
            # Helper: Parse & Validate UUIDs
            # ---------------------------
            def parse_ids(param_name):
                raw = request.GET.get(param_name, '')
                if raw:
                    items = [x.strip() for x in raw.split(',') if x.strip()]
                else:
                    items = request.GET.getlist(param_name)
                return items

            def validate_uuid_list(uuid_list):
                valid = []
                for u in uuid_list:
                    try:
                        valid.append(UUID(u))
                    except:
                        pass
                return valid

            try:
                studyMainArea_list = validate_uuid_list(parse_ids('studyMainArea'))
                uuids_list = validate_uuid_list(parse_ids('uuids'))
            except ValueError as e:
                return Response({
                    "status": False,
                    "statusCode": 400,
                    "message": str(e)
                }, status=400)

            # ---------------------------
            # Base Queryset
            # ---------------------------
            queryset = Studymajorarea.objects.filter(is_deleted=False)
            
            try:
                if studyMainArea_list:
                    print("Filtering by studyMainArea_list")
                    queryset = queryset.filter(mainarea__uuid__in=studyMainArea_list)
                    print(f"Post-filter  studyMainArea_list count: {queryset.count()}")
                elif uuids_list:
                    print("Filtering by uuids_list")
                    queryset = queryset.filter(uuid__in=uuids_list)
                    print(f"Post-filter uuids_list count: {queryset.count()}")
            except Exception as e:
                return Response({
                    "status": False,
                    "statusCode": 400,
                    "message": f"Error during UUID filtering: {str(e)}"
                }, status=400)

            # ---------------------------
            # Search Logic (icontains + istartswith)
            # ---------------------------
            if search:
                queryset = queryset.filter(
                    Q(majorarea__istartswith=search) |
                    Q(majorarea__icontains=search)
                )

            # ---------------------------
            # Sorting Logic (CustomSort)
            # ---------------------------
            # ---------------------------
            # Sorting Logic (CustomSort)
            # ---------------------------
            sort_field_map = {
                'uuid': 'uuid',
                'studyMainArea': 'mainarea__name',
                'majorarea': 'majorarea',
                'description': 'description',
                'created_at': 'created_at',
                'updated_at': 'updated_at',
            }

            sort_fields = []
            annotations = {}

            if custom_sort:
                for idx, rule in enumerate(custom_sort.split(',')):
                    try:
                        field, order = rule.split(':')
                        field = field.strip()
                        order = order.strip().lower()

                        if field not in sort_field_map:
                            return Response({
                                "status": False,
                                "statusCode": 400,
                                "message": f"Invalid sort field: {field}"
                            }, status=400)

                        orm_field = sort_field_map[field]

                        # Case-insensitive sorting for string fields
                        if field in ['studyMainArea', 'majorarea', 'description']:
                            ann_name = f"sort_key_{idx}"
                            annotations[ann_name] = Lower(orm_field)
                            sort_fields.append(ann_name if order == 'asc' else f"-{ann_name}")
                        else:
                            sort_fields.append(
                                orm_field if order == 'asc' else f"-{orm_field}"
                            )

                    except ValueError:
                        return Response({
                            "status": False,
                            "statusCode": 400,
                            "message": f"Invalid sorting rule format: {rule}"
                        }, status=400)

            # Apply annotation
            if annotations:
                queryset = queryset.annotate(**annotations)

            # Default sort if none provided
            if not sort_fields:
                sort_fields = ['-created_at']

            queryset = queryset.order_by(*sort_fields)


            # ---------------------------
            # Prepare Dataset
            # ---------------------------
            dataset = Dataset()
            dataset.headers = [field_header_map[f] for f in field_list]
            dataset.title = 'StudyMajorArea'

            for obj in queryset:
                row = []
                for field in field_list:
                    if field == 'mainarea':
                        value = obj.mainarea.name if obj.mainarea else ''
                    else:
                        value = getattr(obj, field, '')

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
                file_name = 'study_major_areas.csv'
                response_content = file_data
            else:
                file_buffer = io.BytesIO(dataset.export('xlsx'))
                content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                file_name = 'study_major_areas.xlsx'
                response_content = file_buffer.getvalue()

            response = HttpResponse(response_content, content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'
            return response

        except Exception as e:
            return Response({
                "status": False,
                "statusCode": 500,
                "message": "Internal server error",
                "error": str(e)
            }, status=500)



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
            "duplicates": list(reversed(duplicates)),
            "skipped_rows": list(reversed(skipped_rows)),
        }, status=200)

# -------------------- Studyspecialisation -------------------- #


class StudySpecialisationListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        custom_sort = request.GET.get('customSort')
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        uuid_studyMainArea = request.GET.get('studyMainArea', '')
        uuid_studyMajorArea = request.GET.get('studyMajorArea', '')

        queryset = StudySpecialisation.objects.filter(is_deleted=False)

        # ----------------------------------------
        # UUID FILTERING HELPERS
        # ----------------------------------------
        def parse_uuid_list(raw):
            valid = []
            if raw:
                for x in raw.split(','):
                    try:
                        valid.append(UUID(x.strip()))
                    except:
                        pass
            return valid

        # Filter by mainarea
        mainarea_list = parse_uuid_list(uuid_studyMainArea)
        if mainarea_list:
            queryset = queryset.filter(mainarea__uuid__in=mainarea_list)

        # Filter by majorarea
        majorarea_list = parse_uuid_list(uuid_studyMajorArea)
        if majorarea_list:
            queryset = queryset.filter(majorarea__uuid__in=majorarea_list)

        # ----------------------------------------
        # SEARCH FILTER
        # ----------------------------------------
        if search:
            queryset = queryset.filter(studyspecialisation__istartswith=search)

        # ----------------------------------------
        # SORT FIELD MAP
        # ----------------------------------------
        sort_field_map = {
            "studyspecialisation": "studyspecialisation",
            "description": "description",
            "studyMainArea": "mainarea__name",
            "studyMajorArea": "majorarea__majorarea",
            "created_at": "created_at",
            "updated_at": "updated_at",
        }

        # Allowed fields
        allowed_sort_fields = list(sort_field_map.keys())

        sort_fields = []

        # ----------------------------------------
        # CUSTOM SORT LOGIC
        # ----------------------------------------
        if custom_sort:
            for rule in custom_sort.split(","):
                try:
                    field, order = rule.split(":")
                    field = field.strip()
                    order = order.strip().lower()

                    if field not in sort_field_map:
                        continue

                    orm_field = sort_field_map[field]

                    # Case-insensitive fields
                    if field in [
                        "studyspecialisation", "description",
                        "studyMainArea", "studyMajorArea"
                    ]:
                        f = Lower(orm_field)
                    else:
                        f = F(orm_field)

                    sort_fields.append(
                        f.asc(nulls_last=True)
                        if order == "asc" else f.desc(nulls_last=True)
                    )

                except ValueError:
                    continue

        else:
            # ----------------------------------------
            # DEFAULT SORT
            # ----------------------------------------
            if sort_by not in allowed_sort_fields:
                sort_by = "created_at"

            orm_field = sort_field_map.get(sort_by, "created_at")
            f = F(orm_field)

            sort_fields = [
                f.asc(nulls_last=True) if sort_order == "asc" else f.desc(nulls_last=True)
            ]

        queryset = queryset.order_by(*sort_fields)

        # ----------------------------------------
        # PAGINATION
        # ----------------------------------------
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

        # ----------------------------
        # Search and Sorting
        # ----------------------------
        search = request.GET.get('search', '').strip()
        custom_sort = request.GET.get('customSort')

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


        # ---------------------------
        # Helper: Parse & Validate UUIDs
        # ---------------------------
        def parse_ids(param_name):
            raw = request.GET.get(param_name, '')
            if raw:
                items = [x.strip() for x in raw.split(',') if x.strip()]
            else:
                items = request.GET.getlist(param_name)
            return items

        def validate_uuid_list(uuid_list):
            valid = []
            for u in uuid_list:
                try:
                    valid.append(UUID(u))
                except:
                    pass
            return valid

        try:
            studyMajorArea_list = validate_uuid_list(parse_ids('studyMajorArea'))
            studyMainArea_list = validate_uuid_list(parse_ids('studyMainArea'))
            uuids_list = validate_uuid_list(parse_ids('uuids'))
        except ValueError as e:
            return Response({
                "status": False,
                "statusCode": 400,
                "message": str(e)
            }, status=400)
        
        # ----------------------------
        # Base QuerySet
        # ----------------------------
        queryset = StudySpecialisation.objects.filter(is_deleted=False)

        # ----------------------------
        # Apply Filters Only If Given
        # ----------------------------
        if uuids_list:
            queryset = queryset.filter(uuid__in=uuids_list)

        if studyMainArea_list:
            queryset = queryset.filter(mainarea__uuid__in=studyMainArea_list)

        if studyMajorArea_list:
            queryset = queryset.filter(majorarea__uuid__in=studyMajorArea_list)

        # ----------------------------
        # Apply Search
        # ----------------------------
        if search:
            queryset = queryset.filter(
                Q(studyspecialisation__icontains=search)
            )

        # ---------------------------
        # Sorting Logic (CustomSort)
        # ---------------------------
        sort_field_map = {
            'uuid': 'uuid',
            'studyMainArea': 'mainarea__name',
            'studyMajorArea': 'majorarea__majorarea',
            'studyspecialisation': 'studyspecialisation',
            'description': 'description',
            'created_at': 'created_at',
            'updated_at': 'updated_at',
        }

        sort_fields = []
        annotations = {}

        if custom_sort:
            for idx, rule in enumerate(custom_sort.split(',')):
                try:
                    field, order = rule.split(':')
                    field = field.strip()
                    order = order.strip().lower()

                    if field not in sort_field_map:
                        return Response({
                            "status": False,
                            "statusCode": 400,
                            "message": f"Invalid sort field: {field}"
                        }, status=400)

                    orm_field = sort_field_map[field]

                    # Case-insensitive sorting for string fields
                    if field in ['studyMainArea', 'studyMajorArea', 'studyspecialisation', 'description']:
                        ann_name = f"sort_key_{idx}"
                        annotations[ann_name] = Lower(orm_field)
                        sort_fields.append(
                            ann_name if order == 'asc' else f"-{ann_name}"
                        )
                    else:
                        sort_fields.append(
                            orm_field if order == 'asc' else f"-{orm_field}"
                        )

                except ValueError:
                    return Response({
                        "status": False,
                        "statusCode": 400,
                        "message": f"Invalid sorting rule format: {rule}"
                    }, status=400)

        # Apply annotations
        if annotations:
            queryset = queryset.annotate(**annotations)

        # Default sort
        if not sort_fields:
            sort_fields = ['-created_at']

        queryset = queryset.order_by(*sort_fields)


        # ----------------------------
        # Prepare Dataset
        # ----------------------------
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
                        value = timezone.localtime(value).strftime("%d-%m-%Y %I:%M:%S %p")

                elif isinstance(value, bool):
                    value = int(value)

                row.append(value if value is not None else '')

            dataset.append(row)

        # ----------------------------
        # Export File
        # ----------------------------
        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'study_specialisations.csv'

            response = HttpResponse(file_data, content_type=content_type)

        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'study_specialisations.xlsx'

            response = HttpResponse(file_data.getvalue(), content_type=content_type)

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
                    skipped_rows.append({
                        "Row": row_number,
                        "Study Specialisation": specialisation_name or "",
                        "Study Major Area": majorarea_name or "",
                        "Study Main Area": mainarea_name or "",
                        "Description": description or "",
                        "Reason": "Missing required field(s)"
                    })
                    continue

                # Validate mainarea
                mainarea_obj = Studymainarea.objects.filter(name__iexact=mainarea_name, is_deleted=False).first()
                if not mainarea_obj:
                    skipped_rows.append({
                        "Row": row_number,
                        "Study Specialisation": specialisation_name or "",
                        "Study Major Area": majorarea_name or "",
                        "Study Main Area": mainarea_name or "",
                        "Description": description or "",
                        "Reason": "Invalid study main area"
                    })
                    continue

                # Validate majorarea belongs to mainarea
                majorarea_obj = Studymajorarea.objects.filter(majorarea__iexact=majorarea_name, mainarea=mainarea_obj, is_deleted=False).first()
                if not majorarea_obj:
                    skipped_rows.append({
                        "Row": row_number,
                        "Study Specialisation": specialisation_name or "",
                        "Study Major Area": majorarea_name or "",
                        "Study Main Area": mainarea_name or "",
                        "Description": description or "",
                        "Reason": "Invalid or mismatched study major area"
                    })
                    continue

                # Existing check
                existing = StudySpecialisation.objects.filter(
                    studyspecialisation__iexact=specialisation_name,
                    majorarea=majorarea_obj
                ).first()

                if existing:
                    if not existing.is_deleted:
                        duplicates.append({
                        "Row": row_number,
                        "Study Specialisation": specialisation_name or "",
                        "Study Main Area": mainarea_name or "",
                        "Study Major Area": majorarea_name or "",
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
            "duplicates": list(reversed(duplicates)),
            "skipped_rows": list(reversed(skipped_rows)),
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
        try:
            search = request.GET.get('search', '').strip()
            custom_sort = request.GET.get('customSort')   # name:asc,description:desc

            allowed_sort_fields = [
                "name", "description", "datatype",
                "created_at", "updated_at", "uuid"
            ]

            queryset = AcademicResultType.objects.filter(is_deleted=False)

            # ---------------------------------------------------
            # Search
            # ---------------------------------------------------
            if search:
                queryset = queryset.filter(
                    Q(name__istartswith=search)
                )

            # ---------------------------------------------------
            # customSort logic (multi-column sorting)
            # ---------------------------------------------------
            sort_fields = []

            if custom_sort:
                for rule in custom_sort.split(','):
                    try:
                        field, order = rule.split(':')
                        field = field.strip()
                        order = order.strip().lower()

                        if field not in allowed_sort_fields:
                            continue

                        # Case-insensitive string sorting
                        if field in ["name", "description", "datatype"]:
                            f = Lower(field)
                        else:
                            f = F(field)

                        sort_fields.append(
                            f.asc(nulls_last=True) if order == "asc" else f.desc(nulls_last=True)
                        )
                    except ValueError:
                        continue
            else:
                # Fallback Sorting
                sort_by = request.GET.get("sortBy", "created_at")
                sort_order = request.GET.get("sortOrder", "desc")

                if sort_by not in allowed_sort_fields:
                    sort_by = "created_at"

                f = F(sort_by)
                sort_fields = [
                    f.asc(nulls_last=True) if sort_order == "asc" else f.desc(nulls_last=True)
                ]

            queryset = queryset.order_by(*sort_fields)

            # ---------------------------------------------------
            # Pagination
            # ---------------------------------------------------
            paginator = CustomPagination()
            result_page = paginator.paginate_queryset(queryset, request)
            serializer = AcademicResultTypeSerializer(result_page, many=True)
            return paginator.get_paginated_response(serializer.data)

        # -------------------------------------------------------
        # Exception Handling
        # -------------------------------------------------------
        except ValidationError as e:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Invalid data provided",
                "detail": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        except IntegrityError:
            return Response({
                "statusCode": 500,
                "status": False,
                "message": "Database integrity error occurred."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except DatabaseError:
            return Response({
                "statusCode": 500,
                "status": False,
                "message": "Database error occurred."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({
                "statusCode": 500,
                "status": False,
                "message": "Something went wrong.",
                "detail": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# --------------------- Create API ---------------------


class AcademicResultTypeCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        try:
            name = request.data.get("name", "").strip()

            # ----------- Duplicate Check -----------
            if AcademicResultType.objects.filter(name__iexact=name, is_deleted=False).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Academic Result Type with this name already exists."
                }, status=status.HTTP_400_BAD_REQUEST)

            # ----------- Serializer Validation ----------
            serializer = AcademicResultTypeSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            # ----------- Save Safe Block -----------
            serializer.save()

            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Academic Result Type created successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        except ValidationError as e:
            # Serializer validation errors
            return Response({
                "statusCode": 400,
                "status": False,
                "message": e.detail if isinstance(e.detail, str) else " ".join([str(val[0]) for val in e.detail.values()])
            }, status=status.HTTP_400_BAD_REQUEST)

        except IntegrityError:
            # Database constraint errors
            return Response({
                "statusCode": 500,
                "status": False,
                "message": "Database integrity error occurred."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except DatabaseError:
            # General DB error fallback
            return Response({
                "statusCode": 500,
                "status": False,
                "message": "A database error occurred. Please try again."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            # Fallback for unexpected errors
            return Response({
                "statusCode": 500,
                "status": False,
                "message": f"Something went wrong: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
# class AcademicResultTypeExportAPIView(APIView):
#     permission_classes = [IsAuthenticated, IsAdminUser]
 
#     def get(self, request):
#         format_type = request.GET.get('format', 'xlsx').lower()
#         fields = request.GET.get('fields')
#         uuids_param = request.GET.get('uuids', '')
#         uuids = [u.strip() for u in uuids_param.split(',') if u]
 
#         field_header_map = {
#             'uuid': 'UUID',
#             'name': 'Academic Result Type',
#             'description': 'Description',
#             'is_deleted': 'Deleted',
#             'datatype':'Data Type',
#             'updated_at': 'Modified On',
#             'created_at': 'Created On',
#         }
 
#         # field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())
        
#         field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())

#         # force mapping data_type → datatype
#         field_list = [
#             'datatype' if f.lower().replace('-', '_') in ['data_type', 'datatype', 'data type'] else f
#             for f in field_list
#         ]

 
#         queryset = AcademicResultType.objects.filter(is_deleted=False)
#         if uuids:
#             queryset = queryset.filter(uuid__in=uuids)
#         queryset = queryset.order_by('-created_at')
 
#         dataset = Dataset()
#         dataset.headers = [field_header_map.get(f, f) for f in field_list]
#         dataset.title = 'AcademicResultType'
 
#         for obj in queryset:
#             row = []
#             for field in field_list:
#                 value = getattr(obj, field, '')
#                 if field in ['created_at', 'updated_at'] and value:
#                     value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
#                 elif isinstance(value, bool):
#                     value = int(value)
#                 row.append(value if value is not None else '')
#             dataset.append(row)
 
#         if format_type == 'csv':
#             file_data = dataset.export('csv')
#             content_type = 'text/csv'
#             file_name = 'academic_result_types.csv'
#         else:
#             file_data = io.BytesIO(dataset.export('xlsx'))
#             content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
#             file_name = 'academic_result_types.xlsx'
 
#         response = HttpResponse(
#             file_data if format_type == 'csv' else file_data.getvalue(),
#             content_type=content_type
#         )
#         response['Content-Disposition'] = f'attachment; filename="{file_name}"'
#         return response
 

class AcademicResultTypeExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        search = request.GET.get('search', '').strip()
        custom_sort = request.GET.get('customSort')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'name': 'Academic Result Type',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'datatype': 'Data Type',
            'updated_at': 'Modified On',
            'created_at': 'Created On',
        }

        # Field list
        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())

        # Normalize datatype alias
        field_list = [
            'datatype' if f.lower().replace('-', '_') in ['data_type', 'datatype', 'data type'] else f
            for f in field_list
        ]

        # Base queryset
        queryset = AcademicResultType.objects.filter(is_deleted=False)

        if uuids:
            queryset = queryset.filter(uuid__in=uuids)

        if search:
            queryset = queryset.filter(
                Q(name__istartswith=search) |
                Q(name__icontains=search)
            )

        # ---------------------------
        # Custom Sorting
        # ---------------------------
        sort_field_map = {
            'uuid': 'uuid',
            'name': 'name',
            'description': 'description',
            'dataType': 'datatype',
            'created_at': 'created_at',
            'updated_at': 'updated_at',
        }

        sort_fields = []
        annotations = {}

        if custom_sort:
            for idx, rule in enumerate(custom_sort.split(',')):
                try:
                    field, order = rule.split(':')
                    field = field.strip()
                    order = order.strip().lower()

                    if field not in sort_field_map:
                        return Response({
                            "status": False,
                            "statusCode": 400,
                            "message": f"Invalid sort field: {field}"
                        }, status=400)

                    orm_field = sort_field_map[field]

                    # Case-insensitive sorting for strings
                    if field in ['name', 'description', 'datatype']:
                        ann_name = f"sort_key_{idx}"
                        annotations[ann_name] = Lower(orm_field)
                        sort_fields.append(ann_name if order == 'asc' else f"-{ann_name}")
                    else:
                        sort_fields.append(orm_field if order == 'asc' else f"-{orm_field}")

                except ValueError:
                    return Response({
                        "status": False,
                        "statusCode": 400,
                        "message": f"Invalid sorting rule format: {rule}"
                    }, status=400)

        # Apply annotation if needed
        if annotations:
            queryset = queryset.annotate(**annotations)

        # Default sort
        if not sort_fields:
            sort_fields = ['-created_at']

        queryset = queryset.order_by(*sort_fields)

        # ---------------------------
        # Prepare Dataset
        # ---------------------------
        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'AcademicResultType'

        for obj in queryset:
            row = []
            for field in field_list:
                value = getattr(obj, field, '')

                if field in ['created_at', 'updated_at'] and value:
                    value = timezone.localtime(value).strftime("%d-%m-%Y %I:%M:%S %p")
                elif isinstance(value, bool):
                    value = int(value)

                row.append(value if value is not None else '')

            dataset.append(row)

        # ---------------------------
        # Export File
        # ---------------------------
        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'academic_result_types.csv'
            file_output = file_data
        else:
            file_buffer = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'academic_result_types.xlsx'
            file_output = file_buffer.getvalue()

        response = HttpResponse(file_output, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response

 
# --------------------- Import API ---------------------
# class AcademicResultTypeImportAPIView(APIView):
#     permission_classes = [IsAuthenticated, IsAdminUser]

#     def post(self, request):
#         file = request.FILES.get('file')
#         sheet_name = request.data.get('sheet_name')

#         if not file:
#             return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

#         format_type = file.name.split('.')[-1].lower()
#         duplicate_names = []

#         required_headers = {'name', 'datatype'}  # datatype is required now
#         optional_headers = {'description'}

#         try:
#             data = []

#             if format_type == 'xlsx':
#                 import openpyxl
#                 wb = openpyxl.load_workbook(file, read_only=True)
#                 available_sheets = wb.sheetnames

#                 if not sheet_name:
#                     return Response({
#                         'error': 'Please provide sheet_name',
#                         'available_sheets': available_sheets
#                     }, status=status.HTTP_400_BAD_REQUEST)

#                 if sheet_name not in available_sheets:
#                     return Response({
#                         'error': f'Sheet "{sheet_name}" not found',
#                         'available_sheets': available_sheets
#                     }, status=status.HTTP_400_BAD_REQUEST)

#                 ws = wb[sheet_name]
#                 if ws.max_row <= 1:
#                     return Response({
#                         "statusCode": 400,
#                         "status": False,
#                         "message": f'The uploaded XLSX file is empty.'
#                     }, status=status.HTTP_400_BAD_REQUEST)

#                 headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]
#                 if not required_headers.issubset(set(headers)):
#                     return Response({
#                         "statusCode": 400,
#                         "status": True,
#                         'message': f'Missing required headers. Required: {required_headers}, Found: {set(headers)}'
#                     }, status=status.HTTP_400_BAD_REQUEST)

#                 for row in ws.iter_rows(min_row=2, values_only=True):
#                     if not any(row):
#                         continue
#                     row_dict = dict(zip(headers, row))
#                     data.append(row_dict)

#             elif format_type == 'csv':
#                 import csv
#                 decoded_file = file.read().decode('utf-8').splitlines()
#                 reader = csv.DictReader(decoded_file)
#                 for row in reader:
#                     row_lower = {k.strip().lower(): v for k, v in row.items()}
#                     if not required_headers.issubset(set(row_lower.keys())):
#                         return Response({
#                             "statusCode": 400,
#                             "status": True,
#                             "message": f'Missing required headers. Required: {required_headers}'
#                         }, status=status.HTTP_400_BAD_REQUEST)
#                     data.append(row_lower)
#             else:
#                 return Response({
#                     "statusCode": 400,
#                     "status": True,
#                     'error': 'Unsupported file format. Use .xlsx or .csv'
#                 }, status=status.HTTP_400_BAD_REQUEST)

#             imported_count = 0
#             errors = []

#             VALID_TYPES = ["Numeric", "Text"]

#             for idx, row in enumerate(reversed(data), start=2):  # row number starts at 2 (after header)
#                 name = str(row.get('name')).strip() if row.get('name') else None
#                 datatype = str(row.get('datatype')).strip() if row.get('datatype') else None
#                 description = str(row.get('description')).strip() if row.get('description') else ''

#                 if not name or not datatype:
#                     errors.append(f"Row {idx}: 'name' and 'datatype' are required.")
#                     continue

#                 if datatype not in VALID_TYPES:
#                     errors.append(f"Row {idx}: Invalid datatype '{datatype}'. Must be one of {VALID_TYPES}.")
#                     continue

#                 # Validate based on datatype
#                 if datatype == "Numeric" and not name.isdigit():
#                     errors.append(f"Row {idx}: Name '{name}' must be numeric for datatype 'Numeric'.")
#                     continue
#                 elif datatype == "Text" and any(char.isdigit() for char in name):
#                     errors.append(f"Row {idx}: Name '{name}' must not contain numbers for datatype 'Text'.")
#                     continue

#                 existing = AcademicResultType.objects.filter(name__iexact=name).first()
#                 if existing:
#                     if not existing.is_deleted:
#                         duplicate_names.append(name)
#                         continue
#                     else:
#                         existing.description = description
#                         existing.datatype = datatype
#                         existing.is_deleted = False
#                         existing.save()
#                         imported_count += 1
#                 else:
#                     AcademicResultType.objects.create(
#                         name=name,
#                         datatype=datatype,
#                         description=description,
#                         is_deleted=False
#                     )
#                     imported_count += 1

#         except Exception as e:
#             return Response({
#                 "statusCode": 400,
#                 "status": True,
#                 'message': str(e)
#             }, status=status.HTTP_400_BAD_REQUEST)

#         return Response({
#             "statusCode": 200,
#             "status": True,
#             "duplicates": list(set(duplicate_names)),
#             "errors": errors,
#             "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
#             "imported_count": imported_count
#         }, status=status.HTTP_200_OK)

class AcademicResultTypeImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        import io, csv, openpyxl, re

        format_type = file.name.split('.')[-1].lower()
        duplicate_names = []
        skipped_rows = []

        required_headers = {'academic result type', 'data type'}
        optional_headers = {'description', 'modified on'}

        # Robust normalization: lowercase, strip, remove invisible chars
        def normalize_header(h):
            print("hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh00-------------",h)
            if not h:
                return ''
            h = str(h)
            h = re.sub(r'\s+', ' ', h)  # replace all whitespace sequences with a single space
            h = re.sub(r'[\u200B-\u200D\uFEFF]', '', h)  # remove zero-width/invisible chars
            return h.strip().lower()

        try:
            data = []

            # ---------------- XLSX Import ----------------
            if format_type == 'xlsx':
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                print("available_sheetsavailable_sheets-----",available_sheets)

                if not sheet_name:
                    return Response({'error': 'Please provide sheet_name', 'available_sheets': available_sheets}, status=400)
                if sheet_name not in available_sheets:
                    return Response({'error': f'Sheet "{sheet_name}" not found', 'available_sheets': available_sheets}, status=400)

                ws = wb[sheet_name]
                print("wswswswswswsws-----------",ws)
                if ws.max_row <= 1:
                    return Response({"statusCode": 400, "status": False, "message": f'The uploaded XLSX sheet "{sheet_name}" is empty.'}, status=400)

                headers = [normalize_header(cell.value) for cell in next(ws.iter_rows(min_row=1, max_row=1))]

                print("headersheadersheadersheaders----",headers)
                missing = required_headers - set(headers)
                print("missingmissingmissingmissing-------",missing)
                if missing:
                    return Response({"statusCode": 400, "status": False, "message": f"Missing required headers: {missing}"}, status=400)

                for row in ws.iter_rows(min_row=2, values_only=True):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    data.append(row_dict)

            # ---------------- CSV Import ----------------
            elif format_type == 'csv':
                decoded_file = file.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(decoded_file))
                reader.fieldnames = [normalize_header(h) for h in reader.fieldnames]

                missing = required_headers - set(reader.fieldnames)
                if missing:
                    return Response({"statusCode": 400, "status": False, "message": f"Missing required headers: {missing}"}, status=400)

                for row in reader:
                    row_lower = {normalize_header(k): v for k, v in row.items()}
                    data.append(row_lower)

            else:
                return Response({"statusCode": 400, "status": False, "error": "Unsupported file format. Use .xlsx or .csv"}, status=400)

            # ---------------- Data Processing ----------------
            imported_count = 0
            VALID_TYPES = ["Numeric", "Text"]

            for idx, row in enumerate(data, start=2):
                name = str(row.get('academic result type')).strip() if row.get('academic result type') else None
                datatype = str(row.get('data type')).strip() if row.get('data type') else None
                description = str(row.get('description')).strip() if row.get('description') else ''

                # Required fields
                if not name or not datatype:
                    skipped_rows.append({
                        "Row": idx,
                        "Academic Result Type": name or "",
                        "Data Type": datatype or "",
                        "Description": description or "",
                        "Reason": "Missing required field: Academic Result Type or Data Type"
                    })

                    continue

                # Validate data type
                if datatype not in VALID_TYPES:
                    skipped_rows.append({
                    "Row": idx,
                    "Academic Result Type": name or "",
                    "Data Type": datatype or "",
                    "Description": description or "",
                    "Reason": f"Invalid Data Type '{datatype}'. Expected {VALID_TYPES}"
                })

                    continue

                # Name must not contain numbers
                if any(char.isdigit() for char in name):
                    skipped_rows.append({
                    "Row": idx,
                    "Academic Result Type": name or "",
                    "Data Type": datatype or "",
                    "Description": description or "",
                    "Reason": f"Name '{name}' must not contain numbers"
                })

                    continue

                # Duplicate check
                existing = AcademicResultType.objects.filter(name__iexact=name).first()
                if existing:
                    if not existing.is_deleted:
                        duplicate_names.append({
                        "Row": idx,
                        "Academic Result Type": name,
                        "Data Type": datatype,
                        "Description": description,
                        "Reason": "Already exists"
                    })

                        continue
                    else:
                        existing.datatype = datatype
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    AcademicResultType.objects.create(name=name, datatype=datatype, description=description, is_deleted=False)
                    imported_count += 1

        except Exception as e:
            return Response({"statusCode": 400, "status": False, "message": str(e)}, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": duplicate_names,
            "skipped_rows": skipped_rows,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count
        }, status=200)

# -------------------- AcademicResult -------------------- #


# class AcademicResultListAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         # Optional search query parameters
#         search = request.GET.get('search', '').strip()
#         sort_by = request.GET.get('sortBy', 'created_at')
#         sort_order = request.GET.get('sortOrder', 'desc')
#         uuid_param = request.GET.get('academicResultType', '')


#         # Allowed sort fields
#         allowed_sort_fields = ['Academicresult', 'description', 'created_at']
#         if sort_by not in allowed_sort_fields:
#             sort_by = 'created_at'
#         if sort_order == 'desc':
#             sort_by = f'-{sort_by}'

#         # Initial queryset filtered for non-deleted results
#         queryset = AcademicResult.objects.filter(is_deleted=False)

#         uuid_list = []
#         if uuid_param:
#             for u in uuid_param.split(','):
#                 u = u.strip()
#                 try:
#                     uuid_list.append(UUID(u))
#                 except:
#                     pass

#         if uuid_list:
#             queryset = queryset.filter(AcademicResulttype__uuid__in=uuid_list)
            
#         # Apply search filter if search query is provided
#         if search:
#             queryset = queryset.filter(
#                 Q(Academicresult__istartwith=search) 
#             )

#         # Sorting
#         queryset = queryset.order_by(sort_by)

#         # Pagination
#         paginator = CustomPagination()  # CustomPagination should be implemented in your project
#         result_page = paginator.paginate_queryset(queryset, request)
        
#         serializer = AcademicResultSerializer(result_page, many=True)

#         return paginator.get_paginated_response(serializer.data)




class AcademicResultListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        custom_sort = request.GET.get('customSort')  # e.g., "Academicresult:asc,description:desc"
        uuid_param = request.GET.get('academicResultType', '')

        allowed_sort_fields = ['Academicresult', 'description', 'created_at', 'updated_at']

        # Initial queryset
        queryset = AcademicResult.objects.filter(is_deleted=False)

        # ----------------------
        # UUID Filter
        # ----------------------
        uuid_list = []
        if uuid_param:
            for u in uuid_param.split(','):
                u = u.strip()
                try:
                    uuid_list.append(UUID(u))
                except ValueError:
                    pass

        if uuid_list:
            queryset = queryset.filter(AcademicResulttype__uuid__in=uuid_list)

        # ----------------------
        # Search Filter
        # ----------------------
        if search:
            queryset = queryset.filter(
                Q(Academicresult__istartswith=search)
            )

        # ----------------------
        # Sort field mapping
        # ----------------------
        sort_field_map = {
            "uuid": "uuid",
            "academicResultType": "AcademicResulttype__name",
            "Academicresult": "Academicresult",
            "description": "description",
            "created_at": "created_at",
            "updated_at": "updated_at",
        }

        sort_fields = []

        # ----------------------
        # CUSTOM SORT
        # ----------------------
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
                    if field in ['Academicresult', 'description']:
                        f = Lower(orm_field)
                    else:
                        f = F(orm_field)

                    sort_fields.append(
                        f.asc(nulls_last=True) if order == 'asc' else f.desc(nulls_last=True)
                    )

                except ValueError:
                    continue

        # ----------------------
        # DEFAULT SORT
        # ----------------------
        else:
            sort_by = request.GET.get('sortBy', 'created_at')
            sort_order = request.GET.get('sortOrder', 'desc')
            orm_field = sort_field_map.get(sort_by, 'created_at')
            f = F(orm_field)
            sort_fields = [
                f.asc(nulls_last=True) if sort_order.lower() == 'asc' else f.desc(nulls_last=True)
            ]

        # ----------------------
        # APPLY SORTING
        # ----------------------
        queryset = queryset.order_by(*sort_fields)

        # ----------------------
        # Pagination + Response
        # ----------------------
        paginator = CustomPagination()
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


# class AcademicResultExportAPIView(APIView):
#     permission_classes = [IsAuthenticated, IsAdminUser]

#     def get(self, request):
#         format_type = request.GET.get('format', 'xlsx').lower()
#         fields = request.GET.get('fields')
#         uuids_param = request.GET.get('uuids', '')
#         uuids = [u.strip() for u in uuids_param.split(',') if u]

#         # Field mapping for export headers
#         field_header_map = {
#             'uuid': 'UUID',
#             'AcademicResulttype_id': 'Academic Result Type',
#             'Academicresult': 'Academic Result',
#             'description': 'Description',
#             'is_deleted': 'Deleted',
#             'created_at': 'Created On',
#             'updated_at': 'Modified On',
#         }

#         field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())

#         queryset = AcademicResult.objects.filter(is_deleted=False)
#         if uuids:
#             queryset = queryset.filter(uuid__in=uuids)
#         queryset = queryset.order_by('-created_at')

#         dataset = Dataset()
#         dataset.headers = [field_header_map.get(f, f) for f in field_list]
#         dataset.title = 'AcademicResults'

#         for obj in queryset:
#             row = []
#             for field in field_list:
#                 if field == 'AcademicResulttype_id':
#                     value = obj.AcademicResulttype.name if obj.AcademicResulttype else ''
#                 else:
#                     value = getattr(obj, field, '')
#                 if field in ['created_at', 'updated_at'] and value:
#                     value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
#                 elif isinstance(value, bool):
#                     value = int(value)
#                 row.append(value if value is not None else '')
#             dataset.append(row)

#         if format_type == 'csv':
#             file_data = dataset.export('csv')
#             content_type = 'text/csv'
#             file_name = 'academic_results.csv'
#         else:
#             file_data = io.BytesIO(dataset.export('xlsx'))
#             content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
#             file_name = 'academic_results.xlsx'

#         response = HttpResponse(
#             file_data if format_type == 'csv' else file_data.getvalue(),
#             content_type=content_type
#         )
#         response['Content-Disposition'] = f'attachment; filename="{file_name}"'
#         return response


class AcademicResultExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):

        format_type = request.GET.get("format", "xlsx").lower()
        fields = request.GET.get("fields")
        search = request.GET.get("search", "").strip()
        custom_sort = request.GET.get("customSort")

        # ------------------ Field Mapping ------------------
        field_header_map = {
            "uuid": "UUID",
            "AcademicResulttype_id": "Academic Result Type",
            "Academicresult": "Academic Result",
            "description": "Description",
            "created_at": "Created On",
            "updated_at": "Modified On",
        }

        # Allowed sort field mapping
        allowed_sort_fields = {
            "uuid": "uuid",
            "academicResultType": "AcademicResulttype__name",
            "Academicresult": "Academicresult",
            "description": "description",
            "created_at": "created_at",
            "updated_at": "updated_at",
        }

        # Fields to export
        field_list = (
            [f.strip() for f in fields.split(",")]
            if fields else list(field_header_map.keys())
        )

        # ---------------------------
        # Helper: Parse & Validate UUIDs
        # ---------------------------
        def parse_ids(key):
            raw = request.GET.get(key, "")
            if raw:
                return [x.strip() for x in raw.split(",") if x.strip()]
            return request.GET.getlist(key)

        def validate_uuid_list(items):
            valid = []
            for u in items:
                try:
                    valid.append(UUID(u))
                except:
                    pass
            return valid

        # Filters
        uuids_list = validate_uuid_list(parse_ids("uuids"))
        resulttype_list = validate_uuid_list(parse_ids("academicResultType"))

        # ------------------ Queryset ------------------
        queryset = AcademicResult.objects.select_related("AcademicResulttype")

        if uuids_list:
            queryset = queryset.filter(uuid__in=uuids_list)

        if resulttype_list:
            queryset = queryset.filter(AcademicResulttype__uuid__in=resulttype_list)

        # ------------------ Search ------------------
        if search:
            queryset = queryset.filter(
                Q(Academicresult__istartswith=search)
            )

        # ------------------ Custom Sort Logic ------------------
        sort_fields = []

        if custom_sort:
            for rule in custom_sort.split(","):
                try:
                    field, order = rule.split(":")
                    field = field.strip()
                    order = order.strip().lower()

                    if field not in allowed_sort_fields:
                        continue

                    orm_field = allowed_sort_fields[field]

                    # Check text fields for case-insensitive sort
                    text_fields = ["AcademicResulttype", "Academicresult", "description"]
                    is_text = field in text_fields

                    sort_expr = Lower(orm_field) if is_text else F(orm_field)

                    sort_fields.append(
                        sort_expr.asc(nulls_last=True)
                        if order == "asc"
                        else sort_expr.desc(nulls_last=True)
                    )

                except:
                    continue

        else:
            # Default sorting
            sort_fields = [F("created_at").desc(nulls_last=True)]

        queryset = queryset.order_by(*sort_fields)

        # ------------------ Dataset ------------------
        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = "AcademicResults"

        for obj in queryset:
            row = []
            for field in field_list:

                if field == "AcademicResulttype_id":
                    value = obj.AcademicResulttype.name if obj.AcademicResulttype else ""

                elif field in ["created_at", "updated_at"]:
                    field_value = getattr(obj, field)
                    value = (
                        timezone.localtime(field_value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
                        if field_value else ""
                    )

                else:
                    value = getattr(obj, field, "")

                row.append("" if value is None else value)

            dataset.append(row)

        # ------------------ Export ------------------
        if format_type == "csv":
            response = HttpResponse(dataset.export("csv"), content_type="text/csv")
            filename = "academic_results.csv"
        else:
            file_data = io.BytesIO(dataset.export("xlsx"))
            response = HttpResponse(
                file_data.getvalue(),
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            filename = "academic_results.xlsx"

        response["Content-Disposition"] = f'attachment; filename="{filename}"'
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


# ------------------- Export API ------------------- #
class AcademicResultComparisonImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=400)

        format_type = file.name.split('.')[-1].lower()

        required_headers = {
            'original result type',
            'original result',
            'compare result type',
            'compare result'
        }

        optional_headers = {'description'}

        data = []
        duplicates = []
        skipped_rows = []
        imported_count = 0

        try:
            # ============ READ XLSX FILE ============
            if format_type == 'xlsx':
                import openpyxl
                wb = openpyxl.load_workbook(file, read_only=True)
                sheets = wb.sheetnames

                if not sheet_name:
                    return Response({
                        "error": "Please provide sheet_name",
                        "available_sheets": sheets
                    }, status=400)

                if sheet_name not in sheets:
                    return Response({
                        "error": f"Sheet '{sheet_name}' not found",
                        "available_sheets": sheets
                    }, status=400)

                ws = wb[sheet_name]
                headers = [
                    (cell.value or "").strip().lower()
                    for cell in next(ws.iter_rows(min_row=1, max_row=1))
                ]

                missing = required_headers - set(headers)
                if missing:
                    return Response({"error": f"Missing required headers: {missing}"}, status=400)

                for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    row_dict["_row_number"] = idx
                    data.append(row_dict)

            # ============ READ CSV FILE ============
            elif format_type == "csv":
                import csv, io
                decoded = file.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(decoded))

                headers = {h.strip().lower() for h in reader.fieldnames}
                missing = required_headers - headers
                if missing:
                    return Response({"error": f"Missing required headers: {missing}"}, status=400)

                for idx, row in enumerate(reader, start=2):
                    row_dict = {k.lower(): (v or "").strip() for k, v in row.items()}
                    row_dict["_row_number"] = idx
                    data.append(row_dict)

            else:
                return Response({"error": "Unsupported file format"}, status=400)

            # ===========================================================
            #                     PROCESS ROWS
            # ===========================================================
            for row in reversed(data):
                row_no = row.get("_row_number")

                original_type_name = (row.get("original result type") or "").strip()
                original_result_name = (row.get("original result") or "").strip()
                compare_type_name = (row.get("compare result type") or "").strip()
                compare_result_name = (row.get("compare result") or "").strip()
                description = (row.get("description") or "").strip()

                # ------------------ VALIDATE REQUIRED FIELDS ------------------
                if not original_type_name or not original_result_name or not compare_type_name or not compare_result_name:
                    skipped_rows.append({
                        "Row": row_no,
                        "Original Result Type": original_type_name,
                        "Original Result": original_result_name,
                        "Compare Result Type": compare_type_name,
                        "Compare Result": compare_result_name,
                        "Reason": "Missing required fields",
                    })
                    continue

                # ------------------ DATABASE LOOKUPS ------------------
                original_type = AcademicResultType.objects.filter(name__iexact=original_type_name).first()
                if not original_type:
                    skipped_rows.append({
                        "Row": row_no,
                        "Original Result Type": original_type_name,
                        "Reason": "Original Result Type not found"
                    })
                    continue

                original_result = AcademicResult.objects.filter(result_name__iexact=original_result_name).first()
                if not original_result:
                    skipped_rows.append({
                        "Row": row_no,
                        "Original Result": original_result_name,
                        "Reason": "Original Result not found"
                    })
                    continue

                compare_type = AcademicResultType.objects.filter(name__iexact=compare_type_name).first()
                if not compare_type:
                    skipped_rows.append({
                        "Row": row_no,
                        "Compare Result Type": compare_type_name,
                        "Reason": "Compare Result Type not found"
                    })
                    continue

                compare_result = AcademicResult.objects.filter(result_name__iexact=compare_result_name).first()
                if not compare_result:
                    skipped_rows.append({
                        "Row": row_no,
                        "Compare Result": compare_result_name,
                        "Reason": "Compare Result not found"
                    })
                    continue

                # ------------------ DUPLICATE CHECK ------------------
                existing = AcademicResultComparison.objects.filter(
                    original_result_type=original_type,
                    original_result=original_result,
                    compare_result_type=compare_type,
                    compare_result=compare_result
                ).first()

                if existing:
                    duplicates.append({
                        "Row": row_no,
                        "Original Result Type": original_type_name,
                        "Original Result": original_result_name,
                        "Compare Result Type": compare_type_name,
                        "Compare Result": compare_result_name,
                        "Reason": "Duplicate combination already exists"
                    })
                    continue

                # ------------------ CREATE NEW RECORD ------------------
                AcademicResultComparison.objects.create(
                    original_result_type=original_type,
                    original_result=original_result,
                    compare_result_type=compare_type,
                    compare_result=compare_result
                )
                imported_count += 1

        except Exception as e:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": str(e)
            })

        # ===========================================================
        #                     FINAL RESPONSE
        # ===========================================================
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Import completed",
            "imported_count": imported_count,
            "duplicates": list(reversed(duplicates)),
            "skipped_rows": list(reversed(skipped_rows)),
        })


# -------------------- EducationType CRUD -------------------- #

# class EducationTypeListAPIView(APIView):
#     permission_classes = [IsAuthenticated, IsAdminUser]

#     def get(self, request):
#         search = request.GET.get('search', '').strip()
#         sort_by = request.GET.get('sortBy', 'created_at')
#         sort_order = request.GET.get('sortOrder', 'desc')  # default to newest first

#         allowed_sort_fields = ['educationType', 'Perticulars', 'created_at']
#         if sort_by not in allowed_sort_fields:
#             sort_by = 'created_at'

#         # Apply descending order for 'desc'
#         if sort_order == 'desc':
#             sort_by = f'-{sort_by}'

#         queryset = EducationType.objects.filter(is_deleted=False)

#         if search:
#             queryset = queryset.filter(
#                 Q(educationType__istartswith=search)
#             )

#         queryset = queryset.order_by(sort_by)
#         paginator = CustomPagination()
#         result_page = paginator.paginate_queryset(queryset, request)
#         serializer = EducationTypeSerializer(result_page, many=True)
#         return paginator.get_paginated_response(serializer.data)
    

class EducationTypeListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        custom_sort = request.GET.get('customSort')
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        # Allowed fields
        allowed_sort_fields = ['educationType', 'Perticulars', 'created_at']

        # Mapping for ORM
        sort_field_map = {
            'educationType': 'educationType',
            'Perticulars': 'Perticulars',
            'created_at': 'created_at',
            'updated_at': 'updated_at',
        }

        # Initial queryset
        queryset = EducationType.objects.filter(is_deleted=False)

        # Apply search
        if search:
            queryset = queryset.filter(
                Q(educationType__icontains=search)
            )

        sort_fields = []

        # -----------------------------
        # CUSTOM SORT (same style as AcademicResultListAPIView)
        # -----------------------------
        if custom_sort:
            for rule in custom_sort.split(','):
                try:
                    field, order = rule.split(':')
                    field = field.strip()
                    order = order.strip().lower()

                    if field not in sort_field_map:
                        continue

                    orm_field = sort_field_map[field]

                    # Case-insensitive on string fields
                    if field in ['educationType', 'Perticulars']:
                        f = Lower(orm_field)
                    else:
                        f = F(orm_field)

                    sort_fields.append(
                        f.asc(nulls_last=True) if order == 'asc' else f.desc(nulls_last=True)
                    )
                except ValueError:
                    continue
        else:
            # -----------------------------
            # DEFAULT SORT (unchanged)
            # -----------------------------
            if sort_by not in allowed_sort_fields:
                sort_by = 'created_at'

            orm_field = sort_field_map.get(sort_by, 'created_at')
            f = F(orm_field)

            sort_fields = [
                f.asc(nulls_last=True) if sort_order.lower() == 'asc' else f.desc(nulls_last=True)
            ]

        # Apply ordering
        queryset = queryset.order_by(*sort_fields)

        # Pagination + Serialization
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


# class EducationTypeExportAPIView(APIView):
#     permission_classes = [IsAuthenticated, IsAdminUser]
 
#     def get(self, request):
#         format_type = request.GET.get('format', 'xlsx').lower()
#         fields = request.GET.get('fields')
#         uuids_param = request.GET.get('uuids', '')
#         uuids = [u.strip() for u in uuids_param.split(',') if u]
 
#         field_header_map = {
#             'uuid': 'UUID',
#             'educationType': 'Education Type',
#             'Perticulars': 'Particulars',
#             'is_deleted': 'Deleted',
#             'created_at': 'Created On',
#             'updated_at': 'Updated On',
#         }
 
#         if fields:
#             field_list = [f.strip() for f in fields.split(',')]
#         else:
#             field_list = list(field_header_map.keys())
 
#         queryset = EducationType.objects.filter(is_deleted=False)
#         if uuids:
#             queryset = queryset.filter(uuid__in=uuids)
#         queryset = queryset.order_by('-created_at')
 
#         dataset = Dataset()
#         dataset.headers = [field_header_map.get(f, f) for f in field_list]
#         dataset.title = 'EducationType'
 
#         for obj in queryset:
#             row = []
#             for field in field_list:
#                 value = getattr(obj, field, '')
 
#                 if field in ['created_at', 'updated_at'] and value:
#                     value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
#                 elif isinstance(value, bool):
#                     value = int(value)
 
#                 row.append(value if value is not None else '')
 
#             dataset.append(row)
 
#         if format_type == 'csv':
#             file_data = dataset.export('csv')
#             content_type = 'text/csv'
#             file_name = 'education-type.csv'
#         else:
#             file_data = io.BytesIO(dataset.export('xlsx'))
#             content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
#             file_name = 'education-type.xlsx'
 
#         response = HttpResponse(
#             file_data if format_type == 'csv' else file_data.getvalue(),
#             content_type=content_type
#         )
#         response['Content-Disposition'] = f'attachment; filename="{file_name}"'
#         return response
 
class EducationTypeExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        search = request.GET.get('search', '').strip()
        custom_sort = request.GET.get('customSort')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        # -----------------------------
        # Field Header Mapping
        # -----------------------------
        field_header_map = {
            'uuid': 'UUID',
            'educationType': 'Education Type',
            'Perticulars': 'Particulars',
            'is_deleted': 'Deleted',
            'created_at': 'Created On',
            'updated_at': 'Updated On',
        }

        # Final export fields
        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())

        # -----------------------------
        # Base Queryset
        # -----------------------------
        queryset = EducationType.objects.filter(is_deleted=False)

        # UUID Filtering
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)

        # Search Filtering
        if search:
            queryset = queryset.filter(
                Q(educationType__icontains=search) |
                Q(Perticulars__icontains=search)
            )

        # -----------------------------
        # Sorting Logic (Same as AcademicResultTypeExportAPIView)
        # -----------------------------
        sort_field_map = {
            'uuid': 'uuid',
            'educationType': 'educationType',
            'Perticulars': 'Perticulars',
            'created_at': 'created_at',
            'updated_at': 'updated_at',
        }

        sort_fields = []
        annotations = {}

        if custom_sort:
            # Example: ?customSort=educationType:asc,Perticulars:desc
            for idx, rule in enumerate(custom_sort.split(',')):
                try:
                    field, order = rule.split(':')
                    field = field.strip()
                    order = order.strip().lower()

                    if field not in sort_field_map:
                        return Response({
                            "status": False,
                            "statusCode": 400,
                            "message": f"Invalid sort field: {field}"
                        }, status=400)

                    orm_field = sort_field_map[field]

                    # Case-insensitive sorting for text
                    if field in ['educationType', 'Perticulars']:
                        ann_name = f"sort_key_{idx}"
                        annotations[ann_name] = Lower(orm_field)
                        sort_fields.append(ann_name if order == 'asc' else f"-{ann_name}")
                    else:
                        sort_fields.append(orm_field if order == 'asc' else f"-{orm_field}")

                except ValueError:
                    return Response({
                        "status": False,
                        "statusCode": 400,
                        "message": f"Invalid sorting rule format: {rule}"
                    }, status=400)

        # Apply annotations if required
        if annotations:
            queryset = queryset.annotate(**annotations)

        # Default fallback sort
        if not sort_fields:
            sort_fields = ['-created_at']

        queryset = queryset.order_by(*sort_fields)

        # -----------------------------
        # Generate Export Dataset
        # -----------------------------
        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'EducationType'

        for obj in queryset:
            row = []
            for field in field_list:
                value = getattr(obj, field, '')

                if field in ['created_at', 'updated_at'] and value:
                    value = timezone.localtime(value).strftime("%d-%m-%Y %I:%M:%S %p")
                elif isinstance(value, bool):
                    value = int(value)

                row.append(value if value is not None else '')

            dataset.append(row)

        # -----------------------------
        # File Output
        # -----------------------------
        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'education-type.csv'
            output = file_data
        else:
            buffer = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'education-type.xlsx'
            output = buffer.getvalue()

        response = HttpResponse(output, content_type=content_type)
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
                    skipped_rows.append({"Row": row_number,
                                         "Education Type":name or "",
                                         "Perticulars":perticulars or "",
                                          "Reason": "Missing education type"
                                          })
                    continue

                existing = EducationType.objects.filter(educationType__iexact=name).first()
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({"Row": row_number, "Education Type":name or "",
                                         "Perticulars":perticulars or "","Reason": "Already exists"})
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
            "duplicates": list(reversed(duplicates)),
            "skipped_rows": list(reversed(skipped_rows)),
        }, status=200)



# -------------------- MediumofEducation CRUD -------------------- #

class MediumofEducationListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        custom_sort = request.GET.get('customSort')
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')
        uuids_param = request.GET.get('uuids', '')

        # -----------------------------
        # UUID filter
        # -----------------------------
        def parse_uuid_list(raw):
            valid = []
            if raw:
                for u in raw.split(','):
                    try:
                        valid.append(UUID(u.strip()))
                    except:
                        pass
            return valid

        uuid_list = parse_uuid_list(uuids_param)

        # -----------------------------
        # Base queryset
        # -----------------------------
        queryset = MediumofEducation.objects.filter(is_deleted=False)
        if uuid_list:
            queryset = queryset.filter(uuid__in=uuid_list)

        # -----------------------------
        # Search filter
        # -----------------------------
        if search:
            queryset = queryset.filter(name__istartswith=search)

        # -----------------------------
        # Sorting
        # -----------------------------
        sort_field_map = {
            "name": "name",
            "perticulars": "perticulars",
            "created_at": "created_at",
            "updated_at": "updated_at",
        }
        allowed_sort_fields = list(sort_field_map.keys())

        sort_fields = []

        if custom_sort:
            for idx, rule in enumerate(custom_sort.split(',')):
                try:
                    field, order = rule.split(':')
                    field = field.strip()
                    order = order.strip().lower()

                    if field not in sort_field_map:
                        continue

                    orm_field = sort_field_map[field]

                    # Case-insensitive for string fields
                    if field in ['name', 'perticulars']:
                        f = Lower(orm_field)
                    else:
                        f = F(orm_field)

                    sort_fields.append(f.asc(nulls_last=True) if order == 'asc' else f.desc(nulls_last=True))
                except ValueError:
                    continue
        else:
            if sort_by not in allowed_sort_fields:
                sort_by = 'created_at'
            orm_field = sort_field_map[sort_by]
            f = F(orm_field)
            sort_fields = [f.asc(nulls_last=True) if sort_order == 'asc' else f.desc(nulls_last=True)]

        queryset = queryset.order_by(*sort_fields)

        # -----------------------------
        # Pagination + Response
        # -----------------------------
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
        search = request.GET.get('search', '').strip()
        custom_sort = request.GET.get('customSort')

        # ---------------------------
        # Helper: Parse & validate UUIDs
        # ---------------------------
        def parse_ids(param_name):
            raw = request.GET.get(param_name, '')
            if raw:
                items = [x.strip() for x in raw.split(',') if x.strip()]
            else:
                items = request.GET.getlist(param_name)
            return items

        def validate_uuid_list(uuid_list):
            valid = []
            for u in uuid_list:
                try:
                    valid.append(UUID(u))
                except:
                    pass
            return valid

        uuids_list = validate_uuid_list(parse_ids('uuids'))

        # ---------------------------
        # Field Header Mapping
        # ---------------------------
        field_header_map = {
            'uuid': 'UUID',
            'name': 'Medium of Education',
            'perticulars': 'Perticulars',
            'is_deleted': 'Deleted',
            'created_at': 'Created On',
            'updated_at': 'Modified On',
        }
        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())

        # ---------------------------
        # Base QuerySet
        # ---------------------------
        queryset = MediumofEducation.objects.filter(is_deleted=False)
        if uuids_list:
            queryset = queryset.filter(uuid__in=uuids_list)

        if search:
            queryset = queryset.filter(name__istartswith=search)

        # ---------------------------
        # Sorting Logic
        # ---------------------------
        sort_field_map = {
            'uuid': 'uuid',
            'name': 'name',
            'perticulars': 'perticulars',
            'created_at': 'created_at',
            'updated_at': 'updated_at',
        }

        sort_fields = []
        annotations = {}

        if custom_sort:
            for idx, rule in enumerate(custom_sort.split(',')):
                try:
                    field, order = rule.split(':')
                    field = field.strip()
                    order = order.strip().lower()
                    if field not in sort_field_map:
                        return Response({
                            "status": False,
                            "statusCode": 400,
                            "message": f"Invalid sort field: {field}"
                        }, status=400)
                    orm_field = sort_field_map[field]

                    # Case-insensitive sorting for string fields
                    if field in ['name', 'perticulars']:
                        ann_name = f"sort_key_{idx}"
                        annotations[ann_name] = Lower(orm_field)
                        sort_fields.append(ann_name if order == 'asc' else f"-{ann_name}")
                    else:
                        sort_fields.append(orm_field if order == 'asc' else f"-{orm_field}")

                except ValueError:
                    return Response({
                        "status": False,
                        "statusCode": 400,
                        "message": f"Invalid sorting rule format: {rule}"
                    }, status=400)

        # Apply annotations
        if annotations:
            queryset = queryset.annotate(**annotations)

        # Default sort
        if not sort_fields:
            sort_fields = ['-created_at']

        queryset = queryset.order_by(*sort_fields)

        # ---------------------------
        # Prepare Dataset
        # ---------------------------
        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'MediumofEducation'

        for obj in queryset:
            row = []
            for field in field_list:
                value = getattr(obj, field, '')

                if field in ['created_at', 'updated_at'] and value:
                    value = timezone.localtime(value).strftime("%d-%m-%Y %I:%M:%S %p")
                elif isinstance(value, bool):
                    value = int(value)
                row.append(value if value is not None else '')
            dataset.append(row)

        # ---------------------------
        # Export File
        # ---------------------------
        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'medium_of_education.csv'
            response = HttpResponse(file_data, content_type=content_type)
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'medium_of_education.xlsx'
            response = HttpResponse(file_data.getvalue(), content_type=content_type)

        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response
    

class MediumofEducationImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'statusCode': 400, 'status': False, 'message': 'No file uploaded'}, status=400)

        format_type = file.name.split('.')[-1].lower()
        required_headers = {'medium of education'}
        optional_headers = {'perticulars'}

        try:
            # ---------------- Load file ----------------
            data = []
            if format_type == 'xlsx':
                wb = openpyxl.load_workbook(file, read_only=True)
                sheets = wb.sheetnames

                if not sheet_name:
                    return Response({'statusCode': 400, 'status': False, 'message': 'Please provide sheet_name', 'available_sheets': sheets}, status=400)
                if sheet_name not in sheets:
                    return Response({'statusCode': 400, 'status': False, 'message': f'Sheet "{sheet_name}" not found', 'available_sheets': sheets}, status=400)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({'statusCode': 400, 'status': False, 'message': f'Sheet "{sheet_name}" is empty'}, status=400)

                headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                if not required_headers.issubset(set(headers)):
                    return Response({'statusCode': 400, 'status': False, 'message': f'Missing required headers: {required_headers - set(headers)}'}, status=400)

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
                        return Response({'statusCode': 400, 'status': False, 'message': f'Missing required headers: {required_headers - set(row_lower.keys())}'}, status=400)
                    data.append(row_lower)
            else:
                return Response({'statusCode': 400, 'status': False, 'message': 'Unsupported file format. Use .xlsx or .csv'}, status=400)

            # ---------------- Process Rows ----------------
            to_create = []
            duplicates = []
            skipped_rows = []
            existing_in_file = set()

            # Preload existing MediumofEducation
            existing_mediums = {m.name.strip().lower(): m for m in MediumofEducation.objects.all()}

            for row in reversed(data):
                row_number = row.get('_row_number', 'Unknown')
                name = (row.get('medium of education') or '').strip()
                perticulars = (row.get('perticulars') or '').strip()

                if not name:
                    skipped_rows.append({
                        "Row": row_number,
                        "Medium of Education": name or "Unknown",
                        "perticulars":perticulars or "",
                        "Reason": "Missing required field 'Medium of Education'"
                    })
                    continue

                key = name.lower()

                # Check duplicates in DB and current file
                existing_obj = existing_mediums.get(key)
                if existing_obj and not existing_obj.is_deleted:
                    duplicates.append({
                        "Row": row_number,
                        "Medium of Education": name,
                        "perticulars":perticulars or "",
                        "Reason": "Duplicate medium of education"
                    })
                    continue
                elif key in existing_in_file:
                    duplicates.append({
                        "Row": row_number,
                        "Medium of Education": name,
                        "perticulars":perticulars or "",
                        "Reason": "Duplicate in file"
                    })
                    continue

                existing_in_file.add(key)

                # Reactivate if soft-deleted
                if existing_obj and existing_obj.is_deleted:
                    existing_obj.Perticulars = perticulars
                    existing_obj.is_deleted = False
                    existing_obj.save()
                else:
                    to_create.append(
                        MediumofEducation(
                            name=name,
                            perticulars=perticulars,
                            is_deleted=False
                        )
                    )

            # ---------------- Bulk Insert ----------------
            with transaction.atomic():
                MediumofEducation.objects.bulk_create(to_create, ignore_conflicts=True, batch_size=500)

            return Response({
                "statusCode": 200,
                "status": True,
                "imported_count": len(to_create) + sum(1 for m in existing_mediums.values() if m.is_deleted == False),
                "duplicates": reversed(duplicates),
                "skipped_rows": reversed(skipped_rows),
                "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful"
            }, status=200)

        except Exception as e:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": str(e)
            }, status=400)
        
# -------------------- ECAFor CRUD -------------------- #

# class ECAForListAPIView(APIView):

#     def get(self, request):
#         search = request.GET.get('search', '').strip()
#         sort_by = request.GET.get('sortBy', 'created_at')
#         sort_order = request.GET.get('sortOrder', 'desc')

#         allowed_sort_fields = ['name', 'perticulars', 'updated_at']
#         if sort_by not in allowed_sort_fields:
#             sort_by = 'created_at'

#         if sort_order == 'desc':
#             sort_by = f'-{sort_by}'

#         queryset = ECAFor.objects.filter(is_deleted=False)

#         if search:
#             queryset = queryset.filter(Q(name__istartswith=search))

#         queryset = queryset.order_by(sort_by)
#         paginator = CustomPagination()
#         result_page = paginator.paginate_queryset(queryset, request)
#         serializer = ECAForSerializer(result_page, many=True)

#         return paginator.get_paginated_response(serializer.data)

class ECAForListAPIView(APIView):

    def get(self, request):
        search = request.GET.get('search', '').strip()
        custom_sort = request.GET.get('customSort')
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        queryset = ECAFor.objects.filter(is_deleted=False)

        # -----------------------------------------------
        # SEARCH FILTER
        # -----------------------------------------------
        if search:
            queryset = queryset.filter(name__istartswith=search)

        # -----------------------------------------------
        # SORTING MAP
        # -----------------------------------------------
        sort_field_map = {
            "name": "name",
            "description": "description",   # adjust if 'perticulars' field name is different
            "created_at": "created_at",
            "updated_at": "updated_at",
        }

        allowed_sort_fields = list(sort_field_map.keys())
        sort_fields = []

        # -----------------------------------------------
        # CUSTOM SORT
        # -----------------------------------------------
        if custom_sort:
            for rule in custom_sort.split(","):
                try:
                    field, order = rule.split(":")
                    field = field.strip()
                    order = order.strip().lower()

                    if field not in sort_field_map:
                        continue

                    orm_field = sort_field_map[field]

                    # Case-insensitive sorting for string fields
                    if field in ["name", "perticulars"]:
                        f = Lower(orm_field)
                    else:
                        f = F(orm_field)

                    sort_fields.append(
                        f.asc(nulls_last=True)
                        if order == "asc" else f.desc(nulls_last=True)
                    )

                except ValueError:
                    continue

        else:
            # -----------------------------------------------
            # DEFAULT SORT
            # -----------------------------------------------
            if sort_by not in allowed_sort_fields:
                sort_by = "created_at"

            orm_field = sort_field_map.get(sort_by, "created_at")
            f = F(orm_field)
            sort_fields = [
                f.asc(nulls_last=True) if sort_order == "asc" else f.desc(nulls_last=True)
            ]

        queryset = queryset.order_by(*sort_fields)

        # -----------------------------------------------
        # PAGINATION
        # -----------------------------------------------
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



# class ECAForExportAPIView(APIView):
#     permission_classes = [IsAuthenticated, IsAdminUser]

#     def get(self, request):
#         format_type = request.GET.get('format', 'xlsx').lower()
#         fields = request.GET.get('fields')
#         uuids_param = request.GET.get('uuids', '')
#         uuids = [u.strip() for u in uuids_param.split(',') if u]

#         field_header_map = {
#             'uuid': 'UUID',
#             'name': 'ECA For',
#             'description': 'Description',
#             'is_deleted': 'Deleted',
#             'updated_at': 'Modified On',
#         }

#         field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())

#         queryset = ECAFor.objects.filter(is_deleted=False)
#         if uuids:
#             queryset = queryset.filter(uuid__in=uuids)
#         queryset = queryset.order_by('-created_at')

#         dataset = Dataset()
#         dataset.headers = [field_header_map.get(f, f) for f in field_list]
#         dataset.title='ECA For  '

#         for obj in queryset:
#             row = []
#             for field in field_list:
#                 value = getattr(obj, field, '')
#                 if field in ['created_at', 'updated_at'] and value:
#                     value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
#                 elif isinstance(value, bool):
#                     value = int(value)
#                 row.append(value if value is not None else '')
#             dataset.append(row)

#         if format_type == 'csv':
#             file_data = dataset.export('csv')
#             content_type = 'text/csv'
#             file_name = 'esa_for.csv'
#         else:
#             file_data = io.BytesIO(dataset.export('xlsx'))
#             content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
#             file_name = 'esa_for.xlsx'

#         response = HttpResponse(
#             file_data if format_type == 'csv' else file_data.getvalue(),
#             content_type=content_type
#         )
#         response['Content-Disposition'] = f'attachment; filename="{file_name}"'
#         return response

class ECAForExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()

        # ----------------------------
        # Search & Custom Sort Params
        # ----------------------------
        search = request.GET.get('search', '').strip()
        custom_sort = request.GET.get('customSort')
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        # ----------------------------
        # UUID Filtering
        # ----------------------------
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        # ----------------------------
        # Export Field Mapping
        # ----------------------------
        field_header_map = {
            'uuid': 'UUID',
            'name': 'ECA For',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'updated_at': 'Modified On',
            'created_at': 'Created On',
        }

        fields = request.GET.get('fields')
        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())

        # ----------------------------
        # Queryset Base
        # ----------------------------
        queryset = ECAFor.objects.filter(is_deleted=False)

        if uuids:
            queryset = queryset.filter(uuid__in=uuids)

        if search:
            queryset = queryset.filter(name__istartswith=search)

        # ----------------------------
        # Sort Field Map (matches List API)
        # ----------------------------
        sort_field_map = {
            "name": "name",
            "perticulars": "description",
            "created_at": "created_at",
            "updated_at": "updated_at",
        }

        allowed_sort_fields = list(sort_field_map.keys())
        sort_fields = []

        # ----------------------------
        # Custom Sort
        # ----------------------------
        if custom_sort:
            for rule in custom_sort.split(","):
                try:
                    field, order = rule.split(":")
                    field = field.strip()
                    order = order.strip().lower()

                    if field not in sort_field_map:
                        continue

                    orm_field = sort_field_map[field]

                    # Case-insensitive for text fields
                    if field in ["name", "perticulars"]:
                        f = Lower(orm_field)
                    else:
                        f = F(orm_field)

                    sort_fields.append(
                        f.asc(nulls_last=True) if order == "asc" else f.desc(nulls_last=True)
                    )

                except ValueError:
                    continue

        else:
            # Default Sort
            if sort_by not in allowed_sort_fields:
                sort_by = "created_at"

            orm_field = sort_field_map.get(sort_by, "created_at")
            f = F(orm_field)
            sort_fields = [
                f.asc(nulls_last=True) if sort_order == "asc" else f.desc(nulls_last=True)
            ]

        queryset = queryset.order_by(*sort_fields)

        # ----------------------------
        # Dataset Building
        # ----------------------------
        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'ECAFor'

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

        # ----------------------------
        # File Export
        # ----------------------------
        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'eca_for.csv'
            response = HttpResponse(file_data, content_type=content_type)

        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'eca_for.xlsx'
            response = HttpResponse(file_data.getvalue(), content_type=content_type)

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
                    skipped_rows.append({"Row": row_number,"Description":description or "", "Reason": "Missing ECAFor name"})
                    continue

                existing = ECAFor.objects.filter(name__iexact=name).first()
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({"Row": row_number, "ECA For": name,"Description":description or "", "Reason": "Already exists"})
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
            "duplicates": list(reversed(duplicates)),
            "skipped_rows": list(reversed(skipped_rows)),
        }, status=200)


class ECAAwardingBodyListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        custom_sort = request.GET.get('customSort')
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        uuid_country = request.GET.get('country', '')
        uuid_ecafor = request.GET.get('ecaFor', '')

        queryset = ECAAwardingBody.objects.all()

        # ----------------------
        # UUID FILTERING HELPERS
        # ----------------------
        def parse_uuid_list(raw):
            valid = []
            if raw:
                for x in raw.split(','):
                    try:
                        valid.append(UUID(x.strip()))
                    except:
                        pass
            return valid

        country_list = parse_uuid_list(uuid_country)
        ecafor_list = parse_uuid_list(uuid_ecafor)

        if country_list:
            queryset = queryset.filter(country__uuid__in=country_list)
        if ecafor_list:
            queryset = queryset.filter(ecafor__uuid__in=ecafor_list)

        # ----------------------
        # SEARCH FILTER
        # ----------------------
        if search:
            queryset = queryset.filter(eca_body_full_name__istartswith=search)

        # ----------------------
        # SORT FIELD MAP
        # ----------------------
        sort_field_map = {
            "uuid": "uuid",
            "country": "country__name",
            "ecaFor": "ecafor__name",
            "eca_body_full_name": "eca_body_full_name",
            "eca_body_short_name": "eca_body_short_name",
            "eca_valid_period": "eca_valid_period",
            "created_at": "created_at",
            "updated_at": "updated_at",
        }

        allowed_sort_fields = list(sort_field_map.keys())
        sort_fields = []

        # ----------------------
        # CUSTOM SORT LOGIC
        # ----------------------
        if custom_sort:
            for rule in custom_sort.split(","):
                try:
                    field, order = rule.split(":")
                    field = field.strip()
                    order = order.strip().lower()

                    if field not in sort_field_map:
                        continue

                    orm_field = sort_field_map[field]

                    # Case-insensitive fields
                    if field in ["country", "ecafor", "eca_body_full_name", "eca_body_short_name", "eca_valid_period"]:
                        f = Lower(orm_field)
                    else:
                        f = F(orm_field)

                    sort_fields.append(
                        f.asc(nulls_last=True) if order == "asc" else f.desc(nulls_last=True)
                    )

                except ValueError:
                    continue

        else:
            # ----------------------
            # DEFAULT SORT
            # ----------------------
            if sort_by not in allowed_sort_fields:
                sort_by = "created_at"

            orm_field = sort_field_map.get(sort_by, "created_at")
            f = F(orm_field)
            sort_fields = [
                f.asc(nulls_last=True) if sort_order.lower() == "asc" else f.desc(nulls_last=True)
            ]

        queryset = queryset.order_by(*sort_fields)

        # ----------------------
        # PAGINATION
        # ----------------------
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = ECAAwardingBodySerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)
    

class ECAAwardingBodyCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        try:
            serializer = ECAAwardingBodySerializer(data=request.data)

            # -----------------------------------
            # Validate serializer fields first
            # -----------------------------------
            if not serializer.is_valid():
                return Response({
                    "status": False,
                    "statusCode": 400,
                    "message": "Validation error",
                    "data": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

            data = serializer.validated_data

            # -----------------------------------
            # Extract foreign keys
            # -----------------------------------
            country_obj = data.get("country")
            ecafor_obj = data.get("ecafor")
            eca_body_full_name = (data.get("eca_body_full_name") or "").strip()

            # -----------------------------------
            # Duplicate check
            # -----------------------------------
            try:
                if ECAAwardingBody.objects.filter(
                    country=country_obj,            # <-- use instance
                    ecafor=ecafor_obj,              # <-- use instance  
                    eca_body_full_name__iexact=eca_body_full_name
                ).exists():
                    return Response({
                        "status": False,
                        "statusCode": 400,
                        "message": "This ECA Awarding Body already exists.",
                    }, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({
                    "status": False,
                    "statusCode": 400,
                    "message": "Error during duplicate check.",
                    "error": str(e)
                }, status=status.HTTP_400_BAD_REQUEST)

            # -----------------------------------
            # Save object
            # -----------------------------------
            obj = serializer.save()

            return Response({
                "status": True,
                "statusCode": 200,
                "message": "ECA Awarding Body created successfully.",
                "data": ECAAwardingBodySerializer(obj).data
            }, status=status.HTTP_201_CREATED)

        # -----------------------------------
        # Handle DB-level errors
        # -----------------------------------
        except IntegrityError as e:
            return Response({
                "status": False,
                "statusCode": 400,
                "message": "Duplicate entry or invalid foreign key reference.",
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        # -----------------------------------
        # Catch any unexpected error
        # -----------------------------------
        except Exception as e:
            return Response({
                "status": False,
                "statusCode": 500,
                "message": "Something went wrong while creating ECA Awarding Body.",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
     

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
# class ECAAwardingBodyExportAPIView(APIView):
#     def get(self, request):
#         format_type = request.GET.get('format', 'xlsx').lower()
#         fields = request.GET.get('fields')
#         uuids_param = request.GET.get('uuids', '')
#         uuids = [u.strip() for u in uuids_param.split(',') if u]

#         field_header_map = {
#             'uuid': 'UUID',
#             'country': 'Country',
#             'ecafor': 'ECA For',
#             'valid_duration_value': 'ECA Valid Duration',
#             'eca_body_full_name': 'ECA Body Full Name',
#             'eca_body_short_name': 'ECA Body Short Name',
#             'eca_valid_period': 'ECA Valid Period',
#             'created_at': 'Created On',
#             'updated_at': 'Modified On'
#         }

#         field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())
#         queryset = ECAAwardingBody.objects.all()
#         if uuids:
#             queryset = queryset.filter(uuid__in=uuids)
#         queryset = queryset.order_by('-created_at')

#         dataset = Dataset()
#         dataset.headers = [field_header_map.get(f, f) for f in field_list]
#         dataset.title = 'ECA Awarding Body'

#         for eca in queryset:
#             row = []
#             for field in field_list:
#                 value = getattr(eca, field, '')
#                 if field == 'country' and eca.country:
#                     value = eca.country.name
#                 elif isinstance(value, bool):
#                     value = int(value)
#                 elif field in ['created_at', 'updated_at'] and value:
#                     value = timezone.localtime(value).strftime("%d-%m-%Y %I:%M:%S %p")
#                 row.append(value if value is not None else '')
#             dataset.append(row)

#         if format_type == 'csv':
#             file_data = dataset.export('csv')
#             content_type = 'text/csv'
#             file_name = 'eca_awarding_body.csv'
#         else:
#             file_data = io.BytesIO(dataset.export('xlsx'))
#             content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
#             file_name = 'eca_awarding_body.xlsx'

#         response = HttpResponse(
#             file_data if format_type == 'csv' else file_data.getvalue(),
#             content_type=content_type
#         )
#         response['Content-Disposition'] = f'attachment; filename="{file_name}"'
#         return response


class ECAAwardingBodyExportAPIView(APIView):
    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')

        # ----------------------------
        # Filters & Search
        # ----------------------------
        search = request.GET.get('search', '').strip()
        custom_sort = request.GET.get('customSort')


        # ----------------------------
        # Field headers
        # ----------------------------
        field_header_map = {
            'uuid': 'UUID',
            'country': 'Country',
            'ecafor': 'ECA For',
            'valid_duration_value': 'ECA Valid Duration',
            'eca_body_full_name': 'ECA Body Full Name',
            'eca_body_short_name': 'ECA Body Short Name',
            'eca_valid_period': 'ECA Valid Period',
            'description': 'Description',
            'created_at': 'Created On',
            'updated_at': 'Modified On'
        }

        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())


        # ---------------------------
        # Helper: Parse & Validate UUIDs
        # ---------------------------
        def parse_ids(param_name):
            raw = request.GET.get(param_name, '')
            if raw:
                items = [x.strip() for x in raw.split(',') if x.strip()]
            else:
                items = request.GET.getlist(param_name)
            return items

        def validate_uuid_list(uuid_list):
            valid = []
            for u in uuid_list:
                try:
                    valid.append(UUID(u))
                except:
                    pass
            return valid

        try:
            ecafor_list = validate_uuid_list(parse_ids('ecaFor'))
            country_list = validate_uuid_list(parse_ids('country'))
            uuids_list = validate_uuid_list(parse_ids('uuids'))
        except ValueError as e:
            return Response({
                "status": False,
                "statusCode": 400,
                "message": str(e)
            }, status=400)
        
        # ----------------------------
        # Base QuerySet
        # ----------------------------
        queryset = ECAAwardingBody.objects.all()

        if uuids_list:
            queryset = queryset.filter(uuid__in=uuids_list)
        if country_list:
            queryset = queryset.filter(country__uuid__in=country_list)
        if ecafor_list:
            queryset = queryset.filter(ecafor__uuid__in=ecafor_list)
        if search:
            queryset = queryset.filter(Q(eca_body_full_name__istartswith=search))

        # ----------------------------
        # Sorting
        # ----------------------------
        sort_field_map = {
            'uuid': 'uuid',
            'country': 'country__name',
            'ecaFor': 'ecafor__name',
            'eca_body_full_name': 'eca_body_full_name',
            'eca_body_short_name': 'eca_body_short_name',
            'eca_valid_period': 'eca_valid_period',
            'valid_duration_value': 'valid_duration_value',
            'description': 'description',
            'created_at': 'created_at',
            'updated_at': 'updated_at'
        }

        sort_fields = []
        annotations = {}

        if custom_sort:
            for idx, rule in enumerate(custom_sort.split(',')):
                try:
                    field, order = rule.split(':')
                    field = field.strip()
                    order = order.strip().lower()

                    if field not in sort_field_map:
                        return Response({
                            "status": False,
                            "statusCode": 400,
                            "message": f"Invalid sort field: {field}"
                        }, status=400)

                    orm_field = sort_field_map[field]

                    # Case-insensitive for string fields
                    if field in ['country', 'ecafor', 'eca_body_full_name', 'eca_body_short_name', 'eca_valid_period']:
                        ann_name = f"sort_key_{idx}"
                        annotations[ann_name] = Lower(orm_field)
                        sort_fields.append(ann_name if order == 'asc' else f"-{ann_name}")
                    else:
                        sort_fields.append(orm_field if order == 'asc' else f"-{orm_field}")

                except ValueError:
                    return Response({
                        "status": False,
                        "statusCode": 400,
                        "message": f"Invalid sorting rule format: {rule}"
                    }, status=400)

        # Apply annotations if needed
        if annotations:
            queryset = queryset.annotate(**annotations)

        if not sort_fields:
            sort_fields = ['-created_at']

        queryset = queryset.order_by(*sort_fields)

        # ----------------------------
        # Prepare Dataset
        # ----------------------------
        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'ECAAwardingBody'

        for eca in queryset:
            row = []
            for field in field_list:
                value = getattr(eca, field, '')
                if field == 'country' and eca.country:
                    value = eca.country.name
                elif field == 'ecafor' and eca.ecafor:
                    value = eca.ecafor.name
                elif field in ['created_at', 'updated_at'] and value:
                    value = timezone.localtime(value).strftime("%d-%m-%Y %I:%M:%S %p")
                elif isinstance(value, bool):
                    value = int(value)
                row.append(value if value is not None else '')
            dataset.append(row)

        # ----------------------------
        # Export File
        # ----------------------------
        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'eca_awarding_body.csv'
            response = HttpResponse(file_data, content_type=content_type)
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'eca_awarding_body.xlsx'
            response = HttpResponse(file_data.getvalue(), content_type=content_type)

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
                    skipped_rows.append({
                        "Row": row_number, 
                        "Eca Body Full Name": full_name or "",
                        "Eca Body Short Name":short_name or "",
                        "Country":country_name or "",
                        "Eca For":eca_for_name or "",
                        "Valid Duration Value":eca_valid_period or "",
                        "Reason": "Missing required field(s)"
                        })
                    continue

                # Country validation
                country = Country.objects.filter(name__iexact=country_name).first()
                if not country:
                    skipped_rows.append({"Row": row_number, 
                        "Eca Body Full Name": full_name or "",
                        "Eca Body Short Name":short_name or "",
                        "Country":country_name or "",
                        "Eca For":eca_for_name or "",
                        "Valid Duration Value":eca_valid_period or "",
                        "Reason": f'Country "{country_name}" not found'})
                    continue

                # ECAFor validation
                ecafor = ECAFor.objects.filter(name__iexact=eca_for_name).first()
                if not ecafor:
                    skipped_rows.append({"Row": row_number, 
                        "Eca Body Full Name": full_name or "",
                        "Eca Body Short Name":short_name or "",
                        "Country":country_name or "",
                        "Eca For":eca_for_name or "",
                        "Valid Duration Value":eca_valid_period or "",
                        "Reason": f'ECAFor "{eca_for_name}" not found'})
                    continue

      

                # Valid duration value validation
                if valid_duration_value is not None:
                    try:
                        valid_duration_value = int(valid_duration_value)
                        if valid_duration_value < 0:
                            raise ValueError
                    except:
                        skipped_rows.append({"Row": row_number, 
                        "Eca Body Full Name": full_name or "",
                        "Eca Body Short Name":short_name or "",
                        "Country":country_name or "",
                        "Eca For":eca_for_name or "",
                        "Valid Duration Value":eca_valid_period or "",
                        "Reason": 'Valid duration value must be a positive integer'})
                        continue

                # Duplicate check based on unique_together
                existing = ECAAwardingBody.objects.filter(
                    eca_body_full_name__iexact=full_name,
                    country=country,
                    ecafor=ecafor
                ).first()
                if existing:
                    # duplicate_names.append(full_name)
                    duplicate_names.append({"Row": row_number, 
                        "Eca Body Full Name": full_name or "",
                        "Eca Body Short Name":short_name or "",
                        "Country":country_name or "",
                        "Eca For":eca_for_name or "",
                        "Valid Duration Value":eca_valid_period or "",
                        "Reason": "Already exists in database"
                        })
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
            "duplicates": reversed(list(set(duplicate_names))),
            "skipped_rows": reversed(skipped_rows),
            "imported_count": imported_count,
            "message": "Import completed"
        })





# class DegreeAwardedByListAPIView(APIView):
#     def get(self, request):
#         search = request.GET.get('search', '').strip()
#         sort_by = request.GET.get('sortBy', 'created_at')
#         sort_order = request.GET.get('sortOrder', 'desc')
#         custom_sort = request.GET.get('customSort')
#         uuid_country = request.GET.get('country', '')
#         uuid_education_level = request.GET.get('education_level', '')

#         allowed_sort_fields = ['degree_name', 'created_at', 'updated_at']
#         if sort_by not in allowed_sort_fields:
#             sort_by = 'created_at'
#         if sort_order == 'desc':
#             sort_by = f'-{sort_by}'

#         queryset = DegreeAwardedBy.objects.all()
#         if search:
#             queryset = queryset.filter(
#                 Q(degree_name__istartswith=search)
#             )

#         queryset = queryset.order_by(sort_by)
#         paginator = CustomPagination()
#         result_page = paginator.paginate_queryset(queryset, request)
#         serializer = DegreeAwardedBySerializer(result_page, many=True)
#         return paginator.get_paginated_response(serializer.data)

class DegreeAwardedByListAPIView(APIView):
    def get(self, request):
        search = request.GET.get('search', '').strip()

        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')
        custom_sort = request.GET.get('customSort')

        uuid_country = request.GET.get('country', '')
        uuid_education_level = request.GET.get('education_level', '')

        # Allowed fields for normal sorting
        allowed_sort_fields = ['degree_name', 'created_at', 'updated_at']

        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        # -----------------------------------
        # Base Queryset
        # -----------------------------------
        queryset = DegreeAwardedBy.objects.select_related("country", "education_level")

        # -----------------------------------
        # Filters
        # -----------------------------------
        if search:
            queryset = queryset.filter(degree_name__istartswith=search)

        def parse_uuid_list(raw):
            valid = []
            if raw:
                for x in raw.split(','):
                    try:
                        valid.append(UUID(x.strip()))
                    except:
                        pass
            return valid

        # Filter by mainarea
        country_uuids = parse_uuid_list(uuid_country)
        if country_uuids:
            queryset = queryset.filter(country__uuid__in=country_uuids)

        # Filter by majorarea
        education_level_uuids = parse_uuid_list(uuid_education_level)
        if education_level_uuids:
            queryset = queryset.filter(education_level__uuid__in=education_level_uuids)

        # -----------------------------------
        # Custom Sorting (Advanced)
        # ----------------------------------
        if custom_sort:
            sort_fields = []

            from django.db.models.functions import Lower
            from django.db.models import F

            field_map = {
                "uuid": "uuid",
                "country": "country__name",
                "educationLevel": "education_level__educationlevel",
                "degree_name": "degree_name",
                "description": "description",
                "created_at": "created_at",
                "updated_at": "updated_at",
            }
            for rule in custom_sort.split(','):
                try:
                    field, order = rule.split(':')
                    field = field.strip()
                    order = order.strip().lower()

                    if field not in field_map:
                        continue

                    orm_field = field_map[field]

                    # Case-insensitive sorting for text fields
                    if field in ['degree_name', 'country', 'educationLevel', 'description']:
                        expression = Lower(orm_field)
                    else:
                        expression = F(orm_field)

                    sort_fields.append(
                        expression.asc(nulls_last=True)
                        if order == 'asc'
                        else expression.desc(nulls_last=True)
                    )
                except:
                    continue

            if sort_fields:
                queryset = queryset.order_by(*sort_fields)
        else:
            queryset = queryset.order_by(sort_by)

        # -----------------------------------
        # Pagination
        # -----------------------------------
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

# class DegreeAwardedByExportAPIView(APIView):
#     def get(self, request):
#         format_type = request.GET.get('format', 'xlsx').lower()
#         fields = request.GET.get('fields')
#         custom_sort = request.GET.get('customSort')
#         uuids_param = request.GET.get('uuids', '')
#         uuids = [u.strip() for u in uuids_param.split(',') if u]

#         # ------------------ Field Mapping ------------------
#         field_header_map = {
#             'uuid': 'UUID',
#             'country': 'Country',
#             'education_level_name': 'Education Level',
#             'degree_name': 'Degree Awarded By',
#             'description': 'Description',
#             'created_at': 'Created On',
#             'updated_at': 'Modified On'
#         }

#         # ------------------ Allowed Sorting Fields ------------------
#         allowed_sort_fields = {
#             "uuid": "uuid",
#             "country": "country__name",
#             "education_level_name": "education_level__educationlevel",
#             "degree_name": "degree_name",
#             "description": "description",
#             "created_at": "created_at",
#             "updated_at": "updated_at",
#         }

#         # ------------------ Dataset fields ------------------
#         field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())

#         # ------------------ Queryset ------------------
#         queryset = DegreeAwardedBy.objects.select_related("country", "education_level")

#         if uuids:
#             queryset = queryset.filter(uuid__in=uuids)

#         # ---------------------------
#         # ⭐ Custom Sorting (Same Logic as CountryListAPIView)
#         # ---------------------------
#         sort_fields = []

#         if custom_sort:
#             for rule in custom_sort.split(','):
#                 try:
#                     field, order = rule.split(':')
#                     field = field.strip()
#                     order = order.strip().lower()

#                     if field not in allowed_sort_fields:
#                         continue

#                     orm_field = allowed_sort_fields[field]

#                     # Case-insensitive sort for string fields
#                     string_fields = ["country", "education_level_name", "degree_name", "description"]
#                     is_string = field in string_fields

#                     if is_string:
#                         f = Lower(orm_field)
#                     else:
#                         f = F(orm_field)

#                     sort_fields.append(
#                         f.asc(nulls_last=True) if order == 'asc' else f.desc(nulls_last=True)
#                     )
#                 except ValueError:
#                     continue

#         else:
#             # default fallback
#             sort_fields = [F("created_at").desc(nulls_last=True)]

#         queryset = queryset.order_by(*sort_fields)

#         # ------------------ Export Data ------------------
#         dataset = Dataset()
#         dataset.headers = [field_header_map.get(f, f) for f in field_list]
#         dataset.title = 'DegreeAwardedBy'

#         for degree in queryset:
#             row = []
#             for field in field_list:
#                 value = getattr(degree, field, "")

#                 if field == "country":
#                     value = degree.country.name if degree.country else ""

#                 elif field == "education_level_name":
#                     value = degree.education_level.educationlevel if degree.education_level else ""

#                 elif field in ["created_at", "updated_at"] and value:
#                     value = value.strftime("%d-%m-%Y %I:%M:%S %p")

#                 elif isinstance(value, bool):
#                     value = int(value)

#                 row.append(value if value is not None else "")

#             dataset.append(row)

#         # ------------------ File Output ------------------
#         if format_type == 'csv':
#             file_data = dataset.export('csv')
#             content_type = 'text/csv'
#             file_name = 'degrees.csv'
#             response_data = file_data
#         else:
#             file_data = io.BytesIO(dataset.export('xlsx'))
#             content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
#             file_name = 'degrees.xlsx'
#             response_data = file_data.getvalue()

#         response = HttpResponse(response_data, content_type=content_type)
#         response['Content-Disposition'] = f'attachment; filename="{file_name}"'
#         return response



class DegreeAwardedByExportAPIView(APIView):

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        search = request.GET.get("search", "").strip()
        custom_sort = request.GET.get('customSort')

    
        # ------------------ Field Mapping ------------------
        field_header_map = {
            'uuid': 'UUID',
            'country': 'Country',
            'education_level_name': 'Education Level',
            'degree_name': 'Degree Awarded By',
            'description': 'Description',
            'created_at': 'Created On',
            'updated_at': 'Modified On'
        }

        # ------------------ Allowed Sorting Fields ------------------
        allowed_sort_fields = {
            "uuid": "uuid",
            "country": "country__name",
            "educationLevel": "education_level__educationlevel",
            "degree_name": "degree_name",
            "description": "description",
            "created_at": "created_at",
            "updated_at": "updated_at",
        }

        # Dataset Fields
        field_list = (
            [f.strip() for f in fields.split(',')]
            if fields else list(field_header_map.keys())
        )


        # ---------------------------
        # Helper: Parse & Validate UUIDs
        # ---------------------------
        def parse_ids(param_name):
            raw = request.GET.get(param_name, '')
            if raw:
                items = [x.strip() for x in raw.split(',') if x.strip()]
            else:
                items = request.GET.getlist(param_name)
            return items

        def validate_uuid_list(uuid_list):
            valid = []
            for u in uuid_list:
                try:
                    valid.append(UUID(u))
                except:
                    pass
            return valid

        try:
            country_list = validate_uuid_list(parse_ids('country'))
            education_level_list = validate_uuid_list(parse_ids('educationLevel'))
            uuids_list = validate_uuid_list(parse_ids('uuids'))
        except ValueError as e:
            return Response({
                "status": False,
                "statusCode": 400,
                "message": str(e)
            }, status=400)
        
        # ------------------ Queryset ------------------
        queryset = DegreeAwardedBy.objects.select_related("country", "education_level")

        # Filter: UUIDs

        if uuids_list:
            queryset = queryset.filter(uuid__in=uuids_list)

        if country_list:
            queryset = queryset.filter(country__uuid__in=country_list)

        if education_level_list:
            queryset = queryset.filter(education_level__uuid__in=education_level_list)


        # ------------------ Search Matching ------------------
        if search:
            queryset = queryset.filter(
                Q(degree_name__istartswith=search)
            )

        # ------------------ Custom Sort Logic ------------------
        sort_fields = []

        if custom_sort:
            for rule in custom_sort.split(','):
                try:
                    field, order = rule.split(':')
                    field = field.strip()
                    order = order.strip().lower()

                    if field not in allowed_sort_fields:
                        continue

                    orm_field = allowed_sort_fields[field]

                    # Case-insensitive for text fields
                    text_fields = ["country", "education_level_name", "degree_name", "description"]
                    is_text = field in text_fields

                    sort_expr = Lower(orm_field) if is_text else F(orm_field)

                    sort_fields.append(
                        sort_expr.asc(nulls_last=True) if order == "asc"
                        else sort_expr.desc(nulls_last=True)
                    )

                except ValueError:
                    continue
        else:
            # Default sorting
            sort_fields = [F("created_at").desc(nulls_last=True)]

        queryset = queryset.order_by(*sort_fields)

        # ------------------ Dataset ------------------
        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'DegreeAwardedBy'

        for obj in queryset:
            row = []
            for field in field_list:

                if field == "country":
                    value = obj.country.name if obj.country else ""

                elif field == "education_level_name":
                    value = (
                        obj.education_level.educationlevel
                        if obj.education_level else ""
                    )

                elif field in ["created_at", "updated_at"]:
                    value = (
                        obj.created_at.strftime("%d-%m-%Y %I:%M:%S %p")
                        if getattr(obj, field) else ""
                    )

                else:
                    value = getattr(obj, field, "")

                row.append(value if value is not None else "")

            dataset.append(row)

        # ------------------ Export ------------------
        if format_type == 'csv':
            file_data = dataset.export('csv')
            response = HttpResponse(file_data, content_type='text/csv')
            filename = "degree_awarded_by.csv"

        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            response = HttpResponse(
                file_data.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            filename = "degree_awarded_by.xlsx"

        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response



# -------------------- IMPORT API --------------------
# class DegreeAwardedByImportAPIView(APIView):
#     permission_classes = [IsAuthenticated, IsAdminUser]

#     def post(self, request):
#         file = request.FILES.get('file')
#         sheet_name = request.data.get('sheet_name', None)

#         if not file:
#             return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

#         format_type = file.name.split('.')[-1].lower()
#         imported_count = 0
#         skipped_rows = []
#         duplicate_rows = []

#         required_headers = {'degree awarded by', 'country', 'education level'}
#         optional_headers = {'description'}

#         try:
#             data = []

#             # ---------- XLSX ----------
#             if format_type == 'xlsx':
#                 wb = openpyxl.load_workbook(file, read_only=True)
#                 ws = wb[sheet_name] if sheet_name else wb.active
#                 headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]
#                 if not required_headers.issubset(set(headers)):
#                     return Response({'statusCode': 400, 'status': False, 'message': f'Missing required headers: {required_headers - set(headers)}'}, status=status.HTTP_400_BAD_REQUEST)
#                 for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
#                     if not any(row):
#                         continue
#                     row_dict = dict(zip(headers, row))
#                     row_dict['_row_number'] = idx
#                     data.append(row_dict)

#             # ---------- CSV ----------
#             elif format_type == 'csv':
#                 decoded_file = file.read().decode('utf-8')
#                 reader = csv.DictReader(io.StringIO(decoded_file))
#                 headers = [h.strip().lower() for h in reader.fieldnames]
#                 if not required_headers.issubset(set(headers)):
#                     return Response({'statusCode': 400, 'status': False, 'message': f'Missing required headers: {required_headers - set(headers)}'}, status=status.HTTP_400_BAD_REQUEST)
#                 for idx, row in enumerate(reader, start=2):
#                     row_lower = {k.strip().lower(): v for k, v in row.items()}
#                     row_lower['_row_number'] = idx
#                     data.append(row_lower)
#             else:
#                 return Response({'statusCode': 400, 'status': False, 'message': 'Unsupported file format'}, status=status.HTTP_400_BAD_REQUEST)

#             # ---------- Process Data ----------
#             for row in reversed(data):
#                 row_number = row.get('_row_number', 'Unknown')
#                 degree_name = str(row.get('degree awarded by')).strip() if row.get('degree awarded by') else None
#                 country_name = str(row.get('country')).strip() if row.get('country') else None
#                 education_level_name = str(row.get('education level')).strip() if row.get('education level') else None
#                 description = str(row.get('description') or '').strip()

#                 # Required fields check
#                 if not degree_name or not country_name or not education_level_name:
#                     skipped_rows.append({
#                         "Row": row_number,
#                         "Degree Awarded By": degree_name or "Unknown",
#                         "Country": country_name,
#                         "Education Level": education_level_name,
#                         "Reason": "Missing required field(s)"
#                     })
#                     continue

#                 # Foreign key validation
#                 country = Country.objects.filter(name__iexact=country_name).first()
#                 education_level = EducationLevel.objects.filter(educationlevel__iexact=education_level_name).first()
#                 if not country:
#                     skipped_rows.append({
#                         "Row": row_number,
#                         "Degree Awarded By": degree_name,
#                         "Country": country_name,
#                         "Education Level": education_level_name,
#                         "Reason": f'Country "{country_name}" not found'
#                     })
#                     continue
#                 if not education_level:
#                     skipped_rows.append({
#                         "Row": row_number,
#                         "Degree Awarded By": degree_name,
#                         "Country": country_name,
#                         "Education Level": education_level_name,
#                         "Reason": f'Education Level "{education_level_name}" not found'
#                     })
#                     continue

#                 # Duplicate check
#                 existing = DegreeAwardedBy.objects.filter(degree_name__iexact=degree_name, country=country, education_level=education_level).first()
#                 if existing:
#                     duplicate_rows.append({
#                         "Row": row_number,
#                         "Degree Awarded By": degree_name,
#                         "Country": country_name,
#                         "Education Level": education_level_name,
#                         "Reason": "Already exists"
#                     })
#                     continue

#                 # Create record
#                 DegreeAwardedBy.objects.create(
#                     degree_name=degree_name,
#                     country=country,
#                     education_level=education_level,
#                     description=description
#                 )
#                 imported_count += 1

#         except Exception as e:
#             return Response({'statusCode': 400, 'status': False, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

#         return Response({
#             "statusCode": 200,
#             "status": True,
#             "duplicates": duplicate_rows,
#             "skipped_rows": skipped_rows,
#             "imported_count": imported_count,
#             "message": "Import completed"
#         })


class DegreeAwardedByImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=400)

        format_type = file.name.split('.')[-1].lower()

        required_headers = {
            'country',
            'education level',
            'degree awarded by'
        }

        data = []
        skipped_rows = []
        duplicates = []
        imported_count = 0

        try:
            # =====================================================
            #                   READ EXCEL / CSV
            # =====================================================
            if format_type == "xlsx":
                import openpyxl
                wb = openpyxl.load_workbook(file, read_only=True)
                sheets = wb.sheetnames

                if not sheet_name:
                    return Response({"error": "Please provide sheet_name", "available_sheets": sheets}, status=400)

                if sheet_name not in sheets:
                    return Response({"error": f"Sheet '{sheet_name}' not found", "available_sheets": sheets}, status=400)

                ws = wb[sheet_name]
                headers = [
                    (cell.value or "").strip().lower()
                    for cell in next(ws.iter_rows(min_row=1, max_row=1))
                ]

                missing = required_headers - set(headers)
                if missing:
                    return Response({"error": f"Missing required headers: {missing}"}, status=400)

                for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    row_dict["_row_number"] = idx
                    data.append(row_dict)

            elif format_type == "csv":
                import csv, io
                decoded = file.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(decoded))

                headers = {h.strip().lower() for h in reader.fieldnames}

                missing = required_headers - headers
                if missing:
                    return Response({"error": f"Missing required headers: {missing}"}, status=400)

                for idx, row in enumerate(reader, start=2):
                    row_dict = {k.lower(): (v or "").strip() for k, v in row.items()}
                    row_dict["_row_number"] = idx
                    data.append(row_dict)
            else:
                return Response({"error": "Unsupported file format (.xlsx or .csv only)"}, status=400)

            # =====================================================
            #                PROCESS ROWS (same logic as EducationLevel)
            # =====================================================
            for row in data:
                row_no = row.get("_row_number")

                # country_name = row.get("country", "").strip()
                # edu_level_name = row.get("education level", "").strip()
                # degree_name = row.get("degree awarded by", "").strip()
                # description = row.get("description", "")
                country_name = str(row.get("country") or "").strip()
                edu_level_name = str(row.get("education level") or "").strip()
                degree_name = str(row.get("degree awarded by") or "").strip()
                description = str(row.get("description") or "").strip()

                # Required Fields
                if not country_name or not edu_level_name or not degree_name:
                    skipped_rows.append({
                        "Row": row_no,
                        "Reason": "Missing required fields",
                        "Country": country_name,
                        "Education Level": edu_level_name,
                        "Degree Name By": degree_name,
                    })
                    continue

                # ---------------------------------------------
                #            VALIDATE / CREATE COUNTRY
                # ---------------------------------------------
                country = Country.objects.filter(name__iexact=country_name).first()
                if not country:
                    skipped_rows.append({
                        "Row": row_no,
                        "Reason": f'Country "{country_name}" not found',
                        "Country": country_name
                    })
                    continue

                # ---------------------------------------------
                #      VALIDATE / CREATE Education Level
                # ---------------------------------------------
                edu_level = EducationLevel.objects.filter(educationlevel__iexact=edu_level_name).first()

                if not edu_level:
                    skipped_rows.append({
                        "Row": row_no,
                        "Reason": f'Education Level "{edu_level_name}" not found',
                        "Education Level": edu_level_name
                    })
                    continue

                # ---------------------------------------------
                #           DUPLICATE CHECK
                # ---------------------------------------------
                existing = DegreeAwardedBy.objects.filter(
                    country=country,
                    education_level=edu_level
                ).first()

                if existing:
                    duplicates.append({
                        "row": idx + 1,
                        "reason": f"Duplicate: combination of country '{country.name}' and education level '{edu_level.educationlevel}' already exists.",
                    })
                    continue

                #     continue


                # ---------------------------------------------
                #           CREATE NEW RECORD
                # ---------------------------------------------
                DegreeAwardedBy.objects.create(
                    country=country,
                    education_level=edu_level,
                    degree_name=degree_name,
                    description=description
                )
                imported_count += 1

        except Exception as e:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": str(e)
            }, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Import completed",
            "imported_count": imported_count,
            "duplicates": duplicates,
            "skipped_rows": skipped_rows
        })






        
# class DegreeAwardedInstituteListAPIView(APIView):
#     permission_classes = [IsAuthenticated, IsAdminUser]

#     def get(self, request):
#         search = request.GET.get('search', '').strip()
#         sort_by = request.GET.get('sortBy', 'created_at')
#         sort_order = request.GET.get('sortOrder', 'desc')

#         allowed_sort_fields = ['name', 'created_at', 'updated_at']
#         if sort_by not in allowed_sort_fields:
#             sort_by = 'created_at'
#         if sort_order == 'desc':
#             sort_by = f'-{sort_by}'

#         queryset = DegreeAwardedInstitute.objects.all()
#         if search:
#             queryset = queryset.filter(
#                 Q(name__istartswith=search) 
#             )

#         queryset = queryset.order_by(sort_by)
#         serializer = DegreeAwardedInstituteSerializer(queryset, many=True)
#         return Response({
#             "statusCode": 200,
#             "status": True,
#             "data": serializer.data
#         })



# class DegreeAwardedInstituteListAPIView(APIView):
#     permission_classes = [IsAuthenticated, IsAdminUser]

#     def get(self, request):
#         search = request.GET.get('search', '').strip()
#         sort_by = request.GET.get('sortBy', 'created_at')
#         sort_order = request.GET.get('sortOrder', 'desc')

#         # Filter parameters (can be comma-separated UUIDs)
#         country_param = request.GET.get('country', '')
#         state_param = request.GET.get('state', '')
#         education_level_param = request.GET.get('educationLevel', '')
#         degree_awarded_by_param = request.GET.get('degreeAwardedBy', '')

#         # -----------------------
#         # Allowed sort fields
#         # -----------------------
#         allowed_sort_fields = ['name', 'created_at', 'updated_at']
#         if sort_by not in allowed_sort_fields:
#             sort_by = 'created_at'
#         if sort_order == 'desc':
#             sort_by = f'-{sort_by}'

#         # -----------------------
#         # Initial queryset
#         # -----------------------
#         queryset = DegreeAwardedInstitute.objects.all()

#         # -----------------------
#         # Search filter
#         # -----------------------
#         if search:
#             queryset = queryset.filter(Q(name__istartswith=search))

#         # -----------------------
#         # UUID filters helper
#         # -----------------------
#         def parse_uuid_list(param):
#             uuids = []
#             for u in param.split(','):
#                 u = u.strip()
#                 if not u:
#                     continue
#                 try:
#                     uuids.append(UUID(u))
#                 except ValueError:
#                     pass
#             return uuids

#         # Apply filters
#         country_uuids = parse_uuid_list(country_param)
#         state_uuids = parse_uuid_list(state_param)
#         education_level_uuids = parse_uuid_list(education_level_param)
#         degree_awarded_by_uuids = parse_uuid_list(degree_awarded_by_param)

#         if country_uuids:
#             queryset = queryset.filter(country__uuid__in=country_uuids)
#         if state_uuids:
#             queryset = queryset.filter(state__uuid__in=state_uuids)
#         if education_level_uuids:
#             queryset = queryset.filter(education_level__uuid__in=education_level_uuids)
#         if degree_awarded_by_uuids:
#             queryset = queryset.filter(degree_awarded_by__uuid__in=degree_awarded_by_uuids)

#         # -----------------------
#         # Sorting
#         # -----------------------
#         queryset = queryset.order_by(sort_by)

#         # -----------------------
#         # Pagination
#         # -----------------------
#         paginator = CustomPagination()
#         result_page = paginator.paginate_queryset(queryset, request)
#         serializer = DegreeAwardedInstituteSerializer(result_page, many=True)

#         return paginator.get_paginated_response(serializer.data)

class DegreeAwardedInstituteListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')
        custom_sort = request.GET.get('customSort', '')  # e.g., "name:asc,created_at:desc"

        # Filter parameters (comma-separated UUIDs)
        country_param = request.GET.get('country', '')
        state_param = request.GET.get('state', '')
        education_level_param = request.GET.get('educationLevel', '')
        degree_awarded_by_param = request.GET.get('degreeAwardedBy', '')

        # -----------------------
        # Allowed sort fields mapping
        # -----------------------
        sort_field_map = {
            'name': 'name', 
            'created_at': 'created_at',
            'updated_at': 'updated_at',
            'country': 'country__name',
            'state': 'state__stateName',
            'educationLevel': 'education_level__educationlevel',
            'degreeAwardedBy': 'degree_awarded_by__degree_name',
            'description': 'description'
        }

        # -----------------------
        # Initial queryset
        # -----------------------
        queryset = DegreeAwardedInstitute.objects.all()

        # -----------------------
        # Search filter
        # -----------------------
        if search:
            queryset = queryset.filter(Q(name__istartswith=search))

        # -----------------------
        # UUID filters helper
        # -----------------------
        def parse_uuid_list(param):
            uuids = []
            for u in param.split(','):
                u = u.strip()
                if not u:
                    continue
                try:
                    uuids.append(UUID(u))
                except ValueError:
                    pass
            return uuids

        # Apply filters
        country_uuids = parse_uuid_list(country_param)
        state_uuids = parse_uuid_list(state_param)
        education_level_uuids = parse_uuid_list(education_level_param)
        degree_awarded_by_uuids = parse_uuid_list(degree_awarded_by_param)

        if country_uuids:
            queryset = queryset.filter(country__uuid__in=country_uuids)
        if state_uuids:
            queryset = queryset.filter(state__uuid__in=state_uuids)
        if education_level_uuids:
            queryset = queryset.filter(education_level__uuid__in=education_level_uuids)
        if degree_awarded_by_uuids:
            queryset = queryset.filter(degree_awarded_by__uuid__in=degree_awarded_by_uuids)

        # -----------------------
        # Custom Sort
        # -----------------------
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
                    if field in ['name', 'country', 'state', 'educationLevel', 'degreeAwardedBy', 'description']:
                        f = Lower(orm_field)
                    else:
                        f = F(orm_field)

                    sort_fields.append(
                        f.asc(nulls_last=True) if order == 'asc' else f.desc(nulls_last=True)
                    )
                except ValueError:
                    continue

        # -----------------------
        # Default sort if customSort not provided
        # -----------------------
        if not sort_fields:
            orm_field = sort_field_map.get(sort_by, 'created_at')
            f = F(orm_field)
            sort_fields = [
                f.asc(nulls_last=True) if sort_order.lower() == 'asc' else f.desc(nulls_last=True)
            ]

        # Apply sorting
        queryset = queryset.order_by(*sort_fields)

        # -----------------------
        # Pagination
        # -----------------------
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = DegreeAwardedInstituteSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)



# -------------------- CREATE API --------------------

class DegreeAwardedInstituteCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        try:
            # -------------------------
            # Validate UUID (if provided)
            # -------------------------
            uuid_value = request.data.get('uuid')
            if uuid_value:
                try:
                    request.data['uuid'] = UUID(uuid_value)
                except ValueError:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": "Invalid UUID format for 'uuid'."
                    }, status=status.HTTP_400_BAD_REQUEST)

            # -------------------------
            # Serializer validation
            # -------------------------
            serializer = DegreeAwardedInstituteSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "statusCode": 200,
                    "status": True,
                    "message": "Degree Awarded Institute created successfully.",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)

            # -------------------------
            # Serializer errors
            # -------------------------
            errors = []
            for field, field_errors in serializer.errors.items():
                for error in field_errors:
                    errors.append(f"{field}: {error}")

            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Validation error.",
                "errors": errors
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # -------------------------
            # Unexpected errors
            # -------------------------
            return Response({
                "statusCode": 500,
                "status": False,
                "message": "An unexpected error occurred while creating the Degree Awarded Institute.",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
# class DegreeAwardedInstituteExportAPIView(APIView):
#     permission_classes = [IsAuthenticated, IsAdminUser]

#     def get(self, request):
#         format_type = request.GET.get('format', 'xlsx').lower()
#         fields = request.GET.get('fields')
#         uuids_param = request.GET.get('uuids', '')
#         uuids = [u.strip() for u in uuids_param.split(',') if u]

#         field_header_map = {
#             'uuid': 'UUID',
#             'country': 'Country',
#             'state': 'State',
#             'education_level': 'Education Level',
#             'degree_awarded_by': 'Degree Awarded By',
#             'name': 'Degree Awarded Institute',
#             'description': 'Description',
#             'created_at': 'Created On',
#             'updated_at': 'Updated On'
#         }

#         field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())

#         queryset = DegreeAwardedInstitute.objects.all()
#         if uuids:
#             queryset = queryset.filter(uuid__in=uuids)
#         queryset = queryset.order_by('-created_at')

#         dataset = Dataset()
#         dataset.headers = [field_header_map.get(f, f) for f in field_list]
#         dataset.title = 'DegreeAwardedInstitute'

#         for obj in queryset:
#             row = []
#             for field in field_list:
#                 value = getattr(obj, field, '')
#                 if field in ['created_at', 'updated_at'] and value:
#                     value = value.strftime("%d-%m-%Y %I:%M:%S %p")
#                 elif field == 'country' and obj.country:
#                     value = obj.country.name
#                 elif field == 'state' and obj.state:
#                     value = obj.state.stateName
#                 elif field == 'education_level' and obj.education_level:
#                     value = obj.education_level.educationlevel
#                 elif field == 'degree_awarded_by' and obj.degree_awarded_by:
#                     value = obj.degree_awarded_by.degree_name
#                 elif isinstance(value, bool):
#                     value = int(value)
#                 row.append(value if value is not None else '')
#             dataset.append(row)

#         if format_type == 'csv':
#             file_data = dataset.export('csv')
#             content_type = 'text/csv'
#             file_name = 'degree_awarded_institutes.csv'
#         else:
#             file_data = io.BytesIO(dataset.export('xlsx'))
#             content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
#             file_name = 'degree_awarded_institutes.xlsx'

#         response = HttpResponse(
#             file_data if format_type == 'csv' else file_data.getvalue(),
#             content_type=content_type
#         )
#         response['Content-Disposition'] = f'attachment; filename="{file_name}"'
#         return response


class DegreeAwardedInstituteExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        search = request.GET.get("search", "").strip()
        custom_sort = request.GET.get('customSort')

        # ------------------ Field Mapping ------------------
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

        field_list = (
            [f.strip() for f in fields.split(',')]
            if fields else list(field_header_map.keys())
        )

        # ------------------ Allowed Sorting Fields ------------------
        allowed_sort_fields = {
            "uuid": "uuid",
            "country": "country__name",
            "state": "state__stateName",
            "educationLevel": "education_level__educationlevel",
            "degreeAwardedBy": "degree_awarded_by__degree_name",
            "name": "name",
            "description": "description",
            "created_at": "created_at",
            "updated_at": "updated_at",
        }

        # ------------------ Parse Helper ------------------
        def parse_ids(param_name):
            raw = request.GET.get(param_name, '')
            if raw:
                items = [x.strip() for x in raw.split(',') if x.strip()]
            else:
                items = request.GET.getlist(param_name)
            return items

        def validate_uuid_list(uuid_list):
            valid = []
            for u in uuid_list:
                try:
                    valid.append(UUID(u))
                except:
                    pass
            return valid

        try:
            uuids_list = validate_uuid_list(parse_ids("uuids"))
            country_list = validate_uuid_list(parse_ids("country"))
            state_list = validate_uuid_list(parse_ids("state"))
            education_level_list = validate_uuid_list(parse_ids("educationLevel"))
            degree_awarded_by_list = validate_uuid_list(parse_ids("degreeAwardedBy"))
        except ValueError as e:
            return Response({
                "status": False,
                "statusCode": 400,
                "message": f"Invalid UUID: {e}"
            }, status=400)

        # ------------------ Queryset ------------------
        queryset = DegreeAwardedInstitute.objects.select_related(
            "country", "state", "education_level", "degree_awarded_by"
        )

        if uuids_list:
            queryset = queryset.filter(uuid__in=uuids_list)

        if country_list:
            queryset = queryset.filter(country__uuid__in=country_list)

        if state_list:
            queryset = queryset.filter(state__uuid__in=state_list)

        if education_level_list:
            queryset = queryset.filter(education_level__uuid__in=education_level_list)

        if degree_awarded_by_list:
            queryset = queryset.filter(degree_awarded_by__uuid__in=degree_awarded_by_list)

        # ------------------ Search ------------------
        if search:
            queryset = queryset.filter(
                Q(name__istartswith=search)
            )

        # ------------------ Custom Sort ------------------
        sort_fields = []

        if custom_sort:
            for rule in custom_sort.split(','):
                try:
                    field, order = rule.split(':')
                    field = field.strip()
                    order = order.strip().lower()

                    if field not in allowed_sort_fields:
                        continue

                    orm_field = allowed_sort_fields[field]

                    text_fields = [
                        "country", "state", "educationLevel",
                        "degreeAwardedBy", "name", "description"
                    ]
                    is_text = field in text_fields

                    sort_expr = Lower(orm_field) if is_text else F(orm_field)

                    sort_fields.append(
                        sort_expr.asc(nulls_last=True) if order == "asc"
                        else sort_expr.desc(nulls_last=True)
                    )

                except ValueError:
                    continue
        else:
            sort_fields = [F("created_at").desc(nulls_last=True)]

        queryset = queryset.order_by(*sort_fields)

        # ------------------ Dataset ------------------
        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'DegreeAwardedInstitute'

        for obj in queryset:
            row = []
            for field in field_list:

                if field == "country":
                    value = obj.country.name if obj.country else ""

                elif field == "state":
                    value = obj.state.stateName if obj.state else ""

                elif field == "education_level":
                    value = (
                        obj.education_level.educationlevel
                        if obj.education_level else ""
                    )

                elif field == "degree_awarded_by":
                    value = (
                        obj.degree_awarded_by.degree_name
                        if obj.degree_awarded_by else ""
                    )

                elif field in ["created_at", "updated_at"]:
                    dt = getattr(obj, field)
                    value = dt.strftime("%d-%m-%Y %I:%M:%S %p") if dt else ""

                else:
                    value = getattr(obj, field, "")

                row.append(value if value is not None else "")

            dataset.append(row)

        # ------------------ Export File ------------------
        if format_type == 'csv':
            file_data = dataset.export('csv')
            response = HttpResponse(file_data, content_type='text/csv')
            filename = "degree_awarded_institute.csv"

        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            response = HttpResponse(
                file_data.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            filename = "degree_awarded_institute.xlsx"

        response['Content-Disposition'] = f'attachment; filename="{filename}"'
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
                row_number = row.get("_row_number", "")
                name = str(row.get('degree awarded institute')).strip() if row.get('degree awarded institute') else None
                degree_awarded_by_name = str(row.get('degree awarded by')).strip() if row.get('degree awarded by') else None
                description = str(row.get('description')).strip() if row.get('description') else ''
                country_name = str(row.get('country')).strip() if row.get('country') else None
                state_name = str(row.get('state')).strip() if row.get('state') else None
                education_level_name = str(row.get('education level')).strip() if row.get('education level') else None

                if not name or not degree_awarded_by_name:
                    skipped_rows.append({
                        'Row': row_number,
                        'name': name or "",
                        'Degree Awarded By': degree_awarded_by_name or "",
                        'Country': country_name or "",
                        'State': state_name or "",
                        'Education Level': education_level_name or "",
                        'Reason': 'Missing required field(s)'})
                    continue

                # Map DegreeAwardedBy
                degree_awarded_by = DegreeAwardedBy.objects.filter(degree_name__iexact=degree_awarded_by_name).first()
                if not degree_awarded_by:
                    skipped_rows.append({'Row': row_number,
                        'name': name or "",
                        'Degree Awarded By': degree_awarded_by_name or "",
                        'Country': country_name or "",
                        'State': state_name or "",
                        'Education Level': education_level_name or "",
                        'Reason': f'Degree Awarded By "{degree_awarded_by_name}" not found'})
                    continue

                # Map Country, State, Education Level
                country = Country.objects.filter(name__iexact=country_name).first() if country_name else None
                state = State.objects.filter(stateName__iexact=state_name).first() if state_name else None
                education_level = EducationLevel.objects.filter(educationlevel__iexact=education_level_name).first() if education_level_name else None

                # Check duplicate
                existing = DegreeAwardedInstitute.objects.filter(name__iexact=name, degree_awarded_by=degree_awarded_by).first()
                if existing:
                    duplicate_names.append({
                        'Row': row_number,
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
            # "duplicates": duplicate_names,  
            # "skipped_rows": skipped_rows,
            "duplicates": list(reversed(duplicate_names)),
            "skipped_rows": list(reversed(skipped_rows)),
            "imported_count": imported_count,
            "message": "Import successful"
        })
    

