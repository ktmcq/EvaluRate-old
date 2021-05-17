load data infile 'csv/courseisin.csv'
insert into table courseisin
fields terminated by "," optionally enclosed by '"'
(crn,semester,did)
