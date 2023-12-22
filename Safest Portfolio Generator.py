#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from IPython.display import display, Math, Latex

import pandas as pd
import numpy as np
import numpy_financial as npf
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime
import random


# In[ ]:


#total number of stocks you want in the portfolio
#in terms of diversification, the more the better
#ending portfolio may or may not reach this number of stocks, depends on the 
numberofstocks = 22
startinginvestment = 750000
testinvestmentstart = '2023-01-01'
testinvestmentend = '2023-10-01'
startinginvestmentday = '2023-10-25'
#to be able to get the history data, we need the next day 
dayafterinvestment = '2023-10-26'
#optional, just to test the overall percent change
#to use, uncomment this and the ending code 
#endinginvestmentday = '2023-12-03'


# In[ ]:


def get_average__monthly_volume(stock_volume):
    # # get the ticker
    # ticker = yf.Ticker(ticker_symbol)
    # # get the stock data
    # stock_data = ticker.history(start='2023-01-01', end='2023-10-31')

    # # Resample data to monthly frequency and calculate average volume
    # stock_volume = stock_data['Volume']
    # Resample data to monthly frequency and calculate the number of trading days per month
    trading_days_per_month = stock_volume.resample('M').count()

    # Filter out months with less than 18 trading days
    valid_months = trading_days_per_month[trading_days_per_month >= 18]

    # Filter the stock data for the valid months
    stock_volume = stock_volume[stock_volume.index.month.isin(valid_months.index.month)]

    # return the result
    return stock_volume.sum()/len(valid_months)


# In[ ]:


def validtickers(df):
    ticker_lst = []
    #in case there's no title and the column title is a ticker
    try:
        ticker = df.columns[0]
        stock = yf.Ticker(ticker)
        #get historical data from it
        history = stock.history(start=testinvestmentstart, end=testinvestmentend)
        #if it is a valid ticker, this would run and if it hits the requirements, it appends the ticker to the tickerlist
        if ((stock.fast_info['currency'] == "CAD" or stock.fast_info['currency'] == "USD") and (get_average__monthly_volume(history['Volume']) > 150000)): # added my function here
            ticker_lst.append(df.columns[0])
            x = 0
        else:
            #otherwise, it's not a ticker that hits the requirements,
            print('not a valid stock')
            x = 0
    except:
      #if the code outputs an error, the ticker isn't valid, so outputs not a ticker
        print('not a ticker')
        x = 0
    while x < len(df):
      #for the rest of the column, exactly the same process as above, try getting an output from the ticker, and if it doesn't work, go next
        try:
            ticker = df.iloc[x,0]
            stock = yf.Ticker(ticker)
            history = stock.history(start=testinvestmentstart, end=testinvestmentend)
            if ((stock.fast_info['currency'] == 'CAD' or stock.fast_info['currency'] == 'USD') and (get_average__monthly_volume(history['Volume']) > 150000) and (df.iloc[x,0] not in ticker_lst)):
                ticker_lst.append(df.iloc[x,0])
                x += 1
            else:
                print('not a valid stock or already exists')
                x += 1
        except:
            print('not a ticker')
            x += 1

    return ticker_lst

tickerlist = validtickers(pd.read_csv('Tickers.csv'))
#print(tickerlist)


# In[ ]:


stocklist = pd.DataFrame(columns=['Ticker', 'Currency', 'CompanyName', 'Industry'])
cad = 0
usd = 0
repeats = []

#add the ticker, currency, company name, and industry to a dataframe
#if theres duplicates of the same stock from different "currencies", so different stock markets, remove them, then add the proper ones later
for i in tickerlist:
    temp = yf.Ticker(i)
    #check company name for same company but different stock markets
    if temp.info['longName'] in stocklist['CompanyName'].values:
        tempthing = stocklist.loc[stocklist['CompanyName'] == temp.info['longName'], 'Ticker'].values[0]
        repeats.append(i)
        repeats.append(tempthing)
        stocklist = stocklist.drop(stocklist[stocklist['CompanyName'] == temp.info['longName']].index)
    #else, add the ticker, currency, company name and industry
    else:
        tempdf = pd.DataFrame(columns=['Ticker', 'Currency', 'CompanyName', 'Industry'])
        tempdf['Ticker'] = [i]
        tempdf['Currency'] = [temp.info['currency']]
        if temp.info['currency'] == 'CAD':
            cad += 1
        else: 
            usd += 1
        tempdf['CompanyName'] = [temp.info['longName']]
        tempdf['Industry'] = [temp.info['sector']]
        stocklist = pd.concat([stocklist, tempdf], ignore_index=True)

#if theres stocks from both sides, add the stocks in the currency that there is currently the least of the stocks in, if both are equal, add in USD because USD is stronger than CAD (traditionally)
if cad < usd:
    for j in repeats:
        temp1 = yf.Ticker(j)
        if temp1.info['currency'] == 'CAD':
            tempdf1 = pd.DataFrame(columns=['Ticker', 'Currency', 'CompanyName', 'Industry'])
            tempdf1['Ticker'] = [j]
            tempdf1['Currency'] = [temp1.info['currency']]
            tempdf1['CompanyName'] = [temp1.info['longName']]
            tempdf1['Industry'] = [temp1.info['sector']]
            stocklist = pd.concat([stocklist, tempdf1], ignore_index=True)
else: 
     for j in repeats:
        temp1 = yf.Ticker(j)
        if temp1.info['currency'] == 'USD':
            tempdf1 = pd.DataFrame(columns=['Ticker', 'Currency', 'CompanyName', 'Industry'])
            tempdf1['Ticker'] = [j]
            tempdf1['Currency'] = [temp1.info['currency']]
            tempdf1['CompanyName'] = [temp1.info['longName']]
            tempdf1['Industry'] = [temp1.info['sector']]
            stocklist = pd.concat([stocklist, tempdf1], ignore_index=True)   
        
