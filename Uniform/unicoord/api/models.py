from django.db import models

class Module3D(models.Model):
    name = models.CharField(max_length=200)
    file = models.FileField(upload_to="models/")  # original blend/3d file
    updated_file = models.FileField(upload_to="updated/", null=True, blank=True)
    
    scale = models.FloatField(default=1.0)
    color = models.JSONField(default=dict) 

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
