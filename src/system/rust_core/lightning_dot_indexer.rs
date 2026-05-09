pub struct LightningIndexer {
    is_ready: bool,
}

impl LightningIndexer {
    pub fn build_index(&mut self) -> Result<(), String> {
        self.is_ready = true;
        Ok(())
    }
}
