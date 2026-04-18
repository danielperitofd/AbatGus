from django.contrib import admin

from .models import AuditLog, IncomeItem, IndemnityLookupValue, IndemnityRecord, MeatCategory, MeatProductionEntry, ResidueCategory, ResidueCollection, WeeklyIncomeEntry


admin.site.register(
    [
        IncomeItem,
        WeeklyIncomeEntry,
        MeatCategory,
        MeatProductionEntry,
        ResidueCategory,
        ResidueCollection,
        IndemnityRecord,
        IndemnityLookupValue,
        AuditLog,
    ]
)
