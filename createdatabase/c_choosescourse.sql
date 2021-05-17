drop table choosescourse cascade constraints;
create table choosescourse
	(email varchar(100),
	crn varchar(8),
	semester varchar(20),
	category varchar(20),
	constraint pk_choosescourse primary key (email,crn,semester),
	constraint fk_choosescourse_email foreign key (email) references userinfo (email),
	constraint fk_choosescourse_crn_sem foreign key (crn,semester) references course (crn,semester));
