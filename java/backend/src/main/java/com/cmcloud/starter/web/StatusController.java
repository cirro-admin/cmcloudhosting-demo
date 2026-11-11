package com.cmcloud.starter.web;

import com.cmcloud.starter.info.DatabaseInfoService;
import com.cmcloud.starter.info.SystemInfoService;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.LinkedHashMap;
import java.util.Map;

/**
 * One call returning the state of all three tiers, so the page can draw the
 * whole path in a single request rather than three that can disagree.
 */
@RestController
@RequestMapping("/api")
public class StatusController {

    private final SystemInfoService system;
    private final DatabaseInfoService database;

    public StatusController(SystemInfoService system, DatabaseInfoService database) {
        this.system = system;
        this.database = database;
    }

    @GetMapping("/status")
    public Map<String, Object> status(HttpServletRequest request) {
        Map<String, Object> out = new LinkedHashMap<>();
        out.put("web", web(request));
        out.put("application", system.describe());
        out.put("database", database.describe());
        return out;
    }

    /**
     * What the web tier in front of us added to the request.
     *
     * <p>When these headers are present the request arrived through nginx; when
     * they are absent the browser is talking to Spring Boot directly, which is
     * what happens during local development.
     */
    private static Map<String, Object> web(HttpServletRequest request) {
        // ⚠️ Do NOT detect the proxy by reading X-Forwarded-For. `application.yml`
        // sets forward-headers-strategy: native, so Tomcat's RemoteIpValve has
        // already consumed X-Forwarded-For and X-Forwarded-Proto by the time a
        // controller runs — it APPLIES them to getRemoteAddr()/getScheme() and
        // then removes them. Reading the headers therefore reported
        // "Spring Boot (direct)" while the app was sitting behind nginx, which is
        // the opposite of the truth and the first thing this page claims.
        //
        // What the valve leaves is the socket the request actually arrived on.
        // The app binds a high loopback port (the platform hands it one, and the
        // VM unit uses 11001), so anything other than 80/443 means something is
        // in front of us. And getRemoteAddr()/getScheme() are now the
        // proxy-corrected values, which is exactly what we want to show.
        int localPort = request.getLocalPort();
        boolean behindProxy = localPort != 80 && localPort != 443;
        String forwardedFor = request.getHeader("X-Forwarded-For");

        Map<String, Object> out = new LinkedHashMap<>();
        out.put("behindReverseProxy", behindProxy);
        out.put("clientAddress", request.getRemoteAddr());
        out.put("scheme", request.getScheme());
        out.put("host", request.getHeader("Host"));
        out.put("appBoundTo", "127.0.0.1:" + localPort);
        // Present only where no valve consumed it; shown when it is, so the
        // header chain is visible rather than inferred.
        out.put("forwardedFor", forwardedFor);
        out.put("servedBy", behindProxy ? "nginx → Spring Boot" : "Spring Boot (direct)");
        return out;
    }
}
