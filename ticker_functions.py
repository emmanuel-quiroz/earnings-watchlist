from yahoo_finance_earnings_scraper import *
import json
import plotly.graph_objects as go
from config import api_key


#function to retrieve top 8 tickers by marketcap
#@param date string in ISO 8601 format 
#@returns dictionary with ticker as keys and earning call time as values

def getTopTickers(date):
    #check yahoo finance for earnings  earnings on given day
    try:
        earnings_dict = getTickerInfo(date)
        all_tickers = ",".join(earnings_dict.keys())
    except:
        print('No earnings on {}'.format(date))
        return 
        
    #call yahoo api for quote information on all tickers returned from earnings calendar
    yahoo_api_endpoint = "https://yfapi.net/v6/finance/quote"
    querystring = {"symbols":all_tickers}
    headers = {'x-api-key': api_key }

    #send request and parse request response text  
    response = requests.request("GET", yahoo_api_endpoint, headers=headers, params=querystring)
    real_data = json.loads(response.text)
    response_list = real_data['quoteResponse']["result"]

    #iterate to get marketcaps 
    top_tickers = {}
    for index in range(len(response_list)):
        try:
            top_tickers[response_list[index]["symbol"]] = response_list[index]["marketCap"]
        except:
            continue
   
    #sort dictionary and trim 
    top_tickers = list(sorted(top_tickers.items(), key= lambda x:x[1], reverse=True))
    top_tickers = top_tickers[:8]
    top_tickers = dict(top_tickers)

    #replace market cap value with reporting time
    for key in top_tickers:
        top_tickers[key] = earnings_dict[key]

    return top_tickers


#function to retrieve 1 day 6 months chart data from yahoo finance api
#@param ticker symbol  
#@returns json response object 
def getHistoryData_1d_6mo(ticker):
    #retrieve price history data yahoo api endpoint, paramaters, headers
    yh_api_endpnt = "https://yfapi.net/v8/finance/chart/{}".format(ticker)
    paramaters = {
        "interval":'1d',
        "range":'6mo',
    }
    headers = {
        'x-api-key':  api_key
    }
    #make request and parse response
    response = requests.request("GET", yh_api_endpnt, headers=headers, params=paramaters)
    response_text = json.loads(response.text)
    return response_text

#function to retrieve 5 min 1 day  chart data from yahoo finance api
#@param ticker symbol  
#@returns json response object 
def getHistoryData_5m_1d(ticker):
    #retrieve price history data yahoo api endpoint, paramaters, headers
    yh_api_endpnt = "https://yfapi.net/v8/finance/chart/{}".format(ticker)
    paramaters = {
        "interval":'5m',
        "range":'1d',
    }
    headers = {
        'x-api-key':  api_key
    }
    #make request and parse response
    response = requests.request("GET", yh_api_endpnt, headers=headers, params=paramaters)
    response_text = json.loads(response.text)
    return response_text

#function to create DataFrame from json response
#@param json response 
#@returns DataFrame 
#@data-cleaning:
#   -convert timestamp into date
#   -calculate 20 day EMA and 50 day EMA columns 
#   -trim DataFrame to display both EMAs
def createDataFrame(response_text):
    df = pd.DataFrame()
    df['date'] = response_text['chart']['result'][0]['timestamp']
    df['high'] = response_text['chart']['result'][0]['indicators']['quote'][0]['high']
    df['low'] = response_text['chart']['result'][0]['indicators']['quote'][0]['low']
    df['open'] = response_text['chart']['result'][0]['indicators']['quote'][0]['open']
    df['close'] = response_text['chart']['result'][0]['indicators']['quote'][0]['close']
    df['volume'] = response_text['chart']['result'][0]['indicators']['quote'][0]['volume']
    df['date'] = pd.to_datetime(df['date'], unit='s').dt.date
    df['symbol'] = response_text['chart']['result'][0]['meta']['symbol']
    df['20-Day EMA'] = df['close'].ewm(span=20,min_periods=20,adjust=False,ignore_na=False).mean()
    df['50-Day EMA'] = df['close'].ewm(span=50,min_periods=50,adjust=False,ignore_na=False).mean()
    df = df.tail(65)
    return df

#function to display 90 day chart 
#@param Dataframe, dictionary with reporting time
#@returns json response object 
def renderChart(df, ticker_dict):
    ticker_name = df["symbol"].iloc[0]

    fig = go.Figure(data=[go.Candlestick(
        x = df['date'],
        open = df['open'],
        close = df['close'],
        high = df['high'],
        low = df['low']
    )])

    fig.update_layout(xaxis_rangeslider_visible=False, template="plotly_dark",
     title="{} 90 day Chart          Reporting time:{}".format(ticker_name, ticker_dict[ticker_name]), 
     yaxis_title="{} stock".format(ticker_name), width=950, height=550)
    ema_trace_20 = go.Scatter(x=df['date'], y=df['20-Day EMA'], mode='lines', name='20EMA', line={"color":"goldenrod"})
    ema_trace_50 = go.Scatter(x=df['date'], y=df['50-Day EMA'], mode='lines', name='50EMA', line={'color':'lightskyblue'})

    fig.add_trace(ema_trace_20)
    fig.add_trace(ema_trace_50)


    fig.update_xaxes(
        rangebreaks=[
            dict(bounds=["sat", "mon"]), #hide weekends
            dict(values=["2015-12-25", "2016-01-01"])  # hide Christmas and New Year's
        ]
    )
    fig.show()
        