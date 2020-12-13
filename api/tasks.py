from .models import Company, Person, PersonCompany, ScrapeError

from celery import Celery
from bs4 import BeautifulSoup
from datetime import datetime
from decimal import Decimal
from django.utils.timezone import make_aware
import requests

app = Celery('tasks')

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


def scrape_lcr():
    for gov in GOVERNORATES:
        keep_scraping = 0
        cr_sub_id = get_initial_cr_sub_id(gov)
        while(keep_scraping < 3):
            run_scrape.delay(cr_sub_id, gov)
            keep_scraping += 1
            # break


@app.task(bind=True)
def run_scrape(self, cr_sub_id, gov):
    print("hello celery")
    cr_sub_id += 1
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


def get_initial_cr_sub_id(gov):
    last_company = Company.objects.filter(governorate=gov).last()
    if last_company:
        last_cr_sub_id = int(last_company.cr_id.rsplit('0')[-1])
        cr_sub_id = last_cr_sub_id
    else:
        cr_sub_id = 1
    return cr_sub_id


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
    registration_number = get_value(soup, 'DataList1_Label1_0')
    name = get_value(soup, 'DataList1_Label2_0')
    additional_name = get_value(soup, 'DataList1_Label3_0')
    registration_date = get_value(soup, 'DataList1_Label5_0')
    registration_date = datetime.strptime(
        registration_date, '%m/%d/%Y %I:%M:%S %p')
    registration_date = make_aware(registration_date)
    record_type = get_value(soup, 'DataList1_Label6_0')
    company_status = get_value(soup, 'DataList1_Label7_0')
    company_duration = get_value(soup, 'DataList1_Label8_0')
    legal_form = get_value(soup, 'DataList1_Label9_0')
    capital = get_value(soup, 'DataList1_Label10_0', 'decimal')
    title = get_value(soup, 'DataList1_Label11_0')
    description = get_value(soup, 'DataList1_Label12_0')
    personnel_data = soup.find(
        'tr', {'id': 'Relations_ListView_Tr1'})
    missing_personnel_data = False if personnel_data else True
    company = Company(
        cr_id=cr_id,
        source_url=source_url,
        registration_number=registration_number,
        name=name,
        additional_name=additional_name,
        governorate=governorate,
        registration_date=registration_date,
        record_type=record_type,
        company_status=company_status,
        company_duration=company_duration,
        legal_form=legal_form,
        capital=capital,
        title=title,
        description=description,
        missing_personnel_data=missing_personnel_data
    )
    company.save()
    return company


def extract_personnel_data(soup, company):
    """
    Loops through personnel table on company website
        - Scrapes person data from html elements
        - If person has already been scraped
            - Update PersonCompany object to include extra relationship
        - Else
            - Create Person object and add to database
            - Create PersonCompany object and add to database
    """
    table_rows = soup.find(
        'tr', {'id': 'Relations_ListView_Tr1'})
    table_rows = table_rows.parent.findAll('tr')
    table_rows = table_rows[1:]  # Ignore column names
    person_company_dict = {}
    for index, row in enumerate(table_rows):
        name = get_value(row, 'Relations_ListView_desigLabel_' + str(index))
        nationality = get_value(
            row, 'Relations_ListView_countryLabel_' + str(index))
        relationship = get_value(
            row, 'Relations_ListView_relLabel_' + str(index))
        stock = get_value(row, 'Relations_ListView_a_valLabel_' + str(index))
        quota = get_value(row, 'Relations_ListView_s_valLabel_' + str(index))
        ratio = get_value(row, 'Relations_ListView_r_valLabel_' + str(index))
        if name in person_company_dict.keys():
            person_company = person_company_dict[name]
            person_company.relationship = person_company.relationship + '\\' + relationship
            person_company.save()
        else:
            person = Person(
                name=name,
                nationality=nationality,
            )
            person.save()
            person_company = PersonCompany(
                person_id=person.id,
                company_id=company.id,
                relationship=relationship,
                stock=stock,
                quota=quota,
                ratio=ratio
            )
            person_company.save()
            person_company_dict[name] = person_company
    return person_company_dict


def get_value(soup, id, cast_type='string'):
    contents = soup.find('span', {'id': id}).contents
    if contents:
        if cast_type == 'string':
            return str(contents[0])
        elif cast_type == 'decimal':
            return Decimal(contents[0])
    else:
        return ''
