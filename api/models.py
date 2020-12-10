from django.db import models


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

    cr_id = models.IntegerField()
    name = models.CharField(max_length=255)
    registration_number = models.IntegerField()
    additional_name = models.CharField(max_length=255)
    record_type = models.CharField()
    registration_date = models.DateTimeField()
    governorate = models.CharField(
        max_length=2,
        choices=Governorate.choices,
        default=Governorate.UNKNOWN,
    )
    legal_form = models.CharField()
    partnership_duration = models.CharField()
    company_status = models.CharField()
    title = models.CharField()
    capital = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField()


class Individual(Base):
    name = models.CharField(max_length=255)
    nationality = models.CharField()


class IndividualCompany(Base):
    individual = models.ForeignKey(Individual, related_name="individual",
                                   on_delete=models.CASCADE)
    company = models.ForeignKey(Company, related_name="company",
                                on_delete=models.CASCADE)
    relationship = models.CharField()
    stocks = models.IntegerField()
