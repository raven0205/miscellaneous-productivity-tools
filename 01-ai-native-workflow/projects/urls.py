from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("register/", views.register, name="register"),
    path("projects/new/", views.project_create, name="project-create"),
    path("projects/<int:project_id>/", views.project_detail, name="project-detail"),
    path("projects/<int:project_id>/upload/", views.upload_pdfs, name="pdf-upload"),
    path("projects/<int:project_id>/folders/", views.create_folder, name="folder-create"),
    path("projects/<int:project_id>/pdfs/<int:pdf_id>/delete/", views.delete_pdf, name="pdf-delete"),
    path("projects/<int:project_id>/analyze/", views.analyze, name="project-analyze"),
    path("projects/<int:project_id>/review/", views.review, name="project-review"),
    path("projects/<int:project_id>/roadmap/generate/", views.roadmap_generate, name="roadmap-generate"),
    path("projects/<int:project_id>/roadmap/", views.roadmap, name="roadmap"),
    path("projects/<int:project_id>/tasks/<int:task_id>/", views.task_update, name="task-update"),
    path("projects/<int:project_id>/reflection/", views.reflection, name="reflection"),
    path("projects/<int:project_id>/complete/", views.project_complete, name="project-complete"),
]