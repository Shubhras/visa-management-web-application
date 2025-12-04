# from tablib import Dataset
# from django.forms.models import model_to_dict

# def generate_dependency_report(obj):
#     """
#     Creates a dependency report for all child tables
#     pointing to this object.
#     """
#     dataset = Dataset()
#     dataset.title = "Dependency Report"

#     dataset.headers = [
#         "Parent Table",
#         "Parent UUID",
#         "Child Table",
#         "Child Record",
#         "Child UUID"
#     ]

#     parent_model = obj.__class__.__name__
#     parent_uuid = str(obj.uuid)

#     # Scan all reverse FK / M2M relations
#     for rel in obj._meta.get_fields():
#         if rel.auto_created and not rel.concrete:
#             accessor = rel.get_accessor_name()
#             related_model = rel.related_model

#             try:
#                 manager = getattr(obj, accessor)
#                 children = manager.all()
#             except:
#                 continue

#             for child in children:
#                 dataset.append([
#                     parent_model,
#                     parent_uuid,
#                     related_model.__name__,
#                     str(child),
#                     str(getattr(child, "uuid", "")),
#                 ])

#     return dataset






# utils.py
import io
from django.apps import apps
from django.http import HttpResponse
from openpyxl import Workbook


# def generate_dependency_excel(data, filename="dependency_report.xlsx"):
#     """
#     data structure example:
#     [
#         {
#             "parent_name": "Male",
#             "dependencies": [
#                 {"table": "Student", "field": "gender"},
#                 {"table": "Employee", "field": "gender"},
#             ]
#         }
#     ]
#     """

#     wb = Workbook()
#     ws = wb.active
#     ws.title = "Dependencies"

#     # header
#     ws.append(["Parent Name", "Used In Table", "Field"])

#     for entry in data:
#         # parent_id = entry.get("parent_id", "")
#         parent_name = entry.get("parent_name", "")

#         for dep in entry.get("dependencies", []):
#             ws.append([
#                 # parent_id,
#                 parent_name,
#                 dep.get("table", ""),
#                 dep.get("field", ""),
#                 # dep.get("child_id", "")
#             ])

#     stream = io.BytesIO()
#     wb.save(stream)
#     stream.seek(0)

#     response = HttpResponse(
#         stream.getvalue(),
#         content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#     )
#     response["Content-Disposition"] = f'attachment; filename="{filename}"'
#     return response




# def find_dependencies(instance):
#     """
#     Returns list of dependencies:
#     [
#         {"table": "Student", "field": "gender"},
#         ...
#     ]
#     """
#     deps = []

#     for rel in instance._meta.related_objects:
#         model = rel.related_model
#         field_name = rel.field.name

#         related_exists  = model.objects.filter(**{field_name: instance}).exists()

#         if related_exists:
#             deps.append({
#                 "table": model.__name__,
#                 "field": field_name
#                 # "child_id": str(getattr(child, "uuid", child.pk))
#             })

#     return deps


def generate_dependency_excel(data, filename="dependency_report.xlsx"):
    wb = Workbook()
    ws = wb.active
    ws.title = "Dependencies"

    # Correct Headers
    ws.append([
        "Parent Table Name",
        "Parent Field Name",
        "Used In Table",
        "Field"
    ])

    for entry in data:
        ws.append([
            entry.get("parent_table", ""),
            entry.get("parent_field_value", ""),
            entry.get("used_in_table", ""),
            entry.get("field", "")
        ])

    stream = io.BytesIO()
    wb.save(stream)
    stream.seek(0)

    response = HttpResponse(
        stream.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


def find_dependencies(instance, parent_field_label="name"):
    """
    Returns list like:
    [
        {
            "parent_table": "Gender",
            "parent_field_value": "Female",
            "used_in_table": "Applicant",
            "field": "gender"
        }
    ]
    """

    deps = []
    parent_table = instance.__class__.__name__
    parent_field_value = getattr(instance, parent_field_label, "")

    for rel in instance._meta.related_objects:
        model = rel.related_model
        field_name = rel.field.name

        related_qs = model.objects.filter(**{field_name: instance})

        if related_qs.exists():
            deps.append({
                "parent_table": parent_table,
                "parent_field_value": parent_field_value,
                "used_in_table": model.__name__,
                "field": field_name
            })

    return deps
