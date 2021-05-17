load data infile 'csv/choosescourse.csv'
insert into table choosescourse
fields terminated by "," optionally enclosed by '"'
(email,crn,semester,category)
