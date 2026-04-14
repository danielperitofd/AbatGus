from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class AbatGusUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (
            "AbatGus",
            {
                "fields": (
                    "organization",
                    "role",
                    "avatar",
                    "phone",
                    "job_title",
                    "internal_notes",
                )
            },
        ),
    )
    list_display = ("username", "email", "role", "organization", "is_active", "is_staff")
