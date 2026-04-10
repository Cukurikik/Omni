use std::fmt;

#[derive(Debug, Clone)]
pub enum SystemError {
    Connection(String), Timeout(u64), Auth(String), Protocol(String),
    ResourceExhausted, NotFound(String), AlreadyExists(String),
    PermissionDenied(String), Internal(String), Unavailable(String),
}

impl fmt::Display for SystemError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            Self::Connection(s) => write!(f, "Connection error: {}", s),
            Self::Timeout(ms) => write!(f, "Timeout after {}ms", ms),
            Self::Auth(s) => write!(f, "Auth failed: {}", s),
            Self::Protocol(s) => write!(f, "Protocol error: {}", s),
            Self::ResourceExhausted => write!(f, "Resource exhausted"),
            Self::NotFound(s) => write!(f, "Not found: {}", s),
            Self::AlreadyExists(s) => write!(f, "Already exists: {}", s),
            Self::PermissionDenied(s) => write!(f, "Permission denied: {}", s),
            Self::Internal(s) => write!(f, "Internal error: {}", s),
            Self::Unavailable(s) => write!(f, "Service unavailable: {}", s),
        }
    }
}

pub type SystemResult<T> = Result<T, SystemError>;

pub struct ErrorChain { errors: Vec<SystemError> }
impl ErrorChain {
    pub fn new() -> Self { Self { errors: vec![] } }
    pub fn push(&mut self, e: SystemError) { self.errors.push(e); }
    pub fn root_cause(&self) -> Option<&SystemError> { self.errors.first() }
    pub fn latest(&self) -> Option<&SystemError> { self.errors.last() }
    pub fn len(&self) -> usize { self.errors.len() }
}