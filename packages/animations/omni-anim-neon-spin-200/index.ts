import { OmniWebMotionEngine } from '@omni-bridge/ui/motion';

export const omni_anim_neon_spin_200 = () => {
    return {
        id: "omni-anim-neon-spin-200",
        duration: 847,
        easing: "omni-cyberpunk-glitch",
        execute: (el: HTMLElement) => {
            el.style.transform = "translate3d(1px, -24px, 0)";
            el.style.filter = "contrast(1.1326399681971275) hue-rotate(74deg)";
        }
    };
};
