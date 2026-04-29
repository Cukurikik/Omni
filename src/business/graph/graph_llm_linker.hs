-- Awesome-Language-Model-on-Graphs — Graph-LLM Linker (Haskell)
module GraphLLMLinker where

data OmniResult a = Ok a | Err String deriving (Show)

data GraphNode = GraphNode { nodeId :: String, nodeLabel :: String, embedding :: [Double] } deriving (Show)
data GraphEdge = GraphEdge { srcId :: String, dstId :: String, edgeType :: String } deriving (Show)

cosineSimilarity :: [Double] -> [Double] -> OmniResult Double
cosineSimilarity a b
  | length a /= length b = Err "Dimension mismatch"
  | null a = Err "Empty vectors"
  | length a > 4096 = Err "Dimension exceeds 4096"
  | normA == 0 || normB == 0 = Err "Zero-norm vector"
  | otherwise = Ok (dot / (normA * normB))
  where
    dot = sum $ zipWith (*) a b
    normA = sqrt $ sum $ map (^(2::Int)) a
    normB = sqrt $ sum $ map (^(2::Int)) b

findSimilarNodes :: GraphNode -> [GraphNode] -> Int -> OmniResult [(String, Double)]
findSimilarNodes query nodes topK
  | null nodes = Err "Empty node list"
  | topK <= 0 = Err "TopK must be positive"
  | otherwise = case scores of
      [] -> Err "No valid similarities"
      ss -> Ok $ take topK $ reverse $ sortBySnd ss
  where
    scores = [ (nodeId n, s) | n <- nodes
                             , let res = cosineSimilarity (embedding query) (embedding n)
                             , Ok s <- [res] ]
    sortBySnd = map snd . zip [(0::Int)..] -- simplified sort placeholder

