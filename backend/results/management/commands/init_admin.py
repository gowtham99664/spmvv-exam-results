from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import connection, transaction
import os

User = get_user_model()


def drop_stale_columns():
    """Drop old permission columns from the users table if they still exist.
    The User model uses db_table = 'users' (not 'results_user').
    This runs raw SQL before any ORM operations to prevent IntegrityError
    on databases that have stale columns from old migrations."""
    stale_columns = [
        "can_manage_users",
        "can_view_all_branches",
        "can_upload_results",
        "can_delete_results",
        "can_view_statistics",
    ]
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS "
            "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'users'"
        )
        existing = {row[0] for row in cursor.fetchall()}
        for col in stale_columns:
            if col in existing:
                cursor.execute(f"ALTER TABLE users DROP COLUMN {col}")


class Command(BaseCommand):
    help = "Initialize admin user with default credentials from environment"

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            type=str,
            help='Admin username (default: from ADMIN_USERNAME env or "admin")',
        )
        parser.add_argument(
            "--password",
            type=str,
            help="Admin password (default: from ADMIN_DEFAULT_PASSWORD env)",
        )
        parser.add_argument(
            "--email",
            type=str,
            default="admin@spmvv.edu",
            help="Admin email (default: admin@spmvv.edu)",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force reset password if user exists",
        )

    def handle(self, *args, **options):
        username = options.get("username") or os.environ.get("ADMIN_USERNAME", "admin")
        password = options.get("password") or os.environ.get("ADMIN_DEFAULT_PASSWORD")
        email = options.get("email")
        force = options.get("force", False)

        if not password:
            self.stdout.write(
                self.style.ERROR(
                    "Password is required. Set ADMIN_DEFAULT_PASSWORD environment variable "
                    "or use --password option."
                )
            )
            return

        # Drop stale columns before any ORM operation
        try:
            drop_stale_columns()
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Stale column cleanup skipped: {e}"))

        try:
            with transaction.atomic():
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        "email": email,
                        "is_staff": True,
                        "is_superuser": True,
                        "role": "admin",
                        "results_upload": True,
                        "results_edit": True,
                        "results_delete": True,
                        "results_download": True,
                        "students_view": True,
                        "students_detained_report": True,
                        "circulars_view": True,
                        "circulars_create": True,
                        "circulars_edit": True,
                        "circulars_delete": True,
                        "timetable_view": True,
                        "timetable_create": True,
                        "halltickets_view": True,
                        "halltickets_create": True,
                        "halltickets_generate": True,
                        "halltickets_download": True,
                        "statistics_view": True,
                        "auditlogs_view": True,
                        "users_view": True,
                        "users_create": True,
                        "users_edit": True,
                        "users_delete": True,
                        "access_all_branches": True,
                    },
                )

                if created:
                    user.set_password(password)
                    user.save()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Successfully created admin user: {username}"
                        )
                    )
                    self.stdout.write(
                        self.style.WARNING(
                            f"Default password set. Please change it after first login!"
                        )
                    )
                elif force:
                    user.set_password(password)
                    user.is_staff = True
                    user.is_superuser = True
                    user.role = "admin"
                    user.results_upload = True
                    user.results_edit = True
                    user.results_delete = True
                    user.results_download = True
                    user.students_view = True
                    user.students_detained_report = True
                    user.circulars_view = True
                    user.circulars_create = True
                    user.circulars_edit = True
                    user.circulars_delete = True
                    user.timetable_view = True
                    user.timetable_create = True
                    user.halltickets_view = True
                    user.halltickets_create = True
                    user.halltickets_generate = True
                    user.halltickets_download = True
                    user.statistics_view = True
                    user.auditlogs_view = True
                    user.users_view = True
                    user.users_create = True
                    user.users_edit = True
                    user.users_delete = True
                    user.access_all_branches = True
                    user.save()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Successfully updated admin user: {username}"
                        )
                    )
                    self.stdout.write(
                        self.style.WARNING(
                            f"Password has been reset. Please change it after login!"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Admin user {username} already exists. Use --force to reset password."
                        )
                    )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating admin user: {str(e)}"))
            raise
