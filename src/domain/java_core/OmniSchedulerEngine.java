// ===========================================================================
// OMNI SCHEDULER ENGINE (SEMESTER 3 — BATCH 38.2)
// ===========================================================================
// Absorbed From  : Quartz Scheduler + Spring @Scheduled + cron4j
// Logic Inherited: Java / Domain Layer (Cron-Based Task Scheduling)
// ===========================================================================

package omni.domain.scheduler;

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicLong;

public final class OmniSchedulerEngine {

    public enum JobState { PENDING, RUNNING, COMPLETED, FAILED, CANCELLED }

    public static final class JobResult {
        private final boolean success;
        private final String message;
        private final long durationMs;

        public JobResult(boolean success, String message, long durationMs) {
            this.success = success;
            this.message = message;
            this.durationMs = durationMs;
        }

        public boolean isSuccess() { return success; }
        public String getMessage() { return message; }
        public long getDurationMs() { return durationMs; }
    }

    public static final class Job {
        private final String id;
        private final String name;
        private final String cronExpression;
        private final Callable<JobResult> task;
        private JobState state;
        private int executionCount;
        private long lastRunAt;
        private long nextRunAt;
        private JobResult lastResult;
        private final int maxRetries;
        private int retryCount;

        public Job(String name, String cronExpression, Callable<JobResult> task, int maxRetries) {
            this.id = UUID.randomUUID().toString().substring(0, 8);
            this.name = name;
            this.cronExpression = cronExpression;
            this.task = task;
            this.state = JobState.PENDING;
            this.executionCount = 0;
            this.lastRunAt = 0;
            this.nextRunAt = 0;
            this.lastResult = null;
            this.maxRetries = maxRetries;
            this.retryCount = 0;
        }

        public String getId() { return id; }
        public String getName() { return name; }
        public JobState getState() { return state; }
        public int getExecutionCount() { return executionCount; }
        public JobResult getLastResult() { return lastResult; }
    }

    // ---- Cron Expression Parser (minute hour dom month dow) ----

    public static final class CronParser {
        /**
         * Parse a 5-field cron expression and determine if the given
         * calendar time matches.
         * Fields: minute hour day-of-month month day-of-week
         * Supports: * (any), specific values, ranges (1-5), lists (1,3,5)
         */
        public static boolean matches(String cronExpr, Calendar cal) {
            String[] fields = cronExpr.trim().split("\\s+");
            if (fields.length != 5) return false;

            int minute = cal.get(Calendar.MINUTE);
            int hour = cal.get(Calendar.HOUR_OF_DAY);
            int dom = cal.get(Calendar.DAY_OF_MONTH);
            int month = cal.get(Calendar.MONTH) + 1;
            int dow = cal.get(Calendar.DAY_OF_WEEK) - 1; // 0=Sun

            return matchField(fields[0], minute, 0, 59) &&
                   matchField(fields[1], hour, 0, 23) &&
                   matchField(fields[2], dom, 1, 31) &&
                   matchField(fields[3], month, 1, 12) &&
                   matchField(fields[4], dow, 0, 6);
        }

        private static boolean matchField(String field, int value, int min, int max) {
            if ("*".equals(field)) return true;

            // Handle lists: "1,3,5"
            if (field.contains(",")) {
                for (String part : field.split(",")) {
                    if (matchField(part.trim(), value, min, max)) return true;
                }
                return false;
            }

            // Handle ranges: "1-5"
            if (field.contains("-")) {
                String[] range = field.split("-");
                int lo = Integer.parseInt(range[0]);
                int hi = Integer.parseInt(range[1]);
                return value >= lo && value <= hi;
            }

            // Handle step: "*/5"
            if (field.startsWith("*/")) {
                int step = Integer.parseInt(field.substring(2));
                return step > 0 && (value % step == 0);
            }

            // Exact match
            return Integer.parseInt(field) == value;
        }
    }

    // ---- Engine Core ----

    private final Map<String, Job> jobs;
    private final AtomicLong totalExecutions;
    private final AtomicLong totalSuccesses;
    private final AtomicLong totalFailures;

    public OmniSchedulerEngine() {
        this.jobs = new ConcurrentHashMap<>();
        this.totalExecutions = new AtomicLong(0);
        this.totalSuccesses = new AtomicLong(0);
        this.totalFailures = new AtomicLong(0);
    }

    /** Schedule a new job with a cron expression. */
    public Job schedule(String name, String cronExpr, Callable<JobResult> task, int maxRetries) {
        Job job = new Job(name, cronExpr, task, maxRetries);
        jobs.put(job.getId(), job);
        return job;
    }

    /** Execute a job immediately (bypassing cron schedule). */
    public JobResult executeNow(String jobId) {
        Job job = jobs.get(jobId);
        if (job == null) return new JobResult(false, "Job not found: " + jobId, 0);

        job.state = JobState.RUNNING;
        job.lastRunAt = System.currentTimeMillis();
        long start = System.nanoTime();

        try {
            JobResult result = job.task.call();
            long durationMs = (System.nanoTime() - start) / 1_000_000;

            job.executionCount++;
            job.lastResult = new JobResult(result.isSuccess(), result.getMessage(), durationMs);
            totalExecutions.incrementAndGet();

            if (result.isSuccess()) {
                job.state = JobState.COMPLETED;
                job.retryCount = 0;
                totalSuccesses.incrementAndGet();
            } else {
                handleFailure(job);
            }

            return job.lastResult;

        } catch (Exception e) {
            long durationMs = (System.nanoTime() - start) / 1_000_000;
            job.lastResult = new JobResult(false, "Exception: " + e.getMessage(), durationMs);
            job.executionCount++;
            totalExecutions.incrementAndGet();
            handleFailure(job);
            return job.lastResult;
        }
    }

    private void handleFailure(Job job) {
        job.retryCount++;
        totalFailures.incrementAndGet();

        if (job.retryCount >= job.maxRetries) {
            job.state = JobState.FAILED;
        } else {
            job.state = JobState.PENDING; // Will retry
        }
    }

    /** Cancel a scheduled job. */
    public boolean cancel(String jobId) {
        Job job = jobs.get(jobId);
        if (job == null) return false;
        job.state = JobState.CANCELLED;
        return true;
    }

    /** Tick: check all jobs against current time and execute matching ones. */
    public List<JobResult> tick() {
        Calendar now = Calendar.getInstance();
        List<JobResult> results = new ArrayList<>();

        for (Job job : jobs.values()) {
            if (job.state == JobState.PENDING || job.state == JobState.COMPLETED) {
                if (CronParser.matches(job.cronExpression, now)) {
                    results.add(executeNow(job.getId()));
                }
            }
        }

        return results;
    }

    public int getJobCount() { return jobs.size(); }

    // ---- Diagnostics ----

    public Map<String, Object> diagnostics() {
        Map<String, Object> info = new LinkedHashMap<>();
        info.put("engine", "OmniSchedulerEngine");
        info.put("layer", "Java Domain");
        info.put("total_jobs", jobs.size());
        info.put("total_executions", totalExecutions.get());
        info.put("total_successes", totalSuccesses.get());
        info.put("total_failures", totalFailures.get());
        info.put("learned_logic", List.of(
            "quartz-cron-expression-parsing",
            "5-field-cron-minute-hour-dom-month-dow",
            "retry-with-max-attempts",
            "job-state-machine-lifecycle",
            "callable-task-execution",
            "concurrent-hashmap-job-registry",
            "tick-based-scheduler-loop"
        ));
        return info;
    }
}
