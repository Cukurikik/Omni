// OMNI MOTHER SYSTEM - SECURITY LAYER
// Strict Path Traversal Blocker.
// Defends filesystem APIs from Directory Traversal (../) exploits.

import * as path from 'path';

export type OmniResult<T, E> = 
  | { success: true; value: T; error: null }
  | { success: false; value: null; error: E };

export class PathTraversalBlocker {
    private readonly rootDirectory: string;

    constructor(rootDirectory: string) {
        // Enforce absolute paths internally
        if (!path.isAbsolute(rootDirectory)) {
            throw new Error("OMNI_FATAL: Root directory must be an absolute path.");
        }
        
        // Normalize to remove any lingering quirks
        this.rootDirectory = path.normalize(rootDirectory);
    }

    /**
     * @brief Secures user input attempting to request a file within the sandbox.
     * Throws out any request that resolves outside the defined root.
     */
    public secureFilePath(userInputPath: string): OmniResult<string, string> {
        if (!userInputPath || userInputPath.trim() === '') {
            return { success: false, value: null, error: "Empty path provided." };
        }

        // Null byte injection check. Often bypasses weak regex or string endsWith checks in C bindings.
        if (userInputPath.indexOf('\0') !== -1) {
             return { success: false, value: null, error: "OMNI_FATAL: Null byte poison attack detected." };
        }

        // Resolve the requested path against our strict root boundary
        const resolvedPath = path.join(this.rootDirectory, userInputPath);
        
        // Final normalization to collapse all ../ and ./
        const finalNormalizedPath = path.normalize(resolvedPath);

        // Security assertion: The resolved path MUST still start with the root directory.
        // If they requested '../../etc/passwd', the normalized string will no longer start with the root.
        if (!finalNormalizedPath.startsWith(this.rootDirectory)) {
            return { success: false, value: null, error: "OMNI_FATAL: Path Traversal attempt detected and blocked." };
        }

        // Prevent access to the root directory itself (they must target a specific file)
        if (finalNormalizedPath === this.rootDirectory || finalNormalizedPath === this.rootDirectory + path.sep) {
             return { success: false, value: null, error: "OMNI_FATAL: Directory listing not permitted." };
        }

        return { success: true, value: finalNormalizedPath, error: null };
    }
}
