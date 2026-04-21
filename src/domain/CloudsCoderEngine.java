// ===========================================================================
// OMNI DOMAIN LAYER — CLOUDS CODER AGENT ENGINE
// ===========================================================================
// Source Repo   : github.com/FonaTech/Clouds-Coder
// Domain Layer  : Domain (Enterprise business logic, agent orchestration)
// Language      : Java
// Function      : Local-first coding agent platform — CLI/Web plane separation,
//                 session state machine, multi-agent collaboration with 4 roles
//                 (manager/explorer/developer/reviewer), 4-tier context
//                 compression, truncation recovery, timeout governance,
//                 skill loading, and artifact persistence
// ===========================================================================

package OmniDomain.CloudsCoder;

import java.time.Instant;
import java.time.Duration;
import java.util.*;
import java.util.concurrent.*;
import java.util.stream.Collectors;

// ---- Agent Roles ----------------------------------------------------------

enum AgentRole {
    MANAGER("routing/arbitration only; phase-aware delegation"),
    EXPLORER("research, dependency/path analysis, environment probing"),
    DEVELOPER("implementation, file edits, tool execution"),
    REVIEWER("validation, test judgment, approval/block; Debug Mode grants write access");

    final String description;
    AgentRole(String desc) { this.description = desc; }
}

// ---- Session Status -------------------------------------------------------

enum SessionStatus {
    IDLE, THINKING, EXECUTING, AWAITING_INPUT, TRUNCATION_RECOVERY,
    TIMEOUT_RECOVERY, COMPACTING_CONTEXT, COMPLETE, FAILED
}

// ---- Plan Mode ------------------------------------------------------------

enum PlanMode {
    AUTO, ON, OFF
}

// ---- Error Category (6-Category Universal Detection) ----------------------

enum ErrorCategory {
    TEST, LINT, COMPILATION, BUILD, DEPLOY, RUNTIME
}

// ---- Context Compression Tier ---------------------------------------------

enum CompressionTier {
    NORMAL(1.0, "No compression"),
    LIGHT(0.75, "Remove verbose outputs, keep structure"),
    MEDIUM(0.50, "Summarize older messages, keep recent"),
    HEAVY(0.25, "Maximum compression, file buffer offload");

    final double retentionFactor;
    final String description;
    CompressionTier(double factor, String desc) {
        this.retentionFactor = factor;
        this.description = desc;
    }
}

// ---- Skill ----------------------------------------------------------------

class Skill {
    final String name;
    final String category;
    final String content;
    boolean loaded = false;

    Skill(String name, String category, String content) {
        this.name = name;
        this.category = category;
        this.content = content;
    }
}

// ---- Error Entry ----------------------------------------------------------

class ErrorEntry {
    final ErrorCategory category;
    final String message;
    final String file;
    final int line;
    final Instant timestamp;

    ErrorEntry(ErrorCategory category, String message, String file, int line) {
        this.category = category;
        this.message = message;
        this.file = file;
        this.line = line;
        this.timestamp = Instant.now();
    }
}

// ---- Todo Item ------------------------------------------------------------

class TodoItem {
    final String id;
    final String description;
    final AgentRole owner;
    boolean completed;
    Instant createdAt;

    TodoItem(String id, String description, AgentRole owner) {
        this.id = id;
        this.description = description;
        this.owner = owner;
        this.completed = false;
        this.createdAt = Instant.now();
    }
}

// ---- Blackboard (Shared State) --------------------------------------------

class Blackboard {
    String originalGoal = "";
    String status = "idle";
    int managerCycles = 0;
    List<String> planSteps = new ArrayList<>();
    int planCursor = 0;
    String currentPhase = "research";
    List<String> researchNotes = new ArrayList<>();
    List<String> codeArtifacts = new ArrayList<>();
    List<String> executionLogs = new ArrayList<>();
    List<String> reviewFeedback = new ArrayList<>();
    List<ErrorEntry> errors = new ArrayList<>();
    List<TodoItem> todos = new ArrayList<>();

