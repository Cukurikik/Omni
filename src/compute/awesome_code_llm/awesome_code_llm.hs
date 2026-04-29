module AwesomeCodeLLM where

-- Awesome Code LLM — Code understanding metrics
-- Pure functional code complexity analyzer

data OmniResult a e = Ok a | Err e deriving (Show)

data CodeMetrics = CodeMetrics
  { totalLines :: Int
  , codeLines :: Int
  , commentLines :: Int
  , blankLines :: Int
  , cyclomaticComplexity :: Int
  } deriving (Show)

maxLines :: Int
maxLines = 1000000

analyzeCode :: String -> OmniResult CodeMetrics String
analyzeCode source
  | null source = Err "Empty source code"
  | lineCount > maxLines = Err ("Exceeds " ++ show maxLines ++ " line limit")
  | otherwise = Ok CodeMetrics
      { totalLines = lineCount
      , codeLines = length (filter (not . isBlankOrComment) ls)
      , commentLines = length (filter isComment ls)
      , blankLines = length (filter null ls)
      , cyclomaticComplexity = 1 + countBranches source
      }
  where
    ls = lines source
    lineCount = length ls
    isBlankOrComment l = null (trim l) || isComment l
    isComment l = case dropWhile (== ' ') l of
                    ('/':'/':_) -> True
                    ('#':_)     -> True
                    _           -> False
    trim = reverse . dropWhile (== ' ') . reverse . dropWhile (== ' ')
    countBranches s = length (filter (`elem` ["if","for","while","case","catch","&&","||"]) (words s))
