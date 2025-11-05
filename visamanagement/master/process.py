from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Q
from uuid import UUID
import datetime
import openpyxl
from tablib import Dataset
from django.http import HttpResponse
from .models import *
from .serializers import *
from .pagination import *
import io
import pytz
from django.utils import timezone
from tablib import Dataset
from rest_framework import status

from .serializers import DocumentNameSerializer




india_tz = pytz.timezone('Asia/Kolkata')

#----------------Document Category----------------


class DocumentCategoryCreateAPIView(APIView):
    def post(self, request):
        serializer = DocumentCategorySerializer(data=request.data)
        if serializer.is_valid():
            if DocumentCategory.objects.filter(name=serializer.validated_data['name'], is_deleted=False).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Document Category with this name already exists"
                }, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Document Category created successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "statusCode": 400,
            "status": False,
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class DocumentCategoryListAPIView(APIView):
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['name', 'description', 'created_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = DocumentCategory.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = DocumentCategorySerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class DocumentCategoryRetrieveAPIView(APIView):
    def get(self, request, uuid):
        try:
            category = DocumentCategory.objects.get(uuid=uuid, is_deleted=False)
        except DocumentCategory.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Document Category not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = DocumentCategorySerializer(category)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Document Category retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class DocumentCategoryUpdateAPIView(APIView):
    def put(self, request, uuid):
        try:
            category = DocumentCategory.objects.get(uuid=uuid, is_deleted=False)
        except DocumentCategory.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Document Category not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = DocumentCategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            new_name = serializer.validated_data.get("name", category.name)
            if DocumentCategory.objects.filter(name=new_name).exclude(uuid=uuid).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Document Category with this name already exists"
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Document Category updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "statusCode": 400,
            "status": False,
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class DocumentCategoryDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        ids = request.data.get('id', None)
        if not ids:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide 'id' (UUID list or 'all')."
            }, status=status.HTTP_400_BAD_REQUEST)

        if ids == "all":
            categories = DocumentCategory.objects.filter(is_deleted=False)
            count = categories.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No Document Categories found to delete."
                }, status=status.HTTP_404_NOT_FOUND)
            categories.update(is_deleted=True)
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} Document Categories deleted successfully."
            }, status=status.HTTP_200_OK)

        if not isinstance(ids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Provide list of UUIDs in 'id' field or 'all'."
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

        categories = DocumentCategory.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = categories.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching Document Categories found."
            }, status=status.HTTP_404_NOT_FOUND)

        categories.delete()
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} Document Category(ies) deleted successfully.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        }, status=status.HTTP_200_OK)


class DocumentCategoryExportAPIView(APIView):

    def get(self, request):
        # --- Get query params ---
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')  # comma-separated fields
        uuids_param = request.GET.get('uuids', '')  # comma-separated UUIDs

        uuids = [u.strip() for u in uuids_param.split(',') if u]

        # --- Field to header mapping ---
        field_header_map = {
            'uuid': 'UUID',
            'name': 'Document Category',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'created_at': 'Created On',
            'updated_at': 'Updated On'
        }

        # --- Determine which fields to export ---
        if fields:
            field_list = [f.strip() for f in fields.split(',')]
        else:
            field_list = list(field_header_map.keys())

        # --- Fetch queryset ---
        queryset = DocumentCategory.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        # --- Prepare dataset ---
        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]

        for category in queryset:
            row = []
            for field in field_list:
                value = getattr(category, field, '')
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
            file_name = 'document_categories.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'document_categories.xlsx'

        # --- Return response ---
        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


class DocumentCategoryImportAPIView(APIView):

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicate_names = []

        header_field_map = {
            'Document Category': 'name',
            'Description': 'description',
        }

        allowed_headers = set(k.lower() for k in header_field_map.keys())

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
                if not allowed_headers.issubset(set(headers)):
                    return Response({
                        "statusCode": 400,
                        "status": True,
                        'message': f'Missing required headers. Required: {allowed_headers}, Found: {set(headers)}'
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
                    if not allowed_headers.issubset(set(row_lower.keys())):
                        return Response({
                            "statusCode": 400,
                            "status": True,
                            "message": (
                                f'Missing required headers. Required: {", ".join(allowed_headers)}. '
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

            # --- Import Logic ---
            imported_count = 0
            for row in data:
                name = str(row.get('document category')).strip() if row.get('document category') else None
                description = str(row.get('description')).strip() if row.get('description') else ''

                if not name:
                    continue

                existing = DocumentCategory.objects.filter(name__iexact=name).first()

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
                    DocumentCategory.objects.create(
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
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful"
        }, status=status.HTTP_200_OK)

#----------------Document Name----------------


class DocumentNameCreateAPIView(APIView):
    def post(self, request):
        serializer = DocumentNameSerializer(data=request.data)
        if serializer.is_valid():
            doc_cat = serializer.validated_data["document_category"]
            doc_name = serializer.validated_data["document_name"]

            if DocumentName.objects.filter(document_category=doc_cat, document_name__iexact=doc_name, is_deleted=False).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Document Name already exists under this category."
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Document Name created successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            "statusCode": 400,
            "status": False,
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)



class DocumentNameListAPIView(APIView):
    def get(self, request):
        search = request.GET.get('search', '').strip()
        category_id = request.GET.get('category_id')
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['document_name', 'created_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = DocumentName.objects.filter(is_deleted=False)
        if category_id:
            queryset = queryset.filter(document_category_id=category_id)
        if search:
            queryset = queryset.filter(
                Q(document_name__icontains=search) |
                Q(description__icontains=search) |
                Q(document_category__name__icontains=search)
            )

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = DocumentNameSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)



class DocumentNameRetrieveAPIView(APIView):
    def get(self, request, uuid):
        try:
            obj = DocumentName.objects.get(uuid=uuid, is_deleted=False)
        except DocumentName.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Document Name not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = DocumentNameSerializer(obj)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Document Name retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)



class DocumentNameUpdateAPIView(APIView):
    def put(self, request, uuid):
        try:
            obj = DocumentName.objects.get(uuid=uuid, is_deleted=False)
        except DocumentName.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Document Name not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = DocumentNameSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            new_category = serializer.validated_data.get("document_category", obj.document_category)
            new_name = serializer.validated_data.get("document_name", obj.document_name)

            if DocumentName.objects.filter(document_category=new_category, document_name__iexact=new_name).exclude(uuid=uuid).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Document Name already exists under this category."
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Document Name updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            "statusCode": 400,
            "status": False,
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)



class DocumentNameDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        ids = request.data.get('id')
        if not ids:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide 'id' (UUID list or 'all')."
            }, status=status.HTTP_400_BAD_REQUEST)

        if ids == "all":
            objs = DocumentName.objects.filter(is_deleted=False)
            count = objs.count()
            objs.update(is_deleted=True)
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} Document Names deleted successfully."
            }, status=status.HTTP_200_OK)

        if not isinstance(ids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Provide list of UUIDs in 'id' field or 'all'."
            }, status=status.HTTP_400_BAD_REQUEST)

        valid_uuids = []
        for u in ids:
            try:
                valid_uuids.append(UUID(u))
            except ValueError:
                continue

        objs = DocumentName.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = objs.count()
        objs.update(is_deleted=True)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} Document Name(s) deleted successfully."
        }, status=status.HTTP_200_OK)



