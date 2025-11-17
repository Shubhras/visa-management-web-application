from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Q
from django.http import HttpResponse
from tablib import Dataset
from tablib.formats import registry
import openpyxl, datetime
from uuid import UUID
import io, csv, datetime, uuid, openpyxl
from .models import *
from .serializers import *
from django.utils import timezone
from .pagination import *
CSV = registry.get_format('csv')
XLSX = registry.get_format('xlsx')


# ------------------ LIST ------------------
class RepresentingCountryListAPIView(APIView):
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['country__name', 'continent', 'created_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = RepresentingCountry.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(country__name__istartswith=search) |
                Q(continent__istartswith=search) |
                Q(full_name__istartswith=search) |
                Q(short_name__istartswith=search)
            )

        queryset = queryset.order_by(sort_by)

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = RepresentingCountrySerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


# ------------------ CREATE ------------------
class RepresentingCountryCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        serializer = RepresentingCountrySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Representing Country created successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            "statusCode": 400,
            "status": False,
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


# ------------------ RETRIEVE ------------------
class RepresentingCountryRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            country = RepresentingCountry.objects.get(uuid=uuid, is_deleted=False)
        except RepresentingCountry.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Representing Country not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = RepresentingCountrySerializer(country)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Representing Country retrieved successfully",
            "data": serializer.data
        })


# ------------------ UPDATE ------------------
class RepresentingCountryUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            country = RepresentingCountry.objects.get(uuid=uuid, is_deleted=False)
        except RepresentingCountry.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Representing Country not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = RepresentingCountrySerializer(country, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Representing Country updated successfully",
                "data": serializer.data
            })
        return Response({
            "statusCode": 400,
            "status": False,
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


# ------------------ DELETE ------------------
class RepresentingCountryDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        ids = request.data.get('id', None)
        if not ids:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide 'id' field (UUID list or 'all')."
            }, status=status.HTTP_400_BAD_REQUEST)

        if ids == "all":
            countries = RepresentingCountry.objects.filter(is_deleted=False)
            count = countries.count()
            countries.update(is_deleted=True)
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} country records deleted successfully."
            })

        if not isinstance(ids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Provide list of UUIDs or 'all'."
            }, status=status.HTTP_400_BAD_REQUEST)

        valid_uuids, invalid_uuids = [], []
        for u in ids:
            try:
                valid_uuids.append(UUID(u))
            except ValueError:
                invalid_uuids.append(u)

        countries = RepresentingCountry.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = countries.count()
        countries.update(is_deleted=True)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} country record(s) deleted successfully.",
            "data": {"invalid_uuids": invalid_uuids}
        })


