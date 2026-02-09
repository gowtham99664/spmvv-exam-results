from django.urls import path
from . import views
from . import student_management

urlpatterns = [
    # Authentication endpoints
    path('register/', views.register_student, name='register_student'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('change-password/', views.change_password, name='change_password'),
    
    # Result management endpoints
    path('results/upload/', views.upload_results, name='upload_results'),
    path('results/all/', views.get_results, name='get_all_results'),
    path('results/', views.get_results, name='get_results'),
    
    # Exam management endpoints
    path('exams/', views.get_uploaded_exams, name='get_uploaded_exams'),
    path('exams/<str:exam_name>/download/', views.download_exam_results, name='download_exam_results'),
    path('exams/<str:exam_name>/delete/', views.delete_exam_results, name='delete_exam_results'),
    
    # Admin dashboard endpoints
    path('statistics/', views.get_statistics, name='statistics'),
    path('sample-template/', views.download_sample_template, name='sample_template'),
    path('audit-logs/', views.get_audit_logs, name='audit_logs'),
    
    # Notification endpoints
    path('notifications/', views.get_notifications, name='get_notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    
    # Student management endpoints
    path('students/search/', student_management.search_student, name='search_student'),
    path('students/<str:roll_number>/history/', student_management.get_student_history, name='get_student_history'),
    path('semesters/<int:result_id>/subjects/', student_management.get_semester_subjects, name='get_semester_subjects'),
    path('subjects/<int:subject_id>/update/', student_management.update_subject_marks, name='update_subject_marks'),

    # User management endpoints (admin only)
    path('users/', views.list_users, name='list_users'),
    path('users/create/', views.create_user, name='create_user'),
    path('users/<int:user_id>/update/', views.update_user, name='update_user'),
    path('users/<int:user_id>/reset-password/', views.reset_user_password, name='reset_user_password'),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('users/permissions/', views.get_user_permissions, name='get_user_permissions'),

    # Health check endpoint
    path('health/', views.health_check, name='health_check'),
]
