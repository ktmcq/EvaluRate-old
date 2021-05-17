load data infile 'csv/teaches.csv'
insert into table teaches
fields terminated by "," optionally enclosed by '"'
(profid,crn,semester)
