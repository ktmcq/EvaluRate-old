drop table courseisin cascade constraints;
create table courseisin
	(crn varchar(8),
	semester varchar(20),
	did varchar(10),
	constraint fk_courseisin_crn_sem foreign key (crn,semester) references course (crn,semester),
	constraint fk_courseisin_did foreign key (did) references department (did));

exit;
