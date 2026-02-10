from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator
import logging

security_logger = logging.getLogger('security')

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('dean', 'Dean'),
        ('vice_principal', 'Vice Principal'),
        ('principal', 'Principal'),
        ('hod', 'Head of Department'),
        ('faculty', 'Faculty'),
        ('staff', 'Staff'),
        ('student', 'Student'),
    ]
    
    # Basic Info
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='student', help_text='User role (label only)')
    roll_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    branch = models.CharField(max_length=50, null=True, blank=True, help_text='Assigned branch (CSE, ECE, etc.) or NULL for all')
    department = models.CharField(max_length=100, null=True, blank=True, help_text='Department name')
    
    # Granular Permissions (Admin assigns these)
    can_view_statistics = models.BooleanField(default=False, help_text='Can view statistics and reports dashboard')
    can_upload_results = models.BooleanField(default=False, help_text='Can upload exam results (Excel files)')
    can_delete_results = models.BooleanField(default=False, help_text='Can delete exam results')
    can_manage_users = models.BooleanField(default=False, help_text='Can create, edit, and delete users')
    
    # Branch Access Control
    can_view_all_branches = models.BooleanField(default=False, help_text='Can view all branches (overrides branch restriction)')
    
    # Account Status
    is_active_user = models.BooleanField(default=True, help_text='User account is active')
    failed_login_attempts = models.IntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    
    groups = models.ManyToManyField(
        "auth.Group",
        verbose_name="groups",
        blank=True,
        related_name="custom_user_set",
        related_query_name="custom_user",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        verbose_name="user permissions",
        blank=True,
        related_name="custom_user_set",
        related_query_name="custom_user",
    )
    
    class Meta:
        db_table = 'users'
    
    def __str__(self):
        return f"{self.username} ({self.role})"


class LoginAttempt(models.Model):
    username = models.CharField(max_length=150)
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'login_attempts'
        indexes = [
            models.Index(fields=['username', 'timestamp']),
            models.Index(fields=['ip_address', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.username} - {self.timestamp} - {'Success' if self.success else 'Failed'}"


class Result(models.Model):
    RESULT_TYPE_CHOICES = [
        ('regular', 'Regular'),
        ('supplementary', 'Supplementary'),
        ('both', 'Regular and Supplementary'),
    ]
    
    COURSE_CHOICES = [
        ('btech', 'B.Tech'),
        ('mtech', 'M.Tech'),
    ]
    
    BRANCH_CHOICES = [
        ("cse", "Computer Science & Engineering"),
        ("ece", "Electronics & Communication Engineering"),
        ("eee", "Electrical & Electronics Engineering"),
        ("mech", "Mechanical Engineering"),
        ("civil", "Civil Engineering"),
        ("it", "Information Technology"),
        ("chemical", "Chemical Engineering"),
        ("biotechnology", "Biotechnology"),
        ("mba", "MBA"),
        ("mca", "MCA"),
    ]
    
    student = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='results', help_text='Student user (optional, for portal login)')
    roll_number = models.CharField(max_length=50, db_index=True)
    
    student_name = models.CharField(max_length=200)
    year = models.IntegerField(default=1, help_text='Academic year: 1, 2, 3, or 4')
    semester = models.IntegerField(help_text='Semester: 1 or 2')
    exam_name = models.CharField(max_length=300, default='Exam Results', help_text='Auto-generated exam name')
    exam_held_date = models.DateField(null=True, blank=True, help_text='Date when exam was held')
    result_type = models.CharField(max_length=20, choices=RESULT_TYPE_CHOICES)
    course = models.CharField(max_length=10, choices=COURSE_CHOICES, default='btech', help_text='Course: B.Tech or M.Tech')
    branch = models.CharField(max_length=50, choices=BRANCH_CHOICES, default="cse", help_text="Branch/Department")
    overall_result = models.CharField(max_length=50, blank=True)
    overall_grade = models.CharField(max_length=10, blank=True)
    total_marks = models.IntegerField(null=True, blank=True, help_text='Total marks obtained')
    sgpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, help_text='Semester Grade Point Average')
    completion_date = models.DateField(null=True, blank=True, help_text='Date when student passed all subjects (no pending subjects)')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='uploaded_results')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'results'
        unique_together = ['roll_number', 'exam_name']
        indexes = [
            models.Index(fields=['roll_number', 'year', 'semester']),
            models.Index(fields=['uploaded_at']),
            models.Index(fields=['exam_name']),
        ]
    
    def __str__(self):
        return f"{self.roll_number} - Year {self.year} Semester {self.semester}"


class Subject(models.Model):
    result = models.ForeignKey(Result, on_delete=models.CASCADE, related_name='subjects')
    subject_code = models.CharField(max_length=50)
    subject_name = models.CharField(max_length=200)
    credits = models.IntegerField(null=True, blank=True, help_text='Subject credits')
    internal_marks = models.IntegerField(null=True, blank=True)
    external_marks = models.IntegerField(null=True, blank=True)
    total_marks = models.IntegerField(null=True, blank=True)
    grade = models.CharField(max_length=10, blank=True)
    attempts = models.IntegerField(default=1, help_text="Number of attempts for this subject")
    
    class Meta:
        db_table = 'subjects'
        indexes = [
            models.Index(fields=['subject_code']),
        ]
    
    def __str__(self):
        return f"{self.subject_code} - {self.subject_name}"


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('password_change', 'Password Change'),
        ('result_upload', 'Result Upload'),
        ('result_view', 'Result View'),
        ('result_edit', 'Result Edit'),
        ('result_delete', 'Result Delete'),
        ('user_registration', 'User Registration'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    details = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'audit_logs'
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user} - {self.action} - {self.timestamp}"



class BlacklistedToken(models.Model):
    token = models.TextField(unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blacklisted_tokens')
    blacklisted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'blacklisted_tokens'
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['blacklisted_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.blacklisted_at}"


class Notification(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    result = models.ForeignKey(Result, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    message = models.TextField()
    exam_name = models.CharField(max_length=300, blank=True)
    results_published_date = models.DateField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['student', 'is_read', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.student.username} - {self.message[:50]}"
