from django import forms

from .models import Folder, Project, Reflection, Task


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["title", "deadline"]
        widgets = {"deadline": forms.DateInput(attrs={"type": "date"})}


class FolderForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ["name"]


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class PDFUploadForm(forms.Form):
    files = forms.FileField(widget=MultipleFileInput(attrs={"multiple": True}))


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "description", "status", "weight", "due_date", "required"]
        widgets = {"due_date": forms.DateInput(attrs={"type": "date"})}


class ReflectionForm(forms.ModelForm):
    class Meta:
        model = Reflection
        fields = ["what_went_well", "what_was_difficult"]