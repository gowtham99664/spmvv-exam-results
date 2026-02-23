# Generated manually
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('results', '0015_exam_examenrollment_studentphoto_circular_hallticket_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='examsubject',
            name='exam_date',
            field=models.DateField(null=True, blank=True, help_text='Date of examination (required for Theory, optional for Lab)'),
        ),
    ]
