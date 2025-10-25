from django.shortcuts import render
from  .models  import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import  *
from django.core.paginator import Paginator
from django.db.models import Q
import uuid
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
    

class MasterTokenLoginAPIView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = AdminUserLoginSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            # Safe extraction of error message
            if isinstance(e.detail, dict):
                message = next(iter(e.detail.values()))[0]
            elif isinstance(e.detail, list):
                message = e.detail[0]
            else:
                message = str(e.detail)

            return Response({
                "status": False,
                "statusCode": status.HTTP_401_UNAUTHORIZED,
                "message": message
            }, status=status.HTTP_401_UNAUTHORIZED)

        user = serializer.validated_data['user']

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        refresh["email"] = user.email
        refresh["role"] = user.role.name if getattr(user, "role", None) else None
        refresh["user_type"] = "admin"
        refresh["admin_id"] = user.id

        return Response({
            "status": True,
            "statusCode": status.HTTP_200_OK,
            "message": "Login successful",
            "data": {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "name": getattr(user, "name", ""),
                    "email": user.email,
                    "role": user.role.name if getattr(user, "role", None) else None,
                    "user_type": "admin",
                    "is_master": user.is_superuser
                }
            }
        }, status=status.HTTP_200_OK)




class AdminLogoutView(APIView):
    authentication_classes = [JWTAuthentication] 
    permission_classes = [IsAuthenticated]  

    def post(self, request):
        ip = request.META.get("REMOTE_ADDR")
        user_agent = request.META.get("HTTP_USER_AGENT", "unknown")
        user = request.user

        try:
            refresh_token = request.data.get("refresh_token")  

           
            if not refresh_token:
                return Response(
                    {"statusCode": 400, "status": False, "message": "Refresh token is required"},
                    status=status.HTTP_200_OK
                )

            token = RefreshToken(refresh_token)
            token.blacklist()  

            return Response(
                    {"statusCode": 200, "status": True, "message": "Successfully logged out"},
                    status=status.HTTP_200_OK
                )

        except TokenError as e:
            return Response(
                {"statusCode": 400, "status": False, "message": "Invalid or expired refresh token"},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"statusCode": 500, "status": False, "message": "An unexpected error occurred", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



class GenderListAPIView(APIView):
    def get(self, request):
        search = request.GET.get("search", "")
        queryset = Gender.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(Q(text__icontains=search) | Q(description__icontains=search))
        serializer = GenderSerializer(queryset, many=True)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Genders retrieved successfully",
            "data": serializer.data
        })


class GenderCreateAPIView(APIView):
    def post(self, request):
        serializer = GenderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Gender created successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        

        errors = serializer.errors
        messages = []
        for field, msgs in errors.items():
            messages.extend(msgs)
        message_text = " ".join(messages)
        return Response({
            "statusCode": 400,
            "status": False,
            "message": message_text,
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)


class GenderDetailAPIView(APIView):
    def get(self, request, uuid):
        try:
            gender = Gender.objects.get(uuid=uuid, is_deleted=False)
        except Gender.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Gender not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = GenderSerializer(gender)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Gender retrieved successfully",
            "data": serializer.data
        })


class GenderUpdateAPIView(APIView):
    def put(self, request, uuid):
        try:
            gender = Gender.objects.get(uuid=uuid, is_deleted=False)
        except Gender.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Gender not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = GenderSerializer(gender, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Gender updated successfully",
                "data": serializer.data
            })


        errors = serializer.errors
        messages = []
        for field, msgs in errors.items():
            messages.extend(msgs)
        message_text = " ".join(messages)
        return Response({
            "statusCode": 400,
            "status": False,
            "message": message_text,
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)


class GenderDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        ids = request.data.get('id', None)

        if not ids:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide 'id' field (UUID list or 'all').",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        # If client requests all records to be deleted
        if ids == "all":
            genders = Gender.objects.filter(is_deleted=False)
            count = genders.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No genders found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
            genders.update(is_deleted=True)
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} gender(s) deleted successfully.",
                "data": None
            }, status=status.HTTP_200_OK)

        # Otherwise, treat it as a list of UUIDs
        if not isinstance(ids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide a list of UUIDs in 'id' field or 'all'.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate UUIDs
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

        genders = Gender.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = genders.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching genders found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_404_NOT_FOUND)

        genders.update(is_deleted=True)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} gender(s) deleted successfully.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        }, status=status.HTTP_200_OK)


#-------------------------------maritalstatus--------------------------------
class MaritalstatusListAPIView(APIView):
    def get(self, request):
        try:
            search = request.GET.get("search", "")
            page = int(request.GET.get("page", 1))
            per_page = int(request.GET.get("per_page", 10))

            queryset = Maritalstatus.objects.filter(is_deleted=False)
            if search:
                queryset = queryset.filter(Q(text__icontains=search) | Q(description__icontains=search))

            paginator = Paginator(queryset, per_page)
            page_obj = paginator.get_page(page)

            serializer = MaritalstatusSerializer(page_obj, many=True)
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Maritalstatus retrieved successfully",
                "total": paginator.count,
                "total_pages": paginator.num_pages,
                "current_page": page,
                "data": serializer.data
            })

        except ValueError:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Invalid page or per_page parameter",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "statusCode": 500,
                "status": False,
                "message": str(e),
                "data": None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MaritalstatusCreateAPIView(APIView):
    def post(self, request):
        serializer = MaritalstatusSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Maritalstatus created successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)


        errors = serializer.errors
        messages = []
        for field, msgs in errors.items():
            messages.extend(msgs)
        message_text = " ".join(messages)
        return Response({
            "statusCode": 400,
            "status": False,
            "message": message_text,
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)


class MaritalstatusDetailAPIView(APIView):
    def get(self, request, uuid):
        try:
            marital = Maritalstatus.objects.get(uuid=uuid, is_deleted=False)
        except Maritalstatus.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Maritalstatus not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = MaritalstatusSerializer(marital)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Maritalstatus retrieved successfully",
            "data": serializer.data
        })


class MaritalstatusUpdateAPIView(APIView):
    def put(self, request, uuid):
        try:
            marital = Maritalstatus.objects.get(uuid=uuid, is_deleted=False)
        except Maritalstatus.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Maritalstatus not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = MaritalstatusSerializer(marital, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Maritalstatus updated successfully",
                "data": serializer.data
            })


        errors = serializer.errors
        messages = []
        for field, msgs in errors.items():
            messages.extend(msgs)
        message_text = " ".join(messages)
        return Response({
            "statusCode": 400,
            "status": False,
            "message": message_text,
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)


class MaritalstatusDeleteAPIView(APIView):
    def delete(self, request, uuid):
        try:
            marital = Maritalstatus.objects.get(uuid=uuid, is_deleted=False)
        except Maritalstatus.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Maritalstatus not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        marital.is_deleted = True
        marital.save()
        return Response({
            "statusCode": 204,
            "status": True,
            "message": "Maritalstatus deleted successfully",
            "data": None
        }, status=status.HTTP_204_NO_CONTENT)


#-------------------------------continents--------------------------------

class ContinentsCreateAPIView(APIView):
    def post(self, request):
        name = request.data.get("name")
        description = request.data.get("description", "")
        if not name:
            return Response({ "statusCode":400,
                "status":False, "message": "name is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        if Continents.objects.filter(name=name).exists():
            return Response({ 
                "statusCode":400,
                "status":False,
                "message": "Continents with this text already exists"}, status=status.HTTP_400_BAD_REQUEST)
        
        continents = Continents.objects.create(
            name=name,
            description=description
        )
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Gender created successfully",
            "data": {
                "id": continents.uuid,
                "name": continents.name,
                "description": continents.description
            }
        }, status=status.HTTP_200_OK)


class ContinentsListAPIView(APIView):
    def get(self, request):
        
        search_query = request.GET.get('search', '').strip()
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))  

        
        continents = Continents.objects.filter(is_deleted=False)
        if search_query:
            continents = continents.filter(
                Q(name__icontains=search_query) | Q(description__icontains=search_query)
            )

        paginator = Paginator(continents, per_page)
        page_obj = paginator.get_page(page)

        data = [
            {
                "id": m.uuid,
                "name": m.name,
                "description": m.description
            }
            for m in page_obj
        ]

        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Continents retrieved successfully",
            "total_items": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": page_obj.number,
            "per_page": per_page,
            "has_next": page_obj.has_next(),
            "has_previous": page_obj.has_previous(),
            "data": data
        }, status=status.HTTP_200_OK)

class ContinentsUpdateAPIView(APIView):

    def put(self, request, pk):
        try:
            continent = Continents.objects.get(id=pk, is_deleted=False)
        except Continents.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Continents not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        new_name = request.data.get("name", continent.name)
        new_description = request.data.get("description", continent.description)
        

        if Continents.objects.filter(name=new_name).exclude(id=pk).exists():
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Continents with this text already exists"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        continent.name = new_name
        continent.description = new_description
        continent.save()
        
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Continents updated successfully",
            "data": {
                "id": continent.uuid,
                "name": continent.name,
                "description": continent.description
            }
        }, status=status.HTTP_200_OK)
    

class  ContinentsDeleteAPIView(APIView):
    def delete(self, request, pk):
        try:
            continents =  Continents.objects.get(id=pk, is_deleted=False)
        except Continents.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "continents not found"
            }, status=status.HTTP_404_NOT_FOUND)

        continents.is_deleted = True
        continents.save()

        return Response({
            "statusCode": 200,
            "status": True,
            "message": "continents deleted successfully"
        }, status=status.HTTP_200_OK)

#-------------------------------------------country---------------------------------

class CountryCreateAPIView(APIView):
    def post(self, request):
        try:
            name = request.data.get("name")
            continent_id = request.data.get("continent")
            shortName = request.data.get("shortName")
            fullName = request.data.get("fullName")
            officialName = request.data.get("officialName")
            capitalCity = request.data.get("capitalCity")
            dialCodes = request.data.get("dialCodes")
            currencyCode = request.data.get("currencyCode", "")
            status_flag = request.data.get("status", True)


            if not name:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Country name is required"
                }, status=status.HTTP_400_BAD_REQUEST)

            if Country.objects.filter(name__iexact=name, is_deleted=False).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Country name already exists"
                }, status=status.HTTP_400_BAD_REQUEST)


            continent = None
            if continent_id:
                try:
                    continent = Continents.objects.get(uuid=continent_id, is_deleted=False)
                except Continents.DoesNotExist:
                    return Response({
                        "statusCode": 404,
                        "status": False,
                        "message": "Invalid continent ID"
                    }, status=status.HTTP_404_NOT_FOUND)
            
            country = Country.objects.create(
                uuid=uuid.uuid4(),
                name=name,
                continent=continent,
                shortName=shortName,
                fullName=fullName,
                officialName=officialName,
                capitalCity=capitalCity,
                dialCodes=dialCodes,
                currencyCode=currencyCode,
                status=status_flag
            )

            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Country created successfully",
                "data": {
                    "id": country.uuid,
                    "name": country.name,
                    "continent": country.continent.name if country.continent else None,
                    "shortName": country.shortName,
                    "fullName": country.fullName,
                    "officialName": country.officialName,
                    "capitalCity": country.capitalCity,
                    "dialCodes": country.dialCodes,
                    "currencyCode": country.currencyCode,
                    "status": country.status,
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "statusCode": 500,
                "status": False,
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CountryListAPIView(APIView):
    def get(self, request):
        search = request.GET.get("search", "").strip()
        page = int(request.GET.get("page", 1))
        per_page = int(request.GET.get("per_page", 10))

        countries = Country.objects.filter(is_deleted=False)

        if search:
            countries = countries.filter(
                Q(name__icontains=search) |
                Q(fullName__icontains=search) |
                Q(capitalCity__icontains=search) |
                Q(currencyCode__icontains=search)
            )

        paginator = Paginator(countries, per_page)
        page_obj = paginator.get_page(page)

        data = [
            {
                "id": c.uuid,
                "name": c.name,
                "continent": c.continent.name if c.continent else None,
                "shortName": c.shortName,
                "fullName": c.fullName,
                "officialName": c.officialName,
                "capitalCity": c.capitalCity,
                "dialCodes": c.dialCodes,
                "currencyCode": c.currencyCode,
                "status": c.status,
            } for c in page_obj
        ]

        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Countries retrieved successfully",
            "total_items": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": page_obj.number,
            "per_page": per_page,
            "has_next": page_obj.has_next(),
            "has_previous": page_obj.has_previous(),
            "data": data
        }, status=status.HTTP_200_OK)

class CountryDetailAPIView(APIView):
    def get(self, request, pk):
        try:
            country = Country.objects.get(id=pk, is_deleted=False)
        except Country.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Country not found"
            }, status=status.HTTP_404_NOT_FOUND)

        data = {
            "id": country.uuid,
            "name": country.name,
            "continent": country.continent.name if country.continent else None,
            "shortName": country.shortName,
            "fullName": country.fullName,
            "officialName": country.officialName,
            "capitalCity": country.capitalCity,
            "dialCodes": country.dialCodes,
            "currencyCode": country.currencyCode,
            "status": country.status,
        }

        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Country retrieved successfully",
            "data": data
        }, status=status.HTTP_200_OK)

class CountryUpdateAPIView(APIView):
    def put(self, request, pk):
        try:
            country = Country.objects.get(id=pk, is_deleted=False)
        except Country.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Country not found"
            }, status=status.HTTP_404_NOT_FOUND)

        country.name = request.data.get("name", country.name)
        country.shortName = request.data.get("shortName", country.shortName)
        country.fullName = request.data.get("fullName", country.fullName)
        country.officialName = request.data.get("officialName", country.officialName)
        country.capitalCity = request.data.get("capitalCity", country.capitalCity)
        country.dialCodes = request.data.get("dialCodes", country.dialCodes)
        country.currencyCode = request.data.get("currencyCode", country.currencyCode)
        country.status = request.data.get("status", country.status)

        continent_id = request.data.get("continent")
        if continent_id:
            try:
                country.continent = Continents.objects.get(id=continent_id, is_deleted=False)
            except Continents.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Invalid continent ID"
                }, status=status.HTTP_404_NOT_FOUND)

        country.save()

        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Country updated successfully"
        }, status=status.HTTP_200_OK)


class CountryDeleteAPIView(APIView):
    def delete(self, request, pk):
        try:
            country = Country.objects.get(id=pk, is_deleted=False)
        except Country.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Country not found"
            }, status=status.HTTP_404_NOT_FOUND)

        country.is_deleted = True
        country.save()

        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Country deleted successfully"
        }, status=status.HTTP_200_OK)


class CountriesByContinentAPIView(APIView):
    def get(self, request):
        continent_id = request.GET.get("continent_id")
        if not continent_id:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "continent_id is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            continent_uuid = uuid.UUID(continent_id)
        except ValueError:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Invalid UUID format for continent_id"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            continent = Continents.objects.get(id=continent_id)
        except Continents.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Invalid Continent ID"
            }, status=status.HTTP_404_NOT_FOUND)

        countries = Country.objects.filter(continent=continent)
        data = []
        for country in countries:
            data.append({
                "id": str(country.uuid),
                "name": country.name,
                "shortName": country.shortName,
                "fullName": country.fullName
            })

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"Countries for continent '{continent.name}' fetched successfully",
            "data": data
        }, status=status.HTTP_200_OK)



#-------------------------------------------state---------------------------------

