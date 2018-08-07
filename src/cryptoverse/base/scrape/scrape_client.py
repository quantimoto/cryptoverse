import requests
from bs4 import BeautifulSoup


class ScrapeClient:

    @staticmethod
    def get_soup(url):
        response = requests.get(url)
        results = BeautifulSoup(response.text, 'html.parser')
        return results