    void addError(ErrorEntry e) {
        errors.add(e);
        executionLogs.add(String.format("[%s] %s: %s (%s:%d)",
                e.timestamp, e.category, e.message, e.file, e.line));
    }

    int errorCount() { return errors.size(); }

    List<ErrorEntry> errorsByCategory(ErrorCategory cat) {
        return errors.stream().filter(e -> e.category == cat).collect(Collectors.toList());
    }
}

// ---- Session State Machine ------------------------------------------------

class SessionState {
    final String sessionId;
    SessionStatus status;
    PlanMode planMode;
    CompressionTier compressionTier;
    AgentRole activeAgent;
    Blackboard blackboard;
    List<Map<String, String>> conversation;
    Map<String, Skill> loadedSkills;
    int contextTokensUsed;
    int contextTokensMax;
    int roundCount;
    int truncationPasses;
    Instant startedAt;
    Instant lastActivity;

    SessionState(String sessionId, int contextLimit) {
        this.sessionId = sessionId;
        this.status = SessionStatus.IDLE;
        this.planMode = PlanMode.AUTO;
        this.compressionTier = CompressionTier.NORMAL;
        this.activeAgent = AgentRole.MANAGER;
        this.blackboard = new Blackboard();
        this.conversation = new ArrayList<>();
        this.loadedSkills = new HashMap<>();
        this.contextTokensUsed = 0;
        this.contextTokensMax = contextLimit;
        this.roundCount = 0;
        this.truncationPasses = 0;
        this.startedAt = Instant.now();
        this.lastActivity = Instant.now();
    }

    double contextPressure() {
        return (double) contextTokensUsed / contextTokensMax;
    }

    void addMessage(String role, String content) {
        Map<String, String> msg = new HashMap<>();
        msg.put("role", role);
        msg.put("content", content);
        msg.put("timestamp", Instant.now().toString());
        conversation.add(msg);
        contextTokensUsed += estimateTokens(content);
        lastActivity = Instant.now();
    }

    private int estimateTokens(String text) {
        return (int) (text.split("\\s+").length * 1.3);
    }
}

// ---- Timeout Governor -----------------------------------------------------

class TimeoutGovernor {
    final Duration globalTimeout;
    final Duration minimumFloor;
    Instant executionStart;
    Duration modelActiveTime = Duration.ZERO;

    TimeoutGovernor(Duration globalTimeout, Duration minimumFloor) {
        this.globalTimeout = globalTimeout;
        this.minimumFloor = minimumFloor;
    }

    void startExecution() { executionStart = Instant.now(); }

    void addModelActiveSpan(Duration span) {
        modelActiveTime = modelActiveTime.plus(span);
    }

    boolean isTimedOut() {
        if (executionStart == null) return false;
        Duration elapsed = Duration.between(executionStart, Instant.now());
        Duration effective = elapsed.minus(modelActiveTime); // exclude model time
        return effective.compareTo(globalTimeout) > 0 &&
               elapsed.compareTo(minimumFloor) > 0;
    }

    Duration remaining() {
        if (executionStart == null) return globalTimeout;
        Duration elapsed = Duration.between(executionStart, Instant.now());
        Duration effective = elapsed.minus(modelActiveTime);
        return globalTimeout.minus(effective);
    }
}

// ---- Truncation Recovery Engine -------------------------------------------

class TruncationRecovery {
    int maxPasses = 5;
    int tokenPerPass = 0;
    int totalRecoveredTokens = 0;

    static class RecoveryResult {
        boolean recovered;
        String repairedContent;
        int tokensRecovered;
        int passNumber;

        RecoveryResult(boolean recovered, String content, int tokens, int pass) {
            this.recovered = recovered;
            this.repairedContent = content;
            this.tokensRecovered = tokens;
            this.passNumber = pass;
        }
    }

    boolean detectTruncation(String output) {
        // Detect truncation signals: unmatched braces, incomplete JSON, cut-off markers
        int opens = 0, closes = 0;
        for (char c : output.toCharArray()) {
            if (c == '{' || c == '[' || c == '(') opens++;
            if (c == '}' || c == ']' || c == ')') closes++;
        }
        boolean unmatched = opens > closes;
        boolean cutOff = output.endsWith("...") || output.endsWith("```") ||
                         output.endsWith(",") || output.endsWith("\\n");
        return unmatched || cutOff;
    }

