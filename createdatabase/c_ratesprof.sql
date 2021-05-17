drop table ratesprofessor cascade constraints;
create table ratesprofessor
	(email varchar(100),
	profid varchar(10),
	teachingstyle number(8),
	approachability number(8),
	comments varchar(1000),
	takeagain varchar(2),
	overall number(8),
	constraint pk_ratesprof primary key (email,profid), 
	constraint fk_ratesprof_email foreign key (email) references userinfo (email),
	constraint fk_ratesprof_pid foreign key (profid) references professor (profid)); 
