import logging

from ...base.rest.decorators import Memoize, Retry, RateLimit
from ...base.scrape import ScrapeClient

logger = logging.getLogger(__name__)


class BitfinexScrape(ScrapeClient):

    @Memoize(expires=60 * 60 * 24)
    @Retry(IndexError, wait=60)
    def fees(self):
        soup = self.get_soup('https://www.bitfinex.com/fees')

        fees_page_html = soup.find_all('table', class_='striped compact')

        #
        # select table rows with order execution fees
        order_execution_html = fees_page_html[0].find('tbody').find_all('tr')
        order_execution_fees = list()

        # extract maker and taker fees from lowest tier
        for entry in order_execution_html:
            column_values = entry.find_all('td')
            order_execution_fees.append({
                'Executed in the last 30 days (USD Equivalent)': column_values[0].text.strip(),
                'Maker fees': column_values[1].text.strip(),
                'Taker fees': column_values[2].text.strip(),
            })

        #
        # select table rows with deposit fees
        deposit_html = fees_page_html[1].find('tbody').find_all('tr')
        deposit_fees = list()

        # extract currency, deposit and small deposit fees
        for entry in deposit_html:
            column_values = entry.find_all('td')
            deposit_fees.append({
                'Currency': column_values[0].text.strip(),
                'Deposit': column_values[1].text.strip(),
                'Small Deposit*': column_values[2].text.strip()
            })

        #
        # select table rows with withdrawal fees
        withdrawal_html = fees_page_html[2].find('tbody').find_all('tr')
        withdrawal_fees = list()

        # extract currency and fees
        for entry in withdrawal_html:
            column_values = entry.find_all('td')
            withdrawal_fees.append({
                'Currency': column_values[0].text.strip(),
                'Fee': column_values[1].text.strip(),
            })

        #
        # select table rows with margin funding fees
        margin_funding_html = fees_page_html[3].find('tbody').find_all('tr')
        margin_funding_fees = list()

        # extract normal and hidden funding fees
        for entry in margin_funding_html:
            column_values = entry.find_all('td')
            margin_funding_fees.append({
                'Description': column_values[0].text.strip(),
                'Fee': column_values[1].text.strip(),
            })

        results = {
            'Order Execution': order_execution_fees,
            'Deposit': deposit_fees,
            'Withdrawal': withdrawal_fees,
            'Margin Funding': margin_funding_fees,
        }
        return results