# ------------------ EXPORT ------------------
class RepresentingCountryExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'xlsx').lower()
        fields = request.GET.get('fields')  # comma-separated fields
        uuids_param = request.GET.get('uuids', '')  # comma-separated UUIDs
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        # --- Field to header mapping ---
        field_header_map = {
            'uuid': 'UUID',
            'country': 'Country Name',
            'continent': 'Continent',
            'short_name': 'Short Name',
            'full_name': 'Full Name',
            'official_name': 'Official Name',
            'capital_city': 'Capital City',
            'population': 'Population',
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

        queryset = RepresentingCountry.objects.filter(is_deleted=False)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        queryset = queryset.order_by('-created_at')

        dataset = Dataset()
        dataset.headers = [field_header_map.get(f, f) for f in field_list]
        dataset.title = 'Representing Countries'

        for obj in queryset:
            row = []
            for field in field_list:
                value = getattr(obj, field, '')
                if field == 'continent' and obj.continent:
                    value = obj.continent
                elif isinstance(value, datetime.datetime):
                    value = timezone.localtime(value).strftime("%d-%m-%Y %I:%M:%S %p")
                elif isinstance(value, bool):
                    value = int(value)
                row.append(value if value is not None else '')
            dataset.append(row)

        if format_type == 'csv':
            file_data = dataset.export('csv')
            content_type = 'text/csv; charset=utf-8'
            file_name = 'representing_countries.csv'
        else:
            file_data = io.BytesIO(dataset.export('xlsx'))
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'representing_countries.xlsx'

        response = HttpResponse(
            file_data if format_type == 'csv' else file_data.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


# ------------------ IMPORT ------------------
class RepresentingCountryImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')
        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        duplicate_names = []
        skipped_rows = []

        required_headers = {'full name', 'continent'}
        optional_headers = {'short name', 'official name', 'capital city', 'population', 'status'}

        try:
            data = []
            headers = []

            if format_type == 'xlsx':
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
                full_name = str(row.get('full name')).strip() if row.get('full name') else None
                if not full_name:
                    skipped_rows.append({"Full Name": "Unknown", "Reason": "Missing required field: full name"})
                    continue

                continent_name = str(row.get('continent')).strip() if row.get('continent') else ''
                continent_obj = None
                if continent_name:
                    continent_obj = Continents.objects.filter(name__iexact=continent_name).first()
                    if not continent_obj:
                        skipped_rows.append({"Full Name": full_name, "Continent": continent_name, "Reason": "Invalid continent name"})
                        continue

                existing = RepresentingCountry.objects.filter(full_name__iexact=full_name).first()
                if existing:
                    if not existing.is_deleted:
                        duplicate_names.append(full_name)
                        continue
                    existing.is_deleted = False
                    existing.continent = continent_name
                    existing.save()
                    imported_count += 1
                else:
                    RepresentingCountry.objects.create(
                        full_name=full_name,
                        continent=continent_name,
                        short_name=row.get('short name', ''),
                        official_name=row.get('official name', ''),
                        capital_city=row.get('capital city', ''),
                        population=row.get('population', ''),
                        status=row.get('status', ''),
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





# ------------------ VisaMain ------------------
class VisaMainListAPIView(APIView):
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')

        allowed_sort_fields = ['name', 'created_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = VisaMain.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(Q(name__istartswith=search))

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = VisaMainSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


# ------------------ CREATE ------------------
class VisaMainCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        name = request.data.get('name', '').strip()
        if VisaMain.objects.filter(name__iexact=name, is_deleted=False).exists():
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "VisaMain with this name already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = VisaMainSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "VisaMain created successfully.",
                "data": serializer.data
            })
        return Response({"statusCode": 400, "status": False, "message": serializer.errors}, status=400)


# ------------------ RETRIEVE ------------------
class VisaMainRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = VisaMain.objects.get(uuid=uuid, is_deleted=False)
        except VisaMain.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "VisaMain not found"}, status=404)

        serializer = VisaMainSerializer(obj)
        return Response({"statusCode": 200, "status": True, "message": "Retrieved successfully", "data": serializer.data})


# ------------------ UPDATE ------------------
class VisaMainUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = VisaMain.objects.get(uuid=uuid, is_deleted=False)
        except VisaMain.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "VisaMain not found"}, status=404)

        serializer = VisaMainSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"statusCode": 200, "status": True, "message": "Updated successfully", "data": serializer.data})
        return Response({"statusCode": 400, "status": False, "message": serializer.errors}, status=400)


# ------------------ DELETE ------------------
class VisaMainDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        ids = request.data.get('id')
        if not ids:
            return Response({"statusCode": 400, "status": False, "message": "Provide 'id' field (list of UUIDs or 'all')."}, status=400)

        if ids == "all":
            objs = VisaMain.objects.filter(is_deleted=False)
            count = objs.count()
            objs.update(is_deleted=True)
            return Response({"statusCode": 200, "status": True, "message": f"All {count} VisaMain(s) deleted."})

        if not isinstance(ids, list):
            return Response({"statusCode": 400, "status": False, "message": "Provide a list of UUIDs."}, status=400)

        valid_uuids, invalid_uuids = [], []
        for u in ids:
            try:
                valid_uuids.append(UUID(u))
            except ValueError:
                invalid_uuids.append(u)

        objs = VisaMain.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = objs.count()
        objs.update(is_deleted=True)

        return Response({"statusCode": 200, "status": True, "message": f"{count} VisaMain(s) deleted.", "data": {"invalid_uuids": invalid_uuids}})


