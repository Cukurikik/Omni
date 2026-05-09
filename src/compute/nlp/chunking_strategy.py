#=============================================================================
# OMNI COMPUTE LAYER — RAG CHUNKING STRATEGY (PYTHON)
# BATCH: 31 | SEMESTER: 16
# DESCRIPTION: Advanced semantic chunking for RAG pipelines.
#=============================================================================

import re
from typing import List
import omni_bridge.domain.error as err

class SemanticChunker:
    """
    Chunks large documents intelligently based on semantic boundaries 
    rather than naive character counts.
    """
    def __init__(self, max_chunk_size: int = 512, overlap: int = 50):
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap

    def chunk_document(self, text: str) -> err.Result[List[str]]:
        if not text:
            return err.Err("Document text is empty")
            
        try:
            # 1. Split by paragraphs
            paragraphs = re.split(r'\n\s*\n', text)
            
            chunks = []
            current_chunk = []
            current_length = 0
            
            for p in paragraphs:
                p_len = len(p.split())
                
                if current_length + p_len > self.max_chunk_size:
                    if current_chunk:
                        chunks.append(" ".join(current_chunk))
                        
                        # Handle overlap
                        overlap_words = " ".join(current_chunk).split()[-self.overlap:]
                        current_chunk = [" ".join(overlap_words), p]
                        current_length = len(overlap_words) + p_len
                    else:
                        # Paragraph itself is larger than max_chunk_size
                        chunks.append(p)
                else:
                    current_chunk.append(p)
                    current_length += p_len
                    
            if current_chunk:
                chunks.append(" ".join(current_chunk))
                
            return err.Ok(chunks)
        except Exception as e:
            return err.Err(f"Chunking failed: {str(e)}")
