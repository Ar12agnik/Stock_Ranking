import warnings
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
def calculate_metrics(stock_name,body="NSE"):
    if body =='NSE':
        stock_name+=".NS"
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", FutureWarning)
        stock = yf.Ticker(stock_name)
        hist = stock.history(period="1y")

        # Fetch the most recent stock price
        stock_price = stock.history(period='1d')['Close'][0]
        currency = stock.info.get('currency', 'Currency not available')

        # Calculate P/E Ratio
        eps = stock.info.get('trailingEps')
        if eps is not None and eps != 0:
            pe_ratio = stock_price / eps
        else:
            pe_ratio = "Data not available"

        # Calculate Dividend Yield
        annual_dividend = stock.info.get('dividendRate')
        if annual_dividend is not None and stock_price != 0:
            dividend_yield = (annual_dividend / stock_price) * 100
        else:
            dividend_yield = "Data not available"

        # Calculate ROE
        roe = stock.info.get('returnOnEquity', 'Data not available')
        if roe !="Data not available":
            roe=roe*100

        # Calculate Debt/Equity Ratio
        book_value=stock.info['bookValue']
        shares_Outstanding =stock.info['sharesOutstanding']
        shareholder_equity = book_value*shares_Outstanding
        total_debt = stock.info.get('totalDebt', 0)
        debt_equity_ratio = total_debt / shareholder_equity
        if roe=="Data not available":
            roe=eps/book_value


        # Fetch 52-week high and low
        week_52_high = stock.info.get('fiftyTwoWeekHigh', 'Data not available')
        week_52_low = stock.info.get('fiftyTwoWeekLow', 'Data not available')
    return [stock_price,eps,pe_ratio,annual_dividend,dividend_yield,roe,debt_equity_ratio,week_52_high,week_52_low]
def get_stocks(stocks:list,df=None):
    for stock in stocks:
        metrics=calculate_metrics(stock)
        if df is None:
            data = {
                'Name':stock,
                'stock_price' : [metrics[0]],
                'eps' : [metrics[1]],
                'pe_ratio' : [metrics[2]],
                'annual_dividend' : [metrics[3]],
                'dividend_yield' : [metrics[4]],
                'roe' : [metrics[5]],
                'debt_equity_ratio' : [metrics[6]],
                'week_52_high' : [metrics[7]],
                'week_52_low' : [metrics[8]],
            }
            df = pd.DataFrame(data)
        else:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", FutureWarning)
                new_metrics=[stock]
                new_metrics.extend(metrics)
                df.loc[-1] = new_metrics
                df.index = df.index+1
                df=df.sort_index()
    return df
import warnings
def fix_data(df):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", FutureWarning)
        df.replace('Data not available',np.nan,inplace=True)
        df.infer_objects(copy=False)
        columns_with_none = df.columns[df.isnull().any()].tolist()
        for i in columns_with_none:
            if i=='annual_dividend' or i=='dividend_yield':
                df[i] = df[i].fillna(0)
            mean = df[i].mean()
            df[i] = df[i].fillna(mean)
        df.to_csv("new.csv")
        return columns_with_none
    

def get_ranking(stocks):
    a=get_stocks(stocks)
    a.to_csv('data.csv')
    fix_data(a)
    max_pe_ratio = a['pe_ratio'].max()
    min_pe_ratio = a['pe_ratio'].min()
    min_dividend_yield = a['dividend_yield'].min()
    max_dividend_yield = a['dividend_yield'].max()
    max_roe = a['roe'].max()
    min_roe = a['roe'].min()
    min_debt_equity_ratio = a['debt_equity_ratio'].min()
    max_debt_equity_ratio = a['debt_equity_ratio'].max()
    final_scores={}
    for stock in stocks:
        stock=stocks.index(stock)
        pe_stk=a['pe_ratio'][stock]
        pe_normal = (max_pe_ratio-float(pe_stk))/(max_pe_ratio-min_pe_ratio)
        dividend_yield_stk=a['dividend_yield'][stock]
        divident_yield_normal = (float(dividend_yield_stk)-min_dividend_yield)/(max_dividend_yield-min_dividend_yield)
        roe_stk = a['roe'][stock]
        roe_normal=(float(roe_stk)-min_roe)/(max_roe-min_roe)
        debt_equity_ratio_stk = a['debt_equity_ratio'][stock]
        debt_equity_ratio_normal = (max_debt_equity_ratio - float(debt_equity_ratio_stk))/(max_debt_equity_ratio-min_debt_equity_ratio)
        stk_price=a['stock_price'][stock]
        high=a['week_52_high'][stock]
        low=a['week_52_low'][stock]
        ptl_normal = (float(stk_price)-low)/(high-low)
        final_score = (.20*pe_normal)+(.20*divident_yield_normal)+(.25*roe_normal)+(.15*(debt_equity_ratio_normal))+(.20*ptl_normal)
        final_scores[stocks[stock]]=final_score*100
    return final_scores
        
        
#print("Lower is Better:") 
no_of_stocks=int(input("enter the number of stocks to compare: "))
names = [input("enter the Stock Symbol: ") for _ in range(no_of_stocks)]  
print("analyzing.......")     
print("calculating.......")     
data = get_ranking(names)
print("Done!!")
time.sleep(0.5)

values = data.values()
keys = data.keys()
df = pd.DataFrame({'score':values,'symbol':keys},index=np.arange(len(data)))
df.sort_values(by=['score'],inplace=True)
print("Stock Rankings based on calculated scores:")
for i in df['symbol']:
    print(i)
#['SBIN','BHARTIARTL','JSWINFRA','IDEA']