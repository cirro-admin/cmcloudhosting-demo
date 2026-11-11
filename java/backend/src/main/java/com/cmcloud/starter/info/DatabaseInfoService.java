package com.cmcloud.starter.info;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.jdbc.core.simple.JdbcClient;
import org.springframework.stereotype.Service;

import java.util.LinkedHashMap;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Facts about the database connection, read from the database itself.
 *
 * <p>This is the "your data tier" panel, and the one worth dwelling on: it shows
 * the endpoint the application was configured to dial, and separately the address
 * of the PostgreSQL backend that actually answered. When those differ, the
 * connection pooler is visible — the app dials the public endpoint, and a
 * loopback backend answers on the far side of pgbouncer.
 */
@Service
public class DatabaseInfoService {

    private static final Logger log = LoggerFactory.getLogger(DatabaseInfoService.class);

    private static final Pattern JDBC_URL = Pattern.compile(
            "^jdbc:postgresql://(?<host>[^:/?]+)(?::(?<port>\\d+))?/(?<db>[^?]*)(?:\\?(?<params>.*))?$");

    private final JdbcClient jdbc;

    @Value("${spring.datasource.url:}")
    private String datasourceUrl;

    public DatabaseInfoService(JdbcClient jdbc) {
        this.jdbc = jdbc;
    }

    public Map<String, Object> describe() {
        Map<String, Object> out = new LinkedHashMap<>();

        // What we were told to dial — parsed from config, never from the database,
        // so it is still reported when the database is unreachable.
        Matcher m = JDBC_URL.matcher(datasourceUrl == null ? "" : datasourceUrl);
        if (m.matches()) {
            String port = m.group("port") == null ? "5432" : m.group("port");
            out.put("configuredEndpoint", m.group("host") + ":" + port);
            out.put("configuredDatabase", m.group("db"));
            out.put("tls", sslModeOf(m.group("params")));
        } else {
            out.put("configuredEndpoint", "unparsed");
            out.put("configuredDatabase", "unknown");
            out.put("tls", "unknown");
        }

        try {
            long started = System.nanoTime();
            jdbc.sql("SELECT 1").query(Integer.class).single();
            out.put("roundTripMs", Math.round((System.nanoTime() - started) / 100_000.0) / 10.0);

            out.put("serverVersion", shortVersion(
                    jdbc.sql("SELECT version()").query(String.class).single()));

            jdbc.sql("""
                    SELECT current_database()            AS db,
                           current_user                  AS usr,
                           coalesce(host(inet_server_addr()), 'local socket') AS backend_host,
                           coalesce(inet_server_port(), 0) AS backend_port
                    """).query((rs, n) -> {
                out.put("connectedDatabase", rs.getString("db"));
                out.put("connectedUser", rs.getString("usr"));
                out.put("backendAddress", rs.getString("backend_host") + ":" + rs.getInt("backend_port"));
                return null;
            }).list();

            out.put("rowCount", jdbc.sql("SELECT count(*) FROM entries").query(Long.class).single());
            out.put("reachable", true);
        } catch (Exception ex) {
            // A broken database must not blank the page — showing which tier failed
            // and why is more useful than a 500.
            log.warn("database info unavailable: {}", ex.getMessage());
            out.put("reachable", false);
            out.put("error", ex.getClass().getSimpleName() + ": " + ex.getMessage());
        }

        return out;
    }

    private static String sslModeOf(String params) {
        if (params == null || params.isBlank()) {
            return "not requested";
        }
        for (String pair : params.split("&")) {
            String[] kv = pair.split("=", 2);
            if (kv.length == 2 && kv[0].equalsIgnoreCase("sslmode")) {
                return kv[1];
            }
        }
        return "not requested";
    }

    /**
     * "PostgreSQL 17.11 (Ubuntu 17.11-1) on x86_64-pc-linux-gnu, compiled by…"
     * → "PostgreSQL 17.11".
     */
    private static String shortVersion(String full) {
        if (full == null) {
            return "unknown";
        }
        Matcher v = Pattern.compile("^(PostgreSQL\\s+[\\d.]+)").matcher(full.trim());
        return v.find() ? v.group(1) : full.trim();
    }
}
