// moe_atom_kancolle_panel.ts — Interface
// Layer: Interface — Atom Kancolle UI Panel
// Inspired by: atom-kancolle (Notification using fleet girls' voice)

export class KanColleUIPanel {
    private panelElement: HTMLElement;
    private characterImg: HTMLImageElement;
    private messageBox: HTMLDivElement;
    private audioContext: AudioContext;

    constructor() {
        this.panelElement = document.createElement('div');
        this.panelElement.className = 'kancolle-notify-panel';
        
        this.characterImg = document.createElement('img');
        this.messageBox = document.createElement('div');
        
        this.panelElement.appendChild(this.characterImg);
        this.panelElement.appendChild(this.messageBox);
        document.body.appendChild(this.panelElement);
        
        this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
    }

    public async triggerNotification(characterId: string, eventText: string, audioUrl: string) {
        // UI Updates
        this.characterImg.src = `/assets/characters/${characterId}.png`;
        this.messageBox.textContent = eventText;
        this.panelElement.classList.add('slide-in');

        // Audio Playback
        try {
            const response = await fetch(audioUrl);
            const arrayBuffer = await response.arrayBuffer();
            const audioBuffer = await this.audioContext.decodeAudioData(arrayBuffer);
            
            const source = this.audioContext.createBufferSource();
            source.buffer = audioBuffer;
            source.connect(this.audioContext.destination);
            source.start();

            // Dismiss panel after audio finishes
            source.onended = () => {
                this.panelElement.classList.remove('slide-in');
            };
        } catch (e) {
            console.error("[KanColle UI] Audio playback failed:", e);
        }
    }
}
