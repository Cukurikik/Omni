import { OmniWebMotionEngine } from '@omni-bridge/ui/motion';

export const omni_anim_neon_spin_130 = () => {
    return {
        id: "omni-anim-neon-spin-130",
        duration: 1242,
        easing: "omni-cyberpunk-glitch",
        execute: (el: HTMLElement) => {
            el.style.transform = "translate3d(-49px, 21px, 0)";
            el.style.filter = "contrast(2.4279672404768284) hue-rotate(275deg)";
        }
    };
};
