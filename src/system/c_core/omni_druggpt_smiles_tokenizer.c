/* Omni DrugGPT SMILES Tokenizer (C) */
/* System: Fast SMILES string tokenization. */
/* Ref: LIYUESEN/druggpt */
#include <stddef.h>
int omni_smiles_tokenize(const char* smiles, int* tokens, int max_tokens) {
    int count = 0; size_t i = 0;
    while (smiles[i] && count < max_tokens) {
        if (smiles[i] >= 'A' && smiles[i] <= 'Z') { tokens[count++] = (int)smiles[i]; }
        else if (smiles[i] >= 'a' && smiles[i] <= 'z') { tokens[count++] = (int)smiles[i] + 100; }
        else if (smiles[i] >= '0' && smiles[i] <= '9') { tokens[count++] = (int)smiles[i] + 200; }
        else { tokens[count++] = (int)smiles[i] + 300; }
        i++;
    }
    return count;
}
