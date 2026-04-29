// OMNI MOTHER - DIVINE MEMORY INTEGRATION
// Qdrant Vector DB (OMNI Zero-Mock Implementation)
// Implements Payload Filter mathematical boundary bounds.

pub struct ResultT<T> {
    pub value: Option<T>,
    pub is_ok: bool,
    pub error: String,
}

pub struct FloatRange {
    pub gt: Option<f64>,
    pub gte: Option<f64>,
    pub lt: Option<f64>,
    pub lte: Option<f64>,
}

pub struct PayloadFilterEngine;

impl PayloadFilterEngine {
    // Validates a payload value mathematically against a Qdrant-like boundary filter definition
    pub fn match_range_filter(value: f64, range_bound: &FloatRange) -> ResultT<bool> {
        if let Some(v_gt) = range_bound.gt {
             if value <= v_gt {
                 return ResultT { value: Some(false), is_ok: true, error: "".to_string() };
             }
        }
        
        if let Some(v_gte) = range_bound.gte {
             if value < v_gte {
                 return ResultT { value: Some(false), is_ok: true, error: "".to_string() };
             }
        }
        
        if let Some(v_lt) = range_bound.lt {
             if value >= v_lt {
                 return ResultT { value: Some(false), is_ok: true, error: "".to_string() };
             }
        }
        
        if let Some(v_lte) = range_bound.lte {
             if value > v_lte {
                 return ResultT { value: Some(false), is_ok: true, error: "".to_string() };
             }
        }
        
        ResultT { value: Some(true), is_ok: true, error: "".to_string() }
    }
}
