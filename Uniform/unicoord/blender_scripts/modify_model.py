# import bpy
# import sys
# import json

# # Read JSON args
# argv = sys.argv
# argv = argv[argv.index("--") + 1:]
# data = json.loads(argv[0])

# input_file = data["input_file"]
# output_file = data["output_file"]
# scale = data.get("scale", 1.0)
# colors = data.get("colors", {})

# print("Input:", input_file)
# print("Output:", output_file)

# # Reset
# bpy.ops.wm.read_factory_settings(use_empty=True)

# # Import GLB
# bpy.ops.import_scene.gltf(filepath=input_file)

# # Apply scale
# for obj in bpy.data.objects:
#     if obj.type == 'MESH':
#         obj.scale = (scale, scale, scale)

# # Apply colors
# for obj in bpy.data.objects:
#     if obj.type == 'MESH':
#         name = obj.name

#         if name in colors:
#             hex_color = colors[name]

#             r = int(hex_color[1:3], 16) / 255
#             g = int(hex_color[3:5], 16) / 255
#             b = int(hex_color[5:7], 16) / 255

#             # Always create new material
#             mat = bpy.data.materials.new(name=f"Mat_{name}")
#             mat.use_nodes = True

#             # Clear old nodes
#             nodes = mat.node_tree.nodes
#             for n in nodes:
#                 nodes.remove(n)

#             # Add new BSDF
#             bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
#             bsdf.inputs["Base Color"].default_value = (r, g, b, 1)

#             output_node = nodes.new(type="ShaderNodeOutputMaterial")
#             mat.node_tree.links.new(bsdf.outputs["BSDF"], output_node.inputs["Surface"])

#             # Assign to mesh
#             obj.data.materials.clear()
#             obj.data.materials.append(mat)

#             print(f"✔ Color applied: {name} → {hex_color}")

# # Export GLB
# bpy.ops.export_scene.gltf(filepath=output_file, export_format="GLB")

# print("Export Done")


import bpy
import json
import sys
import os

# -------------------------------
# 1. READ PAYLOAD
# -------------------------------
args = sys.argv

if "--" not in args:
    raise Exception("❌ No JSON payload passed to Blender script")

json_data = args[args.index("--") + 1]
payload = json.loads(json_data)

input_file = payload.get("input_file")
output_file = payload.get("output_file")
scale = payload.get("scale", 1)
colors = payload.get("colors", {})

print("========== BLENDER SCRIPT START ==========")
print("Input file:", input_file)
print("Output file:", output_file)
print("Scale:", scale)
print("Colors:", colors)
print("==========================================")

# -------------------------------
# 2. CLEAR DEFAULT OBJECTS
# -------------------------------
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# -------------------------------
# 3. IMPORT MODEL
# -------------------------------
print("Importing GLB:", input_file)
bpy.ops.import_scene.gltf(filepath=input_file)
print("✔ Model Import Successful")

# -------------------------------
# 4. APPLY SCALE TO ALL OBJECTS
# -------------------------------
for obj in bpy.data.objects:
    obj.scale = (scale, scale, scale)

print("✔ Scale Applied")

# -------------------------------
# 5. APPLY COLORS TO MESH NODES
# -------------------------------
def hex_to_rgb(hex_color):
    """Convert #RRGGBB → Blender RGB"""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) / 255 for i in (0, 2, 4))


for mesh_name, hex_color in colors.items():
    print(f"Processing Mesh: {mesh_name} → {hex_color}")

    obj = bpy.data.objects.get(mesh_name)

    if obj is None:
        print(f"❌ Mesh Not Found: {mesh_name}")
        continue

    # Create RGB tuple
    rgb = hex_to_rgb(hex_color)

    # Create new material
    mat = bpy.data.materials.new(name=f"MAT_{mesh_name}")
    mat.use_nodes = True

    # Change Base Color
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (rgb[0], rgb[1], rgb[2], 1)
    else:
        print(f"⚠ No Principled BSDF on {mesh_name}")

    # Assign material
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

    print(f"✔ Color Applied: {mesh_name} → {rgb}")

print("✔ All Color Operations Completed")

# -------------------------------
# 6. EXPORT UPDATED GLB
# -------------------------------
print("Exporting Updated GLB:", output_file)
bpy.ops.export_scene.gltf(filepath=output_file, export_format='GLB')
print("✔ Export Completed")

print("========== BLENDER SCRIPT END ==========")
