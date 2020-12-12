# @app.task(bind=True)
from .models import Company, Person, PersonCompany

from bs4 import BeautifulSoup
from datetime import datetime
from decimal import Decimal
import requests

COMMERCIAL_REGISTRY_URL = 'http://cr.justice.gov.lb/search/result.aspx?id='

# Current Governorates with Registered Companies on
# the Lebanese Commercial Registry
GOVERNORATES = {
    "BE": "1",
    "ML": "2",
    "NL": "3",
    "BA": "4",
    "SL": "5",
    "NA": "6",
}


def scrape_lcr():
    for gov in GOVERNORATES:
        base_url = COMMERCIAL_REGISTRY_URL + GOVERNORATES[gov]
        keep_scraping = True
        last_company = Company.objects.filter(governorate=gov).last()
        cr_id = last_company.cr_id + 1 if last_company else 1
        while(keep_scraping):
            url = base_url + str(cr_id).zfill(9)
            try:
                r = requests.get(url)
                soup = BeautifulSoup(r.content, 'html.parser')
                company = extract_company_data(soup, cr_id, url, gov)
                personnel_data = extract_personnel_data(soup, company)
            except Exception as e:
                print('The scraping job failed. See exception: ')
                print(e)
            break
        break


def extract_company_data(soup, cr_id, source_url, governorate):
    registration_number = get_value(soup, "DataList1_Label1_0")
    name = get_value(soup, "DataList1_Label2_0")
    additional_name = get_value(soup, "DataList1_Label3_0")
    registration_date = get_value(soup, "DataList1_Label5_0")
    registration_date = datetime.strptime(
        registration_date, "%m/%d/%Y %I:%M:%S %p")
    record_type = get_value(soup, "DataList1_Label6_0")
    company_status = get_value(soup, "DataList1_Label7_0")
    company_duration = get_value(soup, "DataList1_Label8_0")
    legal_form = get_value(soup, "DataList1_Label9_0")
    capital = get_value(soup, "DataList1_Label10_0", "decimal")
    title = get_value(soup, "DataList1_Label11_0")
    description = get_value(soup, "DataList1_Label12_0")

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
        description=description
    )
    company.save()
    return company


def extract_personnel_data(soup, company):
    person_list = []
    person_company_list = []
    table_rows = soup.find(
        "tr", {"id": "Relations_ListView_Tr1"}).parent.findAll('tr')
    table_rows = table_rows[1:]  # Ignore column names
    for index, row in enumerate(table_rows):
        name = get_value(row, "Relations_ListView_desigLabel_" + str(index))
        nationality = get_value(
            row, "Relations_ListView_countryLabel_" + str(index))
        relationship = get_value(
            row, "Relations_ListView_relLabel_" + str(index))
        stock = get_value(row, "Relations_ListView_a_valLabel_" + str(index))
        quota = get_value(row, "Relations_ListView_s_valLabel_" + str(index))
        ratio = get_value(row, "Relations_ListView_r_valLabel_" + str(index))
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
        person_list.append(person)
        person_company_list.append(person_company)
    person_company_list = PersonCompany.objects.bulk_create(
        person_company_list)
    return person_list


def get_value(soup, id, cast_type="string"):
    contents = soup.find("span", {"id": id}).contents
    if contents:
        if cast_type == "string":
            return str(contents[0])
        elif cast_type == "decimal":
            return Decimal(contents[0])
    else:
        return ""
