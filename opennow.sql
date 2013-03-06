--List those libraries open right now.
select * from hours where datetime("now", "localtime") between datetime(open) and datetime(close);

--For every library that has a record for today, list whether it's open or closed right now
select *, case when datetime("now", "localtime") between datetime(open) and datetime(close) then 'OPEN' else 'CLOSED' end as open from hours where date(date) = date();
