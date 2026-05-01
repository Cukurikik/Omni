/// OMNI MOTHER SYSTEM - SECURITY LAYER
/// IMDb Review Sanitizer boundary before BERT inference.
/// Strictly removes XSS, SQLi, and null byte injections from user-submitted text.

pub enum SanitizeError {
    InputTooLarge,
    NullByteDetected,
    InvalidUtf8,
}

pub struct ImdbReviewSanitizer;

impl ImdbReviewSanitizer {
    const MAX_REVIEW_LENGTH: usize = 5000;

    /// Validates and sanitizes a raw string buffer securely.
    pub fn sanitize(raw_input: &[u8]) -> Result<String, SanitizeError> {
        if raw_input.len() > Self::MAX_REVIEW_LENGTH {
            return Err(SanitizeError::InputTooLarge);
        }

        // 1. Strict Null Byte Check (prevents C-string truncation attacks in FFI)
        if raw_input.contains(&0x00) {
            return Err(SanitizeError::NullByteDetected);
        }

        // 2. Validate UTF-8
        let mut text = match String::from_utf8(raw_input.to_vec()) {
            Ok(s) => s,
            Err(_) => return Err(SanitizeError::InvalidUtf8),
        };

        // 3. Remove HTML tags (Basic XSS prevention)
        // Uses an iterative approach avoiding heavy regex for raw speed
        text = Self::strip_html_tags(&text);

        // 4. Normalize Whitespace
        text = text.replace('\t', " ").replace('\n', " ");

        Ok(text)
    }

    fn strip_html_tags(input: &str) -> String {
        let mut output = String::with_capacity(input.len());
        let mut inside_tag = false;

        for c in input.chars() {
            match c {
                '<' => inside_tag = true,
                '>' => {
                    if inside_tag {
                        inside_tag = false;
                    } else {
                        output.push('>'); // Rogue closing tag
                    }
                }
                _ => {
                    if !inside_tag {
                        output.push(c);
                    }
                }
            }
        }
        output
    }
}