# ------------------ EXPORT ------------------
class VisaMainExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'csv').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]
        field_list = [f.strip() for f in fields.split(',')] if fields else ['uuid', 'name', 'description', 'is_deleted', 'created_at', 'updated_at']

        queryset = VisaMain.objects.filter(uuid__in=uuids) if uuids else VisaMain.objects.all()
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
            filename = 'visamain.xlsx'
        else:
            data = CSV().export_data(dataset)
            content_type = 'text/csv; charset=utf-8'
            filename = 'visamain.csv'

        response = HttpResponse(data, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


# ------------------ IMPORT ------------------
class VisaMainImportAPIView(APIView):
    
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file uploaded'}, status=400)

        format_type = file.name.split('.')[-1].lower()
        dataset = Dataset()
        duplicate_names = []

        try:
            if format_type == 'xlsx':
                wb = openpyxl.load_workbook(file, read_only=True)
                sheet_name = request.data.get('sheet_name')
                if not sheet_name or sheet_name not in wb.sheetnames:
                    return Response({'error': 'Invalid sheet_name', 'available_sheets': wb.sheetnames}, status=400)
                ws = wb[sheet_name]
                headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                data = [dict(zip(headers, row)) for row in ws.iter_rows(min_row=2, values_only=True)]
            elif format_type == 'csv':
                dataset.load(file.read().decode('utf-8'), format='csv')
                data = dataset.dict
            else:
                return Response({'error': 'Unsupported file format'}, status=400)

            for row in reversed(data):
                name = str(row.get('name')).strip() if row.get('name') else None
                description = str(row.get('description')).strip() if row.get('description') else ''
                if not name:
                    continue
                existing = VisaMain.objects.filter(name__iexact=name).first()
                if existing:
                    if existing.is_deleted:
                        VisaMain.objects.create(name=name, description=description, is_deleted=False)
                    else:
                        duplicate_names.append(name)
                        continue
                else:
                    VisaMain.objects.create(name=name, description=description, is_deleted=False)

        except Exception as e:
            return Response({'error': str(e)}, status=400)

        return Response({"statusCode": 200, "status": True, "duplicates": list(set(duplicate_names)), "message": "Import successful"})
    



#--------------------visamajor-----------------
class VisaMajorListAPIView(APIView):
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')
        allowed_sort_fields = ['name', 'created_at']

        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = VisaMajor.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(Q(name__istartswith=search))

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = VisaMajorSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


# ------------------ CREATE ------------------
class VisaMajorCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        visamain_id = request.data.get('visamain')
        name = request.data.get('name', '').strip()

        if not visamain_id:
            return Response({"statusCode": 400, "status": False, "message": "visamain is required"}, status=400)

        if VisaMajor.objects.filter(visamain_id=visamain_id, name__iexact=name, is_deleted=False).exists():
            return Response({"statusCode": 400, "status": False, "message": "VisaMajor with this name already exists for this VisaMain"}, status=400)

        serializer = VisaMajorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"statusCode": 200, "status": True, "message": "VisaMajor created successfully", "data": serializer.data})
        return Response({"statusCode": 400, "status": False, "message": serializer.errors}, status=400)


# ------------------ RETRIEVE ------------------
class VisaMajorRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = VisaMajor.objects.get(uuid=uuid, is_deleted=False)
        except VisaMajor.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "VisaMajor not found"}, status=404)

        serializer = VisaMajorSerializer(obj)
        return Response({"statusCode": 200, "status": True, "message": "Retrieved successfully", "data": serializer.data})


