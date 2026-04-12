import { OmniWebMotionEngine } from '@omni-bridge/ui/motion';

export const omni_anim_holo_glow_050 = () => {
    return {
        id: "omni-anim-holo-glow-050",
        duration: 563,
        easing: "omni-cyberpunk-glitch",
        execute: (el: HTMLElement) => {
            el.style.transform = "translate3d(28px, 22px, 0)";
            el.style.filter = "contrast(2.4431742836792965) hue-rotate(172deg)";
        }
    };
};
