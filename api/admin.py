from django.contrib import admin
from.models import Company, Person, PersonCompany, ScrapeError

admin.site.register(Company)
admin.site.register(Person)
admin.site.register(PersonCompany)
admin.site.register(ScrapeError)
