from django.shortcuts import render
from  .models  import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import  *
from django.core.paginator import Paginator
from django.db.models import Q
import uuid
from rest_framework.permissions import AllowAny, IsAuthenticated ,BasePermission 
from django.shortcuts import get_object_or_404
from .pagination import  *
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import ValidationError


class IsAdministrator(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role and request.user.role.name == "administrator"


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
                "statusCode": 201,
                "status": True,
                "message": "Gender created successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        

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
    def delete(self, request, uuid):
        try:
            gender = Gender.objects.get(uuid=uuid, is_deleted=False)
        except Gender.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Gender not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        gender.is_deleted = True
        gender.save()
        return Response({
            "statusCode": 204,
            "status": True,
            "message": "Gender deleted successfully",
            "data": None
        }, status=status.HTTP_204_NO_CONTENT)


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
                "statusCode": 201,
                "status": True,
                "message": "Maritalstatus created successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)


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
                "id": continents.id,
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
                "id": m.id,
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
                "id": continent.id,
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
                    continent = Continents.objects.get(id=continent_id, is_deleted=False)
                except Continents.DoesNotExist:
                    return Response({
                        "statusCode": 404,
                        "status": False,
                        "message": "Invalid continent ID"
                    }, status=status.HTTP_404_NOT_FOUND)

            country = Country.objects.create(
                id=uuid.uuid4(),
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
                "statusCode": 201,
                "status": True,
                "message": "Country created successfully",
                "data": {
                    "id": country.id,
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
            }, status=status.HTTP_201_CREATED)

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
                "id": c.id,
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
            "id": country.id,
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
                "id": str(country.id),
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
                "statusCode": 201,
                "status": True,
                "message": "State created successfully",
                "data": {
                    "id": state.id,
                    "name": state.stateName,
                    "country": state.countryName.name if state.countryName else None,
                    "stateshortName": state.stateshortName,
                    "description": state.description,
                    "status": state.is_active,
                }
            }, status=status.HTTP_201_CREATED)

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
                "id": s.id,
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
                "id": str(state.id),
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
                    "id": str(district.id),
                    "districtName": district.districtName,
                    "country": district.countryName.name if district.countryName else None,
                    "state": district.stateName.stateName if district.stateName else None,
                    "description": district.description
                }
                
            }, status=status.HTTP_201_CREATED)

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
                "id": str(district.id),
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
                "id": str(district.id),
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



class DistrictByStateAPIView(APIView):
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
                "id": str(state.id),
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
                "id": str(city.id),
                "cityName": city.cityName,
                "country": city.countryName.name if city.countryName else None,
                "state": city.stateName.stateName if city.stateName else None,
                "district": city.districtName.districtName if city.districtName else None,
                "description": city.description
            }}, status=status.HTTP_201_CREATED)
        

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
                "id": c.id,
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
                "id": str(city.id),
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
                "statusCode": 201,
                "status": True,
                "message": "Relation created successfully",
                "data": {
                    "id": str(relation.id),
                    "relation": relation.relation,
                    "description": relation.description
                }
            }, status=status.HTTP_201_CREATED)

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
                    "id": str(rel.id),
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
                    "id": str(relation.id),
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
                "statusCode": 201,
                "status": True,
                "message": "Timezone created successfully",
                "data": {
                    "id": str(timezone_obj.id),
                    "Timezone": timezone_obj.Timezone,
                    "country": timezone_obj.countryName.name if timezone_obj.countryName else None,
                    "state": timezone_obj.stateName.stateName if timezone_obj.stateName else None,
                    "description": timezone_obj.description
                }
            }, status=status.HTTP_201_CREATED)

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
                "id": str(tz.id),
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
                    "id": str(timezone_obj.id),
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
        queryset = Department.objects.filter(is_deleted=False).order_by('-created_at')
        search = request.GET.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search) | queryset.filter(description__icontains=search)

        paginator = StandardResultsSetPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = DepartmentSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class DepartmentCreateAPIView(APIView):
    def post(self, request):
        serializer = DepartmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 201,
                "status": True,
                "message": "Department created successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
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
    def delete(self, request, uuid):
        try:
            department = Department.objects.get(uuid=uuid, is_deleted=False)
        except Department.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Department not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        department.is_deleted = True
        department.save()
        return Response({
            "statusCode": 204,
            "status": True,
            "message": "Department deleted successfully",
            "data": None
        }, status=status.HTTP_204_NO_CONTENT)