class StateCreateAPIView(APIView):
    def post(self, request):
        try:
            statename = request.data.get("name")
            country_id = request.data.get("countryName") 
            stateshortName = request.data.get("stateshortName")
            description = request.data.get("description")
            status_flag = request.data.get("is_active", True)

            if not statename:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "State name is required"
                }, status=status.HTTP_400_BAD_REQUEST)

            if State.objects.filter(stateName__iexact=statename, is_deleted=False).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "State name already exists"
                }, status=status.HTTP_400_BAD_REQUEST)

            country = None
            if country_id:
                try:
                    country = Country.objects.get(id=country_id, is_deleted=False)
                except Country.DoesNotExist:
                    return Response({
                        "statusCode": 404,
                        "status": False,
                        "message": "Invalid Country ID"
                    }, status=status.HTTP_404_NOT_FOUND)

            state = State.objects.create(
                id=uuid.uuid4(),
                stateName=statename,
                countryName=country,  # pass the Country object
                stateshortName=stateshortName,
                description=description,
                is_active=status_flag
            )

            return Response({
                "statusCode": 200,
                "status": True,
                "message": "State created successfully",
                "data": {
                    "id": state.uuid,
                    "name": state.stateName,
                    "country": state.countryName.name if state.countryName else None,
                    "stateshortName": state.stateshortName,
                    "description": state.description,
                    "status": state.is_active,
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "statusCode": 500,
                "status": False,
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StateListAPIView(APIView):
    def get(self, request):
        search = request.GET.get("search", "").strip()
        page = int(request.GET.get("page", 1))
        per_page = int(request.GET.get("per_page", 10))

        state = State.objects.filter(is_deleted=False)

        if search:
            state = state.filter(
                Q(stateName__icontains=search) 
            )

        paginator = Paginator(state, per_page)
        page_obj = paginator.get_page(page)

        data = [
            {
                "id": s.uuid,
                "name": s.stateName,
                "continent": s.countryName.name if s.countryName else None,
                "shortName": s.stateshortName,
                "description": s.description,
                "is_active": s.is_active,
            } for s in page_obj
        ]

        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Countries retrieved successfully",
            "total_items": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": page_obj.number,
            "per_page": per_page,
            "has_next": page_obj.has_next(),
            "has_previous": page_obj.has_previous(),
            "data": data
        }, status=status.HTTP_200_OK)


class StateUpdateAPIView(APIView):
    def put(self, request, pk):
        try:
            state = State.objects.get(id=pk, is_deleted=False)
        except State.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "State not found"
            }, status=status.HTTP_404_NOT_FOUND)

        state.stateName = request.data.get("stateName", state.stateName)
        state.stateshortName = request.data.get("stateshortName", state.stateshortName)
        state.description = request.data.get("description", state.description)
        state.is_active = request.data.get("is_active", state.is_active)

        country_id = request.data.get("countryName")
        if country_id:
            try:
                state.countryName = Country.objects.get(id=country_id, is_deleted=False)
            except Country.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Invalid country ID"
                }, status=status.HTTP_404_NOT_FOUND)

        state.save()

        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Country updated successfully"
        }, status=status.HTTP_200_OK)


class StateDeleteAPIView(APIView):
    def delete(self, request, pk):
        try:
            state = State.objects.get(id=pk, is_deleted=False)
        except State.DoesNotExist:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "State not found"
            }, status=status.HTTP_404_NOT_FOUND)
        state.is_deleted=True
        state.save()
        return Response({"statusCode": 200,
                "status": True,
                "message": "State deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

class StateByCountryAPIView(APIView):
    def get(self, request):
        country_id = request.GET.get("country_id")
        if not country_id:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "country_id is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        

        try:
            country_uuid = uuid.UUID(country_id)
        except ValueError:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Invalid UUID format for country_id"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            country = Country.objects.get(id=country_id)
        except Country.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Invalid Country ID"
            }, status=status.HTTP_404_NOT_FOUND)

        states = State.objects.filter(countryName=country)
        data = []
        for state in states:
            data.append({
                "id": str(state.uuid),
                "name": state.stateName,
                "shortName": state.stateshortName,
                "fullName": state.description
            })

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"State for country '{state.stateName}' fetched successfully",
            "data": data
        }, status=status.HTTP_200_OK)







#-------------------------------------------district---------------------------------

class DistrictCreateAPIView(APIView):
    def post(self, request):
        try:
            country_id = request.data.get("country_id")
            state_id = request.data.get("state_id")
            district_name = request.data.get("districtName")
            description = request.data.get("description", "")

            if not district_name:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "districtName is required"
                }, status=status.HTTP_400_BAD_REQUEST)

            if District.objects.filter(districtName__iexact=district_name).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "District with this name already exists"
                }, status=status.HTTP_400_BAD_REQUEST)

            if not country_id:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Country ID is required"
                }, status=status.HTTP_400_BAD_REQUEST)

            country = Country.objects.filter(id=country_id).first()
            if not country:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Invalid Country ID"
                }, status=status.HTTP_404_NOT_FOUND)

            state = None
            if state_id:
                state = State.objects.filter(id=state_id, countryName=country).first()
                if not state:
                    return Response({
                        "statusCode": 404,
                        "status": False,
                        "message": "Invalid State ID for this Country"
                    }, status=status.HTTP_404_NOT_FOUND)

            district = District.objects.create(
                countryName=country,
                stateName=state,
                districtName=district_name,
                description=description
            )

            return Response({

                "statusCode": 200,
                "status": True,
                "message":"District createed sucessfully",
                "data":{
                    "id": str(district.uuid),
                    "districtName": district.districtName,
                    "country": district.countryName.name if district.countryName else None,
                    "state": district.stateName.stateName if district.stateName else None,
                    "description": district.description
                }
                
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "statusCode": 500,
                "status": False,
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DistrictListAPIView(APIView):
    def get(self, request):
        search_query = request.GET.get("search", "").strip()
        page = int(request.GET.get("page", 1))
        per_page = int(request.GET.get("per_page", 10))

        districts = District.objects.all()
        if search_query:
            districts = districts.filter(districtName__icontains=search_query)

        paginator = Paginator(districts, per_page)
        page_obj = paginator.get_page(page)

        data = []
        for district in districts:
            data.append({
                "id": str(district.uuid),
                "districtName": district.districtName,
                "country": district.countryName.name if district.countryName else None,
                "state": district.stateName.stateName if district.stateName else None,
                "description": district.description
            })

        return Response({
            "statusCode":200,
            "status":True,
            "message": "Countries retrieved successfully",
            "total_items": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": page_obj.number,
            "per_page": per_page,
            "data": data
        }, status=status.HTTP_200_OK)



class DistrictUpdateAPIView(APIView):
    def put(self, request, pk):
        try:
            district = District.objects.get(id=pk, is_deleted=False)
        except City.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "District not found"
            }, status=status.HTTP_404_NOT_FOUND)

        district_name = request.data.get("districtName", district.districtName)
        description = request.data.get("description", district.description)
        country_id = request.data.get("country_id")
        state_id = request.data.get("state_id")

        if District.objects.filter(districtName=district_name).exclude(id=pk).exists():
            return Response({"statusCode": 400,
                "status": False,
                "error": "District with this name already exists"}, status=status.HTTP_400_BAD_REQUEST)

        district.districtName = district_name
        district.description = description
        district.countryName = Country.objects.filter(id=country_id).first() if country_id else district.countryName
        district.stateName = State.objects.filter(id=state_id).first() if state_id else district.stateName
        district.save()

        return Response({
            "statusCode": 200,
            "status": True,
            "message":"District updated successfully",
            "data":{
                "id": str(district.uuid),
                "districtName": district.districtName,
                "country": district.countryName.name if district.countryName else None,
                "state": district.stateName.stateName if district.stateName else None,
                "description": district.description
            }
        }, status=status.HTTP_200_OK)



class DistrictDeleteAPIView(APIView):
    def delete(self, request, pk):
        try:
            district = District.objects.get(id=pk, is_deleted=False)
        except District.DoesNotExist:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "District not found"
            }, status=status.HTTP_404_NOT_FOUND)
        district.is_deleted=True
        district.save()
        return Response({"statusCode": 200,
                "status": True,
                "message": "District deleted successfully"}, status=status.HTTP_204_NO_CONTENT)






class DistrictByFilterAPIView(APIView):
    def get(self, request):
        country_id = request.GET.get("country_id")
        state_id = request.GET.get("state_id")


        if country_id:
            try:
                country_uuid = uuid.UUID(country_id)
            except ValueError:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Invalid UUID format for country_id"
                }, status=status.HTTP_400_BAD_REQUEST)
            try:
                country = Country.objects.get(id=country_uuid)
            except Country.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Country not found"
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            country = None

        if state_id:
            try:
                state_uuid = uuid.UUID(state_id)
            except ValueError:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Invalid UUID format for state_id"
                }, status=status.HTTP_400_BAD_REQUEST)
            try:
                state = State.objects.get(id=state_uuid)
            except State.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "State not found"
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            state = None


        districts = District.objects.filter(is_deleted=False)
        if country:
            districts = districts.filter(countryName=country)
        if state:
            districts = districts.filter(stateName=state)

        data = []
        for district in districts:
            data.append({
                "id": str(district.id),
                "districtName": district.districtName,
                "country": district.countryName.name if district.countryName else None,
                "state": district.stateName.stateName if district.stateName else None,
                "description": district.description
            })

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{len(data)} districts fetched successfully",
            "data": data
        }, status=status.HTTP_200_OK)






class CityCreateAPIView(APIView):
    def post(self, request):
        try:
            country_id = request.data.get("country_id")
            state_id = request.data.get("state_id")
            district_id = request.data.get("district_id")
            city_name = request.data.get("cityName")
            description = request.data.get("description", "")

            if not city_name:
                return Response({"statusCode": 400,
                "status": False,
                "message": "cityName is required"}, status=status.HTTP_400_BAD_REQUEST)

            if City.objects.filter(cityName=city_name).exists():
                return Response({
                    "statusCode": 400,
                "status": False,
                "message": "City with this name already exists"}, status=status.HTTP_400_BAD_REQUEST)

            country = Country.objects.filter(id=country_id).first() if country_id else None
            state = State.objects.filter(id=state_id).first() if state_id else None
            district = District.objects.filter(id=district_id).first() if district_id else None

            city = City.objects.create(
                countryName=country,
                stateName=state,
                districtName=district,
                cityName=city_name,
                description=description
            )

            return Response({
                "statusCode": 200,
                "status": True,
                "message":"City created sucessfully",
                "data":{
                "id": str(city.uuid),
                "cityName": city.cityName,
                "country": city.countryName.name if city.countryName else None,
                "state": city.stateName.stateName if city.stateName else None,
                "district": city.districtName.districtName if city.districtName else None,
                "description": city.description
            }}, status=status.HTTP_200_OK)
        

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class CityListAPIView(APIView):
    def get(self, request):
        search = request.GET.get("search", "").strip()
        page = int(request.GET.get("page", 1))
        per_page = int(request.GET.get("per_page", 10))

        city = City.objects.filter(is_deleted=False)

        if search:
            city = city.filter(
                Q(cityName__icontains=search) 
            )

        paginator = Paginator(city, per_page)
        page_obj = paginator.get_page(page)

        data = [
            {
                "id": c.uuid,
                "cityName": c.cityName,
                "country": c.countryName.name if c.countryName else None,
                "state": c.stateName.stateName if c.stateName else None,
                "district": c.districtName.districtName if c.districtName else None,
                "description": c.description
            } for c in page_obj
        ]

        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Countries retrieved successfully",
            "total_items": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": page_obj.number,
            "per_page": per_page,
            "has_next": page_obj.has_next(),
            "has_previous": page_obj.has_previous(),
            "data": data
        }, status=status.HTTP_200_OK)


class CityUpdateAPIView(APIView):


    def put(self, request, pk):
        try:
            city = City.objects.get(id=pk, is_deleted=False)
        except City.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "State not found"
            }, status=status.HTTP_404_NOT_FOUND)

        city_name = request.data.get("cityName", city.cityName)
        description = request.data.get("description", city.description)
        country_id = request.data.get("country_id")
        state_id = request.data.get("state_id")
        district_id = request.data.get("district_id")


        if City.objects.filter(cityName=city_name).exclude(id=pk).exists():
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "City with this name already exists"}, status=status.HTTP_400_BAD_REQUEST)

        city.cityName = city_name
        city.description = description
        city.countryName = Country.objects.filter(id=country_id).first() if country_id else city.countryName
        city.stateName = State.objects.filter(id=state_id).first() if state_id else city.stateName
        city.districtName = District.objects.filter(id=district_id).first() if district_id else city.districtName

        city.save()

        return Response(
            {
            "statusCode": 200,
            "status": True,
            "message":"City updated  successfully",
            "data":{
                "id": str(city.uuid),
                "cityName": city.cityName,
                "country": city.countryName.name if city.countryName else None,
                "state": city.stateName.stateName if city.stateName else None,
                "district": city.districtName.districtName if city.districtName else None,
                "description": city.description
        }}, status=status.HTTP_200_OK)


class CityDeleteAPIView(APIView):
    def delete(self, request, pk):
        try:
            city = City.objects.get(id=pk, is_deleted=False)
        except City.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "State not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        city.is_deleted = True
        city.save()

        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Relation deleted successfully"
        }, status=status.HTTP_200_OK)








class RelationCreateAPIView(APIView):
    def post(self, request):
        try:
            relation_name = request.data.get("relation")
            description = request.data.get("description", "")

            if not relation_name:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Relation name is required"
                }, status=status.HTTP_400_BAD_REQUEST)

            if Relation.objects.filter(relation__iexact=relation_name, is_deleted=False).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Relation already exists"
                }, status=status.HTTP_400_BAD_REQUEST)

            relation = Relation.objects.create(
                id=uuid.uuid4(),
                relation=relation_name,
                description=description
            )

            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Relation created successfully",
                "data": {
                    "id": str(relation.uuid),
                    "relation": relation.relation,
                    "description": relation.description
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "statusCode": 500,
                "status": False,
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RelationListAPIView(APIView):
    def get(self, request):
        try:
            search = request.GET.get("search", "")
            page = int(request.GET.get("page", 1))
            per_page = int(request.GET.get("per_page", 10))

            relations = Relation.objects.filter(is_deleted=False)

            if search:
                relations = relations.filter(relation__icontains=search)

            paginator = Paginator(relations, per_page)
            page_obj = paginator.get_page(page)

            data = []
            for rel in page_obj:
                data.append({
                    "id": str(rel.uuid),
                    "relation": rel.relation,
                    "description": rel.description
                })

            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Relation list fetched successfully",
                "total": paginator.count,
                "total_pages": paginator.num_pages,
                "current_page": page,
                "data": data
            }, status=status.HTTP_200_OK)

        except ValueError:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Invalid page or per_page parameter"
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
             
            return Response({
                "statusCode": 500,
                "status": False,
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class RelationUpdateAPIView(APIView):
    def put(self, request, pk):
        try:

            try:
                uuid.UUID(str(pk))
            except ValueError:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Invalid relation ID format"
                }, status=status.HTTP_400_BAD_REQUEST)


            try:
                relation = Relation.objects.get(id=pk, is_deleted=False)
            except Relation.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Relation not found"
                }, status=status.HTTP_404_NOT_FOUND)


            relation_name = request.data.get("relation", "").strip()
            description = request.data.get("description", "").strip()

            if not relation_name:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Relation name is required"
                }, status=status.HTTP_400_BAD_REQUEST)


            if Relation.objects.filter(
                relation__iexact=relation_name, is_deleted=False
            ).exclude(id=pk).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Relation with this name already exists"
                }, status=status.HTTP_400_BAD_REQUEST)


            relation.relation = relation_name
            relation.description = description or relation.description
            relation.save()

            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Relation updated successfully",
                "data": {
                    "id": str(relation.uuid),
                    "relation": relation.relation,
                    "description": relation.description
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "statusCode": 500,
                "status": False,
                "message": f"Something went wrong: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RelationDeleteAPIView(APIView):
    def delete(self, request, pk):
        try:
            relation = Relation.objects.get(id=pk, is_deleted=False)
        except Relation.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "State not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        relation.is_deleted = True
        relation.save()

        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Relation deleted successfully"
        }, status=status.HTTP_200_OK)





