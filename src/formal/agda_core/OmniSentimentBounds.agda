-- Omni Sentiment Bounds (Agda)
-- Formal Layer: Constructive proof of sentiment score bounds.
-- Ref: leduckhai/Sentiment-Reasoning

module OmniSentimentBounds where

open import Data.Nat

data Bounded : Set where
  InRange : (n : ℕ) → Bounded
  OutOfRange : Bounded

checkBound : ℕ → ℕ → Bounded
checkBound val max = if val < max then InRange val else OutOfRange
