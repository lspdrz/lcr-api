from django.db import models
from django.utils.translation import gettext_lazy as _


class Base(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Company(Base):
    class Governorate(models.TextChoices):
        BEIRUT = 'BE', _('Beirut')
        MOUNT_LEBANON = 'ML', _('Mount Lebanon')
        NORTH_LEBANON = 'NL', _('North Lebanon')
        BEKAA = 'BA', _('Bekaa')
        SOUTH_LEBANON = 'SL', _('South Lebanon')
        NABATIEH = 'NA', _('Nabatieh')
        AKKAR = 'AK', _('Akkar')
        BAALBEK_HERMEL = 'BH', _('Baalbek-Hermel')
        UNKNOWN = 'UK', _('Unknown')

    cr_id = models.IntegerField(unique=True)
    source_url = models.CharField(max_length=255, unique=True)
    registration_number = models.IntegerField()
    name = models.CharField(max_length=255)
    additional_name = models.CharField(max_length=255)
    governorate = models.CharField(
        max_length=2,
        choices=Governorate.choices,
        default=Governorate.UNKNOWN,
    )
    registration_date = models.DateTimeField()
    record_type = models.CharField(max_length=128)
    company_status = models.CharField(max_length=128)
    company_duration = models.CharField(max_length=128)
    legal_form = models.CharField(max_length=128)
    capital = models.DecimalField(max_digits=15, decimal_places=2)
    title = models.CharField(max_length=128)
    description = models.TextField()

    def __str__(self):
        return self.name


class Person(Base):
    name = models.CharField(max_length=255)
    nationality = models.CharField(max_length=128)

    def __str__(self):
        return self.name


class PersonCompany(Base):
    person = models.ForeignKey(Person, related_name="person",
                               on_delete=models.CASCADE)
    company = models.ForeignKey(Company, related_name="company",
                                on_delete=models.CASCADE)
    relationship = models.CharField(max_length=128)
    stock = models.IntegerField()
    quota = models.IntegerField()
    ratio = models.IntegerField()
