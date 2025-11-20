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
                Q(name__istartswith=search)     
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
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')  # comma-separated fields
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_header_map = {
            'uuid': 'UUID',
            'name': 'Document Category',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'created_at': 'Created On',
            'updated_at': 'Modified On'
        }

        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())

        queryset = DocumentCategory.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'DocumentCategory'

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

        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'DocumentCategory.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'DocumentCategory.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


class DocumentCategoryImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicates = []
        skipped_rows = []

        required_headers = {"document category"}
        optional_headers = {"description"}

        try:
            data = []

            # ---------- XLSX ----------
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

                headers = [
                    str(cell.value).strip().lower() if cell.value else ""
                    for cell in next(ws.iter_rows(min_row=1, max_row=1))
                ]

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

            # ---------- CSV ----------
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
                                f"Found: {', '.join(row_lower.keys())}"
                            )
                        }, status=400)

                    data.append(row_lower)

            else:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "error": "Unsupported file format. Use .xlsx or .csv"
                }, status=400)

            # ---------- Import Logic with validation ----------
            imported_count = 0

            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")

                # Read values
                category_name = row.get("document category")
                description = row.get("description")

                # Convert to string safely
                category_name_str = str(category_name).strip() if category_name else ""
                description_str = str(description).strip() if description else ""

                # -------- VALIDATIONS --------

                # Category empty
                if not category_name_str:
                    skipped_rows.append({
                        "Row": row_number,
                        "Value": category_name,
                        "Reason": "Document Category cannot be empty"
                    })
                    continue

                # Category wrong datatype (number, date, boolean, etc.)
                if not isinstance(category_name, (str, type(None))):
                    skipped_rows.append({
                        "Row": row_number,
                        "Value": category_name,
                        "Reason": "Invalid data type for Document Category"
                    })
                    continue

                # Suspicious invalid category names
                if isinstance(category_name, str) and category_name.strip().isdigit():
                    skipped_rows.append({
                        "Row": row_number,
                        "Value": category_name,
                        "Reason": "Invalid Document Category name (numbers are not allowed)"
                    })
                    continue

                # Description wrong datatype
                if not isinstance(description, (str, type(None))):
                    skipped_rows.append({
                        "Row": row_number,
                        "Value": description,
                        "Reason": "Invalid Description data type"
                    })
                    continue

                # -------- Duplicate Check --------
                existing = DocumentCategory.objects.filter(name__iexact=category_name_str).first()

                if existing and not existing.is_deleted:
                    duplicates.append({
                        "Row": row_number,
                        "Document Category": category_name_str,
                        "Reason": "Already exists"
                    })
                    continue

                # Restore soft-deleted
                if existing and existing.is_deleted:
                    existing.description = description_str
                    existing.is_deleted = False
                    existing.save()
                    imported_count += 1
                    continue

                # Create new
                DocumentCategory.objects.create(
                    name=category_name_str,
                    description=description_str,
                    is_deleted=False
                )

                imported_count += 1

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
            "duplicates": duplicates,
            "skipped_rows": skipped_rows,
        }, status=200)


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


# class DocumentNameListAPIView(APIView):
#     def get(self, request):
#         search = request.GET.get('search', '').strip()
#         category_id = request.GET.get('category_id')
#         sort_by = request.GET.get('sortBy', 'created_at')
#         sort_order = request.GET.get('sortOrder', 'desc')

#         allowed_sort_fields = ['document_name', 'created_at']
#         if sort_by not in allowed_sort_fields:
#             sort_by = 'created_at'
#         if sort_order == 'desc':
#             sort_by = f'-{sort_by}'

#         queryset = DocumentName.objects.filter(is_deleted=False)
#         if category_id:
#             queryset = queryset.filter(document_category_id=category_id)
#         if search:
#             queryset = queryset.filter(
#                 Q(document_name__icontains=search) |
#                 Q(description__icontains=search) |
#                 Q(document_category__name__icontains=search)
#             )

#         queryset = queryset.order_by(sort_by)
#         paginator = CustomPagination()
#         result_page = paginator.paginate_queryset(queryset, request)
#         serializer = DocumentNameSerializer(result_page, many=True)
#         return paginator.get_paginated_response(serializer.data)


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
                Q(document_name__istartswith=search)
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

        # --- Field to header mapping ---
        field_header_map = {
            'uuid': 'UUID',
            'document_category': 'Document Category',
            'document_name': 'Document Name',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'created_at': 'Created On',
            'updated_at': 'Modified On'
        }

        # --- Required fields always included ---
        required_fields = ['document_category', 'document_name']

        if fields:
            field_list = [f.strip() for f in fields.split(',')]
            for rf in required_fields:
                if rf not in field_list:
                    field_list.insert(0, rf)
        else:
            field_list = list(field_header_map.keys())

        # --- Fetch queryset ---
        queryset = DocumentName.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        # --- Prepare dataset ---
        dataset = Dataset()

        # Correct readable headers
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'DocumentName'

        for obj in queryset:
            row = []
            for field in field_list:
                value = getattr(obj, field, '')

                # FIX 1: Show Category Name instead of ID
                if field == 'document_category':
                    value = getattr(obj.document_category, 'name', '')

                # Date formatting
                elif field in ['created_at', 'updated_at'] and value:
                    value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")

                # Boolean fix
                elif isinstance(value, bool):
                    value = int(value)

                row.append(value if value is not None else '')

            dataset.append(row)

        # --- Export ---
        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'DocumentName.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'DocumentName.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


class DocumentNameImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicates = []
        skipped_rows = []

        required_headers = {"document category", "document name"}
        optional_headers = {"description"}

        try:
            data = []

            # ---------- XLSX ----------
            if format_type == "xlsx":
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({"error": "Please provide sheet_name", "available_sheets": available_sheets}, status=400)

                if sheet_name not in available_sheets:
                    return Response({"error": f'Sheet "{sheet_name}" not found', "available_sheets": available_sheets}, status=400)

                ws = wb[sheet_name]

                if ws.max_row <= 1:
                    return Response({"statusCode": 400, "status": False, "message": f'Sheet "{sheet_name}" is empty.'}, status=400)

                headers = [str(c.value).strip().lower() if c.value else '' for c in next(ws.iter_rows(min_row=1, max_row=1))]

                # Validate headers
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

            # ---------- CSV ----------
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
                            "message": f"Missing required headers. Required: {required_headers}. Found: {set(row_lower.keys())}"
                        }, status=400)

                    data.append(row_lower)

            else:
                return Response({"statusCode": 400, "status": False, "error": "Unsupported file format. Use .xlsx or .csv"}, status=400)

            # ---------- Import Logic ----------
            imported_count = 0

            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")

                category_name = str(row.get("document category")).strip() if row.get("document category") else None
                doc_name = str(row.get("document name")).strip() if row.get("document name") else None
                description = str(row.get("description")).strip() if row.get("description") else ""

                # FIX: Validate missing fields
                if not category_name:
                    skipped_rows.append({"Row": row_number, "Reason": "Document Category is empty"})
                    continue

                if not doc_name:
                    skipped_rows.append({"Row": row_number, "Reason": "Document Name is empty"})
                    continue

                # FIX: Validate wrong category names
                category = DocumentCategory.objects.filter(name__iexact=category_name, is_deleted=False).first()
                if not category:
                    skipped_rows.append({"Row": row_number, "Reason": f'Invalid Input : Category'})
                    continue

                # FIX: Wrong datatype
                if not isinstance(description, str):
                    skipped_rows.append({"Row": row_number, "Reason": "Invalid description data"})
                    continue

                # Check existing
                existing = DocumentName.objects.filter(
                    document_category=category,
                    document_name__iexact=doc_name
                ).first()

                if existing and not existing.is_deleted:
                    duplicates.append({
                        "Row": row_number,
                        "Document Name": doc_name,
                        "Reason": "Already exists"
                    })
                    continue

                if existing and existing.is_deleted:
                    existing.description = description
                    existing.is_deleted = False
                    existing.save()
                else:
                    DocumentName.objects.create(
                        document_category=category,
                        document_name=doc_name,
                        description=description
                    )

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
                Q(name__istartswith=search)
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
            'updated_at': 'Modified On'  # fixed header
        }

        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())

        queryset = DocumentType.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'DocumentType'  # added dataset title

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
            file_name = 'DocumentType.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'DocumentType.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response

class DocumentTypeImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()

        duplicates = []
        skipped_rows = []
        imported_count = 0

        required_headers = {"document type"}
        optional_headers = {"description"}

        try:
            data = []

            # ---------------- XLSX ----------------
            if format_type == "xlsx":
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({
                        "error": "Please provide sheet_name",
                        "available_sheets": available_sheets
                    }, status=400)

                if sheet_name not in available_sheets:
                    return Response({
                        "error": f'Sheet "{sheet_name}" not found',
                        "available_sheets": available_sheets
                    }, status=400)

                ws = wb[sheet_name]

                if ws.max_row <= 1:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'Sheet "{sheet_name}" is empty.'
                    }, status=400)

                # Read headers
                headers = [
                    str(c.value).strip().lower() if c.value else ''
                    for c in next(ws.iter_rows(min_row=1, max_row=1))
                ]

                if not required_headers.issubset(set(headers)):
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f"Missing required headers. Required: {required_headers}, Found: {set(headers)}"
                    }, status=400)

                # Read rows
                for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    row_dict["_row_number"] = idx
                    data.append(row_dict)

            # ---------------- CSV ----------------
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
                            "message": f"Missing required headers. Required: {required_headers}. Found: {set(row_lower.keys())}"
                        }, status=400)

                    data.append(row_lower)

            else:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "error": "Unsupported file format. Use .xlsx or .csv"
                }, status=400)

            # ---------------- IMPORT LOGIC ----------------
            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")

                # Extract fields
                name_raw = row.get("document type")
                description_raw = row.get("description")

                name = str(name_raw).strip() if name_raw else None
                description = str(description_raw).strip() if description_raw else ""

                # ---------------- VALIDATION FIRST ----------------

                # 1. Empty value
                if not name:
                    skipped_rows.append({
                        "Row": row_number,
                        "Reason": "Document Type is empty"
                    })
                    continue

                # 2. Name must contain alphabets (NO pure numbers allowed)
                if name.isdigit():
                    skipped_rows.append({
                        "Row": row_number,
                        "Document Type": name,
                        "Reason": "Invalid value (numbers-only not allowed)"
                    })
                    continue

                # 3. Invalid description datatype
                if description_raw is not None and not isinstance(description_raw, (str, int, float, bool)):
                    skipped_rows.append({
                        "Row": row_number,
                        "Reason": "Invalid description data"
                    })
                    continue

                # ---------------- DUPLICATE CHECK ----------------
                existing = DocumentType.objects.filter(name__iexact=name).first()

                if existing and not existing.is_deleted:
                    duplicates.append({
                        "Row": row_number,
                        "Document Type": name,
                        "Reason": "Already exists"
                    })
                    continue

                # ---------------- RESTORE IF DELETED ----------------
                if existing and existing.is_deleted:
                    existing.description = description
                    existing.is_deleted = False
                    existing.save()
                    imported_count += 1
                    continue

                # ---------------- CREATE NEW ----------------
                try:
                    DocumentType.objects.create(
                        name=name,
                        description=description,
                        is_deleted=False
                    )
                    imported_count += 1

                except Exception as e:
                    skipped_rows.append({
                        "Row": row_number,
                        "Reason": str(e)
                    })
                    continue

        except Exception as e:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": str(e)
            }, status=400)

        # ---------------- FINAL RESPONSE ----------------
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet \"{sheet_name}\" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": duplicates,
            "skipped_rows": skipped_rows
        }, status=200)

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



# class PurposeOfVisitListAPIView(APIView):
#     def get(self, request):
#         search = request.GET.get('search', '').strip()
#         sort_by = request.GET.get('sortBy', 'created_at')
#         sort_order = request.GET.get('sortOrder', 'desc')

#         allowed_sort_fields = ['name', 'description', 'created_at']
#         if sort_by not in allowed_sort_fields:
#             sort_by = 'created_at'

#         if sort_order == 'desc':
#             sort_by = f'-{sort_by}'

#         queryset = PurposeOfVisit.objects.filter(is_deleted=False)
#         if search:
#             queryset = queryset.filter(Q(name__icontains=search) | Q(description__icontains=search))
#         queryset = queryset.order_by(sort_by)

#         paginator = CustomPagination()
#         result_page = paginator.paginate_queryset(queryset, request)
#         serializer = PurposeOfVisitSerializer(result_page, many=True)
#         return paginator.get_paginated_response(serializer.data)

