from ...base.rest.decorators import Memoize
from ...base.scrape import ScrapeClient


class BitfinexScrape(ScrapeClient):

    @Memoize(expires=60 * 60 * 24)
    def fees(self):
        soup = self.get_soup('https://www.bitfinex.com/fees')

        fees_page_html = soup.find_all('table', class_='striped compact')

        # select table rows with order execution fees
        order_html = fees_page_html[0].find_all('tr')
        order_fees = dict()

        # extract maker and taker fees from lowest tier
        order_fees['maker'] = order_html[1].find_all('td')[1].text
        order_fees['taker'] = order_html[1].find_all('td')[2].text

        # remove '%' sign at the end of the string
        order_fees['maker'] = order_fees['maker'][:-1]
        order_fees['taker'] = order_fees['taker'][:-1]

        # convert str into float
        order_fees['maker'] = float(order_fees['maker'])
        order_fees['taker'] = float(order_fees['taker'])

        # select table rows with margin funding fees
        funding_html = fees_page_html[3].find_all('tr')
        funding_fees = dict()

        # extract normal and hidden funding fees
        funding_fees['normal'] = funding_html[1].find('td', class_='bfx-green-text').text.split(' ', 1)[0]
        funding_fees['hidden'] = funding_html[2].find('td', class_='bfx-green-text').text.split(' ', 1)[0]

        # remove '%' sign at the end of the string
        funding_fees['normal'] = funding_fees['normal'][:-1]
        funding_fees['hidden'] = funding_fees['hidden'][:-1]

        results = {
            'order': order_fees,
            'deposit': None,
            'withdrawal': None,
            'funding': funding_fees,
        }
        return results
