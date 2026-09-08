create table cms_sys_user (
  id bigint not null primary key,
  username varchar(64) not null,
  display_name varchar(128),
  mobile varchar(32),
  email varchar(128),
  password_salt varchar(128) not null,
  password_hash varchar(256) not null,
  status integer not null,
  super_admin boolean not null,
  create_time timestamp not null,
  modify_time timestamp
);

create unique index uk_cms_sys_user_username on cms_sys_user(username);

insert into cms_sys_user (
  id, username, display_name, mobile, email, password_salt, password_hash, status, super_admin, create_time, modify_time
) values (
  1,
  'admin',
  '系统管理员',
  '',
  '',
  'Y2hha2VuLWFpLXRlc3QtZGV2LWFkbWluLXNhbHQ=',
  '2JaIq1byDQrHEHpgl/GRmyiqgxY5btZc2jPsN2paEJ8=',
  1,
  true,
  '2026-01-01 00:00:00',
  '2026-01-01 00:00:00'
);

create table cms_sys_role (
  id bigint not null primary key,
  role_code varchar(64) not null,
  role_name varchar(128) not null,
  status integer not null,
  remark varchar(256),
  create_time timestamp not null,
  modify_time timestamp
);

create unique index uk_cms_sys_role_code on cms_sys_role(role_code);

insert into cms_sys_role (
  id, role_code, role_name, status, remark, create_time, modify_time
) values (
  1,
  'SUPER_ADMIN',
  '超级管理员',
  1,
  '开发默认角色，生产必须替换',
  '2026-01-01 00:00:00',
  '2026-01-01 00:00:00'
);

create table cms_sys_menu (
  id bigint not null primary key,
  parent_id bigint,
  menu_name varchar(128) not null,
  menu_type varchar(16) not null,
  path varchar(256),
  permission_code varchar(128),
  sort_no integer not null,
  status integer not null,
  create_time timestamp not null,
  modify_time timestamp
);

create unique index uk_cms_sys_menu_permission on cms_sys_menu(permission_code);
create index idx_cms_sys_menu_parent on cms_sys_menu(parent_id);

insert into cms_sys_menu (
  id, parent_id, menu_name, menu_type, path, permission_code, sort_no, status, create_time, modify_time
) values
  (1, null, '系统管理', 'MENU', '/sys', null, 10, 1, '2026-01-01 00:00:00', '2026-01-01 00:00:00'),
  (2, 1, '用户管理', 'BUTTON', '/sys/users', 'sys:user:list', 20, 1, '2026-01-01 00:00:00', '2026-01-01 00:00:00'),
  (3, 1, '角色管理', 'BUTTON', '/sys/roles', 'sys:role:list', 30, 1, '2026-01-01 00:00:00', '2026-01-01 00:00:00'),
  (4, 1, '菜单管理', 'BUTTON', '/sys/menus', 'sys:menu:list', 40, 1, '2026-01-01 00:00:00', '2026-01-01 00:00:00'),
  (5, 1, '字典管理', 'BUTTON', '/sys/dicts', 'sys:dict:list', 50, 1, '2026-01-01 00:00:00', '2026-01-01 00:00:00'),
  (6, 1, '参数管理', 'BUTTON', '/sys/params', 'sys:param:list', 60, 1, '2026-01-01 00:00:00', '2026-01-01 00:00:00'),
  (7, 1, '操作日志', 'BUTTON', '/sys/logs/operations', 'sys:log:operation', 70, 1, '2026-01-01 00:00:00', '2026-01-01 00:00:00'),
  (8, 1, '登录日志', 'BUTTON', '/sys/logs/logins', 'sys:log:login', 80, 1, '2026-01-01 00:00:00', '2026-01-01 00:00:00');

create table cms_sys_user_role (
  user_id bigint not null,
  role_id bigint not null,
  primary key (user_id, role_id)
);

create table cms_sys_role_menu (
  role_id bigint not null,
  menu_id bigint not null,
  primary key (role_id, menu_id)
);

