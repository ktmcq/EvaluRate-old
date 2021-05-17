load data infile 'csv/ratesprofessor.csv'
insert into table ratesprofessor
fields terminated by "," optionally enclosed by '"'
(email,profid,teachingstyle,approachability,comments,takeagain,overall)
