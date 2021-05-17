drop table professorisin cascade constraints;
create table professorisin
	(profid varchar(10),
	did varchar(10),
	constraint pk_profisin_pid foreign key (profid) references professor (profid),
	constraint pk_profisin_did foreign key (did) references department (did));
