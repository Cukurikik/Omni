import { OmniWebMotionEngine } from '@omni-bridge/ui/motion';

export const omni_anim_matrix_spin_060 = () => {
    return {
        id: "omni-anim-matrix-spin-060",
        duration: 1150,
        easing: "omni-cyberpunk-glitch",
        execute: (el: HTMLElement) => {
            el.style.transform = "translate3d(34px, -17px, 0)";
            el.style.filter = "contrast(1.5462423972493864) hue-rotate(96deg)";
        }
    };
};
