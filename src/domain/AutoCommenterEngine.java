// ===========================================================================
// OMNI DOMAIN LAYER — AUTO-COMMENTER CODE REVIEW ENGINE
// ===========================================================================
// Source Paradigm : nicehash/auto-commenter
// Domain Layer   : Domain (Enterprise backend, developer workflow)
// Language        : Java
// Function        : Automated code review comment generator that analyzes
//                   diffs, detects anti-patterns, computes complexity metrics,
//                   and generates actionable review comments
// ===========================================================================

package domain;

import java.util.*;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

public class AutoCommenterEngine {

    // ---- Enums ----------------------------------------------------------------

    public enum Severity { INFO, SUGGESTION, WARNING, ERROR }
    public enum Category {
        NAMING, COMPLEXITY, SECURITY, STYLE,
        PERFORMANCE, DOCUMENTATION, ERROR_HANDLING, TESTING
    }

    // ---- Data Models ----------------------------------------------------------

    public static class DiffHunk {
        public final String filePath;
        public final int startLine;
        public final int endLine;
        public final List<String> addedLines;
        public final List<String> removedLines;

        public DiffHunk(String filePath, int startLine, int endLine,
                        List<String> added, List<String> removed) {
            this.filePath = filePath;
            this.startLine = startLine;
            this.endLine = endLine;
            this.addedLines = Collections.unmodifiableList(added);
            this.removedLines = Collections.unmodifiableList(removed);
        }
    }

    public static class ReviewComment {
        public final String filePath;
        public final int line;
        public final Severity severity;
        public final Category category;
        public final String message;
        public final String suggestion;

        public ReviewComment(String filePath, int line, Severity severity,
                             Category category, String message, String suggestion) {
            this.filePath = filePath;
            this.line = line;
            this.severity = severity;
            this.category = category;
            this.message = message;
            this.suggestion = suggestion;
        }

        @Override
        public String toString() {
            return String.format("[%s/%s] %s:%d — %s", severity, category, filePath, line, message);
        }
    }

    // ---- Anti-Pattern Rules ---------------------------------------------------

    private static final Map<Pattern, String[]> ANTI_PATTERNS = new LinkedHashMap<>() {{
        put(Pattern.compile("catch\\s*\\(\\s*Exception\\s"),
            new String[]{"Catching generic Exception hides specific errors",
                         "Catch specific exception types instead", "ERROR_HANDLING", "WARNING"});

        put(Pattern.compile("System\\.out\\.print"),
            new String[]{"System.out.print used in production code",
                         "Use a logging framework (SLF4J, Log4j)", "STYLE", "SUGGESTION"});

        put(Pattern.compile("\\bnew\\s+Thread\\("),
            new String[]{"Raw Thread creation detected",
                         "Use ExecutorService for thread management", "PERFORMANCE", "WARNING"});

        put(Pattern.compile("TODO|FIXME|HACK|XXX"),
            new String[]{"Unresolved code marker found",
                         "Address before merging to main", "DOCUMENTATION", "INFO"});

        put(Pattern.compile("password\\s*=\\s*\""),
            new String[]{"Hardcoded password detected!",
                         "Use environment variables or secret manager", "SECURITY", "ERROR"});

        put(Pattern.compile("\\bvar\\b.*=.*null;"),
            new String[]{"Nullable variable initialization",
                         "Use Optional<T> to express optionality", "ERROR_HANDLING", "SUGGESTION"});
    }};

    // ---- Complexity Calculator ------------------------------------------------

    /**
     * Compute cyclomatic complexity of a code block.
     * Counts decision points: if, for, while, case, catch, &&, ||
     */
    public static int computeCyclomaticComplexity(List<String> lines) {
        int complexity = 1; // base path
        Pattern decisionPattern = Pattern.compile(
            "\\b(if|for|while|case|catch)\\b|&&|\\|\\|");

        for (String line : lines) {
            var matcher = decisionPattern.matcher(line);
            while (matcher.find()) {
                complexity++;
            }
        }
        return complexity;
    }

    // ---- Core Analyzer --------------------------------------------------------

    private final List<ReviewComment> comments = new ArrayList<>();

    public AutoCommenterEngine() {
        System.out.println("[AUTOCOMMENT-OMNI-JAVA] Review engine initialized.");
    }

    /**
     * Analyze a diff hunk for anti-patterns and complexity.
     */
    public List<ReviewComment> analyzeDiff(DiffHunk hunk) {
        List<ReviewComment> newComments = new ArrayList<>();

        System.out.printf("[AUTOCOMMENT-OMNI-JAVA] Analyzing: %s (lines %d-%d, +%d -%d)%n",
                hunk.filePath, hunk.startLine, hunk.endLine,
                hunk.addedLines.size(), hunk.removedLines.size());

        // Check added lines for anti-patterns
        for (int i = 0; i < hunk.addedLines.size(); i++) {
            String line = hunk.addedLines.get(i);
            int lineNum = hunk.startLine + i;

            for (var entry : ANTI_PATTERNS.entrySet()) {
                if (entry.getKey().matcher(line).find()) {
                    String[] rule = entry.getValue();
                    ReviewComment comment = new ReviewComment(
                        hunk.filePath, lineNum,
                        Severity.valueOf(rule[3]),
                        Category.valueOf(rule[2]),
                        rule[0], rule[1]
                    );
                    newComments.add(comment);
                    System.out.printf("[AUTOCOMMENT-OMNI-JAVA]   %s%n", comment);
                }
            }
        }

        // Check complexity
        int complexity = computeCyclomaticComplexity(hunk.addedLines);
        if (complexity > 10) {
            newComments.add(new ReviewComment(
                hunk.filePath, hunk.startLine,
                Severity.WARNING, Category.COMPLEXITY,
                String.format("High cyclomatic complexity: %d (threshold: 10)", complexity),
                "Consider extracting logic into smaller methods."
            ));
        }

        // Check for missing documentation
        boolean hasPublicMethod = hunk.addedLines.stream()
                .anyMatch(l -> l.contains("public ") && l.contains("("));
        boolean hasJavadoc = hunk.addedLines.stream()
                .anyMatch(l -> l.trim().startsWith("/**"));
        if (hasPublicMethod && !hasJavadoc) {
            newComments.add(new ReviewComment(
                hunk.filePath, hunk.startLine,
                Severity.SUGGESTION, Category.DOCUMENTATION,
                "Public method lacks Javadoc documentation",
                "Add /** ... */ documentation for all public APIs."
            ));
        }

        comments.addAll(newComments);
        return newComments;
    }

    /**
     * Generate a summary report of all review comments.
     */
    public String generateReport() {
        Map<Severity, Long> bySeverity = comments.stream()
                .collect(Collectors.groupingBy(c -> c.severity, Collectors.counting()));

        StringBuilder sb = new StringBuilder();
        sb.append(String.format("══ Code Review Summary: %d comment(s) ══%n", comments.size()));
        for (Severity s : Severity.values()) {
            sb.append(String.format("  %s: %d%n", s, bySeverity.getOrDefault(s, 0L)));
        }
        return sb.toString();
    }

    public List<ReviewComment> getAllComments() { return Collections.unmodifiableList(comments); }
}
