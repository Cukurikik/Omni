/// <reference lib="dom" />
/// <reference types="node" />
// omni_ultimatestarterkit_engine.ts
// Production-Grade Cross-Platform Starter Kit Engine
// ==============================================================
// Absorbed from: hfjooste/UltimateStarterKit
//
// OMNI Layer: ui/typescript_core
// @since 2026.4.0

const ENGINE_VERSION = "1.0.0-omni";

interface PlatformConfig { os: string; arch: string; apiLevel: number; renderer: string; }
interface ThemeTokens { primary: string; secondary: string; background: string; surface: string; text: string; fontSize: number; borderRadius: number; }
interface ScreenLayout { id: string; type: "stack" | "tab" | "drawer"; children: string[]; params: Record<string, unknown>; }

class StarterKitError extends Error {
    constructor(public code: string, msg: string) { super(msg); this.name = "StarterKitError"; }
}

/**
 * Production-grade cross-platform starter kit engine.
 * Manages platform detection, theming, navigation, and component registration.
 */
export class OmniUltimateStarterKitEngine {
    private platform: PlatformConfig | null = null;
    private theme: ThemeTokens;
    private screens: Map<string, ScreenLayout> = new Map();
    private components: Map<string, { type: string; props: Record<string, unknown> }> = new Map();

    constructor(theme?: Partial<ThemeTokens>) {
        this.theme = {
            primary: theme?.primary ?? "#6200EE",
            secondary: theme?.secondary ?? "#03DAC6",
            background: theme?.background ?? "#121212",
            surface: theme?.surface ?? "#1E1E1E",
            text: theme?.text ?? "#FFFFFF",
            fontSize: theme?.fontSize ?? 16,
            borderRadius: theme?.borderRadius ?? 8,
        };
    }

    /** Detect and configure target platform. */
    detectPlatform(os: string, arch: string = "arm64", apiLevel: number = 33): {
        status: string; data: PlatformConfig;
    } {
        const validOs = ["ios", "android", "web", "macos", "windows", "linux"];
        if (!validOs.includes(os)) throw new StarterKitError("UNKNOWN_OS", `OS must be one of: ${validOs.join(", ")}`);

        const renderer = os === "web" ? "dom" : os === "ios" || os === "macos" ? "uikit" : "canvas";
        this.platform = { os, arch, apiLevel, renderer };
        return { status: "success", data: this.platform };
    }

    /** Register a screen layout. */
    registerScreen(layout: ScreenLayout): { status: string; data: ScreenLayout } {
        if (this.screens.has(layout.id)) throw new StarterKitError("DUP_SCREEN", `Screen '${layout.id}' exists`);
        this.screens.set(layout.id, layout);
        return { status: "success", data: layout };
    }

    /** Register a reusable component. */
    registerComponent(id: string, type: string, props: Record<string, unknown> = {}): {
        status: string; data: { id: string; type: string };
    } {
        this.components.set(id, { type, props });
        return { status: "success", data: { id, type } };
    }

    /** Generate navigation map from registered screens. */
    buildNavigationMap(): {
        status: string; data: { screens: ScreenLayout[]; graph: Record<string, string[]>; totalRoutes: number };
    } {
        const screenList = Array.from(this.screens.values());
        const graph: Record<string, string[]> = {};
        for (const screen of screenList) {
            graph[screen.id] = screen.children.filter(c => this.screens.has(c));
        }
        const totalRoutes = Object.values(graph).reduce((sum, c) => sum + c.length, 0);
        return { status: "success", data: { screens: screenList, graph, totalRoutes } };
    }

    /** Apply theme tokens and compute derived values. */
    applyTheme(overrides: Partial<ThemeTokens>): {
        status: string; data: ThemeTokens & { contrast: string; shadowColor: string };
    } {
        Object.assign(this.theme, overrides);
        const bg = parseInt(this.theme.background.replace("#", ""), 16);
        const isDark = ((bg >> 16) & 0xff) < 128;
        return {
            status: "success",
            data: {
                ...this.theme,
                contrast: isDark ? "#FFFFFF" : "#000000",
                shadowColor: isDark ? "rgba(0,0,0,0.5)" : "rgba(0,0,0,0.2)",
            },
        };
    }

    /** Get full app configuration snapshot. */
    getAppConfig(): {
        status: string; data: {
            platform: PlatformConfig | null; theme: ThemeTokens;
            screenCount: number; componentCount: number;
        };
    } {
        return {
            status: "success",
            data: {
                platform: this.platform,
                theme: this.theme,
                screenCount: this.screens.size,
                componentCount: this.components.size,
            },
        };
    }

    // --- Registry Interface ---
    diagnostics(): Record<string, unknown> {
        return {
            engine: "OmniUltimateStarterKitEngine",
            version: "1.0.0",
            status: "operational",
            layer: "ui",
            language: "TypeScript",
        };
    }
}