    RecoveryResult attemptRecovery(String truncatedOutput, int passNumber) {
        if (passNumber > maxPasses) {
            return new RecoveryResult(false, truncatedOutput, 0, passNumber);
        }

        // Find overlap point for continuation
        String tail = truncatedOutput.substring(
                Math.max(0, truncatedOutput.length() - 200));

        // Repair unmatched symbols
        String repaired = repairSymbols(truncatedOutput);
        int tokensRecovered = estimateTokens(repaired) - estimateTokens(truncatedOutput);
        totalRecoveredTokens += Math.max(0, tokensRecovered);

        System.out.printf("[CLOUDS-OMNI-JAVA] Truncation recovery pass %d/%d: %d tokens recovered%n",
                passNumber, maxPasses, tokensRecovered);

        return new RecoveryResult(true, repaired, tokensRecovered, passNumber);
    }

    String repairSymbols(String text) {
        // Count unmatched pairs and close them
        StringBuilder sb = new StringBuilder(text);
        int braces = 0, brackets = 0, parens = 0;
        for (char c : text.toCharArray()) {
            switch (c) {
                case '{': braces++; break;
                case '}': braces--; break;
                case '[': brackets++; break;
                case ']': brackets--; break;
                case '(': parens++; break;
                case ')': parens--; break;
            }
        }
        while (parens > 0) { sb.append(')'); parens--; }
        while (brackets > 0) { sb.append(']'); brackets--; }
        while (braces > 0) { sb.append('}'); braces--; }
        return sb.toString();
    }

    private int estimateTokens(String text) {
        return (int) (text.split("\\s+").length * 1.3);
    }
}

// ---- Context Compressor ---------------------------------------------------

class ContextCompressor {

    List<Map<String, String>> compress(
            List<Map<String, String>> messages,
            CompressionTier tier,
            int targetTokens
    ) {
        if (tier == CompressionTier.NORMAL) return messages;

        int keepCount = (int) (messages.size() * tier.retentionFactor);
        keepCount = Math.max(keepCount, 5); // always keep at least 5 messages

        List<Map<String, String>> result = new ArrayList<>();

        // Always keep first message (system/goal) and last N messages
        if (!messages.isEmpty()) result.add(messages.get(0));

        int startIdx = Math.max(1, messages.size() - keepCount);
        for (int i = startIdx; i < messages.size(); i++) {
            result.add(messages.get(i));
        }

        // For HEAVY: summarize dropped messages
        if (tier == CompressionTier.HEAVY && startIdx > 1) {
            int dropped = startIdx - 1;
            Map<String, String> summary = new HashMap<>();
            summary.put("role", "system");
            summary.put("content", String.format(
                    "[CONTEXT COMPACTED: %d messages summarized. Key themes preserved.]", dropped));
            result.add(1, summary);
        }

        System.out.printf("[CLOUDS-OMNI-JAVA] Context compressed: %d -> %d messages (%s tier)%n",
                messages.size(), result.size(), tier.name());
        return result;
    }
}

// ---- Clouds Coder Engine (Main Orchestrator) ------------------------------

public class CloudsCoderEngine {
    private final Map<String, SessionState> sessions = new ConcurrentHashMap<>();
    private final Map<String, Skill> skillRegistry = new ConcurrentHashMap<>();
    private final ContextCompressor compressor = new ContextCompressor();
    private final TruncationRecovery truncationRecovery = new TruncationRecovery();

    public CloudsCoderEngine() {
        loadDefaultSkills();
        System.out.println("[CLOUDS-OMNI-JAVA] Clouds Coder engine initialized.");
        System.out.printf("[CLOUDS-OMNI-JAVA] Skills loaded: %d%n", skillRegistry.size());
    }

    // ---- Session Management -----------------------------------------------

    public SessionState createSession(String sessionId, int contextLimit) {
        SessionState state = new SessionState(sessionId, contextLimit);
        sessions.put(sessionId, state);
        System.out.printf("[CLOUDS-OMNI-JAVA] Session created: %s (ctx_limit=%d)%n",
                sessionId, contextLimit);
        return state;
    }

