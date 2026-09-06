import re
from datetime import timedelta

from django.utils import timezone

from .models import LearningTopic, Requirement, Resource, Task, Week


def extract_pdf_text(uploaded_file):
    """Extract text when pypdf is available, with a clear fallback for plain fixtures."""
    if uploaded_file.name.lower().endswith(".txt"):
        return uploaded_file.read().decode("utf-8", errors="replace"), False
    try:
        from pypdf import PdfReader

        reader = PdfReader(uploaded_file)
        text = "\n".join(page.extract_text() or "" for page in reader.pages).strip()
        return text, not bool(text)
    except (ImportError, Exception):
        return "", True


def analyze_project(project):
    text = "\n".join(pdf.extracted_text for pdf in project.pdfs.all()).strip()
    lines = [re.sub(r"^[\s\-\*\d.)]+", "", line).strip() for line in text.splitlines()]
    lines = [line for line in lines if len(line) >= 12]
    requirements = [line for line in lines if any(word in line.lower() for word in ("must", "should", "require", "deliver", "submit"))]
    topics = []
    for line in lines:
        if line.lower().startswith(("topic:", "topics:", "learn:", "learning:")):
            topics.append(line.split(":", 1)[1].strip())
    if not requirements:
        requirements = lines[:5] or ["Review the uploaded course material and identify the project deliverables."]
    if not topics:
        topics = [line for line in lines if len(line.split()) <= 8][:5]
    if not topics:
        topics = ["Core concepts from the uploaded material"]
    project.requirements.all().delete()
    project.learning_topics.all().delete()
    Requirement.objects.bulk_create([Requirement(project=project, text=item) for item in dict.fromkeys(requirements)])
    LearningTopic.objects.bulk_create([LearningTopic(project=project, name=item) for item in dict.fromkeys(topics)])
    return project.requirements.count(), project.learning_topics.count()


def generate_roadmap(project):
    project.weeks.all().delete()
    today = timezone.localdate()
    total_days = max((project.deadline - today).days, 1)
    week_count = max(1, min(12, (total_days + 6) // 7))
    requirements = list(project.requirements.filter(confirmed=True)) or list(project.requirements.all())
    topics = list(project.learning_topics.filter(confirmed=True)) or list(project.learning_topics.all())
    for index in range(week_count):
        start = today + timedelta(days=index * 7)
        end = min(start + timedelta(days=6), project.deadline)
        topic = topics[index % len(topics)].name if topics else "Project planning"
        week = Week.objects.create(project=project, number=index + 1, start_date=start, end_date=end, topic=topic)
        if index < len(requirements):
            requirement = requirements[index]
            Task.objects.create(week=week, title=f"Address: {requirement.text[:180]}", description=requirement.text, weight=2, due_date=end)
        else:
            Task.objects.create(week=week, title=f"Study and apply {topic}", weight=1, due_date=end)
        Resource.objects.create(week=week, title=f"Search for trusted material on {topic}", url="https://www.google.com/search?q=" + topic.replace(" ", "+"))
    return project.weeks.count()


def next_best_action(project):
    tasks = list(Task.objects.filter(week__project=project, status__in=[Task.Status.NOT_STARTED, Task.Status.IN_PROGRESS]).prefetch_related("dependencies"))
    overdue = [task for task in tasks if task.due_date and task.due_date < timezone.localdate()]
    candidates = overdue or tasks
    for task in candidates:
        if any(dependency.status != Task.Status.DONE for dependency in task.dependencies.all()):
            continue
        reason = "It is overdue." if task in overdue else "It is the next available roadmap task."
        return {"task": task, "explanation": reason}
    return {"task": None, "explanation": "All roadmap tasks are complete or waiting on dependencies."}