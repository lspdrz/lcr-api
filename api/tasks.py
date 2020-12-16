from api.models import Company, Person, ScrapeError
from api.helpers.lcr_scrape import LCRScrape
from api import constants

from celery import shared_task
from bs4 import BeautifulSoup
from datetime import datetime
from decimal import Decimal
from django.utils.timezone import make_aware
import requests
import time


@shared_task
def scrape_lcr():
    scrape_count = 0
    governorates = Company.Governorate
    for gov in governorates:
        keep_scraping = 0
        cr_sub_id = get_initial_cr_sub_id(gov)
        while(keep_scraping < 3):
            if scrape_count % constants.REQUEST_LIMIT == 0:
                time.sleep(1)  # So we don't overload the Lebanon CR server
            cr_sub_id += 1
            try:
                run_scrape.delay(cr_sub_id, gov)
            except Exception as e:
                print("Scrape didn't work")
                print(e)
                pass
            scrape_count += 1
            keep_scraping += 1


@shared_task
def run_scrape(cr_sub_id, gov):
    scrape = LCRScrape(cr_sub_id, gov)
    scrape.extract_data()


def get_initial_cr_sub_id(gov):
    try:
        last_company = Company.objects.filter(
            governorate=gov).latest('cr_sub_id')
    except Company.DoesNotExist:
        return 0  # First company ever scraped!
    return last_company.cr_sub_id
