from django.shortcuts import render
from  .models  import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import  *
from django.core.paginator import Paginator
from django.db.models import Q, F
from django.db.models.functions import Lower
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
import datetime
import pytz
from django.utils import timezone
import io
import csv
from django.db import DatabaseError, transaction, IntegrityError

india_tz = pytz.timezone('Asia/Kolkata')




class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_superuser)
    

# -------------------- Language CRUD--------------------
class LanguageCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        name = request.data.get('name', '').strip()
        if Language.objects.filter(name__iexact=name, is_deleted=False).exists():
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Language with this name already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = LanguageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Language created successfully",
                "data": serializer.data
            })

        return Response({
            "statusCode": 400,
            "status": False,
            "message": " ".join([m for msgs in serializer.errors.values() for m in msgs])
        }, status=status.HTTP_400_BAD_REQUEST)


class LanguageRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = Language.objects.get(uuid=uuid, is_deleted=False)
        except Language.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Language not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = LanguageSerializer(obj)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Language retrieved successfully",
            "data": serializer.data
        })


class LanguageUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = Language.objects.get(uuid=uuid, is_deleted=False)
        except Language.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Language not found"
            }, status=status.HTTP_404_NOT_FOUND)

        name = request.data.get('name', '').strip()
        if Language.objects.filter(name__iexact=name).exclude(uuid=uuid).exists():
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Language with this name already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = LanguageSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Language updated successfully",
                "data": serializer.data
            })

        return Response({
            "statusCode": 400,
            "status": False,
            "message": " ".join([m for msgs in serializer.errors.values() for m in msgs])
        }, status=status.HTTP_400_BAD_REQUEST)




class LanguageDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        ids = request.data.get("id", None)
        delete_all = request.data.get("deleteAll", False)
        search = request.GET.get("search", "").strip()

        queryset = Language.objects.filter(is_deleted=False)

        # ---------------------------------------------------
        # CASE 3: deleteAll = true AND search present → Search delete
        # ---------------------------------------------------
        if delete_all and search and (ids in [None, ""]):
            qs_search = queryset.filter(name__istartswith=search)
            count = qs_search.count()

            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No languages found matching this search filter",
                    "data": None
                }, status=404)

            try:
                with transaction.atomic():
                    qs_search.delete()
            except IntegrityError:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "You can't delete selected language(s) because they are used in child tables",
                    "data": None
                }, status=400)

            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"{count} language(s) deleted based on search filter",
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
                    "message": "No languages found to delete",
                    "data": None
                }, status=404)

            deleted, skipped = [], []

            for lang in qs_all:
                try:
                    with transaction.atomic():
                        lang.delete()
                    deleted.append(str(lang.uuid))
                except IntegrityError:
                    skipped.append(lang.name)

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
                    "message": "No matching languages found for given UUIDs",
                    "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
                }, status=404)

            try:
                with transaction.atomic():
                    qs_ids.delete()
            except IntegrityError:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "One or more language(s) are used in child tables, cannot delete.",
                    "data": None
                }, status=400)

            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"{count} language(s) deleted.",
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
    



class LanguageListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')  # default to newest first
        custom_sort = request.GET.get('customSort') #Custom Sorting

        allowed_sort_fields = ['name', 'description', 'created_at','updated_at']
        queryset = Language.objects.filter(is_deleted=False)

        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        
        #sorting
        sort_field_map = {
            'name': 'name',
            'description': 'description',
            'created_at': 'created_at',
            'updated_at': 'updated_at',
        }
        
        sort_fields = []

        if custom_sort:
            for rule in custom_sort.split(','):
                try:
                    field,order = rule.split(':')
                    field = field.strip()
                    order = order.strip().lower()
                    if field not in sort_field_map:
                        continue
                    orm_field = sort_field_map[field]
                    # Case-insensitive sorting for string fields
                    if field in ['name','description']:
                        f = Lower(orm_field)
                    else:
                        f = F(orm_field)
                    sort_fields.append(
                        f.asc(nulls_last=True) if order == 'asc' else f.desc(nulls_last=True)
                    )
                except ValueError:
                    continue
        else:
                # fallback sorting
                sort_by = request.GET.get('sortBy','created_at')
                sort_order = request.GET.get('sortOrder','asc')
                orm_field = sort_field_map.get(sort_by,'created_at')
                f = F(orm_field)
                sort_fields =  [f.asc(nulls_last=True) if sort_order == 'asc' else f.desc(nulls_last=True)]
        queryset = queryset.order_by(*sort_fields)
        print("SORT FIELDS:", sort_fields)



        # Apply descending order for 'desc'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

       # queryset = Language.objects.filter(is_deleted=False)  
        if search:
            queryset = queryset.filter(
                Q(name__istartswith=search) 
            )

       # queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = LanguageSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    



# class LanguageExportAPIView(APIView):
#     permission_classes = [IsAuthenticated, IsAdminUser]

#     def get(self, request):
#         # --- Get query params ---
#         format_type = request.GET.get('format', 'xlsx').lower()
#         fields = request.GET.get('fields')  # comma-separated fields
#         uuids_param = request.GET.get('uuids', '')  # comma-separated UUIDs

#         uuids = [u.strip() for u in uuids_param.split(',') if u]

#         # --- Field to header mapping ---
#         field_header_map = {
#             'uuid': 'UUID',
#             'name': 'Language Name (Test)',
#             'description': 'Description',
#             'is_deleted': 'Deleted',
#             'created_at': 'Created On',
#             'updated_at': 'Modified On',
#         }

#         # --- Determine fields to export ---
#         if fields:
#             field_list = [f.strip() for f in fields.split(',')]
#         else:
#             field_list = list(field_header_map.keys())

#         # --- Fetch queryset ---
#         queryset = Language.objects.all()
#         if uuids:
#             queryset = queryset.filter(uuid__in=uuids)
#         queryset = queryset.order_by('-created_at')

#         # --- Prepare dataset ---
#         dataset = Dataset()
#         dataset.headers = [field_header_map.get(f, f) for f in field_list]
#         dataset.title = 'Language Name(Test)'

#         for lang in queryset:
#             row = []
#             for field in field_list:
#                 value = getattr(lang, field, '')

#                 # Convert datetime to IST
#                 if field in ['created_at', 'updated_at'] and value:
#                     value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
#                 elif isinstance(value, bool):
#                     value = int(value)

#                 row.append(value if value is not None else '')
#             dataset.append(row)

#         # --- Export logic ---
#         if format_type == 'csv':
#             file_data = dataset.export('csv')
#             content_type = 'text/csv'
#             file_name = 'languages.csv'
#         else:
#             file_data = io.BytesIO(dataset.export('xlsx'))
#             content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
#             file_name = 'languages.xlsx'

#         # --- Return response ---
#         response = HttpResponse(
#             file_data if format_type == 'csv' else file_data.getvalue(),
#             content_type=content_type
#         )
#         response['Content-Disposition'] = f'attachment; filename="{file_name}"'
#         return response


class LanguageExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        # --- Get query params ---
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')  # comma-separated fields
        uuids_param = request.GET.get('uuids', '')  # comma-separated UUIDs
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')
        custom_sort = request.GET.get('customSort')
        
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        # --- Field to header mapping ---
        field_header_map = {
            'uuid': 'UUID',
            'name': 'Language Name (Test)',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'created_at': 'Created On',
            'updated_at': 'Modified On',
        }

        # --- Determine fields to export ---
        if fields:
            field_list = [f.strip() for f in fields.split(',')]
        else:
            field_list = list(field_header_map.keys())
        
         # --- Fetch queryset ---
        queryset = Language.objects.all()
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

       
        allowed_sort_fields = ['name', 'description', 'created_at', 'updated_at']
        queryset = Language.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(
                Q(name__istartswith=search) 
            )


         #sorting
        sort_field_map = {
            'name': 'name',
            'description': 'description',
            'created_at': 'created_at',
            'updated_at': 'updated_at',
        }
        sort_fields = []

        if custom_sort:
            for rule in custom_sort.split(','):
                try:
                    field,order = rule.split(':')
                    field = field.strip()
                    order = order.strip().lower()
                    if field not in sort_field_map:
                        continue
                    orm_field = sort_field_map[field]
                    # Case-insensitive sorting for string fields
                    if field in ['name','description']:
                        f = Lower(orm_field)
                    else:
                        f = F(orm_field)
                    sort_fields.append(
                        f.asc(nulls_last=True) if order == 'asc' else f.desc(nulls_last=True)
                    )
                except ValueError:
                    continue
        else:
                # fallback sorting
                sort_by = request.GET.get('sortBy','created_at')
                sort_order = request.GET.get('sortOrder','asc')
                orm_field = sort_field_map.get(sort_by,'created_at')
                f = F(orm_field)
                sort_fields =  [f.asc(nulls_last=True) if sort_order == 'asc' else f.desc(nulls_last=True)]
        queryset = queryset.order_by(*sort_fields)



        
       

        # --- Prepare dataset ---
        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'LanguageName(Test)'

        for lang in queryset:
            row = []
            for field in field_list:
                value = getattr(lang, field, '')

                # Convert datetime to IST
                if field in ['created_at', 'updated_at'] and value:
                    value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
                elif isinstance(value, bool):
                    value = int(value)

                row.append(value if value is not None else '')
            dataset.append(row)

        # --- Export logic ---
        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'languages.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'languages.xlsx'

        # --- Return response ---
        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


class LanguageImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()

        # Required & optional headers
        required_headers = {'language name (test)'}
        optional_headers = {'description', 'is_deleted'}

        data = []
        duplicates = []
        skipped_rows = []

        try:
            headers = []

            # ---------------------------------------------------------
            #                      XLSX Handling
            # ---------------------------------------------------------
            if format_type == 'xlsx':
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

                if ws.max_row <= 1:
                    return Response({
                        "status": False,
                        "statusCode": 400,
                        "message": f"Sheet '{sheet_name}' is empty."
                    }, status=400)

                headers = [
                    (cell.value or "").strip().lower()
                    for cell in next(ws.iter_rows(min_row=1, max_row=1))
                ]

                # Validate required headers
                missing = required_headers - set(headers)
                if missing:
                    return Response({
                        "status": False,
                        "statusCode": 400,
                        "message": f"Missing required headers: {missing}"
                    }, status=400)

                # Load row data
                for row_no, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    row_dict["_row_number"] = row_no
                    data.append(row_dict)

            # ---------------------------------------------------------
            #                       CSV Handling
            # ---------------------------------------------------------
            elif format_type == "csv":
                decoded = file.read().decode('utf-8')
                dataset = Dataset()
                dataset.load(decoded, format="csv")

                for idx, row in enumerate(dataset.dict, start=2):
                    row_lower = {k.lower(): v for k, v in row.items()}

                    missing = required_headers - set(row_lower.keys())
                    if missing:
                        return Response({
                            "status": False,
                            "statusCode": 400,
                            "message": f"Missing required headers: {missing}"
                        }, status=400)

                    row_lower["_row_number"] = idx
                    data.append(row_lower)

            else:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Unsupported file format. Use .xlsx or .csv"
                }, status=400)

            # ---------------------------------------------------------
            #                       PROCESS ROWS
            # ---------------------------------------------------------
            imported_count = 0

            for row in reversed(data):
                row_no = row.get("_row_number", "Unknown")

                name = (row.get("language name (test)") or "").strip()
                description = (row.get("description") or "").strip()
                is_deleted = row.get("is_deleted", False)

                # Missing language name
                if not name:
                    skipped_rows.append({
                        "Row": row_no,
                        "Language Name": "",
                        "Description": description,
                        "Reason": "Missing language name"
                    })
                    continue

                # Check if language already exists
                existing = Language.objects.filter(name__iexact=name).first()

                if existing:
                    if not existing.is_deleted:
                        duplicates.append({
                            "Row": row_no,
                            "Language Name": "",
                            "Description": description,
                            "Reason": "Already exists in database"
                        })
                        continue
                    
                    # Reactivate deleted record
                    existing.description = description
                    existing.is_deleted = False
                    existing.save()
                    imported_count += 1

                else:
                    # Create new
                    Language.objects.create(
                        name=name,
                        description=description,
                        is_deleted=is_deleted or False
                    )
                    imported_count += 1

        except Exception as e:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": str(e)
            }, status=400)

        # ---------------------------------------------------------
        #                        FINAL RESPONSE
        # ---------------------------------------------------------
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"Sheet '{sheet_name}' imported successfully" if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": list(reversed(duplicates)),
            "skipped_rows": list(reversed(skipped_rows)),
        }, status=200)



#--------------------language Test-------------------



# class LanguageTestListAPIView(APIView):
#     permission_classes = [IsAuthenticated, IsAdminUser]

#     def get(self, request):
#         search = request.GET.get('search', '').strip()
#         sort_by = request.GET.get('sortBy', 'created_at')
#         sort_order = request.GET.get('sortOrder', 'desc')
#         custom_sort = request.GET.get('customSort')
#         allowed_sort_fields = ['name', 'fullname', 'description', 'created_at','updated_at']
        
#         if sort_by not in allowed_sort_fields:
#             sort_by = 'created_at'
#         if sort_order == 'desc':
#             sort_by = f'-{sort_by}'
             
#         queryset = LanguageTest.objects.filter(is_deleted=False)

#         if search:
#             queryset = queryset.filter(
#                 Q(name__istartswith=search)
#             )

#         # sorting
#         sort_field_map = {
#             'name': 'name',
#             'fullname': 'fullname',
#             'description': 'description',
#             'created_at': 'created_at',
#             'updated_at': 'updated_at',
#         }
#         sort_fields = []
#         if custom_sort:
#             for rule in custom_sort.split(','):
#                 try:
#                     field,order = rule.split(':')
#                     field = field.strip()
#                     order = order.strip().lower()
#                     if field not in sort_field_map:
#                         continue
#                     orm_field = sort_field_map[field]

#                     if field in ['name','fullname','description']:
#                         f = Lower(orm_field)
#                     else:
#                         f = F(orm_field)
#                     sort_fields.append(
#                         f.asc(nulls_last=True) if order == 'asc' else f.desc(nulls_last=True)
#                     )
#                 except ValueError:
#                     continue
#         else:
#             sort_by = request.GET.get('sortBy','created_at')
#             sort_order = request.GET.get('sortOrder','asc')
#             orm_field = sort_field_map.get(sort_by , 'created_at')
#             f = F(orm_field)
#             sort_fields = [f.asc(nulls_last=True) if sort_order == 'asc' else f.desc(nulls_last=True)]
#         queryset = queryset.order_by(*sort_fields)
#         #queryset = queryset.order_by(sort_by)
#         paginator = CustomPagination()
#         result_page = paginator.paginate_queryset(queryset, request)
#         serializer = LanguageTestSerializer(result_page, many=True)
#         return paginator.get_paginated_response(serializer.data)


class LanguageTestListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        custom_sort = request.GET.get('customSort', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at').strip()
        sort_order = request.GET.get('sortOrder', 'desc').strip().lower()
        uuid_language_name_test = request.GET.get('languageNameTest', '').strip()

        queryset = LanguageTest.objects.filter(is_deleted=False)

        #  Safe UUID List Parser
        def parse_uuid_list(raw):
            valid = []
            if raw:
                for x in raw.split(','):
                    try:
                        valid.append(UUID(x.strip()))
                    except ValueError:
                        continue
            return valid

        #  FILTER → language UUID list
        language_test_uuids = parse_uuid_list(uuid_language_name_test)
        if language_test_uuids:
            queryset = queryset.filter(language__uuid__in=language_test_uuids)

        #  SEARCH
        if search:
            queryset = queryset.filter(
                Q(name__istartswith=search)
            )

        #  SORTING FIXED
        sort_field_map = {
            'languageNameTest': 'language__name',
            'languageTestName': 'name',
            'fullname': 'fullname',
            'description': 'description',
            'created_at': 'created_at',
            'updated_at': 'updated_at',
        }

        orm_field = sort_field_map.get(sort_by, 'created_at')

        # CASE 1 → Custom multi rule sort
        if custom_sort:
            sort_fields = []
            for rule in custom_sort.split(','):
                try:
                    field, order = rule.split(':')
                    field = field.strip()
                    order = order.strip().lower()
                    if field not in sort_field_map:
                        continue
                    mapped = sort_field_map[field]

                    if field in ['fullname', 'description', 'languageNameTest', 'languageTestName']:
                        expr = Lower(F(mapped))
                    else:
                        expr = F(mapped)

                    sort_fields.append(expr.asc(nulls_last=True) if order == 'asc' else expr.desc(nulls_last=True))

                except ValueError:
                    continue

            if sort_fields:
                queryset = queryset.order_by(*sort_fields)

        # CASE 2 → Normal sortBy + sortOrder
        else:
            sort_fields = []  #  Initialized to avoid crash

            if sort_by in ['name', 'fullname', 'description']:
                expr = Lower(F(orm_field))
            else:
                expr = F(orm_field)

            sort_fields.append(
                expr.asc(nulls_last=True) if sort_order == 'asc' else expr.desc(nulls_last=True)
            )

            queryset = queryset.order_by(*sort_fields)  #  Ordering applied here only

        #  Pagination
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = LanguageTestSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)




class LanguageTestCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        language_uuid = request.data.get('language')
        if not language_uuid:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Language UUID is required."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            language = Language.objects.get(uuid=language_uuid, is_deleted=False)
        except Language.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Language not found."
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = LanguageTestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(language=language)
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "LanguageTest created successfully",
                "data": serializer.data
            })

        return Response({
            "statusCode": 400,
            "status": False,
            "message": " ".join([m for msgs in serializer.errors.values() for m in msgs])
        }, status=status.HTTP_400_BAD_REQUEST)


# -------------------- RETRIEVE -------------------- #
class LanguageTestRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = LanguageTest.objects.get(uuid=uuid, is_deleted=False)
        except LanguageTest.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "LanguageTest not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = LanguageTestSerializer(obj)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "LanguageTest retrieved successfully",
            "data": serializer.data
        })


# -------------------- UPDATE -------------------- #
class LanguageTestUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = LanguageTest.objects.get(uuid=uuid, is_deleted=False)
        except LanguageTest.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "LanguageTest not found"
            }, status=status.HTTP_404_NOT_FOUND)

        language_uuid = request.data.get('language')
        language_instance = None
        if language_uuid:
            try:
                language_instance = Language.objects.get(uuid=language_uuid, is_deleted=False)
            except Language.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Language not found."
                }, status=status.HTTP_404_NOT_FOUND)

        serializer = LanguageTestSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(language=language_instance)  # <-- assign FK here
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "LanguageTest updated successfully",
                "data": serializer.data
            })

        return Response({
            "statusCode": 400,
            "status": False,
            "message": " ".join([m for msgs in serializer.errors.values() for m in msgs])
        }, status=status.HTTP_400_BAD_REQUEST)





class LanguageTestDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        try:
            # ---------- Query Params ----------
            search = request.GET.get("search", "").strip()
            language_name_test_param = request.GET.get("languageNameTest", "").strip()

            # ---------- Parse comma UUIDs ----------
            def parse_uuids(param):
                arr = []
                if param:
                    for u in param.split(","):
                        try:
                            arr.append(UUID(u.strip()))
                        except:
                            pass
                return arr

            language_name_test_uuids = parse_uuids(language_name_test_param)

            # ---------- Body Params ----------
            uuids_body = request.data.get("id", None)
            delete_all = request.data.get("deleteAll", False)

            # ---------- Base Queryset ----------
            queryset = LanguageTest.objects.filter(is_deleted=False)
            applied_filters = []

            # Apply search filter
            if search:
                queryset = queryset.filter(name__istartswith=search)
                applied_filters.append("search")

            # Apply languageNameTest filter
            if language_name_test_uuids:
                queryset = queryset.filter(language__uuid__in=language_name_test_uuids)
                applied_filters.append("languageNameTest")

            # ---------- Case 2: Full table delete when id=="all" & deleteAll:false & no filters ----------
            if not delete_all and uuids_body == "all" and not applied_filters and not language_name_test_uuids:
                queryset = LanguageTest.objects.filter(is_deleted=False)
                total = queryset.count()

                if total == 0:
                    return Response({
                        "statusCode": 404,
                        "status": False,
                        "message": "No records found to delete",
                        "data": None
                    }, status=404)

                try:
                    with transaction.atomic():
                        queryset.delete()
                except IntegrityError:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": "Full table can't be deleted, child reference exists.",
                        "data": None
                    }, status=400)

                return Response({
                    "statusCode": 200,
                    "status": True,
                    "message": f"All {total} LanguageTest record(s) permanently deleted",
                    "data": None
                })

            # ---------- Case 3: Delete list of UUIDs from body with filters if applied ----------
            if not delete_all and isinstance(uuids_body, list) and uuids_body:
                valid = []
                invalid = []
                for u in uuids_body:
                    try:
                        valid.append(UUID(u))
                    except:
                        invalid.append(u)

                if not valid:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": "No valid UUIDs provided.",
                        "data": {"invalid_uuids": invalid}
                    }, status=400)

                qs_delete = queryset.filter(uuid__in=valid)
                count = qs_delete.count()

                if count == 0:
                    return Response({
                        "statusCode": 404,
                        "status": False,
                        "message": "No matching records found",
                        "data": {"invalid_uuids": invalid} if invalid else None
                    }, status=404)

                try:
                    with transaction.atomic():
                        qs_delete.delete()
                except IntegrityError:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": "Can't delete selected dataset, child reference exists.",
                        "data": None
                    }, status=400)

                return Response({
                    "statusCode": 200,
                    "status": True,
                    "message": f"{count} LanguageTest record(s) deleted successfully",
                    "data": {"invalid_uuids": invalid} if invalid else None
                })

            # ---------- Case 4: deleteAll:true with filter only ----------
            if delete_all and applied_filters:
                count = queryset.count()
                if count == 0:
                    return Response({
                        "statusCode": 404,
                        "status": False,
                        "message": "No records found matching applied filters",
                        "data": None
                    }, status=404)

                try:
                    with transaction.atomic():
                        queryset.delete()
                except IntegrityError:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": "Filtered dataset can't be deleted, child reference exists",
                        "data": None
                    }, status=400)

                return Response({
                    "statusCode": 200,
                    "status": True,
                    "message": f"{count} record(s) deleted based on filter: {', '.join(applied_filters)}",
                    "data": None
                })

            # ---------- Case 5: deleteAll:true but no filters ----------
            if delete_all and not applied_filters:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "deleteAll:true requires at least one filter to delete",
                    "data": None
                }, status=400)

            # ---------- Final fallback ----------
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Invalid delete request combination",
                "data": None
            }, status=400)

        except Exception as e:
            return Response({
                "statusCode": 500,
                "status": False,
                "message": f"Internal server error: {str(e)}",
                "data": None
            }, status=500)
        


class LanguageTestExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
 
    def get(self, request):
        # --- Get query params ---
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')  # comma-separated fields
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')
        custom_sort = request.GET.get('customSort')
     
 
 
        # --- Field to header mapping ---
        field_header_map = {
            'uuid': 'UUID',
            'language': 'Language Name (Test)',
            'name': 'Language Test Name',
            'fullname': 'Language Test Full Name',
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
           
            languageNameTest_list = validate_uuid_list(parse_ids('languageNameTest'))
            uuids_list = validate_uuid_list(parse_ids('uuids'))
        except ValueError as e:
            return Response({
                "status": False,
                "statusCode": 400,
                "message": str(e)
            }, status=400)
 
        # --- Fetch queryset ---
        queryset = LanguageTest.objects.filter(is_deleted=False)

        if uuids_list:
            queryset = queryset.filter(uuid__in=uuids_list)

        if languageNameTest_list:
            queryset = queryset.filter(language__uuid__in=languageNameTest_list) 

        #searching
        if search:
            queryset = queryset.filter(Q(name__istartswith=search))
            
        sort_field_map = {
            'languageNameTest': 'language__name',
            'languageTestName': 'name',
            'fullname': 'fullname',
            'description': 'description',
            'created_at': 'created_at',
            'updated_at': 'updated_at',
        }

        sort_fields = []
        if custom_sort:
            for rule in custom_sort.split(','):
                try:
                    field,order = rule.split(':')
                    field = field.strip()
                    order = order.strip().lower()
 
                    if field not in sort_field_map:
                        continue
 
                    orm_field = sort_field_map[field]
                    if field in ['languageTestName','fullname','description']:
                        f = Lower(orm_field)
                    elif field == 'languageNameTest':
                        f = Lower('language__name')
                    else:
                        f = F(orm_field)
                    
                    sort_fields.append(
                        f.asc(nulls_last=True) if order == 'asc' else f.desc(nulls_last=True)
                    )
                except ValueError:
                    continue
        else:
             sort_by = request.GET.get('sortBy','created_at')
             sort_order = request.GET.get('sortOrder','asc')
             orm_field = sort_field_map.get(sort_by,'created_at')
             f = F(orm_field)
             sort_fields =  [f.asc(nulls_last=True) if sort_order == 'asc' else f.desc(nulls_last=True)]
 
        queryset = queryset.order_by(*sort_fields)
 
                    
        # --- Prepare dataset ---
        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'LanguageTest'
 
        for obj in queryset:
            row = []
            for field in field_list:
                value = getattr(obj, field, '')
 
                # Special handling for language FK
                if field == 'language' and obj.language:
                    value = obj.language.name
 
                # Convert datetime to IST
                elif field in ['created_at', 'updated_at'] and value:
                    value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
 
                # Boolean to int
                elif isinstance(value, bool):
                    value = int(value)
 
                row.append(value if value is not None else '')
 
            dataset.append(row)
 
        # --- Export logic ---
        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'language_tests.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'language_tests.xlsx'
 
        # --- Return response ---
        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response
    

class LanguageTestImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicate_rows = []
        skipped_rows = []

        required_headers = {'language name (test)', 'language test name'}
        optional_headers = {'language test full name', 'description', 'is_deleted'}

        try:
            data = []
            headers = []

            # ---------------- XLSX Handling ----------------
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

                for row_no, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    row_dict["_row_number"] = row_no
                    data.append(row_dict)

            # ---------------- CSV Handling ----------------
            elif format_type == 'csv':
                decoded_file = file.read().decode('utf-8')
                dataset = Dataset()
                dataset.load(decoded_file, format='csv')

                for idx, row in enumerate(dataset.dict, start=2):
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({
                            "statusCode": 400,
                            "status": False,
                            "message": f'Missing required headers. Required: {required_headers}, Found: {set(row_lower.keys())}'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    row_lower["_row_number"] = idx
                    data.append(row_lower)
            else:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": 'Unsupported file format. Use .xlsx or .csv'
                }, status=status.HTTP_400_BAD_REQUEST)

            # ---------------- PROCESS ROWS ----------------
            imported_count = 0

            for row in reversed(data):
                row_no = row.get("_row_number", "Unknown")
                lang_name = str(row.get('language name (test)')).strip() if row.get('language name (test)') else ''
                test_name = str(row.get('language test name')).strip() if row.get('language test name') else ''
                fullname = str(row.get('language test full name')).strip() if row.get('language test full name') else ''
                description = str(row.get('description')).strip() if row.get('description') else ''
                is_deleted = row.get('is_deleted', False)

                if not lang_name:
                    skipped_rows.append({
                        "Row": row_no,
                        "Language Name (Test)": lang_name or "",
                        "Language Test Full Name":fullname or "",
                        "Language Test Name": test_name or "",
                        "Description":description or "",
                        "Is_deleted":is_deleted or False,
                        "Reason": "Missing parent language name"
                    })
                    continue

                if not test_name:
                    skipped_rows.append({
                        "Row": row_no,
                        "Language Name (Test)": lang_name or "",
                        "Language Test Full Name":fullname or "",
                        "Language Test Name": test_name or "",
                        "Description":description or "",
                        "Is_deleted":is_deleted or False,
                        "Reason": "Missing language test name"
                    })
                    continue

                # Check parent language exists
                language = Language.objects.filter(name__iexact=lang_name, is_deleted=False).first()
                if not language:
                    skipped_rows.append({
                        "Row": row_no,
                        "Language Name (Test)": lang_name or "",
                        "Language Test Full Name":fullname or "",
                        "Language Test Name": test_name or "",
                        "Description":description or "",
                        "Is_deleted":is_deleted or False,
                        "Reason": "Parent language not found or deleted"
                    })
                    continue

                # Check duplicate LanguageTest
                existing = LanguageTest.objects.filter(name__iexact=test_name, language=language).first()
                if existing:
                    duplicate_rows.append({
                        "Row": row_no,
                        "Language Name (Test)": lang_name or "",
                        "Language Test Full Name":fullname or "",
                        "Language Test Name": test_name or "",
                        "Description":description or "",
                        "Is_deleted":is_deleted or False,
                        "Reason": "Duplicate language test"
                    })
                    continue

                # ---------- Create ----------
                LanguageTest.objects.create(
                    language=language,
                    name=test_name,
                    fullname=fullname,
                    description=description,
                    is_deleted=is_deleted or False
                )
                imported_count += 1

        except Exception as e:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        # ---------------- FINAL RESPONSE ----------------
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": list(reversed(duplicate_rows)),
            "skipped_rows": list(reversed(skipped_rows))
        }, status=status.HTTP_200_OK)




# class LanguagetestmoduleNameListAPIView(APIView):
#     permission_classes = [IsAuthenticated, IsAdminUser]

#     def get(self, request):
#         search = request.GET.get('search', '').strip()
#         sort_by = request.GET.get('sortBy', 'created_at')
#         sort_order = request.GET.get('sortOrder', 'desc')
#         allowed_sort_fields = ['name', 'description', 'created_at']

#         if sort_by not in allowed_sort_fields:
#             sort_by = 'created_at'
#         if sort_order == 'desc':
#             sort_by = f'-{sort_by}'

#         queryset = LanguagetestmoduleName.objects.filter(is_deleted=False)
#         if search:
#             queryset = queryset.filter(
#                 Q(name__istartswith=search) |
#                 Q(description__istartswith=search)
#             )

#         queryset = queryset.order_by(sort_by)
#         paginator = CustomPagination()
#         result_page = paginator.paginate_queryset(queryset, request)
#         serializer = LanguagetestmoduleNameSerializer(result_page, many=True)
#         return paginator.get_paginated_response(serializer.data)


class LanguagetestmoduleNameListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')
        custom_sort = request.GET.get('customSort')
        allowed_sort_fields = ['name', 'description', 'created_at','updated_at']

        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = LanguagetestmoduleName.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(
                Q(name__istartswith=search)
            )

        #sorting
        sort_field_map = {
            'name': 'name',
            'description': 'description',
            'created_at': 'created_at',
            'updated_at': 'updated_at',
        }
        sort_fields = []
        if custom_sort:
            for ruls in custom_sort.split(','):
                try:
                    field,order = ruls.split(':')
                    field = field.strip()
                    order = order.strip().lower()

                    if field not in sort_field_map:
                        continue
                    orm_field = sort_field_map[field]
                    #case insensitive sorting
                    if field in ['name','description']:
                        f = Lower(orm_field)
                    else:
                        f = F(orm_field)
                    sort_fields.append(
                        f.asc(nulls_last=True) if order == 'asc' else f.desc(nulls_last=True)
                    )
                except ValueError:
                    continue
        else:
            #fallback sorting
             sort_by = request.GET.get('sortBy', 'created_at')
             sort_order = request.GET.get('sortOrder', 'asc')
             orm_field = sort_field_map.get(sort_by, 'created_at')
             f = F(orm_field)
             sort_fields = [f.asc(nulls_last=True) if sort_order == 'asc' else f.desc(nulls_last=True)]

        queryset =queryset.order_by(*sort_fields)

        
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = LanguagetestmoduleNameSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    


class LanguagetestmoduleNameCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        name = request.data.get("name", "").strip()
        existing = LanguagetestmoduleName.objects.filter(name__iexact=name, is_deleted=False).first()
        if existing:
            return Response({"statusCode": 400, "status": False, "message": "Module with this name already exists."}, status=400)

        serializer = LanguagetestmoduleNameSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"statusCode": 200, "status": True, "message": "Module created successfully", "data": serializer.data})
        else:
            errors = " ".join([msg for msgs in serializer.errors.values() for msg in msgs])
            return Response({"statusCode": 400, "status": False, "message": errors}, status=400)


class LanguagetestmoduleNameRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = LanguagetestmoduleName.objects.get(uuid=uuid, is_deleted=False)
        except LanguagetestmoduleName.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "Not found", "data": None}, status=404)
        serializer = LanguagetestmoduleNameSerializer(obj)
        return Response({"statusCode": 200, "status": True, "message": "Retrieved successfully", "data": serializer.data})


class LanguagetestmoduleNameUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = LanguagetestmoduleName.objects.get(uuid=uuid, is_deleted=False)
        except LanguagetestmoduleName.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Module not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = LanguagetestmoduleNameSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Module updated successfully",
                "data": serializer.data
            })
        return Response({
            "statusCode": 400,
            "status": False,
            "message": " ".join([m for msgs in serializer.errors.values() for m in msgs])
        }, status=status.HTTP_400_BAD_REQUEST)



# class LanguagetestmoduleNameDeleteAPIView(APIView):
#     permission_classes = [IsAuthenticated, IsAdminUser]

#     def delete(self, request, uuid=None):
#         uuids = request.data.get('id', None)

#         if uuid:
#             try:
#                 obj = LanguagetestmoduleName.objects.get(uuid=uuid, is_deleted=False)
#                 obj.delete()
#                 return Response({
#                     "statusCode": 204,
#                     "status": True,
#                     "message": "Module deleted successfully",
#                     "data": None
#                 }, status=status.HTTP_204_NO_CONTENT)
#             except LanguagetestmoduleName.DoesNotExist:
#                 return Response({
#                     "statusCode": 404,
#                     "status": False,
#                     "message": "Module not found",
#                     "data": None
#                 }, status=status.HTTP_404_NOT_FOUND)

#         if uuids == "all":
#             objs = LanguagetestmoduleName.objects.filter(is_deleted=False)
#             count = objs.count()
#             if count == 0:
#                 return Response({
#                     "statusCode": 404,
#                     "status": False,
#                     "message": "No records found to delete.",
#                     "data": None
#                 }, status=status.HTTP_404_NOT_FOUND)
#             objs.delete()
#             return Response({
#                 "statusCode": 200,
#                 "status": True,
#                 "message": f"All {count} records deleted successfully.",
#                 "data": None
#             }, status=status.HTTP_200_OK)

#         if not uuids or not isinstance(uuids, list):
#             return Response({
#                 "statusCode": 400,
#                 "status": False,
#                 "message": "Provide a list of UUIDs in 'id' field or 'all'.",
#                 "data": None
#             }, status=status.HTTP_400_BAD_REQUEST)

#         valid_uuids = []
#         invalid_uuids = []
#         for u in uuids:
#             try:
#                 valid_uuids.append(UUID(u))
#             except ValueError:
#                 invalid_uuids.append(u)

#         objs = LanguagetestmoduleName.objects.filter(uuid__in=valid_uuids, is_deleted=False)
#         count = objs.count()
#         if count == 0:
#             return Response({
#                 "statusCode": 404,
#                 "status": False,
#                 "message": "No matching records found.",
#                 "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
#             }, status=status.HTTP_404_NOT_FOUND)

#         objs.delete()
#         return Response({
#             "statusCode": 200,
#             "status": True,
#             "message": f"{count} record(s) deleted successfully.",
#             "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
#         }, status=status.HTTP_200_OK)


class LanguagetestmoduleNameDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get("id", None)
        delete_all = request.data.get("deleteAll", False)
        search = request.GET.get("search", "").strip()

        queryset = LanguagetestmoduleName.objects.filter(is_deleted=False)

        # ---------------------------------------------------
        # CASE 3: deleteAll = true AND search present → Search delete
        # ---------------------------------------------------
        if delete_all and search and (ids in [None, ""]):
            qs_search = queryset.filter(name__istartswith=search)
            count = qs_search.count()

            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No modules match this search filter",
                    "data": None
                }, status=404)

            try:
                with transaction.atomic():
                    qs_search.delete()
            except IntegrityError:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Module(s) cannot be deleted because they are used in child tables",
                    "data": None
                }, status=400)

            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"{count} module(s) deleted based on search filter",
                "data": None
            }, status=200)

        # ---------------------------------------------------
        # CASE 2: deleteAll = false AND id = "all" → Delete everything
        # ---------------------------------------------------
        if ids == "all" and delete_all is False and search == "":
            qs_all = queryset
            count = qs_all.count()

            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No modules found to delete.",
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
                "message": f"{len(deleted)} deleted, {len(skipped)} skipped."
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
                    "message": "No valid UUIDs provided",
                    "data": {"invalid_uuids": invalid_uuids}
                }, status=400)

            qs_ids = queryset.filter(uuid__in=valid_uuids)
            count = qs_ids.count()

            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No matching records found",
                    "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
                }, status=404)

            try:
                with transaction.atomic():
                    qs_ids.delete()
            except IntegrityError:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "One or more module(s) are used in child tables, cannot delete",
                    "data": None
                }, status=400)

            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"{count} module(s) deleted",
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



  


class LanguagetestmoduleNameExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        custom_sort = request.GET.get('customSort')
        search = request.GET.get('search','').strip()

        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'name': 'Language Test Module Name',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'created_at': 'Created On',
            'updated_at': 'Modified On',
        }

        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())

        queryset = LanguagetestmoduleName.objects.all()
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        # allowed_sort_fields = ['name','description', 'created_at', 'updated_at']
        # queryset = LanguageTest.objects.filter(is_deleted=False)

        #searching
        if search:
            queryset = queryset.filter(name__istartswith=search)

        # custom_sorting login----------->
        sort_field_map = {
            'name': 'name',
            'description': 'description',
            'created_at': 'created_at',
            'updated_at':'updated_at',
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
                    # case -insensitive sorting for string field
                    if field in ['name','description']:
                        f = Lower(orm_field)
                    else:
                        f = F(orm_field)

                    sort_fields.append(
                        f.asc(nulls_last=True) if order == 'asc' else f.desc(nulls_last=True)
                    )
                 except ValueError:
                      continue
        else:
             sort_by = request.GET.get('sortBy','created_at')
             sort_order = request.GET.get('sortOrder','asc')
             orm_field = sort_field_map.get(sort_by,'created_at')
             f = F(orm_field)
             sort_fields =  [f.asc(nulls_last=True) if sort_order == 'asc' else f.desc(nulls_last=True)]

        queryset = queryset.order_by(*sort_fields)
        
        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'LanguagetestmoduleName'

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
            file_name = 'modules.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'modules.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response





class LanguagetestmoduleNameImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicate_names = []

        # Required & optional headers
        required_headers = {'language test module name'}
        optional_headers = {'description', 'is_deleted'}

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
                            "status": False,
                            "message": f'Missing required headers. Required: {required_headers}, Found: {set(row_lower.keys())}'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    data.append(row_lower)
            else:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": 'Unsupported file format. Use .xlsx or .csv'
                }, status=status.HTTP_400_BAD_REQUEST)

            imported_count = 0

            # ---------- Import Rows ----------
            for row in reversed(data):
                name = str(row.get('language test module name')).strip() if row.get('language test module name') else None
                description = str(row.get('description')).strip() if row.get('description') else ''
                is_deleted = row.get('is_deleted', False)

                if not name:
                    continue

                existing = LanguagetestmoduleName.objects.filter(name__iexact=name).first()

                if existing:
                    duplicate_names.append(name)
                    continue
                else:
                    LanguagetestmoduleName.objects.create(
                        name=name,
                        description=description,
                        is_deleted=is_deleted or False
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




# -------------------- List -------------------- #

# class LanguageTestResultListAPIView(APIView):
#     permission_classes = [IsAuthenticated, IsAdminUser]

#     def get(self, request):
#         search = request.GET.get('search', '').strip()
#         custom_sort = request.GET.get('customSort')
#         sort_by = request.GET.get('sortBy', 'created_at')
#         sort_order = request.GET.get('sortOrder', 'desc')

#         # ---------------------------------------------------
#         # Helper: Parse UUID list safely
#         # ---------------------------------------------------
#         def parse_uuid_list(param):
#             raw = request.GET.get(param, '')
#             final_list = []
#             if raw:
#                 for x in raw.split(','):
#                     try:
#                         final_list.append(UUID(x.strip()))
#                     except:
#                         pass
#             return final_list

#         # ---------------------------------------------------
#         # Filters (UUID and text-based)
#         # ---------------------------------------------------
#         language_test_ids = parse_uuid_list('languageNameTest')
#         benchmark_level_ids = parse_uuid_list('languageBenchmarkLevel')
#         uuids_list = parse_uuid_list('uuids')

#         language_test_names = parse_uuid_list('languageTestName')
#         language_module_names = parse_uuid_list('languageModuleName')

#         queryset = LanguageTestResult.objects.filter(is_deleted=False)

#         # ---------------------------------------------------
#         # Apply filters
#         # ---------------------------------------------------
#         if uuids_list:
#             queryset = queryset.filter(uuid__in=uuids_list)

#         if language_test_ids:
#             queryset = queryset.filter(language__uuid__in=language_test_ids)

#         if benchmark_level_ids:
#             queryset = queryset.filter(lb_level__uuid__in=benchmark_level_ids)

#         if language_test_names:
#             queryset = queryset.filter(language_test__uuid__in=language_test_names)

#         if language_module_names:
#             queryset = queryset.filter(module_name__uuid__in=language_module_names)

#         # ---------------------------------------------------
#         # SEARCH block
#         # ---------------------------------------------------
#         if search:
#             queryset = queryset.filter(
#                 Q(numeric_score__istartswith=search)
#             )

#         # ---------------------------------------------------
#         # Sorting Map
#         # ---------------------------------------------------
#         sort_field_map = {
#             "numeric_score": "numeric_score",
#             "description": "description",
#             "languageTestName": "language_test__name",
#             "languageModuleName": "languagetest_module_name__moduleName",
#             "languageBenchmarkLevel": "languagetestbenchmark_level__level_name",
#             "created_at": "created_at",
#             "updated_at": "updated_at",
#         }

#         allowed_sort_fields = list(sort_field_map.keys())
#         sort_fields = []

#         # ---------------------------------------------------
#         # CUSTOM SORT (like field:asc,field2:desc)
#         # ---------------------------------------------------
#         if custom_sort:
#             for rule in custom_sort.split(","):
#                 try:
#                     field, order = rule.split(":")
#                     field = field.strip()
#                     order = order.strip().lower()

#                     if field not in sort_field_map:
#                         continue

#                     orm_field = sort_field_map[field]

#                     # Case-insensitive for text sorting
#                     if field in [
#                         "numeric_score",
#                         "description",
#                         "languageTestName",
#                         "languageModuleName",
#                         "languageBenchmarkLevel"
#                     ]:
#                         f = Lower(orm_field)
#                     else:
#                         f = F(orm_field)

#                     sort_fields.append(
#                         f.asc(nulls_last=True)
#                         if order == "asc" else f.desc(nulls_last=True)
#                     )

#                 except ValueError:
#                     continue

#         else:
#             # ---------------------------------------------------
#             # DEFAULT SORT
#             # ---------------------------------------------------
#             if sort_by not in allowed_sort_fields:
#                 sort_by = "created_at"

#             orm_field = sort_field_map.get(sort_by, "created_at")
#             f = F(orm_field)

#             sort_fields = [
#                 f.asc(nulls_last=True) if sort_order == "asc" else f.desc(nulls_last=True)
#             ]

#         queryset = queryset.order_by(*sort_fields)

#         # ---------------------------------------------------
#         # Pagination + Serialization
#         # ---------------------------------------------------
#         paginator = CustomPagination()
#         result_page = paginator.paginate_queryset(queryset, request)
#         serializer = LanguageTestResultSerializer(result_page, many=True)

#         return paginator.get_paginated_response(serializer.data)


class LanguageTestResultListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        custom_sort = request.GET.get('customSort')
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        uuid_languageNameTest = request.GET.get('languageNameTest', '')
        uuid_languageTestName = request.GET.get('languageTestName', '')
        uuid_languageModuleName = request.GET.get('languageModuleName', '')
        uuid_languageBanchMarkLevel = request.GET.get('languageBanchMarkLevel', '')

        queryset = LanguageTestResult.objects.all()

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

        languageNameTest_name_list = parse_uuid_list(uuid_languageNameTest)
        languageTestName_name_list = parse_uuid_list(uuid_languageTestName)
        languageModuleName_name_list = parse_uuid_list(uuid_languageModuleName)
        languageBanchMarkLevel_name_list = parse_uuid_list(uuid_languageBanchMarkLevel)

        if languageNameTest_name_list:
            queryset = queryset.filter(language__uuid__in=languageNameTest_name_list)

        if languageTestName_name_list:
            queryset = queryset.filter(language_test__uuid__in=languageTestName_name_list)

        if languageModuleName_name_list:
            queryset = queryset.filter(module_name__uuid__in=languageModuleName_name_list)

        if languageBanchMarkLevel_name_list:
            queryset = queryset.filter(lb_level__uuid__in=languageBanchMarkLevel_name_list)

        # ----------------------
        # SEARCH FILTER
        # ----------------------
        if search:
            queryset = queryset.filter(numeric_score__istartswith=search)

        # ----------------------
        # SORT FIELD MAP
        # ----------------------
        sort_field_map = {
            "languageNameTest": "language__name",
            "languageTestName": "language_test__name",
            "languageModuleName": "module_name__name",
            "languageBanchMarkLevel": "lb_level__name",
            "numeric_score": "numeric_score",
            "description": "description",
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
                    if field in ["languageNameTest", "languageTestName", "languageModuleName", "description"]:
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
        serializer = LanguageTestResultSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)
    




# -------------------- Create -------------------- #
class LanguageTestResultCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        # Get UUIDs
        language_uuid = request.data.get("language_id")
        language_test_uuid = request.data.get("language_test_id")
        module_uuid = request.data.get("module_name_id")
        lb_uuid = request.data.get("lb_level_id")

        # Fetch FK objects
        try:
            language_obj = Language.objects.get(uuid=language_uuid)
        except Language.DoesNotExist:
            return Response({"statusCode": 400, "status": False, "message": "Invalid Language UUID"}, status=400)

        try:
            language_test_obj = LanguageTest.objects.get(uuid=language_test_uuid)
        except LanguageTest.DoesNotExist:
            return Response({"statusCode": 400, "status": False, "message": "Invalid Language Test UUID"}, status=400)

        try:
            module_obj = LanguagetestmoduleName.objects.get(uuid=module_uuid)
        except LanguagetestmoduleName.DoesNotExist:
            return Response({"statusCode": 400, "status": False, "message": "Invalid Module UUID"}, status=400)

        try:
            lb_obj = StudyLanguageBanchmark.objects.get(uuid=lb_uuid)
        except StudyLanguageBanchmark.DoesNotExist:
            return Response({"statusCode": 400, "status": False, "message": "Invalid CLB Level UUID"}, status=400)

        # Check duplicate
        existing = LanguageTestResult.objects.filter(
            language=language_obj,
            language_test=language_test_obj,
            module_name=module_obj,
            lb_level=lb_obj,
            is_deleted=False
        ).first()
        if existing:
            return Response({"statusCode": 400, "status": False, "message": "Result already exists."}, status=400)

        data = request.data.copy()
        data['language_id'] = language_obj.uuid
        data['language_test_id'] = language_test_obj.uuid
        data['module_name_id'] = module_obj.uuid
        data['lb_level_id'] = lb_obj.uuid

        serializer = LanguageTestResultSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"statusCode": 200, "status": True, "message": "Result created successfully", "data": serializer.data})

        errors = " ".join([msg for msgs in serializer.errors.values() for msg in msgs])
        return Response({"statusCode": 400, "status": False, "message": errors}, status=400)


# -------------------- Retrieve -------------------- #
class LanguageTestResultRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = LanguageTestResult.objects.get(uuid=uuid, is_deleted=False)
        except LanguageTestResult.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "Not found", "data": None}, status=404)
        serializer = LanguageTestResultSerializer(obj)
        return Response({"statusCode": 200, "status": True, "message": "Retrieved successfully", "data": serializer.data})


