from .models import Company, Person, ScrapeError

from celery import shared_task
from bs4 import BeautifulSoup
from datetime import datetime
from decimal import Decimal
from django.utils.timezone import make_aware
import requests
import time

COMMERCIAL_REGISTRY_URL = 'http://cr.justice.gov.lb/search/result.aspx?id='

# Current Governorates with Registered Companies on
# the Lebanese Commercial Registry
GOVERNORATES = {
    'BE': '1',
    'ML': '2',
    'NL': '3',
    'BA': '4',
    'SL': '5',
    'NA': '6',
}

REQUEST_LIMIT = 10


@shared_task
def scrape_lcr():
    scrape_count = 0
    for gov in GOVERNORATES:
        keep_scraping = True
        cr_sub_id = get_initial_cr_sub_id(gov)
        while(keep_scraping):
            if scrape_count % REQUEST_LIMIT == 0:
                time.sleep(1)  # So we don't overload the Lebanon CR server
            cr_sub_id += 1
            run_scrape.delay(cr_sub_id, gov)
            scrape_count += 1


@shared_task
def run_scrape(cr_sub_id, gov):
    cr_id = GOVERNORATES[gov] + str(cr_sub_id).zfill(9)
    url = COMMERCIAL_REGISTRY_URL + cr_id
    try:
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'html.parser')
        extract_data(soup, cr_id, url, gov)
    except Exception as e:
        print("Scrape didn't work")
        print(e)
        pass


def extract_data(soup, cr_id, url, gov):
    try:
        company = extract_company_data(soup, cr_id, url, gov)
    except Exception as e:
        company_scrape_error = ScrapeError(
            cr_id=cr_id,
            model_type='CO',
            error_message=str(e)
        )
        company_scrape_error.save()
        raise Exception("Failed to scrape company")
    if not company.missing_personnel_data:
        try:
            personnel = extract_personnel_data(soup, company)
        except Exception as e:
            person_scrape_error = ScrapeError(
                cr_id=cr_id,
                model_type='PE',
                error_message=str(e)
            )
            person_scrape_error.save()
            raise Exception("Failed to scrape personnel table")


def extract_company_data(soup, cr_id, source_url, governorate):
    """
    Scrapes company data from html elements
    Creates a Company object and saves to database
    """
    registration_date = get_value(soup, 'DataList1_Label5_0')
    registration_date = datetime.strptime(
        registration_date, '%m/%d/%Y %I:%M:%S %p')
    registration_date = make_aware(registration_date)
    personnel_data = soup.find(
        'tr', {'id': 'Relations_ListView_Tr1'})
    missing_personnel_data = False if personnel_data else True
    company = Company(
        cr_id=cr_id,
        cr_sub_id=get_cr_sub_id(cr_id),
        source_url=source_url,
        registration_number=get_value(soup, 'DataList1_Label1_0'),
        name=get_value(soup, 'DataList1_Label2_0'),
        additional_name=get_value(soup, 'DataList1_Label3_0'),
        governorate=governorate,
        registration_date=registration_date,
        record_type=get_value(soup, 'DataList1_Label6_0'),
        company_status=get_value(soup, 'DataList1_Label7_0'),
        company_duration=get_value(soup, 'DataList1_Label8_0'),
        legal_form=get_value(soup, 'DataList1_Label9_0'),
        capital=get_value(soup, 'DataList1_Label10_0', 'decimal'),
        title=get_value(soup, 'DataList1_Label11_0'),
        description=get_value(soup, 'DataList1_Label12_0'),
        missing_personnel_data=missing_personnel_data
    )
    company.save()
    return company


def extract_personnel_data(soup, company):
    """
    Loops through personnel table on company website
        - Scrapes person data from html elements
        - If person has already been scraped
            - Update Person object to include extra relationship
        - Else
            - Create Person object and add to database
    """
    table_rows = soup.find(
        'tr', {'id': 'Relations_ListView_Tr1'})
    table_rows = table_rows.parent.findAll('tr')
    table_rows = table_rows[1:]  # Ignore column names
    person_dict = {}
    for index, row in enumerate(table_rows):
        name = get_value(row, 'Relations_ListView_desigLabel_' + str(index))
        relationship = get_value(
            row, 'Relations_ListView_relLabel_' + str(index))
        if name in person_dict.keys():
            person = person_dict[name]
            person.relationship = person.relationship + ' \\ ' + relationship
            person.save()
        else:
            person = Person(
                name=name,
                company_id=company.id,
                nationality=get_value(
                    row, 'Relations_ListView_countryLabel_' + str(index)),
                relationship=relationship,
                stock=get_value(
                    row, 'Relations_ListView_a_valLabel_' + str(index)),
                quota=get_value(
                    row, 'Relations_ListView_s_valLabel_' + str(index)),
                ratio=get_value(
                    row, 'Relations_ListView_r_valLabel_' + str(index))
            )
            person.save()
            person_dict[name] = person
    return person_dict


def get_initial_cr_sub_id(gov):
    try:
        last_company = Company.objects.filter(
            governorate=gov).latest('cr_sub_id')
    except Company.DoesNotExist:
        return 0  # First company ever scraped!
    return last_company.cr_sub_id


def get_cr_sub_id(cr_id):
    start_index = next(i for i, x in enumerate(cr_id) if x != '0' and i != 0)
    return int(cr_id[start_index:])


def get_value(soup, tag_id, cast_type='string'):
    """ Helper for soup element casting """
    contents = soup.find('span', {'id': tag_id}).contents
    if contents:
        if cast_type == 'string':
            return str(contents[0])
        elif cast_type == 'decimal':
            return Decimal(contents[0])
    else:
        return ''
