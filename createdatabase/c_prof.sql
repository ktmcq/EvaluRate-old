drop table professor cascade constraints;
create table professor
	(profid varchar(10),
	profname varchar(40),
	constraint pk_prof primary key (profid));
