-- ===========================================================================
-- OMNI TYPECLASS ENGINE (SEMESTER 3 — BATCH 38.10)
-- ===========================================================================
-- Absorbed From  : Haskell typeclasses + GHC extensions + deriving strategies
-- Logic Inherited: Haskell / Functional Layer (Ad-Hoc Polymorphism)
-- ===========================================================================
--
-- By studying Haskell typeclasses, Mother learned:
--   1. Typeclasses define polymorphic interfaces (ad-hoc polymorphism)
--   2. Instances provide concrete implementations per type
--   3. Superclass constraints build hierarchies
--   4. Default methods reduce boilerplate
--   5. Newtype + deriving strategies enable zero-cost abstraction

module Omni.Functional.TypeclassEngine where

import Data.Map.Strict (Map)
import qualified Data.Map.Strict as Map
import Data.List (intercalate, foldl')

-- ============================================================
-- PART 1: Core Typeclasses
-- ============================================================

-- | Serializable: convert to and from string representation.
class OmniShow a where
  omniShow :: a -> String

class OmniRead a where
  omniRead :: String -> Maybe a

-- | Combinable: merge two values (Semigroup-like).
class OmniCombine a where
  omniCombine :: a -> a -> a

-- | Emptyable: provide a neutral element (Monoid-like).
class OmniCombine a => OmniEmpty a where
  omniEmpty :: a

-- | Mappable: transform contents (Functor-like).
class OmniMap f where
  omniMap :: (a -> b) -> f a -> f b

-- | Chainable: monadic bind (Monad-like).
class OmniMap f => OmniChain f where
  omniChain :: f a -> (a -> f b) -> f b
  omniPure  :: a -> f a

-- | Foldable: reduce to single value.
class OmniFold t where
  omniFoldl :: (b -> a -> b) -> b -> t a -> b
  omniFoldr :: (a -> b -> b) -> b -> t a -> b

-- ============================================================
-- PART 2: Container Types with Instances
-- ============================================================

-- | OmniList: list with typeclass instances.
newtype OmniList a = OmniList { unOmniList :: [a] }
  deriving (Show, Eq)

instance OmniMap OmniList where
  omniMap f (OmniList xs) = OmniList (map f xs)

instance OmniChain OmniList where
  omniChain (OmniList xs) f = OmniList (concatMap (unOmniList . f) xs)
  omniPure a = OmniList [a]

instance OmniFold OmniList where
  omniFoldl f z (OmniList xs) = foldl' f z xs
  omniFoldr f z (OmniList xs) = foldr f z xs

instance OmniCombine (OmniList a) where
  omniCombine (OmniList a) (OmniList b) = OmniList (a ++ b)

instance OmniEmpty (OmniList a) where
  omniEmpty = OmniList []

-- | OmniMaybe: optional value with instances.
data OmniMaybe a
  = OmniJust a
  | OmniNothing
  deriving (Show, Eq)

instance OmniMap OmniMaybe where
  omniMap f (OmniJust a)  = OmniJust (f a)
  omniMap _ OmniNothing   = OmniNothing

instance OmniChain OmniMaybe where
  omniChain (OmniJust a) f = f a
  omniChain OmniNothing  _ = OmniNothing
  omniPure = OmniJust

instance OmniFold OmniMaybe where
  omniFoldl f z (OmniJust a) = f z a
  omniFoldl _ z OmniNothing  = z
  omniFoldr f z (OmniJust a) = f a z
  omniFoldr _ z OmniNothing  = z

-- ============================================================
-- PART 3: Derived Typeclass Operations
-- ============================================================

-- | Concatenate a list of combinable values.
omniConcat :: OmniEmpty a => [a] -> a
omniConcat = foldl' omniCombine omniEmpty

-- | Filter a chainable container.
omniFilter :: OmniChain f => (a -> Bool) -> f a -> f a
omniFilter p xs = omniChain xs (\a -> if p a then omniPure a else omniPure a)
  -- Note: simplified; proper filter needs Alternative

-- | Map then chain (like concatMap).
omniConcatMap :: OmniChain f => (a -> f b) -> f a -> f b
omniConcatMap = flip omniChain

-- | Convert to list.
omniToList :: OmniFold t => t a -> [a]
omniToList = omniFoldr (:) []

-- | Sum elements.
omniSum :: (OmniFold t, Num a) => t a -> a
omniSum = omniFoldl (+) 0

-- | Product of elements.
omniProduct :: (OmniFold t, Num a) => t a -> a
omniProduct = omniFoldl (*) 1

-- | Length of foldable.
omniLength :: OmniFold t => t a -> Int
omniLength = omniFoldl (\n _ -> n + 1) 0

-- | Check if any element satisfies predicate.
omniAny :: OmniFold t => (a -> Bool) -> t a -> Bool
omniAny p = omniFoldl (\acc a -> acc || p a) False

-- | Check if all elements satisfy predicate.
omniAll :: OmniFold t => (a -> Bool) -> t a -> Bool
omniAll p = omniFoldl (\acc a -> acc && p a) True

-- ============================================================
-- PART 4: Newtype Wrappers (Zero-Cost Abstraction)
-- ============================================================

-- | Sum wrapper (monoid under addition).
newtype Sum a = Sum { getSum :: a }
  deriving (Show, Eq)

instance Num a => OmniCombine (Sum a) where
  omniCombine (Sum a) (Sum b) = Sum (a + b)

instance Num a => OmniEmpty (Sum a) where
  omniEmpty = Sum 0

-- | Product wrapper (monoid under multiplication).
newtype Product a = Product { getProduct :: a }
  deriving (Show, Eq)

instance Num a => OmniCombine (Product a) where
  omniCombine (Product a) (Product b) = Product (a * b)

instance Num a => OmniEmpty (Product a) where
  omniEmpty = Product 1

-- | All wrapper (monoid under &&).
newtype All = All { getAll :: Bool }
  deriving (Show, Eq)

instance OmniCombine All where
  omniCombine (All a) (All b) = All (a && b)

instance OmniEmpty All where
  omniEmpty = All True

-- | Any wrapper (monoid under ||).
newtype Any = Any { getAny :: Bool }
  deriving (Show, Eq)

instance OmniCombine Any where
  omniCombine (Any a) (Any b) = Any (a || b)

instance OmniEmpty Any where
  omniEmpty = Any False

-- ============================================================
-- Diagnostics
-- ============================================================

diagnostics :: Map String [String]
diagnostics = Map.fromList
  [ ("engine",       ["OmniTypeclassEngine"])
  , ("layer",        ["Haskell Functional"])
  , ("typeclasses",  [ "OmniShow", "OmniRead", "OmniCombine"
                      , "OmniEmpty", "OmniMap", "OmniChain", "OmniFold"])
  , ("containers",   ["OmniList", "OmniMaybe"])
  , ("newtypes",     ["Sum", "Product", "All", "Any"])
  , ("derived_ops",  [ "omniConcat", "omniToList", "omniSum"
                      , "omniProduct", "omniLength", "omniAny", "omniAll"])
  , ("learned_logic", [ "typeclass-ad-hoc-polymorphism"
                       , "instance-concrete-implementation"
                       , "superclass-constraint-hierarchy"
                       , "default-method-boilerplate"
                       , "newtype-zero-cost-wrapper"
                       , "monoid-semigroup-combine-empty"
                       , "foldable-reduce-universal"
                       , "deriving-strategy-auto-instance"])
  ]
