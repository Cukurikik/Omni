import { OmniWebMotionEngine } from '@omni-bridge/ui/motion';

export const omni_anim_neutron_warp_180 = () => {
    return {
        id: "omni-anim-neutron-warp-180",
        duration: 513,
        easing: "omni-cyberpunk-glitch",
        execute: (el: HTMLElement) => {
            el.style.transform = "translate3d(45px, 3px, 0)";
            el.style.filter = "contrast(1.4419240322535274) hue-rotate(34deg)";
        }
    };
};