class DocumentNameExportAPIView(APIView):
    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'document_category': 'Document Category',
            'document_name': 'Document Name',
            'description': 'Description',
            'created_at': 'Created On',
            'updated_at': 'Updated On'
        }

        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())

        queryset = DocumentName.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]

        for obj in queryset:
            row = []
            for field in field_list:
                value = getattr(obj, field, '')
                if field == 'document_category':
                    value = obj.document_category.name
                elif field in ['created_at', 'updated_at'] and value:
                    value = timezone.localtime(value).strftime("%d-%m-%Y %I:%M:%S %p")
                row.append(value if value is not None else '')
            dataset.append(row)

        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'document_names.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'document_names.xlsx'

        response = Response(file_data.getvalue() if format_type == 'xlsx' else file_data, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response



class DocumentNameImportAPIView(APIView):
    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicate_names = []

        allowed_headers = {'document category', 'document name', 'description'}

        try:
            data = []
            if format_type == 'xlsx':
                wb = openpyxl.load_workbook(file, read_only=True)
                ws = wb[sheet_name] if sheet_name else wb.active
                headers = [str(c.value).strip().lower() if c.value else '' for c in next(ws.iter_rows(min_row=1, max_row=1))]
                if not allowed_headers.issubset(set(headers)):
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f"Missing required headers. Required: {allowed_headers}, Found: {set(headers)}"
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
                    if not allowed_headers.issubset(set(row_lower.keys())):
                        return Response({
                            "statusCode": 400,
                            "status": False,
                            "message": f"Missing required headers. Required: {allowed_headers}, Found: {set(row_lower.keys())}"
                        }, status=status.HTTP_400_BAD_REQUEST)
                    data.append(row_lower)
            else:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Unsupported file format. Use .xlsx or .csv"
                }, status=status.HTTP_400_BAD_REQUEST)

            imported_count = 0
            for row in data:
                category_name = str(row.get('document category')).strip()
                document_name = str(row.get('document name')).strip()
                description = str(row.get('description')).strip() if row.get('description') else ''

                if not category_name or not document_name:
                    continue

                category = DocumentCategory.objects.filter(name__iexact=category_name, is_deleted=False).first()
                if not category:
                    continue

                existing = DocumentName.objects.filter(document_category=category, document_name__iexact=document_name).first()

                if existing and not existing.is_deleted:
                    duplicate_names.append(document_name)
                    continue
                elif existing:
                    existing.description = description
                    existing.is_deleted = False
                    existing.save()
                    imported_count += 1
                else:
                    DocumentName.objects.create(
                        document_category=category,
                        document_name=document_name,
                        description=description
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
            "message": f"Import successful. Imported {imported_count} records."
        }, status=status.HTTP_200_OK)



#----------------Document Type----------------

class DocumentTypeCreateAPIView(APIView):
    def post(self, request):
        serializer = DocumentTypeSerializer(data=request.data)
        if serializer.is_valid():
            if DocumentType.objects.filter(name=serializer.validated_data['name'], is_deleted=False).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Document Type with this name already exists"
                }, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Document Type created successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "statusCode": 400,
            "status": False,
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class DocumentTypeListAPIView(APIView):
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['name', 'description', 'created_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = DocumentType.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = DocumentTypeSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class DocumentTypeRetrieveAPIView(APIView):
    def get(self, request, uuid):
        try:
            obj = DocumentType.objects.get(uuid=uuid, is_deleted=False)
        except DocumentType.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Document Type not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = DocumentTypeSerializer(obj)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Document Type retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class DocumentTypeUpdateAPIView(APIView):
    def put(self, request, uuid):
        try:
            obj = DocumentType.objects.get(uuid=uuid, is_deleted=False)
        except DocumentType.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Document Type not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = DocumentTypeSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            new_name = serializer.validated_data.get("name", obj.name)
            if DocumentType.objects.filter(name=new_name).exclude(uuid=uuid).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Document Type with this name already exists"
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Document Type updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "statusCode": 400,
            "status": False,
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class DocumentTypeDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        ids = request.data.get('id', None)
        if not ids:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide 'id' (UUID list or 'all')."
            }, status=status.HTTP_400_BAD_REQUEST)

        if ids == "all":
            objs = DocumentType.objects.filter(is_deleted=False)
            count = objs.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No Document Types found to delete."
                }, status=status.HTTP_404_NOT_FOUND)
            objs.update(is_deleted=True)
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} Document Types deleted successfully."
            }, status=status.HTTP_200_OK)

        if not isinstance(ids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Provide list of UUIDs in 'id' field or 'all'."
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

        objs = DocumentType.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = objs.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching Document Types found."
            }, status=status.HTTP_404_NOT_FOUND)

        objs.update(is_deleted=True)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} Document Type(s) deleted successfully.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        }, status=status.HTTP_200_OK)


class DocumentTypeExportAPIView(APIView):
    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'name': 'Document Type',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'created_at': 'Created On',
            'updated_at': 'Updated On'
        }

        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())
        queryset = DocumentType.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]

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

        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'document_types.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'document_types.xlsx'

        response = Response(file_data.getvalue() if format_type == 'xlsx' else file_data, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


class DocumentTypeImportAPIView(APIView):
    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicate_names = []

        header_field_map = {
            'Document Type': 'name',
            'Description': 'description',
        }

        allowed_headers = set(k.lower() for k in header_field_map.keys())

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
                        'error': f'Sheet \"{sheet_name}\" not found in uploaded file',
                        'available_sheets': available_sheets
                    }, status=status.HTTP_400_BAD_REQUEST)

                ws = wb[sheet_name]
                headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                if not allowed_headers.issubset(set(headers)):
                    return Response({
                        "statusCode": 400,
                        "status": True,
                        'message': f'Missing required headers. Required: {allowed_headers}, Found: {set(headers)}'
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
                    if not allowed_headers.issubset(set(row_lower.keys())):
                        return Response({
                            "statusCode": 400,
                            "status": True,
                            "message": (
                                f'Missing required headers. Required: {", ".join(allowed_headers)}. '
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
            for row in data:
                name = str(row.get('document type')).strip() if row.get('document type') else None
                description = str(row.get('description')).strip() if row.get('description') else ''

                if not name:
                    continue

                existing = DocumentType.objects.filter(name__iexact=name).first()

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
                    DocumentType.objects.create(
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
            "message": f'Sheet \"{sheet_name}\" imported successfully' if sheet_name else "Import successful"
        }, status=status.HTTP_200_OK)


#--------------------Purpose of visite----------------------------



class PurposeOfVisitCreateAPIView(APIView):
    def post(self, request):
        serializer = PurposeOfVisitSerializer(data=request.data)
        if serializer.is_valid():
            if PurposeOfVisit.objects.filter(name=serializer.validated_data['name'], is_deleted=False).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Purpose of Visit with this name already exists"
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Purpose of Visit created successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "statusCode": 400,
            "status": False,
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class PurposeOfVisitListAPIView(APIView):
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['name', 'description', 'created_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = PurposeOfVisit.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(description__icontains=search))
        queryset = queryset.order_by(sort_by)

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = PurposeOfVisitSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class PurposeOfVisitRetrieveAPIView(APIView):
    def get(self, request, uuid):
        try:
            item = PurposeOfVisit.objects.get(uuid=uuid, is_deleted=False)
        except PurposeOfVisit.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Purpose of Visit not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = PurposeOfVisitSerializer(item)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Purpose of Visit retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class PurposeOfVisitUpdateAPIView(APIView):
    def put(self, request, uuid):
        try:
            item = PurposeOfVisit.objects.get(uuid=uuid, is_deleted=False)
        except PurposeOfVisit.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Purpose of Visit not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = PurposeOfVisitSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            new_name = serializer.validated_data.get("name", item.name)
            if PurposeOfVisit.objects.filter(name=new_name).exclude(uuid=uuid).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Purpose of Visit with this name already exists"
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Purpose of Visit updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "statusCode": 400,
            "status": False,
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class PurposeOfVisitDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        ids = request.data.get('id', None)
        if not ids:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide 'id' (UUID list or 'all')."
            }, status=status.HTTP_400_BAD_REQUEST)

        if ids == "all":
            items = PurposeOfVisit.objects.filter(is_deleted=False)
            count = items.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No Purpose of Visit found to delete."
                }, status=status.HTTP_404_NOT_FOUND)
            items.update(is_deleted=True)
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} Purpose of Visit entries deleted successfully."
            }, status=status.HTTP_200_OK)

        if not isinstance(ids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Provide list of UUIDs in 'id' field or 'all'."
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

        items = PurposeOfVisit.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = items.count()
        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching Purpose of Visit found."
            }, status=status.HTTP_404_NOT_FOUND)

        items.update(is_deleted=True)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} Purpose of Visit record(s) deleted successfully.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        }, status=status.HTTP_200_OK)


