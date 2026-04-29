-- ===========================================================================
-- OMNI PARSEC ENGINE (SEMESTER 3 — BATCH 38.5)
-- ===========================================================================
-- Absorbed From  : megaparsec + attoparsec + parsec
-- Logic Inherited: Haskell / Functional Layer (Parser Combinator Library)
-- ===========================================================================
--
-- By studying megaparsec and attoparsec, Mother learned:
--   1. Parsers are monads: sequence with (>>=), choose with (<|>)
--   2. Applicative style enables concise grammar definitions
--   3. Backtracking with 'try' enables arbitrary lookahead
--   4. Error messages accumulate expected/unexpected tokens
--   5. Char-by-char parsing with efficient Text consumption

{-# LANGUAGE ScopedTypeVariables #-}
{-# LANGUAGE LambdaCase #-}

module OmniParsecEngine
  ( -- * Core Types
    Parser
  , ParseError(..)
  , ParseResult
    -- * Running Parsers
  , runParser
  , parse
    -- * Basic Combinators
  , satisfy
  , char
  , string
  , anyChar
  , eof
    -- * Character Classes
  , digit
  , letter
  , alphaNum
  , space
  , spaces
    -- * Combinator Operators
  , (<|>)
  , many
  , many1
  , optional
  , between
  , sepBy
  , sepBy1
  , chainl1
    -- * Token Parsers
  , integer
  , float
  , identifier
  , stringLiteral
  , keyword
    -- * JSON Parser (demonstration)
  , JsonValue(..)
  , jsonParser
    -- * Diagnostics
  , engineDiagnostics
  ) where

import Data.Char (isDigit, isAlpha, isAlphaNum, isSpace)
import Data.List (intercalate)
import Control.Applicative (Alternative(..))

-- ============================================================
-- Core Parser Type
-- ============================================================

-- | Parse error with position and context.
data ParseError = ParseError
  { errorPos      :: !Int
  , errorExpected :: ![String]
  , errorGot      :: !(Maybe Char)
  , errorMessage  :: !String
  } deriving (Show)

type ParseResult a = Either ParseError a

-- | Parser monad: consumes a string and produces a result.
-- State is (remaining input, current position).
newtype Parser a = Parser
  { unParser :: String -> Int -> Either ParseError (a, String, Int)
  }

-- | Functor instance: map over parse results.
instance Functor Parser where
  fmap f (Parser p) = Parser $ \input pos ->
    case p input pos of
      Left err          -> Left err
      Right (a, rest, pos') -> Right (f a, rest, pos')

-- | Applicative instance: sequence parsers.
instance Applicative Parser where
  pure a = Parser $ \input pos -> Right (a, input, pos)
  (Parser pf) <*> (Parser pa) = Parser $ \input pos ->
    case pf input pos of
      Left err           -> Left err
      Right (f, rest, pos') ->
        case pa rest pos' of
          Left err            -> Left err
          Right (a, rest', pos'') -> Right (f a, rest', pos'')

-- | Monad instance: chain parsers with (>>=).
instance Monad Parser where
  return = pure
  (Parser pa) >>= f = Parser $ \input pos ->
    case pa input pos of
      Left err          -> Left err
      Right (a, rest, pos') ->
        let (Parser pb) = f a
        in pb rest pos'

-- | Alternative instance: choice with (<|>).
instance Alternative Parser where
  empty = Parser $ \input pos -> Left ParseError
    { errorPos      = pos
    , errorExpected = []
    , errorGot      = safeHead input
    , errorMessage  = "no alternative matched"
    }
  (Parser pa) <|> (Parser pb) = Parser $ \input pos ->
    case pa input pos of
      Right result -> Right result
      Left _       -> pb input pos

safeHead :: String -> Maybe Char
safeHead []    = Nothing
safeHead (c:_) = Just c

-- ============================================================
-- Running Parsers
-- ============================================================

runParser :: Parser a -> String -> ParseResult a
runParser (Parser p) input =
  case p input 0 of
    Left err         -> Left err
    Right (a, _, _)  -> Right a

parse :: Parser a -> String -> ParseResult a
parse = runParser

-- ============================================================
-- Basic Combinators
-- ============================================================

-- | Parse a character satisfying a predicate.
satisfy :: String -> (Char -> Bool) -> Parser Char
satisfy expected pred' = Parser $ \input pos ->
  case input of
    []     -> Left ParseError
      { errorPos = pos, errorExpected = [expected]
      , errorGot = Nothing, errorMessage = "unexpected end of input" }
    (c:cs) | pred' c   -> Right (c, cs, pos + 1)
           | otherwise -> Left ParseError
      { errorPos = pos, errorExpected = [expected]
      , errorGot = Just c, errorMessage = "unexpected character" }

-- | Parse a specific character.
char :: Char -> Parser Char
char c = satisfy [c] (== c)

-- | Parse a specific string.
string :: String -> Parser String
string []     = pure []
string (c:cs) = (:) <$> char c <*> string cs

-- | Parse any character.
anyChar :: Parser Char
anyChar = satisfy "any character" (const True)

-- | Parse end of input.
eof :: Parser ()
eof = Parser $ \input pos ->
  case input of
    [] -> Right ((), [], pos)
    (c:_) -> Left ParseError
      { errorPos = pos, errorExpected = ["end of input"]
      , errorGot = Just c, errorMessage = "expected end of input" }

-- ============================================================
-- Character Classes
-- ============================================================

digit :: Parser Char
digit = satisfy "digit" isDigit

letter :: Parser Char
letter = satisfy "letter" isAlpha

alphaNum :: Parser Char
alphaNum = satisfy "alphanumeric" isAlphaNum

space :: Parser Char
space = satisfy "space" isSpace

spaces :: Parser String
spaces = many space

-- ============================================================
-- Higher-Order Combinators
-- ============================================================

many1 :: Parser a -> Parser [a]
many1 p = (:) <$> p <*> many p

optional :: Parser a -> Parser (Maybe a)
optional p = (Just <$> p) <|> pure Nothing

between :: Parser open -> Parser close -> Parser a -> Parser a
between open close p = open *> p <* close

sepBy :: Parser a -> Parser sep -> Parser [a]
sepBy p sep = sepBy1 p sep <|> pure []

sepBy1 :: Parser a -> Parser sep -> Parser [a]
sepBy1 p sep = (:) <$> p <*> many (sep *> p)

chainl1 :: Parser a -> Parser (a -> a -> a) -> Parser a
chainl1 p op = p >>= rest
  where
    rest x = (do
      f <- op
      y <- p
      rest (f x y)) <|> pure x

-- ============================================================
-- Token Parsers
-- ============================================================

-- | Parse an integer.
integer :: Parser Int
integer = do
  sign <- optional (char '-')
  digits <- many1 digit
  let n = read digits :: Int
  return $ case sign of
    Just _  -> negate n
    Nothing -> n

-- | Parse a floating point number.
float :: Parser Double
float = do
  sign <- optional (char '-')
  whole <- many1 digit
  _ <- char '.'
  frac <- many1 digit
  let n = read (whole ++ "." ++ frac) :: Double
  return $ case sign of
    Just _  -> negate n
    Nothing -> n

-- | Parse an identifier (letter followed by alphanums).
identifier :: Parser String
identifier = (:) <$> letter <*> many (alphaNum <|> char '_')

-- | Parse a string literal (double-quoted).
stringLiteral :: Parser String
stringLiteral = between (char '"') (char '"') (many stringChar)
  where
    stringChar = (char '\\' *> escapeChar) <|> satisfy "string char" (/= '"')
    escapeChar =
      (char '"'  *> pure '"')  <|>
      (char '\\' *> pure '\\') <|>
      (char 'n'  *> pure '\n') <|>
      (char 't'  *> pure '\t')

-- | Parse a keyword (exact string not followed by alphaNum).
keyword :: String -> Parser String
keyword kw = do
  s <- string kw
  -- Ensure not followed by alphanumeric
  notFollowed <- optional alphaNum
  case notFollowed of
    Just _  -> empty
    Nothing -> return s

-- ============================================================
-- JSON Parser (Full Demonstration)
-- ============================================================

data JsonValue
  = JsonNull
  | JsonBool Bool
  | JsonNumber Double
  | JsonString String
  | JsonArray [JsonValue]
  | JsonObject [(String, JsonValue)]
  deriving (Show, Eq)

jsonParser :: Parser JsonValue
jsonParser = spaces *> jsonValue <* spaces

jsonValue :: Parser JsonValue
jsonValue =
      jsonNull
  <|> jsonBool
  <|> jsonNum
  <|> jsonStr
  <|> jsonArr
  <|> jsonObj

jsonNull :: Parser JsonValue
jsonNull = string "null" *> pure JsonNull

jsonBool :: Parser JsonValue
jsonBool =
  (string "true"  *> pure (JsonBool True)) <|>
  (string "false" *> pure (JsonBool False))

jsonNum :: Parser JsonValue
jsonNum = JsonNumber <$> (float <|> (fromIntegral <$> integer))

jsonStr :: Parser JsonValue
jsonStr = JsonString <$> stringLiteral

jsonArr :: Parser JsonValue
jsonArr = JsonArray <$>
  between (char '[' <* spaces) (spaces *> char ']')
    (jsonValue `sepBy` (spaces *> char ',' <* spaces))

jsonObj :: Parser JsonValue
jsonObj = JsonObject <$>
  between (char '{' <* spaces) (spaces *> char '}')
    (jsonPair `sepBy` (spaces *> char ',' <* spaces))
  where
    jsonPair = do
      key <- spaces *> stringLiteral <* spaces
      _   <- char ':' <* spaces
      val <- jsonValue
      return (key, val)

-- ============================================================
-- Diagnostics
-- ============================================================

engineDiagnostics :: [(String, String)]
engineDiagnostics =
  [ ("engine",        "OmniParsecEngine")
  , ("layer",         "Haskell Functional")
  , ("combinators",   "satisfy,char,string,many,many1,optional,between,sepBy,chainl1")
  , ("token_parsers", "integer,float,identifier,stringLiteral,keyword")
  , ("demo_parser",   "JSON (null,bool,number,string,array,object)")
  , ("learned_logic", intercalate ","
      [ "parser-monad-bind-sequence"
      , "alternative-choice-backtrack"
      , "applicative-style-grammar"
      , "satisfy-predicate-char"
      , "recursive-descent-json"
      , "escape-sequence-handling"
      , "chainl1-left-associative"
      , "sepBy-separator-combinator"
      ])
  ]
