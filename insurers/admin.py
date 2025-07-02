from django.contrib import admin
from django.utils.safestring import mark_safe

from felix.admin import global_admin
from insurers.models import Insurer


class InsurerAdmin(admin.ModelAdmin):
    list_display = ('insurer_logo', 'name', 'country', 'created_on', 'updated_on',)
    search_fields = ('name',)

    def insurer_logo(self, obj):
        return mark_safe(
            '<img src="{}" width="50" />'.format(
                obj.get_insurer_logo(),
            )
        )

    insurer_logo.short_description = 'Logo'


global_admin.register(Insurer, InsurerAdmin)
