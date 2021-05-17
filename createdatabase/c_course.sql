drop table course cascade constraints;
create table course
	(crn varchar(8),
	semester varchar(20),
	seats varchar(5),
	coursenum varchar(30),
	coursename varchar(30),
	location varchar(100),
	dateandtime varchar(150),
	credits varchar(5),
	constraint pk_course primary key (crn,semester));
