# Generated by Django 4.1.7 on 2023-03-18 00:04

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("notes", "0004_alter_note_user"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="note",
            options={"ordering": ["-created"]},
        ),
        migrations.RenameField(
            model_name="note",
            old_name="user",
            new_name="author",
        ),
    ]
