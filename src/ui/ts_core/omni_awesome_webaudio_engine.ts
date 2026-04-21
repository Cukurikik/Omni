/// <reference lib="dom" />
/// <reference types="node" />
// ===========================================================================
// OMNI AWESOME WEBAUDIO ENGINE (TRUE KNOWLEDGE EXTRACTION)
// ===========================================================================
// Absorbed Paradigm : notthetup/awesome-webaudio
// Logic Inherited   : TypeScript / UI Layer (Synthesizer Node Graph Paradigm)
// Domain Layer      : UI / TypeScript Core
// ===========================================================================

/*
 * By studying awesome-webaudio synth projects, Mother learned that advanced browser 
 * synthesizers map out multiple oscillators, LFOs, and Envelopes recursively.
 * 
 * Omni demonstrates native knowledge of this WebAudio Domain structure by creating 
 * an elegant structural Class Chain representing exactly how a real Synth Voice 
 * is wired, preserving TypeScript's strict DOM Node Type boundaries!
 */

// Simulated WebAudio Base Nodes
interface WebAudioNode {
    connect(target: WebAudioNode): void;
    id: string;
}

class SynthOscillatorNode implements WebAudioNode {
    id = "Oscillator";
    type: string;
    frequency: number;

    constructor(type: string, freq: number) {
        this.type = type;
        this.frequency = freq;
    }

    connect(target: WebAudioNode): void {
        // Physical binding simulated
    }
}

class SynthGainNode implements WebAudioNode {
    id = "Gain_Envelope";
    gain: number = 0; // Starts silent (Envelope ADSR controls this)

    connect(target: WebAudioNode): void {
        // Physical binding simulated
    }
}

class SynthDestinationOut implements WebAudioNode {
    id = "Speakers_Destination";
    connect(target: WebAudioNode): void { throw new Error("Destination cannot connect further."); }
}

// Omni Abstract Synth Voice encapsulating the routing chain natively
export class OmniSynthVoice {
    osc1: SynthOscillatorNode;
    osc2: SynthOscillatorNode;
    masterGain: SynthGainNode;
    output: SynthDestinationOut;

    constructor(freq: number) {
        // Instantiating the web audio nodes
        this.osc1 = new SynthOscillatorNode("sawtooth", freq);
        this.osc2 = new SynthOscillatorNode("square", freq / 2); // Sub-oscillator
        this.masterGain = new SynthGainNode();
        this.output = new SynthDestinationOut();

        // THE SYNTHESIS ROUTING GRAPH CHAIN:
        // Osc 1 -->
        //            MasterGain --> Speakers
        // Osc 2 -->
        
        this.osc1.connect(this.masterGain);
        this.osc2.connect(this.masterGain);
        this.masterGain.connect(this.output);
    }

    triggerAttack() {
        this.masterGain.gain = 1.0; // Simulated ADSR trigger
    }

    triggerRelease() {
        this.masterGain.gain = 0.0;
    }

    diagnostics(): object {
        return {
            engine: "OmniAwesomeWebaudioEngine",
            layer: "TypeScript UI Synth Architecture",
            nodes_allocated: 4,
            routing_graph: "Osc1+Osc2 -> MasterGain -> Destination",
            learned_logic: ["advanced-webaudio-routing", "synth-voice-encapsulation", "typescript-node-interfaces"]
        };
    }
}

// ---------------------------------------------------------------------------
// Execution Entry
// ---------------------------------------------------------------------------
if (require.main === module) {
    const voiceA = new OmniSynthVoice(440.0); // 440hz Tone (A4)
    voiceA.triggerAttack();
    
    console.log(JSON.stringify(voiceA.diagnostics(), null, 2));
}
