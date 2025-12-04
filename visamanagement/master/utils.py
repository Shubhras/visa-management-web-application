import io
from django.apps import apps
from django.http import HttpResponse
from openpyxl import Workbook
 
 
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