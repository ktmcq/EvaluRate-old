load data infile 'csv/course.csv'
insert into table course
fields terminated by "," optionally enclosed by '"'
(semester,coursenum,coursename,credits,seats,crn,dateandtime,location)