# -------------------- Update -------------------- #
class LanguageTestResultUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = LanguageTestResult.objects.get(uuid=uuid, is_deleted=False)
        except LanguageTestResult.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "Not found", "data": None}, status=404)

        serializer = LanguageTestResultSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"statusCode": 200, "status": True, "message": "Updated successfully", "data": serializer.data})

        errors = " ".join([msg for msgs in serializer.errors.values() for msg in msgs])
        return Response({"statusCode": 400, "status": False, "message": errors}, status=400)


# -------------------- Delete -------------------- #


class LanguageTestResultDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        try:
            # ---------- Query Params ----------
            search = request.GET.get("search", "").strip()
            language_name_test_param = request.GET.get("languageNameTest", "").strip()
            language_test_name_param = request.GET.get("languageTestName", "").strip()
            language_module_name_param = request.GET.get("languageModuleName", "").strip()
            language_benchmark_level_param = request.GET.get("languageBanchMarkLevel", "").strip()

            # ---------- Parse comma UUIDs ----------
            def parse_uuids(param):
                arr = []
                if param:
                    for u in param.split(","):
                        try:
                            arr.append(UUID(u.strip()))
                        except:
                            pass
                return arr

            language_name_test_uuids = parse_uuids(language_name_test_param)
            language_test_name_uuids = parse_uuids(language_test_name_param)
            language_module_name_uuids = parse_uuids(language_module_name_param)
            language_benchmark_level_uuids = parse_uuids(language_benchmark_level_param)

            # ---------- Body Params ----------
            ids_body = request.data.get("id", None)
            delete_all_flag = request.data.get("deleteAll", False)

            # ---------- Base Queryset ----------
            queryset = LanguageTestResult.objects.filter(is_deleted=False)
            applied_filters = []

            if search:
                queryset = queryset.filter(numeric_score__istartswith=search)
                applied_filters.append("search")

            if language_name_test_uuids:
                queryset = queryset.filter(language__uuid__in=language_name_test_uuids)
                applied_filters.append("languageNameTest")

            if language_test_name_uuids:
                queryset = queryset.filter(language_test__uuid__in=language_test_name_uuids)
                applied_filters.append("languageTestName")

            if language_module_name_uuids:
                queryset = queryset.filter(module_name__uuid__in=language_module_name_uuids)
                applied_filters.append("languageModuleName")

            if language_benchmark_level_uuids:
                queryset = queryset.filter(lb_level__uuid__in=language_benchmark_level_uuids)
                applied_filters.append("languageBanchMarkLevel")

            

            # ---------- Case 2: Full table delete when id=="all", deleteAll:false, no filters ----------
            if not delete_all_flag and ids_body == "all" and not applied_filters:
                total = LanguageTestResult.objects.filter(is_deleted=False).count()
                if total == 0:
                    return Response({
                        "statusCode": 404,
                        "status": False,
                        "message": "No records found to delete",
                        "data": None
                    }, status=404)

                try:
                    with transaction.atomic():
                        LanguageTestResult.objects.filter(is_deleted=False).delete()
                except IntegrityError:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": "Full table can't be deleted, child reference exists.",
                        "data": None
                    }, status=400)

                return Response({
                    "statusCode": 200,
                    "status": True,
                    "message": f"All {total} LanguageTestResult record(s) permanently deleted",
                    "data": None
                })

            # ---------- Case 3: Delete UUID list from body ----------
            if not delete_all_flag and isinstance(ids_body, list) and ids_body:
                valid = []
                invalid = []
                for u in ids_body:
                    try:
                        valid.append(UUID(u))
                    except:
                        invalid.append(u)

                if not valid:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": "No valid UUIDs provided.",
                        "data": {"invalid_uuids": invalid}
                    }, status=400)

                qs_delete = queryset.filter(uuid__in=valid)
                count = qs_delete.count()

                if count == 0:
                    return Response({
                        "statusCode": 404,
                        "status": False,
                        "message": "No matching result(s) found",
                        "data": {"invalid_uuids": invalid} if invalid else None
                    }, status=404)

                try:
                    with transaction.atomic():
                        qs_delete.delete()
                except IntegrityError:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": "Can't delete selected dataset, child reference exists.",
                        "data": None
                    }, status=400)

                return Response({
                    "statusCode": 200,
                    "status": True,
                    "message": f"{count} result(s) deleted successfully",
                    "data": {"invalid_uuids": invalid} if invalid else None
                })

            # ---------- Case 4: deleteAll:true with applied filters ----------
            if delete_all_flag and applied_filters:
                count = queryset.count()
                if count == 0:
                    return Response({
                        "statusCode": 404,
                        "status": False,
                        "message": "No result(s) found matching applied filters",
                        "data": None
                    }, status=404)

                try:
                    with transaction.atomic():
                        queryset.delete()
                except IntegrityError:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": "Filtered dataset can't be deleted, child reference exists",
                        "data": None
                    }, status=400)

                return Response({
                    "statusCode": 200,
                    "status": True,
                    "message": f"{count} result(s) deleted based on filters: {', '.join(applied_filters)}",
                    "data": None
                })
            
            if delete_all_flag and applied_filters and (ids_body in [None, "", []]):
                count = queryset.count()

                if count == 0:
                    return Response({
                        "statusCode": 404,
                        "status": False,
                        "message": "No result(s) found matching applied filters",
                        "data": None
                    }, status=404)

                try:
                    with transaction.atomic():
                        queryset.delete()
                except IntegrityError:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": "Filtered dataset can't be deleted, child reference exists",
                        "data": None
                    }, status=400)

                return Response({
                    "statusCode": 200,
                    "status": True,
                    "message": f"{count} result(s) deleted based on filters: {', '.join(applied_filters)}",
                    "data": None
                })


            # ---------- Case 5: deleteAll:true but no filter applied ----------
            if delete_all_flag and not applied_filters:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "deleteAll:true requires at least one filter to delete",
                    "data": None
                }, status=400)

            # ---------- Final fallback ----------
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Invalid delete request combination",
                "data": None
            }, status=400)

        except Exception as e:
            return Response({
                "statusCode": 500,
                "status": False,
                "message": f"Internal server error: {str(e)}",
                "data": None
            }, status=500)
        



# -------------------- Export -------------------- #


class LanguageTestResultExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        search = request.GET.get('search', '').strip()
        custom_sort = request.GET.get('customSort')
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        # ---------------------------------------------------
        # Helper: Safe UUID parser (re-used logic)
        # ---------------------------------------------------
        def parse_uuid_list(param):
            raw = request.GET.get(param, '')
            final_list = []
            if raw:
                for x in raw.split(','):
                    try:
                        final_list.append(UUID(x.strip()))
                    except:
                        pass
            return final_list

        # Filters (same as List API)
        language_test_ids = parse_uuid_list('languageNameTest')
        benchmark_level_ids = parse_uuid_list('languageBenchmarkLevel')
        uuids_list = parse_uuid_list('uuids')
        language_test_names = parse_uuid_list('languageTestName')
        language_module_names = parse_uuid_list('languageModuleName')

        # ---------------------------------------------------
        # Base queryset
        # ---------------------------------------------------
        queryset = LanguageTestResult.objects.filter(is_deleted=False)

        # Filters
        if uuids_list:
            queryset = queryset.filter(uuid__in=uuids_list)

        if language_test_ids:
            queryset = queryset.filter(language__uuid__in=language_test_ids)

        if benchmark_level_ids:
            queryset = queryset.filter(lb_level__uuid__in=benchmark_level_ids)

        if language_test_names:
            queryset = queryset.filter(language_test__uuid__in=language_test_names)

        if language_module_names:
            queryset = queryset.filter(languagetest_module_name__uuid__in=language_module_names)

        # ---------------------------------------------------
        # SEARCH
        # ---------------------------------------------------
        if search:
            queryset = queryset.filter(
                Q(numeric_score__istartswith=search)
            )

        # ---------------------------------------------------
        # SORTING
        # ---------------------------------------------------
        sort_field_map = {
            "numeric_score": "numeric_score",
            "description": "description",
            "languageTestName": "language_test__name",
            "languageModuleName": "languagetest_module_name__moduleName",
            "languageBenchmarkLevel": "lb_level__level_name",
            "created_at": "created_at",
            "updated_at": "updated_at",
        }

        allowed_sort_fields = list(sort_field_map.keys())
        sort_fields = []

        # Custom sorting
        if custom_sort:
            for rule in custom_sort.split(","):
                try:
                    field, order = rule.split(":")
                    field = field.strip()
                    order = order.strip().lower()

                    if field not in sort_field_map:
                        continue

                    orm_field = sort_field_map[field]

                    # Case-insensitive sort for strings
                    if field in [
                        "description",
                        "languageTestName",
                        "languageModuleName",
                        "languageBenchmarkLevel"
                    ]:
                        f = Lower(orm_field)
                    else:
                        f = F(orm_field)

                    sort_fields.append(
                        f.asc(nulls_last=True)
                        if order == "asc" else f.desc(nulls_last=True)
                    )
                except:
                    continue
        else:
            # Default sort
            if sort_by not in allowed_sort_fields:
                sort_by = "created_at"

            orm_field = sort_field_map.get(sort_by, "created_at")
            f = F(orm_field)

            sort_fields = [
                f.asc(nulls_last=True) if sort_order == "asc" else f.desc(nulls_last=True)
            ]

        queryset = queryset.order_by(*sort_fields)

        # -------------------------------------------------------------------
        # Field to header mapping
        # -------------------------------------------------------------------
        field_header_map = {
            'uuid': 'UUID',
            'language': 'Language Name (Test)',
            'language_test': 'Language Test Name',
            'module_name': 'Module Name',
            'lb_level': 'Language Benchmark Level',
            'numeric_score': 'Language Test Result',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'created_at': 'Created On',
            'updated_at': 'Modified On',
        }

        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())

        # -------------------------------------------------------------------
        # Prepare export dataset
        # -------------------------------------------------------------------
        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'LanguageTestResult'

        india_tz = pytz.timezone("Asia/Kolkata")

        for obj in queryset:
            row = []
            for field in field_list:
                value = getattr(obj, field, '')

                # FK formatting
                if field == 'language' and value:
                    value = value.name
                elif field == 'language_test' and value:
                    value = value.name
                elif field == 'languagetest_module_name' and value:
                    value = value.moduleName
                elif field == 'lb_level' and value:
                    value = value.name

                # Datetime formatting
                elif field in ['created_at', 'updated_at'] and value:
                    value = timezone.localtime(value, india_tz).strftime(
                        "%d-%m-%Y %I:%M:%S %p"
                    )

                # Boolean
                elif isinstance(value, bool):
                    value = int(value)

                row.append(value if value is not None else '')

            dataset.append(row)

        # -------------------------------------------------------------------
        # EXPORT
        # -------------------------------------------------------------------
        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'language_test_results.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = (
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            file_name = 'language_test_results.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response



# -------------------- Import -------------------- #import io

class LanguageTestResultImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=400)

        format_type = file.name.split('.')[-1].lower()
        duplicates, skipped_rows, imported_count = [], [], 0
        data = []

        required_headers = {
            'language name (test)',
            'language test name',
            'module name',
            # 'language benchmark level',
            'language test result'
        }
        optional_headers = {'description','language benchmark level'}

        try:
            # ---------------- XLSX ----------------
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

                for row_no, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row):
                        skipped_rows.append({"Row": row_no, "Reason": "Empty row"})
                        continue
                    row_dict = dict(zip(headers, row))
                    row_dict['_row_number'] = row_no
                    data.append(row_dict)

            # ---------------- CSV ----------------
            elif format_type == 'csv':
                decoded_file = file.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(decoded_file))
                for row_no, row in enumerate(reader, start=2):
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    row_lower['_row_number'] = row_no
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({'error': f'Missing required headers'}, status=400)
                    if not all([row_lower.get(h) for h in required_headers]):
                        skipped_rows.append({"Row": row_no, "Reason": "Required field(s) missing"})
                        continue
                    data.append(row_lower)
            else:
                return Response({'error': 'Unsupported file format'}, status=400)

            # ---------------- Prefetch objects ----------------
            all_languages = Language.objects.all()
            language_map = {l.name.lower(): l for l in all_languages}

            all_tests = LanguageTest.objects.all()
            test_map = {t.name.lower(): t for t in all_tests}

            all_modules = LanguagetestmoduleName.objects.all()
            module_map = {m.name.lower(): m for m in all_modules}

            all_benchmarks = StudyLanguageBanchmark.objects.all()
            lb_map = {b.name.lower(): b for b in all_benchmarks}

            all_results = LanguageTestResult.objects.select_related('language', 'language_test', 'languagetest_module_name', 'lb_level').all()
            existing_map = {
                (r.language.name.lower(), r.language_test.name.lower(), r.languagetest_module_name.name.lower(), r.lb_level.name.lower()): r
                for r in all_results
            }

            # ---------------- Process Rows ----------------
            to_create = []

            for row in reversed(data):
                row_no = row.get('_row_number', 'Unknown')
                language_name = str(row.get('language name (test)')).strip()
                language_test_name = str(row.get('language test name')).strip()
                module_name = str(row.get('module name')).strip()
                lb_level_name = str(row.get('language benchmark level')).strip()
                numeric_score = row.get('language test result')
                description = str(row.get('description', '')).strip()

                key = (language_name.lower(), language_test_name.lower(), module_name.lower())
                existing = existing_map.get(key)

                if existing and not existing.is_deleted:
                    duplicates.append({"Row": row_no ,
                                        "Language Name (Test)": language_name or "",  
                                        "Language Test Name": language_test_name or "",  
                                        "Module Name": module_name or "",  
                                        "Language Benchmark Level": lb_level_name or "",  
                                        "Description":description or "", 
                                        "language test result":numeric_score or "", 
                                        "Reason": "Required related object(s) missing" })
                    continue

                language_obj = language_map.get(language_name.lower())
                test_obj = test_map.get(language_test_name.lower())
                module_obj = module_map.get(module_name.lower())
                lb_obj = lb_map.get(lb_level_name.lower())

                if not (language_obj and test_obj and module_obj and lb_obj):
                    skipped_rows.append({"Row": row_no ,
                                          "Language Name (Test)": language_name or "",  
                                            "Language Test Name": language_test_name or "",  
                                            "Module Name": module_name or "",  
                                            "Language Benchmark Level": lb_level_name or "",  
                                            "Description":description or "", 
                                            "language test result":numeric_score or "", 
                                              "Reason": "Required related object(s) missing"})
                    continue

                if existing and existing.is_deleted:
                    existing.numeric_score = numeric_score
                    existing.description = description
                    existing.is_deleted = False
                    existing.save()
                    imported_count += 1
                else:
                    to_create.append(LanguageTestResult(
                        language=language_obj,
                        language_test=test_obj,
                        languagetest_module_name=module_obj,
                        lb_level=lb_obj,
                        numeric_score=numeric_score,
                        description=description,
                        is_deleted=False
                    ))

            # Bulk insert
            if to_create:
                batch_size = 500
                for i in range(0, len(to_create), batch_size):
                    LanguageTestResult.objects.bulk_create(to_create[i:i+batch_size])
                imported_count += len(to_create)

        except Exception as e:
            return Response({'error': str(e)}, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": list(reversed(duplicates)),
            "skipped_rows": list(reversed(skipped_rows))
        }, status=200)



class CLBLevelListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        custom_sort = request.GET.get('customSort', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at').strip()
        sort_order = request.GET.get('sortOrder', 'desc').strip().lower()

        queryset = CLBLevel.objects.filter(is_deleted=False)

        #  SEARCH filter
        if search:
            queryset = queryset.filter(
                Q(name__istartswith=search) 
            )

        #  SORTING MAP
        sort_field_map = {
            'name': 'name',
            'description': 'description',
            'created_at': 'created_at',
            'updated_at': 'updated_at',
        }

        orm_field = sort_field_map.get(sort_by, 'created_at')

        # CASE 1 → Multi-rule customSort
        if custom_sort:
            sort_fields = []
            for rule in custom_sort.split(','):
                try:
                    field, order = rule.split(':')
                    field = field.strip()
                    order = order.strip().lower()
                    if field not in sort_field_map:
                        continue
                    mapped = sort_field_map[field]

                    # case-insensitive for text
                    expr = Lower(F(mapped)) if field in ['name', 'description'] else F(mapped)

                    sort_fields.append(
                        expr.asc(nulls_last=True) if order == 'asc' else expr.desc(nulls_last=True)
                    )
                except ValueError:
                    continue

            if sort_fields:
                queryset = queryset.order_by(*sort_fields)

        # CASE 2 → Normal sortBy + sortOrder
        else:
            sort_fields = []  
            if sort_by in ['name', 'description']:
                expr = Lower(F(orm_field))
            else:
                expr = F(orm_field)

            sort_fields.append(
                expr.asc(nulls_last=True) if sort_order == 'asc' else expr.desc(nulls_last=True)
            )

            queryset = queryset.order_by(*sort_fields)

        #  Pagination response
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = CLBLevelSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)





class CLBLevelCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        name = request.data.get("name", "").strip()
        existing = CLBLevel.objects.filter(name__iexact=name, is_deleted=False).first()
        if existing:
            return Response({"statusCode": 400, "status": False, "message": "CLB Level with this name already exists."}, status=400)

        serializer = CLBLevelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"statusCode": 200, "status": True, "message": "CLB Level created successfully", "data": serializer.data})
        errors = " ".join([msg for msgs in serializer.errors.values() for msg in msgs])
        return Response({"statusCode": 400, "status": False, "message": errors}, status=400)


class CLBLevelRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = CLBLevel.objects.get(uuid=uuid, is_deleted=False)
        except CLBLevel.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "Not found", "data": None}, status=404)
        serializer = CLBLevelSerializer(obj)
        return Response({"statusCode": 200, "status": True, "message": "Retrieved successfully", "data": serializer.data})


class CLBLevelUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = CLBLevel.objects.get(uuid=uuid, is_deleted=False)
        except CLBLevel.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "Not found", "data": None}, status=404)

        serializer = CLBLevelSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"statusCode": 200, "status": True, "message": "Updated successfully", "data": serializer.data})
        errors = " ".join([msg for msgs in serializer.errors.values() for msg in msgs])
        return Response({"statusCode": 400, "status": False, "message": errors}, status=400)


# class CLBLevelDeleteAPIView(APIView):
#     permission_classes = [IsAuthenticated, IsAdminUser]

#     def delete(self, request):
#         ids = request.data.get('id', None)
#         if not ids:
#             return Response({"statusCode": 400, "status": False, "message": "Provide 'id' field", "data": None}, status=400)

#         if ids == "all":
#             objs = CLBLevel.objects.filter(is_deleted=False)
#             count = objs.count()
#             objs.delete()
#             return Response({"statusCode": 200, "status": True, "message": f"All {count} CLB Level(s) deleted", "data": None})

#         if not isinstance(ids, list):
#             return Response({"statusCode": 400, "status": False, "message": "Provide list of UUIDs", "data": None}, status=400)

#         valid_uuids, invalid_uuids = [], []
#         for u in ids:
#             try:
#                 valid_uuids.append(UUID(u))
#             except ValueError:
#                 invalid_uuids.append(u)

#         objs = CLBLevel.objects.filter(uuid__in=valid_uuids, is_deleted=False)
#         count = objs.count()
#         if count == 0:
#             return Response({"statusCode": 404, "status": False, "message": "No matching CLB Level found", "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None}, status=404)

#         objs.delete()
#         return Response({"statusCode": 200, "status": True, "message": f"{count} CLB Level(s) deleted", "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None})


class CLBLevelDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        ids = request.data.get("id", None)
        delete_all = request.data.get("deleteAll", False)
        search = request.GET.get("search", "").strip()

        queryset = CLBLevel.objects.filter(is_deleted=False)

        # ---------------------------------------------------
        # CASE 3: deleteAll = true AND search present → Search delete
        # ---------------------------------------------------
        if delete_all and search and (ids in [None, ""]):
            qs_search = queryset.filter(name__istartswith=search)   
            count = qs_search.count()

            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No CLB Level found matching this search filter",
                    "data": None
                }, status=404)

            try:
                with transaction.atomic():
                    qs_search.delete()
            except IntegrityError:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "You can't delete selected CLB Level(s) because they are used in child tables",
                    "data": None
                }, status=400)

            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"{count} CLB Level(s) deleted based on search filter",
                "data": None
            }, status=200)

        # ---------------------------------------------------
        # CASE 2: id = "all" → Delete entire table
        # ---------------------------------------------------
        if ids == "all" and delete_all is False and search == "":
            qs_all = queryset
            count = qs_all.count()

            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No CLB Level(s) found to delete",
                    "data": None
                }, status=404)

            deleted, skipped = [], []

            for obj in qs_all:
                try:
                    with transaction.atomic():
                        obj.delete()
                    deleted.append(str(obj.uuid))
                except IntegrityError:
                    skipped.append(obj.level_name)

            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"Delete completed. {len(deleted)} deleted, {len(skipped)} skipped"
            }, status=200)

        # ---------------------------------------------------
        # CASE 1: id = [UUID list] → Bulk delete
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
                    "message": "No valid UUIDs provided",
                    "data": {"invalid_uuids": invalid_uuids}
                }, status=400)

            qs_ids = queryset.filter(uuid__in=valid_uuids)
            count = qs_ids.count()

            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No CLB Level found for given UUID list",
                    "data": None
                }, status=404)

            try:
                with transaction.atomic():
                    qs_ids.delete()
            except IntegrityError:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "One or more CLB Level(s) are used in child tables — cannot delete",
                    "data": None
                }, status=400)

            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"{count} CLB Level(s) deleted",
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





class CLBLevelExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')  
        uuids_param = request.GET.get('uuids', '') 
        uuids = [u.strip() for u in uuids_param.split(',') if u]

     
        field_header_map = {
            'uuid': 'UUID',
            'name': 'CLB Level',  
            'description': 'Description',
            'is_deleted': 'Deleted',
            'created_at': 'Created On',
            'updated_at': 'Modified On',
        }

        if fields:
            field_list = [f.strip() for f in fields.split(',')]
        else:
            field_list = list(field_header_map.keys())

        # --- Fetch queryset ---
        queryset = CLBLevel.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        # --- Prepare dataset ---
        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'CLBLevel'

        for obj in queryset:
            row = []
            for field in field_list:
                value = getattr(obj, field, '')

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
            content_type = 'text/csv; charset=utf-8'
            file_name = 'clblevel.csv'
        else:
            # XLSX export using BytesIO
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'clblevel.xlsx'

        # --- Return response ---
        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response



class CLBLevelImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicate_rows = []
        skipped_rows = []

        required_headers = {'clb level'}  # must be present
        optional_headers = {'description'} # optional

        try:
            data = []
            headers = []

            # ---------------- XLSX Handling ----------------
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
                        "message": f'The uploaded XLSX file (sheet: "{sheet_name}") is empty.'
                    }, status=status.HTTP_400_BAD_REQUEST)

                headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]

                if not required_headers.issubset(set(headers)):
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'Missing required headers. Required: {required_headers}, Found: {set(headers)}'
                    }, status=status.HTTP_400_BAD_REQUEST)

                for row_no, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    row_dict["_row_number"] = row_no
                    data.append(row_dict)

            # ---------------- CSV Handling ----------------
            elif format_type == 'csv':
                decoded_file = file.read().decode('utf-8')
                dataset = Dataset()
                dataset.load(decoded_file, format='csv')

                for idx, row in enumerate(dataset.dict, start=2):
                    row_lower = {k.strip().lower(): v for k, v in row.items()}

                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({
                            "statusCode": 400,
                            "status": False,
                            "message": f'Missing required headers. Required: {required_headers}, Found: {set(row_lower.keys())}'
                        }, status=status.HTTP_400_BAD_REQUEST)

                    row_lower["_row_number"] = idx
                    data.append(row_lower)

            else:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": 'Unsupported file format. Use .xlsx or .csv'
                }, status=status.HTTP_400_BAD_REQUEST)

            # ---------------- PROCESS ROWS ----------------
            imported_count = 0

            for row in reversed(data):
                row_no = row.get("_row_number", "Unknown")
                name = str(row.get('clb level')).strip() if row.get('clb level') else ''
                description = str(row.get('description')).strip() if row.get('description') else ''

                if not name:
                    skipped_rows.append({
                        "Row": row_no,
                        "CLB Level": "",
                        "Description":description or "",
                        "Reason": "Missing CLB level"
                    })
                    continue

                existing = CLBLevel.objects.filter(name__iexact=name).first()

                if existing:
                    if not existing.is_deleted:
                        duplicate_rows.append({
                            "Row": row_no,
                            "CLB Level": name,
                            "Description":description or "",
                            "Reason": "Duplicate CLB level"
                        })
                        continue
                    else:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    CLBLevel.objects.create(
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

        # ---------------- FINAL RESPONSE ----------------
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": list(reversed(duplicate_rows)),
            "skipped_rows": list(reversed(skipped_rows))
        }, status=status.HTTP_200_OK)


# class StudyLanguageBanchmarkListAPIView(APIView):
#     permission_classes = [IsAuthenticated, IsAdminUser]

#     def get(self, request):
#         search = request.GET.get('search', '').strip()
#         sort_by = request.GET.get('sortBy', 'created_at')
#         sort_order = request.GET.get('sortOrder', 'desc')
#         allowed_sort_fields = ['name', 'description', 'created_at']

#         if sort_by not in allowed_sort_fields:
#             sort_by = 'created_at'
#         if sort_order == 'desc':
#             sort_by = f'-{sort_by}'

#         queryset = StudyLanguageBanchmark.objects.filter(is_deleted=False)
#         if search:
#             queryset = queryset.filter(
#                 Q(name__istartswith=search) |
#                 Q(description__istartswith=search)
#             )

#         queryset = queryset.order_by(sort_by)
#         paginator = CustomPagination()
#         result_page = paginator.paginate_queryset(queryset, request)
#         serializer = StudyLanguageBanchmarkSerializer(result_page, many=True)
#         return paginator.get_paginated_response(serializer.data)


class StudyLanguageBanchmarkListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        custom_sort = request.GET.get('customSort', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at').strip()
        sort_order = request.GET.get('sortOrder', 'desc').strip().lower()

        queryset = StudyLanguageBanchmark.objects.filter(is_deleted=False)

        #  SEARCH (multi field)
        if search:
            queryset = queryset.filter(
                Q(name__istartswith=search)
            )

        #  SORTING
        sort_field_map = {
            'name': 'name',
            'description': 'description',
            'created_at': 'created_at',
            'updated_at': 'updated_at',  # if exists in model
        }

        sort_fields = []

        # CASE 1 → Custom multi-rule sorting
        if custom_sort:
            for rule in custom_sort.split(','):
                try:
                    field, order = rule.split(':')
                    field = field.strip()
                    order = order.strip().lower()

                    if field not in sort_field_map:
                        continue

                    orm_field = sort_field_map[field]

                    #  Case-insensitive Lower() for text fields
                    if field in ['name', 'description']:
                        expr = Lower(F(orm_field))
                    else:
                        expr = F(orm_field)

                    sort_fields.append(
                        expr.asc(nulls_last=True) if order == 'asc' else expr.desc(nulls_last=True)
                    )

                except ValueError:
                    continue

            if sort_fields:
                queryset = queryset.order_by(*sort_fields)
            else:
                queryset = queryset.order_by(F('created_at').desc(nulls_last=True))

        # CASE 2 → Normal single field sort (`sortBy` + `sortOrder`)
        else:
            orm_field = sort_field_map.get(sort_by, 'created_at')

            if sort_by in ['name', 'description']:
                expr = Lower(F(orm_field))
            else:
                expr = F(orm_field)

            queryset = queryset.order_by(
                expr.asc(nulls_last=True) if sort_order == 'asc' else expr.desc(nulls_last=True)
            )

        #  PAGINATION
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = StudyLanguageBanchmarkSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    

class StudyLanguageBanchmarkCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        name = request.data.get("name", "").strip()
        existing = StudyLanguageBanchmark.objects.filter(name__iexact=name, is_deleted=False).first()
        if existing:
            return Response({"statusCode": 400, "status": False, "message": "Benchmark with this name already exists."}, status=400)

        serializer = StudyLanguageBanchmarkSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"statusCode": 200, "status": True, "message": "Benchmark created successfully", "data": serializer.data})
        errors = " ".join([msg for msgs in serializer.errors.values() for msg in msgs])
        return Response({"statusCode": 400, "status": False, "message": errors}, status=400)


class StudyLanguageBanchmarkRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = StudyLanguageBanchmark.objects.get(uuid=uuid, is_deleted=False)
        except StudyLanguageBanchmark.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "Not found", "data": None}, status=404)
        serializer = StudyLanguageBanchmarkSerializer(obj)
        return Response({"statusCode": 200, "status": True, "message": "Retrieved successfully", "data": serializer.data})


class StudyLanguageBanchmarkUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = StudyLanguageBanchmark.objects.get(uuid=uuid, is_deleted=False)
        except StudyLanguageBanchmark.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "Not found", "data": None}, status=404)

        serializer = StudyLanguageBanchmarkSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"statusCode": 200, "status": True, "message": "Updated successfully", "data": serializer.data})
        errors = " ".join([msg for msgs in serializer.errors.values() for msg in msgs])
        return Response({"statusCode": 400, "status": False, "message": errors}, status=400)


# class StudyLanguageBanchmarkDeleteAPIView(APIView):
#     permission_classes = [IsAuthenticated, IsAdminUser]

#     def delete(self, request):
#         ids = request.data.get('id', None)
#         if not ids:
#             return Response({"statusCode": 400, "status": False, "message": "Provide 'id' field", "data": None}, status=400)

#         if ids == "all":
#             objs = StudyLanguageBanchmark.objects.filter(is_deleted=False)
#             count = objs.count()
#             objs.delete()
#             return Response({"statusCode": 200, "status": True, "message": f"All {count} benchmark(s) deleted", "data": None})

#         if not isinstance(ids, list):
#             return Response({"statusCode": 400, "status": False, "message": "Provide list of UUIDs", "data": None}, status=400)

#         valid_uuids, invalid_uuids = [], []
#         for u in ids:
#             try:
#                 valid_uuids.append(UUID(u))
#             except ValueError:
#                 invalid_uuids.append(u)

#         objs = StudyLanguageBanchmark.objects.filter(uuid__in=valid_uuids, is_deleted=False)
#         count = objs.count()
#         if count == 0:
#             return Response({"statusCode": 404, "status": False, "message": "No matching benchmark found", "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None}, status=404)

#         objs.delete()
#         return Response({"statusCode": 200, "status": True, "message": f"{count} benchmark(s) deleted", "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None})


class StudyLanguageBanchmarkDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        ids = request.data.get("id", None)
        delete_all = request.data.get("deleteAll", False)
        search = request.GET.get("search", "").strip()

        queryset = StudyLanguageBanchmark.objects.filter(is_deleted=False)

        # ---------------------------------------------------
        # CASE 3: deleteAll = true AND search present → Search delete
        # ---------------------------------------------------
        if delete_all and search and (ids in [None, ""]):
            qs_search = queryset.filter(name__istartswith=search)
            count = qs_search.count()

            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No benchmarks found matching search filter",
                    "data": None
                }, status=404)

            try:
                with transaction.atomic():
                    qs_search.delete()
            except IntegrityError:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Some benchmark(s) are used in child tables. Delete skipped.",
                    "data": None
                }, status=400)

            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"{count} benchmark(s) deleted using search filter",
                "data": None
            }, status=200)

        # ---------------------------------------------------
        # CASE 2: deleteAll = false AND id = "all" → Delete everything
        # ---------------------------------------------------
        if ids == "all" and delete_all is False and search == "":
            qs_all = queryset
            count = qs_all.count()

            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No benchmarks found to delete",
                    "data": None
                }, status=404)

            deleted, skipped = [], []

            for obj in qs_all:
                try:
                    with transaction.atomic():
                        obj.delete()
                    deleted.append(str(obj.uuid))
                except IntegrityError:
                    skipped.append(obj.uuid)

            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"Delete completed: {len(deleted)} deleted, {len(skipped)} skipped",
                "data": {
                    "deleted": deleted,
                    "not_deleted": skipped
                }
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
                    "message": "No matching benchmark records found",
                    "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
                }, status=404)

            try:
                with transaction.atomic():
                    qs_ids.delete()
            except IntegrityError:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "One or more benchmark(s) are used in child tables. Cannot delete.",
                    "data": None
                }, status=400)

            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"{count} benchmark(s) deleted",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=200)

        # ---------------------------------------------------
        # INVALID REQUEST FORMAT
        # ---------------------------------------------------
        return Response({
            "statusCode": 400,
            "status": False,
            "message": "Invalid delete request format",
            "data": None
        }, status=400)





class StudyLanguageBenchmarkExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')  # comma-separated fields
        uuids_param = request.GET.get('uuids', '')  # comma-separated UUIDs

        uuids = [u.strip() for u in uuids_param.split(',') if u]

        # Field to header mapping
        field_header_map = {
            'uuid': 'UUID',
            'name': 'Language Banchmark Level',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'created_at': 'Created On',
            'updated_at': 'Modified On',
        }

        # Determine which fields to export
        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())

        # Fetch queryset
        queryset = StudyLanguageBanchmark.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        # Prepare dataset
        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'LanguageBenchmarkLevel'

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

        # Export data
        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'study_language_benchmark.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'study_language_benchmark.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


class StudyLanguageBenchmarkImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicate_rows = []
        skipped_rows = []

        required_headers = {'language banchmark level'}  # must be present
        optional_headers = {'description'}               # optional

        try:
            data = []
            headers = []

            # ---------------- XLSX Handling ----------------
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
                        "message": f'The uploaded XLSX file (sheet: "{sheet_name}") is empty.'
                    }, status=status.HTTP_400_BAD_REQUEST)

                headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]

                if not required_headers.issubset(set(headers)):
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'Missing required headers. Required: {required_headers}, Found: {set(headers)}'
                    }, status=status.HTTP_400_BAD_REQUEST)

                for row_no, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    row_dict["_row_number"] = row_no
                    data.append(row_dict)

            # ---------------- CSV Handling ----------------
            elif format_type == 'csv':
                decoded_file = file.read().decode('utf-8')
                dataset = Dataset()
                dataset.load(decoded_file, format='csv')

                for idx, row in enumerate(dataset.dict, start=2):
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({
                            "statusCode": 400,
                            "status": False,
                            "message": f'Missing required headers. Required: {required_headers}, Found: {set(row_lower.keys())}'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    row_lower["_row_number"] = idx
                    data.append(row_lower)

            else:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": 'Unsupported file format. Use .xlsx or .csv'
                }, status=status.HTTP_400_BAD_REQUEST)

            # ---------------- PROCESS ROWS ----------------
            imported_count = 0

            for row in reversed(data):
                row_no = row.get("_row_number", "Unknown")
                name = str(row.get('language banchmark level')).strip() if row.get('language banchmark level') else ''
                description = str(row.get('description')).strip() if row.get('description') else ''

                if not name:
                    skipped_rows.append({
                        "Row": row_no,
                        "Language Benchmark Level": "",
                        "Description":description or "",
                        "Reason": "Missing language benchmark level"
                    })
                    continue

                existing = StudyLanguageBanchmark.objects.filter(name__iexact=name).first()

                if existing:
                    if not existing.is_deleted:
                        duplicate_rows.append({
                            "Row": row_no,
                            "Language Benchmark Level": name,
                            "Description":description or "",
                            "Reason": "Duplicate benchmark level"
                        })
                        continue
                    else:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    StudyLanguageBanchmark.objects.create(
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

        # ---------------- FINAL RESPONSE ----------------
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": list(reversed(duplicate_rows)),
            "skipped_rows": list(reversed(skipped_rows))
        }, status=status.HTTP_200_OK)






# class EntranceTestNameListAPIView(APIView):
#     permission_classes = [IsAuthenticated, IsAdminUser]

#     def get(self, request):
#         search = request.GET.get('search', '').strip()
#         sort_by = request.GET.get('sortBy', 'created_at')
#         sort_order = request.GET.get('sortOrder', 'desc')
#         allowed_sort_fields = ['fullname', 'shortname', 'description', 'updated_at']

#         if sort_by not in allowed_sort_fields:
#             sort_by = 'created_at'
#         if sort_order == 'desc':
#             sort_by = f'-{sort_by}'

#         queryset = EntranceTestName.objects.filter(is_deleted=False)
#         if search:
#             queryset = queryset.filter(
#                 Q(fullname__istartswith=search) |
#                 Q(shortname__istartswith=search) |
#                 Q(description__istartswith=search)
#             )

#         queryset = queryset.order_by(sort_by)
#         paginator = CustomPagination()
#         result_page = paginator.paginate_queryset(queryset, request)
#         serializer = EntranceTestNameSerializer(result_page, many=True)
#         return paginator.get_paginated_response(serializer.data)


class EntranceTestNameListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        custom_sort = request.GET.get('customSort', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at').strip()
        sort_order = request.GET.get('sortOrder', 'desc').strip().lower()

        #  base queryset
        queryset = EntranceTestName.objects.filter(is_deleted=False)

        #  search filter
        if search:
            queryset = queryset.filter(
                Q(fullname__istartswith=search)
            )

        #  sorting map
        sort_field_map = {
            'fullname': 'fullname',
            'shortname': 'shortname',
            'description': 'description',
            'created_at': 'created_at',
            'updated_at': 'updated_at',
        }

        orm_field = sort_field_map.get(sort_by, 'created_at')

        # CASE 1 → custom multi-rule sort
        if custom_sort:
            sort_fields = []
            for rule in custom_sort.split(','):
                try:
                    field, order = rule.split(':')
                    field = field.strip()
                    order = order.strip().lower()
                    if field not in sort_field_map:
                        continue
                    mapped = sort_field_map[field]

                    expr = Lower(F(mapped)) if field in ['fullname', 'shortname', 'description'] else F(mapped)

                    sort_fields.append(
                        expr.asc(nulls_last=True) if order == 'asc' else expr.desc(nulls_last=True)
                    )
                except ValueError:
                    continue

            if sort_fields:
                queryset = queryset.order_by(*sort_fields)

        # CASE 2 → normal single sortBy + sortOrder
        else:
            sort_fields = []  #  init list to avoid crash
            
            expr = Lower(F(orm_field)) if sort_by in ['fullname', 'shortname', 'description'] else F(orm_field)

            sort_fields.append(
                expr.asc(nulls_last=True) if sort_order == 'asc' else expr.desc(nulls_last=True)
            )

            queryset = queryset.order_by(*sort_fields)

        #  final fallback default sort
        if not queryset.ordered:
            queryset = queryset.order_by(F('created_at').desc(nulls_last=True))  #  default created_at DESC

        #  pagination
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = EntranceTestNameSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    


class EntranceTestNameCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        fullname = request.data.get("fullname", "").strip()
        shortname = request.data.get("shortname", "").strip()

        existing = EntranceTestName.objects.filter(
            fullname__iexact=fullname,
            shortname__iexact=shortname,
            is_deleted=False
        ).first()
        if existing:
            return Response({"statusCode": 400, "status": False, "message": "Entrance Test with this name already exists."}, status=400)

        serializer = EntranceTestNameSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"statusCode": 200, "status": True, "message": "Entrance Test created successfully", "data": serializer.data})
        errors = " ".join([msg for msgs in serializer.errors.values() for msg in msgs])
        return Response({"statusCode": 400, "status": False, "message": errors}, status=400)


class EntranceTestNameRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = EntranceTestName.objects.get(uuid=uuid, is_deleted=False)
        except EntranceTestName.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "Not found", "data": None}, status=404)
        serializer = EntranceTestNameSerializer(obj)
        return Response({"statusCode": 200, "status": True, "message": "Retrieved successfully", "data": serializer.data})


class EntranceTestNameUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = EntranceTestName.objects.get(uuid=uuid, is_deleted=False)
        except EntranceTestName.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "Not found", "data": None}, status=404)

        serializer = EntranceTestNameSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"statusCode": 200, "status": True, "message": "Updated successfully", "data": serializer.data})
        errors = " ".join([msg for msgs in serializer.errors.values() for msg in msgs])
        return Response({"statusCode": 400, "status": False, "message": errors}, status=400)


# class EntranceTestNameDeleteAPIView(APIView):
#     permission_classes = [IsAuthenticated, IsAdminUser]

#     def delete(self, request):
#         ids = request.data.get('id', None)
#         if not ids:
#             return Response({"statusCode": 400, "status": False, "message": "Provide 'id' field", "data": None}, status=400)

#         if ids == "all":
#             objs = EntranceTestName.objects.filter(is_deleted=False)
#             count = objs.count()
#             objs.delete()
#             return Response({"statusCode": 200, "status": True, "message": f"All {count} entrance test(s) deleted", "data": None})

#         if not isinstance(ids, list):
#             return Response({"statusCode": 400, "status": False, "message": "Provide list of UUIDs", "data": None}, status=400)

#         valid_uuids, invalid_uuids = [], []
#         for u in ids:
#             try:
#                 valid_uuids.append(UUID(u))
#             except ValueError:
#                 invalid_uuids.append(u)

#         objs = EntranceTestName.objects.filter(uuid__in=valid_uuids, is_deleted=False)
#         count = objs.count()
#         if count == 0:
#             return Response({"statusCode": 404, "status": False, "message": "No matching entrance test found", "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None}, status=404)

#         objs.delete()
#         return Response({"statusCode": 200, "status": True, "message": f"{count} entrance test(s) deleted", "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None})

class EntranceTestNameDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        ids = request.data.get("id", None)
        delete_all = request.data.get("deleteAll", False)
        search = request.GET.get("search", "").strip()

        queryset = EntranceTestName.objects.filter(is_deleted=False)

        # ---------------------------------------------------
        # CASE 3: deleteAll = true AND search present → Search delete
        # ---------------------------------------------------
        if delete_all and search and (ids in [None, ""]):
            qs_search = queryset.filter(shortname__istartswith=search)
            count = qs_search.count()

            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No entrance test(s) found matching this search filter",
                    "data": None
                }, status=404)

            try:
                with transaction.atomic():
                    qs_search.delete()
            except IntegrityError:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "You can't delete selected entrance test(s) because they are used in child tables",
                    "data": None
                }, status=400)

            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"{count} entrance test(s) deleted based on search filter",
                "data": None
            }, status=200)

        # ---------------------------------------------------
        # CASE 2: id = "all" AND deleteAll = false → Delete all records
        # ---------------------------------------------------
        if ids == "all" and delete_all is False and search == "":
            qs_all = queryset
            count = qs_all.count()

            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No entrance test(s) found to delete",
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
                "message": f"Delete completed. {len(deleted)} deleted, {len(skipped)} skipped.",
                "data": {"deleted": deleted, "not_deleted": skipped}
            }, status=200)

        # ---------------------------------------------------
        # CASE 1: id = [UUID list] → Bulk delete
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
                    "message": "No entrance test(s) found for given UUID list",
                    "data": None
                }, status=404)

            try:
                with transaction.atomic():
                    qs_ids.delete()
            except IntegrityError:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "One or more entrance test(s) are used in child tables, cannot delete.",
                    "data": None
                }, status=400)

            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"{count} entrance test(s) deleted.",
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



# -------------------- Export -------------------- #

class EntranceTestNameExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        # Field to header mapping
        field_header_map = {
            'uuid': 'UUID',
            'fullname': 'Entrance Test Full Name',
            'shortname': 'Entrance Test Name',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'created_at': 'Created On',
            'updated_at': 'Modified On',
        }

        # Determine fields to export
        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())

        # Fetch queryset
        queryset = EntranceTestName.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        # Prepare dataset
        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'EntranceTestName'

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

        # Export data
        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'entrance_test_name.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'entrance_test_name.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


class EntranceTestNameImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicates = []
        skipped_rows = []

        required_headers = {'entrance test full name'}
        optional_headers = {'entrance test name', 'description'}

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
                        "message": f'The uploaded XLSX file (sheet: "{sheet_name}") is empty.'
                    }, status=status.HTTP_400_BAD_REQUEST)

                headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]

                if not required_headers.issubset(set(headers)):
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'Missing required headers. Required: {required_headers}, Found: {set(headers)}'
                    }, status=status.HTTP_400_BAD_REQUEST)

                for row_no, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row):
                        skipped_rows.append({"Row": row_no, "Reason": "Empty row"})
                        continue
                    row_dict = dict(zip(headers, row))
                    row_dict['_row_number'] = row_no
                    data.append(row_dict)

            # ---------------- CSV ----------------
            elif format_type == 'csv':
                decoded_file = file.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(decoded_file))
                for row_no, row in enumerate(reader, start=2):
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    row_lower['_row_number'] = row_no
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({
                            "statusCode": 400,
                            "status": True,
                            "message": f'Missing required headers. Required: {", ".join(required_headers)}. Found headers in the file: {", ".join(row_lower.keys())}.'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    if not row_lower.get('entrance test full name'):
                        skipped_rows.append({"Row": row_no, "Reason": "Missing entrance test full name"})
                        continue
                    data.append(row_lower)
            else:
                return Response({
                    "statusCode": 400,
                    "status": True,
                    'error': 'Unsupported file format. Use .xlsx or .csv'
                }, status=status.HTTP_400_BAD_REQUEST)

            # ---------------- Process Rows ----------------
            to_create = []
            imported_count = 0

            existing_entries = EntranceTestName.objects.all()
            existing_map = {(e.fullname.lower(), e.shortname.lower() if e.shortname else ''): e for e in existing_entries}

            for row in reversed(data):
                row_no = row.get('_row_number', 'Unknown')
                fullname = str(row.get('entrance test full name')).strip()
                shortname = str(row.get('entrance test name')).strip() if row.get('entrance test name') else ''
                description = str(row.get('description')).strip() if row.get('description') else ''

                if not fullname:
                    skipped_rows.append({"Row": row_no, "FullName": fullname, "ShortName": shortname,"Description":description or "", "Reason": "Missing entrance test full name"})
                    continue

                key = (fullname.lower(), shortname.lower())
                existing = existing_map.get(key)

                if existing:
                    if not existing.is_deleted:
                        duplicates.append({"Row": row_no, "FullName": fullname, "ShortName": shortname,"Description":description or "", "Reason": "Already exists"})
                        continue
                    else:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                        continue

                to_create.append(EntranceTestName(
                    fullname=fullname,
                    shortname=shortname,
                    description=description,
                    is_deleted=False
                ))

            # Bulk insert in batches
            if to_create:
                batch_size = 500
                for i in range(0, len(to_create), batch_size):
                    EntranceTestName.objects.bulk_create(to_create[i:i+batch_size])
                imported_count += len(to_create)

        except Exception as e:
            return Response({
                "statusCode": 400,
                "status": True,
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


#---------------------------------------modulename-----------------------------    

# class EntranceTestModuleNameListAPIView(APIView):
#     permission_classes = [IsAuthenticated, IsAdminUser]

#     def get(self, request):
#         search = request.GET.get('search', '').strip()
#         sort_by = request.GET.get('sortBy', 'created_at')
#         sort_order = request.GET.get('sortOrder', 'desc')
#         allowed_sort_fields = ['moduleName', 'description', 'created_at']

#         if sort_by not in allowed_sort_fields:
#             sort_by = 'created_at'
#         if sort_order == 'desc':
#             sort_by = f'-{sort_by}'

#         queryset = EntranceTestModuleName.objects.filter(is_deleted=False)
#         if search:
#             queryset = queryset.filter(
#                 Q(moduleName__istartswith=search) |
#                 Q(description__istartswith=search)
#             )

#         queryset = queryset.order_by(sort_by)
#         paginator = CustomPagination()
#         result_page = paginator.paginate_queryset(queryset, request)
#         serializer = EntranceTestModuleNameSerializer(result_page, many=True)
#         return paginator.get_paginated_response(serializer.data)



class EntranceTestModuleNameListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        custom_sort = request.GET.get('customSort')
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        uuid_entrance_test_name = request.GET.get('entranceTestName', '')
        

        queryset = EntranceTestModuleName.objects.all()

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

        entrance_test_name_list = parse_uuid_list(uuid_entrance_test_name)

        if entrance_test_name_list:
            queryset = queryset.filter(entrancetest__uuid__in=entrance_test_name_list)

        # ----------------------
        # SEARCH FILTER
        # ----------------------
        if search:
            queryset = queryset.filter(moduleName__istartswith=search)

        # ----------------------
        # SORT FIELD MAP
        # ----------------------
        sort_field_map = {
            "uuid": "uuid",
            "entranceTestName": "entrancetest__fullname",
            "moduleName": "moduleName",
            "description": "description",
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
                    if field in ["moduleName", "entranceTestName", "description"]:
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
        serializer = EntranceTestModuleNameSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)
    


# -------------------- Create -------------------- #
class EntranceTestModuleNameCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        moduleName = request.data.get("moduleName", "").strip()
        existing = EntranceTestModuleName.objects.filter(moduleName__iexact=moduleName, is_deleted=False).first()
        if existing:
            return Response({"statusCode": 400, "status": False, "message": "Module name already exists."}, status=400)

        serializer = EntranceTestModuleNameSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"statusCode": 200, "status": True, "message": "Module created successfully", "data": serializer.data})
        errors = " ".join([msg for msgs in serializer.errors.values() for msg in msgs])
        return Response({"statusCode": 400, "status": False, "message": errors}, status=400)


# -------------------- Retrieve -------------------- #
class EntranceTestModuleNameRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = EntranceTestModuleName.objects.get(uuid=uuid, is_deleted=False)
        except EntranceTestModuleName.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "Not found", "data": None}, status=404)
        serializer = EntranceTestModuleNameSerializer(obj)
        return Response({"statusCode": 200, "status": True, "message": "Retrieved successfully", "data": serializer.data})


