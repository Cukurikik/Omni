// moe_ava_avatar_bridge.js — Interface / UI
// Layer: Interface / Frontend — Live2D Avatar Bridge
//
// Inspired by `avamoe/ava.moe`.
// As the MoE generates tokens, this bridge translates the emotional sentiment
// of the text into Live2D/PixiJS animation parameters, allowing an anime avatar
// to dynamically react (smile, frown, act confused) in real-time.

export class AvaMoeBridge {
    constructor(pixiApp, live2dModel) {
        this.app = pixiApp;
        this.model = live2dModel;
        console.log("[Ava.Moe Bridge] Initialized Live2D Avatar Synchronizer.");
    }

    /**
     * Processes an incoming token stream and adjusts the avatar's expression.
     * @param {string} token - The newly generated word/subword.
     * @param {number} entropy - The Shannon entropy of the token (high = confused).
     */
    processTokenStream(token, entropy) {
        const lowerToken = token.toLowerCase();

        // 1. Emotion Triggers based on vocabulary
        if (lowerToken.includes("happy") || lowerToken.includes("excellent")) {
            this.setExpression("Smile");
        } else if (lowerToken.includes("error") || lowerToken.includes("sorry")) {
            this.setExpression("Sad");
        } else if (lowerToken.includes("warning")) {
            this.setExpression("Surprise");
        }

        // 2. Entropy-driven confusion (If the model is unsure of its prediction)
        if (entropy > 4.5) {
            this.setExpression("Confused");
            this.model.internalModel.coreModel.setParameterValueById("ParamCheek", 1.0); // Blush/Sweat
        } else {
            this.model.internalModel.coreModel.setParameterValueById("ParamCheek", 0.0);
        }

        // 3. Lip Sync Simulation
        // Open mouth slightly on vowels
        if (/[aeiou]/.test(lowerToken)) {
            this.model.internalModel.coreModel.setParameterValueById("ParamMouthOpenY", 0.8);
        } else {
            this.model.internalModel.coreModel.setParameterValueById("ParamMouthOpenY", 0.0);
        }
    }

    setExpression(expressionName) {
        if (!this.model) return;
        // console.log(`[Ava.Moe] Setting expression: ${expressionName}`);
        this.model.expressionManager.setExpression(expressionName);
    }
}
