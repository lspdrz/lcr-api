from django.db import models
from django.utils.translation import gettext_lazy as _


class Base(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Company(Base):
    class Governorate(models.IntegerChoices):
        BEIRUT = 1
        MOUNT_LEBANON = 2
        NORTH_LEBANON = 3
        BEKAA = 4
        SOUTH_LEBANON = 5
        NABATIEH = 6
        # Akkar and Baalbek Hermel currently not included in Commercial Registry
        # AKKAR = 7
        # BAALBEK_HERMEL = 8

    cr_id = models.CharField(max_length=128, unique=True)
    cr_sub_id = models.IntegerField()
    source_url = models.CharField(max_length=255, unique=True)
    registration_number = models.IntegerField()
    name = models.CharField(max_length=255)
    additional_name = models.CharField(max_length=255)
    governorate = models.IntegerField(choices=Governorate.choices)
    registration_date = models.DateTimeField()
    record_type = models.CharField(max_length=255)
    company_status = models.CharField(max_length=255)
    company_duration = models.CharField(max_length=255)
    legal_form = models.CharField(max_length=255)
    capital = models.DecimalField(max_digits=15, decimal_places=2)
    title = models.CharField(max_length=255)
    description = models.TextField()
    missing_personnel_data = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['name'], name="company_name_idx"),
        ]

    def __str__(self):
        return self.name


class Person(Base):
    name = models.CharField(max_length=255)
    company = models.ForeignKey(Company, related_name="company",
                                on_delete=models.CASCADE)
    nationality = models.CharField(max_length=128)
    relationship = models.CharField(max_length=128)
    stock = models.IntegerField()
    quota = models.IntegerField()
    ratio = models.IntegerField()

    class Meta:
        indexes = [
            models.Index(fields=['name'], name="person_name_idx"),
        ]

    def __str__(self):
        return self.name


class ScrapeError(Base):
    class ModelType(models.TextChoices):
        COMPANY = 'CO', _('Company')
        PERSON = 'PE', _('Person')
        UNKNOWN = 'UK', _('Unknown')
    cr_id = models.CharField(max_length=128, unique=True)
    model_type = models.CharField(
        max_length=2,
        choices=ModelType.choices,
        default=ModelType.UNKNOWN,
    )
    error_message = models.CharField(max_length=255)
