from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from datetime import datetime
import requests
import pandas as pd
import sys 

#function to retrieve tickers that have earnings on a certain date 
#@param date string in ISO 8601 format 
#@returns dictionary with ticker as keys and earning call time as values

def getTickerInfo(desired_date):
    #set options for webdriver
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--headless')
    options.add_argument('--disable-dev-shm-usage')

    #target url to scrape based on desired date 
    url = "https://finance.yahoo.com/calendar/earnings?day={}".format(desired_date)

    #webdriver instantiation 
    web_driver = webdriver.Chrome('chromedriver', options=options)

    #visit yahoo earnings calendar and get page source 
    web_driver.implicitly_wait(6)
    web_driver.get(url)
    html = web_driver.page_source

    #check for table and load to pandas df or return if no tables are found
    earnings_results = []
    try:
        earnings_results = pd.read_html(html)
    except Exception as e: 
        print('no earnings on {}'.format(desired_date))
        
    #load first table and extract columns 'Symbol' and 'Earnings Call Time' into dictionary
    earnings_df = earnings_results[0]
    data = dict(zip(earnings_df['Symbol'], earnings_df['Earnings Call Time']))
    
    #check to see if there is a next table
    while True:
        try:
            #wait to check if button is clickable 
            WebDriverWait(web_driver, 2).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="cal-res-table"]/div[2]/button[3]'))).click()  
        except:
            break
        else:
            #if next button clicked wait and get new table, retrieve columns, append to data dicitonary 
            html2 = web_driver.page_source
            earnings_results_next = pd.read_html(html2)  
            earnings_df_next = earnings_results_next[0]
            data2 = dict(zip(earnings_df_next['Symbol'], earnings_df_next['Earnings Call Time']))
            data.update(data2)
    return data


