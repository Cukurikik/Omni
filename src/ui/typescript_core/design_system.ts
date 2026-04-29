export const OmniColors = {
    primary: "#0A84FF",
    background: "#000000",
    text: "#FFFFFF"
};

export function applyTheme(element: HTMLElement) {
    element.style.backgroundColor = OmniColors.background;
    element.style.color = OmniColors.text;
}
