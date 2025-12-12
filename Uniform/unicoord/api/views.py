import os
import json
import subprocess
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Module3D
from .serializers import Module3DSerializer


class Module3DCreateView(APIView):
    def post(self, request):
        serializer = Module3DSerializer(data=request.data)

        if serializer.is_valid():
            module = serializer.save()
            print(" Module saved:", module.name)

            # Blender script path
            script_path = os.path.join(settings.BASE_DIR, "blender_scripts/modify_model.py")
            blender_path = "/home/admin/Documents/blender-5.0.0-linux-x64/blender"  # Ubuntu path
            print("Blender script path:", script_path)

            # Ensure updated folder exists
            updated_folder = os.path.join(settings.MEDIA_ROOT, "updated")
            os.makedirs(updated_folder, exist_ok=True)
            print("Updated folder path:", updated_folder)

            # Output file path
            output_filename = f"updated_{module.id}.glb"  # ya .gltf agar chahen
            output_path = os.path.join(updated_folder, output_filename)
            print("Output path for Blender:", output_path)

            # Blender payload (keys must match Blender script)
            payload = {
                "input_file": module.file.path,
                "output_file": output_path,
                "scale": module.scale,
                "colors": module.color
            }
            args = json.dumps(payload)
            print("Blender payload:", args)

            # Blender command
            command = [
                blender_path,
                "--background",   # -b
                "--python", script_path,
                "--",
                args
            ]
            print("Blender command:", " ".join(command))

            # Run Blender
            result = subprocess.run(command, capture_output=True, text=True)
            print("Blender stdout:", result.stdout)
            print("Blender stderr:", result.stderr)
            print("Blender returncode:", result.returncode)

            if result.returncode != 0:
                return Response({
                    "error": "Blender processing failed",
                    "details": result.stderr
                }, status=500)

            # Save updated file in model
            module.updated_file = f"updated/{output_filename}"
            module.save()
            print("Updated file assigned:", module.updated_file)

            return Response({
                "message": "3D model processed successfully",
                "data": Module3DSerializer(module, context={'request': request}).data,
                "updated_model_url": request.build_absolute_uri(module.updated_file.url)
            })

        print("Serializer errors:", serializer.errors)
        return Response(serializer.errors, status=400)

class Module3DUpdateView(APIView):
    """Handles full update (PUT) and partial update (PATCH) with Blender processing"""

    def _process_blender(self, module, request):
        """Run Blender script and update the module file"""
        script_path = os.path.join(settings.BASE_DIR, "blender_scripts/modify_model.py")
        blender_path = "/home/admin/Documents/blender-5.0.0-linux-x64/blender"

        # Ensure updated folder exists
        updated_folder = os.path.join(settings.MEDIA_ROOT, "updated")
        os.makedirs(updated_folder, exist_ok=True)

        # Output file path
        output_filename = f"updated_{module.id}.glb"
        output_path = os.path.join(updated_folder, output_filename)

        # Blender payload
        payload = {
            "input_file": module.file.path,
            "output_file": output_path,
            "scale": module.scale,
            "colors": module.color
        }
        args = json.dumps(payload)

        # Blender command
        command = [
            blender_path,
            "--background",
            "--python", script_path,
            "--",
            args
        ]

        # Run Blender
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            return {"error": "Blender processing failed", "details": result.stderr}

        # Save updated file in model
        module.updated_file = f"updated/{output_filename}"
        module.save()
        return None

    def put(self, request, pk):
        """Full update"""
        return self._update_module(request, pk, partial=False)

    def patch(self, request, pk):
        """Partial update"""
        return self._update_module(request, pk, partial=True)

    def _update_module(self, request, pk, partial=False):
        try:
            module = Module3D.objects.get(pk=pk)
        except Module3D.DoesNotExist:
            return Response({"error": "Module not found"}, status=404)

        serializer = Module3DSerializer(
            module,
            data=request.data,
            partial=partial,
            context={'request': request}
        )

        if serializer.is_valid():
            module = serializer.save()

            # Blender processing
            blender_error = self._process_blender(module, request)
            if blender_error:
                return Response(blender_error, status=500)

            return Response({
                "message": "Module updated and processed successfully",
                "data": Module3DSerializer(module, context={'request': request}).data,
                "updated_model_url": request.build_absolute_uri(module.updated_file.url)
            })

        return Response(serializer.errors, status=400)
