drop table department cascade constraints;
create table department
	(did varchar(10),
	deptname varchar(50),
	website varchar(50),
	constraint pk_dept primary key (did));
