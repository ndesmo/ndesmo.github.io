---
layout: post
title: 'Moving Medians and Quartiles in Oracle'
modified:
categories: blog
excerpt:
tags: [sql, oracle, statistics] 
image:
  feature: stocks-banner.png
  thumb: stocks.jpeg
  credit: energepic.com
  credit-link: https://www.pexels.com/u/energepic-com-27411/
date: 2017-04-28
share: true
---

I discovered a neat trick today using the `MODEL` clause in Oracle.

My problem was that I had a collection of time-based data, and wanted to compute a running median. Not only that, but the data was not a nice evenly spaced time series, and I basically wanted to compute the "end of day" running median.

This seemed impossible to perform in one query until I realised it was actually quite simple.

I will try to summarise this with an example below

```sql
-- Input some data
with l_data as (

    select to_date('20170101', 'yyyymmdd') as ref_date, 1 as id, 123 as value from dual union all
    select to_date('20170101', 'yyyymmdd') as ref_date, 2 as id, 125 as value from dual union all
    select to_date('20170101', 'yyyymmdd') as ref_date, 3 as id, 150 as value from dual union all
    select to_date('20170101', 'yyyymmdd') as ref_date, 4 as id, 104 as value from dual union all
    select to_date('20170102', 'yyyymmdd') as ref_date, 5 as id, 121 as value from dual union all
    select to_date('20170102', 'yyyymmdd') as ref_date, 6 as id, 122 as value from dual union all
    select to_date('20170102', 'yyyymmdd') as ref_date, 7 as id, 140 as value from dual union all
    select to_date('20170102', 'yyyymmdd') as ref_date, 8 as id, 130 as value from dual union all
    select to_date('20170102', 'yyyymmdd') as ref_date, 9 as id, 135 as value from dual union all
    select to_date('20170103', 'yyyymmdd') as ref_date, 10 as id, 145 as value from dual union all
    select to_date('20170103', 'yyyymmdd') as ref_date, 11 as id, 143 as value from dual union all
    select to_date('20170103', 'yyyymmdd') as ref_date, 12 as id, 140 as value from dual union all
    select to_date('20170105', 'yyyymmdd') as ref_date, 13 as id, 160 as value from dual union all
    select to_date('20170106', 'yyyymmdd') as ref_date, 14 as id, 133 as value from dual union all
    select to_date('20170107', 'yyyymmdd') as ref_date, 15 as id, 158 as value from dual union all
    select to_date('20170107', 'yyyymmdd') as ref_date, 16 as id, 145 as value from dual union all
    select to_date('20170107', 'yyyymmdd') as ref_date, 17 as id, 135 as value from dual union all
    select to_date('20170107', 'yyyymmdd') as ref_date, 18 as id, 142 as value from dual union all
    select to_date('20170107', 'yyyymmdd') as ref_date, 19 as id, 139 as value from dual
    
-- Get the latest ID per day, as we are computing the "end of day" totals
), l_latest as (

    select max(id) as id
      from l_data
     group by ref_date

-- Compute the moving metrics with a lookback window of 3 observations
), l_mov as (

    select id
         , mov_lqtile
         , mov_median
         , mov_uqtile
      from l_data
     model
       dimension by ( id )
       measures ( value
                , 0 mov_lqtile
                , 0 mov_median
                , 0 mov_uqtile )
       rules
       -- only compute for the last observations each day, saves time
         ( mov_lqtile[ for id in ( select id from l_latest ) ] = percentile_disc(0.25) within group (order by value)[id between cv()-3 and cv()]
         , mov_median[ for id in ( select id from l_latest ) ] = median(value)[id between cv()-3 and cv()]
         , mov_uqtile[ for id in ( select id from l_latest ) ] = percentile_disc(0.75) within group (order by value)[id between cv()-3 and cv()] )
    
-- Work out the date range
), l_date_range as (

    select min(ref_date) as min_date
         , max(ref_date) as max_date
      from l_data
     
-- Use the date range to get a full list of dates    
), l_dates as (

    select min_date + level - 1 as ref_date
      from l_date_range
   connect by min_date + level - 1 <= max_date
   
)

-- Display the data with missing dates filled in
-- Display moving median alongside the daily median

    select d.ref_date
         , median(dt.value) as median
         , max(m.mov_lqtile) keep (dense_rank first order by m.id desc) as mov_lqtile
         , max(m.mov_median) keep (dense_rank first order by m.id desc) as mov_median
         , max(m.mov_uqtile) keep (dense_rank first order by m.id desc) as mov_uqtile
         , count(dt.ref_date) as count
      from l_dates d
      left join l_data dt
        on d.ref_date = dt.ref_date
      left join l_mov m
        on dt.id = m.id
     group by d.ref_date
```

| REF_DATE   | MEDIAN | MOV_LQTILE | MOV_MEDIAN | MOV_UQTILE | COUNT |
|:-----------|-------:|-----------:|-----------:|-----------:|------:|
| 01/01/2017 | 124    | 104        | 124        | 125        | 4     |
| 02/01/2017 | 130    | 122        | 132.5      | 135        | 5     |
| 03/01/2017 | 143    | 135        | 141.5      | 143        | 3     |
| 04/01/2017 |        |            |            |            | 0     |
| 05/01/2017 | 160    | 140        | 144        | 145        | 1     |
| 06/01/2017 | 133    | 133        | 141.5      | 143        | 1     |
| 07/01/2017 | 142    | 135        | 140.5      | 142        | 5     |


