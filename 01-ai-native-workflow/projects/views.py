from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import FolderForm, PDFUploadForm, ProjectForm, ReflectionForm, TaskForm
from .models import PDF, Project, Task
from .services import analyze_project, extract_pdf_text, generate_roadmap, next_best_action


def home(request):
	if request.user.is_authenticated:
		return redirect("dashboard")
	return render(request, "projects/landing.html")


@login_required
def dashboard(request):
	projects = request.user.projects.prefetch_related("pdfs", "weeks")
	return render(request, "projects/dashboard.html", {"projects": projects})


def register(request):
	if request.method == "POST":
		form = UserCreationForm(request.POST)
		if form.is_valid():
			user = form.save()
			login(request, user)
			return redirect("dashboard")
	else:
		form = UserCreationForm()
	return render(request, "projects/form.html", {"form": form, "title": "Create account"})


@login_required
def project_create(request):
	form = ProjectForm(request.POST or None)
	if form.is_valid():
		project = form.save(commit=False)
		project.owner = request.user
		project.save()
		return redirect("project-detail", project.pk)
	return render(request, "projects/form.html", {"form": form, "title": "New project"})


@login_required
def project_detail(request, project_id):
	project = get_object_or_404(Project, pk=project_id, owner=request.user)
	return render(request, "projects/project_detail.html", {"project": project, "upload_form": PDFUploadForm(), "folder_form": FolderForm()})


@login_required
def upload_pdfs(request, project_id):
	project = get_object_or_404(Project, pk=project_id, owner=request.user)
	for uploaded_file in request.FILES.getlist("files"):
		text, warning = extract_pdf_text(uploaded_file)
		PDF.objects.create(project=project, file=uploaded_file, extracted_text=text, extraction_warning=warning)
	return redirect("project-detail", project.pk)


@login_required
def create_folder(request, project_id):
	project = get_object_or_404(Project, pk=project_id, owner=request.user)
	form = FolderForm(request.POST)
	if form.is_valid():
		folder = form.save(commit=False)
		folder.project = project
		folder.save()
	return redirect("project-detail", project.pk)


@login_required
def delete_pdf(request, project_id, pdf_id):
	project = get_object_or_404(Project, pk=project_id, owner=request.user)
	if request.method == "POST":
		get_object_or_404(PDF, pk=pdf_id, project=project).delete()
	return redirect("project-detail", project.pk)


@login_required
def analyze(request, project_id):
	project = get_object_or_404(Project, pk=project_id, owner=request.user)
	analyze_project(project)
	return redirect("project-review", project.pk)


@login_required
def review(request, project_id):
	project = get_object_or_404(Project, pk=project_id, owner=request.user)
	if request.method == "POST":
		for requirement in project.requirements.all():
			requirement.confirmed = f"requirement-{requirement.pk}" in request.POST
			requirement.save(update_fields=["confirmed"])
		for topic in project.learning_topics.all():
			topic.confirmed = f"topic-{topic.pk}" in request.POST
			topic.save(update_fields=["confirmed"])
		project.analysis_confirmed = True
		project.save(update_fields=["analysis_confirmed"])
		generate_roadmap(project)
		return redirect("roadmap", project.pk)
	return render(request, "projects/review.html", {"project": project})


@login_required
def roadmap_generate(request, project_id):
	project = get_object_or_404(Project, pk=project_id, owner=request.user)
	generate_roadmap(project)
	return redirect("roadmap", project.pk)


@login_required
def roadmap(request, project_id):
	project = get_object_or_404(Project, pk=project_id, owner=request.user)
	return render(request, "projects/roadmap.html", {"project": project, "action": next_best_action(project)})


@login_required
def task_update(request, project_id, task_id):
	project = get_object_or_404(Project, pk=project_id, owner=request.user)
	task = get_object_or_404(Task, pk=task_id, week__project=project)
	form = TaskForm(request.POST, instance=task)
	if form.is_valid():
		form.save()
	if project.is_complete and project.completed_at is None:
		project.completed_at = timezone.now()
		project.save(update_fields=["completed_at"])
	return redirect("roadmap", project.pk)


@login_required
def reflection(request, project_id):
	project = get_object_or_404(Project, pk=project_id, owner=request.user)
	instance = getattr(project, "reflection", None)
	form = ReflectionForm(request.POST or None, instance=instance)
	if request.method == "POST" and form.is_valid():
		saved = form.save(commit=False)
		saved.project = project
		saved.save()
		return redirect("project-complete", project.pk)
	return render(request, "projects/reflection.html", {"project": project, "form": form})


@login_required
def project_complete(request, project_id):
	project = get_object_or_404(Project, pk=project_id, owner=request.user)
	return render(request, "projects/complete.html", {"project": project})