# ------------------ UPDATE ------------------
class VisaMajorUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = VisaMajor.objects.get(uuid=uuid, is_deleted=False)
        except VisaMajor.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "VisaMajor not found"}, status=404)

        visamain_id = request.data.get('visamain')
        name = request.data.get('name', '').strip()

        if VisaMajor.objects.filter(visamain_id=visamain_id, name__iexact=name, is_deleted=False).exclude(uuid=uuid).exists():
            return Response({"statusCode": 400, "status": False, "message": "VisaMajor with this name already exists for this VisaMain"}, status=400)

        serializer = VisaMajorSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"statusCode": 200, "status": True, "message": "Updated successfully", "data": serializer.data})
        return Response({"statusCode": 400, "status": False, "message": serializer.errors}, status=400)


# ------------------ DELETE ------------------
class VisaMajorDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        ids = request.data.get('id')
        if not ids:
            return Response({"statusCode": 400, "status": False, "message": "Provide 'id' field (list of UUIDs or 'all')."}, status=400)

        if ids == "all":
            objs = VisaMajor.objects.filter(is_deleted=False)
            count = objs.count()
            objs.update(is_deleted=True)
            return Response({"statusCode": 200, "status": True, "message": f"All {count} VisaMajor(s) deleted."})

        if not isinstance(ids, list):
            return Response({"statusCode": 400, "status": False, "message": "Provide a list of UUIDs."}, status=400)

        valid_uuids, invalid_uuids = [], []
        for u in ids:
            try:
                valid_uuids.append(UUID(u))
            except ValueError:
                invalid_uuids.append(u)

        objs = VisaMajor.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = objs.count()
        objs.update(is_deleted=True)

        return Response({"statusCode": 200, "status": True, "message": f"{count} VisaMajor(s) deleted.", "data": {"invalid_uuids": invalid_uuids}})


# ------------------ EXPORT ------------------
class VisaMajorExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'csv').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]
        field_list = [f.strip() for f in fields.split(',')] if fields else ['uuid', 'visamain', 'visamain_name', 'name', 'description', 'is_deleted', 'created_at', 'updated_at']

        queryset = VisaMajor.objects.filter(uuid__in=uuids) if uuids else VisaMajor.objects.all()
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
            filename = 'visamajor.xlsx'
        else:
            data = CSV().export_data(dataset)
            content_type = 'text/csv; charset=utf-8'
            filename = 'visamajor.csv'

        response = HttpResponse(data, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


# ------------------ IMPORT ------------------
class VisaMajorImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file uploaded'}, status=400)

        format_type = file.name.split('.')[-1].lower()
        dataset = Dataset()
        duplicate_names = []

        try:
            if format_type == 'xlsx':
                wb = openpyxl.load_workbook(file, read_only=True)
                sheet_name = request.data.get('sheet_name')
                if not sheet_name or sheet_name not in wb.sheetnames:
                    return Response({'error': 'Invalid sheet_name', 'available_sheets': wb.sheetnames}, status=400)
                ws = wb[sheet_name]
                headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                data = [dict(zip(headers, row)) for row in ws.iter_rows(min_row=2, values_only=True)]
            elif format_type == 'csv':
                dataset.load(file.read().decode('utf-8'), format='csv')
                data = dataset.dict
            else:
                return Response({'error': 'Unsupported file format'}, status=400)

            for row in reversed(data):
                visamain_id = row.get('visamain')
                name = str(row.get('name')).strip() if row.get('name') else ''
                description = str(row.get('description')).strip() if row.get('description') else ''
                if not visamain_id or not name:
                    continue
                existing = VisaMajor.objects.filter(visamain_id=visamain_id, name__iexact=name).first()
                if existing:
                    if existing.is_deleted:
                        VisaMajor.objects.create(visamain_id=visamain_id, name=name, description=description, is_deleted=False)
                    else:
                        duplicate_names.append(name)
                        continue
                else:
                    VisaMajor.objects.create(visamain_id=visamain_id, name=name, description=description, is_deleted=False)
        except Exception as e:
            return Response({'error': str(e)}, status=400)

        return Response({"statusCode": 200, "status": True, "duplicates": list(set(duplicate_names)), "message": "Import successful"})



#-------------------------VisaName----------------
class VisaNameListAPIView(APIView):
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')
        allowed_sort_fields = ['full_name', 'created_at']

        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = VisaName.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(
                Q(full_name__istartswith=search) |
                Q(short_name__istartswith=search) |
                Q(description__istartswith=search)
            )

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = VisaNameSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


# ------------------ CREATE ------------------
class VisaNameCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        serializer = VisaNameSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "VisaName created successfully",
                "data": serializer.data
            }, status=200)

        return Response({
            "statusCode": 400,
            "status": False,
            "message": serializer.errors
        }, status=400)


