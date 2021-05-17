load data infile 'csv/professorisin.csv'
insert into table professorisin
fields terminated by "," optionally enclosed by '"'
(profid,did)