    public SessionState getSession(String sessionId) {
        return sessions.get(sessionId);
    }

    // ---- Message Processing (Agent Loop) ----------------------------------

    public Map<String, Object> processMessage(String sessionId, String userMessage) {
        SessionState state = sessions.get(sessionId);
        if (state == null) throw new IllegalArgumentException("Session not found: " + sessionId);

        state.roundCount++;
        state.addMessage("user", userMessage);
        state.status = SessionStatus.THINKING;

        // Check context pressure
        if (state.contextPressure() > 0.8) {
            autoCompressContext(state);
        }

        // Phase-aware delegation
        AgentRole delegatedRole = delegateByPhase(state, userMessage);
        state.activeAgent = delegatedRole;

        // Plan mode check
        Map<String, Object> response = new HashMap<>();
        if (state.planMode == PlanMode.ON || (state.planMode == PlanMode.AUTO && isComplexTask(userMessage))) {
            response = executePlanMode(state, userMessage);
        } else {
            response = executeDirectMode(state, userMessage, delegatedRole);
        }

        state.status = SessionStatus.IDLE;
        return response;
    }

    // ---- Phase-Aware Delegation -------------------------------------------

    AgentRole delegateByPhase(SessionState state, String message) {
        String phase = state.blackboard.currentPhase;
        String lower = message.toLowerCase();

        switch (phase) {
            case "research": return AgentRole.EXPLORER;
            case "design":   return AgentRole.MANAGER;
            case "implement": return AgentRole.DEVELOPER;
            case "test":     return AgentRole.DEVELOPER;
            case "review":   return AgentRole.REVIEWER;
            case "deploy":   return AgentRole.DEVELOPER;
            default:
                // Intent-based fallback
                if (lower.contains("investigate") || lower.contains("analyze"))
                    return AgentRole.EXPLORER;
                if (lower.contains("review") || lower.contains("check"))
                    return AgentRole.REVIEWER;
                return AgentRole.DEVELOPER;
        }
    }

    // ---- Plan Mode Execution ----------------------------------------------

    Map<String, Object> executePlanMode(SessionState state, String userMessage) {
        state.blackboard.originalGoal = userMessage;
        state.blackboard.managerCycles++;

        // Step 1: Explorer research
        state.blackboard.researchNotes.add("Analyzing: " + userMessage);

        // Step 2: Manager synthesis -> proposals
        List<String> planSteps = new ArrayList<>();
        planSteps.add("1. Research dependencies and requirements");
        planSteps.add("2. Design architecture/approach");
        planSteps.add("3. Implement core changes");
        planSteps.add("4. Write/run tests");
        planSteps.add("5. Code review and validation");
        state.blackboard.planSteps = planSteps;
        state.blackboard.planCursor = 0;

        Map<String, Object> result = new HashMap<>();
        result.put("type", "plan_proposal");
        result.put("steps", planSteps);
        result.put("awaiting_approval", true);
        result.put("agent", AgentRole.MANAGER.name());
        return result;
    }

    Map<String, Object> executeDirectMode(SessionState state, String msg, AgentRole role) {
        state.status = SessionStatus.EXECUTING;

        // Execute tool calls (simulated — real: LLM -> tool_use -> tool_result loop)
        String output = String.format("[%s] Processing: %s", role.name(), msg.substring(0, Math.min(60, msg.length())));
        state.addMessage("assistant", output);
        state.blackboard.executionLogs.add(output);

        // Check for errors in output
        detectErrors(state, output);

        // Check for truncation
        if (truncationRecovery.detectTruncation(output)) {
            state.status = SessionStatus.TRUNCATION_RECOVERY;
            state.truncationPasses++;
            TruncationRecovery.RecoveryResult recovery =
                    truncationRecovery.attemptRecovery(output, state.truncationPasses);
            if (recovery.recovered) {
                output = recovery.repairedContent;
            }
        }

        // Reviewer Debug Mode: if errors detected, reviewer gets write access
        if (!state.blackboard.errors.isEmpty() && role != AgentRole.REVIEWER) {
            state.activeAgent = AgentRole.REVIEWER;
            state.blackboard.reviewFeedback.add(
                    "Debug Mode activated: " + state.blackboard.errors.size() + " errors found");
        }

        Map<String, Object> result = new HashMap<>();
        result.put("type", "response");
        result.put("content", output);
        result.put("agent", role.name());
        result.put("round", state.roundCount);
        result.put("context_pressure", String.format("%.1f%%", state.contextPressure() * 100));
        return result;
    }

