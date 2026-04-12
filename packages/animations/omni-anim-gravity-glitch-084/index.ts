import { OmniWebMotionEngine } from '@omni-bridge/ui/motion';

export const omni_anim_gravity_glitch_084 = () => {
    return {
        id: "omni-anim-gravity-glitch-084",
        duration: 357,
        easing: "omni-cyberpunk-glitch",
        execute: (el: HTMLElement) => {
            el.style.transform = "translate3d(-35px, -19px, 0)";
            el.style.filter = "contrast(1.5344773017768891) hue-rotate(270deg)";
        }
    };
};
