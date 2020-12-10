@app.task(bind=True)
def scrape_lcr(self):
    print('Request: {0!r}'.format(self.request))