class TimezoneCreateAPIView(APIView):
    def post(self, request):
        try:
            timezone_name = request.data.get("Timezone")
            country_id = request.data.get("country_id")
            state_id = request.data.get("state_id")
            description = request.data.get("description", "")

            if not timezone_name:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Timezone name is required"
                }, status=status.HTTP_400_BAD_REQUEST)

            if Timezone.objects.filter(Timezone__iexact=timezone_name, is_deleted=False).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Timezone with this name already exists"
                }, status=status.HTTP_400_BAD_REQUEST)

            country = Country.objects.filter(id=country_id).first() if country_id else None
            state = State.objects.filter(id=state_id).first() if state_id else None

            timezone_obj = Timezone.objects.create(
                id=uuid.uuid4(),
                Timezone=timezone_name,
                countryName=country,
                stateName=state,
                description=description
            )

            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Timezone created successfully",
                "data": {
                    "id": str(timezone_obj.uuid),
                    "Timezone": timezone_obj.Timezone,
                    "country": timezone_obj.countryName.name if timezone_obj.countryName else None,
                    "state": timezone_obj.stateName.stateName if timezone_obj.stateName else None,
                    "description": timezone_obj.description
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "statusCode": 500,
                "status": False,
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TimezoneListAPIView(APIView):
    def get(self, request):
        search = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        per_page = int(request.GET.get("per_page", 10))

        timezones = Timezone.objects.filter(is_deleted=False)
        if search:
            timezones = timezones.filter(Timezone__icontains=search)

        paginator = Paginator(timezones, per_page)
        page_obj = paginator.get_page(page)

        data = []
        for tz in page_obj:
            data.append({
                "id": str(tz.uuid),
                "Timezone": tz.Timezone,
                "country": tz.countryName.name if tz.countryName else None,
                "state": tz.stateName.stateName if tz.stateName else None,
                "description": tz.description
            })

        return Response({
            "statusCode": 200,
            "status": True,
            "total": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": page,
            "message": "Timezones fetched successfully",
            "data": data
        }, status=status.HTTP_200_OK)




class TimezoneUpdateAPIView(APIView):
    def put(self, request, pk):
        try:
            try:
                timezone_obj = Timezone.objects.get(id=pk, is_deleted=False)
            except Timezone.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Timezone not found"
                }, status=status.HTTP_404_NOT_FOUND)

            timezone_obj.Timezone = request.data.get("Timezone", timezone_obj.Timezone)
            timezone_obj.description = request.data.get("description", timezone_obj.description)

            country_id = request.data.get("country_id")
            state_id = request.data.get("state_id")

            if country_id:
                timezone_obj.countryName = Country.objects.filter(id=country_id).first()
            if state_id:
                timezone_obj.stateName = State.objects.filter(id=state_id).first()

            timezone_obj.save()

            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Timezone updated successfully",
                "data": {
                    "id": str(timezone_obj.uuid),
                    "Timezone": timezone_obj.Timezone,
                    "country": timezone_obj.countryName.name if timezone_obj.countryName else None,
                    "state": timezone_obj.stateName.stateName if timezone_obj.stateName else None,
                    "description": timezone_obj.description
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "statusCode": 500,
                "status": False,
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TimezoneDeleteAPIView(APIView):
    def delete(self, request, pk):
        try:
            try:
                timezone_obj = Timezone.objects.get(id=pk, is_deleted=False)
            except Timezone.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Timezone not found"
                }, status=status.HTTP_404_NOT_FOUND)

            timezone_obj.is_deleted = True
            timezone_obj.save()

            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Timezone deleted successfully"
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "statusCode": 500,
                "status": False,
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        



class DepartmentListAPIView(APIView):
    def get(self, request):
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_order = request.GET.get('sortOrder', 'asc')


        allowed_sort_fields = ['name', 'description', 'created_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'

        if sort_order == 'desc':
            sort_by = f'-{sort_by}'


        queryset = Department.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )

        queryset = queryset.order_by(sort_by)

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = DepartmentSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)




class DepartmentCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        name = request.data.get("name").strip()  # get name from request

        # Check if a department with this name exists
        existing = Department.objects.filter(name__iexact=name).first()

        if existing:
            if existing.is_deleted:
                # Reactivate the deleted department
                existing.is_deleted = False
                existing.description = request.data.get("description", existing.description)
                existing.save()
                serializer = DepartmentSerializer(existing)
                return Response({
                    "statusCode": 200,
                    "status": True,
                    "message": "Department reactivated successfully",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Department with this name already exists."
                }, status=status.HTTP_400_BAD_REQUEST)

        # If it doesn't exist, create new
        serializer = DepartmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Department created successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        else:
            errors = serializer.errors
            messages = []
            for field, msgs in errors.items():
                messages.extend(msgs)
            message_text = " ".join(messages)

            return Response({
                "statusCode": 400,
                "status": False,
                "message": message_text,
            }, status=status.HTTP_400_BAD_REQUEST)



class DepartmentRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    def get(self, request, uuid):
        try:
            department = Department.objects.get(uuid=uuid, is_deleted=False)
        except Department.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Department not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = DepartmentSerializer(department)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Department retrieved successfully",
            "data": serializer.data
        })


class DepartmentUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    def put(self, request, uuid):
        try:
            department = Department.objects.get(uuid=uuid, is_deleted=False)
        except Department.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Department not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = DepartmentSerializer(department, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Department updated successfully",
                "data": serializer.data
            })


        errors = serializer.errors
        messages = []
        for field, msgs in errors.items():
            messages.extend(msgs)
        message_text = " ".join(messages)

        return Response({
            "statusCode": 400,
            "status": False,
            "message": message_text,
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)


class DepartmentDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        ids = request.data.get('id', None)

        if not ids:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide 'id' field (UUID list or 'all').",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        # If client requests all departments to be deleted
        if ids == "all":
            departments = Department.objects.filter(is_deleted=False)
            count = departments.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No departments found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
            departments.update(is_deleted=True)
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} department(s) deleted successfully.",
                "data": None
            }, status=status.HTTP_200_OK)

        # Otherwise, treat as list of UUIDs
        if not isinstance(ids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide a list of UUIDs in 'id' field or 'all'.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate UUIDs
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

        # Fetch departments that exist and are not deleted
        departments = Department.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = departments.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching departments found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_404_NOT_FOUND)

        # Soft delete
        departments.update(is_deleted=True)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} department(s) deleted successfully.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        }, status=status.HTTP_200_OK)





class DepartmentExportAPIView(APIView):

    def get(self, request):
        format_type = request.GET.get('format', 'csv').lower()
        fields = request.GET.get('fields')  
        uuids_param = request.GET.get('uuids', '')

        uuids = [u.strip() for u in uuids_param.split(',') if u]

        # Default fields if none provided
        if fields:
            field_list = [f.strip() for f in fields.split(',')]
        else:
            field_list = ['uuid', 'name', 'description', 'is_deleted', 'created_at', 'updated_at']

        if uuids:
            queryset = Department.objects.filter(uuid__in=uuids)
        else:
            queryset = Department.objects.all()

        dataset = Dataset()
        dataset.headers = field_list

        for dept in queryset:
            row = []
            for field in field_list:
                value = getattr(dept, field, '')  # get attribute dynamically
                # Format datetime fields
                if isinstance(value, datetime.datetime):
                    value = value.strftime("%Y-%m-%d %H:%M:%S")
                # Convert boolean to int
                if isinstance(value, bool):
                    value = int(value)
                row.append(value if value is not None else '')
            dataset.append(row)

        if format_type == 'xlsx':
            data = XLSX().export_data(dataset)
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'departments.xlsx'
        else:
            data = CSV().export_data(dataset)
            content_type = 'text/csv; charset=utf-8'
            file_name = 'departments.csv'

        response = HttpResponse(data, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


class DepartmentImportAPIView(APIView):
    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')  # <-- User se sheet name lena

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        dataset = Dataset()

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

                    # Check for existing department
                    if Department.objects.filter(name__iexact=name).exists():
                        duplicate_names.append(name)
                        continue  # skip adding duplicate

                    Department.objects.create(
                        name=name,
                        description=row.get('description', ''),
                        is_deleted=row.get('is_deleted', False)
                    )

            else:  
                dataset.load(file.read().decode('utf-8'), format='csv')
                for row in dataset.dict:
                    name = str(row.get('name')).strip() if row.get('name') else None
                    if not name:
                        continue

                    if Department.objects.filter(name__iexact=name).exists():
                        duplicate_names.append(name)
                        continue

                    Department.objects.create(
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
        }, status=status.HTTP_200_OK)

        
# -----------------------employeeType---------------------------------
class EmployeeTypeListAPIView(APIView):    

    def get(self, request):
        search = request.GET.get('search', '').strip()
        queryset = EmployeeType.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )

        queryset = queryset.order_by('-created_at')

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = EmployeeTypeSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)


class EmployeeTypeCreateAPIView(APIView):
    def post(self, request):
        serializer = EmployeeTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Employee type created successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        else:

            errors = serializer.errors
            messages = []
            for field, msgs in errors.items():
                messages.extend(msgs)
            message_text = " ".join(messages)
            return Response({
                "statusCode": 400,
                "status": False,
                "message": message_text,
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)


class EmployeeTypeRetrieveAPIView(APIView):
    def get(self, request, uuid):
        try:
            emp_type = EmployeeType.objects.get(uuid=uuid, is_deleted=False)
        except EmployeeType.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Employee type not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = EmployeeTypeSerializer(emp_type)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Employee type retrieved successfully",
            "data": serializer.data
        })


class EmployeeTypeUpdateAPIView(APIView):
    def put(self, request, uuid):
        try:
            emp_type = EmployeeType.objects.get(uuid=uuid, is_deleted=False)
        except EmployeeType.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Employee type not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = EmployeeTypeSerializer(emp_type, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Employee type updated successfully",
                "data": serializer.data
            })


        errors = serializer.errors
        messages = []
        for field, msgs in errors.items():
            messages.extend(msgs)
        message_text = " ".join(messages)

        return Response({
            "statusCode": 400,
            "status": False,
            "message": message_text,
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)


class EmployeeTypeDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        uuids = request.data.get('id', None)

        # Single delete via URL parameter
        if uuid:
            try:
                emp_type = EmployeeType.objects.get(uuid=uuid, is_deleted=False)
                emp_type.is_deleted = True
                emp_type.save()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "Employee type deleted successfully",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            except EmployeeType.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Employee type not found",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        # Delete all if "all" is sent
        if uuids == "all":
            emp_types = EmployeeType.objects.filter(is_deleted=False)
            count = emp_types.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No employee types found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
            emp_types.update(is_deleted=True)
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} employee type(s) deleted successfully.",
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
        emp_types = EmployeeType.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = emp_types.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching employee types found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_404_NOT_FOUND)

        emp_types.update(is_deleted=True)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} employee type(s) deleted successfully.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        }, status=status.HTTP_200_OK)



class EmployeeTypeExportAPIView(APIView):
    # permission_classes = [IsAuthenticated]  

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
            queryset = EmployeeType.objects.filter(uuid__in=uuids)
        else:
            queryset = EmployeeType.objects.all()
        
        dataset = Dataset()
        dataset.headers = field_list

        for dept in queryset:
            row = []
            for field in field_list:
                value = getattr(dept, field, '')  
                
                if isinstance(value, datetime.datetime):
                    value = value.strftime("%Y-%m-%d %H:%M:%S")
                
                if isinstance(value, bool):
                    value = int(value)
                row.append(value if value is not None else '')
            dataset.append(row)

        if format_type == 'xlsx':
            data = XLSX().export_data(dataset)
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'Employeetype.xlsx'
        else:
            data = CSV().export_data(dataset)
            content_type = 'text/csv; charset=utf-8'
            file_name = 'Employeetype.csv'

        response = HttpResponse(data, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response



class EmployeeTypeImportAPIView(APIView):
    
    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name') 
        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        dataset = Dataset()

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

                    # Check for existing department
                    if EmployeeType.objects.filter(name__iexact=name).exists():
                        duplicate_names.append(name)
                        continue  # skip adding duplicate

                    EmployeeType.objects.create(
                        name=name,
                        description=row.get('description', ''),
                        is_deleted=row.get('is_deleted', False)
                    )

            else:  # CSV
                dataset.load(file.read().decode('utf-8'), format='csv')
                for row in dataset.dict:
                    name = str(row.get('name')).strip() if row.get('name') else None
                    if not name:
                        continue

                    if EmployeeType.objects.filter(name__iexact=name).exists():
                        duplicate_names.append(name)
                        continue

                    EmployeeType.objects.create(
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
        }, status=status.HTTP_200_OK)




class CompanyTypeListAPIView(APIView):    
    def get(self, request):
        search = request.GET.get('search', '').strip()
        queryset = CompanyType.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )

        queryset = queryset.order_by('-created_at')

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = CompanyTypeSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)

class CompanyTypeCreateAPIView(APIView):
    def post(self, request):
        serializer = CompanyTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Company type created successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        errors = serializer.errors
        messages = []
        for field, msgs in errors.items():
            messages.extend(msgs)
        message_text = " ".join(messages)
        return Response({
            "statusCode": 400,
            "status": False,
            "message": message_text,
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)

class CompanyTypeDetailAPIView(APIView):
    def get(self, request, uuid):
        try:
            company_type = CompanyType.objects.get(uuid=uuid, is_deleted=False)
        except CompanyType.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Company type not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = CompanyTypeSerializer(company_type)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Company type retrieved successfully",
            "data": serializer.data
        })

class CompanyTypeUpdateAPIView(APIView):
    def put(self, request, uuid):
        try:
            company_type = CompanyType.objects.get(uuid=uuid, is_deleted=False)
        except CompanyType.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Company type not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = CompanyTypeSerializer(company_type, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Company type updated successfully",
                "data": serializer.data
            })

        errors = serializer.errors
        messages = []
        for field, msgs in errors.items():
            messages.extend(msgs)
        message_text = " ".join(messages)
        return Response({
            "statusCode": 400,
            "status": False,
            "message": message_text,
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)


class CompanyTypeDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        ids = request.data.get('id', None)

        # ✅ Case 1: Single delete (UUID passed in URL)
        if uuid:
            try:
                company_type = CompanyType.objects.get(uuid=uuid, is_deleted=False)
                company_type.is_deleted = True
                company_type.save()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "Company type deleted successfully",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            except CompanyType.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Company type not found",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        # ✅ Case 2: Delete all
        if ids == "all":
            company_types = CompanyType.objects.filter(is_deleted=False)
            count = company_types.count()
            if count == 0:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "No company types found to delete.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
            company_types.update(is_deleted=True)
            return Response({
                "statusCode": 200,
                "status": True,
                "message": f"All {count} company type(s) deleted successfully.",
                "data": None
            }, status=status.HTTP_200_OK)

        # ✅ Case 3: Multiple delete (UUIDs in request body)
        if not ids or not isinstance(ids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide a list of UUIDs in 'id' field or 'all'.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate UUIDs
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

        # Fetch company types that exist and are not deleted
        company_types = CompanyType.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = company_types.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching company types found.",
                "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
            }, status=status.HTTP_404_NOT_FOUND)

        # Soft delete
        company_types.update(is_deleted=True)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} company type(s) deleted successfully.",
            "data": {"invalid_uuids": invalid_uuids} if invalid_uuids else None
        }, status=status.HTTP_200_OK)
    
class CompanyTypeExportAPIView(APIView):
    # permission_classes = [IsAuthenticated]  
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
            queryset = CompanyType.objects.filter(uuid__in=uuids)
        else:
            queryset = CompanyType.objects.all()

        dataset = Dataset()
        dataset.headers = field_list

        for dept in queryset:
            row = []
            for field in field_list:
                value = getattr(dept, field, '')  
                
                if isinstance(value, datetime.datetime):
                    value = value.strftime("%Y-%m-%d %H:%M:%S")
                
                if isinstance(value, bool):
                    value = int(value)
                row.append(value if value is not None else '')
            dataset.append(row)
        

        if format_type == 'xlsx':
            data = XLSX().export_data(dataset)
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'companytype.xlsx'
        else:
            data = CSV().export_data(dataset)
            content_type = 'text/csv; charset=utf-8'
            file_name = 'companytype.csv'

        response = HttpResponse(data, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


class CompanyTypeImportAPIView(APIView):
    
    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name') 
        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        dataset = Dataset()

        duplicate_names = [] 

        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        dataset = Dataset()

        
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

                    if CompanyType.objects.filter(name__iexact=name).exists():
                        duplicate_names.append(name)
                        continue 

                    CompanyType.objects.create(
                        name=name,
                        description=row.get('description', ''),
                        is_deleted=row.get('is_deleted', False)
                    )

            else:  
                dataset.load(file.read().decode('utf-8'), format='csv')
                for row in dataset.dict:
                    name = str(row.get('name')).strip() if row.get('name') else None
                    if not name:
                        continue

                    if CompanyType.objects.filter(name__iexact=name).exists():
                        duplicate_names.append(name)
                        continue

                    CompanyType.objects.create(
                        name=name,
                        description=row.get('description', ''),
                        is_deleted=row.get('is_deleted', False)
                    )
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
        


        return Response({
            "statusCode": 200,
            "status": True,
            'message': 'Import successful'}, status=status.HTTP_200_OK)
    








class OwnershipTypeListAPIView(APIView):    
    def get(self, request):
        search = request.GET.get('search', '').strip()
        queryset = OwnershipType.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )

        queryset = queryset.order_by('-created_at')

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = OwnershipTypeSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)

class OwnershipTypeCreateAPIView(APIView):
    def post(self, request):
        serializer = OwnershipTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Ownership type created successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        errors = serializer.errors
        messages = []
        for field, msgs in errors.items():
            messages.extend(msgs)
        message_text = " ".join(messages)
        return Response({
            "statusCode": 400,
            "status": False,
            "message": message_text,
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)

class OwnershipTypeDetailAPIView(APIView):
    def get(self, request, uuid):
        try:
            ownership = OwnershipType.objects.get(uuid=uuid, is_deleted=False)
        except OwnershipType.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Ownership type not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = OwnershipTypeSerializer(ownership)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Ownership type retrieved successfully",
            "data": serializer.data
        })