class PurposeOfVisitExportAPIView(APIView):
    def get(self, request):
        format_type = request.GET.get("format", "xlsx").lower()
        fields = request.GET.get("fields")
        uuids_param = request.GET.get("uuids", "")

        uuids = [u.strip() for u in uuids_param.split(",") if u]

        field_header_map = {
            "uuid": "UUID",
            "name": "Purpose of Visit",
            "description": "Description",
            "is_deleted": "Deleted",
            "created_at": "Created On",
            "updated_at": "Updated At",
        }

        # Determine export fields
        if fields:
            field_list = [f.strip() for f in fields.split(",")]
        else:
            field_list = list(field_header_map.keys())

        queryset = PurposeOfVisit.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by("-created_at")

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]

        for purpose in queryset:
            row = []
            for field in field_list:
                value = getattr(purpose, field, "")
                if field in ["created_at", "updated_at"] and value:
                    value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
                elif isinstance(value, bool):
                    value = int(value)
                row.append(value if value is not None else "")
            dataset.append(row)

        # --- Export file ---
        if format_type == "csv":
            file_data = dataset.export("csv")
            content_type = "text/csv"
            file_name = "purpose_of_visit.csv"
            response_content = file_data
        else:
            file_data = io.BytesIO(dataset.export("xlsx"))
            content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            file_name = "purpose_of_visit.xlsx"
            response_content = file_data.getvalue()

        response = HttpResponse(response_content, content_type=content_type)
        response["Content-Disposition"] = f'attachment; filename="{file_name}"'
        return response


