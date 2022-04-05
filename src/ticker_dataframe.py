import plotly.graph_objects as go
import pandas as pd
import requests
from config import api_key
import json



class TickerDataFrame:
    """class TickerDataFrame: used to store price history render candlestick chart 

        Attributes: 
            ticker              ticker symbol string
            ticker_rep_tm       ticker symbol earnings reporting time  
            history_data        list to hold api response with price history data 
            df                  pandas dataframe for housing price data and creating new data features 

        Methods:
            getHisoryData_1d_6mo    creates api call to yahoo finance to retrieve 1-day 6-month price history data 
            fillDataFrame           parses api response and populates dataframe, convert timestamp into date, 
                                    calculate 20 day EMA and 50 day EMA columns, trim df  
            renderChart             utilizes plotly to render candlestick chart for past 3 months 
                                
    """     

    ticker = ''
    ticker_rep_tm = ''
    history_data = []
    df = None

    def __init__(self, ticker, rp_time):
        self.ticker = ticker
        self.ticker_rep_tm = rp_time
        
    
    def getHistoryData_1d_6mo(self):
        yh_api_endpnt = "https://yfapi.net/v8/finance/chart/{}".format(self.ticker)
        paramaters = {
            "interval":'1d',
            "range":'6mo',
        }
        headers = {
            'x-api-key': api_key
        }
        response = requests.request("GET", yh_api_endpnt, headers=headers, params=paramaters)
        self.history_data = json.loads(response.text)



    def fillDataFrame(self, history_data):
        df = pd.DataFrame()
        df['date'] = history_data['chart']['result'][0]['timestamp']
        df['low'] = history_data['chart']['result'][0]['indicators']['quote'][0]['low']
        df['high'] = history_data['chart']['result'][0]['indicators']['quote'][0]['high']
        df['open'] = history_data['chart']['result'][0]['indicators']['quote'][0]['open']
        df['close'] = history_data['chart']['result'][0]['indicators']['quote'][0]['close']
        df['volume'] = history_data['chart']['result'][0]['indicators']['quote'][0]['volume']
        df['date'] = pd.to_datetime(df['date'], unit='s').dt.date
        df['symbol'] = history_data['chart']['result'][0]['meta']['symbol']
        df['20-Day EMA'] = df['close'].ewm(span=20,min_periods=20,adjust=False,ignore_na=False).mean()
        df['50-Day EMA'] = df['close'].ewm(span=50,min_periods=50,adjust=False,ignore_na=False).mean()
        self.df = df.tail(65)

    def renderChart(self):
    
        fig = go.Figure(data=[go.Candlestick(
            x = self.df['date'],
            open = self.df['open'],
            close = self.df['close'],
            high = self.df['high'],
            low = self.df['low']
        )])

        fig.update_layout(xaxis_rangeslider_visible=False, template="plotly_dark",
        title="{} 90 day Chart          Reporting time:{}".format(self.ticker, self.ticker_rep_tm), 
        yaxis_title="{} stock".format(self.ticker), width=950, height=550)
        ema_trace_20 = go.Scatter(x=self.df['date'], y=self.df['20-Day EMA'], mode='lines', name='20EMA', line={"color":"goldenrod"})
        ema_trace_50 = go.Scatter(x=self.df['date'], y=self.df['50-Day EMA'], mode='lines', name='50EMA', line={'color':'lightskyblue'})

        fig.add_trace(ema_trace_20)
        fig.add_trace(ema_trace_50)


        fig.update_xaxes(
            rangebreaks=[
                dict(bounds=["sat", "mon"]), #hide weekends
                dict(values=["2021-12-25", "2021-01-01"])  # hide Christmas and New Year's
            ]
        )
        fig.show()