class OwnershipTypeUpdateAPIView(APIView):
    def put(self, request, uuid):
        try:
            ownership = OwnershipType.objects.get(uuid=uuid, is_deleted=False)
        except OwnershipType.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Ownership type not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = OwnershipTypeSerializer(ownership, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Ownership type updated successfully",
                "data": serializer.data
            })

        errors = serializer.errors
        messages = []
        for field, msgs in errors.items():
            messages.extend(msgs)
        message_text = " ".join(messages)
        return Response({
            "statusCode": 400,
            "status": False,
            "message": message_text,
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)

class OwnershipTypeDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        uuids = request.data.get('id', [])

        # ✅ Case 1: Single delete (UUID in URL)
        if uuid:
            try:
                ownership = OwnershipType.objects.get(uuid=uuid, is_deleted=False)
                ownership.is_deleted = True
                ownership.save()
                return Response({
                    "statusCode": 204,
                    "status": True,
                    "message": "Ownership type deleted successfully",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            except OwnershipType.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Ownership type not found",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        # ✅ Case 2: Multiple delete (UUIDs in request body)
        if not uuids or not isinstance(uuids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide a list of UUIDs in 'uuids' field.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate UUIDs
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

        # Fetch ownership types that exist and are not deleted
        ownerships = OwnershipType.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = ownerships.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching ownership types found.",
                "data": {"invalid_uuids": invalid_uuids}
            }, status=status.HTTP_404_NOT_FOUND)

        # Soft delete
        ownerships.update(is_deleted=True)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} ownership type(s) deleted successfully.",
            "data": {"invalid_uuids": invalid_uuids}
        }, status=status.HTTP_200_OK)


class OwnershipTypeExportAPIView(APIView):
    # permission_classes = [IsAuthenticated]  # Uncomment and adjust as needed

    def get(self, request):
        format_type = request.GET.get('format', 'csv').lower()
        dataset = Dataset()
        dataset.headers = ['uuid', 'name', 'description', 'is_deleted', 'created_at', 'updated_at']

        for dept in OwnershipType.objects.all():
            dataset.append([
                str(dept.uuid),
                dept.name or '',  # Handle potential None
                dept.description or '',
                int(dept.is_deleted),
                dept.created_at.strftime("%Y-%m-%d %H:%M:%S") if dept.created_at else '',
                dept.updated_at.strftime("%Y-%m-%d %H:%M:%S") if dept.updated_at else ''
            ])

        if format_type == 'xlsx':
            data = XLSX().export_data(dataset)  # Returns bytes
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'departments.xlsx'
        else:
            data = CSV().export_data(dataset)  # Returns bytes (ensure UTF-8)
            content_type = 'text/csv; charset=utf-8'
            file_name = 'departments.csv'

        response = HttpResponse(data, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


class OwnershipTypeImportAPIView(APIView):
    
    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        dataset = Dataset()

        try:
            if format_type == 'xlsx':
                dataset.load(file.read(), format='xlsx')
            else:  # default CSV
                dataset.load(file.read().decode('utf-8'), format='csv')
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        for row in dataset.dict:
            OwnershipType.objects.update_or_create(
                name=row.get('name'),
                defaults={
                    'description': row.get('description', ''),
                    'is_deleted': row.get('is_deleted', False)
                }
            )

        return Response({
            "statusCode": 200,
            "status": True,
            'message': 'Import successful'}, status=status.HTTP_200_OK)
    








class StakeholderCategoryCreateAPIView(APIView):
    def post(self, request):
        serializer = StakeholderCategorySerializer(data=request.data)
        if serializer.is_valid():
            if StakeholderCategory.objects.filter(name=serializer.validated_data["name"]).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Stakeholder Category with this name already exists"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Stakeholder Category created successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        

        return Response({
            "statusCode": 400,
            "status": False,
            "message": next(iter(serializer.errors.values()))[0]
        }, status=status.HTTP_400_BAD_REQUEST)


class StakeholderCategoryListAPIView(APIView):    
    def get(self, request):
        search = request.GET.get('search', '').strip()
        queryset = StakeholderCategory.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )

        queryset = queryset.order_by('-created_at')

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = StakeholderCategorySerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)



class StakeholderCategoryDetailAPIView(APIView):
    def get(self, request, uuid):
        category = get_object_or_404(StakeholderCategory, uuid=uuid, is_deleted=False)
        serializer = StakeholderCategorySerializer(category)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Stakeholder Category retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class StakeholderCategoryUpdateAPIView(APIView):
    def put(self, request, uuid):
        category = get_object_or_404(StakeholderCategory, uuid=uuid, is_deleted=False)
        serializer = StakeholderCategorySerializer(category, data=request.data, partial=True)

        if serializer.is_valid():
            new_name = serializer.validated_data.get("name", category.name)
            if StakeholderCategory.objects.filter(name=new_name).exclude(uuid=uuid).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Stakeholder Category with this name already exists"
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Stakeholder Category updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "statusCode": 400,
            "status": False,
            "message": next(iter(serializer.errors.values()))[0]
        }, status=status.HTTP_400_BAD_REQUEST)


class StakeholderCategoryDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        uuids = request.data.get('id', [])

        if uuid:
            category = get_object_or_404(StakeholderCategory, uuid=uuid, is_deleted=False)
            category.is_deleted = True
            category.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Stakeholder Category deleted successfully",
                "data": None
            }, status=status.HTTP_200_OK)

        if not uuids or not isinstance(uuids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide a list of UUIDs in 'uuids' field.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate UUIDs
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

        # Fetch categories that exist and are not deleted
        categories = StakeholderCategory.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = categories.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching stakeholder categories found.",
                "data": {"invalid_uuids": invalid_uuids}
            }, status=status.HTTP_404_NOT_FOUND)

        # Soft delete
        categories.update(is_deleted=True)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} Stakeholder Category(s) deleted successfully.",
        
        }, status=status.HTTP_200_OK)



class StakeholderCategoryExportAPIView(APIView):
    # permission_classes = [IsAuthenticated]  # Uncomment and adjust as needed

    def get(self, request):
        format_type = request.GET.get('format', 'csv').lower()
        dataset = Dataset()
        dataset.headers = ['uuid', 'name', 'description', 'is_deleted', 'created_at', 'updated_at']

        for dept in StakeholderCategory.objects.all():
            dataset.append([
                str(dept.uuid),
                dept.name or '',  # Handle potential None
                dept.description or '',
                int(dept.is_deleted),
                dept.created_at.strftime("%Y-%m-%d %H:%M:%S") if dept.created_at else '',
                dept.updated_at.strftime("%Y-%m-%d %H:%M:%S") if dept.updated_at else ''
            ])

        if format_type == 'xlsx':
            data = XLSX().export_data(dataset)  # Returns bytes
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'departments.xlsx'
        else:
            data = CSV().export_data(dataset)  # Returns bytes (ensure UTF-8)
            content_type = 'text/csv; charset=utf-8'
            file_name = 'departments.csv'

        response = HttpResponse(data, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


class StakeholderCategoryImportAPIView(APIView):
    
    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        dataset = Dataset()

        try:
            if format_type == 'xlsx':
                dataset.load(file.read(), format='xlsx')
            else:  # default CSV
                dataset.load(file.read().decode('utf-8'), format='csv')
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        for row in dataset.dict:
            StakeholderCategory.objects.update_or_create(
                name=row.get('name'),
                defaults={
                    'description': row.get('description', ''),
                    'is_deleted': row.get('is_deleted', False)
                }
            )

        return Response({
            "statusCode": 200,
            "status": True,
            'message': 'Import successful'}, status=status.HTTP_200_OK)
    




class StakeholderTypeCreateAPIView(APIView):
    def post(self, request):
        serializer = StakeholderTypeSerializer(data=request.data)
        if serializer.is_valid():
            if StakeholderType.objects.filter(name=serializer.validated_data["name"]).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Stakeholder Type with this name already exists"
                }, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Stakeholder Type created successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            "statusCode": 400,
            "status": False,
            "message": next(iter(serializer.errors.values()))[0]
        }, status=status.HTTP_400_BAD_REQUEST)


class StakeholderTypeListAPIView(APIView):
    def get(self, request):
        search = request.GET.get('search', '').strip()
        queryset = StakeholderType.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )

        queryset = queryset.order_by('-created_at')

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = StakeholderTypeSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)


class StakeholderTypeDetailAPIView(APIView):
    def get(self, request, uuid):
        stakeholder_type = get_object_or_404(StakeholderType, uuid=uuid, is_deleted=False)
        serializer = StakeholderTypeSerializer(stakeholder_type)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Stakeholder Type retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class StakeholderTypeUpdateAPIView(APIView):
    def put(self, request, uuid):
        stakeholder_type = get_object_or_404(StakeholderType, uuid=uuid, is_deleted=False)
        serializer = StakeholderTypeSerializer(stakeholder_type, data=request.data, partial=True)
        if serializer.is_valid():
            new_name = serializer.validated_data.get("name", stakeholder_type.name)
            if StakeholderType.objects.filter(name=new_name).exclude(uuid=uuid).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Stakeholder Type with this name already exists"
                }, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Stakeholder Type updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            "statusCode": 400,
            "status": False,
            "message": next(iter(serializer.errors.values()))[0]
        }, status=status.HTTP_400_BAD_REQUEST)


class StakeholderTypeDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        uuids = request.data.get('id', [])

        # ✅ Case 1: Single delete (UUID in URL)
        if uuid:
            stakeholder_type = get_object_or_404(StakeholderType, uuid=uuid, is_deleted=False)
            stakeholder_type.is_deleted = True
            stakeholder_type.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Stakeholder Type deleted successfully",
                "data": None
            }, status=status.HTTP_200_OK)

        # ✅ Case 2: Multiple delete (UUIDs in request body)
        if not uuids or not isinstance(uuids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide a list of UUIDs in 'uuids' field.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate UUIDs
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

        # Fetch stakeholder types that exist and are not deleted
        stakeholder_types = StakeholderType.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = stakeholder_types.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching stakeholder types found.",
                "data": {"invalid_uuids": invalid_uuids}
            }, status=status.HTTP_404_NOT_FOUND)

        # Soft delete
        stakeholder_types.update(is_deleted=True)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} Stakeholder Type(s) deleted successfully.",
          
        }, status=status.HTTP_200_OK)



class AccreditationCategoryCreateAPIView(APIView):
    def post(self, request):
        serializer = AccreditationCategorySerializer(data=request.data)
        if serializer.is_valid():
            if AccreditationCategory.objects.filter(name=serializer.validated_data['name'], is_deleted=False).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Accreditation Category with this name already exists"
                }, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Accreditation Category created successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)


        return Response({
            "statusCode": 400,
            "status": False,
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class AccreditationCategoryListAPIView(APIView):    
    def get(self, request):
        search = request.GET.get('search', '').strip()
        queryset = AccreditationCategory.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )

        queryset = queryset.order_by('-created_at')

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = AccreditationCategorySerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)


class AccreditationCategoryRetrieveAPIView(APIView):
    def get(self, request, uuid):
        try:
            category = AccreditationCategory.objects.get(uuid=uuid, is_deleted=False)
        except AccreditationCategory.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Accreditation Category not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = AccreditationCategorySerializer(category)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Accreditation Category retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class AccreditationCategoryUpdateAPIView(APIView):
    def put(self, request, uuid):
        try:
            category = AccreditationCategory.objects.get(uuid=uuid, is_deleted=False)
        except AccreditationCategory.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Accreditation Category not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = AccreditationCategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            new_name = serializer.validated_data.get("name", category.name)
            if AccreditationCategory.objects.filter(name=new_name).exclude(uuid=uuid).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Accreditation Category with this name already exists"
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Accreditation Category updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "statusCode": 400,
            "status": False,
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class AccreditationCategoryDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        uuids = request.data.get('uuids', [])

        # ✅ Case 1: Single delete (UUID in URL)
        if uuid:
            try:
                category = AccreditationCategory.objects.get(uuid=uuid, is_deleted=False)
                category.is_deleted = True
                category.save()
                return Response({
                    "statusCode": 200,
                    "status": True,
                    "message": "Accreditation Category deleted successfully",
                    "data": None
                }, status=status.HTTP_200_OK)
            except AccreditationCategory.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Accreditation Category not found",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        # ✅ Case 2: Multiple delete (UUIDs in request body)
        if not uuids or not isinstance(uuids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide a list of UUIDs in 'uuids' field.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate UUIDs
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

        # Fetch categories that exist and are not deleted
        categories = AccreditationCategory.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = categories.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching accreditation categories found.",
                "data": {"invalid_uuids": invalid_uuids}
            }, status=status.HTTP_404_NOT_FOUND)

        # Soft delete
        categories.update(is_deleted=True)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} Accreditation Category(s) deleted successfully.",
            "data": {"invalid_uuids": invalid_uuids}
        }, status=status.HTTP_200_OK)



class AccreditationCategoryExportAPIView(APIView):
    # permission_classes = [IsAuthenticated]  # Uncomment and adjust as needed

    def get(self, request):
        format_type = request.GET.get('format', 'csv').lower()
        dataset = Dataset()
        dataset.headers = ['uuid', 'name', 'description', 'is_deleted', 'created_at', 'updated_at']

        for dept in StakeholderCategory.objects.all():
            dataset.append([
                str(dept.uuid),
                dept.name or '',  # Handle potential None
                dept.description or '',
                int(dept.is_deleted),
                dept.created_at.strftime("%Y-%m-%d %H:%M:%S") if dept.created_at else '',
                dept.updated_at.strftime("%Y-%m-%d %H:%M:%S") if dept.updated_at else ''
            ])

        if format_type == 'xlsx':
            data = XLSX().export_data(dataset)  # Returns bytes
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'departments.xlsx'
        else:
            data = CSV().export_data(dataset)  # Returns bytes (ensure UTF-8)
            content_type = 'text/csv; charset=utf-8'
            file_name = 'departments.csv'

        response = HttpResponse(data, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


class AccreditationCategoryImportAPIView(APIView):
    
    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        dataset = Dataset()

        try:
            if format_type == 'xlsx':
                dataset.load(file.read(), format='xlsx')
            else:  # default CSV
                dataset.load(file.read().decode('utf-8'), format='csv')
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        for row in dataset.dict:
            StakeholderCategory.objects.update_or_create(
                name=row.get('name'),
                defaults={
                    'description': row.get('description', ''),
                    'is_deleted': row.get('is_deleted', False)
                }
            )

        return Response({
            "statusCode": 200,
            "status": True,
            'message': 'Import successful'}, status=status.HTTP_200_OK)
    





#-------------------------------------------country---------------------------------


class AccreditationNameCreateAPIView(APIView):
    def post(self, request):
        serializer = AccreditationNameSerializer(data=request.data)
        if serializer.is_valid():
            full_name = serializer.validated_data["full_name"]
            short_name = serializer.validated_data["short_name"]

            if AccreditationName.objects.filter(full_name=full_name, is_deleted=False).exists() or \
               AccreditationName.objects.filter(short_name=short_name, is_deleted=False).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Accreditation Name with this full_name or short_name already exists"
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Accreditation Name created successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "statusCode": 400,
            "status": False,
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)



class AccreditationNameListAPIView(APIView):    
    def get(self, request):
        search = request.GET.get('search', '').strip()
        queryset = AccreditationName.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )

        queryset = queryset.order_by('-created_at')

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = AccreditationNameSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)

class AccreditationNameRetrieveAPIView(APIView):
    def get(self, request, uuid):
        try:
            name = AccreditationName.objects.get(uuid=uuid, is_deleted=False)
        except AccreditationName.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Accreditation Name not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = AccreditationNameSerializer(name)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Accreditation Name retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class AccreditationNameUpdateAPIView(APIView):
    def put(self, request, uuid):
        try:
            name = AccreditationName.objects.get(uuid=uuid, is_deleted=False)
        except AccreditationName.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Accreditation Name not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = AccreditationNameSerializer(name, data=request.data, partial=True)
        if serializer.is_valid():
            full_name = serializer.validated_data.get("full_name", name.full_name)
            short_name = serializer.validated_data.get("short_name", name.short_name)

            if AccreditationName.objects.filter(full_name=full_name).exclude(uuid=uuid).exists() or \
               AccreditationName.objects.filter(short_name=short_name).exclude(uuid=uuid).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Accreditation Name with this full_name or short_name already exists"
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Accreditation Name updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "statusCode": 400,
            "status": False,
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class AccreditationNameDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        uuids = request.data.get('uuids', [])

        # ✅ Case 1: Single delete (UUID in URL)
        if uuid:
            try:
                name = AccreditationName.objects.get(uuid=uuid, is_deleted=False)
            except AccreditationName.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Accreditation Name not found"
                }, status=status.HTTP_404_NOT_FOUND)

            name.is_deleted = True
            name.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Accreditation Name deleted successfully"
            }, status=status.HTTP_200_OK)

        # ✅ Case 2: Multiple delete (UUIDs in request body)
        if not uuids or not isinstance(uuids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide a list of UUIDs in 'uuids' field.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        names = AccreditationName.objects.filter(uuid__in=uuids, is_deleted=False)

        if not names.exists():
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching accreditation names found.",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        deleted_count = names.count()
        names.update(is_deleted=True)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{deleted_count} Accreditation Name(s) deleted successfully.",
            "data": None
        }, status=status.HTTP_200_OK)



