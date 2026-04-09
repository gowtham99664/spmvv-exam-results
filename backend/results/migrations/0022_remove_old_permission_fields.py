from django.db import migrations


def remove_old_columns_if_exist(apps, schema_editor):
    """Remove old permission columns only if they still exist in the table.
    NOTE: The User model uses db_table = 'users' (not 'results_user')."""
    connection = schema_editor.connection
    cursor = connection.cursor()

    cursor.execute(
        "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS "
        "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'users'"
    )
    existing_columns = {row[0] for row in cursor.fetchall()}

    old_columns = [
        "can_manage_users",
        "can_view_all_branches",
        "can_upload_results",
        "can_delete_results",
        "can_view_statistics",
    ]

    for col in old_columns:
        if col in existing_columns:
            cursor.execute(f"ALTER TABLE users DROP COLUMN {col}")


class Migration(migrations.Migration):
    dependencies = [
        ("results", "0021_circular_target_audience"),
    ]

    operations = [
        migrations.RunPython(remove_old_columns_if_exist, migrations.RunPython.noop),
    ]
