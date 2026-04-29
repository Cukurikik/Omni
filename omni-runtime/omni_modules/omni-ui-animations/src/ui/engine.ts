/**
 * [OMNI-PACKAGE] omni-ui-animations
 * Description: Zero DOM-Blocking pure GPU Canvas & CSS Matrix animations.
 */

// Animation configuration interface
export interface AnimationConfig {
  duration: number;
  easing: string;
  stagger: boolean;
}

// Pre-built animation presets
export const AnimationPresets = {
  fadeIn: {
    duration: 300,
    easing: "ease-in",
    stagger: false,
  } as AnimationConfig,
  slideUp: {
    duration: 400,
    easing: "cubic-bezier(0.4, 0, 0.2, 1)",
    stagger: false,
  } as AnimationConfig,
  slideIn: {
    duration: 350,
    easing: "ease-out",
    stagger: false,
  } as AnimationConfig,
  staggerReveal: {
    duration: 500,
    easing: "ease-in-out",
    stagger: true,
  } as AnimationConfig,
  bounceIn: {
    duration: 600,
    easing: "cubic-bezier(0.68, -0.55, 0.265, 1.55)",
    stagger: false,
  } as AnimationConfig,
};

/**
 * OmniSlideIn — GPU-accelerated slide-in animation component.
 * Bypasses heavy DOM reflows by using CSS transforms and will-change.
 */
export function createSlideInElement(config: AnimationConfig): HTMLDivElement {
  const el = document.createElement("div");
  el.className = "omni-gpu-slide-in";
  el.style.animationDuration = `${config.duration}ms`;
  el.style.animationTimingFunction = config.easing;
  el.style.willChange = "transform, opacity";
  return el;
}

/**
 * Apply staggered animation to a list of elements.
 * Each element is delayed by `config.duration * 0.1` from the previous.
 */
export function applyStaggerAnimation(
  elements: HTMLElement[],
  config: AnimationConfig,
): void {
  elements.forEach((el, index) => {
    const delay = config.stagger ? index * config.duration * 0.1 : 0;
    el.style.animationDelay = `${delay}ms`;
    el.style.animationDuration = `${config.duration}ms`;
    el.style.animationTimingFunction = config.easing;
    el.classList.add("omni-animate-in");
  });
}

/**
 * OmniAnimationEngine — manages animation lifecycle across the OMNI UI.
 */
export class OmniAnimationEngine {
  private activeAnimations: Map<string, Animation> = new Map();

  animate(elementId: string, config: AnimationConfig): void {
    const el = document.getElementById(elementId);
    if (!el) return;

    const animation = el.animate(
      [
        { transform: "translateY(20px)", opacity: 0 },
        { transform: "translateY(0)", opacity: 1 },
      ],
      {
        duration: config.duration,
        easing: config.easing,
        fill: "forwards",
      },
    );

    this.activeAnimations.set(elementId, animation);
  }

  cancelAll(): void {
    this.activeAnimations.forEach((anim) => anim.cancel());
    this.activeAnimations.clear();
  }
}
