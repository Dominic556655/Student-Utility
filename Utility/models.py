# blog/models.py
from django.db import models
from django.contrib.auth.models import User
from datetime import date

# Create your models here.

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='blog_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.content[:30]
    
class CGPARecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_units = models.IntegerField()
    cgpa = models.FloatField()
    semesters = models.JSONField(default=list, blank=True)
    classification = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.cgpa}"
    
class GPARecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    gpa = models.FloatField()
    total_units = models.IntegerField()
    classification = models.CharField(max_length=50)
    courses = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.gpa}"
    

from django.db import models
from django.contrib.auth.models import User


class ExamHistory(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    course_code = models.CharField(max_length=50)
    current_ca = models.FloatField()
    exam_total = models.FloatField()
    target_grade = models.CharField(max_length=10)
    required_score = models.FloatField()
    result = models.CharField(max_length=50)
    final_score = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.course_code}"
    
class Assignment(models.Model):

    STATUS_CHOICES = [("Not Started", "Not Started"),("In Progress", "In Progress"),("Completed", "Completed"),("Submitted", "Submitted"),]
    
    PRIORITY_CHOICES = [("High", "High"),("Medium", "Medium"),("Low", "Low"),]
    CATEGORY_CHOICES = [("Homework", "Homework"),("Project", "Project"),("Practical", "Practical"),("Report", "Report"),("Group Work", "Group Work"),("Presentation", "Presentation"),]
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    title = models.CharField(max_length=200)
    course_code = models.CharField(max_length=30)
    category = models.CharField(max_length=50,choices=CATEGORY_CHOICES)
    priority = models.CharField(max_length=20,choices=PRIORITY_CHOICES)
    status = models.CharField(max_length=20,null=False,blank=False,default="Not Started")
    progress = models.IntegerField(default=0)
    due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    

class Course(models.Model):
    CATEGORY_CHOICES = [
        ('Backend', 'Backend'),
        ('Frontend', 'Frontend'),
        ('Data Science', 'Data Science'),
        ('Design', 'Design'),
        ('Video Editing', 'Video Editing'),
        ('Graphics Design', 'Graphics Design'),
        ('Cybersecurity', 'Cybersecurity'),
        ('Marketing', 'Marketing'),
    ]

    LEVEL_CHOICES = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
    ]

    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='courses/')
    description = models.TextField()

    category = models.CharField(max_length=100,choices=CATEGORY_CHOICES
    )

    level = models.CharField(max_length=50,choices=LEVEL_CHOICES
    )

    affiliate_link = models.URLField()

    # ADD THESE 👇
    advisor = models.CharField(max_length=100,default="Ichason"
    )

    students = models.IntegerField(default=0
    )

    price = models.CharField(max_length=50,default="$0"
    )

    created_at = models.DateTimeField(auto_now_add=True
    )

    def __str__(self):
        return self.title
    
    # -------> TIME TABLE
    
class TimetableEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    course = models.CharField(max_length=100)

    DAY_CHOICES = [
        ("Monday", "Monday"),
        ("Tuesday", "Tuesday"),
        ("Wednesday", "Wednesday"),
        ("Thursday", "Thursday"),
        ("Friday", "Friday"),
        ("Saturday", "Saturday"),
        ("Sunday", "Sunday"),
    ]

    day = models.CharField(max_length=20, choices=DAY_CHOICES)

    start_time = models.TimeField()
    end_time = models.TimeField()

    venue = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    
    order = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.course} ({self.day})"\
            
class StudySession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    subject = models.CharField(max_length=100)

    goal = models.CharField(max_length=255)

    duration = models.IntegerField(default=25)  # minutes

    completed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject} - {self.user.username}"
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    currency = models.CharField(max_length=5, default="NGN")

    streak = models.IntegerField(default=0)
    last_study_date = models.DateField(null=True, blank=True)
    
    
class AIStudyHistory(models.Model):
    TOOL_CHOICES = [
        ("summarizer", "Summarizer"),
        ("quiz", "Quiz Generator"),
        ("study_plan", "Study Plan"),
        ("explain", "Explain Topic"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    tool_type = models.CharField(
        max_length=30,
        choices=TOOL_CHOICES,
        default="summarizer"
    )

    prompt = models.TextField()

    response = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.tool_type}"
    
class AIUsage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=date.today)
    count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.count}"
    
class AIWallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    free_used = models.IntegerField(default=0)
    paid_credits = models.IntegerField(default=0)
    last_reset = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} wallet"
    
class PaidTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    tx_id = models.CharField(max_length=200, unique=True)
    credits = models.IntegerField()
    amount = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)
    
    
class AISemanticCache(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    prompt = models.TextField()
    response = models.TextField()

    embedding = models.JSONField()  # store vector
    created_at = models.DateTimeField(auto_now_add=True)
    
class StudentProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    full_name = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    student_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    program = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    department = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    academic_year = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    school = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    faculty = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.user.username