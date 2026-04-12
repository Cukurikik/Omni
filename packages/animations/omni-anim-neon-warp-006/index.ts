import { OmniWebMotionEngine } from '@omni-bridge/ui/motion';

export const omni_anim_neon_warp_006 = () => {
    return {
        id: "omni-anim-neon-warp-006",
        duration: 875,
        easing: "omni-cyberpunk-glitch",
        execute: (el: HTMLElement) => {
            el.style.transform = "translate3d(24px, -16px, 0)";
            el.style.filter = "contrast(1.8990258392621058) hue-rotate(355deg)";
        }
    };
};
