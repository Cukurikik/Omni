module AwesomeLLMRAG where

-- Awesome LLM RAG — Pure functional retrieval pipeline
-- Haskell pure monadic pipeline

data OmniResult a e = Ok a | Err e deriving (Show)

data Document = Document { docId :: String, docContent :: String, docScore :: Double } deriving (Show)

maxDocLen :: Int
maxDocLen = 1000000

maxChunkSize :: Int
maxChunkSize = 2048

chunkDocument :: String -> Int -> OmniResult [String] String
chunkDocument content chunkSize
  | null content = Err "Empty document"
  | chunkSize <= 0 || chunkSize > maxChunkSize = Err "Invalid chunk size"
  | length content > maxDocLen = Err "Document exceeds 1MB"
  | otherwise = Ok (go content)
  where
    go [] = []
    go s  = take chunkSize s : go (drop chunkSize s)

computeRelevanceScore :: [Double] -> [Double] -> OmniResult Double String
computeRelevanceScore query doc
  | length query /= length doc = Err "Dimension mismatch"
  | null query = Err "Empty embedding"
  | otherwise = let dot = sum (zipWith (*) query doc)
                    normQ = sqrt (sum (map (^2) query))
                    normD = sqrt (sum (map (^2) doc))
                in if normQ == 0 || normD == 0 then Err "Zero-norm vector"
                   else Ok (dot / (normQ * normD))