#-------------------------------------------bankAccount---------------------------------


class BankAccountTypeCreateAPIView(APIView):
    def post(self, request):
        serializer = BankAccountTypeSerializer(data=request.data)
        if serializer.is_valid():
            if BankAccountType.objects.filter(name=serializer.validated_data['name'], is_deleted=False).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Bank Account  with this name already exists"
                }, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Bank Account created successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)


        return Response({
            "statusCode": 400,
            "status": False,
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class BankAccountTypeListAPIView(APIView):    
    def get(self, request):
        search = request.GET.get('search', '').strip()
        queryset = BankAccountType.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )

        queryset = queryset.order_by('-created_at')

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = BankAccountTypeSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)



class BankAccountTypeRetrieveAPIView(APIView):
    def get(self, request, uuid):
        try:
            bankaccount = BankAccountType.objects.get(uuid=uuid, is_deleted=False)
        except BankAccountType.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Bank Account  not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = BankAccountTypeSerializer(bankaccount)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Bank Account  retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class BankAccountTypeUpdateAPIView(APIView):
    def put(self, request, uuid):
        try:
            category = BankAccountType.objects.get(uuid=uuid, is_deleted=False)
        except BankAccountType.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Bank Account not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = BankAccountTypeSerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            new_name = serializer.validated_data.get("name", category.name)
            if BankAccountType.objects.filter(name=new_name).exclude(uuid=uuid).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Bank Account with this name already exists"
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Bank Account details updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "statusCode": 400,
            "status": False,
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class BankAccountTypeDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        uuids = request.data.get('uuids', [])

        # ✅ Case 1: Single delete (UUID in URL)
        if uuid:
            try:
                category = BankAccountType.objects.get(uuid=uuid, is_deleted=False)
                category.is_deleted = True
                category.save()
                return Response({
                    "statusCode": 200,
                    "status": True,
                    "message": "Bank Account Type deleted successfully",
                    "data": None
                }, status=status.HTTP_200_OK)
            except BankAccountType.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Bank Account Type not found",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        # ✅ Case 2: Multiple delete (UUIDs in request body)
        if not uuids or not isinstance(uuids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide a list of UUIDs in 'uuids' field.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate UUIDs
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

        # Fetch BankAccountTypes that exist and are not deleted
        categories = BankAccountType.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = categories.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching Bank Account Types found.",
                "data": {"invalid_uuids": invalid_uuids}
            }, status=status.HTTP_404_NOT_FOUND)

        # Soft delete
        categories.update(is_deleted=True)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} Bank Account Type(s) deleted successfully."
        }, status=status.HTTP_200_OK)



class BankAccountTypeExportAPIView(APIView):
    # permission_classes = [IsAuthenticated]  # Uncomment and adjust as needed

    def get(self, request):
        format_type = request.GET.get('format', 'csv').lower()
        dataset = Dataset()
        dataset.headers = ['uuid', 'name', 'description', 'is_deleted', 'created_at', 'updated_at']

        for dept in BankAccountType.objects.all():
            dataset.append([
                str(dept.uuid),
                dept.name or '',  # Handle potential None
                dept.description or '',
                int(dept.is_deleted),
                dept.created_at.strftime("%Y-%m-%d %H:%M:%S") if dept.created_at else '',
                dept.updated_at.strftime("%Y-%m-%d %H:%M:%S") if dept.updated_at else ''
            ])

        if format_type == 'xlsx':
            data = XLSX().export_data(dataset)  # Returns bytes
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'departments.xlsx'
        else:
            data = CSV().export_data(dataset)  # Returns bytes (ensure UTF-8)
            content_type = 'text/csv; charset=utf-8'
            file_name = 'departments.csv'

        response = HttpResponse(data, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


class BankAccountTypeImportAPIView(APIView):
    
    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        dataset = Dataset()

        try:
            if format_type == 'xlsx':
                dataset.load(file.read(), format='xlsx')
            else:  # default CSV
                dataset.load(file.read().decode('utf-8'), format='csv')
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        for row in dataset.dict:
            BankAccountType.objects.update_or_create(
                name=row.get('name'),
                defaults={
                    'description': row.get('description', ''),
                    'is_deleted': row.get('is_deleted', False)
                }
            )

        return Response({
            "statusCode": 200,
            "status": True,
            'message': 'Import successful'}, status=status.HTTP_200_OK)
    







#-------------------------------------------LicenseName---------------------------------

class LicenseNameCreateAPIView(APIView):
    def post(self, request):
        serializer = LicenseNameSerializer(data=request.data)
        if serializer.is_valid():
            full_name = serializer.validated_data.get("full_name")
            if LicenseName.objects.filter(full_name=full_name, is_deleted=False).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "License Name with this full name already exists"
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "License Name created successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "statusCode": 400,
            "status": False,
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)




class LicenseNameListAPIView(APIView):    
    def get(self, request):
        search = request.GET.get('search', '').strip()
        queryset = LicenseName.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )

        queryset = queryset.order_by('-created_at')

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = LicenseNameSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)



class LicenseNameRetrieveAPIView(APIView):
    def get(self, request, uuid):
        try:
            license_obj = LicenseName.objects.get(uuid=uuid, is_deleted=False)
        except LicenseName.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "License Name not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = LicenseNameSerializer(license_obj)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "License Name retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)



class LicenseNameUpdateAPIView(APIView):
    def put(self, request, uuid):
        try:
            license_obj = LicenseName.objects.get(uuid=uuid, is_deleted=False)
        except LicenseName.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "License Name not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = LicenseNameSerializer(license_obj, data=request.data, partial=True)
        if serializer.is_valid():
            new_full_name = serializer.validated_data.get("full_name", license_obj.full_name)
            if LicenseName.objects.filter(full_name=new_full_name).exclude(uuid=uuid).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "License Name with this full name already exists"
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "License Name updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "statusCode": 400,
            "status": False,
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)



class LicenseNameDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        uuids = request.data.get('uuids', [])

        # ✅ Case 1: Single delete (UUID in URL)
        if uuid:
            try:
                license_obj = LicenseName.objects.get(uuid=uuid, is_deleted=False)
            except LicenseName.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "License Name not found"
                }, status=status.HTTP_404_NOT_FOUND)

            license_obj.is_deleted = True
            license_obj.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "License Name deleted successfully"
            }, status=status.HTTP_200_OK)

        # ✅ Case 2: Multiple delete (UUIDs in request body)
        if not uuids or not isinstance(uuids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide a list of UUIDs in 'uuids' field.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        license_objs = LicenseName.objects.filter(uuid__in=uuids, is_deleted=False)

        if not license_objs.exists():
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching License Names found.",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        deleted_count = license_objs.count()
        license_objs.update(is_deleted=True)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{deleted_count} License Name(s) deleted successfully.",
            "data": None
        }, status=status.HTTP_200_OK)




#-------------------------------------------LeadSource---------------------------------




class LeadSourceCreateAPIView(APIView):
    def post(self, request):
        serializer = LeadSourceSerializer(data=request.data)
        if serializer.is_valid():
            if LeadSource.objects.filter(name=serializer.validated_data['name'], is_deleted=False).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Lead Source  with this name already exists"
                }, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Lead Source created successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)


        return Response({
            "statusCode": 400,
            "status": False,
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


    

class LeadSourceListAPIView(APIView):    
    def get(self, request):
        search = request.GET.get('search', '').strip()
        queryset = LeadSource.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )

        queryset = queryset.order_by('-created_at')

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = LeadSourceSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)


class LeadSourceRetrieveAPIView(APIView):
    def get(self, request, uuid):
        try:
            leadsource = LeadSource.objects.get(uuid=uuid, is_deleted=False)
        except LeadSource.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Lead Source not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = LeadSourceSerializer(leadsource)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Lead Source retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class LeadSourceUpdateAPIView(APIView):
    def put(self, request, uuid):
        try:
            category = LeadSource.objects.get(uuid=uuid, is_deleted=False)
        except LeadSource.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Lead Source not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = LeadSourceSerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            new_name = serializer.validated_data.get("name", category.name)
            if LeadSource.objects.filter(name=new_name).exclude(uuid=uuid).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Lead Source with this name already exists"
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Lead Source details updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "statusCode": 400,
            "status": False,
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class LeadSourceDeleteAPIView(APIView):
    def delete(self, request, uuid):
        try:
            category = LeadSource.objects.get(uuid=uuid, is_deleted=False)
        except LeadSource.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Lead Source Type  not found"
            }, status=status.HTTP_404_NOT_FOUND)

        category.is_deleted = True
        category.save()
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Lead Source Type  deleted successfully"
        }, status=status.HTTP_200_OK)
    



class LeadSourceExportAPIView(APIView):
    # permission_classes = [IsAuthenticated]  # Uncomment and adjust as needed

    def get(self, request):
        format_type = request.GET.get('format', 'csv').lower()
        dataset = Dataset()
        dataset.headers = ['uuid', 'name', 'description', 'is_deleted', 'created_at', 'updated_at']

        for dept in LeadSource.objects.all():
            dataset.append([
                str(dept.uuid),
                dept.name or '',  # Handle potential None
                dept.description or '',
                int(dept.is_deleted),
                dept.created_at.strftime("%Y-%m-%d %H:%M:%S") if dept.created_at else '',
                dept.updated_at.strftime("%Y-%m-%d %H:%M:%S") if dept.updated_at else ''
            ])

        if format_type == 'xlsx':
            data = XLSX().export_data(dataset)  # Returns bytes
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'departments.xlsx'
        else:
            data = CSV().export_data(dataset)  # Returns bytes (ensure UTF-8)
            content_type = 'text/csv; charset=utf-8'
            file_name = 'departments.csv'

        response = HttpResponse(data, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


class LeadSourceImportAPIView(APIView):
    
    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        dataset = Dataset()

        try:
            if format_type == 'xlsx':
                dataset.load(file.read(), format='xlsx')
            else:  # default CSV
                dataset.load(file.read().decode('utf-8'), format='csv')
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        for row in dataset.dict:
            LeadSource.objects.update_or_create(
                name=row.get('name'),
                defaults={
                    'description': row.get('description', ''),
                    'is_deleted': row.get('is_deleted', False)
                }
            )

        return Response({
            "statusCode": 200,
            "status": True,
            'message': 'Import successful'}, status=status.HTTP_200_OK)
    



#-------------------------------------------InterestLevel---------------------------------



class InterestLevelCreateAPIView(APIView):
    def post(self, request):
        serializer = InterestLevelSerializer(data=request.data)
        if serializer.is_valid():
            if InterestLevel.objects.filter(name=serializer.validated_data['name'], is_deleted=False).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Interest Level  with this name already exists"
                }, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Interest Level created successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)


        return Response({
            "statusCode": 400,
            "status": False,
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class InterestLevelListAPIView(APIView):    
    def get(self, request):
        search = request.GET.get('search', '').strip()
        queryset = InterestLevel.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )

        queryset = queryset.order_by('-created_at')

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = InterestLevelSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)

class InterestLevelRetrieveAPIView(APIView):
    def get(self, request, uuid):
        try:
            interestlevel = InterestLevel.objects.get(uuid=uuid, is_deleted=False)
        except InterestLevel.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Interest Level  not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = InterestLevelSerializer(interestlevel)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Interest Level  retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class InterestLevelUpdateAPIView(APIView):
    def put(self, request, uuid):
        try:
            category = InterestLevel.objects.get(uuid=uuid, is_deleted=False)
        except InterestLevel.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Interest Level not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = InterestLevelSerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            new_name = serializer.validated_data.get("name", category.name)
            if InterestLevel.objects.filter(name=new_name).exclude(uuid=uuid).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Interest Level with this name already exists"
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Interest Level details updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "statusCode": 400,
            "status": False,
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class InterestLevelDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        uuids = request.data.get('uuids', [])

        # ✅ Case 1: Single delete (UUID in URL)
        if uuid:
            try:
                interest = InterestLevel.objects.get(uuid=uuid, is_deleted=False)
                interest.is_deleted = True
                interest.save()
                return Response({
                    "statusCode": 200,
                    "status": True,
                    "message": "Interest Level deleted successfully",
                    "data": None
                }, status=status.HTTP_200_OK)
            except InterestLevel.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Interest Level not found",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        # ✅ Case 2: Multiple delete (UUIDs in request body)
        if not uuids or not isinstance(uuids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide a list of UUIDs in 'uuids' field.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate UUIDs
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

        # Fetch InterestLevel entries that exist and are not deleted
        interests = InterestLevel.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = interests.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching Interest Levels found.",
                "data": {"invalid_uuids": invalid_uuids}
            }, status=status.HTTP_404_NOT_FOUND)

        # Soft delete
        interests.update(is_deleted=True)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} Interest Level(s) deleted successfully.",
        
        }, status=status.HTTP_200_OK)


class InterestLevelExportAPIView(APIView):
    # permission_classes = [IsAuthenticated]  # Uncomment and adjust as needed

    def get(self, request):
        format_type = request.GET.get('format', 'csv').lower()
        dataset = Dataset()
        dataset.headers = ['uuid', 'name', 'description', 'is_deleted', 'created_at', 'updated_at']

        for dept in InterestLevel.objects.all():
            dataset.append([
                str(dept.uuid),
                dept.name or '',  # Handle potential None
                dept.description or '',
                int(dept.is_deleted),
                dept.created_at.strftime("%Y-%m-%d %H:%M:%S") if dept.created_at else '',
                dept.updated_at.strftime("%Y-%m-%d %H:%M:%S") if dept.updated_at else ''
            ])

        if format_type == 'xlsx':
            data = XLSX().export_data(dataset)  # Returns bytes
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'departments.xlsx'
        else:
            data = CSV().export_data(dataset)  # Returns bytes (ensure UTF-8)
            content_type = 'text/csv; charset=utf-8'
            file_name = 'departments.csv'

        response = HttpResponse(data, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


class InterestLevelImportAPIView(APIView):
    
    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        dataset = Dataset()

        try:
            if format_type == 'xlsx':
                dataset.load(file.read(), format='xlsx')
            else:  # default CSV
                dataset.load(file.read().decode('utf-8'), format='csv')
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        for row in dataset.dict:
            InterestLevel.objects.update_or_create(
                name=row.get('name'),
                defaults={
                    'description': row.get('description', ''),
                    'is_deleted': row.get('is_deleted', False)
                }
            )

        return Response({
            "statusCode": 200,
            "status": True,
            'message': 'Import successful'}, status=status.HTTP_200_OK)
    





#-------------------------------------------Priority---------------------------------


class PriorityCreateAPIView(APIView):
    def post(self, request):
        serializer = PrioritySerializer(data=request.data)
        if serializer.is_valid():
            if Priority.objects.filter(name=serializer.validated_data['name'], is_deleted=False).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Priority  with this name already exists"
                }, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Priority created successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)


        return Response({
            "statusCode": 400,
            "status": False,
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)



class PriorityListAPIView(APIView):    
    def get(self, request):
        search = request.GET.get('search', '').strip()
        queryset = Priority.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )

        queryset = queryset.order_by('-created_at')

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = PrioritySerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)


