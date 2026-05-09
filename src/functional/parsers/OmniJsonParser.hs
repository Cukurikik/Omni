-- OmniJsonParser.hs — Pure Haskell JSON AST Parser
-- Layer: Functional / Haskell
--
-- Purely functional JSON parser utilizing the OmniParsers combinator library
-- to safely deserialize configurations without external C-bindings.

module OmniJsonParser where

import OmniParsers
import Data.Char (isDigit, isLetter, isSpace)

-- | Abstract Syntax Tree for JSON
data JValue 
    = JNull
    | JBool Bool
    | JNumber Double
    | JString String
    | JArray [JValue]
    | JObject [(String, JValue)]
    deriving (Show, Eq)

-- Combinators
jsonNull :: Parser JValue
jsonNull = string "null" >> return JNull

jsonBool :: Parser JValue
jsonBool = (string "true" >> return (JBool True))
       <|> (string "false" >> return (JBool False))

-- Simplified string parsing (ignoring escapes for brevity)
jsonString :: Parser String
jsonString = do
    _ <- char '"'
    s <- many (satisfy (/= '"'))
    _ <- char '"'
    return s

jsonJString :: Parser JValue
jsonJString = JString <$> jsonString

-- Simplified number parsing
jsonNumber :: Parser JValue
jsonNumber = do
    s <- many1 (satisfy (\c -> isDigit c || c == '.' || c == '-'))
    return $ JNumber (read s)

jsonArray :: Parser JValue
jsonArray = do
    _ <- char '['
    spaces
    vs <- elements <|> return []
    spaces
    _ <- char ']'
    return $ JArray vs
  where
    elements = do
        v <- jsonValue
        spaces
        (char ',' >> spaces >> elements >>= \vs -> return (v:vs)) <|> return [v]

jsonObject :: Parser JValue
jsonObject = do
    _ <- char '{'
    spaces
    kvs <- members <|> return []
    spaces
    _ <- char '}'
    return $ JObject kvs
  where
    members = do
        k <- jsonString
        spaces
        _ <- char ':'
        spaces
        v <- jsonValue
        spaces
        (char ',' >> spaces >> members >>= \m -> return ((k,v):m)) <|> return [(k,v)]

jsonValue :: Parser JValue
jsonValue = jsonNull <|> jsonBool <|> jsonJString <|> jsonNumber <|> jsonArray <|> jsonObject

-- | Entry point for parsing a JSON string
parseJson :: String -> Either String JValue
parseJson input = case parse (spaces >> jsonValue >>= \v -> spaces >> return v) input of
    [(val, "")] -> Right val
    [(_, rest)] -> Left $ "Incomplete parse. Remaining: " ++ take 20 rest
    _           -> Left "Failed to parse JSON"
