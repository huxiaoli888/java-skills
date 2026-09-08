create table sample_item (
    id bigint not null primary key,
    name varchar(128) not null,
    remark varchar(512) null,
    create_by varchar(128) not null,
    create_time timestamp not null,
    modify_by varchar(128) not null,
    modify_time timestamp not null,
    version bigint not null,
    deleted int not null,
    constraint uk_sample_item_name_deleted unique (name, deleted)
);

create index idx_sample_item_create_time on sample_item (create_time);
