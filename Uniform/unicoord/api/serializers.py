from rest_framework import serializers
from .models import Module3D

class Module3DSerializer(serializers.ModelSerializer):
    updated_file_url = serializers.SerializerMethodField()  # MethodField define karna zaroori hai

    class Meta:
        model = Module3D
        fields = ['id', 'name', 'file', 'updated_file', 'updated_file_url', 'scale', 'color', 'created_at', 'updated_at']

    def get_updated_file_url(self, obj):
        request = self.context.get('request')
        if obj.updated_file and request:
            return request.build_absolute_uri(obj.updated_file.url)
        return None