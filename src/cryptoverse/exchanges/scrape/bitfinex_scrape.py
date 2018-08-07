from cryptoverse.base.scrape import ScrapeClient


class BitfinexScrape(ScrapeClient):

    def fees(self):
        soup = self.get_soup('https://www.bitfinex.com/fees')

        fees_page_html = soup.find_all('table', class_='striped compact')

        # select table rows with order execution fees
        order_execution_html = fees_page_html[0].find_all('tr')
        order_execution_fees = dict()

        # extract maker and taker fees from lowest tier
        order_execution_fees['maker'] = order_execution_html[1].find_all('td')[1].text
        order_execution_fees['taker'] = order_execution_html[1].find_all('td')[2].text

        # remove '%' sign at the end of the string
        order_execution_fees['maker'] = order_execution_fees['maker'][:-1]
        order_execution_fees['taker'] = order_execution_fees['taker'][:-1]

        # convert str into float
        order_execution_fees['maker'] = float(order_execution_fees['maker'])
        order_execution_fees['taker'] = float(order_execution_fees['taker'])

        # select table rows with margin funding fees
        margin_funding_html = fees_page_html[3].find_all('tr')
        margin_funding_fees = dict()

        # extract normal and hidden funding fees
        margin_funding_fees['normal'] = margin_funding_html[1].find('td', class_='bfx-green-text').text.split(' ', 1)[0]
        margin_funding_fees['hidden'] = margin_funding_html[2].find('td', class_='bfx-green-text').text.split(' ', 1)[0]

        # remove '%' sign at the end of the string
        margin_funding_fees['normal'] = margin_funding_fees['normal'][:-1]
        margin_funding_fees['hidden'] = margin_funding_fees['hidden'][:-1]

        results = {
            'order execution': order_execution_fees,
            'deposit': None,
            'withdrawal': None,
            'margin funding': margin_funding_fees,
        }
        return results
