from tablib import Dataset
from django.forms.models import model_to_dict

def generate_dependency_report(obj):
    """
    Creates a dependency report for all child tables
    pointing to this object.
    """
    dataset = Dataset()
    dataset.title = "Dependency Report"

    dataset.headers = [
        "Parent Table",
        "Parent UUID",
        "Child Table",
        "Child Record",
        "Child UUID"
    ]

    parent_model = obj.__class__.__name__
    parent_uuid = str(obj.uuid)

    # Scan all reverse FK / M2M relations
    for rel in obj._meta.get_fields():
        if rel.auto_created and not rel.concrete:
            accessor = rel.get_accessor_name()
            related_model = rel.related_model

            try:
                manager = getattr(obj, accessor)
                children = manager.all()
            except:
                continue

            for child in children:
                dataset.append([
                    parent_model,
                    parent_uuid,
                    related_model.__name__,
                    str(child),
                    str(getattr(child, "uuid", "")),
                ])

    return dataset
