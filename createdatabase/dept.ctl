load data infile 'csv/department.csv'
insert into table department
fields terminated by "," optionally enclosed by '"'
(did,deptname,website)
