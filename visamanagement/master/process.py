from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Q,F
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
from django.db.models.functions import Lower

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
        custom_sort = request.GET.get('customSort')

        # Allowed fields to sort
        allowed_sort_fields = ['name', 'description', 'created_at']

        # Map to ORM fields
        sort_field_map = {
            'name': 'name',
            'description': 'description',
            'created_at': 'created_at'
        }

        sort_fields = []

        # ------------------------------------------
        #  CUSTOM SORT (Same Logic as City API)
        # ------------------------------------------
        if custom_sort:
            for rule in custom_sort.split(','):
                try:
                    field, order = rule.split(':')
                    field = field.strip()
                    order = order.strip().lower()

                    if field not in allowed_sort_fields:
                        continue

                    orm_field = sort_field_map[field]

                    # case-insensitive sorting for text fields
                    if field in ['name', 'description']:
                        f = Lower(orm_field)
                    else:
                        f = F(orm_field)

                    sort_fields.append(
                        f.asc(nulls_last=True) if order == 'asc' else f.desc(nulls_last=True)
                    )

                except ValueError:
                    continue

        # ------------------------------------------
        # DEFAULT SORT
        # ------------------------------------------
        else:
            sort_by = request.GET.get('sortBy', 'created_at')
            sort_order = request.GET.get('sortOrder', 'desc')

            if sort_by not in allowed_sort_fields:
                sort_by = 'created_at'

            orm_field = sort_field_map.get(sort_by, 'created_at')

            f = F(orm_field)
            sort_fields = [
                f.desc(nulls_last=True) if sort_order == 'desc' else f.asc(nulls_last=True)
            ]

        # ------------------------------------------
        # BASE QUERY
        # ------------------------------------------
        queryset = DocumentCategory.objects.filter(is_deleted=False)

        # ------------------------------------------
        # SEARCH
        # ------------------------------------------
        if search:
            queryset = queryset.filter(name__istartswith=search)

        # ------------------------------------------
        # APPLY SORT
        # ------------------------------------------
        queryset = queryset.order_by(*sort_fields)

        # ------------------------------------------
        # PAGINATION
        # ------------------------------------------
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
        try:
            search = request.GET.get("search", "").strip()
            delete_all = request.data.get("deleteAll", False)
            ids = request.data.get("id", None)

            # ----------------------------------
            # CASE 1: DELETE ENTIRE TABLE (id = "all")
            # ----------------------------------
            if ids == "all":
                count = DocumentCategory.objects.count()
                DocumentCategory.objects.all().delete()
                return Response({
                    "statusCode": 200,
                    "status": True,
                    "message": f"All {count} document category(s) deleted from the table.",
                })

           
            # ---------------------------------------------------
            # BASE QUERYSET
            # ---------------------------------------------------
            queryset = DocumentCategory.objects.all()
            applied_filters = []

            # ---------------------------------------------------
            # SEARCH FILTER
            # ---------------------------------------------------
            if search:
                queryset = queryset.filter(name__istartswith=search)
                applied_filters.append("search")

           

            # ---------------------------------------------------
            # CASE 2: DELETE ALL MATCHING FILTERED RESULTS
            # ---------------------------------------------------
            if delete_all:
                count = queryset.count()
                queryset.delete()

                if not applied_filters:
                    msg = f"All {count} document category(s) deleted."
                elif applied_filters == ["search"]:
                    msg = f"{count} document category(s) deleted based on search filter."
                elif applied_filters == ["categoryUuid"]:
                    msg = f"{count} document category(s) deleted based on categoryUuid filter."
                else:
                    msg = f"{count} document category(s) deleted based on search + categoryUuid filters."

                return Response({
                    "statusCode": 200,
                    "status": True,
                    "message": msg
                }, status=200)

            # ---------------------------------------------------
            # CASE 3: DELETE SPECIFIC UUID LIST
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

            filtered_objects.delete()  # HARD DELETE

            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"{count} document category(s) deleted.",
                "invalid_uuids": invalid_uuids if invalid_uuids else None
            }, status=200)

        except Exception as e:
            return Response({
                "statusCode": 500,
                "status": False,
                "message": f"Internal server error: {str(e)}"
            }, status=500)



class DocumentCategoryExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')

        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        search = request.GET.get('search', '').strip()
        custom_sort = request.GET.get('customSort')

        # -----------------------------------------
        # Allowed sorting fields (same rules as City)
        # -----------------------------------------
        allowed_sort_fields = ['name', 'description', 'created_at']

        # Mapping to ORM fields
        sort_field_map = {
            'name': 'name',
            'description': 'description',
            'created_at': 'created_at',
        }

        # -----------------------------------------
        # Field header names for export
        # -----------------------------------------
        field_header_map = {
            'uuid': 'UUID',
            'name': 'Document Category',
            'description': 'Description',
            'is_deleted': 'Deleted',
            'created_at': 'Created On',
            'updated_at': 'Modified On'
        }

        # If fields not provided → export all
        field_list = [f.strip() for f in fields.split(',')] if fields else list(field_header_map.keys())

        # -----------------------------------------
        # Base Query
        # -----------------------------------------
        queryset = DocumentCategory.objects.filter(is_deleted=False)

        # UUID filtering
        if uuids and "all" not in uuids:
            queryset = queryset.filter(uuid__in=uuids)

        # Search
        if search:
            queryset = queryset.filter(name__istartswith=search)

        # -----------------------------------------
        # Sorting
        # -----------------------------------------
        sort_fields = []

        if custom_sort:
            # Supports: ?customSort=name:asc,created_at:desc
            for rule in custom_sort.split(','):
                try:
                    field, order = rule.split(':')
                    field = field.strip()
                    order = order.strip().lower()

                    if field not in allowed_sort_fields:
                        continue

                    orm_field = sort_field_map[field]

                    # Case-insensitive sorting for string fields
                    if field in ['name', 'description']:
                        f = Lower(orm_field)
                    else:
                        f = F(orm_field)

                    sort_fields.append(
                        f.asc(nulls_last=True) if order == "asc" else f.desc(nulls_last=True)
                    )

                except ValueError:
                    continue
        else:
            # Default sorting
            sort_order = request.GET.get('sortOrder', 'desc')
            f = F('created_at')
            sort_fields = [f.desc(nulls_last=True) if sort_order == 'desc' else f.asc(nulls_last=True)]

        queryset = queryset.order_by(*sort_fields)

        # -----------------------------------------
        # Export Logic
        # -----------------------------------------
        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'DocumentCategory'

        india_tz = timezone.get_default_timezone()

        for category in queryset:
            row = []
            for field in field_list:
                value = getattr(category, field, '')

                # Format timestamps
                if field in ['created_at', 'updated_at'] and value:
                    value = timezone.localtime(value, india_tz).strftime("%d-%m-%Y %I:%M:%S %p")

                # Convert boolean to integer
                if isinstance(value, bool):
                    value = int(value)

                row.append(value if value is not None else '')

            dataset.append(row)

        # -----------------------------------------
        # Return file
        # -----------------------------------------
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
            "duplicates": reversed(duplicates),
            "skipped_rows": reversed(skipped_rows),
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


