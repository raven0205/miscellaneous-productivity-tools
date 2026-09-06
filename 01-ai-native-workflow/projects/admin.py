from django.contrib import admin

# Register your models here.
from .models import Folder, LearningTopic, PDF, Project, Reflection, Requirement, Resource, Task, Week

admin.site.register([Project, Folder, PDF, Requirement, LearningTopic, Week, Task, Resource, Reflection])
