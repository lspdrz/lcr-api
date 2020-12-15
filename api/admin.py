from django.contrib import admin
from.models import Company, Person, ScrapeError


class ScrapedDataAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Company, ScrapedDataAdmin)
admin.site.register(Person, ScrapedDataAdmin)
admin.site.register(ScrapeError)
