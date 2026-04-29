-- Awesome-LLM4IE — Information Extraction Pipeline (Haskell)
module LLM4IEPipeline where

data OmniResult a = Ok a | Err String deriving (Show)

data Entity = Entity { entityText :: String, entityType :: String, startPos :: Int, endPos :: Int } deriving (Show)

extractEntities :: String -> [String] -> OmniResult [Entity]
extractEntities text entityTypes
  | null text = Err "Empty input text"
  | length text > 100000 = Err "Text exceeds 100K chars"
  | null entityTypes = Err "No entity types specified"
  | otherwise = Ok $ concatMap (findEntitiesOfType text) entityTypes

findEntitiesOfType :: String -> String -> [Entity]
findEntitiesOfType text eType =
  let ws = words text
      positions = scanl (\acc w -> acc + length w + 1) 0 ws
  in [ Entity w eType p (p + length w)
     | (w, p) <- zip ws positions
     , length w > 3 ]

computeF1 :: Int -> Int -> Int -> OmniResult Double
computeF1 tp fp fn
  | tp < 0 || fp < 0 || fn < 0 = Err "Negative counts"
  | tp + fp == 0 = Err "Zero precision denominator"
  | tp + fn == 0 = Err "Zero recall denominator"
  | otherwise = let prec = fromIntegral tp / fromIntegral (tp + fp)
                    rec = fromIntegral tp / fromIntegral (tp + fn)
                    f1 = 2.0 * prec * rec / (prec + rec)
                in Ok f1