class PriorityRetrieveAPIView(APIView):
    def get(self, request, uuid):
        try:
            priority = Priority.objects.get(uuid=uuid, is_deleted=False)
        except Priority.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Priority  not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = PrioritySerializer(priority)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Priority  retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class PriorityUpdateAPIView(APIView):
    def put(self, request, uuid):
        try:
            category = Priority.objects.get(uuid=uuid, is_deleted=False)
        except Priority.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Priority not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = PrioritySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            new_name = serializer.validated_data.get("name", category.name)
            if Priority.objects.filter(name=new_name).exclude(uuid=uuid).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Priority with this name already exists"
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Priority details updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "statusCode": 400,
            "status": False,
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class PriorityDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        uuids = request.data.get('uuids', [])

        # ✅ Case 1: Single delete (UUID in URL)
        if uuid:
            try:
                priority = Priority.objects.get(uuid=uuid, is_deleted=False)
                priority.is_deleted = True
                priority.save()
                return Response({
                    "statusCode": 200,
                    "status": True,
                    "message": "Priority deleted successfully",
                    "data": None
                }, status=status.HTTP_200_OK)
            except Priority.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Priority not found",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        # ✅ Case 2: Multiple delete (UUIDs in request body)
        if not uuids or not isinstance(uuids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide a list of UUIDs in 'uuids' field.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate UUIDs
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

        # Fetch priorities that exist and are not deleted
        priorities = Priority.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = priorities.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching priorities found.",
                "data": {"invalid_uuids": invalid_uuids}
            }, status=status.HTTP_404_NOT_FOUND)

        # Soft delete
        priorities.update(is_deleted=True)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} Priority(s) deleted successfully.",
            
        }, status=status.HTTP_200_OK)


class PriorityExportAPIView(APIView):
    # permission_classes = [IsAuthenticated]  # Uncomment and adjust as needed

    def get(self, request):
        format_type = request.GET.get('format', 'csv').lower()
        dataset = Dataset()
        dataset.headers = ['uuid', 'name', 'description', 'is_deleted', 'created_at', 'updated_at']

        for dept in Priority.objects.all():
            dataset.append([
                str(dept.uuid),
                dept.name or '',  # Handle potential None
                dept.description or '',
                int(dept.is_deleted),
                dept.created_at.strftime("%Y-%m-%d %H:%M:%S") if dept.created_at else '',
                dept.updated_at.strftime("%Y-%m-%d %H:%M:%S") if dept.updated_at else ''
            ])

        if format_type == 'xlsx':
            data = XLSX().export_data(dataset)  # Returns bytes
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'departments.xlsx'
        else:
            data = CSV().export_data(dataset)  # Returns bytes (ensure UTF-8)
            content_type = 'text/csv; charset=utf-8'
            file_name = 'departments.csv'

        response = HttpResponse(data, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


class PriorityImportAPIView(APIView):
    
    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        dataset = Dataset()

        try:
            if format_type == 'xlsx':
                dataset.load(file.read(), format='xlsx')
            else:  # default CSV
                dataset.load(file.read().decode('utf-8'), format='csv')
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        for row in dataset.dict:
            Priority.objects.update_or_create(
                name=row.get('name'),
                defaults={
                    'description': row.get('description', ''),
                    'is_deleted': row.get('is_deleted', False)
                }
            )

        return Response({
            "statusCode": 200,
            "status": True,
            'message': 'Import successful'}, status=status.HTTP_200_OK)
    




#-------------------------------------------Tags---------------------------------


class TagsCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    def post(self, request):
        serializer = TagsSerializer(data=request.data)
        if serializer.is_valid():
            if Tags.objects.filter(name=serializer.validated_data['name'], is_deleted=False).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Tags  with this name already exists"
                }, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Tags created successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)


        return Response({
            "statusCode": 400,
            "status": False,
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)




class TagsListAPIView(APIView):    
    def get(self, request):
        search = request.GET.get('search', '').strip()
        queryset = Tags.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )

        queryset = queryset.order_by('-created_at')

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = TagsSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)


class TagsRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    def get(self, request, uuid):
        try:
            tag = Tags.objects.get(uuid=uuid, is_deleted=False)
        except Tags.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Tags  not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = TagsSerializer(tag)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Tags  retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class TagsUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    def put(self, request, uuid):
        try:
            category = Tags.objects.get(uuid=uuid, is_deleted=False)
        except Tags.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Tags not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = TagsSerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            new_name = serializer.validated_data.get("name", category.name)
            if Tags.objects.filter(name=new_name).exclude(uuid=uuid).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Tags with this name already exists"
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Tags details updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "statusCode": 400,
            "status": False,
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class TagsDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        uuids = request.data.get('uuids', [])

        # ✅ Case 1: Single delete (UUID in URL)
        if uuid:
            try:
                tag = Tags.objects.get(uuid=uuid, is_deleted=False)
                tag.is_deleted = True
                tag.save()
                return Response({
                    "statusCode": 200,
                    "status": True,
                    "message": "Tag deleted successfully",
                    "data": None
                }, status=status.HTTP_200_OK)
            except Tags.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Tag not found",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        # ✅ Case 2: Multiple delete (UUIDs in request body)
        if not uuids or not isinstance(uuids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide a list of UUIDs in 'uuids' field.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate UUIDs
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

        # Fetch Tags that exist and are not deleted
        tags = Tags.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = tags.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching Tags found.",
                "data": {"invalid_uuids": invalid_uuids}
            }, status=status.HTTP_404_NOT_FOUND)

        # Soft delete
        tags.update(is_deleted=True)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} Tag(s) deleted successfully.",
            
        }, status=status.HTTP_200_OK)
    

class TagsExportAPIView(APIView):
    # permission_classes = [IsAuthenticated]  # Uncomment and adjust as needed

    def get(self, request):
        format_type = request.GET.get('format', 'csv').lower()
        dataset = Dataset()
        dataset.headers = ['uuid', 'name', 'description', 'is_deleted', 'created_at', 'updated_at']

        for dept in Tags.objects.all():
            dataset.append([
                str(dept.uuid),
                dept.name or '',  # Handle potential None
                dept.description or '',
                int(dept.is_deleted),
                dept.created_at.strftime("%Y-%m-%d %H:%M:%S") if dept.created_at else '',
                dept.updated_at.strftime("%Y-%m-%d %H:%M:%S") if dept.updated_at else ''
            ])

        if format_type == 'xlsx':
            data = XLSX().export_data(dataset)  # Returns bytes
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'departments.xlsx'
        else:
            data = CSV().export_data(dataset)  # Returns bytes (ensure UTF-8)
            content_type = 'text/csv; charset=utf-8'
            file_name = 'departments.csv'

        response = HttpResponse(data, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


class TagsImportAPIView(APIView):
    
    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        dataset = Dataset()

        try:
            if format_type == 'xlsx':
                dataset.load(file.read(), format='xlsx')
            else:  # default CSV
                dataset.load(file.read().decode('utf-8'), format='csv')
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        for row in dataset.dict:
            Tags.objects.update_or_create(
                name=row.get('name'),
                defaults={
                    'description': row.get('description', ''),
                    'is_deleted': row.get('is_deleted', False)
                }
            )

        return Response({
            "statusCode": 200,
            "status": True,
            'message': 'Import successful'}, status=status.HTTP_200_OK)
    




#-------------------------------------------ActivityType---------------------------------



class ActivityTypeCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    def post(self, request):
        serializer = ActivityTypeSerializer(data=request.data)
        if serializer.is_valid():
            if ActivityType.objects.filter(name=serializer.validated_data['name'], is_deleted=False).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Activity Type  with this name already exists"
                }, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Activity Type created successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)


        return Response({
            "statusCode": 400,
            "status": False,
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)



class ActivityTypeListAPIView(APIView):    
    def get(self, request):
        search = request.GET.get('search', '').strip()
        queryset = ActivityType.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )

        queryset = queryset.order_by('-created_at')

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = ActivityTypeSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)
    
class ActivityTypeRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    def get(self, request, uuid):
        try:
            activitytype = ActivityType.objects.get(uuid=uuid, is_deleted=False)
        except ActivityType.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Activity Type  not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = ActivityTypeSerializer(activitytype)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Activity Type  retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class ActivityTypeUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    def put(self, request, uuid):
        try:
            category = ActivityType.objects.get(uuid=uuid, is_deleted=False)
        except ActivityType.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Activity Type not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = ActivityTypeSerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            new_name = serializer.validated_data.get("name", category.name)
            if ActivityType.objects.filter(name=new_name).exclude(uuid=uuid).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Activity Type with this name already exists"
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Activity Type details updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "statusCode": 400,
            "status": False,
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class ActivityTypeDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        uuids = request.data.get('uuids', [])

        # ✅ Case 1: Single delete (UUID in URL)
        if uuid:
            try:
                activity = ActivityType.objects.get(uuid=uuid, is_deleted=False)
                activity.is_deleted = True
                activity.save()
                return Response({
                    "statusCode": 200,
                    "status": True,
                    "message": "Activity Type deleted successfully",
                    "data": None
                }, status=status.HTTP_200_OK)
            except ActivityType.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Activity Type not found",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        # ✅ Case 2: Multiple delete (UUIDs in request body)
        if not uuids or not isinstance(uuids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide a list of UUIDs in 'uuids' field.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate UUIDs
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

        # Fetch ActivityType entries that exist and are not deleted
        activities = ActivityType.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = activities.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching Activity Types found.",
                "data": {"invalid_uuids": invalid_uuids}
            }, status=status.HTTP_404_NOT_FOUND)

        # Soft delete
        activities.update(is_deleted=True)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} Activity Type(s) deleted successfully.",
            
        }, status=status.HTTP_200_OK)

class ActivityTypeExportAPIView(APIView):
    # permission_classes = [IsAuthenticated]  # Uncomment and adjust as needed

    def get(self, request):
        format_type = request.GET.get('format', 'csv').lower()
        dataset = Dataset()
        dataset.headers = ['uuid', 'name', 'description', 'is_deleted', 'created_at', 'updated_at']

        for dept in ActivityType.objects.all():
            dataset.append([
                str(dept.uuid),
                dept.name or '',  # Handle potential None
                dept.description or '',
                int(dept.is_deleted),
                dept.created_at.strftime("%Y-%m-%d %H:%M:%S") if dept.created_at else '',
                dept.updated_at.strftime("%Y-%m-%d %H:%M:%S") if dept.updated_at else ''
            ])

        if format_type == 'xlsx':
            data = XLSX().export_data(dataset)  # Returns bytes
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'departments.xlsx'
        else:
            data = CSV().export_data(dataset)  # Returns bytes (ensure UTF-8)
            content_type = 'text/csv; charset=utf-8'
            file_name = 'departments.csv'

        response = HttpResponse(data, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


class ActivityTypeImportAPIView(APIView):
    
    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        dataset = Dataset()

        try:
            if format_type == 'xlsx':
                dataset.load(file.read(), format='xlsx')
            else:  # default CSV
                dataset.load(file.read().decode('utf-8'), format='csv')
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        for row in dataset.dict:
            ActivityType.objects.update_or_create(
                name=row.get('name'),
                defaults={
                    'description': row.get('description', ''),
                    'is_deleted': row.get('is_deleted', False)
                }
            )

        return Response({
            "statusCode": 200,
            "status": True,
            'message': 'Import successful'}, status=status.HTTP_200_OK)
    




#-------------------------------------------LostReasonSerializer---------------------------------


class LostReasonCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    def post(self, request):
        serializer = LostReasonSerializer(data=request.data)
        if serializer.is_valid():
            if LostReason.objects.filter(name=serializer.validated_data['name'], is_deleted=False).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Lost Reason  with this name already exists"
                }, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Lost Reason created successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)


        return Response({
            "statusCode": 400,
            "status": False,
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class LostReasonListAPIView(APIView):    
    def get(self, request):
        search = request.GET.get('search', '').strip()
        queryset = LostReason.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )

        queryset = queryset.order_by('-created_at')

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = LostReasonSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)


class LostReasonRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    def get(self, request, uuid):
        try:
            lostreason = LostReason.objects.get(uuid=uuid, is_deleted=False)
        except LostReason.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Lost Reason  not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = LostReasonSerializer(lostreason)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Lost Reason  retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class LostReasonUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    def put(self, request, uuid):
        try:
            category = LostReason.objects.get(uuid=uuid, is_deleted=False)
        except LostReason.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Lost Reason not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = LostReasonSerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            new_name = serializer.validated_data.get("name", category.name)
            if LostReason.objects.filter(name=new_name).exclude(uuid=uuid).exists():
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Lost Reason with this name already exists"
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Lost Reason  details updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "statusCode": 400,
            "status": False,
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)



class LostReasonDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, uuid=None):
        uuids = request.data.get('uuids', [])

        # ✅ Case 1: Single delete (UUID in URL)
        if uuid:
            try:
                reason = LostReason.objects.get(uuid=uuid, is_deleted=False)
                reason.is_deleted = True
                reason.save()
                return Response({
                    "statusCode": 200,
                    "status": True,
                    "message": "Lost Reason deleted successfully",
                    "data": None
                }, status=status.HTTP_200_OK)
            except LostReason.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status": False,
                    "message": "Lost Reason not found",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        # ✅ Case 2: Multiple delete (UUIDs in request body)
        if not uuids or not isinstance(uuids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide a list of UUIDs in 'uuids' field.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate UUIDs
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

        # Fetch LostReason entries that exist and are not deleted
        reasons = LostReason.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = reasons.count()

        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching Lost Reasons found.",
                "data": {"invalid_uuids": invalid_uuids}
            }, status=status.HTTP_404_NOT_FOUND)

        # Soft delete
        reasons.update(is_deleted=True)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} Lost Reason(s) deleted successfully.",
          
        }, status=status.HTTP_200_OK)

class LostReasonExportAPIView(APIView):
    # permission_classes = [IsAuthenticated]  # Uncomment and adjust as needed

    def get(self, request):
        format_type = request.GET.get('format', 'csv').lower()
        dataset = Dataset()
        dataset.headers = ['uuid', 'name', 'description', 'is_deleted', 'created_at', 'updated_at']

        for dept in LostReason.objects.all():
            dataset.append([
                str(dept.uuid),
                dept.name or '',  # Handle potential None
                dept.description or '',
                int(dept.is_deleted),
                dept.created_at.strftime("%Y-%m-%d %H:%M:%S") if dept.created_at else '',
                dept.updated_at.strftime("%Y-%m-%d %H:%M:%S") if dept.updated_at else ''
            ])

        if format_type == 'xlsx':
            data = XLSX().export_data(dataset)  # Returns bytes
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'departments.xlsx'
        else:
            data = CSV().export_data(dataset)  # Returns bytes (ensure UTF-8)
            content_type = 'text/csv; charset=utf-8'
            file_name = 'departments.csv'

        response = HttpResponse(data, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


class LostReasonImportAPIView(APIView):
    
    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        dataset = Dataset()

        try:
            if format_type == 'xlsx':
                dataset.load(file.read(), format='xlsx')
            else:  # default CSV
                dataset.load(file.read().decode('utf-8'), format='csv')
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        for row in dataset.dict:
            LostReason.objects.update_or_create(
                name=row.get('name'),
                defaults={
                    'description': row.get('description', ''),
                    'is_deleted': row.get('is_deleted', False)
                }
            )

        return Response({
            "statusCode": 200,
            "status": True,
            'message': 'Import successful'}, status=status.HTTP_200_OK)
    







# -------------------- EducationLevelCode -------------------- #
class EducationLevelCodeCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        level_code = request.data.get("Levelcode", "").strip()

        existing = EducationLevelCode.objects.filter(Levelcode__iexact=level_code).first()

        if existing:
            if getattr(existing, 'is_deleted', False):
                existing.is_deleted = False
                existing.description = request.data.get("description", existing.description)
                existing.save()
                serializer = EducationLevelCodeSerializer(existing)
                return Response({
                    "statusCode": 200,
                    "status": True,
                    "message": "Education Level Code reactivated successfully",
                    "data": serializer.data
                })
            else:
                return Response({
                    "statusCode": 400,
                    "status": False,
                    "message": "Education Level Code with this code already exists."
                }, status=status.HTTP_400_BAD_REQUEST)

        serializer = EducationLevelCodeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Education Level Code created successfully",
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
        }, status=status.HTTP_400_BAD_REQUEST)


class EducationLevelCodeRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = EducationLevelCode.objects.get(uuid=uuid, is_deleted=False)
        except EducationLevelCode.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Education Level Code not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = EducationLevelCodeSerializer(obj)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Education Level Code retrieved successfully",
            "data": serializer.data
        })


class EducationLevelCodeUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = EducationLevelCode.objects.get(uuid=uuid, is_deleted=False)
        except EducationLevelCode.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Education Level Code not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = EducationLevelCodeSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Education Level Code updated successfully",
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


class EducationLevelCodeDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        uuids = request.data.get('id', [])
        if not uuids or not isinstance(uuids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide a list of UUIDs in 'id' field.",
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

        objs = EducationLevelCode.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = objs.count()
        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching Education Level Codes found.",
                "data": {"invalid_uuids": invalid_uuids}
            }, status=status.HTTP_404_NOT_FOUND)

        objs.update(is_deleted=True)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} Education Level Code(s) deleted successfully.",
        })


class EducationLevelCodeExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'csv').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_list = [f.strip() for f in fields.split(',')] if fields else ['uuid', 'Levelcode', 'description', 'created_at', 'updated_at']

        queryset = EducationLevelCode.objects.filter(uuid__in=uuids) if uuids else EducationLevelCode.objects.all()

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
            file_name = 'education_level_codes.xlsx'
        else:
            data = CSV().export_data(dataset)
            content_type = 'text/csv; charset=utf-8'
            file_name = 'education_level_codes.csv'

        response = HttpResponse(data, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


class EducationLevelCodeImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        dataset = Dataset()
        duplicate_codes = []

        try:
            if format_type == 'xlsx':
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({'error': 'Please provide sheet_name', 'available_sheets': available_sheets},
                                    status=status.HTTP_400_BAD_REQUEST)

                if sheet_name not in available_sheets:
                    return Response({'error': f'Sheet "{sheet_name}" not found', 'available_sheets': available_sheets},
                                    status=status.HTTP_400_BAD_REQUEST)

                ws = wb[sheet_name]
                headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                for row in ws.iter_rows(min_row=2, values_only=True):
                    data = dict(zip(headers, row))
                    code = str(data.get('Levelcode')).strip() if data.get('Levelcode') else None
                    if not code:
                        continue
                    if EducationLevelCode.objects.filter(Levelcode__iexact=code).exists():
                        duplicate_codes.append(code)
                        continue
                    EducationLevelCode.objects.create(
                        Levelcode=code,
                        description=data.get('description', ''),
                        is_deleted=data.get('is_deleted', False)
                    )
            else:  # CSV
                dataset.load(file.read().decode('utf-8'), format='csv')
                for row in dataset.dict:
                    code = str(row.get('Levelcode')).strip() if row.get('Levelcode') else None
                    if not code:
                        continue
                    if EducationLevelCode.objects.filter(Levelcode__iexact=code).exists():
                        duplicate_codes.append(code)
                        continue
                    EducationLevelCode.objects.create(
                        Levelcode=code,
                        description=row.get('description', ''),
                        is_deleted=row.get('is_deleted', False)
                    )

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": list(set(duplicate_codes)),
            'message': f'Sheet "{sheet_name}" imported successfully' if sheet_name else 'Import successful'
        })




# -------------------- EducationLevel -------------------- #
class EducationLevelCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        educationlevel_name = request.data.get('educationlevel', '').strip()

        # Check for duplicate
        if EducationLevel.objects.filter(educationlevel__iexact=educationlevel_name).exists():
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "This Education Level with the selected Level Code already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        # If no duplicate, create new
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

    def delete(self, request):
        uuids = request.data.get('id', [])
        if not uuids or not isinstance(uuids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide a list of UUIDs in 'id' field.",
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

        objs = EducationLevel.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = objs.count()
        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching Education Levels found.",
                "data": {"invalid_uuids": invalid_uuids}
            }, status=status.HTTP_404_NOT_FOUND)

        objs.update(is_deleted=True)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} Education Level(s) deleted successfully.",
        })


class EducationLevelExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'csv').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_list = [f.strip() for f in fields.split(',')] if fields else [
            'uuid', 'level_code', 'level_code_detail', 'educationlevel', 'description', 'is_deleted', 'created_at', 'updated_at'
        ]

        queryset = EducationLevel.objects.filter(uuid__in=uuids) if uuids else EducationLevel.objects.all()

        dataset = Dataset()
        dataset.headers = field_list

        for obj in queryset:
            row = []
            for field in field_list:
                if field == 'level_code_detail':
                    value = obj.level_code.Levelcode if obj.level_code else ''
                else:
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
            file_name = 'education_levels.xlsx'
        else:
            data = CSV().export_data(dataset)
            content_type = 'text/csv; charset=utf-8'
            file_name = 'education_levels.csv'

        response = HttpResponse(data, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


class EducationLevelImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        dataset = Dataset()
        duplicate_entries = []

        try:
            if format_type == 'xlsx':
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({'error': 'Please provide sheet_name', 'available_sheets': available_sheets},
                                    status=status.HTTP_400_BAD_REQUEST)

                if sheet_name not in available_sheets:
                    return Response({'error': f'Sheet "{sheet_name}" not found', 'available_sheets': available_sheets},
                                    status=status.HTTP_400_BAD_REQUEST)

                ws = wb[sheet_name]
                headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                for row in ws.iter_rows(min_row=2, values_only=True):
                    data = dict(zip(headers, row))
                    code_id = data.get('level_code')
                    if not code_id or not EducationLevelCode.objects.filter(id=code_id).exists():
                        continue
                    if EducationLevel.objects.filter(level_code_id=code_id, educationlevel=data.get('educationlevel', '')).exists():
                        duplicate_entries.append(code_id)
                        continue
                    EducationLevel.objects.create(
                        level_code_id=code_id,
                        educationlevel=data.get('educationlevel', ''),
                        description=data.get('description', ''),
                        is_deleted=data.get('is_deleted', False)
                    )
            else:  # CSV
                dataset.load(file.read().decode('utf-8'), format='csv')
                for row in dataset.dict:
                    code_id = row.get('level_code')
                    if not code_id or not EducationLevelCode.objects.filter(id=code_id).exists():
                        continue
                    if EducationLevel.objects.filter(level_code_id=code_id, educationlevel=row.get('educationlevel', '')).exists():
                        duplicate_entries.append(code_id)
                        continue
                    EducationLevel.objects.create(
                        level_code_id=code_id,
                        educationlevel=row.get('educationlevel', ''),
                        description=row.get('description', ''),
                        is_deleted=row.get('is_deleted', False)
                    )

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": list(set(duplicate_entries)),
            'message': f'Sheet "{sheet_name}" imported successfully' if sheet_name else 'Import successful'
        })



#----------------------------EducationDuration----------------------
class EducationDurationCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        educationlevel_id = request.data.get('educationlevel')
        duration = request.data.get('durations')

        # Prevent duplicates (same level + duration)
        if EducationDuration.objects.filter(educationlevel_id=educationlevel_id, durations=duration).exists():
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "This Education Duration for the selected Education Level already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = EducationDurationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Education Duration created successfully",
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


# -------------------- RETRIEVE -------------------- #
class EducationDurationRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = EducationDuration.objects.get(uuid=uuid, is_deleted=False)
        except EducationDuration.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Education Duration not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = EducationDurationSerializer(obj)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Education Duration retrieved successfully",
            "data": serializer.data
        })


# -------------------- UPDATE -------------------- #
class EducationDurationUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = EducationDuration.objects.get(uuid=uuid, is_deleted=False)
        except EducationDuration.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Education Duration not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        # Prevent duplicates during update
        educationlevel_id = request.data.get('educationlevel')
        duration = request.data.get('durations')
        if EducationDuration.objects.filter(
            educationlevel_id=educationlevel_id, 
            durations=duration
        ).exclude(uuid=uuid).exists():
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "This Education Duration for the selected Education Level already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = EducationDurationSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Education Duration updated successfully",
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


# -------------------- DELETE -------------------- #
class EducationDurationDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        uuids = request.data.get('id', [])
        if not uuids or not isinstance(uuids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide a list of UUIDs in 'id' field.",
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

        objs = EducationDuration.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = objs.count()
        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching Education Durations found.",
                "data": {"invalid_uuids": invalid_uuids}
            }, status=status.HTTP_404_NOT_FOUND)

        objs.update(is_deleted=True)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} Education Duration(s) deleted successfully.",
        })


# -------------------- EXPORT -------------------- #
class EducationDurationExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'csv').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_list = [f.strip() for f in fields.split(',')] if fields else [
            'uuid', 'educationlevel', 'educationlevel_detail', 'durations', 'description', 'is_deleted', 'created_at', 'updated_at'
        ]

        queryset = EducationDuration.objects.filter(uuid__in=uuids) if uuids else EducationDuration.objects.all()

        dataset = Dataset()
        dataset.headers = field_list

        for obj in queryset:
            row = []
            for field in field_list:
                if field == 'educationlevel_detail':
                    value = obj.educationlevel.educationlevel if obj.educationlevel else ''
                else:
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
            file_name = 'education_durations.xlsx'
        else:
            data = CSV().export_data(dataset)
            content_type = 'text/csv; charset=utf-8'
            file_name = 'education_durations.csv'

        response = HttpResponse(data, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


# -------------------- IMPORT -------------------- #
class EducationDurationImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        dataset = Dataset()
        duplicate_entries = []

        try:
            if format_type == 'xlsx':
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({'error': 'Please provide sheet_name', 'available_sheets': available_sheets},
                                    status=status.HTTP_400_BAD_REQUEST)

                if sheet_name not in available_sheets:
                    return Response({'error': f'Sheet "{sheet_name}" not found', 'available_sheets': available_sheets},
                                    status=status.HTTP_400_BAD_REQUEST)

                ws = wb[sheet_name]
                headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                for row in ws.iter_rows(min_row=2, values_only=True):
                    data = dict(zip(headers, row))
                    level_id = data.get('educationlevel')
                    duration_val = data.get('durations')
                    if EducationDuration.objects.filter(educationlevel_id=level_id, durations=duration_val).exists():
                        duplicate_entries.append(f"{level_id}-{duration_val}")
                        continue
                    EducationDuration.objects.create(
                        educationlevel_id=level_id,
                        durations=duration_val,
                        description=data.get('description', ''),
                        is_deleted=data.get('is_deleted', False)
                    )
            else:  # CSV
                dataset.load(file.read().decode('utf-8'), format='csv')
                for row in dataset.dict:
                    level_id = row.get('educationlevel')
                    duration_val = row.get('durations')
                    if EducationDuration.objects.filter(educationlevel_id=level_id, durations=duration_val).exists():
                        duplicate_entries.append(f"{level_id}-{duration_val}")
                        continue
                    EducationDuration.objects.create(
                        educationlevel_id=level_id,
                        durations=duration_val,
                        description=row.get('description', ''),
                        is_deleted=row.get('is_deleted', False)
                    )

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": list(set(duplicate_entries)),
            'message': f'Sheet "{sheet_name}" imported successfully' if sheet_name else 'Import successful'
        })



# -------------------- Studymainarea -------------------- #
class StudymainareaCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        mainarea_name = request.data.get('Mainarea', '').strip()

        # Prevent duplicates
        if Studymainarea.objects.filter(Mainarea__iexact=mainarea_name).exists():
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Studymainarea with this name already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = StudymainareaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Studymainarea created successfully",
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


# -------------------- RETRIEVE -------------------- #
class StudymainareaRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = Studymainarea.objects.get(uuid=uuid, is_deleted=False)
        except Studymainarea.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Studymainarea not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = StudymainareaSerializer(obj)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Studymainarea retrieved successfully",
            "data": serializer.data
        })


# -------------------- UPDATE -------------------- #
class StudymainareaUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = Studymainarea.objects.get(uuid=uuid, is_deleted=False)
        except Studymainarea.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Studymainarea not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        # Prevent duplicates
        mainarea_name = request.data.get('Mainarea', '').strip()
        if Studymainarea.objects.filter(Mainarea__iexact=mainarea_name).exclude(uuid=uuid).exists():
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Studymainarea with this name already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = StudymainareaSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Studymainarea updated successfully",
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


# -------------------- DELETE -------------------- #
class StudymainareaDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        uuids = request.data.get('id', [])
        if not uuids or not isinstance(uuids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide a list of UUIDs in 'id' field.",
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

        objs = Studymainarea.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = objs.count()
        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching Studymainarea found.",
                "data": {"invalid_uuids": invalid_uuids}
            }, status=status.HTTP_404_NOT_FOUND)

        objs.update(is_deleted=True)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} Studymainarea(s) deleted successfully.",
        })


# -------------------- EXPORT -------------------- #
class StudymainareaExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'csv').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_list = [f.strip() for f in fields.split(',')] if fields else [
            'uuid', 'Mainarea', 'description', 'is_deleted', 'created_at', 'updated_at'
        ]

        queryset = Studymainarea.objects.filter(uuid__in=uuids) if uuids else Studymainarea.objects.all()

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
            file_name = 'studymainareas.xlsx'
        else:
            data = CSV().export_data(dataset)
            content_type = 'text/csv; charset=utf-8'
            file_name = 'studymainareas.csv'

        response = HttpResponse(data, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


# -------------------- IMPORT -------------------- #
class StudymainareaImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        dataset = Dataset()
        duplicate_entries = []

        try:
            if format_type == 'xlsx':
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({'error': 'Please provide sheet_name', 'available_sheets': available_sheets},
                                    status=status.HTTP_400_BAD_REQUEST)

                if sheet_name not in available_sheets:
                    return Response({'error': f'Sheet "{sheet_name}" not found', 'available_sheets': available_sheets},
                                    status=status.HTTP_400_BAD_REQUEST)

                ws = wb[sheet_name]
                headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                for row in ws.iter_rows(min_row=2, values_only=True):
                    data = dict(zip(headers, row))
                    mainarea_name = data.get('Mainarea')
                    if Studymainarea.objects.filter(Mainarea__iexact=mainarea_name).exists():
                        duplicate_entries.append(mainarea_name)
                        continue
                    Studymainarea.objects.create(
                        Mainarea=mainarea_name,
                        description=data.get('description', ''),
                        is_deleted=data.get('is_deleted', False)
                    )
            else:  # CSV
                dataset.load(file.read().decode('utf-8'), format='csv')
                for row in dataset.dict:
                    mainarea_name = row.get('Mainarea')
                    if Studymainarea.objects.filter(Mainarea__iexact=mainarea_name).exists():
                        duplicate_entries.append(mainarea_name)
                        continue
                    Studymainarea.objects.create(
                        Mainarea=mainarea_name,
                        description=row.get('description', ''),
                        is_deleted=row.get('is_deleted', False)
                    )

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": list(set(duplicate_entries)),
            'message': f'Sheet "{sheet_name}" imported successfully' if sheet_name else 'Import successful'
        })






# -------------------- Studymajor -------------------- #
class StudymajorareaCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        mainarea_id = request.data.get('mainarea_id')
        majorarea_name = request.data.get('Majorarea', '').strip()

       
        if Studymajorarea.objects.filter(mainarea_id=mainarea_id, Majorarea__iexact=majorarea_name).exists():
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "This Majorarea for the selected Mainarea already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = StudymajorareaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Studymajorarea created successfully",
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
        })

class StudymajorareaRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, uuid):
        try:
            obj = Studymajorarea.objects.get(uuid=uuid, is_deleted=False)
        except Studymajorarea.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Studymajorarea not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = StudymajorareaSerializer(obj)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Studymajorarea retrieved successfully",
            "data": serializer.data
        })


class StudymajorareaUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = Studymajorarea.objects.get(uuid=uuid, is_deleted=False)
        except Studymajorarea.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Studymajorarea not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        mainarea_id = request.data.get('mainarea_id')
        majorarea_name = request.data.get('Majorarea', '').strip()

        if Studymajorarea.objects.filter(mainarea_id=mainarea_id, Majorarea__iexact=majorarea_name).exclude(uuid=uuid).exists():
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "This Majorarea for the selected Mainarea already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = StudymajorareaSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Studymajorarea updated successfully",
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
        })


class StudymajorareaDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        uuids = request.data.get('id', [])
        if not uuids or not isinstance(uuids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide a list of UUIDs in 'id' field.",
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

        objs = Studymajorarea.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = objs.count()
        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching Studymajorarea found.",
                "data": {"invalid_uuids": invalid_uuids}
            }, status=status.HTTP_404_NOT_FOUND)

        objs.update(is_deleted=True)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} Studymajorarea(s) deleted successfully.",
        })


