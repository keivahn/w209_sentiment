import pandas as pd
import psycopg2

##connect to db
conn = psycopg2.connect(database="", user="", password="", 
                        host="", port="")

## Query to get data where relevancy score is higher than 0.6
cur = conn.cursor()
cur.execute("select person, url, website, title, substr(pubdate,1,8) as pubdate, sentiment, trump, hillary from data where trump > 0.6 or hillary > 0.6;")
data = cur.fetchall()
conn.commit()

##List of sources to be used
top_30_list = ['wsj.com', 'ap.org', 'bloomberg.com', 'breitbart.com', 'cadillacnews.com', 'cbsnews.com', 'chicagotribune.com', 'cnn.com', 'democraticunderground.com', 
               'foxnews.com', 'freerepublic.com', 'gazette.com', 'huffingtonpost.com', 'msn.com', 'msnbc.com', 'mysanantonio.com', 
               'newsmax.com', 'patch.com', 'reuters.com', 'srnnews.com', 'tbo.com', 'thehill.com', 'theweek.com', 'time.com', 
               'townhall.com', 'washingtonpost.com', 'washingtontimes.com', 'yahoo.com']

## Put data in pandas dataframe and filter
data = pd.DataFrame(data, columns=['person','url', 'website', 'title','date','score', 'relevancy_trump', 'relevancy_hillary'])
data = data[data['website'].isin(top_30_list)]
data['date']=pd.to_datetime(data['date']) ## convert to date times from string

temp = data[data['person'].isin(['hillary', 'trump'])] ## filter out gary and jill
temp = temp[['person', 'website','score','date','url']] ## leave only needed columns
temp.loc[temp['person'] == 'hillary','person'] = 'Clinton' ## rename to Clinton
temp.loc[temp['person'] == 'trump','person'] = 'Trump' ## rename to Trump
temp.columns=['Candidate','Source','Score','Date','url'] ## rename columns

## Aggregate all news sentiment score by Candidate and Date
avg_sentiment = temp[['Candidate','Date','Score']].groupby(['Candidate','Date']).mean().reset_index()

## Get article counts by date to filter out dates where there are not a lot of articles
temp_count = temp.groupby('Date').count()
temp = temp[temp['Date'].isin(temp_count[temp_count['Candidate'] > 75].index.tolist())] 
avg_sentiment = avg_sentiment[avg_sentiment['Date'].isin(temp_count[temp_count['Candidate'] > 75].index.tolist())]

## Aggregate score and count by Candidate, Source and Date
top25_sentiment = temp.groupby(['Candidate', 'Source', 'Date']).agg(['mean','count']).reset_index()
top25_sentiment.columns =['Candidate', 'Source', 'Date', 'Score', 'Count'] ## Collapse to regular index from multi-index
## Get full index to fill in dates by Candidate and source where mean/count does not exist 
full_index = pd.MultiIndex.from_product([('Clinton', 'Trump'), top_30_list, pd.date_range(top25_sentiment['Date'].min(), top25_sentiment['Date'].max())], names=['Candidate', 'Source', 'Date'])
top25_sentiment = top25_sentiment.set_index(['Candidate','Source','Date']) ## Collapse to regular index from multi-index
top25_sentiment = top25_sentiment.reindex(full_index).reset_index().fillna(0) ## fill NA with 0

## Write data to csv files
top25_sentiment.to_csv('sentiment.csv', index=False)
avg_sentiment.to_csv('avg_sentiment.csv', index=False)