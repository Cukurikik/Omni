-- ===========================================================================
-- OMNI LENS ENGINE (SEMESTER 3 — BATCH 38.5)
-- ===========================================================================
-- Absorbed From  : lens + microlens + optics
-- Logic Inherited: Haskell / Functional Layer (Optics: Lens, Prism, Traversal)
-- ===========================================================================
--
-- By studying the lens library, Mother learned:
--   1. Lens = getter + setter for product types (records)
--   2. Prism = constructor pattern matching for sum types
--   3. Traversal = focus on multiple targets simultaneously
--   4. Van Laarhoven representation: Lens s t a b = forall f. Functor f => (a -> f b) -> s -> f t
--   5. Composition via (.) enables deep nested access

{-# LANGUAGE RankNTypes #-}
{-# LANGUAGE TupleSections #-}

module OmniLensEngine
  ( -- * Lens Type
    Lens
  , Lens'
    -- * Lens Construction
  , lens
  , _1
  , _2
    -- * Lens Operations
  , view
  , set
  , over
    -- * Prism Type
  , Prism
  , Prism'
  , prism
  , preview
  , review
    -- * Traversal
  , Traversal
  , Traversal'
  , traversed
  , both
    -- * Iso
  , Iso
  , Iso'
  , iso
  , from
    -- * Utility
  , (&)
  , (.~)
  , (%~)
  , (^.)
    -- * Example Types
  , Address(..)
  , Person(..)
  , street
  , city
  , name
  , age
  , address
    -- * Diagnostics
  , engineDiagnostics
  ) where

import Data.Functor.Identity
import Data.Functor.Const
import Data.List (intercalate)

-- ============================================================
-- Core Optic Types (Van Laarhoven)
-- ============================================================

-- | Lens: focuses on exactly ONE field in a product type.
-- Van Laarhoven: Lens s t a b = forall f. Functor f => (a -> f b) -> s -> f t
type Lens s t a b = forall f. Functor f => (a -> f b) -> s -> f t
type Lens' s a = Lens s s a a

-- | Prism: focuses on one constructor of a sum type.
type Prism s t a b = forall f. Applicative f => (a -> f b) -> s -> f t
type Prism' s a = Prism s s a a

-- | Traversal: focuses on zero or more targets.
type Traversal s t a b = forall f. Applicative f => (a -> f b) -> s -> f t
type Traversal' s a = Traversal s s a a

-- | Iso: a reversible isomorphism.
type Iso s t a b = forall f. Functor f => (a -> f b) -> s -> f t
type Iso' s a = Iso s s a a

-- ============================================================
-- Lens Construction
-- ============================================================

-- | Build a lens from a getter and setter.
lens :: (s -> a) -> (s -> b -> t) -> Lens s t a b
lens getter setter f s = setter s <$> f (getter s)

-- | Focus on the first element of a tuple.
_1 :: Lens (a, c) (b, c) a b
_1 f (a, c) = (, c) <$> f a

-- | Focus on the second element of a tuple.
_2 :: Lens (c, a) (c, b) a b
_2 f (c, a) = (c,) <$> f a

-- ============================================================
-- Lens Operations
-- ============================================================

-- | Get the focused value.
view :: Lens' s a -> s -> a
view l s = getConst (l Const s)

-- | Set the focused value.
set :: Lens s t a b -> b -> s -> t
set l b s = runIdentity (l (\_ -> Identity b) s)

-- | Modify the focused value with a function.
over :: Lens s t a b -> (a -> b) -> s -> t
over l f s = runIdentity (l (Identity . f) s)

-- ============================================================
-- Prism Operations
-- ============================================================

-- | Build a prism from a constructor and pattern match.
prism :: (b -> t) -> (s -> Either t a) -> Prism s t a b
prism construct match f s =
  case match s of
    Left  t -> pure t
    Right a -> construct <$> f a

-- | Try to extract the focused value (may fail for wrong constructor).
preview :: Prism' s a -> s -> Maybe a
preview p s =
  case p (Const . Just) s of
    Const ma -> ma

-- | Construct a value from the prism target.
review :: Prism' s a -> a -> s
review p a = runIdentity (p (Identity) a)

-- ============================================================
-- Traversal Operations
-- ============================================================

-- | Traverse all elements in a list.
traversed :: Traversal [a] [b] a b
traversed _ []     = pure []
traversed f (x:xs) = (:) <$> f x <*> traversed f xs

-- | Focus on both elements of a pair.
both :: Traversal (a, a) (b, b) a b
both f (a1, a2) = (,) <$> f a1 <*> f a2

-- ============================================================
-- Iso Operations
-- ============================================================

-- | Build an isomorphism from two functions.
iso :: (s -> a) -> (b -> t) -> Iso s t a b
iso sa bt f s = bt <$> f (sa s)

-- | Reverse an isomorphism.
from :: Iso s t a b -> Iso b a t s
from i f b = runIdentity (i (Identity . getConst . f) (runIdentity (i Identity b)))
  -- simplified: this is conceptual; real `from` needs profunctor optics

-- ============================================================
-- Operator Aliases
-- ============================================================

infixl 1 &
(&) :: a -> (a -> b) -> b
x & f = f x

infixr 4 .~
(.~) :: Lens s t a b -> b -> s -> t
(.~) = set

infixr 4 %~
(%~) :: Lens s t a b -> (a -> b) -> s -> t
(%~) = over

infixl 8 ^.
(^.) :: s -> Lens' s a -> a
s ^. l = view l s

-- ============================================================
-- Example Types with Lenses
-- ============================================================

data Address = Address
  { _street :: String
  , _city   :: String
  } deriving (Show, Eq)

data Person = Person
  { _name    :: String
  , _age     :: Int
  , _address :: Address
  } deriving (Show, Eq)

-- Lenses for Address
street :: Lens' Address String
street = lens _street (\a s -> a { _street = s })

city :: Lens' Address String
city = lens _city (\a c -> a { _city = c })

-- Lenses for Person
name :: Lens' Person String
name = lens _name (\p n -> p { _name = n })

age :: Lens' Person Int
age = lens _age (\p a -> p { _age = a })

address :: Lens' Person Address
address = lens _address (\p a -> p { _address = a })

-- Composed lens: person -> address -> city
-- Usage: view (address . city) person
-- This is the power of Van Laarhoven: composition via (.)

-- ============================================================
-- Diagnostics
-- ============================================================

engineDiagnostics :: [(String, String)]
engineDiagnostics =
  [ ("engine",     "OmniLensEngine")
  , ("layer",      "Haskell Functional")
  , ("optic_types", "Lens,Prism,Traversal,Iso")
  , ("operators",  "&,.~,%~,^.")
  , ("examples",   "Address,Person with composable lenses")
  , ("learned_logic", intercalate ","
      [ "van-laarhoven-lens-representation"
      , "functor-f-polymorphism"
      , "const-functor-getter"
      , "identity-functor-setter"
      , "lens-composition-via-dot"
      , "prism-sum-type-pattern-match"
      , "traversal-applicative-multi"
      , "iso-reversible-isomorphism"
      ])
  ]
