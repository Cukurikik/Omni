import { OmniWebMotionEngine } from '@omni-bridge/ui/motion';

export const omni_anim_neutron_slide_120 = () => {
    return {
        id: "omni-anim-neutron-slide-120",
        duration: 374,
        easing: "omni-cyberpunk-glitch",
        execute: (el: HTMLElement) => {
            el.style.transform = "translate3d(-16px, 26px, 0)";
            el.style.filter = "contrast(1.1977604549835652) hue-rotate(322deg)";
        }
    };
};