class PurposeOfVisitImportAPIView(APIView):
    def post(self, request):
        file = request.FILES.get("file")
        sheet_name = request.data.get("sheet_name")

        if not file:
            return Response(
                {"statusCode": 400, "status": False, "message": "No file uploaded"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        format_type = file.name.split(".")[-1].lower()
        duplicate_names = []

        header_field_map = {
            "Purpose of Visit": "name",
            "Description": "description",
        }

        allowed_headers = set(k.lower() for k in header_field_map.keys())
        data = []
        headers = []

        try:
            # ---------- XLSX ----------
            if format_type == "xlsx":
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response(
                        {
                            "statusCode": 400,
                            "status": False,
                            "message": "Please provide sheet_name",
                            "available_sheets": available_sheets,
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                if sheet_name not in available_sheets:
                    return Response(
                        {
                            "statusCode": 400,
                            "status": False,
                            "message": f'Sheet "{sheet_name}" not found in uploaded file',
                            "available_sheets": available_sheets,
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response(
                        {
                            "statusCode": 400,
                            "status": False,
                            "message": f'The uploaded XLSX file (sheet: "{sheet_name}") is empty. Please provide at least one data row.',
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                headers = [
                    str(cell.value).strip().lower() if cell.value else ""
                    for cell in next(ws.iter_rows(min_row=1, max_row=1))
                ]

                if not allowed_headers.issubset(set(headers)):
                    return Response(
                        {
                            "statusCode": 400,
                            "status": False,
                            "message": f"Missing required headers. Required: {allowed_headers}, Found: {set(headers)}",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                for row in ws.iter_rows(min_row=2, values_only=True):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    data.append(row_dict)

                if not data:
                    return Response(
                        {
                            "statusCode": 400,
                            "status": False,
                            "message": f'The uploaded XLSX file (sheet: "{sheet_name}") is empty.',
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            # ---------- CSV ----------
            elif format_type == "csv":
                decoded_file = file.read().decode("utf-8")
                dataset = Dataset()
                dataset.load(decoded_file, format="csv")

                for row in dataset.dict:
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    if not allowed_headers.issubset(set(row_lower.keys())):
                        return Response(
                            {
                                "statusCode": 400,
                                "status": False,
                                "message": (
                                    f"Missing required headers. Required: {', '.join(allowed_headers)}. "
                                    f"Found: {', '.join(row_lower.keys())}."
                                ),
                            },
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    data.append(row_lower)

                if not data:
                    return Response(
                        {
                            "statusCode": 400,
                            "status": False,
                            "message": "The uploaded CSV file is empty.",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            else:
                return Response(
                    {
                        "statusCode": 400,
                        "status": False,
                        "message": "Unsupported file format. Use .xlsx or .csv",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # ---------- Import Logic ----------
            imported_count = 0
            for row in data:
                name = str(row.get("purpose of visit")).strip() if row.get("purpose of visit") else None
                description = str(row.get("description")).strip() if row.get("description") else ""

                if not name:
                    continue

                existing = PurposeOfVisit.objects.filter(name__iexact=name).first()
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
                    PurposeOfVisit.objects.create(name=name, description=description, is_deleted=False)
                    imported_count += 1

        except Exception as e:
            return Response(
                {"statusCode": 400, "status": False, "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "statusCode": 200,
                "status": True,
                "duplicates": list(set(duplicate_names)),
                "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            },
            status=status.HTTP_200_OK,
        )

#--------------------Required Documents ----------------------------


class RequiredDocumentCreateAPIView(APIView):
    def post(self, request):
        serializer = RequiredDocumentSerializer(data=request.data)
        if serializer.is_valid():
            # optional: you could check for exact duplicates (same combination)
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Required Document created successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "statusCode": 400,
            "status": False,
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class RequiredDocumentListAPIView(APIView):
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')
        allowed_sort_fields = [
            'created_at',
            'country', 'visa_main_category', 'visa_major_category', 'visa_name',
            'document_category', 'document_name'
        ]
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = RequiredDocument.objects.filter(is_deleted=False).select_related(
            'country', 'visa_main_category', 'visa_major_category', 'visa_name',
            'document_category', 'document_name'
        )

        if search:
            queryset = queryset.filter(
                Q(description__icontains=search) |
                Q(country__name__icontains=search) |
                Q(visa_main_category__name__icontains=search) |
                Q(visa_major_category__name__icontains=search) |
                Q(visa_name__name__icontains=search) |
                Q(document_category__name__icontains=search) |
                Q(document_name__document_name__icontains=search)
            )

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = RequiredDocumentSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class RequiredDocumentRetrieveAPIView(APIView):
    def get(self, request, uuid):
        try:
            item = RequiredDocument.objects.get(uuid=uuid, is_deleted=False)
        except RequiredDocument.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Required Document not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = RequiredDocumentSerializer(item)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Required Document retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class RequiredDocumentUpdateAPIView(APIView):
    def put(self, request, uuid):
        try:
            item = RequiredDocument.objects.get(uuid=uuid, is_deleted=False)
        except RequiredDocument.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Required Document not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = RequiredDocumentSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Required Document updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "statusCode": 400,
            "status": False,
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class RequiredDocumentDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        ids = request.data.get('id', None)
        if not ids:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide 'id' (UUID list or 'all')."
            }, status=status.HTTP_400_BAD_REQUEST)

        if ids == "all":
            objs = RequiredDocument.objects.filter(is_deleted=False)
            count = objs.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No Required Documents found to delete."
                }, status=status.HTTP_404_NOT_FOUND)
            objs.update(is_deleted=True)
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} Required Documents deleted successfully."
            }, status=status.HTTP_200_OK)

        if not isinstance(ids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Provide list of UUIDs in 'id' field or 'all'."
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

        objs = RequiredDocument.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = objs.count()
        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching Required Documents found."
            }, status=status.HTTP_404_NOT_FOUND)

        objs.update(is_deleted=True)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} Required Document(s) deleted successfully.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        }, status=status.HTTP_200_OK)


class RequiredDocumentExportAPIView(APIView):
    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            "uuid": "UUID",
            "country": "Country",
            "visa_main_category": "Visa Main Category",
            "visa_major_category": "Visa Major Category",
            "visa_name": "Visa Name",
            "document_category": "Document Category",
            "document_name": "Document Name",
            "description": "Description",
            "is_deleted": "Deleted",
            "created_at": "Created On",
            "updated_at": "Updated At",
        }

        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())

        queryset = RequiredDocument.objects.filter(is_deleted=False).select_related(
            'country', 'visa_main_category', 'visa_major_category', 'visa_name', 'document_category', 'document_name'
        )
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]

        for obj in queryset:
            row = []
            for field in field_list:
                if field == 'country':
                    value = getattr(obj.country, 'name', str(obj.country)) if obj.country else ''
                elif field == 'visa_main_category':
                    value = getattr(obj.visa_main_category, 'name', str(obj.visa_main_category)) if obj.visa_main_category else ''
                elif field == 'visa_major_category':
                    value = getattr(obj.visa_major_category, 'name', str(obj.visa_major_category)) if obj.visa_major_category else ''
                elif field == 'visa_name':
                    value = getattr(obj.visa_name, 'name', str(obj.visa_name)) if obj.visa_name else ''
                elif field == 'document_category':
                    value = getattr(obj.document_category, 'name', str(obj.document_category)) if obj.document_category else ''
                elif field == 'document_name':
                    # DocumentName model uses field document_name for name
                    value = getattr(obj.document_name, 'document_name', str(obj.document_name)) if obj.document_name else ''
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
            file_name = 'required_documents.csv'
            response_content = file_data
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'required_documents.xlsx'
            response_content = file_data.getvalue()

        response = HttpResponse(response_content, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


class RequiredDocumentImportAPIView(APIView):
    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicate_rows = []
        missing_references = []

        header_field_map = {
            "Country": "country",
            "Visa Main Category": "visa_main_category",
            "Visa Major Category": "visa_major_category",
            "Visa Name": "visa_name",
            "Document Category": "document_category",
            "Document Name": "document_name",
            "Description": "description",
        }

        allowed_headers = set(k.lower() for k in header_field_map.keys())

        try:
            data = []
            headers = []

            # XLSX handling
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
                if not allowed_headers.issubset(set(headers)):
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        'message': f'Missing required headers. Required: {allowed_headers}, Found: {set(headers)}'
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

            # CSV handling
            elif format_type == 'csv':
                decoded_file = file.read().decode('utf-8')
                dataset = Dataset()
                dataset.load(decoded_file, format='csv')

                for row in dataset.dict:
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    if not allowed_headers.issubset(set(row_lower.keys())):
                        return Response({
                            "statusCode": 400,
                            "status": False,
                            "message": (
                                f'Missing required headers. Required: {", ".join(allowed_headers)}. '
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

            # --- import logic ---
            imported_count = 0

            # Helpers to find related records by name (case-insensitive)
            def get_fk_by_name(model_class, name_value, label):
                if not name_value:
                    return None
                name_value = str(name_value).strip()
                instance = model_class.objects.filter(name__iexact=name_value, is_deleted=False).first()
                return instance

            # Adjust imports for related models (change path if needed)
            from master.models import Country, VisaMainCategory, VisaMajorCategory, VisaName, DocumentCategory, DocumentName

            for row in data:
                country_name = row.get('country')
                visa_main_cat_name = row.get('visa main category')
                visa_major_cat_name = row.get('visa major category')
                visa_name_name = row.get('visa name')
                doc_cat_name = row.get('document category')
                doc_name_name = row.get('document name')
                description = row.get('description') or ''

                # Basic required check: all references must be present
                if not all([country_name, visa_main_cat_name, visa_major_cat_name, visa_name_name, doc_cat_name, doc_name_name]):
                    missing_references.append({
                        "row": row,
                        "reason": "Missing one or more reference fields"
                    })
                    continue

                country_obj = get_fk_by_name(Country, country_name, 'country')
                visa_main_obj = get_fk_by_name(VisaMainCategory, visa_main_cat_name, 'visa_main_category')
                visa_major_obj = get_fk_by_name(VisaMajorCategory, visa_major_cat_name, 'visa_major_category')
                visa_name_obj = get_fk_by_name(VisaName, visa_name_name, 'visa_name')
                doc_cat_obj = get_fk_by_name(DocumentCategory, doc_cat_name, 'document_category')
                doc_name_obj = get_fk_by_name(DocumentName, doc_name_name, 'document_name')

                if not all([country_obj, visa_main_obj, visa_major_obj, visa_name_obj, doc_cat_obj, doc_name_obj]):
                    missing_references.append({
                        "row": row,
                        "found": {
                            "country": bool(country_obj),
                            "visa_main_category": bool(visa_main_obj),
                            "visa_major_category": bool(visa_major_obj),
                            "visa_name": bool(visa_name_obj),
                            "document_category": bool(doc_cat_obj),
                            "document_name": bool(doc_name_obj),
                        }
                    })
                    continue

                # Check existing: same combination of foreign keys
                existing = RequiredDocument.objects.filter(
                    country=country_obj,
                    visa_main_category=visa_main_obj,
                    visa_major_category=visa_major_obj,
                    visa_name=visa_name_obj,
                    document_category=doc_cat_obj,
                    document_name=doc_name_obj
                ).first()

                if existing:
                    if not existing.is_deleted:
                        duplicate_rows.append(row)
                        continue
                    else:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                        continue

                # Create new record
                RequiredDocument.objects.create(
                    country=country_obj,
                    visa_main_category=visa_main_obj,
                    visa_major_category=visa_major_obj,
                    visa_name=visa_name_obj,
                    document_category=doc_cat_obj,
                    document_name=doc_name_obj,
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
            "imported_count": imported_count,
            "duplicates_count": len(duplicate_rows),
            "missing_references_count": len(missing_references),
            "duplicates": duplicate_rows,
            "missing_references": missing_references,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful"
        }, status=status.HTTP_200_OK)


#--------------  Process Status Name -----------


class ProcessStatusCreateAPIView(APIView):
    def post(self, request):
        serializer = ProcessStatusSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Process Status created successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            "statusCode": 400,
            "status": False,
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class ProcessStatusListAPIView(APIView):
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = ProcessStatus.objects.filter(is_deleted=False).select_related(
            'country', 'visa_main_category', 'process_status_name'
        )

        if search:
            queryset = queryset.filter(
                Q(country__name__icontains=search) |
                Q(visa_main_category__name__icontains=search) |
                Q(process_status_name__name__icontains=search) |
                Q(description__icontains=search)
            )

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = ProcessStatusSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class ProcessStatusRetrieveAPIView(APIView):
    def get(self, request, uuid):
        try:
            obj = ProcessStatus.objects.get(uuid=uuid, is_deleted=False)
        except ProcessStatus.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Process Status not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = ProcessStatusSerializer(obj)
        return Response({
            "statusCode": 200,
            "status": True,
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class ProcessStatusUpdateAPIView(APIView):
    def put(self, request, uuid):
        try:
            obj = ProcessStatus.objects.get(uuid=uuid, is_deleted=False)
        except ProcessStatus.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Process Status not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = ProcessStatusSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Process Status updated successfully",
                "data": serializer.data
            })
        return Response({
            "statusCode": 400,
            "status": False,
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class ProcessStatusDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        ids = request.data.get("id")

        if not ids:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Provide 'id' (UUID list or 'all')"
            }, status=status.HTTP_400_BAD_REQUEST)

        if ids == "all":
            count = ProcessStatus.objects.filter(is_deleted=False).update(is_deleted=True)
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All ({count}) Process Status records deleted."
            })

        if not isinstance(ids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Send list of UUIDs or 'all'."
            }, status=status.HTTP_400_BAD_REQUEST)

        valid_uuids, invalid_uuids = [], []
        for u in ids:
            try:
                valid_uuids.append(UUID(u))
            except ValueError:
                invalid_uuids.append(u)

        objs = ProcessStatus.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = objs.count()
        objs.update(is_deleted=True)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} Process Status deleted successfully",
            "invalid_uuids": invalid_uuids
        })


class ProcessStatusExportAPIView(APIView):
    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        queryset = ProcessStatus.objects.filter(is_deleted=False).select_related(
            'country', 'visa_main_category', 'process_status_name'
        )

        dataset = Dataset()
        dataset.headers = [
            "UUID",
            "Country",
            "Visa Main Category",
            "Process Status Name",
            "Description",
            "Created At",
            "Updated At"
        ]

        for obj in queryset:
            dataset.append([
                str(obj.uuid),
                obj.country.name if obj.country else '',
                obj.visa_main_category.name if obj.visa_main_category else '',
                obj.process_status_name.name if obj.process_status_name else '',
                obj.description or '',
                timezone.localtime(obj.created_at, india_tz).strftime("%d-%m-%Y %I:%M:%S %p"),
                timezone.localtime(obj.updated_at, india_tz).strftime("%d-%m-%Y %I:%M:%S %p"),
            ])

        if format_type == 'csv':
            response = HttpResponse(dataset.export('csv'), content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="process_status.csv"'
        else:
            stream = io.BytesIO(dataset.export('xlsx'))
            response = HttpResponse(
                stream.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename="process_status.xlsx"'
        return response


class ProcessStatusImportAPIView(APIView):
    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        required_headers = {'country', 'visa main category', 'process status name', 'description'}

        data = []
        if format_type == 'xlsx':
            wb = openpyxl.load_workbook(file)
            if not sheet_name:
                return Response({"error": "Please provide sheet_name"}, status=400)
            ws = wb[sheet_name]
            headers = [cell.value.lower().strip() for cell in next(ws.iter_rows(min_row=1, max_row=1))]
            if not required_headers.issubset(set(headers)):
                return Response({"error": f"Missing required headers {required_headers}"}, status=400)
            for row in ws.iter_rows(min_row=2, values_only=True):
                data.append(dict(zip(headers, row)))
        else:
            dataset = Dataset().load(file.read().decode('utf-8'), format='csv')
            for row in dataset.dict:
                data.append({k.lower(): v for k, v in row.items()})

        imported = 0
        duplicates = []
        for row in data:
            c_name = str(row.get('country', '')).strip()
            v_name = str(row.get('visa main category', '')).strip()
            p_name = str(row.get('process status name', '')).strip()
            desc = row.get('description', '')

            country = Country.objects.filter(name__iexact=c_name, is_deleted=False).first()
            visa_main = VisaMain.objects.filter(name__iexact=v_name, is_deleted=False).first()
            process_name = ProcessStatus.objects.filter(name__iexact=p_name, is_deleted=False).first()

            if not all([country, visa_main, process_name]):
                continue

            existing = ProcessStatus.objects.filter(
                country=country,
                visa_main_category=visa_main,
                process_status_name=process_name
            ).first()

            if existing and not existing.is_deleted:
                duplicates.append(row)
                continue

            if existing and existing.is_deleted:
                existing.is_deleted = False
                existing.description = desc
                existing.save()
                imported += 1
                continue

            ProcessStatus.objects.create(
                country=country,
                visa_main_category=visa_main,
                process_status_name=process_name,
                description=desc
            )
            imported += 1

        return Response({
            "statusCode": 200,
            "status": True,
            "imported": imported,
            "duplicates": len(duplicates),
            "message": "Import completed"
        })

#------------ Process Sub Status Name -------


class ProcessSubStatusCreateAPIView(APIView):
    def post(self, request):
        serializer = ProcessSubStatusSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Process Sub Status created successfully",
                "data": serializer.data
            })
        return Response({
            "statusCode": 400,
            "status": False,
            "message": serializer.errors
        }, status=400)


class ProcessSubStatusListAPIView(APIView):
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = ProcessSubStatus.objects.filter(is_deleted=False).select_related(
            'country', 'visa_main_category', 'process_status_name'
        )

        if search:
            queryset = queryset.filter(
                Q(country__name__icontains=search) |
                Q(visa_main_category__name__icontains=search) |
                Q(process_status_name__name__icontains=search) |
                Q(process_sub_status_name__icontains=search) |
                Q(description__icontains=search)
            )

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = ProcessSubStatusSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class ProcessSubStatusRetrieveAPIView(APIView):
    def get(self, request, uuid):
        try:
            obj = ProcessSubStatus.objects.get(uuid=uuid, is_deleted=False)
        except ProcessSubStatus.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Process Sub Status not found"
            }, status=404)
        serializer = ProcessSubStatusSerializer(obj)
        return Response({
            "statusCode": 200,
            "status": True,
            "data": serializer.data
        })


