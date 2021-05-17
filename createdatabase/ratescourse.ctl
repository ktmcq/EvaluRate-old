load data infile 'csv/ratescourse.csv'
insert into table ratescourse
fields terminated by "," optionally enclosed by '"'
(email,coursename,usefulness,workload,difficulty,enjoyment,comments,takeagain,overall)
