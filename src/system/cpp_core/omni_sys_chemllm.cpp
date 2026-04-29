#include <cstdint>

extern "C" {
    // SMILES string validation heuristic (bracket matching)
    bool chemllm_validate_smiles_brackets(const char* smiles, uint32_t length) {
        int32_t balance = 0;
        int32_t ring_balance = 0;
        
        for (uint32_t i = 0; i < length; ++i) {
            if (smiles[i] == '(') balance++;
            else if (smiles[i] == ')') balance--;
            
            if (smiles[i] == '[') ring_balance++;
            else if (smiles[i] == ']') ring_balance--;
            
            if (balance < 0 || ring_balance < 0) return false;
        }
        
        return balance == 0 && ring_balance == 0;
    }
}