class ProcessSubStatusUpdateAPIView(APIView):
    def put(self, request, uuid):
        try:
            obj = ProcessSubStatus.objects.get(uuid=uuid, is_deleted=False)
        except ProcessSubStatus.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Process Sub Status not found"
            }, status=404)

        serializer = ProcessSubStatusSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Process Sub Status updated successfully",
                "data": serializer.data
            })
        return Response({
            "statusCode": 400,
            "status": False,
            "message": serializer.errors
        }, status=400)


class ProcessSubStatusDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        ids = request.data.get("id")

        if not ids:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Provide 'id' (UUID list or 'all')"
            }, status=400)

        if ids == "all":
            count = ProcessSubStatus.objects.filter(is_deleted=False).update(is_deleted=True)
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All ({count}) Process Sub Status records deleted."
            })

        if not isinstance(ids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Send list of UUIDs or 'all'."
            }, status=400)

        valid_uuids, invalid_uuids = [], []
        for u in ids:
            try:
                valid_uuids.append(UUID(u))
            except ValueError:
                invalid_uuids.append(u)

        objs = ProcessSubStatus.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = objs.count()
        objs.update(is_deleted=True)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} Process Sub Status deleted successfully",
            "invalid_uuids": invalid_uuids
        })


class ProcessSubStatusExportAPIView(APIView):
    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        queryset = ProcessSubStatus.objects.filter(is_deleted=False).select_related(
            'country', 'visa_main_category', 'process_status_name'
        )

        dataset = Dataset()
        dataset.headers = [
            "UUID",
            "Country",
            "Visa Main Category",
            "Process Status Name",
            "Process Sub Status Name",
            "Description",
            "Created At",
            "Updated At"
        ]

        for obj in queryset:
            dataset.append([
                str(obj.uuid),
                obj.country.name if obj.country else '',
                obj.visa_main_category.name if obj.visa_main_category else '',
                obj.process_status_name.name if obj.process_status_name else '',
                obj.process_sub_status_name,
                obj.description or '',
                timezone.localtime(obj.created_at, india_tz).strftime("%d-%m-%Y %I:%M:%S %p"),
                timezone.localtime(obj.updated_at, india_tz).strftime("%d-%m-%Y %I:%M:%S %p"),
            ])

        if format_type == 'csv':
            response = HttpResponse(dataset.export('csv'), content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="process_sub_status.csv"'
        else:
            stream = io.BytesIO(dataset.export('xlsx'))
            response = HttpResponse(
                stream.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename="process_sub_status.xlsx"'
        return response


class ProcessSubStatusImportAPIView(APIView):
    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({"error": "No file uploaded"}, status=400)

        format_type = file.name.split('.')[-1].lower()
        required_headers = {
            'country', 'visa main category', 'process status name', 'process sub status name', 'description'
        }

        data = []
        if format_type == 'xlsx':
            wb = openpyxl.load_workbook(file)
            if not sheet_name:
                return Response({"error": "Please provide sheet_name"}, status=400)
            ws = wb[sheet_name]
            headers = [cell.value.lower().strip() for cell in next(ws.iter_rows(min_row=1, max_row=1))]
            if not required_headers.issubset(set(headers)):
                return Response({"error": f"Missing required headers {required_headers}"}, status=400)
            for row in ws.iter_rows(min_row=2, values_only=True):
                data.append(dict(zip(headers, row)))
        else:
            dataset = Dataset().load(file.read().decode('utf-8'), format='csv')
            for row in dataset.dict:
                data.append({k.lower(): v for k, v in row.items()})

        imported = 0
        duplicates = []
        for row in data:
            c_name = str(row.get('country', '')).strip()
            v_name = str(row.get('visa main category', '')).strip()
            ps_name = str(row.get('process status name', '')).strip()
            pss_name = str(row.get('process sub status name', '')).strip()
            desc = row.get('description', '')

            country = Country.objects.filter(name__iexact=c_name, is_deleted=False).first()
            visa_main = VisaMain.objects.filter(name__iexact=v_name, is_deleted=False).first()
            process_status = ProcessStatus.objects.filter(name__iexact=ps_name, is_deleted=False).first()

            if not all([country, visa_main, process_status]):
                continue

            existing = ProcessSubStatus.objects.filter(
                country=country,
                visa_main_category=visa_main,
                process_status_name=process_status,
                process_sub_status_name__iexact=pss_name
            ).first()

            if existing and not existing.is_deleted:
                duplicates.append(row)
                continue

            if existing and existing.is_deleted:
                existing.is_deleted = False
                existing.description = desc
                existing.save()
                imported += 1
                continue

            ProcessSubStatus.objects.create(
                country=country,
                visa_main_category=visa_main,
                process_status_name=process_status,
                process_sub_status_name=pss_name,
                description=desc
            )
            imported += 1

        return Response({
            "statusCode": 200,
            "status": True,
            "imported": imported,
            "duplicates": len(duplicates),
            "message": "Import completed"
        })

#--------------  Process Type ------------------


class ProcessTypeCreateAPIView(APIView):
    def post(self, request):
        serializer = ProcessTypeSerializer(data=request.data)
        if serializer.is_valid():
            if ProcessType.objects.filter(name__iexact=serializer.validated_data['name'], is_deleted=False).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Process Type with this name already exists"
                }, status=400)
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Process Type created successfully",
                "data": serializer.data
            })
        return Response({
            "statusCode": 400,
            "status": False,
            "message": serializer.errors
        }, status=400)


