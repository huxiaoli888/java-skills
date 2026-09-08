package com.chaken.ai.test.production.idempotency;

import static org.assertj.core.api.Assertions.assertThat;

import com.chaken.ai.test.common.log.model.OperationAuditRecord;
import com.chaken.ai.test.common.log.model.OperationType;
import com.chaken.ai.test.production.audit.JdbcOperationAuditService;
import com.chaken.ai.test.production.audit.JdbcTemplateOperationAuditRecordRepository;
import com.chaken.ai.test.security.idempotency.IdempotencyDecision;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.datasource.DriverManagerDataSource;

class JdbcIdempotencyAndAuditIntegrationTest {
    private JdbcTemplate jdbcTemplate;

    @BeforeEach
    void setUpDatabase() {
        DriverManagerDataSource dataSource = new DriverManagerDataSource(
                "jdbc:h2:mem:api_infra;MODE=MySQL;DATABASE_TO_LOWER=TRUE;DB_CLOSE_DELAY=-1",
                "sa",
                "");
        dataSource.setDriverClassName("org.h2.Driver");
        jdbcTemplate = new JdbcTemplate(dataSource);
        jdbcTemplate.execute("drop table if exists api_idempotency_record");
        jdbcTemplate.execute("drop table if exists operation_audit_log");
        jdbcTemplate.execute("""
                create table api_idempotency_record (
                    id bigint auto_increment primary key,
                    owner_id varchar(128) not null,
                    business_type varchar(64) not null,
                    business_key varchar(128) not null,
                    request_fingerprint varchar(128) not null,
                    status varchar(32) not null,
                    response_snapshot text null,
                    created_time timestamp not null,
                    expire_time timestamp not null,
                    constraint uk_api_idempotency unique (owner_id, business_type, business_key)
                )
                """);
        jdbcTemplate.execute("""
                create table operation_audit_log (
                    id bigint auto_increment primary key,
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
                )
                """);
    }

    @Test
    void jdbcIdempotencyDetectsSameAndDifferentRequestsWithUniqueConstraint() {
        JdbcTemplateIdempotencyRecordRepository repository =
                new JdbcTemplateIdempotencyRecordRepository(jdbcTemplate);
        JdbcIdempotencyService service = new JdbcIdempotencyService(repository, Clock.systemUTC(), Duration.ofHours(1));

        assertThat(service.check("owner", "fingerprint-a", "ORDER", "ORDER-1"))
                .isEqualTo(IdempotencyDecision.FIRST_REQUEST);
        assertThat(service.check("owner", "fingerprint-a", "ORDER", "ORDER-1"))
                .isEqualTo(IdempotencyDecision.REPLAY_SAME_REQUEST);
        assertThat(service.check("owner", "fingerprint-b", "ORDER", "ORDER-1"))
                .isEqualTo(IdempotencyDecision.CONFLICT_DIFFERENT_REQUEST);
        service.saveResult("owner", "ORDER", "ORDER-1", "{\"code\":\"000000\"}");

        String snapshot = jdbcTemplate.queryForObject(
                "select response_snapshot from api_idempotency_record where owner_id = ? and business_key = ?",
                String.class,
                "owner",
                "ORDER-1");
        assertThat(snapshot).isEqualTo("{\"code\":\"000000\"}");
    }

    @Test
    void jdbcAuditServiceWritesRecordToDatabase() {
        JdbcTemplateOperationAuditRecordRepository repository =
                new JdbcTemplateOperationAuditRecordRepository(jdbcTemplate);
        JdbcOperationAuditService auditService = new JdbcOperationAuditService(repository);
        OperationAuditRecord record = new OperationAuditRecord();
        record.setReqid("req-1");
        record.setTraceId("trace-1");
        record.setOperator("admin");
        record.setOperationType(OperationType.CREATE);
        record.setAction("create user");
        record.setBusinessId("user-1");
        record.setSuccess(true);
        record.setClientIp("127.0.0.1");
        record.setDurationMs(12L);
        record.setTimestamp(Instant.now());

        auditService.save(record);

        Integer count = jdbcTemplate.queryForObject(
                "select count(*) from operation_audit_log where reqid = ? and operation_name = ?",
                Integer.class,
                "req-1",
                "create user");
        assertThat(count).isEqualTo(1);
    }
}