class DocumentNameListAPIView(APIView):
    def get(self, request):
        search = request.GET.get('search', '').strip()
        category_id = request.GET.get('category_id')
        custom_sort = request.GET.get('customSort')

        # ------------------------------------------
        #  Allowed sortable fields
        # ------------------------------------------
        allowed_sort_fields = ['document_name', 'created_at']

        # Map API fields → ORM fields
        sort_field_map = {
            'document_name': 'document_name',
            'created_at': 'created_at'
        }

        sort_fields = []

        # ------------------------------------------
        #  CUSTOM SORT (Same logic as Ideal API)
        # ------------------------------------------
        if custom_sort:
            for rule in custom_sort.split(','):
                try:
                    field, order = rule.split(':')
                    field = field.strip()
                    order = order.strip().lower()

                    if field not in allowed_sort_fields:
                        continue

                    orm_field = sort_field_map[field]

                    # Case-insensitive sorting for text fields
                    if field == 'document_name':
                        f = Lower(orm_field)
                    else:
                        f = F(orm_field)

                    sort_fields.append(
                        f.asc(nulls_last=True) if order == 'asc' else f.desc(nulls_last=True)
                    )

                except ValueError:
                    continue

        # ------------------------------------------
        #  DEFAULT SORT (If customSort missing)
        # ------------------------------------------
        else:
            sort_by = request.GET.get('sortBy', 'created_at')
            sort_order = request.GET.get('sortOrder', 'desc')

            if sort_by not in allowed_sort_fields:
                sort_by = 'created_at'

            orm_field = sort_field_map.get(sort_by, 'created_at')

            f = F(orm_field)
            sort_fields = [
                f.desc(nulls_last=True) if sort_order == 'desc' else f.asc(nulls_last=True)
            ]

        # ------------------------------------------
        # BASE QUERY
        # ------------------------------------------
        queryset = DocumentName.objects.filter(is_deleted=False)

        if category_id:
            queryset = queryset.filter(document_category_id=category_id)

        # ------------------------------------------
        # SEARCH
        # ------------------------------------------
        if search:
            queryset = queryset.filter(document_name__istartswith=search)

        # ------------------------------------------
        # APPLY SORT
        # ------------------------------------------
        queryset = queryset.order_by(*sort_fields)

        # ------------------------------------------
        # PAGINATION
        # ------------------------------------------
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
        try:
            ids = request.data.get('id')
            search = request.GET.get("search", "").strip()
            delete_all = request.data.get("deleteAll", False)

            # -----------------------------------------
            # Parse comma-separated UUID filter
            # -----------------------------------------
            def parse_uuid_list(param):
                raw = request.GET.get(param, "")
                result = []
                if raw:
                    for x in raw.split(","):
                        try:
                            result.append(UUID(x.strip()))
                        except:
                            pass
                return result

            name_uuids = parse_uuid_list("documentNameUuid")
            category_uuids = parse_uuid_list("documentCategory")   # <--- NEW

            # -----------------------------------------
            # BASE QUERYSET
            # -----------------------------------------
            queryset = DocumentName.objects.filter(is_deleted=False)
            applied_filters = []

            # -----------------------------------------
            # SEARCH FILTER
            # -----------------------------------------
            if search:
                queryset = queryset.filter(document_name__istartswith=search)
                applied_filters.append("search")

            # -----------------------------------------
            # UUID FILTER (documentNameUuid)
            # -----------------------------------------
            if name_uuids:
                queryset = queryset.filter(uuid__in=name_uuids)
                applied_filters.append("documentNameUuid")

            # -----------------------------------------
            # Document Category UUID FILTER  (NEW)
            # -----------------------------------------
            if category_uuids:
                queryset = queryset.filter(document_category__uuid__in=category_uuids)
                applied_filters.append("documentCategory")

            # ===========================================================
            # CASE 1 → id == "all": delete filtered results only
            # ===========================================================
            if ids == "all":
                count = queryset.count()
                if count == 0:
                    return Response({
                        "statusCode": 404,
                        "status": False,
                        "message": "No Document Names found matching filters."
                    }, status=404)

                queryset.update(is_deleted=True)

                msg = (
                    f"{count} Document Names deleted based on filters: {', '.join(applied_filters)}."
                    if applied_filters else
                    f"All {count} Document Names deleted successfully."
                )

                return Response({
                    "statusCode": 200,
                    "status": True,
                    "message": msg
                }, status=200)

            # ===========================================================
            # CASE 2 → deleteAll: delete ONLY filtered results
            # ===========================================================
            if delete_all:
                count = queryset.count()
                if count == 0:
                    return Response({
                        "statusCode": 404,
                        "status": False,
                        "message": "No Document Names found matching filters."
                    }, status=404)

                queryset.update(is_deleted=True)

                if not applied_filters:
                    msg = f"All {count} Document Names deleted."
                elif applied_filters == ["search"]:
                    msg = f"{count} Document Names deleted based on search filter."
                elif applied_filters == ["documentNameUuid"]:
                    msg = f"{count} Document Names deleted based on UUID filter."
                elif applied_filters == ["documentCategory"]:
                    msg = f"{count} Document Names deleted based on Document Category filter."
                else:
                    msg = f"{count} Document Names deleted based on multiple filters."

                return Response({
                    "statusCode": 200,
                    "status": True,
                    "message": msg
                }, status=200)

            # ===========================================================
            # CASE 3 → DELETE SPECIFIC UUID LIST (WITH SEARCH FILTER)
            # ===========================================================
            if not ids or not isinstance(ids, list):
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Provide list of UUIDs in 'id' field or 'all'."
                }, status=400)

            valid_uuids, invalid_uuids = [], []
            for u in ids:
                try:
                    valid_uuids.append(UUID(u))
                except ValueError:
                    invalid_uuids.append(u)

            # Apply both search + filters
            objs = queryset.filter(uuid__in=valid_uuids)
            count = objs.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No matching Document Names found to delete.",
                    "invalid_uuids": invalid_uuids if invalid_uuids else None
                }, status=404)

            objs.update(is_deleted=True)

            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"{count} Document Name(s) deleted successfully.",
                "invalid_uuids": invalid_uuids if invalid_uuids else None
            }, status=200)

        except Exception as e:
            return Response({
                "statusCode": 500,
                "status": False,
                "message": f"Internal server error: {str(e)}"
            }, status=500)


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
            "duplicates": reversed(duplicates),
            "skipped_rows": reversed(skipped_rows)
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
        custom_sort = request.GET.get('customSort')

        # ---------------------------------------------------
        # Allowed sortable fields
        # ---------------------------------------------------
        allowed_sort_fields = ['name', 'description', 'created_at']

        # Map API fields → ORM fields
        sort_field_map = {
            'name': 'name',
            'description': 'description',
            'created_at': 'created_at'
        }

        sort_fields = []

        # ---------------------------------------------------
        # CUSTOM SORT (Excel-style multi sorting)
        # ---------------------------------------------------
        if custom_sort:
            for rule in custom_sort.split(','):
                try:
                    field, order = rule.split(':')
                    field = field.strip()
                    order = order.strip().lower()

                    if field not in allowed_sort_fields:
                        continue

                    orm_field = sort_field_map[field]

                    # Case-insensitive sorting for text fields
                    if field in ['name', 'description']:
                        f = Lower(orm_field)
                    else:
                        f = F(orm_field)

                    sort_fields.append(
                        f.asc(nulls_last=True) if order == 'asc' else f.desc(nulls_last=True)
                    )

                except ValueError:
                    continue

        # ---------------------------------------------------
        # DEFAULT SORT (if customSort is not sent)
        # ---------------------------------------------------
        else:
            sort_by = request.GET.get('sortBy', 'created_at')
            sort_order = request.GET.get('sortOrder', 'desc')

            if sort_by not in allowed_sort_fields:
                sort_by = 'created_at'

            orm_field = sort_field_map.get(sort_by, 'created_at')
            f = F(orm_field)

            sort_fields = [
                f.desc(nulls_last=True) if sort_order == 'desc' else f.asc(nulls_last=True)
            ]

        # ---------------------------------------------------
        # BASE QUERY
        # ---------------------------------------------------
        queryset = DocumentType.objects.filter(is_deleted=False)

        # ---------------------------------------------------
        # SEARCH
        # ---------------------------------------------------
        if search:
            queryset = queryset.filter(name__istartswith=search)

        # ---------------------------------------------------
        # APPLY SORT
        # ---------------------------------------------------
        queryset = queryset.order_by(*sort_fields)

        # ---------------------------------------------------
        # PAGINATION
        # ---------------------------------------------------
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
        search = request.GET.get("search", "").strip()

        if not ids:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide 'id' (UUID list or 'all')."
            }, status=status.HTTP_400_BAD_REQUEST)

        # -----------------------------
        # IF "all" → delete all matched by search
        # -----------------------------
        if ids == "all":
            objs = DocumentType.objects.filter(is_deleted=False)

            # Apply search
            if search:
                objs = objs.filter(name__icontains=search)

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
                "message": f"{count} Document Types deleted successfully."
            }, status=status.HTTP_200_OK)

        # -----------------------------
        # NORMAL DELETE → only delete selected UUIDs
        # -----------------------------
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

        # Apply selected UUIDs + search (search should NOT delete extra items)
        objs = DocumentType.objects.filter(uuid__in=valid_uuids, is_deleted=False)

        # Apply search filter (optional)
        if search:
            objs = objs.filter(name__icontains=search)

        count = objs.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching Document Types found to delete."
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
            "duplicates": reversed(duplicates),
            "skipped_rows": reversed(skipped_rows)
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


class PurposeOfVisitListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()

        # -----------------------
        # CUSTOM SORTING (Excel type)
        # -----------------------
        custom_sort = request.GET.get('customSort')
        allowed_sort_fields = ['name', 'description', 'created_at']

        if custom_sort:
            sort_fields = []
            for rule in custom_sort.split(','):
                try:
                    field, order = rule.split(':')
                    field = field.strip()
                    order = order.strip().lower()

                    if field not in allowed_sort_fields:
                        continue

                    # Case-insensitive sorting like Excel
                    if order == "asc":
                        sort_fields.append(F(field).asc(nulls_last=True))
                    else:
                        sort_fields.append(F(field).desc(nulls_last=True))

                except ValueError:
                    continue

        else:
            # NORMAL SORTING
            sort_by = request.GET.get('sortBy', 'created_at')
            sort_order = request.GET.get('sortOrder', 'desc')

            if sort_by not in allowed_sort_fields:
                sort_by = 'created_at'

            if sort_order == 'desc':
                sort_fields = [f'-{sort_by}']
            else:
                sort_fields = [sort_by]

        # ---------------------------
        # BASE QUERY
        # ---------------------------
        queryset = PurposeOfVisit.objects.filter(is_deleted=False)

        # ---------------------------
        # STRICT SEARCH (name only)
        # ---------------------------
        if search:
            queryset = queryset.filter(name__istartswith=search)

        # ---------------------------
        # APPLY SORTING
        # ---------------------------
        queryset = queryset.order_by(*sort_fields)

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
        search = request.GET.get("search", "").strip()   # <-- added search

        if not ids:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide 'id' (UUID list or 'all')."
            }, status=status.HTTP_400_BAD_REQUEST)

        # ----------------------------------------------------------------
        # DELETE ALL (with optional search filter)
        # ----------------------------------------------------------------
        if ids == "all":
            visits = PurposeOfVisit.objects.filter(is_deleted=False)

            # Apply search filter
            if search:
                visits = visits.filter(name__icontains=search)

            count = visits.count()

            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No Purpose Of Visit records found to delete."
                }, status=status.HTTP_404_NOT_FOUND)

            # Hard delete (your original logic)
            visits.delete()

            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} Purpose Of Visit records deleted successfully."
            }, status=status.HTTP_200_OK)

        # ----------------------------------------------------------------
        # SELECTED DELETE (Only selected IDs should delete)
        # ----------------------------------------------------------------
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

        # Apply selected UUIDs
        visits = PurposeOfVisit.objects.filter(uuid__in=valid_uuids, is_deleted=False)

        # Apply search (BUT still delete only selected UUIDs)
        if search:
            visits = visits.filter(name__icontains=search)

        count = visits.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching Purpose Of Visit records found."
            }, status=status.HTTP_404_NOT_FOUND)

        # Hard delete (your original logic)
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
            "duplicates": reversed(duplicates),
            "skipped_rows": reversed(skipped_rows)
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


class DocumentsForListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()

        # -----------------------
        # CUSTOM SORTING (Excel type)
        # -----------------------
        custom_sort = request.GET.get('customSort')
        allowed_sort_fields = ['name', 'updated_at', 'created_at']

        if custom_sort:
            sort_fields = []
            for rule in custom_sort.split(','):
                try:
                    field, order = rule.split(':')
                    field = field.strip()
                    order = order.strip().lower()

                    if field not in allowed_sort_fields:
                        continue

                    # Excel-like case-insensitive sort
                    if order == "asc":
                        sort_fields.append(F(field).asc(nulls_last=True))
                    else:
                        sort_fields.append(F(field).desc(nulls_last=True))

                except ValueError:
                    continue

        else:
            # NORMAL SORTING
            sort_by = request.GET.get('sortBy', 'created_at')
            sort_order = request.GET.get('sortOrder', 'desc')

            if sort_by not in allowed_sort_fields:
                sort_by = 'created_at'

            if sort_order == 'asc':
                sort_fields = [sort_by]
            else:
                sort_fields = [f'-{sort_by}']

        # ---------------------------
        # BASE QUERY
        # ---------------------------
        queryset = DocumentsFor.objects.filter(is_deleted=False)

        # ---------------------------
        # STRICT SEARCH (ONLY name)
        # ---------------------------
        if search:
            queryset = queryset.filter(name__istartswith=search)

        # ---------------------------
        # APPLY SORTING
        # ---------------------------
        queryset = queryset.order_by(*sort_fields)

        # Pagination
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
        search = request.GET.get("search", "").strip()   # <-- added search support

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

        # -------- Delete ALL (with search support) --------
        if ids == "all":
            records = DocumentsFor.objects.all()

            # Apply search filter
            if search:
                records = records.filter(name__icontains=search)

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

        # -------- Bulk delete only selected UUIDs (with search applied safely) --------
        records = DocumentsFor.objects.filter(uuid__in=valid_uuids)

        # Apply search filter too — BUT still delete ONLY selected UUIDs
        if search:
            records = records.filter(name__icontains=search)

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
            "duplicates": reversed(duplicates),
            "skipped_rows": reversed(skipped_rows),
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
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()

        # -----------------------------------------------------
        # SORT FIELD MAP — Correct fields based on your model
        # -----------------------------------------------------
        allowed_sort_fields = {
            'created_at': 'created_at',
            'country': 'country__name',
            'visa_main_category': 'visa_main_category__name',
            'visa_major_category': 'visa_major_category__name',
            'visa_name': 'visa_name__name',
            'document_category': 'document_category__name',
            'document_name': 'document_name__document_name'
        }

        custom_sort = request.GET.get('customSort')
        sort_fields = []

        # -----------------------------------------------------
        # CUSTOM SORTING (Excel Style)
        # -----------------------------------------------------
        if custom_sort:
            for rule in custom_sort.split(','):
                try:
                    field, order = rule.split(':')
                    field = field.strip()
                    order = order.strip().lower()

                    if field not in allowed_sort_fields:
                        continue

                    orm_field = allowed_sort_fields[field]

                    if order == "asc":
                        sort_fields.append(F(orm_field).asc(nulls_last=True))
                    else:
                        sort_fields.append(F(orm_field).desc(nulls_last=True))

                except ValueError:
                    continue

        else:
            # -----------------------------------------------------
            # NORMAL SORTING
            # -----------------------------------------------------
            sort_by = request.GET.get('sortBy', 'created_at')
            sort_order = request.GET.get('sortOrder', 'desc')

            if sort_by not in allowed_sort_fields:
                sort_by = 'created_at'

            orm_field = allowed_sort_fields[sort_by]

            if sort_order == "asc":
                sort_fields = [orm_field]
            else:
                sort_fields = [f"-{orm_field}"]

        # -----------------------------------------------------
        # BASE QUERY
        # -----------------------------------------------------
        queryset = RequiredDocument.objects.filter(is_deleted=False).select_related(
            'country',
            'visa_main_category',
            'visa_major_category',
            'visa_name',
            'document_category',
            'document_name'
        )

        # -----------------------------------------------------
        # STRICT SEARCH — ONLY document_for (document_name)
        # -----------------------------------------------------
        if search:
            queryset = queryset.filter(
                document_name__document_name__istartswith=search
            )

        # -----------------------------------------------------
        # APPLY SORTING
        # -----------------------------------------------------
        queryset = queryset.order_by(*sort_fields)

        # -----------------------------------------------------
        # PAGINATION
        # -----------------------------------------------------
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = RequiredDocumentSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

