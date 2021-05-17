drop table userinfo cascade constraints;
create table userinfo
	(email varchar(100),
	password varchar(100),
	accounttype varchar(20),
	privacy varchar(10),
	regtime varchar(10),
	names varchar(100),
	gradyear varchar(5),
	constraint pk_user primary key (email));	