class EmployeeTypeListAPIView(APIView):
    def get(self, request):
        queryset = EmployeeType.objects.filter(is_deleted=False).order_by('-created_at')
        search = request.GET.get('search')
        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(description__icontains=search))

        paginator = StandardResultsSetPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = EmployeeTypeSerializer(result_page, many=True)
        return paginator.get_paginated_response({
            "statusCode": 200,
            "status": True,
            "message": "Employee types retrieved successfully",
            "data": serializer.data
        })


class EmployeeTypeCreateAPIView(APIView):
    def post(self, request):
        serializer = EmployeeTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 201,
                "status": True,
                "message": "Employee type created successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
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
    def delete(self, request, uuid):
        try:
            emp_type = EmployeeType.objects.get(uuid=uuid, is_deleted=False)
        except EmployeeType.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Employee type not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        emp_type.is_deleted = True
        emp_type.save()
        return Response({
            "statusCode": 204,
            "status": True,
            "message": "Employee type deleted successfully",
            "data": None
        }, status=status.HTTP_204_NO_CONTENT)







class CompanyTypeListAPIView(APIView):
    def get(self, request):
        search = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        per_page = int(request.GET.get("per_page", 10))

        queryset = CompanyType.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(name__icontains=search)

        paginator = Paginator(queryset, per_page)
        page_obj = paginator.get_page(page)
        serializer = CompanyTypeSerializer(page_obj, many=True)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Company types retrieved successfully",
            "total": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": page,
            "data": serializer.data
        })

class CompanyTypeCreateAPIView(APIView):
    def post(self, request):
        serializer = CompanyTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 201,
                "status": True,
                "message": "Company type created successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)

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
    def delete(self, request, uuid):
        try:
            company_type = CompanyType.objects.get(uuid=uuid, is_deleted=False)
        except CompanyType.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Company type not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        company_type.is_deleted = True
        company_type.save()
        return Response({
            "statusCode": 204,
            "status": True,
            "message": "Company type deleted successfully",
            "data": None
        }, status=status.HTTP_204_NO_CONTENT)



class OwnershipTypeListAPIView(APIView):
    def get(self, request):
        search = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        per_page = int(request.GET.get("per_page", 10))

        queryset = OwnershipType.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(description__icontains=search))

        paginator = Paginator(queryset, per_page)
        page_obj = paginator.get_page(page)
        serializer = OwnershipTypeSerializer(page_obj, many=True)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Ownership types retrieved successfully",
            "total": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": page,
            "data": serializer.data
        })

