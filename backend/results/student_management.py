"""
Student Results Management API Views
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import models
from .models import Result, Subject, AuditLog
from .views import get_client_ip
import logging

logger = logging.getLogger(__name__)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search_student(request):
    if request.user.role != "admin":
        return Response({"error": "Admin only"}, status=403)
    try:
        query = request.GET.get("q", "").strip()
        if not query:
            return Response({"error": "Search query is required"}, status=400)
        results = Result.objects.filter(roll_number__icontains=query).values("roll_number", "student_name", "course", "branch").distinct()
        students = []
        seen = set()
        for result in results:
            roll = result["roll_number"]
            if roll not in seen:
                seen.add(roll)
                students.append({"roll_number": roll, "student_name": result["student_name"], "course": dict(Result.COURSE_CHOICES).get(result["course"], result["course"]), "branch": dict(Result.BRANCH_CHOICES).get(result["branch"], result["branch"])})
        return Response({"students": students})
    except Exception as e:
        logger.error(f"Error searching students: {str(e)}")
        return Response({"error": str(e)}, status=500)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_student_history(request, roll_number):
    if request.user.role != "admin":
        return Response({"error": "Admin only"}, status=403)
    try:
        results = Result.objects.filter(roll_number=roll_number).select_related("student").prefetch_related("subjects").order_by("year", "semester", "result_type", "-uploaded_at")
        if not results.exists():
            return Response({"error": "No results found for this roll number"}, status=404)
        first_result = results.first()
        student_info = {"roll_number": roll_number, "student_name": first_result.student_name, "course": first_result.get_course_display(), "branch": first_result.get_branch_display()}
        
        # Group results by (year, semester) and consolidate
        semester_data = {}
        for result in results:
            key = (result.year, result.semester)
            if key not in semester_data:
                semester_data[key] = []
            semester_data[key].append(result)
        
        semester_summary = []
        for (year, semester), result_list in sorted(semester_data.items()):
            # Consolidate subjects from all results (regular + supplementary)
            # Keep the latest attempt for each subject (by subject_code)
            consolidated_subjects = {}
            latest_result = result_list[0]  # Most recent result for display
            all_exam_names = []
            latest_completion_date = None
            
            for result in reversed(result_list):  # Process oldest to newest
                all_exam_names.append(result.exam_name)
                if result.completion_date:
                    latest_completion_date = result.completion_date
                    
                for subject in result.subjects.all():
                    subject_code = subject.subject_code
                    # If subject doesn't exist or this one has more attempts, use this one
                    if subject_code not in consolidated_subjects or subject.attempts > consolidated_subjects[subject_code].attempts:
                        consolidated_subjects[subject_code] = subject
            
            # Calculate totals from consolidated subjects
            subjects = list(consolidated_subjects.values())
            total_subjects = len(subjects)
            total_marks = 0
            max_marks = 0
            pending_subjects = 0
            
            for subject in subjects:
                if subject.total_marks:
                    total_marks += subject.total_marks
                    max_marks += 100
                if subject.subject_result.lower() == "fail":
                    pending_subjects += 1
            
            percentage = round((total_marks / max_marks * 100), 2) if max_marks > 0 else 0
            overall_result = "Pass" if pending_subjects == 0 else "Fail"
            max_attempts = max([s.attempts for s in subjects]) if subjects else 1
            completion_date_str = latest_completion_date.strftime("%Y-%m-%d") if latest_completion_date else None
            
            # Create consolidated exam name
            if len(result_list) > 1:
                exam_name = f"{latest_result.exam_name} (Consolidated)"
            else:
                exam_name = latest_result.exam_name
            
            semester_summary.append({
                "year": year, 
                "semester": semester, 
                "result_id": latest_result.id, 
                "exam_name": exam_name, 
                "result_type": "Consolidated" if len(result_list) > 1 else latest_result.get_result_type_display(), 
                "total_marks_percentage": percentage, 
                "overall_result": overall_result, 
                "overall_grade": latest_result.overall_grade, 
                "total_subjects": total_subjects, 
                "pending_subjects": pending_subjects, 
                "max_attempts": max_attempts, 
                "completion_date": completion_date_str, 
                "uploaded_at": latest_result.uploaded_at.strftime("%Y-%m-%d %H:%M:%S"),
                "result_count": len(result_list)  # Number of exams consolidated
            })
        return Response({"student_info": student_info, "semester_summary": semester_summary})
    except Exception as e:
        logger.error(f"Error getting student history for {roll_number}: {str(e)}")
        return Response({"error": str(e)}, status=500)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_semester_subjects(request, result_id):
    if request.user.role != "admin":
        return Response({"error": "Admin only"}, status=403)
    try:
        result = Result.objects.get(id=result_id)
        
        # Get all results for this student/year/semester (to consolidate subjects)
        all_results = Result.objects.filter(
            roll_number=result.roll_number,
            year=result.year,
            semester=result.semester
        ).prefetch_related("subjects").order_by("result_type", "-uploaded_at")
        
        # Consolidate subjects (keep latest attempt for each subject_code)
        consolidated_subjects = {}
        for res in reversed(list(all_results)):  # Process oldest to newest
            for subject in res.subjects.all():
                subject_code = subject.subject_code
                if subject_code not in consolidated_subjects or subject.attempts > consolidated_subjects[subject_code].attempts:
                    consolidated_subjects[subject_code] = subject
        
        subjects = sorted(consolidated_subjects.values(), key=lambda s: s.subject_code)
        subject_details = []
        for subject in subjects:
            subject_details.append({
                "id": subject.id, 
                "subject_code": subject.subject_code, 
                "subject_name": subject.subject_name, 
                "internal_marks": subject.internal_marks, 
                "external_marks": subject.external_marks, 
                "total_marks": subject.total_marks, 
                "subject_result": subject.get_subject_result_display(), 
                "grade": subject.grade, 
                "attempts": subject.attempts
            })
        
        semester_info = {
            "roll_number": result.roll_number, 
            "student_name": result.student_name, 
            "year": result.year, 
            "semester": result.semester, 
            "exam_name": result.exam_name + (" (Consolidated)" if all_results.count() > 1 else ""), 
            "result_type": "Consolidated" if all_results.count() > 1 else result.get_result_type_display(), 
            "overall_result": result.overall_result, 
            "overall_grade": result.overall_grade
        }
        return Response({"semester_info": semester_info, "subjects": subject_details})
    except Result.DoesNotExist:
        return Response({"error": "Result not found"}, status=404)
    except Exception as e:
        logger.error(f"Error getting semester subjects for result {result_id}: {str(e)}")
        return Response({"error": str(e)}, status=500)

@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_subject_marks(request, subject_id):
    if request.user.role != "admin":
        return Response({"error": "Admin only"}, status=403)
    try:
        subject = Subject.objects.select_related("result").get(id=subject_id)
        internal_marks = request.data.get("internal_marks")
        external_marks = request.data.get("external_marks")
        total_marks = request.data.get("total_marks")
        subject_result = request.data.get("subject_result", "").lower()
        grade = request.data.get("grade", "")
        if subject_result not in ["pass", "fail", "absent"]:
            return Response({"error": "Invalid subject_result. Must be: pass, fail, or absent"}, status=400)
        if internal_marks is not None:
            subject.internal_marks = internal_marks
        if external_marks is not None:
            subject.external_marks = external_marks
        if total_marks is not None:
            subject.total_marks = total_marks
        if subject.subject_result.lower() == "fail" and subject_result == "pass":
            subject.attempts += 1
        subject.subject_result = subject_result
        subject.grade = grade
        subject.save()
        result = subject.result
        all_subjects = result.subjects.all()
        failed_count = all_subjects.filter(subject_result__iexact="fail").count()
        if failed_count == 0:
            result.overall_result = "Pass"
            result.save()
        AuditLog.objects.create(user=request.user, action="result_edit", details=f"Updated marks for {subject.subject_code} - {result.roll_number} Year {result.year} Sem {result.semester}", ip_address=get_client_ip(request))
        return Response({"message": "Subject marks updated successfully", "subject": {"id": subject.id, "subject_code": subject.subject_code, "subject_name": subject.subject_name, "internal_marks": subject.internal_marks, "external_marks": subject.external_marks, "total_marks": subject.total_marks, "subject_result": subject.get_subject_result_display(), "grade": subject.grade, "attempts": subject.attempts}, "overall_result_updated": failed_count == 0})
    except Subject.DoesNotExist:
        return Response({"error": "Subject not found"}, status=404)
    except Exception as e:
        logger.error(f"Error updating subject marks for subject {subject_id}: {str(e)}")
        return Response({"error": str(e)}, status=500)

