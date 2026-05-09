-- OmniParsers.hs — Monadic Parser Combinators
-- Layer: Functional / Haskell
--
-- Purely functional monadic parsers for parsing custom configuration files
-- or DSLs safely, without using regex, ensuring correctness for OMNI routing.

module OmniParsers (
    Parser,
    parse,
    item,
    satisfy,
    char,
    string,
    many,
    many1,
    space,
    spaces,
    integer
) where

import Control.Applicative
import Data.Char (isDigit, isSpace)

-- A parser takes a string and returns a list of (result, remaining_string)
newtype Parser a = Parser { parse :: String -> [(a, String)] }

instance Functor Parser where
    fmap f p = Parser $ \s -> [(f a, s') | (a, s') <- parse p s]

instance Applicative Parser where
    pure a = Parser $ \s -> [(a, s)]
    pf <*> pa = Parser $ \s -> [(f a, s'') | (f, s') <- parse pf s, (a, s'') <- parse pa s']

instance Monad Parser where
    return = pure
    p >>= f = Parser $ \s -> concat [parse (f a) s' | (a, s') <- parse p s]

instance Alternative Parser where
    empty = Parser $ \_ -> []
    p1 <|> p2 = Parser $ \s -> case parse p1 s of
                                [] -> parse p2 s
                                res -> res

-- Basic combinators

item :: Parser Char
item = Parser $ \s -> case s of
                        [] -> []
                        (c:cs) -> [(c, cs)]

satisfy :: (Char -> Bool) -> Parser Char
satisfy p = do
    c <- item
    if p c then return c else empty

char :: Char -> Parser Char
char c = satisfy (== c)

string :: String -> Parser String
string [] = return []
string (c:cs) = do
    _ <- char c
    _ <- string cs
    return (c:cs)

many1 :: Parser a -> Parser [a]
many1 p = do
    a <- p
    as <- many p
    return (a:as)

space :: Parser Char
space = satisfy isSpace

spaces :: Parser ()
spaces = do
    _ <- many space
    return ()

integer :: Parser Int
integer = do
    digits <- many1 (satisfy isDigit)
    return (read digits)

-- Example usage:
-- parseConfig :: Parser (String, Int)
-- parseConfig = do
--    _ <- string "threads="
--    n <- integer
--    return ("threads", n)
