export class StepAudioStudioUI {
    private container: HTMLElement;

    constructor(containerId: string) {
        const el = document.getElementById(containerId);
        if (!el) throw new Error(`Container ${containerId} not found`);
        this.container = el;
    }

    public renderInterface(): void {
        this.container.innerHTML = `
            <div style="background: #2b2b2b; color: white; padding: 20px; font-family: Inter, sans-serif; border-radius: 10px; width: 600px;">
                <h2>Step Audio EditX Studio</h2>
                
                <div style="margin-bottom: 15px;">
                    <label style="display: block; margin-bottom: 5px;">Input Text</label>
                    <textarea id="ttsText" rows="4" style="width: 100%; background: #1a1a1a; color: white; border: 1px solid #444; border-radius: 5px; padding: 10px;"></textarea>
                </div>
                
                <div style="margin-bottom: 15px;">
                    <label style="display: block; margin-bottom: 5px;">Emotion Control (Happy, Sad, Angry, Fear, Surprise)</label>
                    <input type="range" id="emoHappy" min="0" max="100" value="50" style="width: 18%;">
                    <input type="range" id="emoSad" min="0" max="100" value="0" style="width: 18%;">
                    <input type="range" id="emoAngry" min="0" max="100" value="0" style="width: 18%;">
                    <input type="range" id="emoFear" min="0" max="100" value="0" style="width: 18%;">
                    <input type="range" id="emoSurprise" min="0" max="100" value="0" style="width: 18%;">
                </div>
                
                <button id="generateAudioBtn" style="background: #ff5500; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: bold;">Generate Audio</button>
                <div id="audioPlayerContainer" style="margin-top: 20px;"></div>
            </div>
        `;
    }
}
