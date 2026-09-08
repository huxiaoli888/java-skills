create table api_idempotency_record (
    id bigint not null primary key,
    owner_id varchar(128) not null,
    business_type varchar(64) not null,
    business_key varchar(128) not null,
    request_fingerprint varchar(128) not null,
    status varchar(32) not null,
    response_snapshot text null,
    created_time timestamp not null,
    expire_time timestamp not null,
    constraint uk_api_idempotency unique (owner_id, business_type, business_key)
);

create table operation_audit_log (
    id bigint not null primary key,
    reqid varchar(64) not null,
    trace_id varchar(64) null,
    operator varchar(128) null,
    operation_type varchar(64) not null,
    operation_name varchar(128) not null,
    business_id varchar(128) null,
    success int not null,
    code varchar(32) null,
    message varchar(512) null,
    client_ip varchar(64) null,
    duration_ms bigint not null,
    create_time timestamp not null
);

create index idx_operation_audit_reqid on operation_audit_log (reqid);
create index idx_operation_audit_create_time on operation_audit_log (create_time);