insert into cms_sys_user_role (user_id, role_id) values (1, 1);
insert into cms_sys_role_menu (role_id, menu_id) values
  (1, 1),
  (1, 2),
  (1, 3),
  (1, 4),
  (1, 5),
  (1, 6),
  (1, 7),
  (1, 8);

create table cms_sys_dict (
  id bigint not null primary key,
  dict_code varchar(64) not null,
  dict_name varchar(128) not null,
  status integer not null,
  remark varchar(256),
  create_time timestamp not null,
  modify_time timestamp
);

create unique index uk_cms_sys_dict_code on cms_sys_dict(dict_code);

insert into cms_sys_dict (
  id, dict_code, dict_name, status, remark, create_time, modify_time
) values (
  1,
  'sys_status',
  '系统状态',
  1,
  '开发默认字典',
  '2026-01-01 00:00:00',
  '2026-01-01 00:00:00'
);

create table cms_sys_dict_item (
  id bigint not null primary key,
  dict_code varchar(64) not null,
  item_value varchar(64) not null,
  item_label varchar(128) not null,
  sort_no integer not null,
  status integer not null,
  remark varchar(256),
  create_time timestamp not null,
  modify_time timestamp
);

create unique index uk_cms_sys_dict_item_value on cms_sys_dict_item(dict_code, item_value);
create index idx_cms_sys_dict_item_code on cms_sys_dict_item(dict_code);

insert into cms_sys_dict_item (
  id, dict_code, item_value, item_label, sort_no, status, remark, create_time, modify_time
) values
  (1, 'sys_status', '1', '启用', 10, 1, '开发默认字典项', '2026-01-01 00:00:00', '2026-01-01 00:00:00'),
  (2, 'sys_status', '0', '停用', 20, 1, '开发默认字典项', '2026-01-01 00:00:00', '2026-01-01 00:00:00');

create table cms_sys_param (
  id bigint not null primary key,
  param_key varchar(128) not null,
  param_value varchar(512) not null,
  param_name varchar(128) not null,
  status integer not null,
  remark varchar(256),
  create_time timestamp not null,
  modify_time timestamp
);

create unique index uk_cms_sys_param_key on cms_sys_param(param_key);

insert into cms_sys_param (
  id, param_key, param_value, param_name, status, remark, create_time, modify_time
) values (
  1,
  'system.name',
  '后台管理系统',
  '系统名称',
  1,
  '开发默认参数，不保存密钥类配置',
  '2026-01-01 00:00:00',
  '2026-01-01 00:00:00'
);

create table cms_admin_token (
  id bigint not null primary key,
  admin_id bigint not null,
  username varchar(64) not null,
  token_hash varchar(128) not null,
  udid varchar(128),
  status integer not null,
  expire_time timestamp not null,
  create_time timestamp not null,
  last_active_time timestamp
);

create unique index uk_cms_admin_token_hash on cms_admin_token(token_hash);
create index idx_cms_admin_token_admin on cms_admin_token(admin_id);
create index idx_cms_admin_token_expire on cms_admin_token(expire_time);

create table cms_operation_log (
  id bigint not null primary key,
  operation varchar(128) not null,
  operation_type varchar(32) not null,
  business_id varchar(128),
  detail varchar(512),
  success boolean not null,
  error_message varchar(256),
  trace_id varchar(64),
  reqid varchar(64),
  request_method varchar(16),
  request_uri varchar(256),
  request_time bigint,
  user_agent varchar(512),
  ip varchar(64),
  creator_name varchar(128),
  create_time timestamp not null
);

create index idx_cms_operation_log_time on cms_operation_log(create_time);
create index idx_cms_operation_log_reqid on cms_operation_log(reqid);
create index idx_cms_operation_log_creator on cms_operation_log(creator_name);

create table cms_login_log (
  id bigint not null primary key,
  operation integer not null,
  status integer not null,
  user_agent varchar(512),
  ip varchar(64),
  creator_name varchar(128),
  trace_id varchar(64),
  reqid varchar(64),
  create_time timestamp not null
);

create index idx_cms_login_log_time on cms_login_log(create_time);
create index idx_cms_login_log_reqid on cms_login_log(reqid);
create index idx_cms_login_log_creator on cms_login_log(creator_name);
