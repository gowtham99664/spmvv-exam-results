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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_student_history(request, roll_number):
    """Get complete history of results for a student. Each exam is shown separately."""
    if request.user.role != 'admin':
        return Response({'error': 'Admin only'}, status=403)
    
    try:
        results = Result.objects.filter(
            roll_number=roll_number
        ).select_related('student').prefetch_related('subjects').order_by(
            'year', 'semester', 'uploaded_at'
        )
        
        if not results.exists():
            return Response({'error': 'No results found for this roll number'}, status=404)
        
        first_result = results.first()
        student_info = {
            'roll_number': roll_number,
            'student_name': first_result.student_name,
            'course': first_result.get_course_display(),
            'branch': first_result.get_branch_display()
        }
        
        # Count exams per year/semester for attempt count
        exam_counts = {}
        for result in results:
            key = (result.year, result.semester)
            exam_counts[key] = exam_counts.get(key, 0) + 1
        
        semester_summary = []
        for result in results:
            subjects = result.subjects.all()
            total_subjects = subjects.count()
            pending_subjects = 0
            
            # Count F grades as pending subjects
            for subject in subjects:
                if subject.grade and subject.grade.upper() == 'F':
                    pending_subjects += 1
            
            overall_result = result.overall_result if result.overall_result else ('Pass' if pending_subjects == 0 else 'Fail')
            key = (result.year, result.semester)
            num_attempts = exam_counts[key]
            completion_date_str = result.completion_date.strftime('%Y-%m-%d') if result.completion_date else None
            
            semester_summary.append({
                'year': result.year,
                'semester': result.semester,
                'result_id': result.id,
                'exam_name': result.exam_name,
                'result_type': result.get_result_type_display(),
                'total_marks': result.total_marks,
                'sgpa': float(result.sgpa) if result.sgpa else None,
                'overall_result': overall_result,
                'total_subjects': total_subjects,
                'pending_subjects': pending_subjects,
                'num_attempts': num_attempts,
                'completion_date': completion_date_str,
                'uploaded_at': result.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return Response({'student_info': student_info, 'semester_summary': semester_summary})
    except Exception as e:
        logger.error(f'Error getting student history for {roll_number}: {str(e)}')
        return Response({'error': str(e)}, status=500)



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_semester_subjects(request, result_id):
    """Get subjects for a SPECIFIC exam (result_id). Each exam is independent."""  
    if request.user.role != "admin":
        return Response({"error": "Admin only"}, status=403)
    try:
        result = Result.objects.get(id=result_id)
        
        # Get subjects for THIS specific exam only (no consolidation)
        subjects = result.subjects.all().order_by("subject_code")
        
        subject_details = []
        for subject in subjects:
            subject_details.append({
                "id": subject.id,
                "subject_code": subject.subject_code,
                "subject_name": subject.subject_name,
                "credits": subject.credits,
                "total_marks": subject.total_marks,
                "grade": subject.grade
            })
        
        semester_info = {
            "roll_number": result.roll_number,
            "student_name": result.student_name,
            "year": result.year,
            "semester": result.semester,
            "exam_name": result.exam_name,
            "result_type": result.get_result_type_display(),
            "overall_result": result.overall_result,
            "total_marks": result.total_marks,
            "sgpa": float(result.sgpa) if result.sgpa else None
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
        grade = request.data.get("grade", "").strip().upper()

        valid_grades = ["O", "A", "B", "C", "D", "F", "AB"]  # AB = absent
        if grade and grade not in valid_grades:
            return Response({"error": f"Invalid grade. Must be one of: {', '.join(valid_grades)}"}, status=400)

        if internal_marks is not None:
            subject.internal_marks = internal_marks
        if external_marks is not None:
            subject.external_marks = external_marks
        if total_marks is not None:
            subject.total_marks = total_marks

        # Track attempts: if subject was previously failed (grade F) and is now passing
        prev_grade = (subject.grade or "").strip().upper()
        if prev_grade == "F" and grade and grade != "F":
            subject.attempts += 1

        subject.grade = grade
        subject.save()

        result = subject.result
        all_subjects = result.subjects.all()
        # Determine pass/fail: any subject with grade F means overall fail
        failed_count = all_subjects.filter(grade__iexact="F").count()
        if failed_count == 0:
            result.overall_result = "Pass"
            result.save()

        AuditLog.objects.create(
            user=request.user,
            action="result_edit",
            details=f"Updated marks for {subject.subject_code} - {result.roll_number} Year {result.year} Sem {result.semester}",
            ip_address=get_client_ip(request)
        )
        subject_result_display = "Fail" if grade == "F" else ("Absent" if grade == "AB" else "Pass")
        return Response({
            "message": "Subject marks updated successfully",
            "subject": {
                "id": subject.id,
                "subject_code": subject.subject_code,
                "subject_name": subject.subject_name,
                "internal_marks": subject.internal_marks,
                "external_marks": subject.external_marks,
                "total_marks": subject.total_marks,
                "subject_result": subject_result_display,
                "grade": subject.grade,
                "attempts": subject.attempts
            },
            "overall_result_updated": failed_count == 0
        })
    except Subject.DoesNotExist:
        return Response({"error": "Subject not found"}, status=404)
    except Exception as e:
        logger.error(f"Error updating subject marks for subject {subject_id}: {str(e)}")
        return Response({"error": str(e)}, status=500)