# -------------------- Update -------------------- #
class EntranceTestModuleNameUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = EntranceTestModuleName.objects.get(uuid=uuid, is_deleted=False)
        except EntranceTestModuleName.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "Not found", "data": None}, status=404)

        serializer = EntranceTestModuleNameSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"statusCode": 200, "status": True, "message": "Updated successfully", "data": serializer.data})
        errors = " ".join([msg for msgs in serializer.errors.values() for msg in msgs])
        return Response({"statusCode": 400, "status": False, "message": errors}, status=400)


# -------------------- Delete -------------------- #
# class EntranceTestModuleNameDeleteAPIView(APIView):
#     permission_classes = [IsAuthenticated, IsAdminUser]

#     def delete(self, request):
#         ids = request.data.get('id', None)
#         if not ids:
#             return Response({"statusCode": 400, "status": False, "message": "Provide 'id' field", "data": None}, status=400)

#         if ids == "all":
#             objs = EntranceTestModuleName.objects.filter(is_deleted=False)
#             count = objs.count()
#             objs.delete()
#             return Response({"statusCode": 200, "status": True, "message": f"All {count} module(s) deleted", "data": None})

#         if not isinstance(ids, list):
#             return Response({"statusCode": 400, "status": False, "message": "Provide list of UUIDs", "data": None}, status=400)

#         valid_uuids, invalid_uuids = [], []
#         for u in ids:
#             try:
#                 valid_uuids.append(UUID(u))
#             except ValueError:
#                 invalid_uuids.append(u)

#         objs = EntranceTestModuleName.objects.filter(uuid__in=valid_uuids, is_deleted=False)
#         count = objs.count()
#         if count == 0:
#             return Response({"statusCode": 404, "status": False, "message": "No matching module found", "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None}, status=404)

#         objs.delete()
#         return Response({"statusCode": 200, "status": True, "message": f"{count} module(s) deleted", "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None})


class EntranceTestModuleNameDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        try:
            # ---------- Query Params ----------
            search = request.GET.get("search", "").strip()
            entrance_test_name_param = request.GET.get("entranceTestName", "").strip()

            # Parse comma separated UUIDs from filter (if needed)
            def parse_uuids(param):
                arr = []
                if param:
                    for u in param.split(","):
                        try:
                            arr.append(UUID(u.strip()))
                        except:
                            pass
                return arr

            entrance_test_name_uuids = parse_uuids(entrance_test_name_param)

            # ---------- Body Params ----------
            ids_body = request.data.get("id", None)
            delete_all_flag = request.data.get("deleteAll", False)

            # ---------- Base Queryset ----------
            queryset = EntranceTestModuleName.objects.filter(is_deleted=False)
            applied_filters = []

            # Apply search filter
            if search:
                queryset = queryset.filter(moduleName__istartswith=search)
                applied_filters.append("search")

            # Apply entranceTestName filter
            if entrance_test_name_uuids:
                queryset = queryset.filter(entrancetest__uuid__in=entrance_test_name_uuids)
                applied_filters.append("entranceTestName")

            # ---------- Case 1: Delete single UUID from URL ----------
            if uuid:
                try:
                    obj = queryset.get(uuid=uuid)
                except EntranceTestModuleName.DoesNotExist:
                    return Response({
                        "statusCode": 404,
                        "status": False,
                        "message": "Entrance Test Module not found",
                        "data": None
                    }, status=404)

                try:
                    with transaction.atomic():
                        obj.delete()
                except IntegrityError:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": "You can't delete this record, child reference exists.",
                        "data": None
                    }, status=400)

                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "Entrance Test Module permanently deleted",
                    "data": None
                }, status=204)

            # ---------- Case 2: Full table delete when id=="all" & deleteAll:false & no filters ----------
            if not delete_all_flag and ids_body == "all" and not applied_filters:
                queryset = EntranceTestModuleName.objects.filter(is_deleted=False)
                total = queryset.count()

                if total == 0:
                    return Response({
                        "statusCode": 404,
                        "status": False,
                        "message": "No records found to delete",
                        "data": None
                    }, status=404)

                try:
                    with transaction.atomic():
                        queryset.delete()
                except IntegrityError:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": "Full table can't be deleted, child reference exists.",
                        "data": None
                    }, status=400)

                return Response({
                    "statusCode": 200,
                    "status": True,
                    "message": f"All {total} module(s) permanently deleted",
                    "data": None
                })

            # ---------- Case 3: Bulk UUID list delete from body ----------
            if not delete_all_flag and isinstance(ids_body, list) and ids_body:
                valid = []
                invalid = []
                for u in ids_body:
                    try:
                        valid.append(UUID(u))
                    except:
                        invalid.append(u)

                if not valid:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": "No valid UUIDs provided.",
                        "data": {"invalid_uuids": invalid}
                    }, status=400)

                qs_delete = queryset.filter(uuid__in=valid)
                count = qs_delete.count()

                if count == 0:
                    return Response({
                        "statusCode": 404,
                        "status": False,
                        "message": "No matching module found",
                        "data": {"invalid_uuids": invalid} if invalid else None
                    }, status=404)

                try:
                    with transaction.atomic():
                        qs_delete.delete()
                except IntegrityError:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": "Can't delete selected dataset, child reference exists.",
                        "data": None
                    }, status=400)

                return Response({
                    "statusCode": 200,
                    "status": True,
                    "message": f"{count} module(s) deleted successfully",
                    "data": {"invalid_uuids": invalid} if invalid else None
                })

            # ---------- Case 4: deleteAll:true & filter applied ----------
            if delete_all_flag and applied_filters:
                count = queryset.count()

                if count == 0:
                    return Response({
                        "statusCode": 404,
                        "status": False,
                        "message": "No records found matching applied filters",
                        "data": None
                    }, status=404)

                try:
                    with transaction.atomic():
                        queryset.delete()
                except IntegrityError:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": "Filtered dataset can't be deleted, child reference exists",
                        "data": None
                    }, status=400)

                return Response({
                    "statusCode": 200,
                    "status": True,
                    "message": f"{count} record(s) deleted based on filter: {', '.join(applied_filters)}",
                    "data": None
                })

            # ---------- Case 5: deleteAll:true without filter ----------
            if delete_all_flag and not applied_filters:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "deleteAll:true requires at least one filter to delete",
                    "data": None
                }, status=400)

            # ---------- Final fallback ----------
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Invalid delete request combination",
                "data": None
            }, status=400)

        except Exception as e:
            return Response({
                "statusCode": 500,
                "status": False,
                "message": f"Internal server error: {str(e)}",
                "data": None
            }, status=500)
        


class EntranceTestModuleExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'entrancetest': 'Entrance Test Name',
            'moduleName': 'Entrance Test Module Name',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'created_at': 'Created On',
            'updated_at': 'Modified On',
        }

        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())

        queryset = EntranceTestModuleName.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'EntranceTestModules'

        for obj in queryset:
            row = []
            for field in field_list:
                value = getattr(obj, field, '')
                # Foreign key handling
                if field == 'entrancetest' and value:
                    value = value.shortname if hasattr(value, 'shortname') else str(value)
                # Datetime formatting
                elif field in ['created_at', 'updated_at'] and value:
                    value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
                # Boolean formatting
                elif isinstance(value, bool):
                    value = int(value)
                row.append(value if value is not None else '')
            dataset.append(row)

        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'entrance_test_modules.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'entrance_test_modules.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


# ------------------- IMPORT API -------------------

class EntranceTestModuleImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicates = []
        skipped_rows = []

        required_headers = {'entrance test name', 'entrance test module name'}
        optional_headers = {'description'}

        data = []

        try:
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
                    return Response({'error': f'Sheet "{sheet_name}" is empty.'}, status=400)

                headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                if not required_headers.issubset(set(headers)):
                    return Response({'error': f'Missing required headers. Required: {required_headers}, Found: {set(headers)}'}, status=400)

                for row_no, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row):
                        skipped_rows.append({"Row": row_no, "Reason": "Empty row"})
                        continue
                    row_dict = dict(zip(headers, row))
                    row_dict['_row_number'] = row_no
                    data.append(row_dict)

            # ---------------- CSV ----------------
            elif format_type == 'csv':
                decoded_file = file.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(decoded_file))
                for row_no, row in enumerate(reader, start=2):
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    row_lower['_row_number'] = row_no
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({'error': f'Missing required headers. Required: {", ".join(required_headers)}. Found: {", ".join(row_lower.keys())}'}, status=400)
                    if not row_lower.get('entrance test name') or not row_lower.get('entrance test module name'):
                        skipped_rows.append({"Row": row_no, "Reason": "Missing entrance test name or module name"})
                        continue
                    data.append(row_lower)
            else:
                return Response({'error': 'Unsupported file format. Use .xlsx or .csv'}, status=400)

            # ---------------- Process Rows ----------------
            to_create = []
            imported_count = 0

            # Pre-fetch existing modules to reduce queries
            all_tests = EntranceTestName.objects.all()
            test_map = {t.shortname.lower(): t for t in all_tests if t.shortname}

            all_modules = EntranceTestModuleName.objects.select_related('entrancetest').all()
            existing_map = {(m.entrancetest.shortname.lower(), m.moduleName.lower()): m for m in all_modules if m.entrancetest and m.moduleName}

            for row in reversed(data):
                row_no = row.get('_row_number', 'Unknown')
                test_name = str(row.get('entrance test name')).strip()
                module_name = str(row.get('entrance test module name')).strip()
                description = str(row.get('description')).strip() if row.get('description') else ''

                if not test_name or not module_name:
                    skipped_rows.append({"Row": row_no, "EntranceTest": test_name or "", "Module": module_name or "","Description":description or "","Reason": "Missing entrance test name or module name"})
                    continue

                test_obj = test_map.get(test_name.lower())
                if not test_obj:
                    skipped_rows.append({"Row": row_no, "EntranceTest": test_name or "", "Module": module_name or "","Description":description or "", "Reason": f'Entrance test "{test_name}" not found'})
                    continue

                key = (test_name.lower(), module_name.lower())
                existing = existing_map.get(key)

                if existing:
                    if not existing.is_deleted:
                        duplicates.append({"Row": row_no, "EntranceTest": test_name, "Module": module_name,"Description":description or "", "Reason": "Already exists"})
                        continue
                    else:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                        continue

                to_create.append(EntranceTestModuleName(
                    entrancetest=test_obj,
                    moduleName=module_name,
                    description=description,
                    is_deleted=False
                ))

            # Bulk insert in batches
            if to_create:
                batch_size = 500
                for i in range(0, len(to_create), batch_size):
                    EntranceTestModuleName.objects.bulk_create(to_create[i:i+batch_size])
                imported_count += len(to_create)

        except Exception as e:
            return Response({'error': str(e)}, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": list(reversed(duplicates)),
            "skipped_rows": list(reversed(skipped_rows))
        }, status=200)



#----------------------------result--------------
# class EntranceTestResultListAPIView(APIView):
#     permission_classes = [IsAuthenticated, IsAdminUser]

#     def get(self, request):
#         search = request.GET.get('search', '').strip()
#         sort_by = request.GET.get('sortBy', 'created_at')
#         sort_order = request.GET.get('sortOrder', 'desc')
#         allowed_sort_fields = ['testresult', 'description', 'created_at']

#         if sort_by not in allowed_sort_fields:
#             sort_by = 'created_at'
#         if sort_order == 'desc':
#             sort_by = f'-{sort_by}'

#         queryset = EntranceTestResult.objects.filter(is_deleted=False)
#         if search:
#             queryset = queryset.filter(
#                 Q(testresult__istartswith=search) |
#                 Q(description__istartswith=search) |
#                 Q(entrancetest__fullname__istartswith=search) |
#                 Q(moduleName__moduleName__istartswith=search)
#             )

#         queryset = queryset.order_by(sort_by)
#         paginator = CustomPagination()
#         result_page = paginator.paginate_queryset(queryset, request)
#         serializer = EntranceTestResultSerializer(result_page, many=True)
#         return paginator.get_paginated_response(serializer.data)



class EntranceTestResultListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        custom_sort = request.GET.get('customSort')
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        uuid_entrance_test_name = request.GET.get('entranceTestName', '')
        uuid_entrance_test_module_name = request.GET.get('entranceTestModuleName', '')

        

        queryset = EntranceTestResult.objects.all()

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

        entrance_test_name_list = parse_uuid_list(uuid_entrance_test_name)
        entrance_test_module_name_list = parse_uuid_list(uuid_entrance_test_module_name)

        if entrance_test_name_list:
            queryset = queryset.filter(entrancetest__uuid__in=entrance_test_name_list)

        if entrance_test_module_name_list:
            queryset = queryset.filter(moduleName__uuid__in=entrance_test_module_name_list)

        # ----------------------
        # SEARCH FILTER
        # ----------------------
        if search:
            queryset = queryset.filter(testresult__istartswith=search)

        # ----------------------
        # SORT FIELD MAP
        # ----------------------
        sort_field_map = {
            "uuid": "uuid",
            "entranceTestName": "entrancetest__fullname",
            "entranceTestModuleName": "moduleName__moduleName",
            "testresult": "testresult",
            "description": "description",
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
                    if field in ["moduleName", "entranceTestName", "description"]:
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
        serializer = EntranceTestResultSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)
    


# -------------------- Create -------------------- #
class EntranceTestResultCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        # Get UUIDs from request
        entrancetest_uuid = request.data.get("entrancetest_id")
        module_uuid = request.data.get("moduleName_id")

        # Fetch the actual foreign key objects
        try:
            entrancetest_obj = EntranceTestName.objects.get(uuid=entrancetest_uuid, is_deleted=False)
        except EntranceTestName.DoesNotExist:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Invalid Entrance Test UUID."
            }, status=400)

        try:
            module_obj = EntranceTestModuleName.objects.get(uuid=module_uuid, is_deleted=False)
        except EntranceTestModuleName.DoesNotExist:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Invalid Module UUID."
            }, status=400)

        # Check duplicates for same entrance test + module
        existing = EntranceTestResult.objects.filter(
            entrancetest=entrancetest_obj,
            moduleName=module_obj,
            is_deleted=False
        ).first()
        if existing:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Result for this test and module already exists."
            }, status=400)

        # Replace UUIDs with actual objects for serializer
        data = request.data.copy()
        data['entrancetest_id'] = entrancetest_obj.uuid
        data['moduleName_id'] = module_obj.uuid

        serializer = EntranceTestResultSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Result created successfully",
                "data": serializer.data
            })

        # Collect errors
        errors = " ".join([msg for msgs in serializer.errors.values() for msg in msgs])
        return Response({
            "statusCode": 400,
            "status": False,
            "message": errors
        }, status=400)


