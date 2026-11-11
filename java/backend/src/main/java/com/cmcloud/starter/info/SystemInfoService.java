package com.cmcloud.starter.info;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.lang.management.ManagementFactory;
import java.net.InetAddress;
import java.net.UnknownHostException;
import java.time.Duration;
import java.util.LinkedHashMap;
import java.util.Map;

/**
 * Facts about the JVM and the machine it is running on.
 *
 * <p>This is the "your application tier" panel: which JDK is actually executing,
 * how much memory the process is allowed and using, and how long it has been up.
 * Uptime resetting to zero after a redeploy while the data survives is the
 * clearest way to show that state lives in the database, not in the app.
 */
@Service
public class SystemInfoService {

    @Value("${server.port:11001}")
    private int port;

    @Value("${spring.application.name:starter}")
    private String appName;

    public Map<String, Object> describe() {
        Runtime runtime = Runtime.getRuntime();
        long uptimeMs = ManagementFactory.getRuntimeMXBean().getUptime();

        // maxMemory reflects -XX:MaxRAMPercentage against the systemd MemoryMax
        // cgroup limit, so this is the number the service is really held to.
        long maxHeapMb = runtime.maxMemory() / (1024 * 1024);
        long usedHeapMb = (runtime.totalMemory() - runtime.freeMemory()) / (1024 * 1024);

        Map<String, Object> out = new LinkedHashMap<>();
        out.put("application", appName);
        out.put("hostname", hostname());
        out.put("javaVersion", System.getProperty("java.version"));
        out.put("javaVendor", System.getProperty("java.vm.vendor"));
        out.put("jvmName", System.getProperty("java.vm.name"));
        out.put("os", System.getProperty("os.name") + " " + System.getProperty("os.arch"));
        out.put("availableProcessors", runtime.availableProcessors());
        out.put("heapUsedMb", usedHeapMb);
        out.put("heapMaxMb", maxHeapMb);
        out.put("uptime", humanDuration(uptimeMs));
        out.put("uptimeMs", uptimeMs);
        out.put("listeningOn", "127.0.0.1:" + port);
        return out;
    }

    private static String hostname() {
        try {
            return InetAddress.getLocalHost().getHostName();
        } catch (UnknownHostException e) {
            return "unknown";
        }
    }

    private static String humanDuration(long millis) {
        Duration d = Duration.ofMillis(millis);
        long days = d.toDays();
        long hours = d.toHoursPart();
        long minutes = d.toMinutesPart();
        long seconds = d.toSecondsPart();
        if (days > 0) {
            return "%dd %dh %dm".formatted(days, hours, minutes);
        }
        if (hours > 0) {
            return "%dh %dm".formatted(hours, minutes);
        }
        if (minutes > 0) {
            return "%dm %ds".formatted(minutes, seconds);
        }
        return seconds + "s";
    }
}
