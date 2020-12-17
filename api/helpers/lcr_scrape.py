from api.models import Company, Person, ScrapeError
from api import constants

from celery import shared_task
from bs4 import BeautifulSoup
from datetime import datetime
from decimal import Decimal
from django.utils.timezone import make_aware
import requests
import time


class LCRScrape:
    def __init__(self, cr_sub_id, gov):
        self.cr_sub_id = cr_sub_id
        self.governorate = gov
        self.cr_id = str(gov) + str(cr_sub_id).zfill(9)
        self.source_url = constants.COMMERCIAL_REGISTRY_URL + self.cr_id
        self.soup = None
        self.company = None
        self.personnel = {}

    def extract_data(self):
        self.__get_soup()
        self.__get_company()
        self.__get_personnel()

    def __get_soup(self):
        try:
            r = requests.get(self.source_url)
            self.soup = BeautifulSoup(r.content, 'html.parser')
        except Exception as e:
            scrape_error = ScrapeError(
                cr_id=self.cr_id,
                model_type='UK',
                error_message=str(e)
            )
            scrape_error.save()
            raise Exception("Failed to get soup from source url")

    def __get_company(self):
        try:
            self.__scrape_company()
        except Exception as e:
            company_scrape_error = ScrapeError(
                cr_id=self.cr_id,
                model_type='CO',
                error_message=str(e)
            )
            company_scrape_error.save()
            raise Exception("Failed to scrape company")

    def __get_personnel(self):
        if self.company.missing_personnel_data:
            return False
        try:
            self.__scrape_personnel()
        except Exception as e:
            personnel_scrape_error = ScrapeError(
                cr_id=self.cr_id,
                model_type='PE',
                error_message=str(e)
            )
            personnel_scrape_error.save()
            raise Exception("Failed to scrape personnel table")

    def __scrape_company(self):
        """
        Scrapes company data from html elements
        Creates a Company object and saves to database
        """
        registration_date = self.__get_soup_value('DataList1_Label5_0')
        registration_date = datetime.strptime(
            registration_date, '%m/%d/%Y %I:%M:%S %p')
        registration_date = make_aware(registration_date)
        personnel_data = self.soup.find(
            'tr', {'id': 'Relations_ListView_Tr1'})
        missing_personnel_data = False if personnel_data else True
        self.company = Company(
            cr_id=self.cr_id,
            cr_sub_id=self.cr_sub_id,
            source_url=self.source_url,
            registration_number=self.__get_soup_value('DataList1_Label1_0'),
            name=self.__get_soup_value('DataList1_Label2_0'),
            additional_name=self.__get_soup_value('DataList1_Label3_0'),
            governorate=self.governorate,
            registration_date=registration_date,
            record_type=self.__get_soup_value('DataList1_Label6_0'),
            company_status=self.__get_soup_value('DataList1_Label7_0'),
            company_duration=self.__get_soup_value('DataList1_Label8_0'),
            legal_form=self.__get_soup_value('DataList1_Label9_0'),
            capital=self.__get_soup_value('DataList1_Label10_0', 'decimal'),
            title=self.__get_soup_value('DataList1_Label11_0'),
            description=self.__get_soup_value('DataList1_Label12_0'),
            missing_personnel_data=missing_personnel_data
        )
        self.company.save()

    def __scrape_personnel(self):
        """
        Loops through personnel table on company website
            - Scrapes person data from html elements
            - If person has already been scraped
                - Update Person object to include extra relationship
            - Else
                - Create Person object and add to database
        """
        table_rows = self.soup.find(
            'tr', {'id': 'Relations_ListView_Tr1'})
        table_rows = table_rows.parent.findAll('tr')
        table_rows = table_rows[1:]  # Ignore column names
        person_dict = {}
        for index, row in enumerate(table_rows):
            name = self.__get_soup_value(
                'Relations_ListView_desigLabel_' + str(index))
            relationship = self.__get_soup_value(
                'Relations_ListView_relLabel_' + str(index))
            if name in person_dict.keys():
                person = person_dict[name]
                person = self.__update_person(person, relationship, index)

            else:
                person = Person(
                    name=name,
                    company_id=self.company.id,
                    nationality=self.__get_soup_value(
                        'Relations_ListView_countryLabel_' + str(index)),
                    relationship=relationship,
                    stock=self.__get_soup_value(
                        'Relations_ListView_a_valLabel_' + str(index), 'int'),
                    quota=self.__get_soup_value(
                        'Relations_ListView_s_valLabel_' + str(index), 'int'),
                    ratio=self.__get_soup_value(
                        'Relations_ListView_r_valLabel_' + str(index), 'int')
                )
                person_dict[name] = person
        self.personnel = person_dict.values()
        Person.objects.bulk_create(self.personnel)

    def __update_person(self, person, relationship, index):
        person.relationship = person.relationship + ' \\ ' + relationship
        stock = self.__get_soup_value(
            'Relations_ListView_a_valLabel_' + str(index), 'int')
        quota = self.__get_soup_value(
            'Relations_ListView_s_valLabel_' + str(index), 'int')
        ratio = self.__get_soup_value(
            'Relations_ListView_r_valLabel_' + str(index), 'int')
        if person.stock == 0:
            person.stock = stock
        if person.quota == 0:
            person.quota = quota
        if person.ratio == 0:
            person.ratio = ratio

    def __get_soup_value(self, tag_id, cast_type='string'):
        """ Helper for soup element casting """
        contents = self.soup.find('span', {'id': tag_id}).contents
        if contents:
            if cast_type == 'string':
                return str(contents[0])
            elif cast_type == 'decimal':
                return Decimal(contents[0])
            elif cast_type == 'int':
                return int(contents[0])
        else:
            return ''