class ProcessTypeListAPIView(APIView):
    def get(self, request):
        search = request.GET.get("search", "").strip()
        sort_by = request.GET.get("sortBy", "created_at")
        sort_order = request.GET.get("sortOrder", "desc")

        allowed_fields = ["name", "description", "created_at"]
        if sort_by not in allowed_fields:
            sort_by = "created_at"

        if sort_order == "desc":
            sort_by = f"-{sort_by}"

        queryset = ProcessType.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(description__icontains=search))
        queryset = queryset.order_by(sort_by)

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = ProcessTypeSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class ProcessTypeRetrieveAPIView(APIView):
    def get(self, request, uuid):
        try:
            obj = ProcessType.objects.get(uuid=uuid, is_deleted=False)
        except ProcessType.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Process Type not found"
            }, status=404)

        serializer = ProcessTypeSerializer(obj)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Process Type retrieved successfully",
            "data": serializer.data
        })
        

class ProcessTypeUpdateAPIView(APIView):
    def put(self, request, uuid):
        try:
            obj = ProcessType.objects.get(uuid=uuid, is_deleted=False)
        except ProcessType.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Process Type not found"
            }, status=404)

        serializer = ProcessTypeSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            new_name = serializer.validated_data.get("name", obj.name)
            if ProcessType.objects.filter(name__iexact=new_name).exclude(uuid=uuid).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Process Type with this name already exists"
                }, status=400)

            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Process Type updated successfully",
                "data": serializer.data
            })
        return Response({
            "statusCode": 400,
            "status": False,
            "message": serializer.errors
        }, status=400)


class ProcessTypeDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        ids = request.data.get("id")
        if not ids:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Provide 'id' (UUID list or 'all')"
            }, status=400)

        if ids == "all":
            count = ProcessType.objects.filter(is_deleted=False).update(is_deleted=True)
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All ({count}) Process Types deleted successfully."
            })

        if not isinstance(ids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Provide list of UUIDs or 'all'"
            }, status=400)

        valid_uuids, invalid_uuids = [], []
        for u in ids:
            try:
                valid_uuids.append(UUID(u))
            except ValueError:
                invalid_uuids.append(u)

        objs = ProcessType.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = objs.count()
        objs.update(is_deleted=True)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} Process Type(s) deleted successfully.",
            "invalid_uuids": invalid_uuids
        })
        