# -------------------- EXPORT -------------------- #
class StudymajorareaExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'csv').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_list = [f.strip() for f in fields.split(',')] if fields else [
            'uuid', 'mainarea', 'Majorarea', 'description', 'is_deleted', 'created_at', 'updated_at'
        ]

        queryset = Studymajorarea.objects.filter(uuid__in=uuids) if uuids else Studymajorarea.objects.all()

        dataset = Dataset()
        dataset.headers = field_list

        for obj in queryset:
            row = []
            for field in field_list:
                if field == 'mainarea':
                    value = obj.mainarea.Mainarea if obj.mainarea else ''
                else:
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
            file_name = 'studymajorareas.xlsx'
        else:
            data = CSV().export_data(dataset)
            content_type = 'text/csv; charset=utf-8'
            file_name = 'studymajorareas.csv'

        response = HttpResponse(data, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


# -------------------- IMPORT -------------------- #
class StudymajorareaImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')

        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        dataset = Dataset()
        duplicate_entries = []

        try:
            if format_type == 'xlsx':
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({'error': 'Please provide sheet_name', 'available_sheets': available_sheets},
                                    status=status.HTTP_400_BAD_REQUEST)

                if sheet_name not in available_sheets:
                    return Response({'error': f'Sheet "{sheet_name}" not found', 'available_sheets': available_sheets},
                                    status=status.HTTP_400_BAD_REQUEST)

                ws = wb[sheet_name]
                headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                for row in ws.iter_rows(min_row=2, values_only=True):
                    data = dict(zip(headers, row))
                    mainarea_id = data.get('mainarea')
                    majorarea_name = data.get('Majorarea')
                    if Studymajorarea.objects.filter(mainarea_id=mainarea_id, Majorarea__iexact=majorarea_name).exists():
                        duplicate_entries.append(f"{mainarea_id}-{majorarea_name}")
                        continue
                    Studymajorarea.objects.create(
                        mainarea_id=mainarea_id,
                        Majorarea=majorarea_name,
                        description=data.get('description', ''),
                        is_deleted=data.get('is_deleted', False)
                    )
            else:  
                dataset.load(file.read().decode('utf-8'), format='csv')
                for row in dataset.dict:
                    mainarea_id = row.get('mainarea_id')
                    majorarea_name = row.get('Majorarea')
                    if Studymajorarea.objects.filter(mainarea_id=mainarea_id, Majorarea__iexact=majorarea_name).exists():
                        duplicate_entries.append(f"{mainarea_id}-{majorarea_name}")
                        continue
                    Studymajorarea.objects.create(
                        mainarea_id=mainarea_id,
                        Majorarea=majorarea_name,
                        description=row.get('description', ''),
                        is_deleted=row.get('is_deleted', False)
                    )

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": list(set(duplicate_entries)),
            'message': f'Sheet "{sheet_name}" imported successfully' if sheet_name else 'Import successful'
        })





# -------------------- StudySpecialisation -------------------- 
class StudySpecialisationCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        mainarea_id = request.data.get('mainarea_id')
        majorarea_id = request.data.get('Majorarea_id')
        specialisation_name = request.data.get('studyspecialisation', '').strip()

        # Prevent duplicates
        if StudySpecialisation.objects.filter(
            mainarea_id=mainarea_id,
            Majorarea_id=majorarea_id,
            studyspecialisation__iexact=specialisation_name
        ).exists():
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "This specialisation already exists for the selected main and major area."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = StudySpecialisationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Study Specialisation created successfully",
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


# -------------------- RETRIEVE -------------------- #
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


# -------------------- UPDATE -------------------- #
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

        mainarea_id = request.data.get('mainarea_id')
        majorarea_id = request.data.get('Majorarea_id')
        specialisation_name = request.data.get('studyspecialisation', '').strip()

        if StudySpecialisation.objects.filter(
            mainarea_id=mainarea_id,
            Majorarea_id=majorarea_id,
            studyspecialisation__iexact=specialisation_name
        ).exclude(uuid=uuid).exists():
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "This specialisation already exists for the selected main and major area."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = StudySpecialisationSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Study Specialisation updated successfully",
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


# -------------------- DELETE -------------------- #
class StudySpecialisationDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        uuids = request.data.get('id', [])
        if not uuids or not isinstance(uuids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide a list of UUIDs in 'id' field.",
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

        objs = StudySpecialisation.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = objs.count()
        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching Study Specialisation found.",
                "data": {"invalid_uuids": invalid_uuids}
            }, status=status.HTTP_404_NOT_FOUND)

        objs.update(is_deleted=True)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} Study Specialisation(s) deleted successfully.",
        })


# -------------------- EXPORT -------------------- #
class StudySpecialisationExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'csv').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_list = [f.strip() for f in fields.split(',')] if fields else [
            'uuid', 'mainarea', 'Majorarea', 'studyspecialisation', 'description', 'is_deleted', 'created_at', 'updated_at'
        ]

        queryset = StudySpecialisation.objects.filter(uuid__in=uuids) if uuids else StudySpecialisation.objects.all()

        dataset = Dataset()
        dataset.headers = field_list

        for obj in queryset:
            row = []
            for field in field_list:
                if field == 'mainarea':
                    value = obj.mainarea.Mainarea if obj.mainarea else ''
                elif field == 'Majorarea':
                    value = obj.Majorarea.Majorarea if obj.Majorarea else ''
                else:
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
            file_name = 'studyspecialisations.xlsx'
        else:
            data = CSV().export_data(dataset)
            content_type = 'text/csv; charset=utf-8'
            file_name = 'studyspecialisations.csv'

        response = HttpResponse(data, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


# -------------------- IMPORT -------------------- #
class StudySpecialisationImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')
        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        dataset = Dataset()
        duplicate_entries = []

        try:
            if format_type == 'xlsx':
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({'error': 'Please provide sheet_name', 'available_sheets': available_sheets},
                                    status=status.HTTP_400_BAD_REQUEST)

                if sheet_name not in available_sheets:
                    return Response({'error': f'Sheet "{sheet_name}" not found', 'available_sheets': available_sheets},
                                    status=status.HTTP_400_BAD_REQUEST)

                ws = wb[sheet_name]
                headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                for row in ws.iter_rows(min_row=2, values_only=True):
                    data = dict(zip(headers, row))
                    mainarea_id = data.get('mainarea_id')
                    majorarea_id = data.get('Majorarea_id')
                    specialisation_name = data.get('studyspecialisation')
                    if StudySpecialisation.objects.filter(
                        mainarea_id=mainarea_id,
                        Majorarea_id=majorarea_id,
                        studyspecialisation__iexact=specialisation_name
                    ).exists():
                        duplicate_entries.append(f"{mainarea_id}-{majorarea_id}-{specialisation_name}")
                        continue
                    StudySpecialisation.objects.create(
                        mainarea_id=mainarea_id,
                        Majorarea_id=majorarea_id,
                        studyspecialisation=specialisation_name,
                        description=data.get('description', ''),
                        is_deleted=data.get('is_deleted', False)
                    )
            else:  # CSV
                dataset.load(file.read().decode('utf-8'), format='csv')
                for row in dataset.dict:
                    mainarea_id = row.get('mainarea_id')
                    majorarea_id = row.get('Majorarea_id')
                    specialisation_name = row.get('studyspecialisation')
                    if StudySpecialisation.objects.filter(
                        mainarea_id=mainarea_id,
                        Majorarea_id=majorarea_id,
                        studyspecialisation__iexact=specialisation_name
                    ).exists():
                        duplicate_entries.append(f"{mainarea_id}-{majorarea_id}-{specialisation_name}")
                        continue
                    StudySpecialisation.objects.create(
                        mainarea_id=mainarea_id,
                        Majorarea_id=majorarea_id,
                        studyspecialisation=specialisation_name,
                        description=row.get('description', ''),
                        is_deleted=row.get('is_deleted', False)
                    )

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": list(set(duplicate_entries)),
            'message': f'Sheet "{sheet_name}" imported successfully' if sheet_name else 'Import successful'
        })



# -------------------- AcademicResultType -------------------- 
class AcademicResultTypeCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        name = request.data.get('Academicresulttype', '').strip()
        if AcademicResultType.objects.filter(Academicresulttype__iexact=name).exists():
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

        name = request.data.get('Academicresulttype', '').strip()
        if AcademicResultType.objects.filter(Academicresulttype__iexact=name).exclude(uuid=uuid).exists():
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Academic Result Type with this name already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = AcademicResultTypeSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Academic Result Type updated successfully",
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


class AcademicResultTypeDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        uuids = request.data.get('id', [])
        if not uuids or not isinstance(uuids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide a list of UUIDs in 'id' field."
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

        objs = AcademicResultType.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = objs.count()
        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching Academic Result Types found.",
                "data": {"invalid_uuids": invalid_uuids}
            }, status=status.HTTP_404_NOT_FOUND)

        objs.update(is_deleted=True)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} Academic Result Type(s) deleted successfully."
        })


class AcademicResultTypeExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'csv').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_list = [f.strip() for f in fields.split(',')] if fields else [
            'uuid', 'Academicresulttype', 'description', 'is_deleted', 'created_at', 'updated_at'
        ]

        queryset = AcademicResultType.objects.filter(uuid__in=uuids) if uuids else AcademicResultType.objects.all()

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
            file_name = 'academic_result_types.xlsx'
        else:
            data = CSV().export_data(dataset)
            content_type = 'text/csv; charset=utf-8'
            file_name = 'academic_result_types.csv'

        response = HttpResponse(data, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


class AcademicResultTypeImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')
        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        dataset = Dataset()
        duplicate_entries = []

        try:
            if format_type == 'xlsx':
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({'error': 'Please provide sheet_name', 'available_sheets': available_sheets},
                                    status=status.HTTP_400_BAD_REQUEST)

                if sheet_name not in available_sheets:
                    return Response({'error': f'Sheet "{sheet_name}" not found', 'available_sheets': available_sheets},
                                    status=status.HTTP_400_BAD_REQUEST)

                ws = wb[sheet_name]
                headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                for row in ws.iter_rows(min_row=2, values_only=True):
                    data = dict(zip(headers, row))
                    name = data.get('Academicresulttype')
                    if AcademicResultType.objects.filter(Academicresulttype__iexact=name).exists():
                        duplicate_entries.append(name)
                        continue
                    AcademicResultType.objects.create(
                        Academicresulttype=name,
                        description=data.get('description', ''),
                        is_deleted=data.get('is_deleted', False)
                    )
            else:
                dataset.load(file.read().decode('utf-8'), format='csv')
                for row in dataset.dict:
                    name = row.get('Academicresulttype')
                    if AcademicResultType.objects.filter(Academicresulttype__iexact=name).exists():
                        duplicate_entries.append(name)
                        continue
                    AcademicResultType.objects.create(
                        Academicresulttype=name,
                        description=row.get('description', ''),
                        is_deleted=row.get('is_deleted', False)
                    )

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": list(set(duplicate_entries)),
            'message': f'Sheet "{sheet_name}" imported successfully' if sheet_name else 'Import successful'
        })






# -------------------- AcademicResult -------------------- #
class AcademicResultCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        academic_type = request.data.get('AcademicResulttype_id')
        academic_result = request.data.get('Academicresult', '').strip()

        # Duplicate prevention: same type + result
        if AcademicResult.objects.filter(
            AcademicResulttype_id=academic_type,
            Academicresult__iexact=academic_result,
            is_deleted=False
        ).exists():
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "This Academic Result already exists for the selected type."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = AcademicResultSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Academic Result created successfully",
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


# -------------------- RETRIEVE -------------------- #
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


# -------------------- UPDATE -------------------- #
class AcademicResultUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, uuid):
        try:
            obj = AcademicResult.objects.get(uuid=uuid, is_deleted=False)
        except AcademicResult.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Academic Result not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        academic_type = request.data.get('AcademicResulttype_id')
        academic_result = request.data.get('Academicresult', '').strip()

        if AcademicResult.objects.filter(
            AcademicResulttype_id=academic_type,
            Academicresult__iexact=academic_result
        ).exclude(uuid=uuid).exists():
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "This Academic Result already exists for the selected type."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = AcademicResultSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Academic Result updated successfully",
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


# -------------------- DELETE -------------------- #
class AcademicResultDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request):
        uuids = request.data.get('id', [])
        if not uuids or not isinstance(uuids, list):
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Please provide a list of UUIDs in 'id' field."
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

        objs = AcademicResult.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = objs.count()
        if count == 0:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "No matching Academic Results found.",
                "data": {"invalid_uuids": invalid_uuids}
            }, status=status.HTTP_404_NOT_FOUND)

        objs.update(is_deleted=True)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} Academic Result(s) deleted successfully."
        })


# -------------------- EXPORT -------------------- #
class AcademicResultExportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        format_type = request.GET.get('format', 'csv').lower()
        fields = request.GET.get('fields')
        uuids_param = request.GET.get('uuids', '')
        uuids = [u.strip() for u in uuids_param.split(',') if u]

        field_list = [f.strip() for f in fields.split(',')] if fields else [
            'uuid', 'AcademicResulttype', 'Academicresult', 'description', 'is_deleted', 'created_at', 'updated_at'
        ]

        queryset = AcademicResult.objects.filter(uuid__in=uuids) if uuids else AcademicResult.objects.all()

        dataset = Dataset()
        dataset.headers = field_list

        for obj in queryset:
            row = []
            for field in field_list:
                value = getattr(obj, field, '')
                if field == 'AcademicResulttype' and obj.AcademicResulttype:
                    value = obj.AcademicResulttype.Academicresulttype
                if isinstance(value, datetime.datetime):
                    value = value.strftime("%Y-%m-%d %H:%M:%S")
                if isinstance(value, bool):
                    value = int(value)
                row.append(value if value is not None else '')
            dataset.append(row)

        if format_type == 'xlsx':
            data = XLSX().export_data(dataset)
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name = 'academic_results.xlsx'
        else:
            data = CSV().export_data(dataset)
            content_type = 'text/csv; charset=utf-8'
            file_name = 'academic_results.csv'

        response = HttpResponse(data, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


# -------------------- IMPORT -------------------- #
class AcademicResultImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        sheet_name = request.data.get('sheet_name')
        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        format_type = file.name.split('.')[-1].lower()
        dataset = Dataset()
        duplicate_entries = []

        try:
            if format_type == 'xlsx':
                wb = openpyxl.load_workbook(file, read_only=True)
                available_sheets = wb.sheetnames

                if not sheet_name:
                    return Response({'error': 'Please provide sheet_name', 'available_sheets': available_sheets},
                                    status=status.HTTP_400_BAD_REQUEST)

                if sheet_name not in available_sheets:
                    return Response({'error': f'Sheet "{sheet_name}" not found', 'available_sheets': available_sheets},
                                    status=status.HTTP_400_BAD_REQUEST)

                ws = wb[sheet_name]
                headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                for row in ws.iter_rows(min_row=2, values_only=True):
                    data = dict(zip(headers, row))
                    academic_type = data.get('AcademicResulttype_id')
                    academic_result = data.get('Academicresult')
                    if AcademicResult.objects.filter(AcademicResulttype_id=academic_type, Academicresult__iexact=academic_result).exists():
                        duplicate_entries.append(academic_result)
                        continue
                    AcademicResult.objects.create(
                        AcademicResulttype_id=academic_type,
                        Academicresult=academic_result,
                        description=data.get('description', ''),
                        is_deleted=data.get('is_deleted', False)
                    )
            else:
                dataset.load(file.read().decode('utf-8'), format='csv')
                for row in dataset.dict:
                    academic_type = row.get('AcademicResulttype_id')
                    academic_result = row.get('Academicresult')
                    if AcademicResult.objects.filter(AcademicResulttype_id=academic_type, Academicresult__iexact=academic_result).exists():
                        duplicate_entries.append(academic_result)
                        continue
                    AcademicResult.objects.create(
                        AcademicResulttype_id=academic_type,
                        Academicresult=academic_result,
                        description=row.get('description', ''),
                        is_deleted=row.get('is_deleted', False)
                    )

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "statusCode": 200,
            "status": True,
            "duplicates": list(set(duplicate_entries)),
            'message': f'Sheet "{sheet_name}" imported successfully' if sheet_name else 'Import successful'
        })






# -------------------- EducationType CRUD -------------------- #

class EducationTypeListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        queryset = EducationType.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(educationType__icontains=search) |
                Q(Perticulars__icontains=search)
            )

        queryset = queryset.order_by('-created_at')
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
        objs.update(is_deleted=True)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} Education Type(s) deleted successfully",
            "invalid_uuids": invalid_uuids
        })


# -------------------- MediumofEducation CRUD -------------------- #

class MediumofEducationListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '').strip()
        queryset = MediumofEducation.objects.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(Perticulars__icontains=search)
            )

        queryset = queryset.order_by('-created_at')
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

        objs = MediumofEducation.objects.filter(uuid__in=valid_uuids, is_deleted=False)
        count = objs.count()
        objs.update(is_deleted=True)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": f"{count} Medium of Education(s) deleted successfully",
            "invalid_uuids": invalid_uuids
        })




# -------------------- Language --------------------
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


# -------------------- RETRIEVE -------------------- #
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


# -------------------- UPDATE -------------------- #
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


# -------------------- DELETE -------------------- #
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


# -------------------- EXPORT -------------------- #
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


# -------------------- IMPORT -------------------- #
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
