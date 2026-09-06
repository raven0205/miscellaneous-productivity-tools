from datetime import date, timedelta

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import LearningTopic, Project, Reflection, Requirement, Task, Week

class ProjectRoutingTests(TestCase):
	def test_home_page_returns_project_name(self):
		response = self.client.get("/")

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "AI Study Project Manager")

	def test_home_route_has_named_url(self):
		self.assertEqual(reverse("home"), "/")

	def test_admin_requires_authentication(self):
		response = self.client.get("/admin/")

		self.assertRedirects(response, "/admin/login/?next=/admin/")


class MvpWorkflowTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(username="student", password="password123")
		self.client.force_login(self.user)
		self.project = Project.objects.create(
			owner=self.user,
			title="Capstone",
			deadline=timezone.localdate() + timedelta(days=14),
		)

	def test_create_project_and_upload_multiple_text_fixtures(self):
		response = self.client.post(reverse("project-create"), {"title": "Research", "deadline": date.today() + timedelta(days=10)})
		project = Project.objects.get(title="Research")
		self.assertRedirects(response, reverse("project-detail", args=[project.pk]))

		files = [
			SimpleUploadedFile("brief-one.txt", b"Must submit a research report.\nTopic: Data analysis"),
			SimpleUploadedFile("brief-two.txt", b"Should present findings.\nTopic: Visualization"),
		]
		response = self.client.post(reverse("pdf-upload", args=[project.pk]), {"files": files})
		self.assertRedirects(response, reverse("project-detail", args=[project.pk]))
		self.assertEqual(project.pdfs.count(), 2)
		self.assertIn("Must submit", project.pdfs.first().extracted_text)

	def test_analysis_review_and_roadmap_generation(self):
		PDF_CONTENT = b"Must submit a research report.\nTopic: Data analysis"
		self.client.post(
			reverse("pdf-upload", args=[self.project.pk]),
			{"files": SimpleUploadedFile("brief.txt", PDF_CONTENT)},
		)
		response = self.client.get(reverse("project-analyze", args=[self.project.pk]))
		self.assertRedirects(response, reverse("project-review", args=[self.project.pk]))
		self.assertTrue(Requirement.objects.filter(project=self.project).exists())
		self.assertTrue(LearningTopic.objects.filter(project=self.project).exists())

		self.client.post(reverse("project-review", args=[self.project.pk]), {
			f"requirement-{self.project.requirements.first().pk}": "on",
			f"topic-{self.project.learning_topics.first().pk}": "on",
		})
		self.assertTrue(Week.objects.filter(project=self.project).exists())
		self.project.refresh_from_db()
		self.assertTrue(self.project.analysis_confirmed)

	def test_weighted_progress_next_action_completion_and_reflection(self):
		week = Week.objects.create(
			project=self.project,
			number=1,
			start_date=timezone.localdate(),
			end_date=self.project.deadline,
		)
		Task.objects.create(week=week, title="Done task", weight=3, status=Task.Status.DONE)
		pending = Task.objects.create(week=week, title="Pending task", weight=1)
		self.assertEqual(self.project.progress(), 75.0)
		self.assertEqual(self.project.tracking_status(), "On Track")
		self.assertEqual(self.client.get(reverse("roadmap", args=[self.project.pk])).status_code, 200)

		self.client.post(reverse("task-update", args=[self.project.pk, pending.pk]), {
			"title": pending.title,
			"description": "",
			"status": Task.Status.DONE,
			"weight": 1,
			"due_date": self.project.deadline,
			"required": "on",
		})
		self.project.refresh_from_db()
		self.assertIsNotNone(self.project.completed_at)

		response = self.client.post(reverse("reflection", args=[self.project.pk]), {
			"what_went_well": "The roadmap was clear.",
			"what_was_difficult": "Balancing the research.",
		})
		self.assertRedirects(response, reverse("project-complete", args=[self.project.pk]))
		self.assertTrue(Reflection.objects.filter(project=self.project).exists())
