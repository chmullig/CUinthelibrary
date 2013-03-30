--List those libraries open right now.
select *, round((julianday(close)-julianday("now", "localtime"))*24, 2) from hours where datetime("now", "localtime") between datetime(open) and datetime(close)
order by round((julianday(close)-julianday("now", "localtime"))*24, 2) ;

--For every library that has a record for today, list whether it's open or closed right now
--select *, case when datetime("now", "localtime") between datetime(open) and datetime(close) then 'OPEN' else 'CLOSED' end as open from hours where date(date) = date();
