import { OmniWebMotionEngine } from '@omni-bridge/ui/motion';

export const omni_anim_holo_burst_128 = () => {
    return {
        id: "omni-anim-holo-burst-128",
        duration: 1092,
        easing: "omni-cyberpunk-glitch",
        execute: (el: HTMLElement) => {
            el.style.transform = "translate3d(21px, 9px, 0)";
            el.style.filter = "contrast(1.412806120748678) hue-rotate(231deg)";
        }
    };
};
