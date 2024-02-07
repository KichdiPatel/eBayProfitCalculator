import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pandas as pd
from scipy import stats
# from selenium import webdriver
# from selenium.webdriver.common.by import By
import time as time


def getURL(search):
    search_upd = ""
    for word in search.split():
        search_upd += word + "+"
    
    search_upd = search_upd.rstrip(search_upd[-1])

    url = f"https://www.ebay.com/sch/i.html?_from=R40&_nkw={search_upd}&_sacat=0&LH_ItemCondition=3000&LH_BIN=1&LH_PrefLoc=1&rt=nc&LH_Sold=1&LH_Complete=1"

    return url

def checkDates(s, is_expensive):
    results = s.find(id='mainContent')
    div_elements = results.find_all('div',class_='s-item__title--tag')
    uncleaned_dates = [div.find('span', class_='POSITIVE') for div in div_elements if div.find('span', class_='POSITIVE')]
    cleaned_dates = [date.get_text(strip=True).replace('Sold  ', '') for date in uncleaned_dates]
    if(len(cleaned_dates) < 4):
        return False
    
    date_to_check = cleaned_dates[3]
    date_to_check = date_to_check.replace(",", "")
    date_obj = datetime.strptime(date_to_check, "%b %d %Y")

    now = datetime.now()
    difference = abs((date_obj - now).days)-1
    if(is_expensive):
        return (difference <=15)
    else:
        return (difference <=10)
    
def getEstPrice(s):
    results = s.find(id='mainContent')
    div_elements = results.find_all('div',class_='s-item__detail s-item__detail--primary')
    uncleaned_prices = [div.find('span', class_='POSITIVE') for div in div_elements if div.find('span', class_='POSITIVE')]
    cleaned_prices = [date.get_text(strip=True).replace('$', '') for date in uncleaned_prices]
    
    data = []
    rg = 15
    if(len(cleaned_prices) < 15):
        rg = len(cleaned_prices)
    
    for i in range(rg):
        p = cleaned_prices[i].replace(",", "")
        data.append(float(p))
    
    df = pd.DataFrame(data, columns=['Prices'])

    # Calculate Z-scores for the 'Values' column
    z_scores = abs(stats.zscore(df['Prices']))

    # Define a Z-score threshold (e.g., 2 for a 95% confidence interval)
    z_score_threshold = 2

    # Filter the DataFrame to exclude rows with Z-scores above the threshold
    filtered_df = df[z_scores <= z_score_threshold]


    estPrice = round(filtered_df['Prices'].mean()*0.75, 2)
    
    return estPrice

def get_breakeven(product_search):
    url = getURL(product_search)
    html = requests.get(url)
    s = BeautifulSoup(html.content, 'html.parser')

    sale_price = getEstPrice(s)
    is_expensive = sale_price > 1000

    if(checkDates(s,is_expensive)):
        breakeven = round(sale_price, 2)
        return breakeven
    elif(is_expensive):
        # print("4 not sold in last 15 days")
        return -1000000
    else:
        # print("4 not sold in last 10 days")
        return -1000000
 

"""
Iterate through the csv(["checked?" == 0]):
check the break even price
see if the break-even-price is >= (0.9*listing-price)
if price is good, create add the row to a new csv, "possibilities.csv"
in "possibilities.csv" add the current profit
set "checked?" = 1
"""



while(True):
    product = input("What product? ")
    val = get_breakeven(product)
    print(val)