#print(stocklist)


# In[ ]:


#create a list for each sector to store the stock tickers in 
Health = []
Tech = []
BasMat = []
FinServ = []
ConsCyc = []
CommServ = []
ConsDef = []
Energy = [] 
Util = []
RealEst = []
Indus = [] 

#seperate stocks by the 11 industries
j = 0
while j < len(stocklist):
    if stocklist.iloc[j, 3] == 'Healthcare':
        Health.append(stocklist.iloc[j, 0])
    elif stocklist.iloc[j, 3] == 'Technology':
        Tech.append(stocklist.iloc[j, 0])
    elif stocklist.iloc[j, 3] == 'Basic Materials':
        BasMat.append(stocklist.iloc[j, 0])
    elif stocklist.iloc[j, 3] == 'Financial Services':
        FinServ.append(stocklist.iloc[j, 0])
    elif stocklist.iloc[j, 3] == 'Consumer Cyclical':
        ConsCyc.append(stocklist.iloc[j, 0])
    elif stocklist.iloc[j, 3] == 'Communication Services':
        CommServ.append(stocklist.iloc[j, 0])
    elif stocklist.iloc[j, 3] == 'Consumer Defensive':
        ConsDef.append(stocklist.iloc[j, 0])
    elif stocklist.iloc[j, 3] == 'Energy':
        Energy.append(stocklist.iloc[j, 0])
    elif stocklist.iloc[j, 3] == 'Utilities':
        Util.append(stocklist.iloc[j, 0])
    elif stocklist.iloc[j, 3] == 'Real Estate':
        RealEst.append(stocklist.iloc[j, 0])
    else:
        Indus.append(stocklist.iloc[j, 0])
    j += 1

industrylist = [Health, Tech, BasMat, FinServ, ConsCyc, CommServ, ConsDef, Energy, Util, RealEst, Indus]
industrynamelist = ['Health', 'Tech', 'BasMat', 'FinServ', 'ConsCyc', 'CommServ', 'ConsDef', 'Energy', 'Util', 'RealEst', 'Indus']

'''
print(Health)
print(Tech)
print(BasMat)
print(FinServ)
print(ConsCyc)
print(CommServ)
print(ConsDef)
print(Energy)
print(Util)
print(RealEst)
print(Indus)
'''


# In[ ]:


flatstocklist = []
#flatten out the stocklist
for i in industrylist:
    flatstocklist.extend(i)
#print(flatstocklist)


# In[ ]:


#evens out the number of stocks per sector, only while the number of stocks is higher than wanted
#while the number of stocks is higher than the wanted number, takes the sector with the most stocks and removes the one 
#with the smallest close price
#small close price means small company, which is relatively less safe 
while len(flatstocklist) > numberofstocks:
    lenlist = [len(i) for i in industrylist]
    maxindex = lenlist.index(max(lenlist))
    moststocks = industrylist[maxindex]
    k = 0
    l = ''
    for j in moststocks:
        ticker = yf.Ticker(j)
        m = ticker.history(start=testinvestmentstart, end=testinvestmentend).Close
        m = m.iloc[0,0]
        if m > k:
            k = m
            l = j
    flatstocklist = [item for item in flatstocklist if item != l]
    industrylist[maxindex] = [item for item in industrylist[maxindex] if item != l]
#print(flatstocklist)


# In[ ]:


#to get the final weighting, we take the standard deviation of the percent change and add the beta to it
#since we want low percent change and low beta, we divide one by the total, so the lower the number, the higher the weighting
n = 0
weightinglist = []
for o in flatstocklist:
    ticker = yf.Ticker(o)
    #for new stocks, the beta might not exist, so we have to check for that 
    if 'beta' in ticker.info:
        p = 1 / (abs(ticker.info['beta']) + abs(ticker.history(start=testinvestmentstart, end=testinvestmentend).Close.pct_change().std()))
        weightinglist.append(p)
        n += p
    else:
        p = 1 / (1 + abs(ticker.history(start=testinvestmentstart, end=testinvestmentend).Close.pct_change().std()))
        weightinglist.append(p)
        n += p
for q in range(len(weightinglist)):
    weightinglist[q] = weightinglist[q]/n
#print(weightinglist)


# In[ ]:


#output a csv file with the dataframe of Ticker and Number of shares bought 
Stock_Final = pd.DataFrame(columns=['Ticker','Shares'])
for r in range(len(weightinglist)):
    ticker = yf.Ticker(flatstocklist[r])
    morningprice = ticker.history(start=startinginvestmentday,end=dayafterinvestment).Close.iloc[0]
    s = (weightinglist[r]*startinginvestment)/morningprice
    Stock_Final.loc[len(Stock_Final)] = [flatstocklist[r], s]
Stock_Final.to_csv('Stocks.csv')


# In[ ]:


'''
#test safety
test = pd.DataFrame()
for t in range(len(Stock_Final)):
    ticker = yf.Ticker(Stock_Final.iloc[t,0])
    test[Stock_Final.iloc[t,0]] = (ticker.history(start=startinginvestmentday,end=endinginvestmentday).Close)*Stock_Final.iloc[t,1]
test['Sum'] = test.sum(axis=1)
overallchange = (test.iloc[len(test)-1,len(test.columns)-1]-test.iloc[0,len(test.columns)-1])/test.iloc[0,len(test.columns)-1]
overallchange *= 100
print(f'{overallchange.round(2)}%') 
'''

