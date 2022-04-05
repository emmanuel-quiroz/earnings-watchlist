import json
import requests
from config import api_key

class TopEarningsDriver:
    """class TopEarningsDriver used to handle scrapeYahoo return data

    Attributes:
        tickers         Dicitionary containing ticker symbol as key and reporting time as value
        quotes          response list returned by yahoo finance api containing marketcap data 
        marketcaps      Dictionar containing ticker symbol as key and marketcap as value

    Methods:
        getQuotes           creates api call for all symbols in tickers and stores result in quotes
        extractMarketCap    parses api response and extracts symbol and marketcap value and places them in marketcaps 
        trimTopEight        sort tickers my marketcap value, trim and keep top eight ticker symbols 
    
    """
    
    tickers = {}
    quotes = []
    market_caps = {}

    def __init__(self, tickers):
        self.tickers = tickers

    def getQuotes(self):
        all_tickers = ",".join(self.tickers.keys())

        yahoo_api_endpoint = "https://yfapi.net/v6/finance/quote"
        querystring = {"symbols":all_tickers}
        headers = {'x-api-key': api_key}

        response = requests.request("GET", yahoo_api_endpoint, headers=headers, params=querystring)
        real_data = json.loads(response.text)
        self.quotes = real_data['quoteResponse']["result"]
        

    def extractMarketCaps(self):
        self.market_caps = {}
        for index in range(len(self.quotes)):
            try:
                self.market_caps[self.quotes[index]["symbol"]] = self.quotes[index]["marketCap"]
            except:
                continue
        
        
    def trimTopEight(self):
        top_eight = self.market_caps
        top_eight = list(sorted(top_eight.items(), key= lambda x:x[1], reverse=True))
        top_eight = top_eight[:8]
        self.market_caps = dict(top_eight)

        temp_dict = {}
        for key in self.market_caps:
            temp_dict[key] = self.tickers[key]
        
        self.tickers = temp_dict
    
