from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Project(models.Model):
	owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="projects")
	title = models.CharField(max_length=200)
	deadline = models.DateField()
	created_at = models.DateTimeField(auto_now_add=True)
	analysis_confirmed = models.BooleanField(default=False)
	completed_at = models.DateTimeField(null=True, blank=True)

	class Meta:
		ordering = ["deadline", "title"]

	def __str__(self):
		return self.title

	@property
	def is_complete(self):
		tasks = Task.objects.filter(week__project=self, required=True)
		return tasks.exists() and not tasks.exclude(status=Task.Status.DONE).exists()

	def progress(self):
		tasks = list(Task.objects.filter(week__project=self))
		total_weight = sum(task.weight for task in tasks)
		completed_weight = sum(task.weight for task in tasks if task.status == Task.Status.DONE)
		return round(completed_weight / total_weight * 100, 1) if total_weight else 0

	def expected_progress(self):
		today = timezone.localdate()
		start = self.created_at.date()
		total_days = max((self.deadline - start).days, 1)
		elapsed_days = min(max((today - start).days, 0), total_days)
		return round(elapsed_days / total_days * 100, 1)

	def tracking_status(self):
		return "On Track" if self.progress() >= self.expected_progress() * 0.7 else "At Risk"


class Folder(models.Model):
	project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="folders")
	name = models.CharField(max_length=120)

	class Meta:
		constraints = [models.UniqueConstraint(fields=["project", "name"], name="unique_folder_name_per_project")]

	def __str__(self):
		return self.name


class PDF(models.Model):
	project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="pdfs")
	folder = models.ForeignKey(Folder, on_delete=models.SET_NULL, null=True, blank=True, related_name="pdfs")
	file = models.FileField(upload_to="project-pdfs/")
	extracted_text = models.TextField(blank=True)
	extraction_warning = models.BooleanField(default=False)
	uploaded_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.file.name


class Requirement(models.Model):
	project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="requirements")
	text = models.TextField()
	confirmed = models.BooleanField(default=False)

	def __str__(self):
		return self.text[:80]


class LearningTopic(models.Model):
	project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="learning_topics")
	name = models.CharField(max_length=200)
	confirmed = models.BooleanField(default=False)

	def __str__(self):
		return self.name


class Week(models.Model):
	project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="weeks")
	number = models.PositiveIntegerField()
	start_date = models.DateField()
	end_date = models.DateField()
	topic = models.CharField(max_length=200, blank=True)

	class Meta:
		ordering = ["number"]
		constraints = [models.UniqueConstraint(fields=["project", "number"], name="unique_week_number_per_project")]

	def __str__(self):
		return f"Week {self.number}: {self.project.title}"


class Task(models.Model):
	class Status(models.TextChoices):
		NOT_STARTED = "not_started", "Not Started"
		IN_PROGRESS = "in_progress", "In Progress"
		DONE = "done", "Done"

	week = models.ForeignKey(Week, on_delete=models.CASCADE, related_name="tasks")
	title = models.CharField(max_length=250)
	description = models.TextField(blank=True)
	status = models.CharField(max_length=20, choices=Status.choices, default=Status.NOT_STARTED)
	weight = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
	due_date = models.DateField(null=True, blank=True)
	required = models.BooleanField(default=True)
	dependencies = models.ManyToManyField("self", symmetrical=False, blank=True, related_name="dependents")

	class Meta:
		ordering = ["due_date", "id"]

	def __str__(self):
		return self.title


class Resource(models.Model):
	week = models.ForeignKey(Week, on_delete=models.CASCADE, related_name="resources")
	title = models.CharField(max_length=200)
	url = models.URLField()
	trusted = models.BooleanField(default=True)

	def __str__(self):
		return self.title


class Reflection(models.Model):
	project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name="reflection")
	what_went_well = models.TextField()
	what_was_difficult = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)
