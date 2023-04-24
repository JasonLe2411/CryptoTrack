import pandas as pd 
import streamlit as st 
from utils import createDataset,getPriceChange,normalizePrice
import datetime
import time
import plotly.express as px
from plotly import graph_objects as go 
from plotly.subplots import make_subplots


tickers = ["BTC-USD","^GSPC","ETH-USD","^DJI"]
names = ["Bitcoin","S&P 500","Ethereum","Dow Jones"]

tickerDict = {}
for i in range(len(names)):
    tickerDict[names[i]] = tickers[i]


#Start from 2021/1/1 23:59
period1 = int(time.mktime(datetime.datetime(2021,1,1,23,59).timetuple()))
#Ends at this moment
period2 = int(time.mktime(datetime.datetime.now().timetuple()))
#Intervals
interval = "1d"

dataset = createDataset(tickers,period1,period2,interval)
selectedAttributes = ["Open","High","Low","Close","Adj Close","MA20","MA200"]


#Change date column to datetime type:
dataset['Date'] = pd.to_datetime(dataset['Date'], format="%Y-%m-%d")

#Add Moving averages:
dataset["MA20"] = dataset.Close.rolling(20).mean()
dataset["MA200"] = dataset.Close.rolling(200).mean()


st.set_page_config(page_title="Crypto Price Tracker",
                    page_icon = ":dollar_banknote:",
                    layout="wide")


#Sidebar
st.sidebar.header("Please Filter Here: ")
#Start date, default to 10 days before
day10 = datetime.date.today() - datetime.timedelta(days=10)
start = st.sidebar.date_input(label="Select start date:",value = day10,min_value=datetime.date(2021,1,1),max_value=datetime.date.today())
#End date 
end = st.sidebar.date_input(label="Select end date:",min_value=start,max_value=datetime.date.today())

#Graph 1 tickers
tickers1 = st.sidebar.radio(
    "Select your ticker for Graph 1:",
    options = names,
)
ticker1 = tickerDict[tickers1]
#Graph2 tickers
tickers2 = st.sidebar.radio(
    "Select your ticker for Graph 2:",
    index=1,
    options = names,
)
ticker2 = tickerDict[tickers2]

attr = st.sidebar.multiselect(
    "Select your attributes:",
    options= selectedAttributes,
    default= ["High"]
)


#Get all columns for the dataframe
columns = attr + ["Date","Ticker"]



dfGraph1 = dataset.query(
    "Ticker == @ticker1 & @start <= Date <= @end" 
)[columns]

dfGraph2 = dataset.query(
    "Ticker == @ticker2 & @start <= Date <= @end"
)[columns]

#Mainpage
st.title(":bar_chart: Price Tracker Dashboard")
st.markdown("##")


st.subheader("Price change during the period")
data = [ ]

for i in attr: 
    data.append(go.Scatter(x = dfGraph1["Date"], y=dfGraph1[i], name=f"{tickers1} {i}"))
    data.append(go.Scatter(x = dfGraph2["Date"], y=dfGraph2[i], name=f"{tickers2} {i}",yaxis='y2'))



# Add titles and color the font of the titles to match that of the traces
# 'SteelBlue' and 'DarkOrange' are the defaults of the first two colors.

y1 = go.layout.YAxis(title=f"Price of {tickers1}", titlefont=go.layout.yaxis.title.Font(color='LightBlue'))
y2 = go.layout.YAxis(title=f"Price of {tickers2}", titlefont=go.layout.yaxis.title.Font(color='SteelBlue'))

# update second y axis to be position appropriately
y2.update(overlaying='y', side='right')

# Add the pre-defined formatting for both y axes 
layout = go.Layout(yaxis1 = y1, yaxis2 = y2)

fig = go.Figure(data=data, layout=layout)



#Check box to normalize
normal = st.checkbox("Normalize")
normalizePrice(dfGraph1,datetime.datetime(start.year,start.month,start.day),"High","df1norm")
normalizePrice(dfGraph2,datetime.datetime(start.year,start.month,start.day),"High","df2norm")
if normal: 
    data = [
        go.Scatter(x = dfGraph1["Date"], y=dfGraph1["df1norm"], name=tickers1),
        go.Scatter(x = dfGraph2["Date"], y = dfGraph2["df2norm"], name=tickers2)
    ]
    fig = go.Figure(data=data, layout=dict())

st.plotly_chart(fig)

# Calculate price changes 
priceChange1 = getPriceChange(dfGraph1,attr[0])
if priceChange1 >= 0:
    st.markdown("{}: :green[+ {:.1f}%]".format(tickers1,priceChange1))
else:
    st.markdown("{}: :red[- {:.1f}%]".format(tickers1,abs(priceChange1)))

priceChange2 = getPriceChange(dfGraph2,attr[0])
if priceChange2 >= 0:
    st.markdown("{}: :green[+ {:.1f}%]".format(tickers2,priceChange2))
else:
    st.markdown("{}: :red[- {:.1f}%]".format(tickers2,abs(priceChange2)))


st.markdown("---")

st.subheader("Technical Analysis")
concat = pd.concat([dfGraph1.set_index(dfGraph1["Date"])["df1norm"],dfGraph2.set_index(dfGraph2["Date"])["df2norm"]],axis=1,join="inner")
corr = concat["df1norm"].corr(concat["df2norm"])
st.markdown("The correllation between price of {} and {} is: {:.3f}".format(tickers1,tickers2,corr))
