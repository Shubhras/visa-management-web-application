from django.shortcuts import render
from  .models  import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import  *
from django.core.paginator import Paginator
from django.db.models import Q
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

    def delete(self, request, uuid=None):
        uuids = request.data.get('id', None)

        # --- Single delete via URL parameter ---
        if uuid:
            try:
                lang = Language.objects.get(uuid=uuid, is_deleted=False)
                lang.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "Language deleted successfully",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            except Language.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Language not found",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        # --- Delete all if 'all' is passed ---
        if uuids == "all":
            langs = Language.objects.filter(is_deleted=False)
            count = langs.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No Language records found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
            langs.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} Language record(s) deleted successfully.",
                "data": None
            }, status=status.HTTP_200_OK)

        # --- Validate UUID list ---
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

        # --- Bulk delete ---
        langs = Language.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = langs.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching Language records found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_404_NOT_FOUND)

        langs.delete()

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} Language record(s) deleted successfully.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        }, status=status.HTTP_200_OK)


class LanguageListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')  # default to newest first

        allowed_sort_fields = ['name', 'description', 'created_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        # Apply descending order for 'desc'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = Language.objects.filter(is_deleted=False)  
        if search:
            queryset = queryset.filter(
                Q(name__istartswith=search) |
                Q(description__istartswith=search)
            )

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = LanguageSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)





class LanguageExportAPIView(APIView):
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

        # --- Prepare dataset ---
        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'Language Name(Test)'

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
        duplicate_names = []

        # Required & optional headers
        required_headers = {'language name (test)'}
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

                # Validate required headers
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
                    "error": 'Unsupported file format. Use .xlsx or .csv'
                }, status=status.HTTP_400_BAD_REQUEST)

            imported_count = 0

            # ---------- Import Rows ----------
            for row in reversed(data):
                name = str(row.get('language name (test)')).strip() if row.get('language name (test)') else None
                description = str(row.get('description')).strip() if row.get('description') else ''
                is_deleted = row.get('is_deleted', False)

                if not name:
                    continue

                existing = Language.objects.filter(name__iexact=name).first()

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
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": list(set(duplicate_names)),
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count
        }, status=status.HTTP_200_OK)




#--------------------language Test-------------------

class LanguageTestListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')
        allowed_sort_fields = ['name', 'fullname', 'description', 'updated_at']

        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = LanguageTest.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(
                Q(name__istartswith=search) |
                Q(fullname__istartswith=search) |
                Q(description__istartswith=search)
            )

        queryset = queryset.order_by(sort_by)
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

    def delete(self, request, uuid=None):
        uuids = request.data.get('id', None)

        if uuid:
            try:
                obj = LanguageTest.objects.get(uuid=uuid, is_deleted=False)
                obj.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "LanguageTest deleted successfully",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            except LanguageTest.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "LanguageTest not found",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        if uuids == "all":
            objs = LanguageTest.objects.filter(is_deleted=False)
            count = objs.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No LanguageTest records found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
            objs.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} LanguageTest record(s) deleted successfully.",
                "data": None
            }, status=status.HTTP_200_OK)

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

        objs = LanguageTest.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = objs.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching LanguageTest records found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_404_NOT_FOUND)

        objs.delete()
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} LanguageTest record(s) deleted successfully.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        }, status=status.HTTP_200_OK)



class LanguageTestExportAPIView(APIView):
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
            'language': 'Language Name (Test)',
            'name': 'Language Test Name',
            'fullname': 'Language Test Full Name',
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
        queryset = LanguageTest.objects.all()
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

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
        duplicate_names = []

        required_headers = {'language name (test)', 'language test name'}
        optional_headers = {'language test full name', 'description', 'is_deleted'}

        try:
            data = []
            headers = []

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

            for row in reversed(data):
                lang_name = str(row.get('language name (test)')).strip()
                name = str(row.get('language test name')).strip()
                fullname = str(row.get('language test full name')).strip() if row.get('language test full name') else ''
                description = str(row.get('description')).strip() if row.get('description') else ''
                is_deleted = row.get('is_deleted', False)

                language = Language.objects.filter(name__iexact=lang_name, is_deleted=False).first()
                if not language:
                    duplicate_names.append(lang_name)
                    continue

                existing = LanguageTest.objects.filter(name__iexact=name, language=language).first()
                if existing:
                    duplicate_names.append(name)
                    continue

                LanguageTest.objects.create(
                    language=language,
                    name=name,
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

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": list(set(duplicate_names)),
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count
        }, status=status.HTTP_200_OK)








class LanguagetestmoduleNameListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')
        allowed_sort_fields = ['name', 'description', 'created_at']

        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = LanguagetestmoduleName.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(
                Q(name__istartswith=search) |
                Q(description__istartswith=search)
            )

        queryset = queryset.order_by(sort_by)
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



class LanguagetestmoduleNameDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        uuids = request.data.get('id', None)

        if uuid:
            try:
                obj = LanguagetestmoduleName.objects.get(uuid=uuid, is_deleted=False)
                obj.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "Module deleted successfully",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            except LanguagetestmoduleName.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Module not found",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        if uuids == "all":
            objs = LanguagetestmoduleName.objects.filter(is_deleted=False)
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
                "message": f"All {count} records deleted successfully.",
                "data": None
            }, status=status.HTTP_200_OK)

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

        objs = LanguagetestmoduleName.objects.filter(uuid__in=valid_uuids, is_deleted=False)
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
            "message": f"{count} record(s) deleted successfully.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        }, status=status.HTTP_200_OK)


        
class LanguagetestmoduleNameExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')

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





class LanguageTestResultListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')
        allowed_sort_fields = ['numeric_score', 'description', 'created_at']

        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = LanguageTestResult.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(
                Q(numeric_score__istartswith=search) |
                Q(description__istartswith=search) |
                Q(language_test__name__istartswith=search) |
                Q(languagetest_module_name__moduleName__istartswith=search)
            )

        queryset = queryset.order_by(sort_by)
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
        clb_uuid = request.data.get("clb_level_id")

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
            clb_obj = CLBLevel.objects.get(uuid=clb_uuid)
        except CLBLevel.DoesNotExist:
            return Response({"statusCode": 400, "status": False, "message": "Invalid CLB Level UUID"}, status=400)

        # Check duplicate
        existing = LanguageTestResult.objects.filter(
            language=language_obj,
            language_test=language_test_obj,
            languagetest_module_name=module_obj,
            clb_level=clb_obj,
            is_deleted=False
        ).first()
        if existing:
            return Response({"statusCode": 400, "status": False, "message": "Result already exists."}, status=400)

        data = request.data.copy()
        data['language_id'] = language_obj.uuid
        data['language_test_id'] = language_test_obj.uuid
        data['module_name_id'] = module_obj.uuid
        data['clb_level_id'] = clb_obj.uuid

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
        ids = request.data.get('id', None)
        if not ids:
            return Response({"statusCode": 400, "status": False, "message": "Provide 'id' field", "data": None}, status=400)

        if ids == "all":
            objs = LanguageTestResult.objects.filter(is_deleted=False)
            count = objs.count()
            objs.delete()
            return Response({"statusCode": 200, "status": True, "message": f"All {count} result(s) deleted", "data": None})

        if not isinstance(ids, list):
            return Response({"statusCode": 400, "status": False, "message": "Provide list of UUIDs", "data": None}, status=400)

        valid_uuids, invalid_uuids = [], []
        for u in ids:
            try:
                valid_uuids.append(UUID(u))
            except ValueError:
                invalid_uuids.append(u)

        objs = LanguageTestResult.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = objs.count()
        if count == 0:
            return Response({"statusCode": 404, "status": False, "message": "No matching result found", "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None}, status=404)

        objs.delete()
        return Response({"statusCode": 200, "status": True, "message": f"{count} result(s) deleted", "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None})


class LanguageTestResultExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        # Field to header mapping
        field_header_map = {
            'uuid': 'UUID',
            'language': 'Language',
            'language_test': 'Language Test',
            'languagetest_module_name': 'Module Name',
            'clb_level': 'CLB Level',
            'numeric_score': 'Numeric Score',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'created_at': 'Created On',
            'updated_at': 'Modified On',
        }

        # Fields to export
        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())

        # Fetch queryset
        queryset = LanguageTestResult.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        # Prepare dataset
        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'Language Test Results'

        for obj in queryset:
            row = []
            for field in field_list:
                value = getattr(obj, field, '')
                # Foreign keys formatting
                if field == 'language' and value:
                    value = value.name
                elif field == 'language_test' and value:
                    value = value.name
                elif field == 'languagetest_module_name' and value:
                    value = value.moduleName
                elif field == 'clb_level' and value:
                    value = value.name
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
            file_name = 'language_test_results.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'language_test_results.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response
    
# -------------------- Import -------------------- #
class LanguageTestResultImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')
        if not file:
            return Response({'error': 'No file uploaded'}, status=400)

        format_type = file.name.split('.')[-1].lower()
        duplicate_entries, skipped_rows, imported_count = [], [], 0

        required_headers = {'language', 'language test', 'language test module name', 'clb level', 'numeric score'}
        optional_headers = {'description'}

        try:
            data = []

            if format_type == 'xlsx':
                wb = openpyxl.load_workbook(file, read_only=True)
                if not sheet_name:
                    return Response({'error': 'Provide sheet_name', 'available_sheets': wb.sheetnames}, status=400)
                if sheet_name not in wb.sheetnames:
                    return Response({'error': f'Sheet "{sheet_name}" not found', 'available_sheets': wb.sheetnames}, status=400)
                ws = wb[sheet_name]
                headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                if not required_headers.issubset(set(headers)):
                    return Response({'error': f'Missing required headers. Required: {required_headers}, Found: {set(headers)}'}, status=400)

                for row in ws.iter_rows(min_row=2, values_only=True):
                    if not any(row):
                        continue
                    data.append(dict(zip(headers, row)))

            elif format_type == 'csv':
                dataset = Dataset()
                dataset.load(file.read().decode('utf-8'), format='csv')
                for row in dataset.dict:
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({'error': f'Missing required headers'}, status=400)
                    data.append(row_lower)
            else:
                return Response({'error': 'Unsupported file format'}, status=400)

            for row in reversed(data):
                language_name = str(row.get('language')).strip()
                language_test_name = str(row.get('language test')).strip()
                module_name = str(row.get('module name')).strip()
                clb_level_name = str(row.get('clb level')).strip()
                numeric_score = row.get('numeric score')
                description = row.get('description', '')

                if not (language_name and language_test_name and module_name and clb_level_name and numeric_score):
                    skipped_rows.append({"row": row, "reason": "Required field(s) missing"})
                    continue

                existing = LanguageTestResult.objects.filter(
                    language__name__iexact=language_name,
                    language_test__name__iexact=language_test_name,
                    languagetest_module_name__moduleName__iexact=module_name,
                    clb_level__name__iexact=clb_level_name
                ).first()

                if existing and not existing.is_deleted:
                    duplicate_entries.append(f"{language_name} - {language_test_name} - {module_name} - {clb_level_name}")
                    continue

                language_obj = Language.objects.filter(name__iexact=language_name).first()
                language_test_obj = LanguageTest.objects.filter(name__iexact=language_test_name).first()
                module_obj = LanguagetestmoduleName.objects.filter(moduleName__iexact=module_name).first()
                clb_obj = CLBLevel.objects.filter(name__iexact=clb_level_name).first()

                if not (language_obj and language_test_obj and module_obj and clb_obj):
                    skipped_rows.append({"row": row, "reason": "Invalid FK reference"})
                    continue

                if existing and existing.is_deleted:
                    existing.numeric_score = numeric_score
                    existing.description = description
                    existing.is_deleted = False
                    existing.save()
                else:
                    LanguageTestResult.objects.create(
                        language=language_obj,
                        language_test=language_test_obj,
                        languagetest_module_name=module_obj,
                        clb_level=clb_obj,
                        numeric_score=numeric_score,
                        description=description
                    )
                imported_count += 1

        except Exception as e:
            return Response({'error': str(e)}, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": list(set(duplicate_entries)),
            "skipped_rows": skipped_rows,
            "imported_count": imported_count,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful"
        }, status=200)






class CLBLevelListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')
        allowed_sort_fields = ['name', 'description', 'created_at']

        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = CLBLevel.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(
                Q(name__istartswith=search) |
                Q(description__istartswith=search)
            )

        queryset = queryset.order_by(sort_by)
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


class CLBLevelDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        ids = request.data.get('id', None)
        if not ids:
            return Response({"statusCode": 400, "status": False, "message": "Provide 'id' field", "data": None}, status=400)

        if ids == "all":
            objs = CLBLevel.objects.filter(is_deleted=False)
            count = objs.count()
            objs.delete()
            return Response({"statusCode": 200, "status": True, "message": f"All {count} CLB Level(s) deleted", "data": None})

        if not isinstance(ids, list):
            return Response({"statusCode": 400, "status": False, "message": "Provide list of UUIDs", "data": None}, status=400)

        valid_uuids, invalid_uuids = [], []
        for u in ids:
            try:
                valid_uuids.append(UUID(u))
            except ValueError:
                invalid_uuids.append(u)

        objs = CLBLevel.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = objs.count()
        if count == 0:
            return Response({"statusCode": 404, "status": False, "message": "No matching CLB Level found", "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None}, status=404)

        objs.delete()
        return Response({"statusCode": 200, "status": True, "message": f"{count} CLB Level(s) deleted", "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None})


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
        dataset.title = 'CLB Level'

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
        duplicate_names = []

        # Define required and optional headers
        required_headers = {'clb level'}           # must be present
        optional_headers = {'description'}    # optional

        try:
            data = []
            headers = []

            # ---------- XLSX Handling ----------
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

                if not data:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'The uploaded XLSX file (sheet: "{sheet_name}") is empty. Provide at least one data row.'
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
                        "message": "The uploaded CSV file is empty. Provide at least one data row."
                    }, status=status.HTTP_400_BAD_REQUEST)

            else:
                return Response({
                    "statusCode": 400,
                    "status": True,
                    'error': 'Unsupported file format. Use .xlsx or .csv'
                }, status=status.HTTP_400_BAD_REQUEST)

            imported_count = 0

            # ---------- Import Rows ----------
            for row in reversed(data):
                name = str(row.get('clb level')).strip() if row.get('clb level') else None
                description = str(row.get('description')).strip() if row.get('description') else ''

                if not name:
                    continue  # skip rows without name

                existing = CLBLevel.objects.filter(name__iexact=name).first()

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
                    CLBLevel.objects.create(
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




class StudyLanguageBanchmarkListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')
        allowed_sort_fields = ['name', 'description', 'created_at']

        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = StudyLanguageBanchmark.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(
                Q(name__istartswith=search) |
                Q(description__istartswith=search)
            )

        queryset = queryset.order_by(sort_by)
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


class StudyLanguageBanchmarkDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        ids = request.data.get('id', None)
        if not ids:
            return Response({"statusCode": 400, "status": False, "message": "Provide 'id' field", "data": None}, status=400)

        if ids == "all":
            objs = StudyLanguageBanchmark.objects.filter(is_deleted=False)
            count = objs.count()
            objs.delete()
            return Response({"statusCode": 200, "status": True, "message": f"All {count} benchmark(s) deleted", "data": None})

        if not isinstance(ids, list):
            return Response({"statusCode": 400, "status": False, "message": "Provide list of UUIDs", "data": None}, status=400)

        valid_uuids, invalid_uuids = [], []
        for u in ids:
            try:
                valid_uuids.append(UUID(u))
            except ValueError:
                invalid_uuids.append(u)

        objs = StudyLanguageBanchmark.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = objs.count()
        if count == 0:
            return Response({"statusCode": 404, "status": False, "message": "No matching benchmark found", "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None}, status=404)

        objs.delete()
        return Response({"statusCode": 200, "status": True, "message": f"{count} benchmark(s) deleted", "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None})


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
        dataset.title = 'Language Benchmark Level'

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
        duplicate_names = []

        required_headers = {'language banchmark level'}  # must be present
        optional_headers = {'description'}         # optional

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
                        "message": f'The uploaded XLSX file (sheet: "{sheet_name}") is empty.'
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
                            "message": (
                                f'Missing required headers. Required: {", ".join(required_headers)}. '
                                f'Found headers in the file: {", ".join(row_lower.keys())}.'
                            )
                        }, status=status.HTTP_400_BAD_REQUEST)
                    data.append(row_lower)

            else:
                return Response({
                    "statusCode": 400,
                    "status": True,
                    'error': 'Unsupported file format. Use .xlsx or .csv'
                }, status=status.HTTP_400_BAD_REQUEST)

            imported_count = 0

            # ---------- Import Rows ----------
            for row in reversed(data):
                name = str(row.get('language banchmark level')).strip() if row.get('language banchmark level') else None
                description = str(row.get('description')).strip() if row.get('description') else ''

                if not name:
                    continue

                existing = StudyLanguageBanchmark.objects.filter(name__iexact=name).first()

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
                    StudyLanguageBanchmark.objects.create(
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







class EntranceTestNameListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')
        allowed_sort_fields = ['fullname', 'shortname', 'description', 'updated_at']

        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = EntranceTestName.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(
                Q(fullname__istartswith=search) |
                Q(shortname__istartswith=search) |
                Q(description__istartswith=search)
            )

        queryset = queryset.order_by(sort_by)
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


class EntranceTestNameDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        ids = request.data.get('id', None)
        if not ids:
            return Response({"statusCode": 400, "status": False, "message": "Provide 'id' field", "data": None}, status=400)

        if ids == "all":
            objs = EntranceTestName.objects.filter(is_deleted=False)
            count = objs.count()
            objs.delete()
            return Response({"statusCode": 200, "status": True, "message": f"All {count} entrance test(s) deleted", "data": None})

        if not isinstance(ids, list):
            return Response({"statusCode": 400, "status": False, "message": "Provide list of UUIDs", "data": None}, status=400)

        valid_uuids, invalid_uuids = [], []
        for u in ids:
            try:
                valid_uuids.append(UUID(u))
            except ValueError:
                invalid_uuids.append(u)

        objs = EntranceTestName.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = objs.count()
        if count == 0:
            return Response({"statusCode": 404, "status": False, "message": "No matching entrance test found", "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None}, status=404)

        objs.delete()
        return Response({"statusCode": 200, "status": True, "message": f"{count} entrance test(s) deleted", "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None})


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
        dataset.title = 'Entrance Test Name'

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
        duplicate_names = []

        required_headers = {'entrance test full name'}  # Must exist
        optional_headers = {'entrance test name', 'description'}

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
                dataset = Dataset()
                dataset.load(file.read().decode('utf-8'), format='csv')
                for row in dataset.dict:
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
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

            else:
                return Response({
                    "statusCode": 400,
                    "status": True,
                    'error': 'Unsupported file format. Use .xlsx or .csv'
                }, status=status.HTTP_400_BAD_REQUEST)

            imported_count = 0

            # ---------- Import Rows ----------
            for row in reversed(data):
                fullname = str(row.get('entrance test full name')).strip() if row.get('entrance test full name') else None
                shortname = str(row.get('entrance test name')).strip() if row.get('entrance test name') else ''
                description = str(row.get('description')).strip() if row.get('description') else ''

                if not fullname:
                    continue

                existing = EntranceTestName.objects.filter(fullname__iexact=fullname, shortname__iexact=shortname).first()

                if existing:
                    if not existing.is_deleted:
                        duplicate_names.append(fullname)
                        continue
                    else:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    EntranceTestName.objects.create(
                        fullname=fullname,
                        shortname=shortname,
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



#---------------------------------------modulename-----------------------------    

class EntranceTestModuleNameListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')
        allowed_sort_fields = ['moduleName', 'description', 'created_at']

        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = EntranceTestModuleName.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(
                Q(moduleName__istartswith=search) |
                Q(description__istartswith=search)
            )

        queryset = queryset.order_by(sort_by)
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
class EntranceTestModuleNameDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        ids = request.data.get('id', None)
        if not ids:
            return Response({"statusCode": 400, "status": False, "message": "Provide 'id' field", "data": None}, status=400)

        if ids == "all":
            objs = EntranceTestModuleName.objects.filter(is_deleted=False)
            count = objs.count()
            objs.delete()
            return Response({"statusCode": 200, "status": True, "message": f"All {count} module(s) deleted", "data": None})

        if not isinstance(ids, list):
            return Response({"statusCode": 400, "status": False, "message": "Provide list of UUIDs", "data": None}, status=400)

        valid_uuids, invalid_uuids = [], []
        for u in ids:
            try:
                valid_uuids.append(UUID(u))
            except ValueError:
                invalid_uuids.append(u)

        objs = EntranceTestModuleName.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = objs.count()
        if count == 0:
            return Response({"statusCode": 404, "status": False, "message": "No matching module found", "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None}, status=404)

        objs.delete()
        return Response({"statusCode": 200, "status": True, "message": f"{count} module(s) deleted", "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None})


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
        dataset.title = 'Entrance Test Modules'

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
        duplicate_entries = []
        required_headers = {'entrance test name', 'entrance test module name'}
        optional_headers = {'description'}

        try:
            data = []

            # XLSX handling
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
                    return Response({
                        'error': f'Missing required headers. Required: {required_headers}, Found: {set(headers)}'
                    }, status=400)

                for row in ws.iter_rows(min_row=2, values_only=True):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    data.append(row_dict)

            # CSV handling
            elif format_type == 'csv':
                dataset = Dataset()
                dataset.load(file.read().decode('utf-8'), format='csv')
                for row in dataset.dict:
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({
                            'error': f'Missing required headers. Required: {", ".join(required_headers)}. Found: {", ".join(row_lower.keys())}'
                        }, status=400)
                    data.append(row_lower)
            else:
                return Response({'error': 'Unsupported file format. Use .xlsx or .csv'}, status=400)

            imported_count = 0

            for row in reversed(data):
                entrancetest_name = str(row.get('entrance test name')).strip() if row.get('entrance test name') else None
                module_name = str(row.get('entrance test module name')).strip() if row.get('entrance test module name') else None
                description = str(row.get('description')).strip() if row.get('description') else ''

                if not entrancetest_name or not module_name:
                    continue

                entrancetest_obj = EntranceTestName.objects.filter(shortname__iexact=entrancetest_name).first()
                if not entrancetest_obj:
                    continue

                existing = EntranceTestModuleName.objects.filter(
                    entrancetest=entrancetest_obj,
                    moduleName__iexact=module_name
                ).first()

                if existing:
                    if not existing.is_deleted:
                        duplicate_entries.append(f"{entrancetest_name} - {module_name}")
                        continue
                    else:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    EntranceTestModuleName.objects.create(
                        entrancetest=entrancetest_obj,
                        moduleName=module_name,
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
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count
        }, status=200)



#----------------------------result--------------
class EntranceTestResultListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')
        allowed_sort_fields = ['testresult', 'description', 'created_at']

        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = EntranceTestResult.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(
                Q(testresult__istartswith=search) |
                Q(description__istartswith=search) |
                Q(entrancetest__fullname__istartswith=search) |
                Q(moduleName__moduleName__istartswith=search)
            )

        queryset = queryset.order_by(sort_by)
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
class EntranceTestResultDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        ids = request.data.get('id', None)
        if not ids:
            return Response({"statusCode": 400, "status": False, "message": "Provide 'id' field", "data": None}, status=400)

        if ids == "all":
            objs = EntranceTestResult.objects.filter(is_deleted=False)
            count = objs.count()
            objs.delete()
            return Response({"statusCode": 200, "status": True, "message": f"All {count} result(s) deleted", "data": None})

        if not isinstance(ids, list):
            return Response({"statusCode": 400, "status": False, "message": "Provide list of UUIDs", "data": None}, status=400)

        valid_uuids, invalid_uuids = [], []
        for u in ids:
            try:
                valid_uuids.append(UUID(u))
            except ValueError:
                invalid_uuids.append(u)

        objs = EntranceTestResult.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = objs.count()
        if count == 0:
            return Response({"statusCode": 404, "status": False, "message": "No matching result found", "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None}, status=404)

        objs.delete()
        return Response({"statusCode": 200, "status": True, "message": f"{count} result(s) deleted", "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None})


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
        dataset.title = 'Entrance Test Results'

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


class EntranceTestResultImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicate_entries = []
        skipped_rows = []

        required_headers = {'entrance test name', 'entrance test module name', 'entrance test result'}
        optional_headers = {'description'}

        try:
            data = []

            # XLSX handling
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
                    return Response({
                        'error': f'Missing required headers. Required: {required_headers}, Found: {set(headers)}'
                    }, status=400)

                for row in ws.iter_rows(min_row=2, values_only=True):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    data.append(row_dict)

            # CSV handling
            elif format_type == 'csv':
                dataset = Dataset()
                dataset.load(file.read().decode('utf-8'), format='csv')
                for row in dataset.dict:
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({
                            'error': f'Missing required headers. Required: {", ".join(required_headers)}. Found: {", ".join(row_lower.keys())}'
                        }, status=400)
                    data.append(row_lower)
            else:
                return Response({'error': 'Unsupported file format. Use .xlsx or .csv'}, status=400)

            imported_count = 0

            for row in reversed(data):
                entrancetest_name = str(row.get('entrance test name')).strip() if row.get('entrance test name') else None
                moduleName_name = str(row.get('entrance test module name')).strip() if row.get('entrance test module name') else None
                testresult = str(row.get('entrance test result')).strip() if row.get('entrance test result') else None
                description = str(row.get('description')).strip() if row.get('description') else ''

                if not entrancetest_name or not moduleName_name or not testresult:
                    skipped_rows.append({
                        "row": row,
                        "reason": "Required field(s) missing"
                    })
                    continue

                existing = EntranceTestResult.objects.filter(
                    entrancetest__shortname__iexact=entrancetest_name,
                    moduleName__moduleName__iexact=moduleName_name
                ).first()

                if existing:
                    if not existing.is_deleted:
                        duplicate_entries.append(f"{entrancetest_name} - {moduleName_name}")
                        continue
                    else:
                        existing.testresult = testresult
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    # Gracefully handle missing EntranceTestName or ModuleName
                    entrance_obj = EntranceTestName.objects.filter(shortname__iexact=entrancetest_name).first()
                    module_obj = EntranceTestModuleName.objects.filter(moduleName__iexact=moduleName_name).first()

                    if not entrance_obj:
                        skipped_rows.append({
                            "row": row,
                            "reason": f'EntranceTestName "{entrancetest_name}" does not exist'
                        })
                        continue

                    if not module_obj:
                        skipped_rows.append({
                            "row": row,
                            "reason": f'EntranceTestModuleName "{moduleName_name}" does not exist'
                        })
                        continue

                    # Create new record
                    EntranceTestResult.objects.create(
                        entrancetest=entrance_obj,
                        moduleName=module_obj,
                        testresult=testresult,
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