# ------------------ RETRIEVE ------------------
class VisaNameRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = VisaName.objects.get(uuid=uuid, is_deleted=False)
        except VisaName.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "VisaName not found"}, status=404)

        serializer = VisaNameSerializer(obj)
        return Response({"statusCode": 200, "status": True, "message": "Retrieved successfully", "data": serializer.data})


# ------------------ UPDATE ------------------
class VisaNameUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = VisaName.objects.get(uuid=uuid, is_deleted=False)
        except VisaName.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "VisaName not found"}, status=404)

        country_id = request.data.get('country')
        visamain_id = request.data.get('visamain')
        visamajor_id = request.data.get('visamajor')
        full_name = request.data.get('full_name', '').strip()

        if VisaName.objects.filter(
            country_id=country_id,
            visamain_id=visamain_id,
            visamajor_id=visamajor_id,
            full_name__iexact=full_name,
            is_deleted=False
        ).exclude(uuid=uuid).exists():
            return Response({"statusCode": 400, "status": False, "message": "VisaName with this combination already exists"}, status=400)

        serializer = VisaNameSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"statusCode": 200, "status": True, "message": "Updated successfully", "data": serializer.data})
        return Response({"statusCode": 400, "status": False, "message": serializer.errors}, status=400)


# ------------------ DELETE ------------------
class VisaNameDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        ids = request.data.get('id')
        if not ids:
            return Response({"statusCode": 400, "status": False, "message": "Provide 'id' field (list of UUIDs or 'all')."}, status=400)

        if ids == "all":
            objs = VisaName.objects.filter(is_deleted=False)
            count = objs.count()
            objs.update(is_deleted=True)
            return Response({"statusCode": 200, "status": True, "message": f"All {count} VisaName(s) deleted."})

        if not isinstance(ids, list):
            return Response({"statusCode": 400, "status": False, "message": "Provide a list of UUIDs."}, status=400)

        valid_uuids, invalid_uuids = [], []
        for u in ids:
            try:
                valid_uuids.append(UUID(u))
            except ValueError:
                invalid_uuids.append(u)

        objs = VisaName.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = objs.count()
        objs.update(is_deleted=True)

        return Response({"statusCode": 200, "status": True, "message": f"{count} VisaName(s) deleted.", "data": {"invalid_uuids": invalid_uuids}})