    // ---- Error Detection (6-Category) -------------------------------------

    void detectErrors(SessionState state, String output) {
        String lower = output.toLowerCase();
        if (lower.contains("error:") || lower.contains("exception")) {
            ErrorCategory cat = ErrorCategory.RUNTIME;
            if (lower.contains("test") || lower.contains("assert")) cat = ErrorCategory.TEST;
            else if (lower.contains("lint")) cat = ErrorCategory.LINT;
            else if (lower.contains("compile") || lower.contains("syntax")) cat = ErrorCategory.COMPILATION;
            else if (lower.contains("build")) cat = ErrorCategory.BUILD;
            else if (lower.contains("deploy")) cat = ErrorCategory.DEPLOY;

            state.blackboard.addError(new ErrorEntry(cat, output.substring(0, Math.min(100, output.length())), "", 0));
        }
    }

    // ---- Context Auto-Compression -----------------------------------------

    void autoCompressContext(SessionState state) {
        double pressure = state.contextPressure();
        CompressionTier tier;
        if (pressure > 0.95) tier = CompressionTier.HEAVY;
        else if (pressure > 0.85) tier = CompressionTier.MEDIUM;
        else tier = CompressionTier.LIGHT;

        state.compressionTier = tier;
        state.conversation = compressor.compress(
                state.conversation, tier, state.contextTokensMax);
        // Recalculate tokens
        state.contextTokensUsed = state.conversation.stream()
                .mapToInt(m -> (int) (m.getOrDefault("content", "").split("\\s+").length * 1.3))
                .sum();
    }

    // ---- Skill Management -------------------------------------------------

    void loadDefaultSkills() {
        registerSkill(new Skill("code-review", "quality", "Structured code review with checklist"));
        registerSkill(new Skill("agent-builder", "agent", "Build new agent configurations"));
        registerSkill(new Skill("mcp-builder", "integration", "Build MCP server configurations"));
        registerSkill(new Skill("pdf-analysis", "data", "Parse and analyze PDF documents"));
        registerSkill(new Skill("html-report", "reporting", "Generate HTML reports from data"));
        registerSkill(new Skill("degradation-recovery", "reliability", "Recover from degraded states"));
    }

    public void registerSkill(Skill skill) {
        skillRegistry.put(skill.name, skill);
    }

    public Skill loadSkill(String sessionId, String skillName) {
        SessionState state = sessions.get(sessionId);
        Skill skill = skillRegistry.get(skillName);
        if (state != null && skill != null) {
            skill.loaded = true;
            state.loadedSkills.put(skillName, skill);
            System.out.printf("[CLOUDS-OMNI-JAVA] Skill loaded: %s -> session %s%n",
                    skillName, sessionId);
        }
        return skill;
    }

    // ---- Helpers ----------------------------------------------------------

    boolean isComplexTask(String message) {
        int wordCount = message.split("\\s+").length;
        return wordCount > 30 || message.contains("refactor") || message.contains("migrate")
                || message.contains("implement") || message.contains("architecture");
    }

    // ---- Stats ------------------------------------------------------------

    public Map<String, Object> engineStats() {
        Map<String, Object> stats = new HashMap<>();
        stats.put("active_sessions", sessions.size());
        stats.put("skills_registered", skillRegistry.size());
        stats.put("total_rounds", sessions.values().stream()
                .mapToInt(s -> s.roundCount).sum());
        stats.put("total_errors", sessions.values().stream()
                .mapToInt(s -> s.blackboard.errorCount()).sum());
        return stats;
    }
}
