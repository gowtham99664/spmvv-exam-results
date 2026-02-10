from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, Result, Subject, Notification, AuditLog

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['roll_number', 'password', 'password_confirm', 'first_name', 'last_name', 'email']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        
        if User.objects.filter(roll_number=attrs['roll_number']).exists():
            raise serializers.ValidationError({"roll_number": "Roll number already exists."})
        
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        roll_number = validated_data['roll_number']
        
        user = User.objects.create_user(
            username=roll_number,
            roll_number=roll_number,
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            email=validated_data.get('email', ''),
            role='student'
        )
        return user


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True, write_only=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password": "Password fields didn't match."})
        return attrs


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'subject_code', 'subject_name', 'credits', 'internal_marks', 
                  'external_marks', 'total_marks', 'grade', 'attempts']


class ResultSerializer(serializers.ModelSerializer):
    subjects = SubjectSerializer(many=True, read_only=True)
    result_type_display = serializers.CharField(source='get_result_type_display', read_only=True)
    
    class Meta:
        model = Result
        fields = ['id', 'roll_number', 'student_name', 'year', 'semester', 'exam_name', 
                  'result_type', 'result_type_display', 'overall_result', 'total_marks', 'sgpa',
                  'completion_date', 'subjects', 'uploaded_at', 'updated_at']


class NotificationSerializer(serializers.ModelSerializer):
    results_published_date_formatted = serializers.SerializerMethodField()
    result_id = serializers.IntegerField(source='result.id', read_only=True)
    
    class Meta:
        model = Notification
        fields = ['id', 'message', 'exam_name', 'results_published_date', 
                  'results_published_date_formatted', 'result_id', 'is_read', 'created_at']
    
    def get_results_published_date_formatted(self, obj):
        if obj.results_published_date:
            # Format as DD-MMM-YYYY (e.g., 07-Feb-2026)
            return obj.results_published_date.strftime('%d-%b-%Y')
        return None


class AuditLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = ['id', 'username', 'action', 'details', 'ip_address', 'timestamp']