# ------------------ EXPORT ------------------
class VisaNameExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'csv').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]
        field_list = [f.strip() for f in fields.split(',')] if fields else [
            'uuid', 'country', 'country_name', 'visamain', 'visamain_name',
            'visamajor', 'visamajor_name', 'full_name', 'short_name', 'description', 'is_deleted', 'created_at', 'updated_at'
        ]

        queryset = VisaName.objects.filter(uuid__in=uuids) if uuids else VisaName.objects.all()
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
            filename = 'visaname.xlsx'
        else:
            data = CSV().export_data(dataset)
            content_type = 'text/csv; charset=utf-8'
            filename = 'visaname.csv'

        response = HttpResponse(data, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


# ------------------ IMPORT ------------------
class VisaNameImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file uploaded'}, status=400)

        format_type = file.name.split('.')[-1].lower()
        dataset = Dataset()
        duplicate_names = []

        try:
            if format_type == 'xlsx':
                wb = openpyxl.load_workbook(file, read_only=True)
                sheet_name = request.data.get('sheet_name')
                if not sheet_name or sheet_name not in wb.sheetnames:
                    return Response({'error': 'Invalid sheet_name', 'available_sheets': wb.sheetnames}, status=400)
                ws = wb[sheet_name]
                headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                data = [dict(zip(headers, row)) for row in ws.iter_rows(min_row=2, values_only=True)]
            elif format_type == 'csv':
                dataset.load(file.read().decode('utf-8'), format='csv')
                data = dataset.dict
            else:
                return Response({'error': 'Unsupported file format'}, status=400)

            for row in reversed(data):
                country_id = row.get('country')
                visamain_id = row.get('visamain')
                visamajor_id = row.get('visamajor')
                full_name = str(row.get('full_name')).strip() if row.get('full_name') else ''
                short_name = str(row.get('short_name')).strip() if row.get('short_name') else ''
                description = str(row.get('description')).strip() if row.get('description') else ''

                if not all([country_id, visamain_id, visamajor_id, full_name]):
                    continue

                existing = VisaName.objects.filter(
                    country_id=country_id,
                    visamain_id=visamain_id,
                    visamajor_id=visamajor_id,
                    full_name__iexact=full_name
                ).first()

                if existing:
                    if existing.is_deleted:
                        VisaName.objects.create(
                            country_id=country_id, visamain_id=visamain_id,
                            visamajor_id=visamajor_id, full_name=full_name,
                            short_name=short_name, description=description, is_deleted=False
                        )
                    else:
                        duplicate_names.append(full_name)
                        continue
                else:
                    VisaName.objects.create(
                        country_id=country_id, visamain_id=visamain_id,
                        visamajor_id=visamajor_id, full_name=full_name,
                        short_name=short_name, description=description, is_deleted=False
                    )
        except Exception as e:
            return Response({'error': str(e)}, status=400)

        return Response({"statusCode": 200, "status": True, "duplicates": list(set(duplicate_names)), "message": "Import successful"})
    




#----------------applicantType--------------------
class ApplicantTypeListAPIView(APIView):
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'desc')
        allowed_sort_fields = ['name', 'created_at']

        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'

        queryset = ApplicantType.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(
                Q(name__istartswith=search)
            )

        queryset = queryset.order_by(sort_by)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = ApplicantTypeSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


# ------------------ CREATE ------------------
class ApplicantTypeCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        name = request.data.get('name', '').strip()
        if not name:
            return Response({"statusCode": 400, "status": False, "message": "Name is required"}, status=400)

        if ApplicantType.objects.filter(name__iexact=name, is_deleted=False).exists():
            return Response({"statusCode": 400, "status": False, "message": "ApplicantType with this name already exists"}, status=400)

        serializer = ApplicantTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"statusCode": 200, "status": True, "message": "ApplicantType created successfully", "data": serializer.data})
        return Response({"statusCode": 400, "status": False, "message": serializer.errors}, status=400)


# ------------------ RETRIEVE ------------------
class ApplicantTypeRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = ApplicantType.objects.get(uuid=uuid, is_deleted=False)
        except ApplicantType.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "ApplicantType not found"}, status=404)

        serializer = ApplicantTypeSerializer(obj)
        return Response({"statusCode": 200, "status": True, "message": "Retrieved successfully", "data": serializer.data})


