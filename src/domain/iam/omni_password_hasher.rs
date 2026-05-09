// omni_password_hasher.rs — Argon2 Password Hashing
// Layer: Domain / IAM
//
// Implements secure password hashing and verification using the Argon2id 
// algorithm, resistant to GPU cracking and side-channel attacks. Zero mock.

use argon2::{
    password_hash::{
        rand_core::OsRng,
        PasswordHash, PasswordHasher, PasswordVerifier, SaltString
    },
    Argon2, Algorithm, Version, Params
};

pub struct OmniPasswordHasher {
    argon2: Argon2<'static>,
}

impl OmniPasswordHasher {
    /// Initializes the Argon2id hasher with OMNI's strict security parameters.
    pub fn new() -> Self {
        // Strict parameters: 64MB memory, 3 iterations, 4 parallel lanes
        let params = Params::new(65536, 3, 4, None).unwrap();
        
        let argon2 = Argon2::new(
            Algorithm::Argon2id,
            Version::V0x13,
            params
        );
        
        OmniPasswordHasher { argon2 }
    }

    /// Hashes a plaintext password into an Argon2id string.
    pub fn hash_password(&self, password: &str) -> Result<String, &'static str> {
        let salt = SaltString::generate(&mut OsRng);
        
        let password_hash = self.argon2
            .hash_password(password.as_bytes(), &salt)
            .map_err(|_| "Failed to generate password hash")?;
            
        Ok(password_hash.to_string())
    }

    /// Verifies a plaintext password against a previously generated Argon2id hash.
    pub fn verify_password(&self, password: &str, hash_str: &str) -> bool {
        let parsed_hash = match PasswordHash::new(hash_str) {
            Ok(ph) => ph,
            Err(_) => return false,
        };
        
        self.argon2.verify_password(password.as_bytes(), &parsed_hash).is_ok()
    }
}