class PurposeOfVisitListAPIView(APIView):

    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        # Allowed sorting fields
        allowed_sort_fields = ['name', 'description', 'created_at']

        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        # Base Query
        queryset = PurposeOfVisit.objects.filter(is_deleted=False)

        # STRICT search → ONLY name, using istartswith
        if search:
            queryset = queryset.filter(
                Q(name__istartswith=search)
            )

        queryset = queryset.order_by(sort_by)

        # Pagination
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
        ids = request.data.get('uuids', None)

        if not ids:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide 'id' (UUID list or 'all')."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Delete All
        if ids == "all":
            visits = PurposeOfVisit.objects.filter(is_deleted=False)
            count = visits.count()

            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No Purpose Of Visit records found to delete."
                }, status=status.HTTP_404_NOT_FOUND)

            visits.update(is_deleted=True)

            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} Purpose Of Visit records deleted successfully."
            }, status=status.HTTP_200_OK)

        # Check must be list
        if not isinstance(ids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Provide list of UUIDs in 'id' field or 'all'."
            }, status=status.HTTP_400_BAD_REQUEST)

        valid_uuids, invalid_uuids = [], []

        # Validate UUIDs
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

        visits = PurposeOfVisit.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = visits.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching Purpose Of Visit records found."
            }, status=status.HTTP_404_NOT_FOUND)

        # Hard delete — same as your reference
        visits.delete()

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} Purpose Of Visit record(s) deleted successfully.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        }, status=status.HTTP_200_OK)


class PurposeOfVisitExportAPIView(APIView):
    def get(self, request):
        format_type = request.GET.get("format", "xlsx").lower()
        fields = request.GET.get("fields")
        uuids_param = request.GET.get("uuids", "")
        uuids = [u.strip() for u in uuids_param.split(",") if u]

        # IMPORTANT FIX - Correct field mapping
        field_header_map = {
            "uuid": "UUID",
            "name": "Purpose of Visit",   # <-- MODEL FIELD IS `name` BUT HEADER = "Purpose of Visit"
            "description": "Description",
            "created_at": "Created On",
            "updated_at": "Modified On",
        }

        # Always use exact fields (never fall back to wrong ones)
        field_list = ["name", "description", "created_at", "updated_at"]

        queryset = PurposeOfVisit.objects.filter(is_deleted=False)

        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by("-created_at")

        dataset = Dataset()
        dataset.headers = [field_header_map[f] for f in field_list]
        dataset.title = "PurposeofVisit"
        

        for obj in queryset:
            row = []
            for field in field_list:
                value = getattr(obj, field, "")
                if field in ["created_at", "updated_at"] and value:
                    value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
                row.append(value if value else "")
            dataset.append(row)

        if format_type == "csv":
            file_data = dataset.export("csv")
            content_type = "text/csv"
            file_name = "PurposeofVisit.csv"
        else:
            file_data = io.BytesIO(dataset.export("xlsx"))
            content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            file_name = "PurposeofVisit.xlsx"

        response = HttpResponse(
            file_data if format_type == "csv" else file_data.getvalue(),
            content_type=content_type
        )
        response["Content-Disposition"] = f'attachment; filename=\"{file_name}\"'
        return response
    
    
class PurposeOfVisitImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get("file")
        sheet_name = request.data.get("sheet_name")

        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split(".")[-1].lower()

        duplicates = []
        skipped_rows = []
        imported_count = 0

        required_headers = {"purpose of visit"}
        optional_headers = {"description"}

        try:
            data = []

            # ---------------- XLSX ----------------
            if format_type == "xlsx":
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({
                        "error": "Please provide sheet_name",
                        "available_sheets": available_sheets
                    }, status=400)

                if sheet_name not in available_sheets:
                    return Response({
                        "error": f'Sheet "{sheet_name}" not found',
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
                    str(c.value).strip().lower() if c.value else ""
                    for c in next(ws.iter_rows(min_row=1, max_row=1))
                ]

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

            # ---------------- CSV ----------------
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
                            "message": f"Missing required headers. Required: {required_headers}. Found: {set(row_lower.keys())}"
                        }, status=400)

                    data.append(row_lower)
            else:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "error": "Unsupported file format. Use .xlsx or .csv"
                }, status=400)

            # ---------------- IMPORT LOGIC ----------------
            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")

                # Extract values
                name_raw = row.get("purpose of visit")
                name = str(name_raw).strip() if name_raw else None
                description_raw = row.get("description")
                description = str(description_raw).strip() if description_raw else ""

                # ---------------- VALIDATION ----------------

                # Missing name
                if not name:
                    skipped_rows.append({
                        "Row": row_number,
                        "Reason": "Purpose of Visit is empty"
                    })
                    continue

                # Invalid value (non-alphabetic start, numeric only, etc.)
                if isinstance(name_raw, (int, float)) or not any(c.isalpha() for c in name):
                    skipped_rows.append({
                        "Row": row_number,
                        "Reason": f'Invalid Input : Purpose of Visit'
                    })
                    continue

                # Invalid datatype for description
                if description_raw is not None and not isinstance(description_raw, (str, int, float, bool)):
                    skipped_rows.append({
                        "Row": row_number,
                        "Reason": "Invalid description data"
                    })
                    continue

                # ---------------- DUPLICATE / RESTORE LOGIC ----------------
                existing = PurposeOfVisit.objects.filter(name__iexact=name).first()

                if existing and not existing.is_deleted:
                    duplicates.append({
                        "Row": row_number,
                        "PurposeOfVisit": name,
                        "Reason": "Already exists"
                    })
                    continue

                if existing and existing.is_deleted:
                    existing.description = description
                    existing.is_deleted = False
                    existing.save()
                    imported_count += 1
                    continue

                # ---------------- CREATE NEW ----------------
                try:
                    PurposeOfVisit.objects.create(
                        name=name,
                        description=description,
                        is_deleted=False
                    )
                    imported_count += 1
                except Exception as e:
                    skipped_rows.append({
                        "Row": row_number,
                        "Reason": str(e)
                    })
                    continue

        except Exception as e:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": str(e)
            }, status=400)

        # ---------------- FINAL RESPONSE ----------------
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": duplicates,
            "skipped_rows": skipped_rows
        }, status=200)

#-----------------------DocumentsFor--------------------------------


class DocumentsForCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        serializer = DocumentsForSerializer(data=request.data)
        if serializer.is_valid():
            name = serializer.validated_data.get("name").strip()
            if DocumentsFor.objects.filter(name__iexact=name, is_deleted=False).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Documents For with this name already exists."
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Documents For created successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "statusCode": 400,
            "status": False,
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


# class DocumentsForListAPIView(APIView):
#     def get(self, request):
#         search = request.GET.get("search", "").strip()
#         sort_by = request.GET.get("sortBy", "created_at")
#         sort_order = request.GET.get("sortOrder", "desc")

#         allowed_sort_fields = ["name", "description", "created_at"]
#         if sort_by not in allowed_sort_fields:
#             sort_by = "created_at"

#         if sort_order == "desc":
#             sort_by = f"-{sort_by}"

#         queryset = DocumentsFor.objects.filter(is_deleted=False)