#New API
class VisaMajorByCountryListAPIView(APIView):
    def get(self, request, representing_country_uuid):

        # Step 1 — Validate representing country
        representing_country = (
            RepresentingCountry.objects
            .filter(uuid=representing_country_uuid, is_deleted=False)
            .select_related("country")
            .first()
        )

        if not representing_country:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Representing Country not found"
            }, status=404)

        # Step 2 — Get the actual mapped country
        country_obj = representing_country.country

        # Step 3 — Fetch distinct Visa Major categories from RequiredDocument
        visa_majors = (
            RequiredDocument.objects.filter(
                country=country_obj,
                is_deleted=False
            )
            .values(
                "visa_major_category__uuid",
                "visa_major_category__name"
            )
            .distinct()
        )

        # Step 4 — Prepare the response list
        data = [
            {
                "uuid": item["visa_major_category__uuid"],
                "name": item["visa_major_category__name"]
            }
            for item in visa_majors
        ]

        return Response({
            "statusCode": 200,
            "status": True,
            "representing_country": representing_country.fullName,  # FIXED
            "mapped_country": country_obj.fullName,
            "count": len(data),
            "data": data
        }, status=200)


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

        # Filters for search delete
        documents_for = request.GET.get("documents_for")
        country = request.GET.get("country")
        visa_main = request.GET.get("visa_main_category")
        visa_major = request.GET.get("visa_major_category")

        if not ids:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide 'id' (UUID list or 'all')."
            }, status=status.HTTP_400_BAD_REQUEST)

        # -----------------------------------------------------
        # DELETE ALL (with search/filter support)
        # -----------------------------------------------------
        if ids == "all":
            objs = RequiredDocument.objects.filter(is_deleted=False)

            # Apply filters
            if documents_for:
                objs = objs.filter(documents_for__uuid=documents_for)

            if country:
                objs = objs.filter(country__uuid=country)

            if visa_main:
                objs = objs.filter(visa_main_category__uuid=visa_main)

            if visa_major:
                objs = objs.filter(visa_major_category__uuid=visa_major)

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

        # -----------------------------------------------------
        # UUID list validation
        # -----------------------------------------------------
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

        # -----------------------------------------------------
        # SELECTED DELETE (with safe search filters)
        # Only selected UUIDs should delete
        # -----------------------------------------------------
        objs = RequiredDocument.objects.filter(uuid__in=valid_uuids, is_deleted=False)

        # Apply filters (but still delete only selected UUIDs)
        if documents_for:
            objs = objs.filter(documents_for__uuid=documents_for)

        if country:
            objs = objs.filter(country__uuid=country)

        if visa_main:
            objs = objs.filter(visa_main_category__uuid=visa_main)

        if visa_major:
            objs = objs.filter(visa_major_category__uuid=visa_major)

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
            "duplicates": reversed(duplicates),
            "skipped_rows": reversed(skipped_rows),
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
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        custom_sort = request.GET.get('customSort')

        # ---------------------------------------------------------
        # ALLOWED SORT FIELDS + ORM MAPPING
        # ---------------------------------------------------------
        allowed_sort_fields = {
            'process_status_name': 'process_status_name__name',
            'country': 'country__name',
            'visa_main_category': 'visa_main_category__name',
            'created_at': 'created_at'
        }

        sort_fields = []

        # ---------------------------------------------------------
        # CUSTOM SORT (Excel-like)
        # ---------------------------------------------------------
        if custom_sort:
            for rule in custom_sort.split(','):
                try:
                    field, order = rule.split(':')
                    field = field.strip()
                    order = order.strip().lower()

                    if field not in allowed_sort_fields:
                        continue

                    orm_field = allowed_sort_fields[field]

                    # Case-insensitive sort for string fields
                    if field in ["process_status_name", "country", "visa_main_category"]:
                        f = Lower(orm_field)
                    else:
                        f = F(orm_field)

                    sort_fields.append(
                        f.asc(nulls_last=True) if order == 'asc' else f.desc(nulls_last=True)
                    )
                except ValueError:
                    continue

        else:
            # ---------------------------------------------------------
            # DEFAULT SORT (sortBy + sortOrder)
            # ---------------------------------------------------------
            sort_by = request.GET.get('sortBy', 'created_at')
            sort_order = request.GET.get('sortOrder', 'desc')

            if sort_by not in allowed_sort_fields:
                sort_by = 'created_at'

            orm_field = allowed_sort_fields[sort_by]

            f = F(orm_field)
            sort_fields = [
                f.desc(nulls_last=True) if sort_order == 'desc' else f.asc(nulls_last=True)
            ]

        # ---------------------------------------------------------
        # BASE QUERY
        # ---------------------------------------------------------
        queryset = ProcessStatusName.objects.filter(is_deleted=False).select_related(
            'country', 'visa_main_category'
        )

        # ---------------------------------------------------------
        # STRICT SEARCH — ONLY on Process Status Name
        # ---------------------------------------------------------
        if search:
            queryset = queryset.filter(
                process_status_name__name__istartswith=search
            )

        # ---------------------------------------------------------
        # APPLY SORTING
        # ---------------------------------------------------------
        queryset = queryset.order_by(*sort_fields)

        # ---------------------------------------------------------
        # PAGINATION
        # ---------------------------------------------------------
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

        # Filters
        country = request.GET.get("country")
        visa_main = request.GET.get("visa_main_category")

        if not ids:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Provide 'id' (UUID list or 'all')"
            }, status=status.HTTP_400_BAD_REQUEST)

        # ------------------------------------------------
        # DELETE ALL (with FILTER support)
        # ------------------------------------------------
        if ids == "all":
            objs = ProcessStatusName.objects.filter(is_deleted=False)

            # Apply filters
            if country:
                objs = objs.filter(country__uuid=country)

            if visa_main:
                objs = objs.filter(visa_main_category__uuid=visa_main)

            count = objs.count()
            objs.update(is_deleted=True)

            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All ({count}) Process Status records deleted."
            })

        # ------------------------------------------------
        # Validate UUID LIST
        # ------------------------------------------------
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

        # ------------------------------------------------
        # DELETE ONLY SELECTED (with FILTERS applied)
        # ------------------------------------------------
        objs = ProcessStatusName.objects.filter(uuid__in=valid_uuids, is_deleted=False)

        # Apply filters (VERY IMPORTANT: delete only selected UUIDs)
        if country:
            objs = objs.filter(country__uuid=country)

        if visa_main:
            objs = objs.filter(visa_main_category__uuid=visa_main)

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
            "duplicates": reversed(duplicates),
            "skipped_rows": reversed(skipped_rows)
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
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()

        # -----------------------
        # CUSTOM SORTING (Excel type)
        # -----------------------
        custom_sort = request.GET.get('customSort')

        # Allowed fields (ONLY THESE)
        allowed_sort_fields = [
            'process_sub_status_name',
            'country__name',
            'visa_main_category__name',
            'process_status_name__name',
            'created_at'
        ]

        if custom_sort:
            sort_fields = []
            for rule in custom_sort.split(','):
                try:
                    field, order = rule.split(':')
                    field = field.strip()
                    order = order.strip().lower()

                    if field not in allowed_sort_fields:
                        continue

                    # Case-insensitive Excel-like sort
                    if order == "asc":
                        sort_fields.append(F(field).asc(nulls_last=True))
                    else:
                        sort_fields.append(F(field).desc(nulls_last=True))

                except ValueError:
                    continue

        else:
            # NORMAL SORTING
            sort_by = request.GET.get('sortBy', 'created_at')
            sort_order = request.GET.get('sortOrder', 'desc')

            if sort_by not in allowed_sort_fields:
                sort_by = 'created_at'

            if sort_order == 'desc':
                sort_fields = [f'-{sort_by}']
            else:
                sort_fields = [sort_by]

        # ---------------------------
        # Base queryset
        # ---------------------------
        queryset = ProcessSubStatusName.objects.filter(is_deleted=False).select_related(
            'country', 'visa_main_category', 'process_status_name'
        )

        # ---------------------------
        # Search (ONLY process_sub_status_name)
        # ---------------------------
        if search:
            queryset = queryset.filter(
                process_sub_status_name__istartswith=search
            )

        # ---------------------------
        # APPLY SORTING
        # ---------------------------
        queryset = queryset.order_by(*sort_fields)

        # Pagination
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



