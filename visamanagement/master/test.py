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

        objs = Language.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = objs.count()
        objs.update(is_deleted=True)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} Language(s) deleted successfully",
            "invalid_uuids": invalid_uuids
        })


# -------------------- LIST -------------------- #
class LanguageListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        queryset = Language.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )

        queryset = queryset.order_by('-created_at')
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = LanguageSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class LanguageExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'csv').lower()
        fields = request.GET.get('fields')  
        uuids_param = request.GET.get('uuids', '')

        uuids = [u.strip() for u in uuids_param.split(',') if u]

        if fields:
            field_list = [f.strip() for f in fields.split(',')]
        else:
            field_list = ['uuid', 'name', 'description', 'is_deleted', 'created_at', 'updated_at']

        if uuids:
            queryset = Language.objects.filter(uuid__in=uuids)
        else:
            queryset = Language.objects.all()

        dataset = Dataset()
        dataset.headers = field_list

        for obj in queryset:
            row = []
            for field in field_list:
                value = getattr(obj, field, '')
                if isinstance(value, datetime.datetime):
                    value = value.strftime("%Y-%m-%d %H:%M:%S")
                if isinstance(value, bool):
                    value = int(value)
                row.append(value if value is not None else '')
            dataset.append(row)

        if format_type == 'xlsx':
            data = XLSX().export_data(dataset)
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'languages.xlsx'
        else:
            data = CSV().export_data(dataset)
            content_type = 'text/csv; charset=utf-8'
            file_name = 'languages.csv'

        response = HttpResponse(data, content_type=content_type)
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

        try:
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
                data = []
                headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                for row in ws.iter_rows(min_row=2, values_only=True):
                    data.append(dict(zip(headers, row)))

                for row in data:
                    name = str(row.get('name')).strip() if row.get('name') else None
                    if not name:
                        continue
                    if Language.objects.filter(name__iexact=name).exists():
                        duplicate_names.append(name)
                        continue
                    Language.objects.create(
                        name=name,
                        description=row.get('description', ''),
                        is_deleted=row.get('is_deleted', False)
                    )

            else:  # CSV
                dataset = Dataset().load(file.read().decode('utf-8'), format='csv')
                for row in dataset.dict:
                    name = str(row.get('name')).strip() if row.get('name') else None
                    if not name:
                        continue
                    if Language.objects.filter(name__iexact=name).exists():
                        duplicate_names.append(name)
                        continue
                    Language.objects.create(
                        name=name,
                        description=row.get('description', ''),
                        is_deleted=row.get('is_deleted', False)
                    )

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": list(set(duplicate_names)),
            'message': f'Sheet "{sheet_name}" imported successfully' if sheet_name else 'Import successful'
        })



class LanguageTestListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')
        allowed_sort_fields = ['name', 'fullname', 'description', 'created_at']

        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = LanguageTest.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(fullname__icontains=search) |
                Q(description__icontains=search)
            )

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = LanguageTestSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class LanguageTestCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        name = request.data.get("name", "").strip()
        existing = LanguageTest.objects.filter(name__iexact=name, is_deleted=False).first()
        if existing:
            return Response({"statusCode": 400, "status": False, "message": "LanguageTest with this name already exists."}, status=400)

        serializer = LanguageTestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"statusCode": 200, "status": True, "message": "LanguageTest created successfully", "data": serializer.data})
        else:
            errors = " ".join([msg for msgs in serializer.errors.values() for msg in msgs])
            return Response({"statusCode": 400, "status": False, "message": errors}, status=400)


class LanguageTestRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = LanguageTest.objects.get(uuid=uuid, is_deleted=False)
        except LanguageTest.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "Not found", "data": None}, status=404)
        serializer = LanguageTestSerializer(obj)
        return Response({"statusCode": 200, "status": True, "message": "Retrieved successfully", "data": serializer.data})


class LanguageTestUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = LanguageTest.objects.get(uuid=uuid, is_deleted=False)
        except LanguageTest.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "Not found", "data": None}, status=404)

        serializer = LanguageTestSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"statusCode": 200, "status": True, "message": "Updated successfully", "data": serializer.data})
        errors = " ".join([msg for msgs in serializer.errors.values() for msg in msgs])
        return Response({"statusCode": 400, "status": False, "message": errors}, status=400)


class LanguageTestDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        ids = request.data.get('id', None)
        if not ids:
            return Response({"statusCode": 400, "status": False, "message": "Provide 'id' field", "data": None}, status=400)

        if ids == "all":
            objs = LanguageTest.objects.filter(is_deleted=False)
            count = objs.count()
            objs.update(is_deleted=True)
            return Response({"statusCode": 200, "status": True, "message": f"All {count} LanguageTest(s) deleted", "data": None})

        if not isinstance(ids, list):
            return Response({"statusCode": 400, "status": False, "message": "Provide list of UUIDs", "data": None}, status=400)

        valid_uuids, invalid_uuids = [], []
        for u in ids:
            try:
                valid_uuids.append(UUID(u))
            except ValueError:
                invalid_uuids.append(u)

        objs = LanguageTest.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = objs.count()
        if count == 0:
            return Response({"statusCode": 404, "status": False, "message": "No matching LanguageTest found", "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None}, status=404)

        objs.update(is_deleted=True)
        return Response({"statusCode": 200, "status": True, "message": f"{count} LanguageTest(s) deleted", "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None})


class LanguageTestExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'csv').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]
        field_list = [f.strip() for f in fields.split(',')] if fields else ['uuid', 'name', 'fullname', 'description', 'is_deleted', 'created_at', 'updated_at']
        queryset = LanguageTest.objects.filter(uuid__in=uuids) if uuids else LanguageTest.objects.all()

        dataset = Dataset()
        dataset.headers = field_list
        for obj in queryset:
            row = []
            for field in field_list:
                value = getattr(obj, field, '')
                if isinstance(value, datetime.datetime):
                    value = value.strftime("%Y-%m-%d %H:%M:%S")
                if isinstance(value, bool):
                    value = int(value)
                row.append(value if value is not None else '')
            dataset.append(row)

        if format_type == 'xlsx':
            data = XLSX().export_data(dataset)
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'languagetest.xlsx'
        else:
            data = CSV().export_data(dataset)
            content_type = 'text/csv; charset=utf-8'
            file_name = 'languagetest.csv'

        response = HttpResponse(data, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


class LanguageTestImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')
        if not file:
            return Response({'error': 'No file uploaded'}, status=400)

        format_type = file.name.split('.')[-1].lower()
        dataset = Dataset()
        duplicate_names = []

        try:
            if format_type == 'xlsx':
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames
                if not sheet_name:
                    return Response({'error': 'Provide sheet_name', 'available_sheets': available_sheets}, status=400)
                if sheet_name not in available_sheets:
                    return Response({'error': f'Sheet "{sheet_name}" not found', 'available_sheets': available_sheets}, status=400)

                ws = wb[sheet_name]
                headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                data = [dict(zip(headers, row)) for row in ws.iter_rows(min_row=2, values_only=True)]

            elif format_type == 'csv':
                dataset.load(file.read().decode('utf-8'), format='csv')
                data = dataset.dict
            else:
                return Response({'error': 'Unsupported format'}, status=400)

            for row in data:
                name = str(row.get('name')).strip() if row.get('name') else None
                fullname = str(row.get('fullname')).strip() if row.get('fullname') else ''
                description = str(row.get('description')).strip() if row.get('description') else ''

                if not name:
                    continue

                existing = LanguageTest.objects.filter(name__iexact=name).first()
                if existing:
                    if existing.is_deleted:
                        LanguageTest.objects.create(name=name, fullname=fullname, description=description, is_deleted=False)
                    else:
                        duplicate_names.append(name)
                        continue
                else:
                    LanguageTest.objects.create(name=name, fullname=fullname, description=description, is_deleted=False)

        except Exception as e:
            return Response({'error': str(e)}, status=400)

        return Response({"statusCode": 200, "status": True, "duplicates": list(set(duplicate_names)), "message": f'Import successful'}, status=200)











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
                Q(name__icontains=search) |
                Q(description__icontains=search)
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
            return Response({"statusCode": 404, "status": False, "message": "Not found", "data": None}, status=404)

        serializer = LanguagetestmoduleNameSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"statusCode": 200, "status": True, "message": "Updated successfully", "data": serializer.data})
        errors = " ".join([msg for msgs in serializer.errors.values() for msg in msgs])
        return Response({"statusCode": 400, "status": False, "message": errors}, status=400)


class LanguagetestmoduleNameDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        ids = request.data.get('id', None)
        if not ids:
            return Response({"statusCode": 400, "status": False, "message": "Provide 'id' field", "data": None}, status=400)

        if ids == "all":
            objs = LanguagetestmoduleName.objects.filter(is_deleted=False)
            count = objs.count()
            objs.update(is_deleted=True)
            return Response({"statusCode": 200, "status": True, "message": f"All {count} module(s) deleted", "data": None})

        if not isinstance(ids, list):
            return Response({"statusCode": 400, "status": False, "message": "Provide list of UUIDs", "data": None}, status=400)

        valid_uuids, invalid_uuids = [], []
        for u in ids:
            try:
                valid_uuids.append(UUID(u))
            except ValueError:
                invalid_uuids.append(u)

        objs = LanguagetestmoduleName.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = objs.count()
        if count == 0:
            return Response({"statusCode": 404, "status": False, "message": "No matching module found", "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None}, status=404)

        objs.update(is_deleted=True)
        return Response({"statusCode": 200, "status": True, "message": f"{count} module(s) deleted", "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None})


class LanguagetestmoduleNameExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'csv').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]
        field_list = [f.strip() for f in fields.split(',')] if fields else ['uuid', 'name', 'description', 'is_deleted', 'created_at', 'updated_at']
        queryset = LanguagetestmoduleName.objects.filter(uuid__in=uuids) if uuids else LanguagetestmoduleName.objects.all()

        dataset = Dataset()
        dataset.headers = field_list
        for obj in queryset:
            row = []
            for field in field_list:
                value = getattr(obj, field, '')
                if isinstance(value, datetime.datetime):
                    value = value.strftime("%Y-%m-%d %H:%M:%S")
                if isinstance(value, bool):
                    value = int(value)
                row.append(value if value is not None else '')
            dataset.append(row)

        if format_type == 'xlsx':
            data = XLSX().export_data(dataset)
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'languagetestmodule.xlsx'
        else:
            data = CSV().export_data(dataset)
            content_type = 'text/csv; charset=utf-8'
            file_name = 'languagetestmodule.csv'

        response = HttpResponse(data, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


class LanguagetestmoduleNameImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')
        if not file:
            return Response({'error': 'No file uploaded'}, status=400)

        format_type = file.name.split('.')[-1].lower()
        dataset = Dataset()
        duplicate_names = []

        try:
            if format_type == 'xlsx':
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames
                if not sheet_name:
                    return Response({'error': 'Provide sheet_name', 'available_sheets': available_sheets}, status=400)
                if sheet_name not in available_sheets:
                    return Response({'error': f'Sheet "{sheet_name}" not found', 'available_sheets': available_sheets}, status=400)

                ws = wb[sheet_name]
                headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                data = [dict(zip(headers, row)) for row in ws.iter_rows(min_row=2, values_only=True)]

            elif format_type == 'csv':
                dataset.load(file.read().decode('utf-8'), format='csv')
                data = dataset.dict
            else:
                return Response({'error': 'Unsupported format'}, status=400)

            for row in data:
                name = str(row.get('name')).strip() if row.get('name') else None
                description = str(row.get('description')).strip() if row.get('description') else ''

                if not name:
                    continue

                existing = LanguagetestmoduleName.objects.filter(name__iexact=name).first()
                if existing:
                    if existing.is_deleted:
                        LanguagetestmoduleName.objects.create(name=name, description=description, is_deleted=False)
                    else:
                        duplicate_names.append(name)
                        continue
                else:
                    LanguagetestmoduleName.objects.create(name=name, description=description, is_deleted=False)

        except Exception as e:
            return Response({'error': str(e)}, status=400)

        return Response({"statusCode": 200, "status": True, "duplicates": list(set(duplicate_names)), "message": f'Import successful'}, status=200)


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
                Q(name__icontains=search) |
                Q(description__icontains=search)
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
            objs.update(is_deleted=True)
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

        objs.update(is_deleted=True)
        return Response({"statusCode": 200, "status": True, "message": f"{count} CLB Level(s) deleted", "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None})


class CLBLevelExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'csv').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]
        field_list = [f.strip() for f in fields.split(',')] if fields else ['uuid', 'name', 'description', 'is_deleted', 'created_at', 'updated_at']
        queryset = CLBLevel.objects.filter(uuid__in=uuids) if uuids else CLBLevel.objects.all()

        dataset = Dataset()
        dataset.headers = field_list
        for obj in queryset:
            row = []
            for field in field_list:
                value = getattr(obj, field, '')
                if isinstance(value, datetime.datetime):
                    value = value.strftime("%Y-%m-%d %H:%M:%S")
                if isinstance(value, bool):
                    value = int(value)
                row.append(value if value is not None else '')
            dataset.append(row)

        if format_type == 'xlsx':
            data = XLSX().export_data(dataset)
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'clblevel.xlsx'
        else:
            data = CSV().export_data(dataset)
            content_type = 'text/csv; charset=utf-8'
            file_name = 'clblevel.csv'

        response = HttpResponse(data, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


class CLBLevelImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')
        if not file:
            return Response({'error': 'No file uploaded'}, status=400)

        format_type = file.name.split('.')[-1].lower()
        dataset = Dataset()
        duplicate_names = []

        try:
            if format_type == 'xlsx':
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames
                if not sheet_name:
                    return Response({'error': 'Provide sheet_name', 'available_sheets': available_sheets}, status=400)
                if sheet_name not in available_sheets:
                    return Response({'error': f'Sheet "{sheet_name}" not found', 'available_sheets': available_sheets}, status=400)

                ws = wb[sheet_name]
                headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                data = [dict(zip(headers, row)) for row in ws.iter_rows(min_row=2, values_only=True)]

            elif format_type == 'csv':
                dataset.load(file.read().decode('utf-8'), format='csv')
                data = dataset.dict
            else:
                return Response({'error': 'Unsupported format'}, status=400)

            for row in data:
                name = str(row.get('name')).strip() if row.get('name') else None
                description = str(row.get('description')).strip() if row.get('description') else ''

                if not name:
                    continue

                existing = CLBLevel.objects.filter(name__iexact=name).first()
                if existing:
                    if existing.is_deleted:
                        CLBLevel.objects.create(name=name, description=description, is_deleted=False)
                    else:
                        duplicate_names.append(name)
                        continue
                else:
                    CLBLevel.objects.create(name=name, description=description, is_deleted=False)

        except Exception as e:
            return Response({'error': str(e)}, status=400)

        return Response({"statusCode": 200, "status": True, "duplicates": list(set(duplicate_names)), "message": f'Import successful'}, status=200)



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
                Q(name__icontains=search) |
                Q(description__icontains=search)
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
            objs.update(is_deleted=True)
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

        objs.update(is_deleted=True)
        return Response({"statusCode": 200, "status": True, "message": f"{count} benchmark(s) deleted", "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None})


class StudyLanguageBanchmarkExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'csv').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]
        field_list = [f.strip() for f in fields.split(',')] if fields else ['uuid', 'name', 'description', 'is_deleted', 'created_at', 'updated_at']
        queryset = StudyLanguageBanchmark.objects.filter(uuid__in=uuids) if uuids else StudyLanguageBanchmark.objects.all()

        dataset = Dataset()
        dataset.headers = field_list
        for obj in queryset:
            row = []
            for field in field_list:
                value = getattr(obj, field, '')
                if isinstance(value, datetime.datetime):
                    value = value.strftime("%Y-%m-%d %H:%M:%S")
                if isinstance(value, bool):
                    value = int(value)
                row.append(value if value is not None else '')
            dataset.append(row)

        if format_type == 'xlsx':
            data = XLSX().export_data(dataset)
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'study_language_banchmark.xlsx'
        else:
            data = CSV().export_data(dataset)
            content_type = 'text/csv; charset=utf-8'
            file_name = 'study_language_banchmark.csv'

        response = HttpResponse(data, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


class StudyLanguageBanchmarkImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')
        if not file:
            return Response({'error': 'No file uploaded'}, status=400)

        format_type = file.name.split('.')[-1].lower()
        dataset = Dataset()
        duplicate_names = []

        try:
            if format_type == 'xlsx':
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames
                if not sheet_name:
                    return Response({'error': 'Provide sheet_name', 'available_sheets': available_sheets}, status=400)
                if sheet_name not in available_sheets:
                    return Response({'error': f'Sheet "{sheet_name}" not found', 'available_sheets': available_sheets}, status=400)

                ws = wb[sheet_name]
                headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                data = [dict(zip(headers, row)) for row in ws.iter_rows(min_row=2, values_only=True)]

            elif format_type == 'csv':
                dataset.load(file.read().decode('utf-8'), format='csv')
                data = dataset.dict
            else:
                return Response({'error': 'Unsupported format'}, status=400)

            for row in data:
                name = str(row.get('name')).strip() if row.get('name') else None
                description = str(row.get('description')).strip() if row.get('description') else ''

                if not name:
                    continue

                existing = StudyLanguageBanchmark.objects.filter(name__iexact=name).first()
                if existing:
                    if existing.is_deleted:
                        StudyLanguageBanchmark.objects.create(name=name, description=description, is_deleted=False)
                    else:
                        duplicate_names.append(name)
                        continue
                else:
                    StudyLanguageBanchmark.objects.create(name=name, description=description, is_deleted=False)

        except Exception as e:
            return Response({'error': str(e)}, status=400)

        return Response({"statusCode": 200, "status": True, "duplicates": list(set(duplicate_names)), "message": f'Import successful'}, status=200)


class EntranceTestNameListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')
        allowed_sort_fields = ['fullname', 'shortname', 'description', 'created_at']

        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = EntranceTestName.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(
                Q(fullname__icontains=search) |
                Q(shortname__icontains=search) |
                Q(description__icontains=search)
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
            objs.update(is_deleted=True)
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

        objs.update(is_deleted=True)
        return Response({"statusCode": 200, "status": True, "message": f"{count} entrance test(s) deleted", "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None})


# -------------------- Export -------------------- #
class EntranceTestNameExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'csv').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]
        field_list = [f.strip() for f in fields.split(',')] if fields else ['uuid', 'fullname', 'shortname', 'description', 'is_deleted', 'created_at', 'updated_at']
        queryset = EntranceTestName.objects.filter(uuid__in=uuids) if uuids else EntranceTestName.objects.all()

        dataset = Dataset()
        dataset.headers = field_list
        for obj in queryset:
            row = []
            for field in field_list:
                value = getattr(obj, field, '')
                if isinstance(value, datetime.datetime):
                    value = value.strftime("%Y-%m-%d %H:%M:%S")
                if isinstance(value, bool):
                    value = int(value)
                row.append(value if value is not None else '')
            dataset.append(row)

        if format_type == 'xlsx':
            data = XLSX().export_data(dataset)
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'entrance_test_name.xlsx'
        else:
            data = CSV().export_data(dataset)
            content_type = 'text/csv; charset=utf-8'
            file_name = 'entrance_test_name.csv'

        response = HttpResponse(data, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response




# -------------------- Import -------------------- #
class EntranceTestNameImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')
        if not file:
            return Response({'error': 'No file uploaded'}, status=400)

        format_type = file.name.split('.')[-1].lower()
        dataset = Dataset()
        duplicate_names = []

        try:
            if format_type == 'xlsx':
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames
                if not sheet_name:
                    return Response({'error': 'Provide sheet_name', 'available_sheets': available_sheets}, status=400)
                if sheet_name not in available_sheets:
                    return Response({'error': f'Sheet "{sheet_name}" not found', 'available_sheets': available_sheets}, status=400)

                ws = wb[sheet_name]
                headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                data = [dict(zip(headers, row)) for row in ws.iter_rows(min_row=2, values_only=True)]

            elif format_type == 'csv':
                dataset.load(file.read().decode('utf-8'), format='csv')
                data = dataset.dict
            else:
                return Response({'error': 'Unsupported format'}, status=400)

            for row in data:
                fullname = str(row.get('fullname')).strip() if row.get('fullname') else None
                shortname = str(row.get('shortname')).strip() if row.get('shortname') else ''
                description = str(row.get('description')).strip() if row.get('description') else ''

                if not fullname:
                    continue

                existing = EntranceTestName.objects.filter(fullname__iexact=fullname, shortname__iexact=shortname).first()
                if existing:
                    if existing.is_deleted:
                        EntranceTestName.objects.create(fullname=fullname, shortname=shortname, description=description, is_deleted=False)
                    else:
                        duplicate_names.append(fullname)
                        continue
                else:
                    EntranceTestName.objects.create(fullname=fullname, shortname=shortname, description=description, is_deleted=False)

        except Exception as e:
            return Response({'error': str(e)}, status=400)

        return Response({"statusCode": 200, "status": True, "duplicates": list(set(duplicate_names)), "message": f'Import successful'}, status=200)



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
                Q(moduleName__icontains=search) |
                Q(description__icontains=search)
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
            objs.update(is_deleted=True)
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

        objs.update(is_deleted=True)
        return Response({"statusCode": 200, "status": True, "message": f"{count} module(s) deleted", "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None})



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
                Q(testresult__icontains=search) |
                Q(description__icontains=search) |
                Q(entrancetest__fullname__icontains=search) |
                Q(moduleName__moduleName__icontains=search)
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
        entrancetest_id = request.data.get("entrancetest_id")
        moduleName_id = request.data.get("moduleName_id")

        # Check duplicates for same entrance test + module
        existing = EntranceTestResult.objects.filter(
            entrancetest_id=entrancetest_id,
            moduleName_id=moduleName_id,
            is_deleted=False
        ).first()
        if existing:
            return Response({"statusCode": 400, "status": False, "message": "Result for this test and module already exists."}, status=400)

        serializer = EntranceTestResultSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"statusCode": 200, "status": True, "message": "Result created successfully", "data": serializer.data})
        errors = " ".join([msg for msgs in serializer.errors.values() for msg in msgs])
        return Response({"statusCode": 400, "status": False, "message": errors}, status=400)


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
            objs.update(is_deleted=True)
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

        objs.update(is_deleted=True)
        return Response({"statusCode": 200, "status": True, "message": f"{count} result(s) deleted", "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None})


# -------------------- Export -------------------- #
class EntranceTestResultExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'csv').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_list = [f.strip() for f in fields.split(',')] if fields else [
            'uuid', 'entrancetest', 'moduleName', 'testresult', 'description', 'is_deleted', 'created_at', 'updated_at'
        ]

        queryset = EntranceTestResult.objects.filter(uuid__in=uuids) if uuids else EntranceTestResult.objects.all()

        dataset = Dataset()
        dataset.headers = field_list

        for obj in queryset:
            row = []
            for field in field_list:
                value = getattr(obj, field, '')
                if isinstance(value, datetime.datetime):
                    value = value.strftime("%Y-%m-%d %H:%M:%S")
                if isinstance(value, bool):
                    value = int(value)
                # For foreign keys, show readable name
                if field in ['entrancetest', 'moduleName']:
                    value = getattr(obj, field).fullname if field == 'entrancetest' else getattr(obj, field).moduleName
                row.append(value if value is not None else '')
            dataset.append(row)

        if format_type == 'xlsx':
            data = XLSX().export_data(dataset)
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'entrance_test_results.xlsx'
        else:
            data = CSV().export_data(dataset)
            content_type = 'text/csv; charset=utf-8'
            file_name = 'entrance_test_results.csv'

        response = HttpResponse(data, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


# -------------------- Import -------------------- #
class EntranceTestResultImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=400)

        format_type = file.name.split('.')[-1].lower()
        dataset = Dataset()
        duplicate_entries = []

        try:
            # XLSX handling
            if format_type == 'xlsx':
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames
                if not sheet_name:
                    return Response({'error': 'Provide sheet_name', 'available_sheets': available_sheets}, status=400)
                if sheet_name not in available_sheets:
                    return Response({'error': f'Sheet "{sheet_name}" not found', 'available_sheets': available_sheets}, status=400)
                ws = wb[sheet_name]
                headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                data = [dict(zip(headers, row)) for row in ws.iter_rows(min_row=2, values_only=True)]
            elif format_type == 'csv':
                dataset.load(file.read().decode('utf-8'), format='csv')
                data = dataset.dict
            else:
                return Response({'error': 'Unsupported format'}, status=400)

            for row in data:
                entrancetest_name = row.get('entrancetest', '').strip()
                moduleName_name = row.get('moduleName', '').strip()
                testresult = row.get('testresult', '').strip()
                description = row.get('description', '').strip() if row.get('description') else ''

                if not entrancetest_name or not moduleName_name or not testresult:
                    continue

                # Check for duplicates
                existing = EntranceTestResult.objects.filter(
                    entrancetest__fullname__iexact=entrancetest_name,
                    moduleName__moduleName__iexact=moduleName_name,
                    is_deleted=False
                ).first()
                if existing:
                    duplicate_entries.append(f"{entrancetest_name} - {moduleName_name}")
                    continue

                # Create new entry
                EntranceTestResult.objects.create(
                    entrancetest=EntranceTestName.objects.get(fullname__iexact=entrancetest_name),
                    moduleName=EntranceTestModuleName.objects.get(moduleName__iexact=moduleName_name),
                    testresult=testresult,
                    description=description,
                    is_deleted=False
                )
        except Exception as e:
            return Response({'error': str(e)}, status=400)

        return Response({"statusCode": 200, "status": True, "duplicates": list(set(duplicate_entries)), "message": "Import successful"}, status=200)
    
    