/// @omni-layer System | @omni-source vllm-project/vllm | @omni-lang Rust
/// @omni-description Paged attention block table: maps virtual to physical KV blocks.
#[derive(Debug)]
pub enum PageError { BlockNotFound(usize), TableFull }
pub type OmniResult<T> = Result<T, PageError>;

pub struct BlockTable {
    virtual_to_physical: Vec<Option<usize>>,
    physical_free: Vec<usize>,
    max_blocks: usize,
}
impl BlockTable {
    pub fn new(max_virtual: usize, max_physical: usize) -> Self {
        Self { virtual_to_physical: vec![None; max_virtual], physical_free: (0..max_physical).collect(), max_blocks: max_physical }
    }
    pub fn allocate(&mut self, virtual_id: usize) -> OmniResult<usize> {
        if self.physical_free.is_empty() { return Err(PageError::TableFull); }
        let phys = self.physical_free.pop().unwrap();
        if virtual_id < self.virtual_to_physical.len() { self.virtual_to_physical[virtual_id] = Some(phys); }
        Ok(phys)
    }
    pub fn translate(&self, virtual_id: usize) -> OmniResult<usize> {
        self.virtual_to_physical.get(virtual_id).and_then(|v| *v).ok_or(PageError::BlockNotFound(virtual_id))
    }
    pub fn free(&mut self, virtual_id: usize) -> OmniResult<()> {
        if let Some(phys) = self.virtual_to_physical.get(virtual_id).and_then(|v| *v) {
            self.physical_free.push(phys);
            self.virtual_to_physical[virtual_id] = None;
            Ok(())
        } else { Err(PageError::BlockNotFound(virtual_id)) }
    }
    pub fn stats(&self) -> (usize, usize) { (self.max_blocks - self.physical_free.len(), self.physical_free.len()) }
}
