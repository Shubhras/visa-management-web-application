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