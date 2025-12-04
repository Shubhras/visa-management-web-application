from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction, IntegrityError
from django.core.exceptions import ValidationError
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, serializers 
from uuid import UUID
from django.shortcuts import get_object_or_404
from django.core.files.storage import default_storage


class ApplicantCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = ApplicantSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            with transaction.atomic():
                applicant = serializer.save()

            return Response({
                "status": True,
                "statusCode": 201,
                "message": "Applicant created successfully",
                "data": ApplicantSerializer(applicant).data
            }, status=status.HTTP_201_CREATED)

        except serializers.ValidationError as ve:
            return Response({
                "status": False,
                "statusCode": 400,
                "message": "Validation failed",
                "errors": ve.detail
            }, status=status.HTTP_400_BAD_REQUEST)

        except IntegrityError as ie:
            return Response({
                "status": False,
                "statusCode": 400,
                "message": "Database integrity error",
                "details": str(ie)
            }, status=status.HTTP_400_BAD_REQUEST)

        except ValidationError as ve:
            return Response({
                "status": False,
                "statusCode": 400,
                "message": "Validation failed",
                "errors": ve.message_dict
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "status": False,
                "statusCode": 500,
                "message": "Something went wrong",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ApplicantGetAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        applicants = Applicant.objects.all()

        # UUID Filter Multiple
        uuids = request.GET.get("uuids")
        if uuids:
            uuid_list = []
            for u in uuids.split(","):
                try:
                    uuid_list.append(UUID(u.strip()))
                except:
                    return Response({
                        "status": False,
                        "message": f"Invalid UUID: {u}"
                    }, status=status.HTTP_400_BAD_REQUEST)

            applicants = applicants.filter(uuid__in=uuid_list)

        serializer = ApplicantSerializer(applicants, many=True)
        return Response({
            "status": True,
            "statusCode": 200,
            "message": "Applicants fetched successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class ApplicantDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, uuid):
        try:
            valid_uuid = UUID(str(uuid))
        except:
            return Response({
                "status": False,
                "statusCode": 400,
                "message": "Invalid UUID format"
            }, status=status.HTTP_400_BAD_REQUEST)

        applicant = get_object_or_404(Applicant, uuid=valid_uuid)
        serializer = ApplicantSerializer(applicant)

        return Response({
            "status": True,
            "statusCode": 200,
            "message": "Applicant detail fetched successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class ApplicantUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, uuid):
        try:
            applicant = Applicant.objects.get(uuid=uuid)
        except Applicant.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Applicant not found."
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            serializer = ApplicantSerializer(applicant, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)

            with transaction.atomic():
                applicant = serializer.save()

            return Response({
                "status": "success",
                "message": "Applicant updated successfully.",
                "data": ApplicantSerializer(applicant).data
            }, status=status.HTTP_200_OK)

        except serializers.ValidationError as ve:
            return Response({
                "status": "error",
                "message": "Validation failed.",
                "errors": ve.detail
            }, status=status.HTTP_400_BAD_REQUEST)

        except IntegrityError as ie:
            return Response({
                "status": "error",
                "message": "Database integrity error.",
                "details": str(ie)
            }, status=status.HTTP_400_BAD_REQUEST)

        except ValidationError as ve:
            return Response({
                "status": "error",
                "message": "Validation failed.",
                "errors": ve.message_dict
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "status": "error",
                "message": "Something went wrong.",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#<-----------------------delete----------------->
class ApplicantDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self,request,uuid=None):
        id = request.data.get('id',None)

        #single delete via url
        if uuid:
            try:
                obj = Applicant.objects.get(uuid=uuid)
                obj.delete()
                return Response({
                    "statusCode":204,
                    "status":True,
                    "message":"Applicant permanently deleted.",
                    "data":None
                },status=status.HTTP_204_NO_CONTENT)
            except Applicant.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status" :  False,
                    "message": "Applicant not found. ",
                    "data":None        
                        },status=status.HTTP_404_NOT_FOUND)
        #delete all
        if id == "all":
            queryset = Applicant.objects.all()
            count = queryset.count()
            queryset.delete()
            return Response({
                "statusCode":200,
                "status":True,
                "message": f"All {count} Applicant permanently deleted. ",
                "data":None
            },status=status.HTTP_200_OK)
        #Bulk Delete
        if not id or not isinstance(id,list):
            return Response({
                "statusCode":400,
                "status":False,
                "message":"Please provide a list of U"
                "UIDs in 'id' field or 'all'.",
                "data":None
            },status= status.HTTP_400_BAD_REQUEST)
        
        valid_uuids= []
        invalid_uuids= []
        for u in id:
            try:
                valid_uuids.append(UUID(u))
            except ValueError:
                invalid_uuids.append(UUID(u))
        queryset = Applicant.objects.filter(uuid__in=valid_uuids)
        count = queryset.count()
        queryset.delete()
        return Response({
            "statusCode":200,
            "status":True,
            "message":f"{count} Applicant permanently deleted.",
            "data":{"invalid_uuids": invalid_uuids} if invalid_uuids else None
        },status = status.HTTP_200_OK)
        
#<----------------Education----------------->

class EducationCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = EducationSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "statusCode": 201,
                    "status": True,
                    "message": "Education record created successfully.",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)

            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Validation failed.",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "statusCode": 500,
                "status": False,
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class EducationListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        queryset = Education.objects.all()

        #filter 
        uuids = request.GET.get("uuids")
        if uuids:
            uuid_list = []
            for u in uuids.split(","):
                try:
                    uuid_list.append(UUID(u.strip()))
                except:
                    return Response({
                        "status" : False,
                        "message":f"Invalid UUID:{u}"
                       
                    },status=status.HTTP_400_BAD_REQUEST)
                
            queryset = queryset.filter(uuid__in=uuid_list)
        serializer = EducationSerializer(queryset ,many=True)
        return Response({
            "status":True, 
            "message":"Education data fatched successfully",
            "data":serializer.data,

            },status=status.HTTP_200_OK)

class EducationDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request,uuid):
        try:
            valid_uuid = UUID(str(uuid))
        except:
            return Response({
                "status":False,
                "message":"Invalid UUID format",
            },status = status.HTTP_400_BAD_REQUEST)
        education = get_object_or_404(Education,uuid=valid_uuid)
        serializer = EducationSerializer(education)
        
        return Response({
            "status":True,
            "statusCode":200,
            "message":"Education detail fetched successfully",
            "data":serializer.data
        },status= status.HTTP_200_OK)


class EducationUpdateAPIView(APIView):
    def put(self,request,uuid):
        try: 
            education = Education.objects.get(uuid=uuid)
        except Education.DoesNotExist:
              return Response({
                "status": "error",
                "message": "Education not found."
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            serializer = EducationSerializer(education,data = request.data, partial = True)
            serializer.is_valid(raise_exception=True)

            with transaction.atomic():
                education = serializer.save()
            return Response({
                "status":True,
                "message":"Education updated successfully.",
                "data":EducationSerializer(education).data
            },status = status.HTTP_200_OK)
        except serializers.ValidationError as ve:
            return Response({
                "status": "error",
                "message": "Validation failed.",
                "errors": ve.detail
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except IntegrityError as ie:
            return Response({
                "status": "error",
                "message": "Database integrity error.",
                "details": str(ie)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except ValidationError as ve:
            return Response({
                "status": "error",
                "message": "Validation failed.",
                "errors": ve.message_dict
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "status": "error",
                "message": "Something went wrong.",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class EducationDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self,request,uuid=None):
        id = request.data.get('id',None)
        
        #single delete via url
        if uuid:
            try:
                obj = Education.objects.get(uuid=uuid)
                obj.delete()
                return Response({
                    "statusCode":204,
                    "status":True,
                    "message":"Education permanently deleted.",
                    "data":None
                },status=status.HTTP_204_NO_CONTENT)
            except Education.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status" :  False,
                    "message": "Education not found. ",
                    "data":None        
                        },status=status.HTTP_404_NOT_FOUND)
        #delete all
        if id == "all":
            queryset = Education.objects.all()
            count = queryset.count()
            queryset.delete()
            return Response({
                "statusCode":200,
                "status":True,
                "message": f"All {count} Education permanently deleted. ",
                "data":None
            },status=status.HTTP_200_OK)
        
        #Bulk Delete
        if not id or not isinstance(id,list):
            return Response({
                "statusCode":400,
                "status":False,
                "message":"Please provide a list of U"
                "UIDs in 'id' field or 'all'.",
                "data":None
            },status= status.HTTP_400_BAD_REQUEST)
        valid_uuids= []
        invalid_uuids= []
        for u in id:
            try:
                valid_uuids.append(UUID(u))
            except ValueError:
                invalid_uuids.append(UUID(u))
        queryset = Education.objects.filter(uuid__in=valid_uuids)
        count = queryset.count()
        queryset.delete()
        return Response({
            "statusCode":200,
            "status":True,
            "message":f"{count} Education permanently deleted.",
            "data":{"invalid_uuids": invalid_uuids} if invalid_uuids else None
        },status = status.HTTP_200_OK)

#<=====================Work_Experience=========================>
class WorkExperienceCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            serializer = WorkExperienceSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "statusCode": 201,
                    "status": True,
                    "message": "WorkExperience record created successfully.",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)
            else:

                return Response({
                      "statusCode":400,
                      "status":False,
                      "message":"Validation Faild. ",
                      "data":serializer.errors

                    },status=status.HTTP_400_BAD_REQUEST)
    
        except Exception as e:
            return Response({
                "statusCode": 500,
                "status": False,
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
        
class WorkExperienceListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        queryset = WorkExperience.objects.all()

        #filter 
        uuids = request.GET.get("uuids")
        if uuids:
            uuid_list = []
            for u in uuids.split(","):
                try:
                    uuid_list.append(UUID(u.strip()))
                except:
                    return Response({
                        "status" : False,
                        "message":f"Invalid UUID:{u}"
                       
                    },status=status.HTTP_400_BAD_REQUEST)
                
            queryset = queryset.filter(uuid__in=uuid_list)
        serializer = WorkExperienceSerializer(queryset ,many=True)
        return Response({
            "status":True, 
            "message":"WorkExperience data fatched successfully",
            "data":serializer.data,

            },status=status.HTTP_200_OK)


class WorkExperienceDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request,uuid):
        try:
            valid_uuid = UUID(str(uuid))
        except:
            return Response({
                "status":False,
                "message":"Invalid UUID format",
            },status = status.HTTP_400_BAD_REQUEST)
        education = get_object_or_404(WorkExperience,uuid=valid_uuid)
        serializer = WorkExperienceSerializer(education)
        
        return Response({
            "status":True,
            "statusCode":200,
            "message":"WorkExperience detail fetched successfully",
            "data":serializer.data
        },status= status.HTTP_200_OK)


class WorkExperienceUpdateAPIView(APIView):
    def put(self,request,uuid):
        try: 
            education = WorkExperience.objects.get(uuid=uuid)
        except WorkExperience.DoesNotExist:
              return Response({
                "status": "error",
                "message": "WorkExperience not found."
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            serializer = WorkExperienceSerializer(education,data = request.data, partial = True)
            serializer.is_valid(raise_exception=True)

            with transaction.atomic():
                education = serializer.save()
            return Response({
                "status":True,
                "message":"WorkExperience updated successfully.",
                "data":WorkExperienceSerializer(education).data
            },status = status.HTTP_200_OK)
        except serializers.ValidationError as ve:
            return Response({
                "status": "error",
                "message": "Validation failed.",
                "errors": ve.detail
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except IntegrityError as ie:
            return Response({
                "status": "error",
                "message": "Database integrity error.",
                "details": str(ie)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except ValidationError as ve:
            return Response({
                "status": "error",
                "message": "Validation failed.",
                "errors": ve.message_dict
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "status": "error",
                "message": "Something went wrong.",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class WorkExperiencenDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self,request,uuid=None):
        id = request.data.get('id',None)
        
        #single delete via url
        if uuid:
            try:
                obj = WorkExperience.objects.get(uuid=uuid)
                obj.delete()
                return Response({
                    "statusCode":204,
                    "status":True,
                    "message":"WorkExperience permanently deleted.",
                    "data":None
                },status=status.HTTP_204_NO_CONTENT)
            except WorkExperience.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status" :  False,
                    "message": "WorkExperience not found. ",
                    "data":None        
                        },status=status.HTTP_404_NOT_FOUND)
        #delete all
        if id == "all":
            queryset = WorkExperience.objects.all()
            count = queryset.count()
            queryset.delete()
            return Response({
                "statusCode":200,
                "status":True,
                "message": f"All {count} WorkExperience permanently deleted. ",
                "data":None
            },status=status.HTTP_200_OK)
        
        #Bulk Delete
        if not id or not isinstance(id,list):
            return Response({
                "statusCode":400,
                "status":False,
                "message":"Please provide a list of U"
                "UIDs in 'id' field or 'all'.",
                "data":None
            },status= status.HTTP_400_BAD_REQUEST)
        valid_uuids= []
        invalid_uuids= []
        for u in id:
            try:
                valid_uuids.append(UUID(u))
            except ValueError:
                invalid_uuids.append(UUID(u))
        queryset = WorkExperience.objects.filter(uuid__in=valid_uuids)
        count = queryset.count()
        queryset.delete()
        return Response({
            "statusCode":200,
            "status":True,
            "message":f"{count} WorkExperience permanently deleted.",
            "data":{"invalid_uuids": invalid_uuids} if invalid_uuids else None
        },status = status.HTTP_200_OK)
    
    
#<======================Language_Ability=======================>
        
class LanguageAbilityCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            serializer = LanguageAbilitySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "status":True,
                    "statusCode":201,
                    "message":"LanguageAbility record created successfully.",
                    "data":serializer.data
                },status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "statusCode":400,
                    "status":False,
                    "message":"Validation Faild. ",
                    "data":serializer.Errors
                },status=status.HTTP_400_BAD_REQUEST)           
        except Exception as e:
            return Response({
                "statusCode":500,
                "status":False,
                "message":str(e)
            },status=status.HTTP_500_INTERNAL_SERVER_ERROR)

       
class LanguageAbilityListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        queryset = LanguageAbility.objects.all()

        #filter 
        uuids = request.GET.get("uuids")
        if uuids:
            uuid_list = []
            for u in uuids.split(","):
                try:
                    uuid_list.append(UUID(u.strip()))
                except:
                    return Response({
                        "status" : False,
                        "message":f"Invalid UUID:{u}"
                       
                    },status=status.HTTP_400_BAD_REQUEST)
                
            queryset = queryset.filter(uuid__in=uuid_list)
        serializer = LanguageAbilitySerializer(queryset ,many=True)
        return Response({
            "status":True, 
            "message":"Language Ability data fatched successfully",
            "data":serializer.data,

            },status=status.HTTP_200_OK)


class LanguageAbilityDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request,uuid):
        try:
            valid_uuid = UUID(str(uuid))
        except:
            return Response({
                "status":False,
                "message":"Invalid UUID format",
            },status=status.HTTP_400_BAD_REQUEST)
        language_abillity = get_object_or_404(LanguageAbility,uuid=valid_uuid)
        serializer = LanguageAbilitySerializer(language_abillity)
        return Response({
            "status":True,
            "statusCode":200,
            "message":"Language Ability detail fetched successfully. ",
            "data": serializer.data
        },status=status.HTTP_200_OK)


class LanguageAbilityUpdateAPIView(APIView):
    def put(self,request,uuid):
        try: 
            language = LanguageAbility.objects.get(uuid=uuid)
        except LanguageAbility.DoesNotExist:
              return Response({
                "status": "error",
                "message": "Language Abiliy not found."
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            serializer = LanguageAbilitySerializer(language,data = request.data, partial = True)
            serializer.is_valid(raise_exception=True)

            with transaction.atomic():
                language = serializer.save()
            return Response({
                "status":True,
                "message":"Language Ability updated successfully.",
                "data":LanguageAbilitySerializer(language).data
            },status = status.HTTP_200_OK)
        except serializers.ValidationError as ve:
            return Response({
                "status": "error",
                "message": "Validation failed.",
                "errors": ve.detail
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except IntegrityError as ie:
            return Response({
                "status": "error",
                "message": "Database integrity error.",
                "details": str(ie)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except ValidationError as ve:
            return Response({
                "status": "error",
                "message": "Validation failed.",
                "errors": ve.message_dict
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "status": "error",
                "message": "Something went wrong.",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

class LanguageAbilityDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self,request,uuid=None):
        id = request.data.get('id',None)
        
        #single delete via url
        if uuid:
            try:
                obj = LanguageAbility.objects.get(uuid=uuid)
                obj.delete()
                return Response({
                    "statusCode":204,
                    "status":True,
                    "message":"Language Ability permanently deleted.",
                    "data":None
                },status=status.HTTP_204_NO_CONTENT)
            except LanguageAbility.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status" :  False,
                    "message": "Language Ability not found. ",
                    "data":None        
                        },status=status.HTTP_404_NOT_FOUND)
        #delete all
        if id == "all":
            queryset = LanguageAbility.objects.all()
            count = queryset.count()
            queryset.delete()
            return Response({
                "statusCode":200,
                "status":True,
                "message": f"All {count} Language Ability permanently deleted. ",
                "data":None
            },status=status.HTTP_200_OK)
        
        #Bulk Delete
        if not id or not isinstance(id,list):
            return Response({
                "statusCode":400,
                "status":False,
                "message":"Please provide a list of U"
                "UIDs in 'id' field or 'all'.",
                "data":None
            },status= status.HTTP_400_BAD_REQUEST)
        valid_uuids= []
        invalid_uuids= []
        for u in id:
            try:
                valid_uuids.append(UUID(u))
            except ValueError:
                invalid_uuids.append(UUID(u))
        queryset = LanguageAbility.objects.filter(uuid__in=valid_uuids)
        count = queryset.count()
        queryset.delete()
        return Response({
            "statusCode":200,
            "status":True,
            "message":f"{count} Language Ability permanently deleted.",
            "data":{"invalid_uuids": invalid_uuids} if invalid_uuids else None
        },status = status.HTTP_200_OK)
    
#<====================Entrance Test Ability=======================>
        
class EntranceTestAbiityCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            serializer = EntranceTestAbilitySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "status":True,
                    "statusCode":201,
                    "message":"Entrance Test Ability record created successfully.",
                    "data":serializer.data
                },status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "statusCode":400,
                    "status":False,
                    "message":"Validation Faild. ",
                    "data":serializer.Errors
                },status=status.HTTP_400_BAD_REQUEST)           
        except Exception as e:
            return Response({
                "statusCode":500,
                "status":False,
                "message":str(e)
            },status=status.HTTP_500_INTERNAL_SERVER_ERROR)

      
class EntranceTestAbilityListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        queryset = EntranceTestAbility.objects.all()

        #filter 
        uuids = request.GET.get("uuids")
        if uuids:
            uuid_list = []
            for u in uuids.split(","):
                try:
                    uuid_list.append(UUID(u.strip()))
                except:
                    return Response({
                        "status" : False,
                        "message":f"Invalid UUID:{u}"
                       
                    },status=status.HTTP_400_BAD_REQUEST)
                
            queryset = queryset.filter(uuid__in=uuid_list)
        serializer = EntranceTestAbilitySerializer(queryset ,many=True)
        return Response({
            "status":True, 
            "message":"Entrance Test Ability data fatched successfully",
            "data":serializer.data,

            },status=status.HTTP_200_OK)


class EntranceTestAbilityDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request,uuid):
        try:
            valid_uuid = UUID(str(uuid))
        except:
            return Response({
                "status":False,
                "message":"Invalid UUID format",
            },status=status.HTTP_400_BAD_REQUEST)
        entrance_abillity = get_object_or_404(EntranceTestAbility,uuid=valid_uuid)
        serializer = EntranceTestAbilitySerializer(entrance_abillity)
        return Response({
            "status":True,
            "statusCode":200,
            "message":"Entrance Test Abilitydetail fetched successfully. ",
            "data": serializer.data
        },status=status.HTTP_200_OK)


class EntranceTestAbilityUpdateAPIView(APIView):
    def put(self,request,uuid):
        try: 
            entrance = EntranceTestAbility.objects.get(uuid=uuid)
        except EntranceTestAbility.DoesNotExist:
              return Response({
                "status": "error",
                "message": "EntranceTestAbility not found."
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            serializer = EntranceTestAbilitySerializer(entrance,data = request.data, partial = True)
            serializer.is_valid(raise_exception=True)

            with transaction.atomic():
                entrance = serializer.save()
            return Response({
                "status":True,
                "message":"EntranceTestAbility updated successfully.",
                "data":EntranceTestAbilitySerializer(entrance).data
            },status = status.HTTP_200_OK)
        except serializers.ValidationError as ve:
            return Response({
                "status": "error",
                "message": "Validation failed.",
                "errors": ve.detail
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except IntegrityError as ie:
            return Response({
                "status": "error",
                "message": "Database integrity error.",
                "details": str(ie)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except ValidationError as ve:
            return Response({
                "status": "error",
                "message": "Validation failed.",
                "errors": ve.message_dict
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "status": "error",
                "message": "Something went wrong.",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class EntranceTestAbilityDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self,request,uuid=None):
        id = request.data.get('id',None)
        
        #single delete via url
        if uuid:
            try:
                obj = EntranceTestAbility.objects.get(uuid=uuid)
                obj.delete()
                return Response({
                    "statusCode":204,
                    "status":True,
                    "message":"EntranceTestAbilitypermanently deleted.",
                    "data":None
                },status=status.HTTP_204_NO_CONTENT)
            except EntranceTestAbility.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status" :  False,
                    "message": "EntranceTestAbility not found. ",
                    "data":None        
                        },status=status.HTTP_404_NOT_FOUND)
        #delete all
        if id == "all":
            queryset = EntranceTestAbility.objects.all()
            count = queryset.count()
            queryset.delete()
            return Response({
                "statusCode":200,
                "status":True,
                "message": f"All {count} EntranceTestAbility permanently deleted. ",
                "data":None
            },status=status.HTTP_200_OK)
        
        #Bulk Delete
        if not id or not isinstance(id,list):
            return Response({
                "statusCode":400,
                "status":False,
                "message":"Please provide a list of U"
                "UIDs in 'id' field or 'all'.",
                "data":None
            },status= status.HTTP_400_BAD_REQUEST)
        valid_uuids= []
        invalid_uuids= []
        for u in id:
            try:
                valid_uuids.append(UUID(u))
            except ValueError:
                invalid_uuids.append(UUID(u))
        queryset = EntranceTestAbility.objects.filter(uuid__in=valid_uuids)
        count = queryset.count()
        queryset.delete()
        return Response({
            "statusCode":200,
            "status":True,
            "message":f"{count} EntranceTestAbility permanently deleted.",
            "data":{"invalid_uuids": invalid_uuids} if invalid_uuids else None
        },status = status.HTTP_200_OK)
    

#<=========================Relative==========================>

class RelativeCreateAPTView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
            try:
                serializer = RelativeSerializer(data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response({
                    "statusCode":201,
                    "status":True,
                    "message ": "Relative created successfully. ",
                    "data": serializer.data
                     },status=status.HTTP_201_CREATED)
                else:
                    return Response({
                        "statusCode":400,
                        "status":False,
                        "message":"Validation Faild. ",
                        "data":serializer.errors
                    },status=status.HTTP_400_BAD_REQUEST)
            except Exception as e :
                return Response({
                    "statusCode":500,
                    "status":False,
                    "message":"Something went wrong. ",
                    "error":str(e)
                },status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RelativeListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        queryset = Relative.objects.all()

        #filter 
        uuids = request.GET.get("uuids")
        if uuids:
            uuid_list = []
            for u in uuids.split(","):
                try:
                    uuid_list.append(UUID(u.strip()))
                except:
                    return Response({
                        "status" : False,
                        "message":f"Invalid UUID:{u}"
                       
                    },status=status.HTTP_400_BAD_REQUEST)
                
            queryset = queryset.filter(uuid__in=uuid_list)
        serializer = RelativeSerializer(queryset ,many=True)
        return Response({
            "status":True, 
            "message":"Relative data fatched successfully. ",
            "data":serializer.data,

            },status=status.HTTP_200_OK)

class RelativeDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request,uuid):
        try:
            valid_uuid = UUID(str(uuid))
        except:
            return Response({
                "status":False,
                "message":"Invalid UUID format",
            },status=status.HTTP_400_BAD_REQUEST)
        relative = get_object_or_404(Relative,uuid=valid_uuid)
        serializer = RelativeSerializer(relative)
        return Response({
            "status":True,
            "statusCode":200,
            "message":"Relative fetched successfully. ",
            "data": serializer.data
        },status=status.HTTP_200_OK)

class RelativeUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def put(self,request,uuid):
        try: 
            relative = Relative.objects.get(uuid=uuid)
        except Relative.DoesNotExist:
               return Response({
                "status": "error",
                "message": "Relative not found."
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            serializer = RelativeSerializer(relative,data = request.data, partial = True)
            serializer.is_valid(raise_exception=True)

            with transaction.atomic():
                relative = serializer.save()
            return Response({
                "status":True,
                "message":"Relative updated successfully.",
                "data":RelativeSerializer(relative).data
            },status = status.HTTP_200_OK)
        except serializers.ValidationError as ve:
            return Response({
                "status": "error",
                "message": "Validation failed.",
                "errors": ve.detail
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except IntegrityError as ie:
            return Response({
                "status": "error",
                "message": "Database integrity error.",
                "details": str(ie)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except ValidationError as ve:
            return Response({
                "status": "error",
                "message": "Validation failed.",
                "errors": ve.message_dict
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "status": "error",
                "message": "Something went wrong.",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class RelativeDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self,request,uuid=None):
        id = request.data.get('id',None)
        
        #single delete via url
        if uuid:
            try:
                obj = Relative.objects.get(uuid=uuid)
                obj.delete()
                return Response({
                    "statusCode":204,
                    "status":True,
                    "message":"Relative deleted.",
                    "data":None
                },status=status.HTTP_204_NO_CONTENT)
            except Relative.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status" :  False,
                    "message": "Relative not found. ",
                    "data":None        
                        },status=status.HTTP_404_NOT_FOUND)
        #delete all
        if id == "all":
            queryset = Relative.objects.all()
            count = queryset.count()
            queryset.delete()
            return Response({
                "statusCode":200,
                "status":True,
                "message": f"All {count} Relative permanently deleted. ",
                "data":None
            },status=status.HTTP_200_OK)
        
        #Bulk Delete
        if not id or not isinstance(id,list):
            return Response({
                "statusCode":400,
                "status":False,
                "message":"Please provide a list of U"
                "UIDs in 'id' field or 'all'.",
                "data":None
            },status= status.HTTP_400_BAD_REQUEST)
        valid_uuids= []
        invalid_uuids= []
        for u in id:
            try:
                valid_uuids.append(UUID(u))
            except ValueError:
                invalid_uuids.append(UUID(u))
        queryset = Relative.objects.filter(uuid__in=valid_uuids)
        count = queryset.count()
        queryset.delete()
        return Response({
            "statusCode":200,
            "status":True,
            "message":f"{count} Relative permanently deleted.",
            "data":{"invalid_uuids": invalid_uuids} if invalid_uuids else None
        },status = status.HTTP_200_OK)
    
#<================Visita_History====================>
class VisitHistoryCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            serializer = VisitHistorySerializer(data=request.data)
            if serializer.is_valid():
               serializer.save()
               return Response({
                 "statusCode":201,
                 "status":True,
                 "message":"Visit History created Successfully. ",
                 "data":serializer.data
                },status = status.HTTP_201_CREATED)
            else:
                return Response({
                    "statusCode":400,
                    "status":False,
                    "message":"Validation failed. ",
                    "error":serializer.errors
                },status=status.HTTP_400_BAD_REQUEST)
        except Exception as e :
                return Response({
                    "statusCode":500,
                    "status":False,
                    "message":"Something went wrong. ",
                    "error":str(e)
                },status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VisitHistoryListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        queryset = VisitHistory.objects.all()

        #filter 
        uuids = request.GET.get("uuids")
        if uuids:
            uuid_list = []
            for u in uuids.split(","):
                try:
                    uuid_list.append(UUID(u.strip()))
                except:
                    return Response({
                        "status" : False,
                        "message":f"Invalid UUID:{u}"
                       
                    },status=status.HTTP_400_BAD_REQUEST)
                
            queryset = queryset.filter(uuid__in=uuid_list)
        serializer = VisitHistorySerializer(queryset ,many=True)
        return Response({
            "status":True, 
            "message":"Visit History data fatched successfully. ",
            "data":serializer.data,

            },status=status.HTTP_200_OK)


class VisitHistoryDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request,uuid):
        try:
            valid_uuid = UUID(str(uuid))
        except:
            return Response({
                "status":False,
                "message":"Invalid UUID format",
            },status=status.HTTP_400_BAD_REQUEST)
        visit = get_object_or_404(VisitHistory,uuid=valid_uuid)
        serializer = VisitHistorySerializer(visit)
        return Response({
            "status":True,
            "statusCode":200,
            "message":"Visit History fetched successfully. ",
            "data": serializer.data
        },status=status.HTTP_200_OK)


class VisitHistoryUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def put(self,request,uuid):
        try: 
            visit = VisitHistory.objects.get(uuid=uuid)
        except VisitHistory.DoesNotExist:
               return Response({
                "status": "error",
                "message": "Visit History not found."
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            serializer = VisitHistorySerializer(visit,data = request.data, partial = True)
            serializer.is_valid(raise_exception=True)

            with transaction.atomic():
                visit = serializer.save()
            return Response({
                "status":True,
                "message":"Visit History updated successfully.",
                "data":VisitHistorySerializer(visit).data
            },status = status.HTTP_200_OK)
        except serializers.ValidationError as ve:
            return Response({
                "status": "error",
                "message": "Validation failed.",
                "errors": ve.detail
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except IntegrityError as ie:
            return Response({
                "status": "error",
                "message": "Database integrity error.",
                "details": str(ie)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except ValidationError as ve:
            return Response({
                "status": "error",
                "message": "Validation failed.",
                "errors": ve.message_dict
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "status": "error",
                "message": "Something went wrong.",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
       

class VisitHistoryDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self,request,uuid=None):
        id = request.data.get('id',None)
        
        #single delete via url
        if uuid:
            try:
                obj = VisitHistory.objects.get(uuid=uuid)
                obj.delete()
                return Response({
                    "statusCode":204,
                    "status":True,
                    "message":"visit history deleted.",
                    "data":None
                },status=status.HTTP_204_NO_CONTENT)
            except VisitHistory.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status" :  False,
                    "message": "Visit History not found. ",
                    "data":None        
                        },status=status.HTTP_404_NOT_FOUND)
        #delete all
        if id == "all":
            queryset = VisitHistory.objects.all()
            count = queryset.count()
            queryset.delete()
            return Response({
                "statusCode":200,
                "status":True,
                "message": f"All {count} Visit History permanently deleted. ",
                "data":None
            },status=status.HTTP_200_OK)
        
        #Bulk Delete
        if not id or not isinstance(id,list):
            return Response({
                "statusCode":400,
                "status":False,
                "message":"Please provide a list of U"
                "UIDs in 'id' field or 'all'.",
                "data":None
            },status= status.HTTP_400_BAD_REQUEST)
        valid_uuids= []
        invalid_uuids= []
        for u in id:
            try:
                valid_uuids.append(UUID(u))
            except ValueError:
                invalid_uuids.append(UUID(u))
        queryset = VisitHistory.objects.filter(uuid__in=valid_uuids)
        count = queryset.count()
        queryset.delete()
        return Response({
            "statusCode":200,
            "status":True,
            "message":f"{count} Visit History permanently deleted.",
            "data":{"invalid_uuids": invalid_uuids} if invalid_uuids else None
        },status = status.HTTP_200_OK)
    
#<=====================Refusal_History=====================>

class RefusalHistoryCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            serializer = RefusalHistorySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "statusCode":201,
                    "status":True,
                    "message":"Refusal History create Successfully. ",
                    "data":serializer.data
                },status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "statusCode":400,
                    "status":False,
                    "message": "Validation failed. ",
                    "error": serializer.errors
                },status = status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                    "statusCode":500,
                    "status":False,
                    "message":"Something went wrong. ",
                    "error":str(e)
                },status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RefusalHistoryListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        queryset = RefusalHistory.objects.all()

        #filter 
        uuids = request.GET.get("uuids")
        if uuids:
            uuid_list = []
            for u in uuids.split(","):
                try:
                    uuid_list.append(UUID(u.strip()))
                except:
                    return Response({
                        "status" : False,
                        "message":f"Invalid UUID:{u}"
                       
                    },status=status.HTTP_400_BAD_REQUEST)
                
            queryset = queryset.filter(uuid__in=uuid_list)
        serializer = RefusalHistorySerializer(queryset ,many=True)
        return Response({
            "status":True, 
            "message":"Refusal History data fatched successfully. ",
            "data":serializer.data,

            },status=status.HTTP_200_OK)


class RefusalHistoryDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request,uuid):
        try:
            valid_uuid = UUID(str(uuid))
        except:
            return Response({
                "status":False,
                "message":"Invalid UUID format",
            },status=status.HTTP_400_BAD_REQUEST)
        refusal = get_object_or_404(RefusalHistory,uuid=valid_uuid)
        serializer = RefusalHistorySerializer(refusal)
        return Response({
            "status":True,
            "statusCode":200,
            "message":"Refusal History fetched successfully. ",
            "data": serializer.data
        },status=status.HTTP_200_OK)


class RefusalHistoryUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def put(self,request,uuid):
        try: 
            refusal = RefusalHistory.objects.get(uuid=uuid)
        except RefusalHistory.DoesNotExist:
               return Response({
                "status": "error",
                "message": "Refusal History not found."
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            serializer = RefusalHistorySerializer(refusal,data = request.data, partial = True)
            serializer.is_valid(raise_exception=True)

            with transaction.atomic():
                refusal = serializer.save()
            return Response({
                "status":True,
                "message":"Refusal History updated successfully.",
                "data":RefusalHistorySerializer(refusal).data
            },status = status.HTTP_200_OK)
        except serializers.ValidationError as ve:
            return Response({
                "status": "error",
                "message": "Validation failed.",
                "errors": ve.detail
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except IntegrityError as ie:
            return Response({
                "status": "error",
                "message": "Database integrity error.",
                "details": str(ie)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except ValidationError as ve:
            return Response({
                "status": "error",
                "message": "Validation failed.",
                "errors": ve.message_dict
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "status": "error",
                "message": "Something went wrong.",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
       

class RefusalHistoryDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self,request,uuid=None):
        id = request.data.get('id',None)
        
        #single delete via url
        if uuid:
            try:
                obj = RefusalHistory.objects.get(uuid=uuid)
                obj.delete()
                return Response({
                    "statusCode":204,
                    "status":True,
                    "message":"Refusal History deleted.",
                    "data":None
                },status=status.HTTP_204_NO_CONTENT)
            except RefusalHistory.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status" :  False,
                    "message": "Refusal History not found. ",
                    "data":None        
                        },status=status.HTTP_404_NOT_FOUND)
        #delete all
        if id == "all":
            queryset = RefusalHistory.objects.all()
            count = queryset.count()
            queryset.delete()
            return Response({
                "statusCode":200,
                "status":True,
                "message": f"All {count} Refusal History permanently deleted. ",
                "data":None
            },status=status.HTTP_200_OK)
        
        #Bulk Delete
        if not id or not isinstance(id,list):
            return Response({
                "statusCode":400,
                "status":False,
                "message":"Please provide a list of U"
                "UIDs in 'id' field or 'all'.",
                "data":None
            },status= status.HTTP_400_BAD_REQUEST)
        valid_uuids= []
        invalid_uuids= []
        for u in id:
            try:
                valid_uuids.append(UUID(u))
            except ValueError:
                invalid_uuids.append(UUID(u))
        queryset = RefusalHistory.objects.filter(uuid__in=valid_uuids)
        count = queryset.count()
        queryset.delete()
        return Response({
            "statusCode":200,
            "status":True,
            "message":f"{count} Refusal History permanently deleted.",
            "data":{"invalid_uuids": invalid_uuids} if invalid_uuids else None
        },status = status.HTTP_200_OK)
    

#<=======================Business_Experience=====================>

class BusinessExperienceCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            serializer = BusinessExperienceSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "statusCode":201,
                    "status":True,
                    "message":"Business Experience create Successfully. ",
                    "data":serializer.data
                },status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "statusCode":400,
                    "status":False,
                    "message": "Validation failed. ",
                    "error": serializer.errors
                },status = status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                    "statusCode":500,
                    "status":False,
                    "message":"Something went wrong. ",
                    "error":str(e)
                },status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BusinessExperienceListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        queryset = BusinessExperience.objects.all()

        #filter 
        uuids = request.GET.get("uuids")
        if uuids:
            uuid_list = []
            for u in uuids.split(","):
                try:
                    uuid_list.append(UUID(u.strip()))
                except:
                    return Response({
                        "status" : False,
                        "message":f"Invalid UUID:{u}"
                       
                    },status=status.HTTP_400_BAD_REQUEST)
                
            queryset = queryset.filter(uuid__in=uuid_list)
        serializer = BusinessExperienceSerializer(queryset ,many=True)
        return Response({
            "status":True, 
            "message":"Business Experience data fatched successfully. ",
            "data":serializer.data,

            },status=status.HTTP_200_OK)


class BusinessExperienceDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request,uuid):
        try:
            valid_uuid = UUID(str(uuid))
        except:
            return Response({
                "status":False,
                "message":"Invalid UUID format",
            },status=status.HTTP_400_BAD_REQUEST)
        experiences = get_object_or_404(BusinessExperience,uuid=valid_uuid)
        serializer = BusinessExperienceSerializer(experiences)
        return Response({
            "status":True,
            "statusCode":200,
            "message":"Business Experience fetched successfully. ",
            "data": serializer.data
        },status=status.HTTP_200_OK)



class BusinessExperienceUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def put(self,request,uuid):
        try: 
            experiences = BusinessExperience.objects.get(uuid=uuid)
        except BusinessExperience.DoesNotExist:
               return Response({
                "status": "error",
                "message": "Business Experience not found."
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            serializer = BusinessExperienceSerializer(experiences,data = request.data, partial = True)
            serializer.is_valid(raise_exception=True)

            with transaction.atomic():
               experiences = serializer.save()
            return Response({
                "status":True,
                "message":"Refusal History updated successfully.",
                "data":BusinessExperienceSerializer(experiences).data
            },status = status.HTTP_200_OK)
        except serializers.ValidationError as ve:
            return Response({
                "status": "error",
                "message": "Validation failed.",
                "errors": ve.detail
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except IntegrityError as ie:
            return Response({
                "status": "error",
                "message": "Database integrity error.",
                "details": str(ie)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except ValidationError as ve:
            return Response({
                "status": "error",
                "message": "Validation failed.",
                "errors": ve.message_dict
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "status": "error",
                "message": "Something went wrong.",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class BusinessExperienceDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self,request,uuid=None):
        id = request.data.get('id',None)
        
        #single delete via url
        if uuid:
            try:
                obj = BusinessExperience.objects.get(uuid=uuid)
                obj.delete()
                return Response({
                    "statusCode":204,
                    "status":True,
                    "message":"Business Experience deleted.",
                    "data":None
                },status=status.HTTP_204_NO_CONTENT)
            except BusinessExperience.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status" :  False,
                    "message": "Business Experience not found. ",
                    "data":None        
                        },status=status.HTTP_404_NOT_FOUND)
        #delete all
        if id == "all":
            queryset = BusinessExperience.objects.all()
            count = queryset.count()
            queryset.delete()
            return Response({
                "statusCode":200,
                "status":True,
                "message": f"All {count} Business Experience permanently deleted. ",
                "data":None
            },status=status.HTTP_200_OK)
        
        #Bulk Delete
        if not id or not isinstance(id,list):
            return Response({
                "statusCode":400,
                "status":False,
                "message":"Please provide a list of U"
                "UIDs in 'id' field or 'all'.",
                "data":None
            },status= status.HTTP_400_BAD_REQUEST)
        valid_uuids= []
        invalid_uuids= []
        for u in id:
            try:
                valid_uuids.append(UUID(u))
            except ValueError:
                invalid_uuids.append(UUID(u))
        queryset = BusinessExperience.objects.filter(uuid__in=valid_uuids)
        count = queryset.count()
        queryset.delete()
        return Response({
            "statusCode":200,
            "status":True,
            "message":f"{count} Business Experience permanently deleted.",
            "data":{"invalid_uuids": invalid_uuids} if invalid_uuids else None
        },status = status.HTTP_200_OK)
    
#<=====================Net_worth=========================>
class NetworthCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            serializer = NetworthSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "statusCode":201,
                    "status":True,
                    "message":"Networth create successfully. ",
                    "data":serializer.data
                },status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "statusCode":400,
                    "status":False,
                    "message":"Validation Faild",
                    "error":serializer.errors
                },status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "statusCode":500,
                "status":False,
                "message":"Something went wrong. ",
                "error":str(e)
            },status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NetworthListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        queryset = Networth.objects.all()

        #filter
        uuids = request.GET.get("uuids")
        if uuids:
            uuid_list = []
            for u in uuids.split(","):
                try:
                    uuid_list.append(UUID(u.strip()))
                except:
                    return Response({
                        "status":False,
                        "message":f"Invalid UUID:{u}"
                    },status=status.HTTP_400_BAD_REQUEST)
            queryset = queryset.filter(uuid_in=uuid_list)

        serializer = NetworthSerializer(queryset,many=True)
        return Response({
            "status":True,
            "message":"Networth data fatched successfully. ",
            "data":serializer.data,
        },status=status.HTTP_200_OK)

class NetworthDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request,uuid):
        try:
            valid_uuid = UUID(str(uuid))
        except:
            return Response({
                "statusCode":400,
                "status":False,
                "message":"Invalide UUID format"
            },status=status.HTTP_400_BAD_REQUEST)
        networth = get_object_or_404(Networth,uuid=valid_uuid)
        serializer = NetworthSerializer(networth)
        return Response({
            "status":True,
            "message":"Networth fetched successfully. ",
            "data":serializer.data
        },status=status.HTTP_200_OK)

class NetworthUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def put(self,request,uuid):
        try: 
            networth = Networth.objects.get(uuid=uuid)
        except Networth.DoesNotExist:
               return Response({
                "status": "error",
                "message": "Networth not found."
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            serializer = NetworthSerializer(networth,data = request.data, partial = True)
            serializer.is_valid(raise_exception=True)

            with transaction.atomic():
               networth = serializer.save()
            return Response({
                "status":True,
                "message":"Networth updated successfully.",
                "data":NetworthSerializer(networth).data
            },status = status.HTTP_200_OK)
        except serializers.ValidationError as ve:
            return Response({
                "status": "error",
                "message": "Validation failed.",
                "errors": ve.detail
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except IntegrityError as ie:
            return Response({
                "status": "error",
                "message": "Database integrity error.",
                "details": str(ie)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except ValidationError as ve:
            return Response({
                "status": "error",
                "message": "Validation failed.",
                "errors": ve.message_dict
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "status": "error",
                "message": "Something went wrong.",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class NetworthDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self,request,uuid=None):
        id = request.data.get('id',None)
        
        #single delete via url
        if uuid:
            try:
                obj = Networth.objects.get(uuid=uuid)
                obj.delete()
                return Response({
                    "statusCode":204,
                    "status":True,
                    "message":"Networth deleted.",
                    "data":None
                },status=status.HTTP_204_NO_CONTENT)
            except Networth.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status" :  False,
                    "message": "Networth not found. ",
                    "data":None        
                        },status=status.HTTP_404_NOT_FOUND)
        #delete all
        if id == "all":
            queryset = Networth.objects.all()
            count = queryset.count()
            queryset.delete()
            return Response({
                "statusCode":200,
                "status":True,
                "message": f"All {count} Networth permanently deleted. ",
                "data":None
            },status=status.HTTP_200_OK)
        
        #Bulk Delete
        if not id or not isinstance(id,list):
            return Response({
                "statusCode":400,
                "status":False,
                "message":"Please provide a list of U"
                "UIDs in 'id' field or 'all'.",
                "data":None
            },status= status.HTTP_400_BAD_REQUEST)
        valid_uuids= []
        invalid_uuids= []
        for u in id:
            try:
                valid_uuids.append(UUID(u))
            except ValueError:
                invalid_uuids.append(UUID(u))
        queryset = Networth.objects.filter(uuid__in=valid_uuids)
        count = queryset.count()
        queryset.delete()
        return Response({
            "statusCode":200,
            "status":True,
            "message":f"{count} Networth permanently deleted.",
            "data":{"invalid_uuids": invalid_uuids} if invalid_uuids else None
        },status = status.HTTP_200_OK)
    
#<============================EligibilityFlags============================>
class EligibilityFlagsRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, applicant_uuid):
        applicant = get_object_or_404(Applicant, uuid=applicant_uuid)
        flags = get_object_or_404(EligibilityFlags, applicant=applicant)

        serializer = EligibilityFlagsSerializer(flags)

        return Response({
            "status": True,
            "message": "Eligibility flags fetched successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
class EligibilityFlagsUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, applicant_uuid):
        applicant = get_object_or_404(Applicant, uuid=applicant_uuid)
        flags = get_object_or_404(EligibilityFlags, applicant=applicant)

        serializer = EligibilityFlagsSerializer(flags, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response({
                "status": True,
                "message": "Eligibility flags updated successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "status": False,
            "message": "Validation failed.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class EligibilityFlagsCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = EligibilityFlagsSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "statusCode": 201,
                    "status": True,
                    "message": "Eligibility flags created successfully.",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)

            return Response({
                "statusCode": 400,
                "status": False,
                "message": "Validation failed.",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "statusCode": 500,
                "status": False,
                "message": "Something went wrong.",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#<========================SpouseEducation=======================>
class SpouseEducationleadCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            serializer = SpouseEducationleadSerializer(data = request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "statusCode":201,
                    "status":True,
                    "message":"Spouse Education create successfully. ",
                    "data":serializer.data
                },status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "statusCode":400,
                    "status":False,
                    "message":"Validation Faild. ",
                    "error":serializer.errors
                },status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "statusCode":500,
                "status":False,
                "message":"Something went wrong.",
                "error":str(e)
            },status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class SpouseEducationleadListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        queryset = SpouseEducationlead.objects.all()

        #filter
        uuids = request.GET.get("uuids")
        if uuids:
            uuid_list = []
            for u in uuids.split(","):
                try:
                    uuid_list.append(UUID(u.strip()))
                except:
                    return Response({
                        "status":False,
                        "message":f"Invalid UUID:{u}"
                    },status=status.HTTP_400_BAD_REQUEST)
            queryset = queryset.filter(uuid_in=uuid_list)

        serializer = SpouseEducationleadSerializer(queryset,many=True)
        return Response({
            "status":True,
            "message":"Spouse Education data fatched successfully. ",
            "data":serializer.data,
        },status=status.HTTP_200_OK)

class SpouseEducationleadDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request,uuid):
        try:
            valid_uuid = UUID(str(uuid))
        except:
            return Response({
                "statusCode":400,
                "status":False,
                "message":"Invalide UUID format"
            },status=status.HTTP_400_BAD_REQUEST)
        spouse = get_object_or_404(SpouseEducationlead,uuid=valid_uuid)
        serializer = SpouseEducationleadSerializer(spouse)
        return Response({
            "status":True,
            "message":"Spouse Education fetched successfully. ",
            "data":serializer.data
        },status=status.HTTP_200_OK)

class SpouseEducationleadUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def put(self,request,uuid):
        try: 
            spouse = SpouseEducationlead.objects.get(uuid=uuid)
        except SpouseEducationlead.DoesNotExist:
               return Response({
                "status": "error",
                "message": "Spouse Educationlead not found."
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            serializer = SpouseEducationleadSerializer(spouse,data = request.data, partial = True)
            serializer.is_valid(raise_exception=True)

            with transaction.atomic():
               spouse = serializer.save()
            return Response({
                "status":True,
                "message":"Spouse Educationlead updated successfully.",
                "data":SpouseEducationleadSerializer(spouse).data
            },status = status.HTTP_200_OK)
        except serializers.ValidationError as ve:
            return Response({
                "status": "error",
                "message": "Validation failed.",
                "errors": ve.detail
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except IntegrityError as ie:
            return Response({
                "status": "error",
                "message": "Database integrity error.",
                "details": str(ie)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except ValidationError as ve:
            return Response({
                "status": "error",
                "message": "Validation failed.",
                "errors": ve.message_dict
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "status": "error",
                "message": "Something went wrong.",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class SpouseEducationleadDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self,request,uuid=None):
        id = request.data.get('id',None)
        
        #single delete via url
        if uuid:
            try:
                obj = SpouseEducationlead.objects.get(uuid=uuid)
                obj.delete()
                return Response({
                    "statusCode":204,
                    "status":True,
                    "message":"Spouse Educationlead deleted.",
                    "data":None
                },status=status.HTTP_204_NO_CONTENT)
            except SpouseEducationlead.DoesNotExist:
                return Response({
                    "statusCode": 404,
                    "status" :  False,
                    "message": "Spouse Educationlead not found. ",
                    "data":None        
                        },status=status.HTTP_404_NOT_FOUND)
        #delete all
        if id == "all":
            queryset = SpouseEducationlead.objects.all()
            count = queryset.count()
            queryset.delete()
            return Response({
                "statusCode":200,
                "status":True,
                "message": f"All {count} Spouse Educationlead permanently deleted. ",
                "data":None
            },status=status.HTTP_200_OK)
        
        #Bulk Delete
        if not id or not isinstance(id,list):
            return Response({
                "statusCode":400,
                "status":False,
                "message":"Please provide a list of U"
                "UIDs in 'id' field or 'all'.",
                "data":None
            },status= status.HTTP_400_BAD_REQUEST)
        valid_uuids= []
        invalid_uuids= []
        for u in id:
            try:
                valid_uuids.append(UUID(u))
            except ValueError:
                invalid_uuids.append(UUID(u))
        queryset = SpouseEducationlead.objects.filter(uuid__in=valid_uuids)
        count = queryset.count()
        queryset.delete()
        return Response({
            "statusCode":200,
            "status":True,
            "message":f"{count} SpouseEducationlead permanently deleted.",
            "data":{"invalid_uuids": invalid_uuids} if invalid_uuids else None
        },status = status.HTTP_200_OK)
    
class LeadDocumentCreateAPI(APIView):
    
    def post(self, request):
        files = request.FILES.getlist("attachments")

        # Convert uploaded files to URLs
        file_urls = []
        for f in files:
            path = default_storage.save(f"documents/{f.name}", f)
            file_urls.append(default_storage.url(path))

        # Create serializer input
        payload = {
            "applicant": request.data.get("applicant"),
            "documentcategory": request.data.get("documentcategory"),
            "documentname": request.data.get("documentname"),
            "attachments": file_urls
        }

        serializer = LeadDocumentSerializer(data=payload)
        serializer.is_valid(raise_exception=True)

        # Create model
        lead_doc = LeadDocument.objects.create(
            applicant_id = Applicant.objects.get(uuid=serializer.validated_data["applicant"]).id,
            documentcategory_id = DocumentCategory.objects.get(uuid=serializer.validated_data["documentcategory"]).id,
            documentname_id = DocumentName.objects.get(uuid=serializer.validated_data["documentname"]).id,
            attachments = file_urls
        )

        return Response({
            "uuid": lead_doc.uuid,
            "applicant": str(lead_doc.applicant.uuid),
            "documentcategory": str(lead_doc.documentcategory.uuid),
            "documentname": str(lead_doc.documentname.uuid),
            "attachments": file_urls,
            "created_at": lead_doc.created_at
        })
