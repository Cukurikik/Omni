-- Omni DAEDAL Dependent Types (Idris)
-- Formal Layer: Length-indexed denoising guarantees.
-- Ref: Li-Jinsong/DAEDAL

module OmniDaedalTypes
import Data.Vect

%default total

DenoisedSequence : Nat -> Type
DenoisedSequence n = Vect n Double

denoise : DenoisedSequence n -> Double -> DenoisedSequence n
denoise xs scale = map (\x => x - scale * 0.01) xs
