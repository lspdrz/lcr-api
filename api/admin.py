from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse

from api.models import Company, Person, ScrapeError


def linkify(field_name):
    """
    Converts a foreign key value into clickable links.

    If field_name is 'parent', link text will be str(obj.parent)
    Link will be admin url for the admin url for obj.parent.id:change
    Taken from: https://stackoverflow.com/questions/37539132/display-foreign-key-columns-as-link-to-detail-object-in-django-admin/53092940
    """
    def _linkify(obj):
        linked_obj = getattr(obj, field_name)
        if linked_obj is None:
            return '-'
        app_label = linked_obj._meta.app_label
        model_name = linked_obj._meta.model_name
        view_name = f'admin:{app_label}_{model_name}_change'
        link_url = reverse(view_name, args=[linked_obj.pk])
        return format_html('<a href="{}">{}</a>', link_url, linked_obj)

    _linkify.short_description = field_name  # Sets column name
    return _linkify


class ScrapedDataAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class PersonInline(admin.TabularInline):
    model = Person
    show_change_link = True


class CompanyAdmin(ScrapedDataAdmin):
    list_display = ('name', 'description', 'governorate',
                    'show_company_url', 'missing_personnel_data')
    search_fields = ('name', )
    inlines = (
        PersonInline,
    )
    fieldsets = (
        (None, {
            'fields': ('name', 'show_company_url', 'description', 'governorate',
                       'registration_number', 'registration_date', 'record_type',
                       'company_status', 'company_duration', 'legal_form',
                       'capital', 'title', 'additional_name', 'missing_personnel_data',)
        }),
    )

    def show_company_url(self, instance):
        return format_html(
            '<a href="{0}" target="_blank">{1}</a>',
            instance.source_url,
            instance.source_url
        )
    show_company_url.short_description = "Source URL"


class PersonAdmin(ScrapedDataAdmin):
    list_display = ('name', linkify('company'),
                    'relationship', 'stock', 'nationality',)
    search_fields = ('name',)
    fieldsets = (
        (None, {
            'fields': ('name', linkify('company'),
                       'relationship', 'stock', 'quota',
                       'ratio', 'nationality',)
        }),
    )


admin.site.register(Company, CompanyAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(ScrapeError)
