from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction, IntegrityError
from django.core.exceptions import ValidationError
from .models import Applicant
from .serializers import ApplicantSerializer
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
