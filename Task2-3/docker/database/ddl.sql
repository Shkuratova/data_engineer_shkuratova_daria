create table users(
    guid uuid primary key,
    username varchar(50) unique not null,
    email varchar(255) unique not null,
    date_joined timestamp not null
);
alter table users add constraint valid_email
    check ( email like '%_@__%.__%');

create table topics(
    guid uuid primary key,
    user_guid uuid references users(guid) not null,
    title varchar(500) not null,
    content text null,
    date_created timestamp not null
);

create table messages(
    guid uuid primary key,
    user_guid uuid references users(guid) null,
    topic_guid uuid references topics(guid) not null,
    date_created timestamp not null,
    body text not null
);

create table log_event(
    guid uuid primary key,
    event_name varchar(255) not null
);

create table logs(
    guid uuid,
    log_date timestamp not null,
    user_guid uuid,
    topic_guid uuid,
    message_guid uuid,
    response_status_code int not null ,
    log_message varchar(1024),
    event_guid uuid

) partition by range (log_date);

create table logs_y2025m02 partition of logs
for values from ('2025-02-01') to ('2025-03-01');

alter table logs_y2025m02 add constraint logs_y2025m02_pk primary key (guid);
alter table logs_y2025m02 add constraint user_logs_fk
    foreign key (user_guid) references users (guid) on delete set null;
alter table logs_y2025m02 add constraint topic_logs_fk
    foreign key (topic_guid) references topics (guid) on delete set null;
alter table logs_y2025m02 add constraint message_logs_fk
    foreign key (message_guid) references messages (guid) on delete set null;
alter table logs_y2025m02 add constraint event_logs_fk
    foreign key (event_guid) references log_event (guid);
alter table logs_y2025m02 add constraint valid_status_code check ( response_status_code in (0,1) );

create table logs_y2025m03 partition of logs
for values from ('2025-03-01') to ('2025-04-01');

alter table logs_y2025m03 add constraint logs_y2025m03_pk primary key (guid);
alter table logs_y2025m03 add constraint user_logs_fk
    foreign key (user_guid) references users (guid) on delete set null;
alter table logs_y2025m03 add constraint topic_logs_fk
    foreign key (topic_guid) references topics (guid) on delete set null;
alter table logs_y2025m03 add constraint message_logs_fk
    foreign key (message_guid) references messages (guid) on delete set null;
alter table logs_y2025m03 add constraint event_logs_fk
    foreign key (event_guid) references log_event (guid);
alter table logs_y2025m03 add constraint valid_status_code check ( response_status_code in (0,1) );