#New API
class ProcessSubStatusByCountryAPIView(APIView):

    def get(self, request, representing_country_uuid):

        representing_country = (
            RepresentingCountry.objects
            .filter(uuid=representing_country_uuid, is_deleted=False)
            .select_related("country")
            .first()
        )

        if not representing_country:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Representing Country not found"
            }, status=404)

        # Step 2 — Get actual country object linked to representing country
        country_obj = representing_country.country  

        # Step 3 — Filter ProcessSubStatus by THIS country
        items = (
            ProcessSubStatusName.objects
            .filter(country=country_obj, is_deleted=False)
            .select_related("process_status_name")
            .order_by("process_sub_status_name")
        )

        # Step 4 — Prepare response
        data = [
            {
                "uuid": i.uuid,
                "country_name": i.country.fullName,
                "visa_main_category_name": i.visa_main_category.visa_main_category,
                "process_status_name_value": i.process_status_name.process_status_name,
                "process_sub_status_name": i.process_sub_status_name,
                "description": i.description,
            }
            for i in items
        ]

        return Response({
            "statusCode": 200,
            "status": True,
            "representing_country": representing_country.full_name,
            "mapped_country": country_obj.fullName,
            "count": len(data),
            "data": data
        }, status=200)


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

        # Filters
        country = request.GET.get("country")
        visa_main_category = request.GET.get("visa_main_category")
        process_status_name = request.GET.get("process_status_name")
        search = request.GET.get("search", "").strip()

        if not ids:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Provide 'id' (UUID list or 'all')"
            }, status=400)

        # Build base queryset with filters + search
        queryset = ProcessSubStatusName.objects.filter(is_deleted=False)

        if country:
            queryset = queryset.filter(country__uuid=country)

        if visa_main_category:
            queryset = queryset.filter(visa_main_category__uuid=visa_main_category)

        if process_status_name:
            queryset = queryset.filter(process_status_name__uuid=process_status_name)

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )

        # -------------------------------
        #        BULK DELETE (ALL)
        # -------------------------------
        if ids == "all":
            count = queryset.count()
            queryset.update(is_deleted=True)
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"({count}) Process Sub Status records deleted."
            })

        # -------------------------------
        #     SINGLE / MULTIPLE DELETE
        # -------------------------------
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

        # Only delete selected items from filtered + searched result
        objs = queryset.filter(uuid__in=valid_uuids)
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
            "duplicates": reversed(duplicates),
            "skipped_rows": reversed(skipped_rows)
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
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get("search", "").strip()

        # -----------------------
        # CUSTOM SORTING (Excel type)
        # -----------------------
        custom_sort = request.GET.get("customSort")

        # Allowed sorting fields
        allowed_sort_fields = ["name", "description", "created_at", "updated_at"]

        sort_fields = []

        if custom_sort:
            for rule in custom_sort.split(","):
                try:
                    field, order = rule.split(":")
                    field = field.strip()
                    order = order.strip().lower()

                    if field not in allowed_sort_fields:
                        continue

                    # Case-insensitive sort for string fields
                    if field in ["name", "description"]:
                        f = Lower(field)
                    else:
                        f = F(field)

                    sort_fields.append(f.asc(nulls_last=True) if order == "asc" else f.desc(nulls_last=True))

                except ValueError:
                    continue

        else:
            # -----------------------
            # NORMAL SORTING
            # -----------------------
            sort_by = request.GET.get("sortBy", "created_at")
            sort_order = request.GET.get("sortOrder", "desc")

            if sort_by not in allowed_sort_fields:
                sort_by = "created_at"

            if sort_by in ["name", "description"]:
                f = Lower(sort_by)
            else:
                f = F(sort_by)

            sort_fields = [f.asc(nulls_last=True) if sort_order == "asc" else f.desc(nulls_last=True)]

        # -----------------------
        # BASE QUERYSET
        # -----------------------
        queryset = ProcessType.objects.filter(is_deleted=False)

        # -----------------------
        # SEARCH (using Q)
        # -----------------------
        if search:
            queryset = queryset.filter(
                Q(name__istartswith=search)
            )

        # -----------------------
        # APPLY SORTING
        # -----------------------
        queryset = queryset.order_by(*sort_fields)

        # Pagination + Serialization
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

        # SEARCH SUPPORT
        search = request.GET.get("search", "").strip()

        if not ids:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Provide 'id' (UUID list or 'all')"
            }, status=400)

        # BASE QUERYSET (with search)
        queryset = ProcessType.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )

        # ---------------------------
        #      BULK DELETE (ALL)
        # ---------------------------
        if ids == "all":
            count = queryset.count()
            queryset.update(is_deleted=True)
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All ({count}) Process Types deleted successfully."
            })

        # ---------------------------
        #  SINGLE / MULTIPLE DELETE
        # ---------------------------
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

        # Only delete items from searched result
        objs = queryset.filter(uuid__in=valid_uuids)
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
            "duplicates": reversed(duplicates),
            "skipped_rows": reversed(skipped_rows)
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
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get("search", "").strip()
        custom_sort = request.GET.get("customSort")  # e.g., name:asc,created_at:desc

        # Allowed sortable fields (must match DB columns)
        allowed_sort_fields = ["name", "description", "created_at", "updated_at"]

        queryset = PaymentTo.objects.filter(is_deleted=False)

        # --------------------------
        # SEARCH (Only on main column: name)
        # --------------------------
        if search:
            queryset = queryset.filter(Q(name__istartswith=search))

        # ORM reference mapping
        sort_field_map = {
            "name": "name",
            "description": "description",
            "created_at": "created_at",
            "updated_at": "updated_at",
        }

        sort_fields = []

        # --------------------------
        # CUSTOM SORT LOGIC (Excel type sorting)
        # --------------------------
        if custom_sort:
            for rule in custom_sort.split(","):
                try:
                    field, order = rule.split(":")
                    field = field.strip()
                    order = order.strip().lower()

                    # Skip unknown fields
                    if field not in sort_field_map:
                        continue

                    orm_field = sort_field_map[field]

                    # Case-insensitive for string fields
                    if field in ["name", "description"]:
                        f = Lower(orm_field)
                    else:
                        f = F(orm_field)

                    sort_fields.append(
                        f.asc(nulls_last=True)
                        if order == "asc"
                        else f.desc(nulls_last=True)
                    )

                except ValueError:
                    continue

        else:
            # --------------------------
            # NORMAL SORTING (Fallback)
            # --------------------------
            sort_by = request.GET.get("sortBy", "created_at")
            sort_order = request.GET.get("sortOrder", "desc")

            # Fix wrong sort field if given
            if sort_by not in allowed_sort_fields:
                sort_by = "created_at"

            orm_field = sort_field_map.get(sort_by, "created_at")
            f = F(orm_field)

            sort_fields = [
                f.asc(nulls_last=True) if sort_order == "asc" else f.desc(nulls_last=True)
            ]

        # Apply sorting
        queryset = queryset.order_by(*sort_fields)

        # Pagination + Serialization
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

    def delete(self, request, uuid=None):
        ids = request.data.get('id', None)

        # SEARCH SUPPORT
        search = request.GET.get("search", "").strip()

        # Base queryset WITH SEARCH
        queryset = PaymentTo.objects.all()
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )

        # ----------------------------------------
        # 1. DELETE using URL param UUID
        # ----------------------------------------
        if uuid:
            try:
                payment_to = queryset.get(uuid=uuid)  # searched version
                payment_to.delete()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "Payment To permanently deleted.",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            except PaymentTo.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Payment To not found within search results.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        # ----------------------------------------
        # 2. DELETE ALL (Only from SEARCH results)
        # ----------------------------------------
        if ids == "all":
            items = queryset  # delete only filtered data
            count = items.count()

            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No Payment To records found to delete in search results.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

            items.delete()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} Payment To record(s) permanently deleted based on search.",
                "data": None
            }, status=status.HTTP_200_OK)

        # ----------------------------------------
        # 3. BULK DELETE using list of UUIDs
        # ----------------------------------------
        if not ids or not isinstance(ids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide a list of UUIDs in 'id' field or 'all'.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        valid_uuids = []
        invalid_uuids = []

        # Validate all UUIDs
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

        # Fetch only SEARCHED ITEMS to delete
        items = queryset.filter(uuid__in=valid_uuids)
        count = items.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching Payment To records found in search results.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_404_NOT_FOUND)

        # PERMANENT DELETE
        items.delete()

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} Payment To record(s) permanently deleted based on search selection.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        }, status=status.HTTP_200_OK)


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
            "duplicates": reversed(duplicates),
            "skipped_rows": reversed(skipped_rows)
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
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get("search", "").strip()

        # --------------------------------------
        # CUSTOM SORTING (Excel type)
        # --------------------------------------
        custom_sort = request.GET.get("customSort")
        allowed_sort_fields = ["payment_category", "description", "created_at", "updated_at"]

        sort_fields = []

        if custom_sort:
            for rule in custom_sort.split(","):
                try:
                    field, order = rule.split(":")
                    field = field.strip()
                    order = order.strip().lower()

                    if field not in allowed_sort_fields:
                        continue

                    # Case-insensitive sort for string fields
                    if field in ["payment_category", "description"]:
                        expr = Lower(field)
                    else:
                        expr = F(field)

                    sort_fields.append(
                        expr.asc(nulls_last=True) if order == "asc" else expr.desc(nulls_last=True)
                    )

                except ValueError:
                    continue

        else:
            # --------------------------------------
            # NORMAL SORTING
            # --------------------------------------
            sort_by = request.GET.get("sortBy", "created_at")
            sort_order = request.GET.get("sortOrder", "desc")

            if sort_by not in allowed_sort_fields:
                sort_by = "created_at"

            if sort_by in ["payment_category", "description"]:
                expr = Lower(sort_by)
            else:
                expr = F(sort_by)

            sort_fields = [
                expr.asc(nulls_last=True) if sort_order == "asc" else expr.desc(nulls_last=True)
            ]

        # --------------------------------------
        # BASE QUERYSET
        # --------------------------------------
        queryset = PaymentCategory.objects.filter(is_deleted=False)

        # --------------------------------------
        # SEARCH (Only on payment_category)
        # --------------------------------------
        if search:
            queryset = queryset.filter(
                Q(payment_category__istartswith=search)
            )

        # --------------------------------------
        # APPLY SORTING
        # --------------------------------------
        queryset = queryset.order_by(*sort_fields)

        # --------------------------------------
        # PAGINATION + SERIALIZER
        # --------------------------------------
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

        # SEARCH + FILTER SUPPORT
        search = request.GET.get("search", "").strip()
        payment_to = request.GET.get("paymentTo", "").strip()

        # Base queryset
        queryset = PaymentCategory.objects.filter(is_deleted=False)

        # Apply SEARCH
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )

        # Apply FILTER (PaymentTo)
        if payment_to:
            queryset = queryset.filter(payment_to__uuid=payment_to)

        # ----------------------------------------
        # 1. DELETE ALL (ONLY from filtered & searched data)
        # ----------------------------------------
        if ids == "all":
            count = queryset.count()

            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No Payment Categories found to delete in search/filter results."
                }, status=404)

            queryset.update(is_deleted=True)
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All ({count}) Payment Categories deleted based on search/filter."
            })

        # ----------------------------------------
        # 2. DELETE SELECTED UUIDs
        # ----------------------------------------
        if not ids or not isinstance(ids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Provide list of UUIDs or 'all'."
            }, status=400)

        valid_uuids, invalid_uuids = [], []
        for u in ids:
            try:
                valid_uuids.append(UUID(u))
            except ValueError:
                invalid_uuids.append(u)

        # Only delete from search + filter results
        objs = queryset.filter(uuid__in=valid_uuids)
        count = objs.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching Payment Category records found in search/filter results.",
                "invalid_uuids": invalid_uuids
            }, status=404)

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
        file = request.FILES.get("file")
        sheet_name = request.data.get("sheet_name")

        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split(".")[-1].lower()
        duplicates = []
        skipped_rows = []

        required_headers = {"payment to", "payment category"}
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
                        "message": (
                            f"Missing required headers. Required: {required_headers}, "
                            f"Found: {set(headers)}"
                        )
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

                payment_to_name = (
                    str(row.get("payment to")).strip()
                    if row.get("payment to") else None
                )
                category_name = (
                    str(row.get("payment category")).strip()
                    if row.get("payment category") else None
                )
                description = (
                    str(row.get("description")).strip()
                    if row.get("description") else ""
                )

                # ----- Validate Payment To -----
                if not payment_to_name:
                    skipped_rows.append({
                        "Row": row_number,
                        "Reason": "Missing Payment To"
                    })
                    continue

                payment_to_obj = PaymentTo.objects.filter(
                    name__iexact=payment_to_name,
                    is_deleted=False
                ).first()

                if not payment_to_obj:
                    skipped_rows.append({
                        "Row": row_number,
                        "Reason": f'Payment To "{payment_to_name}" not found'
                    })
                    continue

                # ----- Validate Payment Category -----
                if not category_name:
                    skipped_rows.append({
                        "Row": row_number,
                        "Reason": "Missing Payment Category"
                    })
                    continue

                existing = PaymentCategory.objects.filter(
                    payment_to=payment_to_obj,
                    payment_category__iexact=category_name
                ).first()

                if existing:
                    if not existing.is_deleted:
                        duplicates.append({
                            "Row": row_number,
                            "Payment Category": category_name,
                            "Reason": "Already exists in database"
                        })
                        continue
                    else:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                else:
                    PaymentCategory.objects.create(
                        payment_to=payment_to_obj,
                        payment_category=category_name,
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
            "duplicates": reversed(duplicates),
            "skipped_rows": reversed(skipped_rows),
        }, status=status.HTTP_200_OK)



