from django.conf import settings
"""
Request Limit for Scraping, pauses for one second
every time limit is reached
"""
REQUEST_LIMIT = 10

"""
URL endpoint for Lebanon Commercial Registry
"""
COMMERCIAL_REGISTRY_URL = 'http://cr.justice.gov.lb/search/result.aspx?id='

"""
How many records to scrape for each governorate
NOTE:
These are estimated original values based on manual searching.
In other words, these were about the highest ids I could find on the LCR website for each
government, and I assume that there aren't more ids higher than them as of 17-12-2020
"""
GOVERNORATE_SCRAPE_LIMIT = {
    1: int(settings.BEIRUT_SCRAPE_LIMIT),
    2: int(settings.MOUNT_LEBANON_SCRAPE_LIMIT),
    3: int(settings.NORTH_LEBANON_SCRAPE_LIMIT),
    4: int(settings.BEKAA_SCRAPE_LIMIT),
    5: int(settings.SOUTH_LEBANON_SCRAPE_LIMIT),
    6: int(settings.NABATIEH_SCRAPE_LIMIT),
}
