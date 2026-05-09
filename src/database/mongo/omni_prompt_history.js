// OMNI Framework - MongoDB Schema for Prompt History
// Stores user interactions for auditing and RLHF (Reinforcement Learning from Human Feedback)

const mongoose = require('mongoose');

const promptHistorySchema = new mongoose.Schema({
    tenant_id: { 
        type: String, 
        required: true, 
        index: true 
    },
    user_id: { 
        type: String, 
        required: true 
    },
    model_id: { 
        type: String, 
        required: true 
    },
    prompt_text: { 
        type: String, 
        required: true 
    },
    completion_text: { 
        type: String, 
        required: true 
    },
    input_tokens: { type: Number, default: 0 },
    output_tokens: { type: Number, default: 0 },
    
    // Fields for RLHF
    user_rating: { 
        type: Number, 
        min: 1, 
        max: 5, 
        default: null 
    },
    feedback_notes: { 
        type: String, 
        default: null 
    },
    
    timestamp: { 
        type: Date, 
        default: Date.now,
        expires: 31536000 // Automatically delete after 1 year (Data retention policy)
    }
});

// Index for fast querying by tenant and date
promptHistorySchema.index({ tenant_id: 1, timestamp: -1 });

const PromptHistory = mongoose.model('PromptHistory', promptHistorySchema);

module.exports = PromptHistory;
