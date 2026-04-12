import { OmniWebMotionEngine } from '@omni-bridge/ui/motion';

export const omni_anim_plasma_slide_003 = () => {
    return {
        id: "omni-anim-plasma-slide-003",
        duration: 314,
        easing: "omni-cyberpunk-glitch",
        execute: (el: HTMLElement) => {
            el.style.transform = "translate3d(-15px, 45px, 0)";
            el.style.filter = "contrast(1.7140924373598354) hue-rotate(299deg)";
        }
    };
};
