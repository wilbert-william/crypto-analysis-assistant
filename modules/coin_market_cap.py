from requests import Session
import json

from tools import api

class api_list():
    def __init__(self):
        self.url_categories = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/categories'
        self.url_category = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/category'
        self.url_fearngreed_latest = 'https://pro-api.coinmarketcap.com/v3/fear-and-greed/latest'
        self.url_fearngreed_historical = 'https://pro-api.coinmarketcap.com/v3/fear-and-greed/historical'
        self.url_metadata = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/info'
        self.url_metrics_latest = 'https://pro-api.coinmarketcap.com/v1/global-metrics/quotes/latest'
        self.url_top100 = 'https://pro-api.coinmarketcap.com/v3/index/cmc100-latest'
        self.url_current_price = 'https://pro-api.coinmarketcap.com/v1/tools/price-conversion'
        cmc_instance = api.API()
        self.cmc_api = cmc_instance.cmc_api()
    
    
    def categories(self) -> str:
        """Returns information about all coin categories available on CoinMarketCap.
        Includes a paginated list of cryptocurrency quotes and metadata from each category."""
        url = self.url_categories
        parameters = {
          'limit':'500',
        }
        headers = {
          'Accepts': 'application/json',
          'X-CMC_PRO_API_KEY': self.cmc_api,
        }

        session = Session()
        session.headers.update(headers)

        response = session.get(url, params=parameters)
        data_categories = json.loads(response.text)

        return data_categories['data']
    
    def category(self, input_id:str) -> str:
        """Returns information about a single coin category available on CoinMarketCap. 
        Includes a paginated list of the cryptocurrency quotes and metadata for the category."""
        url = self.url_category
        parameters = {
        'id': f'{input_id}'
        }
        headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': self.cmc_api,
        }

        session = Session()
        session.headers.update(headers)

        response = session.get(url, params=parameters)
        category_data = json.loads(response.text)
        
        return category_data['data']
    
    def fearngreed_latest(self) -> str:
        """Returns the lastest CMC Crypto Fear and Greed value."""
        try:
            url = self.url_fearngreed_latest
            headers = {
              'Accepts': 'application/json',
              'X-CMC_PRO_API_KEY': self.cmc_api
            }

            session = Session()
            session.headers.update(headers)

            response = session.get(url)
            response.raise_for_status()  
            data = json.loads(response.text)
            return data['data']
        except Exception as e:
            return {'error': f'Failed to fetch fear and greed data: {str(e)}'}

    def fearngreed_historical(self, limit:str) -> str:
        """Returns a paginated list of all CMC Crypto Fear and Greed values at 12am UTC time."""
        try:
            if not isinstance(limit, (int, str)) or str(limit).strip() == '':
                return {'error': 'Invalid limit parameter'}

            url = self.url_fearngreed_historical
            parameters = {
                'limit': str(limit)
            }
            headers = {
              'Accepts': 'application/json',
              'X-CMC_PRO_API_KEY': self.cmc_api
            }

            session = Session()
            session.headers.update(headers)

            response = session.get(url, params=parameters)
            response.raise_for_status()
            data = json.loads(response.text)
            return data['data']
        except Exception as e:
            return {'error': f'Failed to fetch historical fear and greed data: {str(e)}'}

    def metadata(self, symbol:str) -> str:
        """Returns all static metadata available for one or more cryptocurrencies. 
        This information includes details like logo, description, official website URL, 
        social links, and links to a cryptocurrency's technical documentation."""
        try:
            if not symbol or not isinstance(symbol, str):
                return {'error': 'Invalid symbol parameter'}

            url = self.url_metadata
            parameters = {
              'symbol': symbol,
            }
            headers = {
              'Accepts': 'application/json',
              'X-CMC_PRO_API_KEY': self.cmc_api,
            }

            session = Session()
            session.headers.update(headers)

            response = session.get(url, params=parameters)
            response.raise_for_status()
            data = json.loads(response.text)
            return data['data']
        except Exception as e:
            return {'error': f'Failed to fetch metadata: {str(e)}'}

    def metrics_latest(self) -> str:
        """Returns the latest global cryptocurrency market metrics."""
        try:
            url = self.url_metrics_latest
            headers = {
              'Accepts': 'application/json',
              'X-CMC_PRO_API_KEY': self.cmc_api,  
            }

            session = Session()
            session.headers.update(headers)

            response = session.get(url)
            response.raise_for_status()
            data = json.loads(response.text)
            return data['data']
        except Exception as e:
            return {'error': f'Failed to fetch latest metrics: {str(e)}'}

    def top100(self) -> str:
        """Returns the lastest CoinMarketCap 100 Index value, constituents, and constituent weights."""
        try:
            url = self.url_top100
            headers = {
              'Accepts': 'application/json',
              'X-CMC_PRO_API_KEY': self.cmc_api,  
            }

            session = Session()
            session.headers.update(headers)

            response = session.get(url)
            response.raise_for_status()
            data = json.loads(response.text)
            return data['data']
        except Exception as e:
            return {'error': f'Failed to fetch top 100 data: {str(e)}'}
        
    def current_price(self, symbol:str) -> str:
        """return the latest price of 1 amount of cryptocurrency"""
        try:
            url = self.url_current_price
            parameters = {
                'symbol': f'{symbol}',
                'amount': '1'
            }
            headers = {
                'Accepts': 'application/json',
                'X-CMC_PRO_API_KEY': self.cmc_api,
            }

            session = Session()
            session.headers.update(headers)

            response = session.get(url, params=parameters)
            data = json.loads(response.text)
            return data['data']
        except Exception as e:
            return {'error': f'Failed to fetch current_price: {str(e)}'}