# -------------------- Retrieve -------------------- #
class EntranceTestResultRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = EntranceTestResult.objects.get(uuid=uuid, is_deleted=False)
        except EntranceTestResult.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "Not found", "data": None}, status=404)
        serializer = EntranceTestResultSerializer(obj)
        return Response({"statusCode": 200, "status": True, "message": "Retrieved successfully", "data": serializer.data})


# -------------------- Update -------------------- #
class EntranceTestResultUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = EntranceTestResult.objects.get(uuid=uuid, is_deleted=False)
        except EntranceTestResult.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "Not found", "data": None}, status=404)

        serializer = EntranceTestResultSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"statusCode": 200, "status": True, "message": "Updated successfully", "data": serializer.data})
        errors = " ".join([msg for msgs in serializer.errors.values() for msg in msgs])
        return Response({"statusCode": 400, "status": False, "message": errors}, status=400)


# -------------------- Delete -------------------- #
# class EntranceTestResultDeleteAPIView(APIView):
#     permission_classes = [IsAuthenticated, IsAdminUser]

#     def delete(self, request):
#         ids = request.data.get('id', None)
#         if not ids:
#             return Response({"statusCode": 400, "status": False, "message": "Provide 'id' field", "data": None}, status=400)

#         if ids == "all":
#             objs = EntranceTestResult.objects.filter(is_deleted=False)
#             count = objs.count()
#             objs.delete()
#             return Response({"statusCode": 200, "status": True, "message": f"All {count} result(s) deleted", "data": None})

#         if not isinstance(ids, list):
#             return Response({"statusCode": 400, "status": False, "message": "Provide list of UUIDs", "data": None}, status=400)

#         valid_uuids, invalid_uuids = [], []
#         for u in ids:
#             try:
#                 valid_uuids.append(UUID(u))
#             except ValueError:
#                 invalid_uuids.append(u)

#         objs = EntranceTestResult.objects.filter(uuid__in=valid_uuids, is_deleted=False)
#         count = objs.count()
#         if count == 0:
#             return Response({"statusCode": 404, "status": False, "message": "No matching result found", "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None}, status=404)

#         objs.delete()
#         return Response({"statusCode": 200, "status": True, "message": f"{count} result(s) deleted", "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None})

class EntranceTestResultDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        try:
            # ---------- Query Params ----------
            search = request.GET.get("search", "").strip()
            entrance_test_name_param = request.GET.get("entranceTestName", "").strip()
            entrance_test_module_name_param = request.GET.get("entranceTestModuleName", "").strip()

            # ---------- Parse comma UUIDs ----------
            def parse_uuids(param):
                arr = []
                if param:
                    for u in param.split(","):
                        try:
                            arr.append(UUID(u.strip()))
                        except:
                            pass
                return arr

            entrance_test_name_uuids = parse_uuids(entrance_test_name_param)
            entrance_test_module_name_uuids = parse_uuids(entrance_test_module_name_param)

            # ---------- Body Params ----------
            ids_body = request.data.get("id", None)
            delete_all_flag = request.data.get("deleteAll", False)

            # ---------- Base Queryset ----------
            queryset = EntranceTestResult.objects.filter(is_deleted=False)
            applied_filters = []

            # Apply search
            if search:
                queryset = queryset.filter(testresult__istartswith=search)
                applied_filters.append("search")

            # Apply entranceTestName filter
            if entrance_test_name_uuids:
                queryset = queryset.filter(entrancetest__uuid__in=entrance_test_name_uuids)
                applied_filters.append("entranceTestName")

            # Apply entranceTestModuleName filter
            if entrance_test_module_name_uuids:
                queryset = queryset.filter(moduleName__uuid__in=entrance_test_module_name_uuids)
                applied_filters.append("entranceTestModuleName")

            # ---------- Case 2: Full table delete when id=="all", deleteAll:false, no filters ----------
            if not delete_all_flag and ids_body == "all" and not applied_filters:
                queryset = EntranceTestResult.objects.filter(is_deleted=False)
                total = queryset.count()

                if total == 0:
                    return Response({
                        "statusCode": 404,
                        "status": False,
                        "message": "No records found to delete",
                        "data": None
                    }, status=404)

                try:
                    with transaction.atomic():
                        queryset.delete()
                except IntegrityError:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": "Full table can't be deleted, child reference exists.",
                        "data": None
                    }, status=400)

                return Response({
                    "statusCode": 200,
                    "status": True,
                    "message": f"All {total} result(s) permanently deleted",
                    "data": None
                })

            # ---------- Case 3: Delete UUID list from body ----------
            if not delete_all_flag and isinstance(ids_body, list) and ids_body:
                valid = []
                invalid = []
                for u in ids_body:
                    try:
                        valid.append(UUID(u))
                    except:
                        invalid.append(u)

                if not valid:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": "No valid UUIDs provided.",
                        "data": {"invalid_uuids": invalid}
                    }, status=400)

                qs_delete = queryset.filter(uuid__in=valid)
                count = qs_delete.count()

                if count == 0:
                    return Response({
                        "statusCode": 404,
                        "status": False,
                        "message": "No matching result(s) found",
                        "data": {"invalid_uuids": invalid} if invalid else None
                    }, status=404)

                try:
                    with transaction.atomic():
                        qs_delete.delete()
                except IntegrityError:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": "Can't delete selected dataset, child reference exists.",
                        "data": None
                    }, status=400)

                return Response({
                    "statusCode": 200,
                    "status": True,
                    "message": f"{count} result(s) deleted successfully",
                    "data": {"invalid_uuids": invalid} if invalid else None
                })

            # ---------- Case 4: deleteAll:true with applied filters ----------
            if delete_all_flag and applied_filters:
                count = queryset.count()

                if count == 0:
                    return Response({
                        "statusCode": 404,
                        "status": False,
                        "message": "No result(s) found matching applied filters",
                        "data": None
                    }, status=404)

                try:
                    with transaction.atomic():
                        queryset.delete()
                except IntegrityError:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": "Filtered dataset can't be deleted, child reference exists",
                        "data": None
                    }, status=400)

                return Response({
                    "statusCode": 200,
                    "status": True,
                    "message": f"{count} result(s) deleted based on filters: {', '.join(applied_filters)}",
                    "data": None
                })


            # ---------- Case 4: deleteAll:true with applied filters ----------
            if delete_all_flag and applied_filters and (ids_body in [None, "", []]):
                count = queryset.count()

                if count == 0:
                    return Response({
                        "statusCode": 404,
                        "status": False,
                        "message": "No result(s) found matching applied filters",
                        "data": None
                    }, status=404)

                try:
                    with transaction.atomic():
                        queryset.delete()
                except IntegrityError:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": "Filtered dataset can't be deleted, child reference exists",
                        "data": None
                    }, status=400)

                return Response({
                    "statusCode": 200,
                    "status": True,
                    "message": f"{count} result(s) deleted based on filters: {', '.join(applied_filters)}",
                    "data": None
                })



            # ---------- Case 5: deleteAll:true but no filter applied ----------
            if delete_all_flag and not applied_filters:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "deleteAll:true requires at least one filter to delete",
                    "data": None
                }, status=400)

            # ---------- Final fallback ----------
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Invalid delete request combination",
                "data": None
            }, status=400)

        except Exception as e:
            return Response({
                "statusCode": 500,
                "status": False,
                "message": f"Internal server error: {str(e)}",
                "data": None
            }, status=500)
        



# -------------------- Export -------------------- #
class EntranceTestResultExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        # Field to header mapping
        field_header_map = {
            'uuid': 'UUID',
            'entrancetest': 'Entrance Test Name',
            'moduleName': 'Entrance Test Module Name',
            'testresult': 'Entrance Test Result',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'created_at': 'Created On',
            'updated_at': 'Modified On',
        }

        # Fields to export
        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())

        # Fetch queryset
        queryset = EntranceTestResult.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        # Prepare dataset
        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'EntranceTestResults'

        for obj in queryset:
            row = []
            for field in field_list:
                value = getattr(obj, field, '')
                # Foreign keys
                if field == 'entrancetest' and value:
                    value = value.shortname
                elif field == 'moduleName' and value:
                    value = value.moduleName
                # Datetime formatting
                elif field in ['created_at', 'updated_at'] and value:
                    value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
                # Boolean formatting
                elif isinstance(value, bool):
                    value = int(value)
                row.append(value if value is not None else '')
            dataset.append(row)

        # Export data
        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'entrance_test_results.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'entrance_test_results.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


# class EntranceTestResultImportAPIView(APIView):
#     permission_classes = [IsAuthenticated, IsAdminUser]

#     def post(self, request):
#         file = request.FILES.get('file')
#         sheet_name = request.data.get('sheet_name')

#         if not file:
#             return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

#         format_type = file.name.split('.')[-1].lower()
#         duplicate_entries = []
#         skipped_rows = []

#         required_headers = {'entrance test name', 'entrance test module name', 'entrance test result'}
#         optional_headers = {'description'}

#         try:
#             data = []

#             # XLSX handling
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
#                     return Response({
#                         'error': f'Missing required headers. Required: {required_headers}, Found: {set(headers)}'
#                     }, status=400)

#                 for row in ws.iter_rows(min_row=2, values_only=True):
#                     if not any(row):
#                         continue
#                     row_dict = dict(zip(headers, row))
#                     data.append(row_dict)

#             # CSV handling
#             elif format_type == 'csv':
#                 dataset = Dataset()
#                 dataset.load(file.read().decode('utf-8'), format='csv')
#                 for row in dataset.dict:
#                     row_lower = {k.strip().lower(): v for k, v in row.items()}
#                     if not required_headers.issubset(set(row_lower.keys())):
#                         return Response({
#                             'error': f'Missing required headers. Required: {", ".join(required_headers)}. Found: {", ".join(row_lower.keys())}'
#                         }, status=400)
#                     data.append(row_lower)
#             else:
#                 return Response({'error': 'Unsupported file format. Use .xlsx or .csv'}, status=400)

#             imported_count = 0

#             for row in reversed(data):
#                 entrancetest_name = str(row.get('entrance test name')).strip() if row.get('entrance test name') else None
#                 moduleName_name = str(row.get('entrance test module name')).strip() if row.get('entrance test module name') else None
#                 testresult = str(row.get('entrance test result')).strip() if row.get('entrance test result') else None
#                 description = str(row.get('description')).strip() if row.get('description') else ''

#                 if not entrancetest_name or not moduleName_name or not testresult:
#                     skipped_rows.append({
#                         "row": row,
#                         "reason": "Required field(s) missing"
#                     })
#                     continue

#                 existing = EntranceTestResult.objects.filter(
#                     entrancetest__shortname__iexact=entrancetest_name,
#                     moduleName__moduleName__iexact=moduleName_name
#                 ).first()

#                 if existing:
#                     if not existing.is_deleted:
#                         duplicate_entries.append(f"{entrancetest_name} - {moduleName_name}")
#                         continue
#                     else:
#                         existing.testresult = testresult
#                         existing.description = description
#                         existing.is_deleted = False
#                         existing.save()
#                         imported_count += 1
#                 else:
#                     # Gracefully handle missing EntranceTestName or ModuleName
#                     entrance_obj = EntranceTestName.objects.filter(shortname__iexact=entrancetest_name).first()
#                     module_obj = EntranceTestModuleName.objects.filter(moduleName__iexact=moduleName_name).first()

#                     if not entrance_obj:
#                         skipped_rows.append({
#                             "row": row,
#                             "reason": f'EntranceTestName "{entrancetest_name}" does not exist'
#                         })
#                         continue

#                     if not module_obj:
#                         skipped_rows.append({
#                             "row": row,
#                             "reason": f'EntranceTestModuleName "{moduleName_name}" does not exist'
#                         })
#                         continue

#                     # Create new record
#                     EntranceTestResult.objects.create(
#                         entrancetest=entrance_obj,
#                         moduleName=module_obj,
#                         testresult=testresult,
#                         description=description,
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



class EntranceTestResultImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicates = []
        skipped_rows = []

        required_headers = {'entrance test name', 'entrance test module name', 'entrance test result'}
        optional_headers = {'description'}

        data = []

        try:
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
                    return Response({'error': f'Sheet "{sheet_name}" is empty.'}, status=400)

                headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                if not required_headers.issubset(set(headers)):
                    return Response({'error': f'Missing required headers. Required: {required_headers}, Found: {set(headers)}'}, status=400)

                for row_no, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row):
                        skipped_rows.append({"Row": row_no, "Reason": "Empty row"})
                        continue
                    row_dict = dict(zip(headers, row))
                    row_dict['_row_number'] = row_no
                    data.append(row_dict)

            # ---------------- CSV ----------------
            elif format_type == 'csv':
                decoded_file = file.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(decoded_file))
                for row_no, row in enumerate(reader, start=2):
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    row_lower['_row_number'] = row_no
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({'error': f'Missing required headers. Required: {", ".join(required_headers)}. Found: {", ".join(row_lower.keys())}'}, status=400)
                    if not row_lower.get('entrance test name') or not row_lower.get('entrance test module name') or not row_lower.get('entrance test result'):
                        skipped_rows.append({"Row": row_no, "Reason": "Required field(s) missing"})
                        continue
                    data.append(row_lower)
            else:
                return Response({'error': 'Unsupported file format. Use .xlsx or .csv'}, status=400)

            # ---------------- Process Rows ----------------
            to_create = []
            imported_count = 0

            # Pre-fetch EntranceTestName and ModuleName objects
            all_tests = EntranceTestName.objects.all()
            test_map = {t.shortname.lower(): t for t in all_tests if t.shortname}

            all_modules = EntranceTestModuleName.objects.all()
            module_map = {(m.entrancetest.shortname.lower(), m.moduleName.lower()): m for m in all_modules if m.entrancetest and m.moduleName}

            all_results = EntranceTestResult.objects.select_related('entrancetest', 'moduleName').all()
            existing_map = {(r.entrancetest.shortname.lower(), r.moduleName.moduleName.lower()): r for r in all_results if r.entrancetest and r.moduleName}

            for row in reversed(data):
                row_no = row.get('_row_number', 'Unknown')
                test_name = str(row.get('entrance test name')).strip()
                module_name = str(row.get('entrance test module name')).strip()
                result = str(row.get('entrance test result')).strip()
                description = str(row.get('description')).strip() if row.get('description') else ''

                if not test_name or not module_name or not result:
                    skipped_rows.append({"Row": row_no,"EntranceTest": test_name or "", "Module": module_name or "", "Entrance Test Result":result or "", "Reason": "Required field(s) missing"})
                    continue

                key_module = (test_name.lower(), module_name.lower())
                existing_result = existing_map.get(key_module)

                if existing_result:
                    if not existing_result.is_deleted:
                        duplicates.append({"Row": row_no,"EntranceTest": test_name or "", "Module": module_name or "", "Entrance Test Result":result or "", "Reason": "Already exists"})
                        continue
                    else:
                        existing_result.testresult = result
                        existing_result.description = description
                        existing_result.is_deleted = False
                        existing_result.save()
                        imported_count += 1
                        continue

                test_obj = test_map.get(test_name.lower())
                module_obj = module_map.get(key_module)

                if not test_obj:
                    skipped_rows.append({"Row": row_no, "Reason": f'EntranceTestName "{test_name}" does not exist'})
                    continue
                if not module_obj:
                    skipped_rows.append({"Row": row_no, "Reason": f'EntranceTestModuleName "{module_name}" does not exist'})
                    continue

                to_create.append(EntranceTestResult(
                    entrancetest=test_obj,
                    moduleName=module_obj,
                    testresult=result,
                    description=description,
                    is_deleted=False
                ))

            # Bulk insert in batches
            if to_create:
                batch_size = 500
                for i in range(0, len(to_create), batch_size):
                    EntranceTestResult.objects.bulk_create(to_create[i:i+batch_size])
                imported_count += len(to_create)

        except Exception as e:
            return Response({'error': str(e)}, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": list(reversed(duplicates)),
            "skipped_rows": list(reversed(skipped_rows))
        }, status=200)


