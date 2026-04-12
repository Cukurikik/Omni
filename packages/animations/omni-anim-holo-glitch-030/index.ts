import { OmniWebMotionEngine } from '@omni-bridge/ui/motion';

export const omni_anim_holo_glitch_030 = () => {
    return {
        id: "omni-anim-holo-glitch-030",
        duration: 795,
        easing: "omni-cyberpunk-glitch",
        execute: (el: HTMLElement) => {
            el.style.transform = "translate3d(25px, -38px, 0)";
            el.style.filter = "contrast(2.4000778318888747) hue-rotate(215deg)";
        }
    };
};