class ProcessTypeExportAPIView(APIView):
    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        queryset = ProcessType.objects.filter(is_deleted=False)

        dataset = Dataset()
        dataset.headers = [
            "UUID",
            "Process Type",
            "Description",
            "Created At",
            "Updated At"
        ]

        for obj in queryset:
            dataset.append([
                str(obj.uuid),
                obj.name,
                obj.description or '',
                timezone.localtime(obj.created_at, india_tz).strftime("%d-%m-%Y %I:%M:%S %p"),
                timezone.localtime(obj.updated_at, india_tz).strftime("%d-%m-%Y %I:%M:%S %p"),
            ])

        if format_type == 'csv':
            response = HttpResponse(dataset.export('csv'), content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="process_type.csv"'
        else:
            stream = io.BytesIO(dataset.export('xlsx'))
            response = HttpResponse(
                stream.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename="process_type.xlsx"'
        return response


class ProcessTypeImportAPIView(APIView):
    def post(self, request):
        file = request.FILES.get("file")
        sheet_name = request.data.get("sheet_name")

        if not file:
            return Response({"error": "No file uploaded"}, status=400)

        format_type = file.name.split('.')[-1].lower()
        required_headers = {'process type', 'description'}
        data = []

        if format_type == 'xlsx':
            wb = openpyxl.load_workbook(file)
            if not sheet_name:
                return Response({"error": "Please provide sheet_name"}, status=400)
            ws = wb[sheet_name]
            headers = [cell.value.lower().strip() for cell in next(ws.iter_rows(min_row=1, max_row=1))]
            if not required_headers.issubset(set(headers)):
                return Response({"error": f"Missing required headers {required_headers}"}, status=400)
            for row in ws.iter_rows(min_row=2, values_only=True):
                data.append(dict(zip(headers, row)))
        else:
            dataset = Dataset().load(file.read().decode('utf-8'), format='csv')
            for row in dataset.dict:
                data.append({k.lower(): v for k, v in row.items()})

        imported = 0
        duplicates = []
        for row in data:
            name = str(row.get('process type', '')).strip()
            description = row.get('description', '')

            if not name:
                continue

            existing = ProcessType.objects.filter(name__iexact=name).first()
            if existing and not existing.is_deleted:
                duplicates.append(row)
                continue

            if existing and existing.is_deleted:
                existing.is_deleted = False
                existing.description = description
                existing.save()
                imported += 1
                continue

            ProcessType.objects.create(name=name, description=description)
            imported += 1

        return Response({
            "statusCode": 200,
            "status": True,
            "imported": imported,
            "duplicates": len(duplicates),
            "message": "Import completed successfully"
        })

#--------------  Payment To --------------------


class PaymentToCreateAPIView(APIView):
    def post(self, request):
        serializer = PaymentToSerializer(data=request.data)
        if serializer.is_valid():
            if PaymentTo.objects.filter(name__iexact=serializer.validated_data['name'], is_deleted=False).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Payment To with this name already exists"
                }, status=400)
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Payment To created successfully",
                "data": serializer.data
            })
        return Response({
            "statusCode": 400,
            "status": False,
            "message": serializer.errors
        }, status=400)


class PaymentToListAPIView(APIView):
    def get(self, request):
        search = request.GET.get("search", "").strip()
        sort_by = request.GET.get("sortBy", "created_at")
        sort_order = request.GET.get("sortOrder", "desc")

        allowed_fields = ["name", "description", "created_at"]
        if sort_by not in allowed_fields:
            sort_by = "created_at"

        if sort_order == "desc":
            sort_by = f"-{sort_by}"

        queryset = PaymentTo.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(description__icontains=search))
        queryset = queryset.order_by(sort_by)

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = PaymentToSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class PaymentToRetrieveAPIView(APIView):
    def get(self, request, uuid):
        try:
            obj = PaymentTo.objects.get(uuid=uuid, is_deleted=False)
        except PaymentTo.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Payment To not found"
            }, status=404)

        serializer = PaymentToSerializer(obj)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Payment To retrieved successfully",
            "data": serializer.data
        })


class PaymentToUpdateAPIView(APIView):
    def put(self, request, uuid):
        try:
            obj = PaymentTo.objects.get(uuid=uuid, is_deleted=False)
        except PaymentTo.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Payment To not found"
            }, status=404)

        serializer = PaymentToSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            new_name = serializer.validated_data.get("name", obj.name)
            if PaymentTo.objects.filter(name__iexact=new_name).exclude(uuid=uuid).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Payment To with this name already exists"
                }, status=400)

            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Payment To updated successfully",
                "data": serializer.data
            })
        return Response({
            "statusCode": 400,
            "status": False,
            "message": serializer.errors
        }, status=400)


class PaymentToDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        ids = request.data.get("id")
        if not ids:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Provide 'id' (UUID list or 'all')"
            }, status=400)

        if ids == "all":
            count = PaymentTo.objects.filter(is_deleted=False).update(is_deleted=True)
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All ({count}) Payment To records deleted successfully."
            })

        if not isinstance(ids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Provide list of UUIDs or 'all'"
            }, status=400)

        valid_uuids, invalid_uuids = [], []
        for u in ids:
            try:
                valid_uuids.append(UUID(u))
            except ValueError:
                invalid_uuids.append(u)

        objs = PaymentTo.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = objs.count()
        objs.update(is_deleted=True)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} Payment To record(s) deleted successfully.",
            "invalid_uuids": invalid_uuids
        })


class PaymentToExportAPIView(APIView):
    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        queryset = PaymentTo.objects.filter(is_deleted=False)

        dataset = Dataset()
        dataset.headers = [
            "UUID",
            "Payment To",
            "Description",
            "Created At",
            "Updated At"
        ]

        for obj in queryset:
            dataset.append([
                str(obj.uuid),
                obj.name,
                obj.description or '',
                timezone.localtime(obj.created_at, india_tz).strftime("%d-%m-%Y %I:%M:%S %p"),
                timezone.localtime(obj.updated_at, india_tz).strftime("%d-%m-%Y %I:%M:%S %p"),
            ])

        if format_type == 'csv':
            response = HttpResponse(dataset.export('csv'), content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="payment_to.csv"'
        else:
            stream = io.BytesIO(dataset.export('xlsx'))
            response = HttpResponse(
                stream.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename="payment_to.xlsx"'
        return response


class PaymentToImportAPIView(APIView):
    def post(self, request):
        file = request.FILES.get("file")
        sheet_name = request.data.get("sheet_name")

        if not file:
            return Response({"error": "No file uploaded"}, status=400)

        format_type = file.name.split('.')[-1].lower()
        required_headers = {'payment to', 'description'}
        data = []

        if format_type == 'xlsx':
            wb = openpyxl.load_workbook(file)
            if not sheet_name:
                return Response({"error": "Please provide sheet_name"}, status=400)
            ws = wb[sheet_name]
            headers = [cell.value.lower().strip() for cell in next(ws.iter_rows(min_row=1, max_row=1))]
            if not required_headers.issubset(set(headers)):
                return Response({"error": f"Missing required headers {required_headers}"}, status=400)
            for row in ws.iter_rows(min_row=2, values_only=True):
                data.append(dict(zip(headers, row)))
        else:
            dataset = Dataset().load(file.read().decode('utf-8'), format='csv')
            for row in dataset.dict:
                data.append({k.lower(): v for k, v in row.items()})

        imported = 0
        duplicates = []
        for row in data:
            name = str(row.get('payment to', '')).strip()
            description = row.get('description', '')

            if not name:
                continue

            existing = PaymentTo.objects.filter(name__iexact=name).first()
            if existing and not existing.is_deleted:
                duplicates.append(row)
                continue

            if existing and existing.is_deleted:
                existing.is_deleted = False
                existing.description = description
                existing.save()
                imported += 1
                continue

            PaymentTo.objects.create(name=name, description=description)
            imported += 1

        return Response({
            "statusCode": 200,
            "status": True,
            "imported": imported,
            "duplicates": len(duplicates),
            "message": "Import completed successfully"
        })


#--------------  Payment Category --------------


class PaymentCategoryCreateAPIView(APIView):
    def post(self, request):
        serializer = PaymentCategorySerializer(data=request.data)
        if serializer.is_valid():
            payment_to = serializer.validated_data["payment_to"]
            name = serializer.validated_data["payment_category"]

            if PaymentCategory.objects.filter(payment_to=payment_to, payment_category__iexact=name, is_deleted=False).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Payment Category with this name already exists under this Payment To."
                }, status=400)

            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Payment Category created successfully",
                "data": serializer.data
            })
        return Response({
            "statusCode": 400,
            "status": False,
            "message": serializer.errors
        }, status=400)


