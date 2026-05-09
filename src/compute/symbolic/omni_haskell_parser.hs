module Omni.Parser (parseEquation) where

import Text.Parsec
import Text.Parsec.String (Parser)
import Text.Parsec.Expr
import Text.Parsec.Token as Token
import Text.Parsec.Language (emptyDef)

-- Omni Haskell AST Parser (Haskell)
-- Functional Layer
-- Purely functional deterministic parser to construct Abstract Syntax Trees
-- for the OmniTPSRPlanner (Symbolic Regression engine).

data Expr
    = Var String
    | Con Double
    | Add Expr Expr
    | Sub Expr Expr
    | Mul Expr Expr
    | Div Expr Expr
    deriving (Show, Eq)

languageDef :: LanguageDef st
languageDef = emptyDef
    { Token.identStart      = letter
    , Token.identLetter     = alphaNum
    , Token.reservedNames   = []
    , Token.reservedOpNames = ["+", "-", "*", "/"]
    }

lexer :: Token.TokenParser st
lexer = Token.makeTokenParser languageDef

identifier :: Parser String
identifier = Token.identifier lexer

reservedOp :: String -> Parser ()
reservedOp = Token.reservedOp lexer

parens :: Parser a -> Parser a
parens = Token.parens lexer

float :: Parser Double
float = Token.float lexer <|> (fromIntegral <$> Token.integer lexer)

expr :: Parser Expr
expr = buildExpressionParser table term
  where
    table =
        [ [ Infix (reservedOp "*" >> return Mul) AssocLeft
          , Infix (reservedOp "/" >> return Div) AssocLeft
          ]
        , [ Infix (reservedOp "+" >> return Add) AssocLeft
          , Infix (reservedOp "-" >> return Sub) AssocLeft
          ]
        ]
    term = parens expr
       <|> (Con <$> float)
       <|> (Var <$> identifier)

-- | Parses a mathematical string into an Omni AST.
parseEquation :: String -> Either ParseError Expr
parseEquation = parse (expr <* eof) ""
