{- ===========================================================================
   OMNI PURE FUNCTIONAL ENGINE (SEMESTER 3 REMEDIATION — BATCH 38.1)
   ===========================================================================
   Absorbed From  : base + containers + mtl + lens concepts
   Logic Inherited: Haskell / Functional Layer (Pure Immutable Data Pipeline)
   Domain Layer   : Functional (Haskell Core)
   ===========================================================================

   By studying Haskell's base library, containers, and mtl, Mother
   learned that Haskell's type system enforces purity at compile time:
     1. ADTs (algebraic data types) for domain modeling
     2. Monadic composition for sequencing side effects
     3. Lazy evaluation with strict annotations where needed
     4. Pattern matching for exhaustive case analysis
     5. Higher-order functions (map, fold, filter) replace loops

   Haskell IS the language for formally-verified pure computation in OMNI.
-}

module OmniPureFunctionalEngine
  ( -- * Core Types
    Pipeline(..)
  , PipelineStep(..)
  , PipelineResult(..)
  , PipelineError(..)
    -- * Pipeline Construction
  , emptyPipeline
  , addStep
  , addGuard
  , addTransform
    -- * Pipeline Execution
  , runPipeline
  , runPipelineWith
    -- * Utility Combinators
  , mapPipeline
  , filterPipeline
  , foldPipeline
  , composePipelines
    -- * Diagnostics
  , diagnostics
  ) where

import Data.List (foldl', intercalate)
import Data.Maybe (mapMaybe)

-- ---- Error Types (ADT) ----

-- | Errors that can occur during pipeline execution.
data PipelineError
  = GuardFailed String        -- ^ A guard condition was not met
  | TransformError String     -- ^ A transformation step failed
  | EmptyInput                -- ^ No input was provided
  | CompositionError String   -- ^ Pipelines could not be composed
  deriving (Show, Eq)

-- ---- Result Type (Either-based monadic error handling) ----

-- | Pipeline result — Right for success, Left for error.
-- This replaces try/catch with monadic composition.
type PipelineResult a = Either PipelineError a

-- ---- Pipeline Step (ADT with 3 variants) ----

-- | A single step in the pipeline.
data PipelineStep a
  = Transform String (a -> PipelineResult a)
    -- ^ Named transformation: applies a function to the data
  | Guard String (a -> Bool)
    -- ^ Named guard: fails the pipeline if predicate is False
  | Filter String (a -> Bool)
    -- ^ Named filter: removes elements that don't match (for lists)

-- | Get the name of a pipeline step.
stepName :: PipelineStep a -> String
stepName (Transform n _) = "Transform:" ++ n
stepName (Guard n _)     = "Guard:" ++ n
stepName (Filter n _)    = "Filter:" ++ n

-- ---- Pipeline (Composable Chain of Steps) ----

-- | A pipeline is an ordered sequence of steps.
data Pipeline a = Pipeline
  { pipelineSteps :: [PipelineStep a]
  , pipelineName  :: String
  }

-- ---- Construction ----

-- | Create an empty pipeline with a name.
emptyPipeline :: String -> Pipeline a
emptyPipeline name = Pipeline { pipelineSteps = [], pipelineName = name }

-- | Add a generic step to the pipeline.
addStep :: PipelineStep a -> Pipeline a -> Pipeline a
addStep step p = p { pipelineSteps = pipelineSteps p ++ [step] }

-- | Add a named transformation step.
addTransform :: String -> (a -> PipelineResult a) -> Pipeline a -> Pipeline a
addTransform name f = addStep (Transform name f)

-- | Add a named guard (assertion) step.
addGuard :: String -> (a -> Bool) -> Pipeline a -> Pipeline a
addGuard name pred' = addStep (Guard name pred')

-- ---- Execution ----

-- | Run a pipeline on input data.
-- Each step is applied sequentially via monadic bind (>>=).
-- If any step fails, the entire pipeline short-circuits with Left.
runPipeline :: Pipeline a -> a -> PipelineResult a
runPipeline pipeline input =
  foldl' applyStep (Right input) (pipelineSteps pipeline)
  where
    applyStep :: PipelineResult a -> PipelineStep a -> PipelineResult a
    applyStep (Left err) _             = Left err  -- Short-circuit on error
    applyStep (Right val) (Transform _ f) = f val
    applyStep (Right val) (Guard name pred')
      | pred' val  = Right val
      | otherwise = Left (GuardFailed $ name ++ ": guard condition failed")
    applyStep (Right val) (Filter _ _) = Right val  -- Filter is a no-op on single values

-- | Run the pipeline with logging of each step.
runPipelineWith :: Pipeline a -> a -> (PipelineResult a, [String])
runPipelineWith pipeline input =
  foldl' step (Right input, []) (pipelineSteps pipeline)
  where
    step :: (PipelineResult a, [String]) -> PipelineStep a -> (PipelineResult a, [String])
    step (Left err, logs) s  = (Left err, logs ++ ["SKIP " ++ stepName s])
    step (Right val, logs) s =
      let result = applyOne val s
          status = case result of
                     Right _ -> "OK   " ++ stepName s
                     Left e  -> "FAIL " ++ stepName s ++ " (" ++ show e ++ ")"
      in (result, logs ++ [status])

    applyOne :: a -> PipelineStep a -> PipelineResult a
    applyOne val (Transform _ f)    = f val
    applyOne val (Guard name pred')
      | pred' val  = Right val
      | otherwise = Left (GuardFailed name)
    applyOne val (Filter _ _)      = Right val

-- ---- Combinators (Higher-Order Pipeline Operations) ----

-- | Apply a pipeline to each element of a list, collecting results.
mapPipeline :: Pipeline a -> [a] -> [PipelineResult a]
mapPipeline pipeline = map (runPipeline pipeline)

-- | Filter a list, keeping only elements that pass all guards.
filterPipeline :: Pipeline a -> [a] -> [a]
filterPipeline pipeline = filter passes
  where
    passes x = case runPipeline pipeline x of
                 Right _ -> True
                 Left _  -> False

-- | Fold over pipeline results, accumulating a value.
foldPipeline :: Pipeline a -> (b -> a -> b) -> b -> [a] -> PipelineResult b
foldPipeline pipeline f z xs =
  foldl' step (Right z) xs
  where
    step (Left err) _ = Left err
    step (Right acc) x =
      case runPipeline pipeline x of
        Left err  -> Left err
        Right val -> Right (f acc val)

-- | Compose two pipelines sequentially.
composePipelines :: Pipeline a -> Pipeline a -> Pipeline a
composePipelines p1 p2 = Pipeline
  { pipelineSteps = pipelineSteps p1 ++ pipelineSteps p2
  , pipelineName  = pipelineName p1 ++ " >>> " ++ pipelineName p2
  }

-- ---- Diagnostics ----

-- | OMNI Engine Registry diagnostics.
diagnostics :: Pipeline a -> [(String, String)]
diagnostics pipeline =
  [ ("engine",        "OmniPureFunctionalEngine")
  , ("layer",         "Haskell Functional")
  , ("pipeline_name", pipelineName pipeline)
  , ("step_count",    show (length (pipelineSteps pipeline)))
  , ("step_names",    intercalate ", " (map stepName (pipelineSteps pipeline)))
  , ("learned_logic", intercalate ", "
      [ "adt-algebraic-data-types"
      , "monadic-either-error-handling"
      , "foldl-strict-left-fold"
      , "pattern-matching-exhaustive"
      , "higher-order-pipeline-combinators"
      , "lazy-evaluation-with-strict-folds"
      , "type-class-polymorphism"
      ])
  ]
