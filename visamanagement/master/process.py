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
                queryset = DocumentCategory.objects.all()

                deletable = []
                non_deletable = []

                for obj in queryset:
                    if DocumentName.objects.filter(document_category=obj).exists():
                        non_deletable.append(obj)
                    else:
                        deletable.append(obj)

                deleted_count = len(deletable)
                not_deleted_count = len(non_deletable)

                # delete only safe ones
                DocumentCategory.objects.filter(id__in=[o.id for o in deletable]).delete()

                return Response({
                    "statusCode": 200,
                    "status": True,
                    "message": f"{deleted_count} data deleted; {not_deleted_count} data not deleted, they are connected to another table."
                })

            # ----------------------------------
            # BASE QUERYSET
            # ----------------------------------
            queryset = DocumentCategory.objects.all()

            # ----------------------------------
            # SEARCH FILTER
            # ----------------------------------
            if search:
                queryset = queryset.filter(name__istartswith=search)

            # ---------------------------------------------------
            # CASE 2: DELETE ALL MATCHING SEARCH RESULTS
            # ---------------------------------------------------
            if delete_all:

                deletable = []
                non_deletable = []

                for obj in queryset:
                    if DocumentName.objects.filter(document_category=obj).exists():
                        non_deletable.append(obj)
                    else:
                        deletable.append(obj)

                deleted_count = len(deletable)
                not_deleted_count = len(non_deletable)

                DocumentCategory.objects.filter(id__in=[o.id for o in deletable]).delete()

                return Response({
                    "statusCode": 200,
                    "status": True,
                    "message": f"{deleted_count} data is deleted ; {not_deleted_count} data is not deleted ,they are connected to another table",
                })

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

            deletable = []
            non_deletable = []

            for obj in filtered_objects:
                if DocumentName.objects.filter(document_category=obj).exists():
                    non_deletable.append(obj)
                else:
                    deletable.append(obj)

            # delete safe ones
            DocumentCategory.objects.filter(id__in=[o.id for o in deletable]).delete()

            # -----------------------------
            # SINGLE DELETE MESSAGE
            # -----------------------------
            if len(valid_uuids) == 1:
                if len(non_deletable) == 1:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": "Could not delete the data, it is connected to another table."
                    })
                else:
                    return Response({
                        "statusCode": 200,
                        "status": True,
                        "message": "1 data deleted successfully."
                    })

            # -----------------------------
            # MULTIPLE DELETE MESSAGE
            # -----------------------------
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"{len(deletable)} data is deleted ; {len(non_deletable)} data is not deleted ,they are connected to another table",
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

    REQUIRED_HEADERS = {"document category"}
    OPTIONAL_HEADERS = {"description"}

    def post(self, request):
        file = request.FILES.get("file")
        sheet_name = request.data.get("sheet_name")

        if not file:
            return Response({"statusCode": 400, "status": False, "message": "No file uploaded"}, status=400)

        format_type = file.name.split(".")[-1].lower()
        data = []
        duplicates = []
        skipped_rows = []
        to_create = []
        seen_in_file = set()

        try:
            # =========================
            #   READ XLSX FILE
            # =========================
            if format_type == "xlsx":
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": "Please provide sheet_name",
                        "available_sheets": available_sheets,
                    }, status=400)

                if sheet_name not in available_sheets:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'Sheet "{sheet_name}" not found',
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
                    str(c.value).strip().lower() if c.value else ""
                    for c in next(ws.iter_rows(min_row=1, max_row=1))
                ]

                if not self.REQUIRED_HEADERS.issubset(set(headers)):
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f"Missing required headers. Required: {self.REQUIRED_HEADERS}, Found: {set(headers)}"
                    }, status=400)

                for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    row_dict["_row_number"] = idx
                    data.append(row_dict)

            # =========================
            #   READ CSV FILE
            # =========================
            elif format_type == "csv":
                decoded_file = file.read().decode("utf-8")
                dataset = Dataset()
                dataset.load(decoded_file, format="csv")

                for idx, row in enumerate(dataset.dict, start=2):
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    row_lower["_row_number"] = idx

                    if not self.REQUIRED_HEADERS.issubset(set(row_lower.keys())):
                        return Response({
                            "statusCode": 400,
                            "status": False,
                            "message": f"Missing required headers. Required: {self.REQUIRED_HEADERS}"
                        }, status=400)

                    data.append(row_lower)

            else:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Unsupported file format. Use .xlsx or .csv",
                }, status=400)

            # =========================
            #   PRELOAD EXISTING RECORDS
            # =========================
            existing_map = {
                dc.name.lower(): dc
                for dc in DocumentCategory.objects.all()
            }

            imported_count = 0

            # =========================
            #   PROCESS ROWS IN REVERSE ORDER
            # =========================
            for row in reversed(data):
                row_no = row.get("_row_number", "Unknown")
                name = str(row.get("document category") or "").strip()
                description = str(row.get("description") or "").strip()

                # ---------------- VALIDATION ----------------
                skip_reason = None

                if not name:
                    skip_reason = "Document category is required"
                elif name.isdigit():
                    skip_reason = "Numbers are not allowed"
                else:
                    has_alnum = any(c.isalnum() for c in name)
                    if not has_alnum:
                        skip_reason = "Special characters only are not allowed"

                if skip_reason:
                    skipped_rows.append({
                        "Row": row_no,
                        "Document Category": name or "",
                        "Description": description,
                        "Reason": skip_reason
                    })
                    continue

                # ---------------- DUPLICATES ----------------
                key = name.lower()

                if key in seen_in_file:
                    duplicates.append({
                        "Row": row_no,
                        "Document Category": name,
                        "Description": description,
                        "Reason": "Duplicate in uploaded file"
                    })
                    continue

                seen_in_file.add(key)

                existing = existing_map.get(key)
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({
                            "Row": row_no,
                            "Document Category": name,
                            "Description": description,
                            "Reason": "Already exists in database"
                        })
                        continue

                    # Restore soft-deleted
                    existing.description = description
                    existing.is_deleted = False
                    existing.save()
                    imported_count += 1
                    continue

                # Add to bulk create
                to_create.append(
                    DocumentCategory(
                        name=name,
                        description=description,
                        is_deleted=False
                    )
                )

            # =========================
            #   BULK CREATE
            # =========================
            if to_create:
                batch_size = 500
                for i in range(0, len(to_create), batch_size):
                    DocumentCategory.objects.bulk_create(to_create[i:i + batch_size])

                imported_count += len(to_create)

        except Exception as e:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": str(e)
            }, status=400)

        # =========================
        #   SUCCESS RESPONSE (REVERSED)
        # =========================
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": list(reversed(duplicates)),
            "skipped_rows": list(reversed(skipped_rows))
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
        file = request.FILES.get("file")
        sheet_name = request.data.get("sheet_name")

        if not file:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "No file uploaded"
            }, status=400)

        format_type = file.name.split(".")[-1].lower()

        # REQUIRED HEADERS
        required_headers = {"document name", "document category"}
        optional_headers = {"description"}

        data = []
        duplicates = []
        skipped_rows = []
        to_create = []
        seen_in_file = set()

        # ------- Category Map -------
        category_map = {
            c.name.strip().lower(): c
            for c in DocumentCategory.objects.all()
        }

        # ------------ Read XLSX ------------
        try:
            if format_type == "xlsx":
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": "Please provide sheet_name",
                        "available_sheets": available_sheets
                    }, status=400)

                if sheet_name not in available_sheets:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'Sheet \"{sheet_name}\" not found',
                        "available_sheets": available_sheets
                    }, status=400)

                ws = wb[sheet_name]

                if ws.max_row <= 1:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'Sheet \"{sheet_name}\" is empty.'
                    }, status=400)

                headers = [
                    str(c.value).strip().lower() if c.value else ""
                    for c in next(ws.iter_rows(min_row=1, max_row=1))
                ]

                if not required_headers.issubset(set(headers)):
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f"Missing required headers. Required: {required_headers} Found: {set(headers)}"
                    }, status=400)

                for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    row_dict["_row_number"] = idx
                    data.append(row_dict)

            # ------------ Read CSV ------------
            elif format_type == "csv":
                decoded = file.read().decode("utf-8")
                dataset = Dataset()
                dataset.load(decoded, format="csv")

                for idx, row in enumerate(dataset.dict, start=2):
                    row_lower = {k.strip().lower(): v for k, v in row.items()}
                    row_lower["_row_number"] = idx

                    if not required_headers.issubset(row_lower.keys()):
                        return Response({
                            "statusCode": 400,
                            "status": False,
                            "message": f"Missing required headers. Required: {required_headers}"
                        }, status=400)

                    data.append(row_lower)

            else:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Unsupported file format. Use .xlsx or .csv"
                }, status=400)

            # ------- Preload ALL existing records -------
            existing_map = {
                (d.document_category_id, d.document_name.lower()): d
                for d in DocumentName.objects.all()
            }

            imported_count = 0

            # ------- Process Rows in Reverse -------
            for row in reversed(data):
                row_no = row.get("_row_number")

                name = str(row.get("document name") or "").strip()
                category_name = str(row.get("document category") or "").strip()
                description = str(row.get("description") or "").strip()

                if not name:
                    skipped_rows.append({
                        "Row": row_no,
                        "Document Name": name,
                        "Description": description,
                        "Reason": "Missing Document Name"
                    })
                    continue

                if not category_name:
                    skipped_rows.append({
                        "Row": row_no,
                        "Document Name": name,
                        "Description": description,
                        "Reason": "Missing Document Category"
                    })
                    continue

                # Map category
                category_obj = category_map.get(category_name.lower())
                if not category_obj:
                    skipped_rows.append({
                        "Row": row_no,
                        "Document Name": name,
                        "Document Category": category_name,
                        "Reason": "Document Category not found in database"
                    })
                    continue

                key = (category_obj.id, name.lower())

                # Duplicate inside file
                if key in seen_in_file:
                    duplicates.append({
                        "Row": row_no,
                        "Document Name": name,
                        "Description": description,
                        "Reason": "Duplicate in uploaded file"
                    })
                    continue

                seen_in_file.add(key)

                # Existing record in DB
                existing = existing_map.get(key)
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({
                            "Row": row_no,
                            "Document Name": name,
                            "Description": description,
                            "Reason": "Already exists in database"
                        })
                        continue

                    # Reactivate deleted record
                    existing.description = description
                    existing.is_deleted = False
                    existing.save()
                    imported_count += 1
                    continue

                # Create new instance
                to_create.append(DocumentName(
                    document_category=category_obj,
                    document_name=name,
                    description=description,
                    is_deleted=False
                ))

            # ------- Bulk Insert -------
            if to_create:
                batch_size = 500
                for i in range(0, len(to_create), batch_size):
                    DocumentName.objects.bulk_create(to_create[i:i+batch_size])
                imported_count += len(to_create)

        except Exception as e:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": str(e),
            }, status=400)

        # ------- Response -------
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Import successful",
            "imported_count": imported_count,
            "duplicates": list(reversed(duplicates)),
            "skipped_rows": list(reversed(skipped_rows))
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
        try:
            search = request.GET.get("search", "").strip()
            delete_all = request.data.get("deleteAll", False)
            ids = request.data.get("id", None)

            # ------------------------------------------------------
            # CASE 1: DELETE ENTIRE TABLE (id = "all")
            # ------------------------------------------------------
            if ids == "all":
                queryset = DocumentType.objects.filter(is_deleted=False)

                deleted_count = queryset.count()
                queryset.update(is_deleted=True)

                return Response({
                    "statusCode": 200,
                    "status": True,
                    "message": f"{deleted_count} data deleted successfully."
                })

            # ------------------------------------------------------
            # BASE QUERYSET
            # ------------------------------------------------------
            queryset = DocumentType.objects.filter(is_deleted=False)

            # ------------------------------------------------------
            # SEARCH FILTER (Document Type column only)
            # ------------------------------------------------------
            if search:
                queryset = queryset.filter(name__istartswith=search)

            # ------------------------------------------------------
            # CASE 2: DELETE ALL MATCHING SEARCH RESULTS
            # ------------------------------------------------------
            if delete_all:
                deleted_count = queryset.count()
                queryset.update(is_deleted=True)

                return Response({
                    "statusCode": 200,
                    "status": True,
                    "message": f"{deleted_count} data deleted successfully."
                })

            # ------------------------------------------------------
            # CASE 3: DELETE SPECIFIC UUID LIST
            # ------------------------------------------------------
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

            # Filter only matched items
            filtered_objects = queryset.filter(uuid__in=valid_uuids)

            deleted_count = filtered_objects.count()
            filtered_objects.update(is_deleted=True)

            # -----------------------------
            # SINGLE DELETE MESSAGE
            # -----------------------------
            if len(valid_uuids) == 1:
                if deleted_count == 0:
                    return Response({
                        "statusCode": 404,
                        "status": False,
                        "message": "Could not delete, item not found."
                    })
                else:
                    return Response({
                        "statusCode": 200,
                        "status": True,
                        "message": "1 data deleted successfully."
                    })

            # -----------------------------
            # MULTIPLE DELETE MESSAGE
            # -----------------------------
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"{deleted_count} data deleted successfully.",
                "invalid_uuids": invalid_uuids if invalid_uuids else None
            }, status=200)

        except Exception as e:
            return Response({
                "statusCode": 500,
                "status": False,
                "message": f"Internal server error: {str(e)}"
            }, status=500)




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

    IMPORT_HEADERS_ORDER = [
        "uuid",
        "document type",
        "description",
        "created on",
        "modified on"
    ]

    REQUIRED_HEADERS = {"document type"}
    OPTIONAL_HEADERS = {"description"}

    def post(self, request):
        file = request.FILES.get("file")
        sheet_name = request.data.get("sheet_name")

        if not file:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "No file uploaded"
            }, status=400)

        format_type = file.name.split(".")[-1].lower()
        data = []
        duplicates = []
        skipped_rows = []
        to_create = []
        seen_in_file = set()

        try:
            # ---------------- XLSX ----------------
            if format_type == "xlsx":
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": "Please provide sheet_name",
                        "available_sheets": available_sheets
                    }, status=400)

                if sheet_name not in available_sheets:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'Sheet "{sheet_name}" not found',
                        "available_sheets": available_sheets
                    }, status=400)

                ws = wb[sheet_name]

                # if sheet empty
                if ws.max_row <= 1:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'Sheet "{sheet_name}" is empty.'
                    }, status=400)

                # Read and normalize headers
                headers = [str(c.value).strip().lower() if c.value else "" for c in next(ws.iter_rows(min_row=1, max_row=1))]

                if not self.REQUIRED_HEADERS.issubset(set(headers)):
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f"Missing required headers. Required: {self.REQUIRED_HEADERS}, Found: {set(headers)}"
                    }, status=400)

                # read rows
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

                    if not self.REQUIRED_HEADERS.issubset(set(row_lower.keys())):
                        return Response({
                            "statusCode": 400,
                            "status": False,
                            "message": f"Missing required headers. Required: {self.REQUIRED_HEADERS}, Found: {set(row_lower.keys())}"
                        }, status=400)

                    data.append(row_lower)

            else:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Unsupported file format. Use .xlsx or .csv"
                }, status=400)

            # ------------ Pre-load existing ------------
            existing_map = {dt.name.lower(): dt for dt in DocumentType.objects.all()}
            imported_count = 0

            # ------------ PROCESS ROWS IN REVERSED ORDER (so we can reverse result lists later) ------------
            for row in reversed(data):
                row_no = row.get("_row_number", "Unknown")
                # Collect wrong values in export-header order
                wrong_values = []

                # Raw reads (may be None)
                name_raw = row.get("document type")
                description_raw = row.get("description")

                # Normalize for DB insertion (empty string if blank)
                name = str(name_raw).strip() if name_raw not in [None, ""] else ""
                description = str(description_raw).strip() if description_raw not in [None, ""] else ""

                # ---------- VALIDATIONS (ORDERED) ----------
                # Document Type (required) — only letters & spaces allowed
                if not name:
                    # missing
                    wrong_values.append({"Document Type": name_raw})
                else:
                    # allow only letters and spaces (no digits, no special chars)
                    if not all((c.isalpha() or c.isspace()) for c in name):
                        # contains digits or special characters -> invalid
                        wrong_values.append({"Document Type": name_raw})

                # Description (optional) — accept str/int/float/bool; otherwise flag
                if description_raw not in [None, ""] and not isinstance(description_raw, (str, int, float, bool)):
                    wrong_values.append({"Description": description_raw})

                # If any wrong values — add to skipped_rows with Value list in order
                if wrong_values:
                    skipped_rows.append({
                        "Row": row_no,
                        "Value": wrong_values,
                        "Reason": "Invalid or missing data"
                    })
                    continue

                # ------------ DUPLICATE IN FILE ------------
                key = name.lower()
                if key in seen_in_file:
                    duplicates.append({
                        "Row": row_no,
                        "Document Type": name,
                        "Description": description,
                        "Reason": "Duplicate in uploaded file"
                    })
                    continue
                seen_in_file.add(key)

                # ------------ DUPLICATE IN DB ------------
                existing = existing_map.get(key)
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({
                            "Row": row_no,
                            "Document Type": name,
                            "Description": description,
                            "Reason": "Already exists in database"
                        })
                        continue
                    else:
                        # restore deleted
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                        continue

                # ------------ Prepare for bulk create ------------
                to_create.append(
                    DocumentType(
                        name=name,
                        description=description,
                        is_deleted=False
                    )
                )

            # ------------ Bulk Create (batched) ------------
            if to_create:
                batch_size = 500
                for i in range(0, len(to_create), batch_size):
                    DocumentType.objects.bulk_create(to_create[i:i + batch_size])
                imported_count += len(to_create)

        except Exception as e:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": str(e)
            }, status=400)

        # ------------ Final Response (original file order) ------------
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet \"{sheet_name}\" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": list(reversed(duplicates)),
            "skipped_rows": list(reversed(skipped_rows))
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
        ids = request.data.get('id', None)
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
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "No file uploaded"
            }, status=400)

        format_type = file.name.split(".")[-1].lower()
        required_headers = {"purpose of visit"}
        optional_headers = {"description"}

        data = []
        duplicates = []
        skipped_rows = []
        to_create = []
        seen_in_file = set()
        imported_count = 0

        try:
            # ---------------- XLSX ----------------
            if format_type == "xlsx":
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": "Please provide sheet_name",
                        "available_sheets": available_sheets
                    }, status=400)

                if sheet_name not in available_sheets:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'Sheet "{sheet_name}" not found',
                        "available_sheets": available_sheets
                    }, status=400)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'Sheet "{sheet_name}" is empty.'
                    }, status=400)

                headers = [str(c.value).strip().lower() if c.value else "" for c in next(ws.iter_rows(min_row=1, max_row=1))]
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
                            "message": f"Missing required headers. Required: {', '.join(required_headers)}. Found: {', '.join(row_lower.keys())}."
                        }, status=400)
                    data.append(row_lower)

            else:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Unsupported file format. Use .xlsx or .csv",
                }, status=400)

            # ---------------- EXISTING RECORDS ----------------
            existing_map = {p.name.lower(): p for p in PurposeOfVisit.objects.all()}

            # ---------------- PROCESS ROWS ----------------
            for row in reversed(data):
                row_no = row.get("_row_number", "Unknown")
                name = str(row.get("purpose of visit") or "").strip()
                description = str(row.get("description") or "").strip()

                # ---------------- VALIDATION ----------------
                if not name:
                    skipped_rows.append({
                        "Row": row_no,
                        "PurposeOfVisit": name,
                        "Description": description,
                        "Reason": "Purpose of Visit is empty"
                    })
                    continue

                if isinstance(row.get("purpose of visit"), (int, float)) or not any(c.isalpha() for c in name):
                    skipped_rows.append({
                        "Row": row_no,
                        "PurposeOfVisit": name,
                        "Description": description,
                        "Reason": "Invalid Input: Purpose of Visit"
                    })
                    continue

                if row.get("description") is not None and not isinstance(row.get("description"), (str, int, float, bool)):
                    skipped_rows.append({
                        "Row": row_no,
                        "PurposeOfVisit": name,
                        "Description": description,
                        "Reason": "Invalid description data"
                    })
                    continue

                # ---------------- DUPLICATES IN FILE ----------------
                key = name.lower()
                if key in seen_in_file:
                    duplicates.append({
                        "Row": row_no,
                        "PurposeOfVisit": name,
                        "Description": description,
                        "Reason": "Duplicate in uploaded file"
                    })
                    continue
                seen_in_file.add(key)

                # ---------------- EXISTING RECORDS ----------------
                existing = existing_map.get(key)
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({
                            "Row": row_no,
                            "PurposeOfVisit": name,
                            "Description": description,
                            "Reason": "Already exists in database"
                        })
                        continue
                    # Reactivate deleted record
                    existing.description = description
                    existing.is_deleted = False
                    existing.save()
                    imported_count += 1
                    continue

                # ---------------- PREPARE FOR BULK CREATE ----------------
                to_create.append(PurposeOfVisit(name=name, description=description, is_deleted=False))

            # ---------------- BULK CREATE ----------------
            if to_create:
                batch_size = 500
                for i in range(0, len(to_create), batch_size):
                    PurposeOfVisit.objects.bulk_create(to_create[i:i + batch_size])
                imported_count += len(to_create)

        except Exception as e:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": str(e)
            }, status=400)

        # ---------------- SUCCESS RESPONSE ----------------
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": list(reversed(duplicates)),
            "skipped_rows": list(reversed(skipped_rows))
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
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "No file uploaded"
            }, status=400)

        format_type = file.name.split(".")[-1].lower()
        required_headers = {"documents for"}
        optional_headers = {"description"}

        data = []
        duplicates = []
        skipped_rows = []
        to_create = []
        seen_in_file = set()
        imported_count = 0

        try:
            # ---------------- XLSX Handling ----------------
            if format_type == "xlsx":
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": "Please provide sheet_name",
                        "available_sheets": available_sheets
                    }, status=400)

                if sheet_name not in available_sheets:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'Sheet "{sheet_name}" not found',
                        "available_sheets": available_sheets
                    }, status=400)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'Sheet "{sheet_name}" is empty.'
                    }, status=400)

                headers = [str(c.value).strip().lower() if c.value else "" for c in next(ws.iter_rows(min_row=1, max_row=1))]
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

            # ---------------- CSV Handling ----------------
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
                            "message": f"Missing required headers. Required: {', '.join(required_headers)}. Found: {', '.join(row_lower.keys())}."
                        }, status=400)
                    data.append(row_lower)

            else:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Unsupported file format. Use .xlsx or .csv",
                }, status=400)

            # ---------------- EXISTING RECORDS ----------------
            existing_map = {p.name.lower(): p for p in DocumentsFor.objects.all()}

            # ---------------- PROCESS ROWS ----------------
            for row in reversed(data):
                row_no = row.get("_row_number", "Unknown")
                name_raw = row.get("documents for")
                name = str(name_raw).strip() if name_raw else None
                description_raw = row.get("description")
                description = str(description_raw).strip() if description_raw else ""

                row_skipped = {}

                # Missing name
                if not name:
                    row_skipped["Documents For"] = name_raw
                    row_skipped["Reason"] = "Missing documents for name"
                    skipped_rows.append({"Row": row_no, **row_skipped})
                    continue

                # Invalid name (non-alphabetic)
                if not isinstance(name, str) or not name.replace(" ", "").isalpha():
                    row_skipped["Documents For"] = name_raw
                    row_skipped["Reason"] = "Invalid Input: Documents For"
                    skipped_rows.append({"Row": row_no, **row_skipped})
                    continue

                # Invalid description
                if description_raw is not None and not isinstance(description_raw, (str, int, float, bool)):
                    row_skipped["Description"] = description_raw
                    row_skipped["Reason"] = "Invalid description data"
                    skipped_rows.append({"Row": row_no, **row_skipped})
                    continue

                # Duplicate in file
                key = name.lower()
                if key in seen_in_file:
                    duplicates.append({
                        "Row": row_no,
                        "Documents For": name,
                        "Description": description,
                        "Reason": "Duplicate in uploaded file"
                    })
                    continue
                seen_in_file.add(key)

                # Existing record in DB
                existing = existing_map.get(key)
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({
                            "Row": row_no,
                            "Documents For": name,
                            "Description": description,
                            "Reason": "Already exists in database"
                        })
                        continue
                    # Reactivate deleted record
                    existing.description = description
                    existing.is_deleted = False
                    existing.save()
                    imported_count += 1
                    continue

                # Prepare for bulk create
                to_create.append(DocumentsFor(name=name, description=description, is_deleted=False))

            # ---------------- BULK CREATE ----------------
            if to_create:
                batch_size = 500
                for i in range(0, len(to_create), batch_size):
                    DocumentsFor.objects.bulk_create(to_create[i:i + batch_size])
                imported_count += len(to_create)

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
            "duplicates": list(reversed(duplicates)),
            "skipped_rows": list(reversed(skipped_rows))
        }, status=200)



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
        ids = request.data.get('id', None)

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
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "No file uploaded"
            }, status=400)

        format_type = file.name.split(".")[-1].lower()

        required_headers = {
            "country",
            "visa main category",
            "visa major category",
            "visa name",
            "document category",
            "document name"
        }
        optional_headers = {"description"}

        data = []
        duplicates = []
        skipped_rows = []
        to_create = []
        seen_in_file = set()
        imported_count = 0

        try:
            # ---------------- XLSX Handling ----------------
            if format_type == "xlsx":
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": "Please provide sheet_name",
                        "available_sheets": available_sheets
                    }, status=400)

                if sheet_name not in available_sheets:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'Sheet "{sheet_name}" not found',
                        "available_sheets": available_sheets
                    }, status=400)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'Sheet "{sheet_name}" is empty.'
                    }, status=400)

                headers = [str(c.value).strip().lower() if c.value else '' for c in next(ws.iter_rows(min_row=1, max_row=1))]
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

            # ---------------- CSV Handling ----------------
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
                            "message": f"Missing required headers. Required: {', '.join(required_headers)}. Found: {', '.join(row_lower.keys())}."
                        }, status=400)
                    data.append(row_lower)

            else:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Unsupported file format. Use .xlsx or .csv",
                }, status=400)

            # ---------------- Helper: FK Lookup ----------------
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

            # ---------------- EXISTING RECORDS ----------------
            existing_map = {
                (r.country_id, r.visa_main_category_id, r.visa_major_category_id, r.visa_name_id,
                 r.document_category_id, r.document_name_id): r
                for r in RequiredDocument.objects.all()
            }

            # ---------------- PROCESS ROWS ----------------
            for row in reversed(data):
                row_number = row.get("_row_number", "Unknown")
                row_skipped = {}
                # Extract values
                country_val = row.get("country")
                visa_main_val = row.get("visa main category")
                visa_major_val = row.get("visa major category")
                visa_name_val = row.get("visa name")
                doc_cat_val = row.get("document category")
                doc_name_val = row.get("document name")
                description_val = row.get("description") or ""

                # FK lookups
                country_obj = get_fk_by_name(Country, country_val)
                visa_main_obj = get_fk_by_name(VisaMain, visa_main_val)
                visa_major_obj = get_fk_by_name(VisaMajor, visa_major_val)
                visa_name_obj = get_fk_by_name(VisaName, visa_name_val)
                doc_cat_obj = get_fk_by_name(DocumentCategory, doc_cat_val)
                doc_name_obj = get_fk_by_name(DocumentName, doc_name_val)

                # Check for missing references
                missing_refs = []
                if not country_obj: row_skipped["Country"] = country_val; missing_refs.append("Country")
                if not visa_main_obj: row_skipped["Visa Main Category"] = visa_main_val; missing_refs.append("Visa Main Category")
                if not visa_major_obj: row_skipped["Visa Major Category"] = visa_major_val; missing_refs.append("Visa Major Category")
                if not visa_name_obj: row_skipped["Visa Name"] = visa_name_val; missing_refs.append("Visa Name")
                if not doc_cat_obj: row_skipped["Document Category"] = doc_cat_val; missing_refs.append("Document Category")
                if not doc_name_obj: row_skipped["Document Name"] = doc_name_val; missing_refs.append("Document Name")

                if missing_refs:
                    row_skipped["Row"] = row_number
                    row_skipped["Reason"] = f"Invalid input: {', '.join(missing_refs)}"
                    skipped_rows.append(row_skipped)
                    continue

                # Duplicate check (by file order)
                key = (country_obj.id, visa_main_obj.id, visa_major_obj.id, visa_name_obj.id,
                       doc_cat_obj.id, doc_name_obj.id)
                if key in seen_in_file:
                    duplicates.append({
                        "Row": row_number,
                        "Country": country_val,
                        "Visa Main Category": visa_main_val,
                        "Visa Major Category": visa_major_val,
                        "Visa Name": visa_name_val,
                        "Document Category": doc_cat_val,
                        "Document Name": doc_name_val,
                        "Description": description_val,
                        "Reason": "Duplicate in uploaded file"
                    })
                    continue
                seen_in_file.add(key)

                # Existing DB check
                existing = existing_map.get(key)
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({
                            "Row": row_number,
                            "Country": country_val,
                            "Visa Main Category": visa_main_val,
                            "Visa Major Category": visa_major_val,
                            "Visa Name": visa_name_val,
                            "Document Category": doc_cat_val,
                            "Document Name": doc_name_val,
                            "Description": description_val,
                            "Reason": "Already exists in database"
                        })
                        continue
                    else:
                        existing.description = description_val
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                        continue

                # Prepare bulk create
                to_create.append(RequiredDocument(
                    country=country_obj,
                    visa_main_category=visa_main_obj,
                    visa_major_category=visa_major_obj,
                    visa_name=visa_name_obj,
                    document_category=doc_cat_obj,
                    document_name=doc_name_obj,
                    description=description_val,
                    is_deleted=False
                ))

            # ---------------- BULK CREATE ----------------
            if to_create:
                batch_size = 500
                for i in range(0, len(to_create), batch_size):
                    RequiredDocument.objects.bulk_create(to_create[i:i + batch_size])
                imported_count += len(to_create)

        except Exception as e:
            return Response({"statusCode": 400, "status": False, "message": str(e)}, status=400)

        # ---------------- FINAL RESPONSE ----------------
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": list(reversed(duplicates)),
            "skipped_rows": list(reversed(skipped_rows)),
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
        ids = request.data.get("id")

        # Filters
        country = request.GET.get("country")
        visa_main = request.GET.get("visa_main_category")

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

    EXPORT_HEADERS_ORDER = [
        "Country",
        "Visa Main Category",
        "Process Status",
        "Description"
    ]

    REQUIRED_HEADERS = {"country", "visa main category", "process status name"}
    OPTIONAL_HEADERS = {"description"}

    def post(self, request):
        file = request.FILES.get("file")
        sheet_name = request.data.get("sheet_name")

        if not file:
            return Response({"statusCode": 400, "status": False, "message": "No file uploaded"}, status=400)

        format_type = file.name.split(".")[-1].lower()
        data = []
        duplicates = []
        skipped_rows = []
        to_create = []
        seen_in_file = set()
        imported_count = 0

        try:
            # ---------------- XLSX ----------------
            if format_type == "xlsx":
                wb = openpyxl.load_workbook(file, read_only=True)
                sheets = wb.sheetnames

                if not sheet_name:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": "Please provide sheet_name",
                        "available_sheets": sheets
                    }, status=400)

                if sheet_name not in sheets:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'Sheet "{sheet_name}" not found in file',
                        "available_sheets": sheets
                    }, status=400)

                ws = wb[sheet_name]

                headers = [(cell.value or "").strip().lower() for cell in next(ws.iter_rows(min_row=1, max_row=1))]

                if not self.REQUIRED_HEADERS.issubset(headers):
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f"Missing required headers: {self.REQUIRED_HEADERS}, Found: {set(headers)}"
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
                    if not self.REQUIRED_HEADERS.issubset(row_lower.keys()):
                        return Response({
                            "statusCode": 400,
                            "status": False,
                            "message": f"Missing required headers: {self.REQUIRED_HEADERS}"
                        }, status=400)
                    data.append(row_lower)
            else:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "error": "Unsupported file format (.xlsx/.csv only)"
                }, status=400)

            # ---------------- Preload existing ----------------
            existing_map = {}
            for ps in ProcessStatusName.objects.select_related("country", "visa_main_category").all():
                key = f"{ps.country.id}_{ps.visa_main_category.id}_{ps.process_status_name.lower()}"
                existing_map[key] = ps

            # ---------------- Process rows in reversed order ----------------
            for row in reversed(data):
                row_number = row.get("_row_number")
                country_name = str(row.get("country") or "").strip()
                visa_main_name = str(row.get("visa main category") or "").strip()
                ps_name = str(row.get("process status name") or "").strip()
                description = str(row.get("description") or "").strip()

                wrong_values = []

                # Validate country
                country_obj = Country.objects.filter(name__iexact=country_name, is_deleted=False).first()
                if not country_obj:
                    wrong_values.append({"Country": country_name})

                # Validate visa main category
                visa_obj = VisaMain.objects.filter(name__iexact=visa_main_name, is_deleted=False).first()
                if not visa_obj:
                    wrong_values.append({"Visa Main Category": visa_main_name})

                # Validate process status
                if not ps_name:
                    wrong_values.append({"Process Status": ps_name})

                # If any validation failed
                if wrong_values:
                    skipped_rows.append({
                        "Row": row_number,
                        "Value": wrong_values,
                        "Reason": "Invalid or missing data"
                    })
                    continue

                # Duplicate in file
                key_in_file = f"{country_obj.id}_{visa_obj.id}_{ps_name.lower()}"
                if key_in_file in seen_in_file:
                    duplicates.append({
                        "Row": row_number,
                        "Process Status": ps_name,
                        "Description": description,
                        "Reason": "Duplicate in uploaded file"
                    })
                    continue
                seen_in_file.add(key_in_file)

                # Duplicate in DB
                existing = existing_map.get(key_in_file)
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({
                            "Row": row_number,
                            "Process Status": ps_name,
                            "Description": description,
                            "Reason": "Already exists in database"
                        })
                        continue
                    else:
                        existing.description = description
                        existing.is_deleted = False
                        existing.save()
                        imported_count += 1
                        continue

                # Prepare for bulk create
                to_create.append(ProcessStatusName(
                    country=country_obj,
                    visa_main_category=visa_obj,
                    process_status_name=ps_name,
                    description=description
                ))

            # ---------------- Bulk Create ----------------
            if to_create:
                batch_size = 500
                for i in range(0, len(to_create), batch_size):
                    ProcessStatusName.objects.bulk_create(to_create[i:i + batch_size])
                imported_count += len(to_create)

        except Exception as e:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": str(e)
            }, status=400)

        # ---------------- Final Response ----------------
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": list(reversed(duplicates)),
            "skipped_rows": list(reversed(skipped_rows))
        }, status=200)



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
        ids = request.data.get("id")

        # Filters
        country = request.GET.get("country")
        visa_main_category = request.GET.get("visa_main_category")
        process_status_name = request.GET.get("process_status_name")
        search = request.GET.get("search", "").strip()

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
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "No file uploaded"
            }, status=400)

        format_type = file.name.split(".")[-1].lower()
        required_headers = {
            "country",
            "visa main category",
            "process status name",
            "process sub status name"
        }
        optional_headers = {"description"}

        data = []
        duplicates = []
        skipped_rows = []
        to_create = []
        seen_in_file = set()
        imported_count = 0

        from master.models import Country, VisaMain, ProcessStatusName, ProcessSubStatusName

        try:
            # ---------------- XLSX Handling ----------------
            if format_type == "xlsx":
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": "Please provide sheet_name",
                        "available_sheets": available_sheets
                    }, status=400)

                if sheet_name not in available_sheets:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'Sheet "{sheet_name}" not found',
                        "available_sheets": available_sheets
                    }, status=400)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'Sheet "{sheet_name}" is empty.'
                    }, status=400)

                headers = [str(c.value).strip().lower() if c.value else "" for c in next(ws.iter_rows(min_row=1, max_row=1))]

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

            # ---------------- CSV Handling ----------------
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
                            "message": f"Missing required headers. Required: {', '.join(required_headers)}. Found: {', '.join(row_lower.keys())}."
                        }, status=400)
                    data.append(row_lower)

            else:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Unsupported file format. Use .xlsx or .csv",
                }, status=400)

            # ---------------- Helper FK ----------------
            def get_fk(model_class, value):
                if not value:
                    return None
                return model_class.objects.filter(name__iexact=str(value).strip(), is_deleted=False).first()

            # ---------------- Existing records ----------------
            existing_map = {}
            for r in ProcessSubStatusName.objects.all():
                key = (
                    r.country_id,
                    r.visa_main_category_id,
                    r.process_status_name_id,
                    r.process_sub_status_name.lower()
                )
                existing_map[key] = r

            # ---------------- Process Rows ----------------
            for row in reversed(data):
                row_num = row.get("_row_number", "Unknown")
                country_val = row.get("country")
                visa_main_val = row.get("visa main category")
                status_val = row.get("process status name")
                sub_status_val = row.get("process sub status name")
                description_val = str(row.get("description") or "").strip()

                row_skipped = {}

                # Validate each FK
                country_obj = get_fk(Country, country_val)
                visa_main_obj = get_fk(VisaMain, visa_main_val)
                process_status_obj = None
                if country_obj and visa_main_obj:
                    process_status_obj = ProcessStatusName.objects.filter(
                        country=country_obj,
                        visa_main_category=visa_main_obj,
                        process_status_name__iexact=status_val,
                        is_deleted=False
                    ).first()

                # Collect skipped reasons
                if not country_obj: row_skipped["Country"] = country_val
                if not visa_main_obj: row_skipped["Visa Main Category"] = visa_main_val
                if not process_status_obj: row_skipped["Process Status Name"] = status_val
                if not sub_status_val: row_skipped["Process Sub Status Name"] = sub_status_val

                if row_skipped:
                    row_skipped["Row"] = row_num
                    row_skipped["Reason"] = f"Invalid input: {', '.join(row_skipped.keys())}"
                    skipped_rows.append(row_skipped)
                    continue

                # Check duplicates in file
                key_in_file = (
                    country_obj.id,
                    visa_main_obj.id,
                    process_status_obj.id,
                    sub_status_val.lower()
                )
                if key_in_file in seen_in_file:
                    duplicates.append({
                        "Row": row_num,
                        "Country": country_val,
                        "Visa Main Category": visa_main_val,
                        "Process Status Name": status_val,
                        "Process Sub Status Name": sub_status_val,
                        "Description": description_val,
                        "Reason": "Duplicate in uploaded file"
                    })
                    continue
                seen_in_file.add(key_in_file)

                # Check duplicates in DB
                existing = existing_map.get(key_in_file)
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({
                            "Row": row_num,
                            "Country": country_val,
                            "Visa Main Category": visa_main_val,
                            "Process Status Name": status_val,
                            "Process Sub Status Name": sub_status_val,
                            "Description": description_val,
                            "Reason": "Already exists in database"
                        })
                        continue
                    # Reactivate deleted
                    existing.description = description_val
                    existing.is_deleted = False
                    existing.save()
                    imported_count += 1
                    continue

                # Prepare bulk create
                to_create.append(ProcessSubStatusName(
                    country=country_obj,
                    visa_main_category=visa_main_obj,
                    process_status_name=process_status_obj,
                    process_sub_status_name=sub_status_val,
                    description=description_val,
                    is_deleted=False
                ))

            # ---------------- Bulk Create ----------------
            if to_create:
                batch_size = 500
                for i in range(0, len(to_create), batch_size):
                    ProcessSubStatusName.objects.bulk_create(to_create[i:i + batch_size])
                imported_count += len(to_create)

        except Exception as e:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": str(e)
            }, status=400)

        # ---------------- SUCCESS RESPONSE ----------------
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": list(reversed(duplicates)),
            "skipped_rows": list(reversed(skipped_rows))
        }, status=200)


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
        ids = request.data.get("id")

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
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "No file uploaded"
            }, status=400)

        format_type = file.name.split(".")[-1].lower()
        required_headers = {"process type"}
        optional_headers = {"description"}

        data = []
        duplicates = []
        skipped_rows = []
        to_create = []
        seen_in_file = set()

        try:
            # ---------------- XLSX Handling ----------------
            if format_type == "xlsx":
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": "Please provide sheet_name",
                        "available_sheets": available_sheets
                    }, status=400)

                if sheet_name not in available_sheets:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'Sheet "{sheet_name}" not found',
                        "available_sheets": available_sheets
                    }, status=400)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'Sheet "{sheet_name}" is empty.'
                    }, status=400)

                headers = [str(c.value).strip().lower() if c.value else "" for c in next(ws.iter_rows(min_row=1, max_row=1))]
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

            # ---------------- CSV Handling ----------------
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
                            "message": f"Missing required headers. Required: {', '.join(required_headers)}. Found: {', '.join(row_lower.keys())}."
                        }, status=400)
                    data.append(row_lower)

            else:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Unsupported file format. Use .xlsx or .csv",
                }, status=400)

            # ---------------- Preload existing records ----------------
            existing_map = {pt.name.lower(): pt for pt in ProcessType.objects.all()}
            imported_count = 0

            # ---------------- Process Rows ----------------
            for row in reversed(data):
                row_no = row.get("_row_number", "Unknown")
                name = str(row.get("process type") or "").strip()
                description = str(row.get("description") or "").strip()

                if not name:
                    skipped_rows.append({
                        "Row": row_no,
                        "Process Type": name,
                        "Description": description or "",
                        "Reason": "Missing Process Type"
                    })
                    continue

                key = name.lower()

                # Duplicate in file
                if key in seen_in_file:
                    duplicates.append({
                        "Row": row_no,
                        "Process Type": name,
                        "Description": description or "",
                        "Reason": "Duplicate in uploaded file"
                    })
                    continue
                seen_in_file.add(key)

                existing = existing_map.get(key)
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({
                            "Row": row_no,
                            "Process Type": name,
                            "Description": description or "",
                            "Reason": "Already exists in database"
                        })
                        continue

                    # Reactivate deleted record
                    existing.description = description
                    existing.is_deleted = False
                    existing.save()
                    imported_count += 1
                    continue

                # Prepare for bulk create
                to_create.append(ProcessType(name=name, description=description, is_deleted=False))

            # ---------------- Bulk Create ----------------
            if to_create:
                batch_size = 500
                for i in range(0, len(to_create), batch_size):
                    ProcessType.objects.bulk_create(to_create[i:i + batch_size])
                imported_count += len(to_create)

        except Exception as e:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": str(e)
            }, status=400)

        # ---------------- SUCCESS RESPONSE -----------------
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": list(reversed(duplicates)),
            "skipped_rows": list(reversed(skipped_rows))
        }, status=200)


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
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "No file uploaded"
            }, status=400)

        format_type = file.name.split('.')[-1].lower()
        required_headers = {"payment to"}
        optional_headers = {"description"}

        data = []
        duplicates = []
        skipped_rows = []
        to_create = []
        seen_in_file = set()
        imported_count = 0

        try:
            # ---------------- XLSX Handling ----------------
            if format_type == "xlsx":
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": "Please provide sheet_name",
                        "available_sheets": available_sheets,
                    }, status=400)

                if sheet_name not in available_sheets:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'Sheet "{sheet_name}" not found',
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

            # ---------------- CSV Handling ----------------
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

            # ---------------- Process Rows ----------------
            from master.models import PaymentTo

            # Preload existing DB records
            existing_map = {p.name.lower(): p for p in PaymentTo.objects.all()}

            for row in reversed(data):
                row_no = row.get("_row_number", "Unknown")
                raw_name = row.get("payment to")
                description = str(row.get("description") or "").strip()

                # Validate required field
                if not raw_name or not isinstance(raw_name, str) or not raw_name.strip():
                    skipped_rows.append({
                        "Row": row_no,
                        "Payment To": raw_name,
                        "Description": description,
                        "Reason": "Missing or invalid Payment To name"
                    })
                    continue

                name = raw_name.strip()
                key = name.lower()

                # Check duplicate in file
                if key in seen_in_file:
                    duplicates.append({
                        "Row": row_no,
                        "Payment To": name,
                        "Description": description,
                        "Reason": "Duplicate in uploaded file"
                    })
                    continue
                seen_in_file.add(key)

                # Check existing in DB
                existing = existing_map.get(key)
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({
                            "Row": row_no,
                            "Payment To": name,
                            "Description": description,
                            "Reason": "Already exists in database"
                        })
                        continue
                    # Reactivate soft-deleted
                    existing.description = description
                    existing.is_deleted = False
                    existing.save()
                    imported_count += 1
                    continue

                # Prepare for bulk create
                to_create.append(PaymentTo(
                    name=name,
                    description=description,
                    is_deleted=False
                ))

            # Bulk create
            if to_create:
                batch_size = 500
                for i in range(0, len(to_create), batch_size):
                    PaymentTo.objects.bulk_create(to_create[i:i + batch_size])
                imported_count += len(to_create)

        except Exception as e:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": str(e),
            }, status=400)

        # ---------------- SUCCESS RESPONSE -----------------
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": list(reversed(duplicates)),
            "skipped_rows": list(reversed(skipped_rows))
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
        ids = request.data.get("id")

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
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "No file uploaded"
            }, status=400)

        format_type = file.name.split(".")[-1].lower()
        required_headers = {"payment to", "payment category"}
        optional_headers = {"description"}

        data = []
        duplicates = []
        skipped_rows = []
        to_create = []
        seen_in_file = set()
        imported_count = 0

        try:
            # ---------------- XLSX Handling ----------------
            if format_type == "xlsx":
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": "Please provide sheet_name",
                        "available_sheets": available_sheets,
                    }, status=400)

                if sheet_name not in available_sheets:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'Sheet "{sheet_name}" not found',
                        "available_sheets": available_sheets,
                    }, status=400)

                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    return Response({
                        "statusCode": 400,
                        "status": False,
                        "message": f'Sheet "{sheet_name}" is empty.'
                    }, status=400)

                headers = [str(c.value).strip().lower() if c.value else "" for c in next(ws.iter_rows(min_row=1, max_row=1))]
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

            # ---------------- CSV Handling ----------------
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
                            "message": f"Missing required headers. Required: {', '.join(required_headers)}. Found: {', '.join(row_lower.keys())}."
                        }, status=400)
                    data.append(row_lower)
            else:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Unsupported file format. Use .xlsx or .csv",
                }, status=400)

            # ---------------- Process Rows ----------------
            from master.models import PaymentTo, PaymentCategory

            # Preload PaymentTo and PaymentCategory
            payment_to_map = {p.name.lower(): p for p in PaymentTo.objects.filter(is_deleted=False)}
            existing_map = {}  # {(payment_to_id, category.lower()): obj}
            for pc in PaymentCategory.objects.all():
                key = (pc.payment_to_id, pc.payment_category.lower())
                existing_map[key] = pc

            for row in reversed(data):
                row_no = row.get("_row_number", "Unknown")
                row_skipped = {}
                payment_to_name = str(row.get("payment to") or "").strip()
                category_name = str(row.get("payment category") or "").strip()
                description = str(row.get("description") or "").strip()

                # Validate Payment To
                if not payment_to_name:
                    row_skipped["Payment To"] = payment_to_name
                    row_skipped["Reason"] = "Missing Payment To"

                elif payment_to_name.lower() not in payment_to_map:
                    row_skipped["Payment To"] = payment_to_name
                    row_skipped["Reason"] = f'Payment To "{payment_to_name}" not found'

                # Validate Payment Category
                if not category_name:
                    row_skipped["Payment Category"] = category_name
                    row_skipped["Reason"] = "Missing Payment Category"

                # Add to skipped_rows if any error
                if row_skipped:
                    row_skipped["Row"] = row_no
                    row_skipped["Description"] = description
                    skipped_rows.append(row_skipped)
                    continue

                payment_to_obj = payment_to_map[payment_to_name.lower()]
                key = (payment_to_obj.id, category_name.lower())
                existing = existing_map.get(key)

                # Check duplicates in file
                file_key = (payment_to_obj.id, category_name.lower())
                if file_key in seen_in_file:
                    duplicates.append({
                        "Row": row_no,
                        "Payment To": payment_to_name,
                        "Payment Category": category_name,
                        "Description": description,
                        "Reason": "Duplicate in uploaded file"
                    })
                    continue
                seen_in_file.add(file_key)

                # Check existing in DB
                if existing:
                    if not existing.is_deleted:
                        duplicates.append({
                            "Row": row_no,
                            "Payment To": payment_to_name,
                            "Payment Category": category_name,
                            "Description": description,
                            "Reason": "Already exists in database"
                        })
                        continue
                    # Reactivate soft-deleted
                    existing.description = description
                    existing.is_deleted = False
                    existing.save()
                    imported_count += 1
                    continue

                # Prepare for bulk create
                to_create.append(PaymentCategory(
                    payment_to=payment_to_obj,
                    payment_category=category_name,
                    description=description,
                    is_deleted=False
                ))

            # Bulk create
            if to_create:
                batch_size = 500
                for i in range(0, len(to_create), batch_size):
                    PaymentCategory.objects.bulk_create(to_create[i:i + batch_size])
                imported_count += len(to_create)

        except Exception as e:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": str(e),
            }, status=400)

        # ---------------- SUCCESS RESPONSE -----------------
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f'Sheet "{sheet_name}" imported successfully' if sheet_name else "Import successful",
            "imported_count": imported_count,
            "duplicates": list(reversed(duplicates)),
            "skipped_rows": list(reversed(skipped_rows)),
        }, status=200)


