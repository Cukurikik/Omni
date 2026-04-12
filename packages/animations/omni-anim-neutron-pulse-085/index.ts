import { OmniWebMotionEngine } from '@omni-bridge/ui/motion';

export const omni_anim_neutron_pulse_085 = () => {
    return {
        id: "omni-anim-neutron-pulse-085",
        duration: 488,
        easing: "omni-cyberpunk-glitch",
        execute: (el: HTMLElement) => {
            el.style.transform = "translate3d(50px, 49px, 0)";
            el.style.filter = "contrast(1.9536333716857803) hue-rotate(29deg)";
        }
    };
};
