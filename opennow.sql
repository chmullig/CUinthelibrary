select * from hours where datetime("now", "localtime") between datetime(open) and datetime(close);