#         if search:
#             queryset = queryset.filter(Q(name__icontains=search) | Q(description__icontains=search))

#         queryset = queryset.order_by(sort_by)

#         paginator = CustomPagination()
#         result_page = paginator.paginate_queryset(queryset, request)
#         serializer = DocumentsForSerializer(result_page, many=True)
#         return paginator.get_paginated_response(serializer.data)

class DocumentsForListAPIView(APIView):
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        # Allowed sort fields – description removed because you said API
        # must filter only by document_for column (name).
        allowed_sort_fields = ['name', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        # Apply descending order for 'desc'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = DocumentsFor.objects.filter(is_deleted=False)

        # Search only on name (document_for column)
        if search:
            queryset = queryset.filter(
                Q(name__istartswith=search)
            )

        # Apply dynamic ordering
        queryset = queryset.order_by(sort_by)

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = DocumentsForSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)


class DocumentsForRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            record = DocumentsFor.objects.get(uuid=uuid, is_deleted=False)
        except DocumentsFor.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Documents For not found."
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = DocumentsForSerializer(record)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Documents For retrieved successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class DocumentsForUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            record = DocumentsFor.objects.get(uuid=uuid, is_deleted=False)
        except DocumentsFor.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Documents For not found."
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = DocumentsForSerializer(record, data=request.data, partial=True)
        if serializer.is_valid():
            new_name = serializer.validated_data.get("name", record.name)
            if DocumentsFor.objects.filter(name__iexact=new_name).exclude(uuid=uuid).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Documents For with this name already exists."
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Documents For updated successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "statusCode": 400,
            "status": False,
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class DocumentsForDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get('id', None)

        # -------- Single delete via URL param --------
        if uuid:
            try:
                record = DocumentsFor.objects.get(uuid=uuid)
                record.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "Documents For permanently deleted.",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            except DocumentsFor.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Documents For not found.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        # -------- Delete ALL --------
        if ids == "all":
            records = DocumentsFor.objects.all()
            count = records.count()

            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No Documents For records found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

            records.delete()

            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} Documents For record(s) permanently deleted.",
                "data": None
            }, status=status.HTTP_200_OK)

        # -------- Validate list of UUIDs --------
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

        # -------- Bulk delete --------
        records = DocumentsFor.objects.filter(uuid__in=valid_uuids)
        count = records.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching Documents For records found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_404_NOT_FOUND)

        records.delete()

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} Documents For record(s) permanently deleted.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        }, status=status.HTTP_200_OK)


class DocumentsForExportAPIView(APIView):
    def get(self, request):
        format_type = request.GET.get("format", "xlsx").lower()
        fields = request.GET.get("fields")
        uuids_param = request.GET.get("uuids", "")
        uuids = [u.strip() for u in uuids_param.split(",") if u]

        field_header_map = {
            "uuid": "UUID",
            "name": "Documents For",
            "description": "Description",
            "is_deleted": "Deleted",
            "created_at": "Created On",
            "updated_at": "Modified On"
        }

        field_list = [f.strip() for f in fields.split(",")] if fields else list(field_header_map.keys())

        queryset = DocumentsFor.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by("-created_at")

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'DocumentsFor'

        for obj in queryset:
            row = []
            for field in field_list:
                value = getattr(obj, field, "")
                if field in ["created_at", "updated_at"] and value:
                    value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
                elif isinstance(value, bool):
                    value = int(value)
                row.append(value if value is not None else "")
            dataset.append(row)

        if format_type == "csv":
            file_data = dataset.export("csv")
            content_type = "text/csv"
            file_name = "DocumentsFor.csv"
            response_content = file_data
        else:
            file_data = io.BytesIO(dataset.export("xlsx"))
            content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            file_name = "DocumentsFor.xlsx"
            response_content = file_data.getvalue()

        response = HttpResponse(response_content, content_type=content_type)
        response["Content-Disposition"] = f'attachment; filename="{file_name}"'
        return response


class DocumentsForImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get("file")
        sheet_name = request.data.get("sheet_name")

        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split(".")[-1].lower()
        duplicates = []
        skipped_rows = []

        required_headers = {"documents for"}
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
                name = str(row.get("documents for")).strip() if row.get("documents for") else None
                description = str(row.get("description")).strip() if row.get("description") else ""

                # Skip if no name
                if not name:
                    skipped_rows.append({
                        "Row": row_number,
                        "Reason": "Missing documents for name"
                    })
                    continue

                # Validate only alphabetic names (spaces and common punctuation allowed)
                if not isinstance(name, str) or not name.replace(" ", "").isalpha():
                    skipped_rows.append({
                        "Row": row_number,
                        "Reason": f'Invalid Input : Documents For'
                    })
                    continue

                existing = DocumentsFor.objects.filter(name__iexact=name).first()

                if existing:
                    if not existing.is_deleted:
                        duplicates.append({
                            "Row": row_number,
                            "Documents For": name,
                            "Reason": "Already exists in database"
                        })
                        continue
                    else:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    DocumentsFor.objects.create(
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
        ids = request.data.get('uuids', None)
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

        # Mapping of model fields to export headers
        field_header_map = {
            "country": "Country",
            "visa_main_category": "Visa Main Category",
            "visa_major_category": "Visa Major Category",
            "visa_name": "Visa Name",
            "document_category": "Document Category",
            "document_name": "Document Name",
            "description": "Description",
            "updated_at": "Modified On",
        }

        # Required order for export
        required_order = [
            "country",
            "visa_main_category",
            "visa_major_category",
            "visa_name",
            "document_category",
            "document_name",
        ]

        # If fields param provided, merge with required_order
        if fields:
            field_list = [f.strip() for f in fields.split(',')]
            for rf in reversed(required_order):
                if rf not in field_list:
                    field_list.insert(0, rf)
        else:
            field_list = required_order + ["description", "updated_at"]

        queryset = RequiredDocument.objects.filter(is_deleted=False).select_related(
            'country', 'visa_main_category', 'visa_major_category',
            'visa_name', 'document_category', 'document_name'
        )

        if uuids:
            queryset = queryset.filter(uuid__in=uuids)

        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map[f] for f in field_list]
        dataset.title = 'RequiredDocuments'

        for obj in queryset:
            row = []
            for field in field_list:
                # Use human-readable names for all FKs
                if field == 'country':
                    value = obj.country.name if obj.country else ""
                elif field == 'visa_main_category':
                    value = obj.visa_main_category.name if obj.visa_main_category else ""
                elif field == 'visa_major_category':
                    value = obj.visa_major_category.name if obj.visa_major_category else ""
                elif field == 'visa_name':
                    value = obj.visa_name.full_name if obj.visa_name else ""  # Corrected
                elif field == 'document_category':
                    value = obj.document_category.name if obj.document_category else ""
                elif field == 'document_name':
                    value = obj.document_name.document_name if obj.document_name else ""  # Corrected
                else:
                    value = getattr(obj, field, '')

                # Format datetime nicely
                if field == 'updated_at' and value:
                    value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")

                row.append(value)

            dataset.append(row)

        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'RequiredDocuments.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'RequiredDocuments.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


class RequiredDocumentImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get("file")
        sheet_name = request.data.get("sheet_name")

        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split(".")[-1].lower()
        duplicates = []
        skipped_rows = []

        # Required headers must match export
        required_headers = {
            "country",
            "visa main category",
            "visa major category",
            "visa name",
            "document category",
            "document name"
        }
        optional_headers = {"description"}

        try:
            data = []

            # ---------- XLSX Handling ----------
            if format_type == "xlsx":
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({"error": "Please provide sheet_name", "available_sheets": available_sheets}, status=400)
                if sheet_name not in available_sheets:
                    return Response({"error": f'Sheet "{sheet_name}" not found', "available_sheets": available_sheets}, status=400)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({"statusCode": 400, "status": False, "message": f'Sheet "{sheet_name}" is empty.'}, status=400)

                headers = [str(c.value).strip().lower() if c.value else '' for c in next(ws.iter_rows(min_row=1, max_row=1))]
                if not required_headers.issubset(set(headers)):
                    return Response({"statusCode": 400, "status": False, "message": f"Missing required headers. Required: {required_headers}, Found: {set(headers)}"}, status=400)

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
                        return Response({"statusCode": 400, "status": False, "message": f"Missing required headers. Required: {', '.join(required_headers)}. Found: {', '.join(row_lower.keys())}."}, status=400)
                    data.append(row_lower)
            else:
                return Response({"statusCode": 400, "status": False, "error": "Unsupported file format. Use .xlsx or .csv"}, status=400)

            # ---------- Import Logic ----------
            imported_count = 0

            # Helper to fetch object by correct field per model
            def get_fk_by_name(model_class, value):
                if not value:
                    return None
                value = str(value).strip()
                field_map = {
                    'Country': 'name',
                    'VisaMain': 'name',
                    'VisaMajor': 'name',
                    'VisaName': 'full_name',
                    'DocumentCategory': 'name',
                    'DocumentName': 'document_name'
                }
                field_name = field_map.get(model_class.__name__)
                if not field_name:
                    return None
                filter_kwargs = {f"{field_name}__iexact": value, "is_deleted": False}
                return model_class.objects.filter(**filter_kwargs).first()

            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")
                country_name = row.get("country")
                visa_main_name = row.get("visa main category")
                visa_major_name = row.get("visa major category")
                visa_name_name = row.get("visa name")
                doc_cat_name = row.get("document category")
                doc_name_name = row.get("document name")
                description = row.get("description") or ''

                # Lookup by name
                country_obj = get_fk_by_name(Country, country_name)
                visa_main_obj = get_fk_by_name(VisaMain, visa_main_name)
                visa_major_obj = get_fk_by_name(VisaMajor, visa_major_name)
                visa_name_obj = get_fk_by_name(VisaName, visa_name_name)
                doc_cat_obj = get_fk_by_name(DocumentCategory, doc_cat_name)
                doc_name_obj = get_fk_by_name(DocumentName, doc_name_name)

                missing_refs = []
                if not country_obj: missing_refs.append("Country")
                if not visa_main_obj: missing_refs.append("Visa Main Category")
                if not visa_major_obj: missing_refs.append("Visa Major Category")
                if not visa_name_obj: missing_refs.append("Visa Name")
                if not doc_cat_obj: missing_refs.append("Document Category")
                if not doc_name_obj: missing_refs.append("Document Name")

                if missing_refs:
                    skipped_rows.append({"Row": row_number, "Reason": f"Invalid input {', '.join(missing_refs)}"})
                    continue

                # Check existence
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
                        duplicates.append({"Row": row_number, "Reason": "Already exists in database"})
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
            return Response({"statusCode": 400, "status": False, "message": str(e)}, status=400)

        # ---------- Final response ----------
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": duplicates,
            "skipped_rows": skipped_rows,
        }, status=200)


#-------------- Process Status Name -----------


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

        queryset = ProcessStatusName.objects.filter(is_deleted=False).select_related(
            'country', 'visa_main_category'
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
            obj = ProcessStatusName.objects.get(uuid=uuid, is_deleted=False)
        except ProcessStatusName.DoesNotExist:
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
            obj = ProcessStatusName.objects.get(uuid=uuid, is_deleted=False)
        except ProcessStatusName.DoesNotExist:
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
        ids = request.data.get("uuids")

        if not ids:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Provide 'id' (UUID list or 'all')"
            }, status=status.HTTP_400_BAD_REQUEST)

        if ids == "all":
            count = ProcessStatusName.objects.filter(is_deleted=False).update(is_deleted=True)
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

        objs = ProcessStatusName.objects.filter(uuid__in=valid_uuids, is_deleted=False)
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
        india_tz = pytz.timezone("Asia/Kolkata")

        # --- Get query params ---
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')  # comma-separated fields
        uuids_param = request.GET.get('uuids', '')  # comma-separated UUIDs
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        # --- Field to header mapping ---
        field_header_map = {
            'uuid': 'UUID',
            'country': 'Country',
            'visa_main_category': 'Visa Main Category',
            'process_status_name': 'Process Status Name',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'updated_at': 'Modified On',
        }

        # --- Determine which fields to export ---
        if fields:
            field_list = [f.strip() for f in fields.split(',') if f.strip() in field_header_map]
        else:
            field_list = list(field_header_map.keys())

        if not field_list:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "No valid fields provided.",
                "allowed_fields": list(field_header_map.keys())
            }, status=400)

        # --- Fetch queryset ---
        queryset = ProcessStatusName.objects.filter(is_deleted=False).select_related("country", "visa_main_category")
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        # --- Prepare dataset ---
        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'ProcessStatus'

        for obj in queryset:
            row = []
            for field in field_list:
                if field == "country":
                    value = obj.country.name if obj.country else ""
                elif field == "visa_main_category":
                    value = obj.visa_main_category.name if obj.visa_main_category else ""
                else:
                    value = getattr(obj, field, "")

                    # Convert datetime fields to IST and naive
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
            file_name = 'ProcessStatus.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'ProcessStatus.xlsx'

        # --- Return response ---
        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


class ProcessStatusImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get("file")
        sheet_name = request.data.get("sheet_name")

        if not file:
            return Response({"error": "No file uploaded"}, status=400)

        format_type = file.name.split(".")[-1].lower()

        required_headers = {
            "country",
            "visa main category",
            "process status name"
        }

        optional_headers = {"description"}

        duplicates = []
        skipped_rows = []
        data = []

        try:
            # ---------------- XLSX ----------------
            if format_type == "xlsx":
                wb = openpyxl.load_workbook(file, read_only=True)
                sheets = wb.sheetnames

                if not sheet_name:
                    return Response({
                        "error": "Please provide sheet_name",
                        "available_sheets": sheets
                    }, status=400)

                if sheet_name not in sheets:
                    return Response({
                        "error": f'Sheet "{sheet_name}" not found in file',
                        "available_sheets": sheets
                    }, status=400)

                ws = wb[sheet_name]

                headers = [
                    (cell.value or "").strip().lower()
                    for cell in next(ws.iter_rows(min_row=1, max_row=1))
                ]

                if not required_headers.issubset(headers):
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f"Missing required headers: {required_headers}, Found: {set(headers)}"
                    }, status=400)

                for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row):
                        continue

                    row_dict = dict(zip(headers, row))
                    row_dict["_row_number"] = idx
                    data.append(row_dict)

            # ---------------- CSV ----------------
            elif format_type == "csv":
                decoded = file.read().decode("utf-8")
                dataset = Dataset()
                dataset.load(decoded, "csv")

                for idx, row in enumerate(dataset.dict, start=2):
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    row_lower["_row_number"] = idx

                    if not required_headers.issubset(row_lower.keys()):
                        return Response({
                            "statusCode": 400,
                            "status": False,
                            "message": f"Missing required headers: {required_headers}"
                        }, status=400)

                    data.append(row_lower)

            else:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "error": "Unsupported file format (.xlsx/.csv only)"
                }, status=400)

            # ---------------- Import Logic ----------------
            imported_count = 0

            for row in reversed(data):
                row_number = row.get("_row_number")

                country_name = str(row.get("country") or "").strip()
                visa_main_name = str(row.get("visa main category") or "").strip()
                ps_name = str(row.get("process status name") or "").strip()
                description = str(row.get("description") or "").strip()

                if not country_name or not visa_main_name or not ps_name:
                    skipped_rows.append({
                        "Row": row_number,
                        "Reason": "Missing required fields"
                    })
                    continue

                # Country
                country_obj = Country.objects.filter(
                    name__iexact=country_name,
                    is_deleted=False
                ).first()

                if not country_obj:
                    skipped_rows.append({
                        "Row": row_number,
                        "Reason": "Invalid Input : Country"
                    })
                    continue

                # Visa Main Category
                visa_obj = VisaMain.objects.filter(
                    name__iexact=visa_main_name,
                    is_deleted=False
                ).first()

                if not visa_obj:
                    skipped_rows.append({
                        "Row": row_number,
                        "Reason": "Invalid Input : Visa Main Category"
                    })
                    continue

                # Existing check
                existing = ProcessStatusName.objects.filter(
                    country=country_obj,
                    visa_main_category=visa_obj,
                    process_status_name__iexact=ps_name
                ).first()

                if existing:
                    if not existing.is_deleted:
                        duplicates.append({
                            "Row": row_number,
                            "Process Status": ps_name,
                            "Reason": "Already exists"
                        })
                        continue

                    existing.description = description
                    existing.is_deleted = False
                    existing.save()
                    imported_count += 1

                else:
                    ProcessStatusName.objects.create(
                        country=country_obj,
                        visa_main_category=visa_obj,
                        process_status_name=ps_name,
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

        queryset = ProcessSubStatusName.objects.filter(is_deleted=False).select_related(
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
            obj = ProcessSubStatusName.objects.get(uuid=uuid, is_deleted=False)
        except ProcessSubStatusName.DoesNotExist:
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
            obj = ProcessSubStatusName.objects.get(uuid=uuid, is_deleted=False)
        except ProcessSubStatusName.DoesNotExist:
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
        ids = request.data.get("uuids")

        if not ids:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Provide 'id' (UUID list or 'all')"
            }, status=400)

        if ids == "all":
            count = ProcessSubStatusName.objects.filter(is_deleted=False).update(is_deleted=True)
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

        objs = ProcessSubStatusName.objects.filter(uuid__in=valid_uuids, is_deleted=False)
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
        format_type = request.GET.get("format", "xlsx").lower()
        fields = request.GET.get("fields")
        uuids_param = request.GET.get("uuids", "")
        uuids = [u.strip() for u in uuids_param.split(",") if u]

        field_header_map = {
            "uuid": "UUID",
            "country": "Country",
            "visa_main_category": "Visa Main Category",
            "process_status_name": "Process Status Name",
            "process_sub_status_name": "Process Sub Status Name",
            "description": "Description",
            "created_at": "Created On",
            "updated_at": "Modified On",
        }

        field_list = [f.strip() for f in fields.split(",")] if fields else list(field_header_map.keys())

        queryset = ProcessSubStatusName.objects.filter(is_deleted=False).select_related(
            "country", "visa_main_category", "process_status_name"
        )
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by("-created_at")

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = "ProcessSubStatus"

        for obj in queryset:
            row = []
            for field in field_list:
                if field == "country":
                    value = getattr(obj.country, "name", "") if obj.country else ""
                elif field == "visa_main_category":
                    value = getattr(obj.visa_main_category, "name", "") if obj.visa_main_category else ""
                elif field == "process_status_name":
                    value = getattr(obj.process_status_name, "process_status_name", "") if obj.process_status_name else ""
                elif field == "process_sub_status_name":
                    value = getattr(obj, "process_sub_status_name", "")
                else:
                    value = getattr(obj, field, "")

                if field in ["created_at", "updated_at"] and value:
                    value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
                elif isinstance(value, bool):
                    value = int(value)

                row.append(value if value is not None else "")
            dataset.append(row)

        if format_type == "csv":
            file_data = dataset.export("csv")
            content_type = "text/csv"
            file_name = "ProcessSubStatus.csv"
        else:
            file_data = io.BytesIO(dataset.export("xlsx"))
            content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            file_name = "ProcessSubStatus.xlsx"

        response = HttpResponse(file_data if format_type == "csv" else file_data.getvalue(), content_type=content_type)
        response["Content-Disposition"] = f'attachment; filename="{file_name}"'
        return response


class ProcessSubStatusImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get("file")
        sheet_name = request.data.get("sheet_name")

        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split(".")[-1].lower()
        duplicates = []
        skipped_rows = []

        required_headers = {
            "country",
            "visa main category",
            "process status name",
            "process sub status name"
        }
        optional_headers = {"description"}

        try:
            data = []

            # ---------- XLSX Handling ----------
            if format_type == "xlsx":
                wb = openpyxl.load_workbook(file, read_only=True)
                if not sheet_name:
                    return Response({
                        "error": "Please provide sheet_name",
                        "available_sheets": wb.sheetnames
                    }, status=400)
                if sheet_name not in wb.sheetnames:
                    return Response({
                        "error": f'Sheet "{sheet_name}" not found',
                        "available_sheets": wb.sheetnames
                    }, status=400)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'Sheet "{sheet_name}" is empty.'
                    }, status=400)

                headers = [
                    str(c.value).strip().lower() if c.value else ""
                    for c in next(ws.iter_rows(min_row=1, max_row=1))
                ]

                if not required_headers.issubset(set(headers)):
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f"Missing required headers: {required_headers}"
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
                            "message": f"Missing required headers: {required_headers}"
                        }, status=400)
                    data.append(row_lower)

            else:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Unsupported file format"
                }, status=400)

            # ---------- Import Rows ----------
            imported_count = 0

            from master.models import Country, VisaMain, ProcessStatusName, ProcessSubStatusName

            def get_fk(model_class, value):
                if not value:
                    return None
                return model_class.objects.filter(name__iexact=str(value).strip(), is_deleted=False).first()

            for row in reversed(data):
                row_num = row.get("_row_number", "?")
                country_name = row.get("country")
                visa_main_name = row.get("visa main category")
                process_status_name = row.get("process status name")
                sub_status_name = row.get("process sub status name")
                description = str(row.get("description") or "").strip()

                # Check missing required fields
                if not all([country_name, visa_main_name, process_status_name, sub_status_name]):
                    skipped_rows.append({
                        "Row": row_num,
                        "Reason": "Missing required data"
                    })
                    continue

                # Get foreign keys
                country = get_fk(Country, country_name)
                visa_main = get_fk(VisaMain, visa_main_name)
                process_status = None
                if country and visa_main:
                    process_status = ProcessStatusName.objects.filter(
                        country=country,
                        visa_main_category=visa_main,
                        process_status_name__iexact=process_status_name,
                        is_deleted=False
                    ).first()

                # Invalid references
                if not country:
                    skipped_rows.append({
                        "Row": row_num,
                        "Reason": f'Invalid Input : Country'
                    })
                    continue
                if not visa_main:
                    skipped_rows.append({
                        "Row": row_num,
                        "Reason": f'Invalid Input : Visa Main Category'
                    })
                    continue
                if not process_status:
                    skipped_rows.append({
                        "Row": row_num,
                        "Reason": f'Invalid Input : Process Status'
                    })
                    continue

                # Check duplicates
                existing = ProcessSubStatusName.objects.filter(
                    country=country,
                    visa_main_category=visa_main,
                    process_status_name=process_status,
                    process_sub_status_name__iexact=sub_status_name
                ).first()

                if existing and not existing.is_deleted:
                    duplicates.append({
                        "Row": row_num,
                        "Process Sub Status Name": sub_status_name,
                        "Reason": "Already exists"
                    })
                    continue

                # Restore soft-deleted
                if existing and existing.is_deleted:
                    existing.is_deleted = False
                    existing.description = description
                    existing.save()
                    imported_count += 1
                    continue

                # Create new
                ProcessSubStatusName.objects.create(
                    country=country,
                    visa_main_category=visa_main,
                    process_status_name=process_status,
                    process_sub_status_name=sub_status_name,
                    description=description,
                    is_deleted=False
                )
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
        ids = request.data.get("uuids")
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
        format_type = request.GET.get("format", "xlsx").lower()
        fields = request.GET.get("fields")
        uuids_param = request.GET.get("uuids", "")
        uuids = [u.strip() for u in uuids_param.split(",") if u]

        field_header_map = {
            "uuid": "UUID",
            "name": "Process Type",
            "description": "Description",
            "created_at": "Created On",
            "updated_at": "Modified On",
        }

        field_list = [f.strip() for f in fields.split(",")] if fields else list(field_header_map.keys())

        queryset = ProcessType.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by("-created_at")

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = "ProcessType"

        for obj in queryset:
            row = []
            for field in field_list:
                value = getattr(obj, field, "")
                if field in ["created_at", "updated_at"] and value:
                    value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")
                elif isinstance(value, bool):
                    value = int(value)
                row.append(value if value is not None else "")
            dataset.append(row)

        if format_type == "csv":
            file_data = dataset.export("csv")
            content_type = "text/csv"
            file_name = "ProcessType.csv"
        else:
            file_data = io.BytesIO(dataset.export("xlsx"))
            content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            file_name = "ProcessType.xlsx"

        response = HttpResponse(file_data if format_type == "csv" else file_data.getvalue(), content_type=content_type)
        response["Content-Disposition"] = f'attachment; filename="{file_name}"'
        return response


class ProcessTypeImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get("file")
        sheet_name = request.data.get("sheet_name")
        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split(".")[-1].lower()
        duplicates = []
        skipped_rows = []

        required_headers = {"process type"}
        optional_headers = {"description"}

        data = []

        # ---------- XLSX Handling ----------
        if format_type == "xlsx":
            wb = openpyxl.load_workbook(file, read_only=True)
            if not sheet_name:
                return Response({"error": "Please provide sheet_name", "available_sheets": wb.sheetnames}, status=400)
            if sheet_name not in wb.sheetnames:
                return Response({"error": f'Sheet "{sheet_name}" not found', "available_sheets": wb.sheetnames}, status=400)

            ws = wb[sheet_name]
            if ws.max_row <= 1:
                return Response({"statusCode": 400, "status": False, "message": f'Sheet "{sheet_name}" is empty.'}, status=400)

            headers = [str(c.value).strip().lower() if c.value else "" for c in next(ws.iter_rows(min_row=1, max_row=1))]
            if not required_headers.issubset(set(headers)):
                return Response({"statusCode": 400, "status": False, "message": f"Missing required headers: {required_headers}"}, status=400)

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
                    return Response({"statusCode": 400, "status": False, "message": f"Missing required headers: {required_headers}"}, status=400)
                data.append(row_lower)
        else:
            return Response({"statusCode": 400, "status": False, "message": "Unsupported file format"}, status=400)

        # ---------- Import Rows ----------
        imported_count = 0

        for row in reversed(data):
            row_num = row.get("_row_number", "?")
            name = row.get("process type", "")
            description = str(row.get("description") or "").strip()

            # Validate data type: must be a non-empty string
            if not name or not isinstance(name, str) or not name.strip():
                skipped_rows.append({"Row": row_num, "Reason": f'Invalid Input : Process Type'})
                continue

            name = name.strip()
            existing = ProcessType.objects.filter(name__iexact=name).first()

            if existing and not existing.is_deleted:
                duplicates.append({"Row": row_num, "Process Type": name, "Reason": "Already exists"})
                continue

            if existing and existing.is_deleted:
                existing.is_deleted = False
                existing.description = description
                existing.save()
                imported_count += 1
                continue

            ProcessType.objects.create(name=name, description=description)
            imported_count += 1

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": duplicates,
            "skipped_rows": skipped_rows
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
        ids = request.data.get("uuids")
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
        fields = request.GET.get('fields')  # comma-separated fields
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        # --- Field to header mapping ---
        field_header_map = {
            'uuid': 'UUID',
            'name': 'Payment To',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'created_at': 'Created On',
            'updated_at': 'Modified On',
            
        }

        if fields:
            field_list = [f.strip() for f in fields.split(',')]
        else:
            field_list = list(field_header_map.keys())

        queryset = PaymentTo.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'PaymentTo'

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
            file_name = 'PaymentTo.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'PaymentTo.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response



class PaymentToImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get("file")
        sheet_name = request.data.get("sheet_name")

        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicates = []
        skipped_rows = []

        required_headers = {"payment to"}
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
                    data.append(row_lower)
            else:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Unsupported file format. Use .xlsx or .csv"
                }, status=400)

            # ---------- Import Rows ----------
            imported_count = 0

            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")
                raw_name = row.get("payment to")

                # Check for invalid datatype or empty value
                if raw_name is None or not isinstance(raw_name, str) or not raw_name.strip():
                    skipped_rows.append({
                        "Row": row_number,
                        "Reason": f'Invalid Input : Payment To'
                    })
                    continue

                name = raw_name.strip()
                description = str(row.get("description")).strip() if row.get("description") else ""

                # Check for duplicates only on valid string names
                existing = PaymentTo.objects.filter(name__iexact=name).first()
                if existing and not existing.is_deleted:
                    duplicates.append({
                        "Row": row_number,
                        "Payment To": name,
                        "Reason": "Already exists in database"
                    })
                    continue

                # Restore soft-deleted entries
                if existing and existing.is_deleted:
                    existing.description = description
                    existing.is_deleted = False
                    existing.save()
                    imported_count += 1
                    continue

                # Create new valid entry
                PaymentTo.objects.create(
                    name=name,
                    description=description,
                    is_deleted=False
                )
                imported_count += 1

        except Exception as e:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": str(e),
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
        ids = request.data.get("uuids")
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

        # --- Field to header mapping ---
        field_header_map = {
            'uuid': 'UUID',
            'payment_to': 'Payment To',
            'payment_category': 'Payment Category',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'created_at': 'Created On',
            'updated_at': 'Modified On',
        }

        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())

        queryset = PaymentCategory.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-updated_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'PaymentCategory'

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

        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv'
            file_name = 'PaymentCategory.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'PaymentCategory.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


class PaymentCategoryImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')
        if not file:
            return Response({"statusCode": 400, "status": False, "message": "No file uploaded"}, status=400)

        format_type = file.name.split('.')[-1].lower()
        required_headers = {'payment to', 'payment category'}
        optional_headers = {'description'}
        data = []
        duplicates = []
        skipped_rows = []

        try:
            # ---------- XLSX ----------
            if format_type == 'xlsx':
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({"statusCode": 400, "status": False, "message": "Please provide sheet_name", "available_sheets": available_sheets}, status=400)

                if sheet_name not in available_sheets:
                    return Response({"statusCode": 400, "status": False, "message": f'Sheet "{sheet_name}" not found', "available_sheets": available_sheets}, status=400)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({"statusCode": 400, "status": False, "message": f'The sheet "{sheet_name}" is empty'}, status=400)

                headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                if not required_headers.issubset(set(headers)):
                    return Response({"statusCode": 400, "status": False, "message": f"Missing required headers. Required: {required_headers}, Found: {set(headers)}"}, status=400)

                for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    row_dict['_row_number'] = idx
                    data.append(row_dict)

            # ---------- CSV ----------
            elif format_type == 'csv':
                decoded_file = file.read().decode('utf-8')
                dataset = Dataset()
                dataset.load(decoded_file, format='csv')

                for idx, row in enumerate(dataset.dict, start=2):
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    row_lower['_row_number'] = idx
                    if not required_headers.issubset(set(row_lower.keys())):
                        return Response({"statusCode": 400, "status": False, "message": f"Missing required headers. Required: {required_headers}, Found: {set(row_lower.keys())}"}, status=400)
                    data.append(row_lower)
            else:
                return Response({"statusCode": 400, "status": False, "message": "Unsupported file format. Use .xlsx or .csv"}, status=400)

            # ---------- Import Rows ----------
            imported_count = 0

            for row in reversed(data):
                row_num = row.get('_row_number', '?')
                reasons = []  # Collect all issues for this row

                payment_to_name = row.get('payment to')
                category_name = row.get('payment category')
                description = str(row.get('description', '')).strip() if row.get('description') else ''

                # Validate 'Payment To'
                if not payment_to_name or not isinstance(payment_to_name, str) or not payment_to_name.strip():
                    reasons.append(f'Invalid Input : Payment To')
                else:
                    payment_to_name = payment_to_name.strip()
                    payment_to = PaymentTo.objects.filter(name__iexact=payment_to_name, is_deleted=False).first()
                    if not payment_to:
                        reasons.append(f'Payment To "{payment_to_name}" not found')

                # Validate 'Payment Category'
                if not category_name or not isinstance(category_name, str) or not category_name.strip():
                    reasons.append(f'Invalid Input : Payment Category')
                else:
                    category_name = category_name.strip()

                # If there are any issues, skip this row
                if reasons:
                    skipped_rows.append({"Row": row_num, "Reason": "; ".join(reasons)})
                    continue

                # Check for duplicates
                existing = PaymentCategory.objects.filter(payment_to=payment_to, payment_category__iexact=category_name).first()
                if existing and not existing.is_deleted:
                    duplicates.append({'Row': row_num, 'Payment Category': category_name, 'Reason': 'Already exists in database'})
                    continue

                if existing and existing.is_deleted:
                    existing.description = description
                    existing.is_deleted = False
                    existing.save()
                    imported_count += 1
                    continue

                PaymentCategory.objects.create(payment_to=payment_to, payment_category=category_name, description=description, is_deleted=False)
                imported_count += 1

        except Exception as e:
            return Response({"statusCode": 400, "status": False, "message": f"Error importing data: {str(e)}"}, status=400)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": duplicates,
            "skipped_rows": skipped_rows,
        }, status=200)



