load data infile 'csv/professor.csv'
insert into table professor
fields terminated by "," optionally enclosed by '"'
(profid,profname)


