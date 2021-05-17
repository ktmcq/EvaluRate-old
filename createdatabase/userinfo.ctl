load data infile 'csv/userinfo.csv'
insert into table userinfo
fields terminated by "," optionally enclosed by '"'
(email,password,accounttype,privacy,regtime,names,gradyear)
