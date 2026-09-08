create table sample_item (
  id bigint not null primary key,
  name varchar(64) not null,
  code varchar(64) not null,
  description varchar(256),
  enabled boolean not null,
  create_by varchar(64) not null,
  create_time datetime(3) not null,
  modify_by varchar(64) not null,
  modify_time datetime(3) not null,
  version bigint not null default 0,
  deleted int not null default 0,
  constraint uk_sample_item_code unique(code)
);

create index idx_sample_item_deleted_time on sample_item(deleted, modify_time);
