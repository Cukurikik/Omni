use std::collections::HashMap;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum FeatureStatus {
    Draft,
    Experimental,
    Stable,
    Deprecated,
}

#[derive(Debug, Clone)]
pub struct LanguageFeature {
    pub id: &'static str,
    pub description: &'static str,
    pub status: FeatureStatus,
    pub min_omni_version: &'static str,
}

pub struct RFCRegistry {
    features: HashMap<&'static str, LanguageFeature>,
}

impl RFCRegistry {
    pub fn new() -> Self {
        let mut registry = Self {
            features: HashMap::new(),
        };

        // Register core Phase 9 features
        registry.register(LanguageFeature {
            id: "rfc-001-abi-stability",
            description: "Binary stability layer and 15-target bridge",
            status: FeatureStatus::Stable,
            min_omni_version: "1.0",
        });

        registry.register(LanguageFeature {
            id: "rfc-002-formal-verification",
            description: "Compile-time Design by Contract verification",
            status: FeatureStatus::Stable,
            min_omni_version: "1.0",
        });

        registry.register(LanguageFeature {
            id: "rfc-003-quantum-jit",
            description: "Machine-learning driven JIT compilation",
            status: FeatureStatus::Experimental,
            min_omni_version: "1.1",
        });
        
        registry.register(LanguageFeature {
            id: "rfc-004-legacy-assimilation",
            description: "AST-based ingestion of Java/C#/TS/etc.",
            status: FeatureStatus::Draft,
            min_omni_version: "1.2",
        });

        registry
    }

    fn register(&mut self, feature: LanguageFeature) {
        self.features.insert(feature.id, feature);
    }

    /// Compiler gate: Checks if a feature is allowed in the current build context
    pub fn check_feature_flag(&self, feature_id: &str, allow_experimental: bool) -> Result<(), String> {
        let feature = self.features.get(feature_id).ok_or_else(|| format!("Uknown language feature: {}", feature_id))?;
        
        match feature.status {
            FeatureStatus::Stable => Ok(()),
            FeatureStatus::Experimental => {
                if allow_experimental {
                    Ok(())
                } else {
                    Err(format!("Feature '{}' is Experimental. You must pass `--enable-experimental=true`.", feature_id))
                }
            },
            FeatureStatus::Draft => {
                // Draft features are completely rejected in normal builds
                Err(format!("Feature '{}' is still in Draft status! It is not ready for assimilation.", feature_id))
            },
            FeatureStatus::Deprecated => {
                // Warn but allow
                println!("⚠️ WARNING: Feature '{}' is Deprecated.", feature_id);
                Ok(())
            }
        }
    }
}
