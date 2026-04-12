import { OmniWebMotionEngine } from '@omni-bridge/ui/motion';

export const omni_anim_glass_burst_025 = () => {
    return {
        id: "omni-anim-glass-burst-025",
        duration: 1277,
        easing: "omni-cyberpunk-glitch",
        execute: (el: HTMLElement) => {
            el.style.transform = "translate3d(24px, -45px, 0)";
            el.style.filter = "contrast(1.5932177333092024) hue-rotate(69deg)";
        }
    };
};
