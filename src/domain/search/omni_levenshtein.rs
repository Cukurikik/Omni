// omni_levenshtein.rs — Levenshtein Distance
// Layer: Domain / Rust
//
// Fast implementation of the Levenshtein (edit) distance algorithm
// utilizing two-row memory optimization instead of a full O(N*M) matrix.
// Critical for fuzzy string matching in the search engine. Zero mock.

use std::cmp::min;

pub struct OmniLevenshtein;

impl OmniLevenshtein {
    /// Computes the edit distance between two strings using O(min(N, M)) memory.
    pub fn distance(s1: &str, s2: &str) -> usize {
        let mut chars1: Vec<char> = s1.chars().collect();
        let mut chars2: Vec<char> = s2.chars().collect();

        // Optimization: Ensure chars1 is the shorter sequence to save memory
        if chars1.len() > chars2.len() {
            std::mem::swap(&mut chars1, &mut chars2);
        }

        let len1 = chars1.len();
        let len2 = chars2.len();

        if len1 == 0 {
            return len2;
        }

        // We only need two rows of the dynamic programming matrix
        let mut prev_row: Vec<usize> = (0..=len1).collect();
        let mut curr_row: Vec<usize> = vec![0; len1 + 1];

        for i in 1..=len2 {
            curr_row[0] = i;
            let char2 = chars2[i - 1];

            for j in 1..=len1 {
                let cost = if chars1[j - 1] == char2 { 0 } else { 1 };
                
                let deletion = prev_row[j] + 1;
                let insertion = curr_row[j - 1] + 1;
                let substitution = prev_row[j - 1] + cost;

                curr_row[j] = min(deletion, min(insertion, substitution));
            }

            // Swap rows
            std::mem::swap(&mut prev_row, &mut curr_row);
        }

        // Because we swapped at the end of the loop, the result is in prev_row
        prev_row[len1]
    }
}
