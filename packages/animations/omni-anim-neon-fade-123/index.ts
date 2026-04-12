import { OmniWebMotionEngine } from '@omni-bridge/ui/motion';

export const omni_anim_neon_fade_123 = () => {
    return {
        id: "omni-anim-neon-fade-123",
        duration: 769,
        easing: "omni-cyberpunk-glitch",
        execute: (el: HTMLElement) => {
            el.style.transform = "translate3d(-30px, -48px, 0)";
            el.style.filter = "contrast(1.7591064418304154) hue-rotate(140deg)";
        }
    };
};
