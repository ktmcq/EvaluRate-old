drop table ratescourse cascade constraints;
create table ratescourse
	(email varchar(100),
	coursename varchar(30),
	usefulness number(8),
	workload number(8),
	difficulty number(8),
	enjoyment number(8),
	comments varchar(1000),
	takeagain varchar(2),
	overall number(8),
	constraint fk_ratescourse_email foreign key (email) references userinfo (email),
	constraint pk_ratescourse_name primary key (coursename,email));
