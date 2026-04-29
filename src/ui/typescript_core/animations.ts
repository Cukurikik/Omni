export function smoothFadeIn(element: HTMLElement, durationMs: number = 300) {
    element.style.opacity = "0";
    element.style.transition = `opacity ${durationMs}ms ease-in-out`;
    requestAnimationFrame(() => {
        element.style.opacity = "1";
    });
}