class PaymentCategoryListAPIView(APIView):
    def get(self, request):
        search = request.GET.get("search", "").strip()
        sort_by = request.GET.get("sortBy", "created_at")
        sort_order = request.GET.get("sortOrder", "desc")

        allowed_sort_fields = ["payment_category", "description", "created_at"]
        if sort_by not in allowed_sort_fields:
            sort_by = "created_at"

        if sort_order == "desc":
            sort_by = f"-{sort_by}"

        queryset = PaymentCategory.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(
                Q(payment_category__icontains=search) |
                Q(description__icontains=search) |
                Q(payment_to__name__icontains=search)
            )
        queryset = queryset.order_by(sort_by)

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = PaymentCategorySerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class PaymentCategoryRetrieveAPIView(APIView):
    def get(self, request, uuid):
        try:
            obj = PaymentCategory.objects.get(uuid=uuid, is_deleted=False)
        except PaymentCategory.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Payment Category not found"
            }, status=404)

        serializer = PaymentCategorySerializer(obj)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Payment Category retrieved successfully",
            "data": serializer.data
        })


class PaymentCategoryUpdateAPIView(APIView):
    def put(self, request, uuid):
        try:
            obj = PaymentCategory.objects.get(uuid=uuid, is_deleted=False)
        except PaymentCategory.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Payment Category not found"
            }, status=404)

        serializer = PaymentCategorySerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            new_name = serializer.validated_data.get("payment_category", obj.payment_category)
            payment_to = serializer.validated_data.get("payment_to", obj.payment_to)

            if PaymentCategory.objects.filter(payment_to=payment_to, payment_category__iexact=new_name).exclude(uuid=uuid).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Payment Category with this name already exists under this Payment To."
                }, status=400)

            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Payment Category updated successfully",
                "data": serializer.data
            })
        return Response({
            "statusCode": 400,
            "status": False,
            "message": serializer.errors
        }, status=400)


class PaymentCategoryDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        ids = request.data.get("id")
        if not ids:
            return Response({"statusCode": 400, "status": False, "message": "Provide 'id' (UUID list or 'all')"}, status=400)

        if ids == "all":
            count = PaymentCategory.objects.filter(is_deleted=False).update(is_deleted=True)
            return Response({"statusCode": 200, "status": True, "message": f"All ({count}) Payment Categories deleted."})

        if not isinstance(ids, list):
            return Response({"statusCode": 400, "status": False, "message": "Provide list of UUIDs or 'all'."}, status=400)

        valid_uuids, invalid_uuids = [], []
        for u in ids:
            try:
                valid_uuids.append(UUID(u))
            except ValueError:
                invalid_uuids.append(u)

        objs = PaymentCategory.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = objs.count()
        objs.update(is_deleted=True)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} Payment Category(ies) deleted.",
            "invalid_uuids": invalid_uuids
        })



class PaymentCategoryExportAPIView(APIView):
    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')

        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'payment_to': 'Payment To',
            'payment_category': 'Payment Category',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'updated_at': 'Modified On',
        }

        # Determine fields to export
        if fields:
            field_list = [f.strip() for f in fields.split(',')]
        else:
            field_list = list(field_header_map.keys())

        queryset = PaymentCategory.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-updated_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]

        for obj in queryset:
            row = []
            for field in field_list:
                if field == 'payment_to':
                    value = obj.payment_to.name if obj.payment_to else ''
                else:
                    value = getattr(obj, field, '')

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
            file_name = 'payment_category.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'payment_category.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


class PaymentCategoryImportAPIView(APIView):
    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "No file uploaded"
            }, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        required_headers = {'payment to', 'payment category'}  # Required headers
        optional_headers = {'description'}
        data = []
        duplicate_records = []

        try:
            # ---------------- XLSX Handling ----------------
            if format_type == 'xlsx':
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": "Please provide sheet_name",
                        "available_sheets": available_sheets
                    }, status=status.HTTP_400_BAD_REQUEST)

                if sheet_name not in available_sheets:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'Sheet "{sheet_name}" not found in uploaded file',
                        "available_sheets": available_sheets
                    }, status=status.HTTP_400_BAD_REQUEST)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'The uploaded sheet "{sheet_name}" is empty. Please provide at least one data row.'
                    }, status=status.HTTP_400_BAD_REQUEST)

                headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                if not required_headers.issubset(set(headers)):
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f"Missing required headers. Required: {required_headers}, Found: {set(headers)}"
                    }, status=status.HTTP_400_BAD_REQUEST)

                for row in ws.iter_rows(min_row=2, values_only=True):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    data.append(row_dict)

            # ---------------- CSV Handling ----------------
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
                            "message": f"Missing required headers. Required: {required_headers}, Found: {set(row_lower.keys())}"
                        }, status=status.HTTP_400_BAD_REQUEST)
                    data.append(row_lower)
            else:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Unsupported file format. Use .xlsx or .csv"
                }, status=status.HTTP_400_BAD_REQUEST)

            if not data:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "The uploaded file is empty. Please provide at least one data row."
                }, status=status.HTTP_400_BAD_REQUEST)

            imported_count = 0
            for row in data:
                payment_to_name = str(row.get('payment to', '')).strip()
                category_name = str(row.get('payment category', '')).strip()
                description = str(row.get('description', '')).strip() if row.get('description') else ''

                if not payment_to_name or not category_name:
                    continue

                payment_to = PaymentTo.objects.filter(name__iexact=payment_to_name, is_deleted=False).first()
                if not payment_to:
                    continue

                existing = PaymentCategory.objects.filter(
                    payment_to=payment_to,
                    payment_category__iexact=category_name
                ).first()

                if existing:
                    if not existing.is_deleted:
                        duplicate_records.append(category_name)
                        continue
                    else:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                        continue

                PaymentCategory.objects.create(
                    payment_to=payment_to,
                    payment_category=category_name,
                    description=description,
                    is_deleted=False
                )
                imported_count += 1

        except Exception as e:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": f"Error while importing data: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "statusCode": 200,
            "status": True,
            "imported_count": imported_count,
            "duplicates": list(set(duplicate_records)),
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful"
        }, status=status.HTTP_200_OK)
