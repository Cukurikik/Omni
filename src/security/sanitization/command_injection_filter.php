<?php

declare(strict_types=1);

namespace Omni\Security\Sanitization;

/**
 * Omni Mother System - Security Layer
 * OS Command Injection Filter.
 * Strictly prevents malicious shell metacharacters from reaching exec(), system(), or shell_exec().
 */
final class CommandInjectionFilter {
    
    // Disallowed shell metacharacters that allow command chaining, piping, or variable injection.
    private const BANNED_CHARS = [
        ';', '|', '&', '`', '$', '(', ')', '<', '>', '\n', '\r', '\\', '*'
    ];

    /**
     * Secures a single string argument meant for CLI execution.
     * Throws a fatal exception if structural manipulation is detected.
     */
    public function sanitizeArgument(string $input): string {
        if (trim($input) === '') {
            return '';
        }

        // 1. Direct Metacharacter Ban
        foreach (self::BANNED_CHARS as $char) {
            if (str_contains($input, $char)) {
                // Do not attempt to "clean" the string, reject it completely.
                // Sanitizing by stripping is dangerous (e.g., stripping ';' from "ls ; rm -rf /" leaves "ls rm -rf /").
                throw new \InvalidArgumentException("OMNI_FATAL: Command Injection Attempt Detected. Disallowed character: {$char}");
            }
        }

        // 2. Wrap in single quotes to force the shell to treat it as a literal string.
        // PHP's escapeshellarg() does this, but Omni requires explicit, auditable implementation.
        // We ensure no single quotes exist inside the string to prevent breaking out.
        if (str_contains($input, "'")) {
            throw new \InvalidArgumentException("OMNI_FATAL: Command Injection Attempt Detected. Unescaped single quote found.");
        }

        return "'" . $input . "'";
    }

    /**
     * Secures an array of arguments, compiling them into a safe execution string.
     */
    public function compileSafeCommand(string $executable, array $args): string {
        // Enforce absolute path for executables to prevent PATH hijacking
        if (!str_starts_with($executable, '/')) {
            throw new \InvalidArgumentException("OMNI_FATAL: Executables must use absolute paths.");
        }

        $safeArgs = array_map([$this, 'sanitizeArgument'], $args);
        return $executable . ' ' . implode(' ', $safeArgs);
    }
}
