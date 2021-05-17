drop table teaches cascade constraints;
create table teaches
	(profid varchar(10),
	crn varchar(8),
	semester varchar(20),
	constraint fk_teaches_pid foreign key (profid) references professor (profid),
	constraint fk_teaches_crn_sem foreign key (crn,semester) references course (crn,semester));
