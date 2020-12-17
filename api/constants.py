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
    1: 117000,
    2: 127660,
    3: 50000,
    4: 24100,
    5: 24560,
    6: 10000,
}
