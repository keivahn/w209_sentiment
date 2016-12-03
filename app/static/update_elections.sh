psql dfs -c "update alchemy_epochs set tracker = 0, next = null where parsed = false and next is not null"

psql election -c "\copy (select person Candidate, to_timestamp(timestamp)::date::varchar Date, avg(sentiment)::varchar Score from data where person in ('Trump','Clinton') group by 1, 2) to 'avg_sentiment.csv' CSV HEADER"
psql election -c "\copy (select person Candidate, a.website Source, to_timestamp(timestamp)::date::varchar Date, avg(sentiment)::varchar Score, count(*)::varchar Count
from data a join top_websites b on a.website = b.website
where person in ('Trump','Clinton') group by 1, 2, 3) to 'sentiment.csv' CSV HEADER"