# ------------------ UPDATE ------------------
class ApplicantTypeUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = ApplicantType.objects.get(uuid=uuid, is_deleted=False)
        except ApplicantType.DoesNotExist:
            return Response({"statusCode": 404, "status": False, "message": "ApplicantType not found"}, status=404)

        name = request.data.get('name', '').strip()
        if ApplicantType.objects.filter(name__iexact=name, is_deleted=False).exclude(uuid=uuid).exists():
            return Response({"statusCode": 400, "status": False, "message": "ApplicantType with this name already exists"}, status=400)

        serializer = ApplicantTypeSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"statusCode": 200, "status": True, "message": "Updated successfully", "data": serializer.data})
        return Response({"statusCode": 400, "status": False, "message": serializer.errors}, status=400)


# ------------------ DELETE ------------------
class ApplicantTypeDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        ids = request.data.get('id')
        if not ids:
            return Response({"statusCode": 400, "status": False, "message": "Provide 'id' field (list of UUIDs or 'all')."}, status=400)

        if ids == "all":
            objs = ApplicantType.objects.filter(is_deleted=False)
            count = objs.count()
            objs.update(is_deleted=True)
            return Response({"statusCode": 200, "status": True, "message": f"All {count} ApplicantType(s) deleted."})

        if not isinstance(ids, list):
            return Response({"statusCode": 400, "status": False, "message": "Provide a list of UUIDs."}, status=400)

        valid_uuids, invalid_uuids = [], []
        for u in ids:
            try:
                valid_uuids.append(UUID(u))
            except ValueError:
                invalid_uuids.append(u)

        objs = ApplicantType.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = objs.count()
        objs.update(is_deleted=True)

        return Response({"statusCode": 200, "status": True, "message": f"{count} ApplicantType(s) deleted.", "data": {"invalid_uuids": invalid_uuids}})


# ------------------ EXPORT ------------------
class ApplicantTypeExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'csv').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]
        field_list = [f.strip() for f in fields.split(',')] if fields else [
            'uuid', 'name', 'description', 'is_deleted', 'created_at', 'updated_at'
        ]

        queryset = ApplicantType.objects.filter(uuid__in=uuids) if uuids else ApplicantType.objects.all()
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
            filename = 'applicanttype.xlsx'
        else:
            data = CSV().export_data(dataset)
            content_type = 'text/csv; charset=utf-8'
            filename = 'applicanttype.csv'

        response = HttpResponse(data, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


# ------------------ IMPORT ------------------
class ApplicantTypeImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file uploaded'}, status=400)

        format_type = file.name.split('.')[-1].lower()
        dataset = Dataset()
        duplicate_names = []

        try:
            if format_type == 'xlsx':
                wb = openpyxl.load_workbook(file, read_only=True)
                sheet_name = request.data.get('sheet_name')
                if not sheet_name or sheet_name not in wb.sheetnames:
                    return Response({'error': 'Invalid sheet_name', 'available_sheets': wb.sheetnames}, status=400)
                ws = wb[sheet_name]
                headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                data = [dict(zip(headers, row)) for row in ws.iter_rows(min_row=2, values_only=True)]
            elif format_type == 'csv':
                dataset.load(file.read().decode('utf-8'), format='csv')
                data = dataset.dict
            else:
                return Response({'error': 'Unsupported file format'}, status=400)

            for row in reversed(data):
                name = str(row.get('name')).strip() if row.get('name') else ''
                description = str(row.get('description')).strip() if row.get('description') else ''

                if not name:
                    continue

                existing = ApplicantType.objects.filter(name__iexact=name).first()
                if existing:
                    if existing.is_deleted:
                        ApplicantType.objects.create(name=name, description=description, is_deleted=False)
                    else:
                        duplicate_names.append(name)
                        continue
                else:
                    ApplicantType.objects.create(name=name, description=description, is_deleted=False)
        except Exception as e:
            return Response({'error': str(e)}, status=400)

        return Response({"statusCode": 200, "status": True, "duplicates": list(set(duplicate_names)), "message": "Import successful"})