class OwnershipTypeCreateAPIView(APIView):
    def post(self, request):
        serializer = OwnershipTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 201,
                "status": True,
                "message": "Ownership type created successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)

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
    def delete(self, request, uuid):
        try:
            ownership = OwnershipType.objects.get(uuid=uuid, is_deleted=False)
        except OwnershipType.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Ownership type not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        ownership.is_deleted = True
        ownership.save()
        return Response({
            "statusCode": 204,
            "status": True,
            "message": "Ownership type deleted successfully",
            "data": None
        }, status=status.HTTP_204_NO_CONTENT)







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
        try:
            search = request.GET.get("search", "")
            page = int(request.GET.get("page", 1))
            per_page = int(request.GET.get("per_page", 10))

            queryset = StakeholderCategory.objects.filter(is_deleted=False)
            if search:
                queryset = queryset.filter(name__icontains=search)

            paginator = Paginator(queryset, per_page)
            page_obj = paginator.get_page(page)
            serializer = StakeholderCategorySerializer(page_obj, many=True)

            return Response({
                "statusCode": 200,
                "status": True,
                "message": "Stakeholder Categories retrieved successfully",
                "total": paginator.count,
                "total_pages": paginator.num_pages,
                "current_page": page,
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        except ValueError:
            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Invalid pagination parameters"
            }, status=status.HTTP_400_BAD_REQUEST)


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
    def delete(self, request, uuid):
        category = get_object_or_404(StakeholderCategory, uuid=uuid, is_deleted=False)
        category.is_deleted = True
        category.save()
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Stakeholder Category deleted successfully"
        }, status=status.HTTP_200_OK)




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
        search = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        per_page = int(request.GET.get("per_page", 10))

        queryset = StakeholderType.objects.filter(is_deleted=False)
        if search:
            queryset = queryset.filter(name__icontains=search)

        paginator = Paginator(queryset, per_page)
        page_obj = paginator.get_page(page)
        serializer = StakeholderTypeSerializer(page_obj, many=True)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Stakeholder Types retrieved successfully",
            "total": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": page,
            "data": serializer.data
        }, status=status.HTTP_200_OK)


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
    def delete(self, request, uuid):
        stakeholder_type = get_object_or_404(StakeholderType, uuid=uuid, is_deleted=False)
        stakeholder_type.is_deleted = True
        stakeholder_type.save()
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Stakeholder Type deleted successfully"
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
        search = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        per_page = int(request.GET.get("per_page", 10))

        categories = AccreditationCategory.objects.filter(is_deleted=False)
        if search:
            categories = categories.filter(name__icontains=search)

        paginator = Paginator(categories, per_page)
        page_obj = paginator.get_page(page)

        serializer = AccreditationCategorySerializer(page_obj, many=True)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Accreditation Categories retrieved successfully",
            "total": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": page,
            "data": serializer.data
        }, status=status.HTTP_200_OK)


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
    def delete(self, request, uuid):
        try:
            category = AccreditationCategory.objects.get(uuid=uuid, is_deleted=False)
        except AccreditationCategory.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Accreditation Category not found"
            }, status=status.HTTP_404_NOT_FOUND)

        category.is_deleted = True
        category.save()
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Accreditation Category deleted successfully"
        }, status=status.HTTP_200_OK)



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
        search = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        per_page = int(request.GET.get("per_page", 10))

        names = AccreditationName.objects.filter(is_deleted=False)
        if search:
            names = names.filter(full_name__icontains=search)

        paginator = Paginator(names, per_page)
        page_obj = paginator.get_page(page)

        serializer = AccreditationNameSerializer(page_obj, many=True)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Accreditation Names retrieved successfully",
            "total": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": page,
            "data": serializer.data
        }, status=status.HTTP_200_OK)


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
    def delete(self, request, uuid):
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
        search = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        per_page = int(request.GET.get("per_page", 10))

        categories = BankAccountType.objects.filter(is_deleted=False)
        if search:
            categories = categories.filter(name__icontains=search)

        paginator = Paginator(categories, per_page)
        page_obj = paginator.get_page(page)

        serializer = BankAccountTypeSerializer(page_obj, many=True)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Bank Account retrieved successfully",
            "total": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": page,
            "data": serializer.data
        }, status=status.HTTP_200_OK)


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
    def delete(self, request, uuid):
        try:
            category = BankAccountType.objects.get(uuid=uuid, is_deleted=False)
        except BankAccountType.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Bank Account Type  not found"
            }, status=status.HTTP_404_NOT_FOUND)

        category.is_deleted = True
        category.save()
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Bank Account Type  deleted successfully"
        }, status=status.HTTP_200_OK)



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
        search = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        per_page = int(request.GET.get("per_page", 10))

        licenses = LicenseName.objects.filter(is_deleted=False)
        if search:
            licenses = licenses.filter(full_name__icontains=search)

        paginator = Paginator(licenses, per_page)
        page_obj = paginator.get_page(page)
        serializer = LicenseNameSerializer(page_obj, many=True)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": "License Names retrieved successfully",
            "total": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": page,
            "data": serializer.data
        }, status=status.HTTP_200_OK)



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
    def delete(self, request, uuid):
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
        search = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        per_page = int(request.GET.get("per_page", 10))

        categories = LeadSource.objects.filter(is_deleted=False)
        if search:
            categories = categories.filter(name__icontains=search)

        paginator = Paginator(categories, per_page)
        page_obj = paginator.get_page(page)

        serializer = LeadSourceSerializer(page_obj, many=True)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Lead Source retrieved successfully",
            "total": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": page,
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class LeadSourceRetrieveAPIView(APIView):
    def get(self, request, uuid):
        try:
            leadsource = LeadSource.objects.get(uuid=uuid, is_deleted=False)
        except LeadSource.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Lead Source  not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = LeadSourceSerializer(leadsource)
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Lead Source  retrieved successfully",
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
        search = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        per_page = int(request.GET.get("per_page", 10))

        categories = InterestLevel.objects.filter(is_deleted=False)
        if search:
            categories = categories.filter(name__icontains=search)

        paginator = Paginator(categories, per_page)
        page_obj = paginator.get_page(page)

        serializer = InterestLevelSerializer(page_obj, many=True)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Interest Level retrieved successfully",
            "total": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": page,
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class InterestLevelRetrieveAPIView(APIView):
    def get(self, request, uuid):
        try:
            interestlevel = InterestLevel.objects.get(uuid=uuid, is_deleted=False)
        except LeadSource.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Lead Source  not found"
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
    def delete(self, request, uuid):
        try:
            category = InterestLevel.objects.get(uuid=uuid, is_deleted=False)
        except LeadSource.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Interest Level Type  not found"
            }, status=status.HTTP_404_NOT_FOUND)

        category.is_deleted = True
        category.save()
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Interest Level Type  deleted successfully"
        }, status=status.HTTP_200_OK)
    

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
        search = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        per_page = int(request.GET.get("per_page", 10))

        categories = Priority.objects.filter(is_deleted=False)
        if search:
            categories = categories.filter(name__icontains=search)

        paginator = Paginator(categories, per_page)
        page_obj = paginator.get_page(page)

        serializer = PrioritySerializer(page_obj, many=True)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Priority retrieved successfully",
            "total": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": page,
            "data": serializer.data
        }, status=status.HTTP_200_OK)


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
    def delete(self, request, uuid):
        try:
            category = Priority.objects.get(uuid=uuid, is_deleted=False)
        except LeadSource.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Priority not found"
            }, status=status.HTTP_404_NOT_FOUND)

        category.is_deleted = True
        category.save()
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Priority  deleted successfully"
        }, status=status.HTTP_200_OK)
    

#-------------------------------------------Tags---------------------------------


class TagsCreateAPIView(APIView):
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
        search = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        per_page = int(request.GET.get("per_page", 10))

        categories = Tags.objects.filter(is_deleted=False)
        if search:
            categories = categories.filter(name__icontains=search)

        paginator = Paginator(categories, per_page)
        page_obj = paginator.get_page(page)

        serializer = TagsSerializer(page_obj, many=True)

        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Priority retrieved successfully",
            "total": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": page,
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class TagsRetrieveAPIView(APIView):
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
    def delete(self, request, uuid):
        try:
            category = Tags.objects.get(uuid=uuid, is_deleted=False)
        except Tags.DoesNotExist:
            return Response({
                "statusCode": 404,
                "status": False,
                "message": "Tags not found"
            }, status=status.HTTP_404_NOT_FOUND)

        category.is_deleted = True
        category.save()
        return Response({
            "statusCode": 200,
            "status": True,
            "message": "Tags  deleted successfully"
        }, status=status.HTTP_200_OK)
    
