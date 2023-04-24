import datetime
import time
import pandas as pd 
import math


def createDataset(tickers,period1,period2,interval):
    totalDf = pd.DataFrame()
    for i in tickers:
        query_string= f'https://query1.finance.yahoo.com/v7/finance/download/{i}?period1={period1}&period2={period2}&interval={interval}&events=history&includeAdjustedClose=true'
        df = pd.read_csv(query_string)
        df["Ticker"] = i 
        totalDf = pd.concat([totalDf,df],ignore_index=True)
    return totalDf


def getPriceChange(dataset,attr="High"):
    try:
        startPrice = dataset.iloc[0][attr]
        endPrice = 0 
        for index, row in dataset[::-1].iterrows():
            if math.isnan(row[attr]) != True:
                endPrice = row[attr]
                break
        return ((float(endPrice) / float(startPrice)) - 1)*100
    except:
        return "There's no data on the dataset"

def normalizePrice(dataset,date,attr,name):
    price = dataset[dataset["Date"]==date]["High"]
    dataset[name] = dataset["High"]//(price.iloc[0]/100)
    return True

    



if __name__ == "__main__":
    tickers = ["BTC-USD","^GSPC"]
    #Start from 2023/4/1 23:59
    period1 = int(time.mktime(datetime.datetime(2023,4,1,23,59).timetuple()))
    #Ends at this moment
    period2 = int(time.mktime(datetime.datetime.now().timetuple()))
    #Intervals
    interval = "1d"
    print(createDataset(tickers,period1,period2,interval))