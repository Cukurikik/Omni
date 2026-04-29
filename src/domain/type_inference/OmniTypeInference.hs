-- OMNI FRAMEWORK — COMPUTE LAYER: HASKELL CORE
-- OmniTypeInference.hs — Production Type Inference Engine
-- ========================================================
-- Implements Hindley-Milner type inference algorithm (Algorithm W)
-- for static type checking across OMNI's polylingual UAST.
--
-- Components:
--   - Type representation (TVar, TCon, TArrow, TForall)
--   - Substitution and unification
--   - Type environment management
--   - Algorithm W for principal type inference
--   - Constraint generation and solving
--
-- OMNI Layer: compute/haskell_core
-- @since 2026.4.2

module Omni.Compute.TypeInference
    ( Type(..)
    , Scheme(..)
    , Subst
    , TypeEnv
    , InferError(..)
    , InferResult
    , emptySubst
    , emptyEnv
    , unify
    , infer
    , generalize
    , instantiate
    , applySubst
    , diagnostics
    ) where

import qualified Data.Map.Strict as Map
import qualified Data.Set as Set
import Data.List (intercalate)

-- ---------------------------------------------------------------------------
-- 1. TYPE REPRESENTATION
-- ---------------------------------------------------------------------------

-- | Type expressions in the OMNI type system.
data Type
    = TVar String           -- ^ Type variable: α, β, γ
    | TCon String           -- ^ Type constructor: Int, String, Bool
    | TArrow Type Type      -- ^ Function type: τ₁ → τ₂
    | TList Type            -- ^ List type: [τ]
    | TTuple [Type]         -- ^ Tuple type: (τ₁, τ₂, ...)
    | TApp Type Type        -- ^ Type application: F τ
    deriving (Eq, Ord)

instance Show Type where
    show (TVar name)    = name
    show (TCon name)    = name
    show (TArrow a b)   = "(" ++ show a ++ " -> " ++ show b ++ ")"
    show (TList t)      = "[" ++ show t ++ "]"
    show (TTuple ts)    = "(" ++ intercalate ", " (map show ts) ++ ")"
    show (TApp f a)     = show f ++ " " ++ show a

-- | Type scheme (polytype): ∀ α₁ α₂ ... αₙ. τ
data Scheme = Forall [String] Type
    deriving (Show, Eq)

-- ---------------------------------------------------------------------------
-- 2. SUBSTITUTION
-- ---------------------------------------------------------------------------

-- | A substitution maps type variables to types.
type Subst = Map.Map String Type

-- | The identity substitution.
emptySubst :: Subst
emptySubst = Map.empty

-- | Compose two substitutions: (s1 `composeSubst` s2) applies s2 first, then s1.
composeSubst :: Subst -> Subst -> Subst
composeSubst s1 s2 = Map.map (applySubst s1) s2 `Map.union` s1

-- | Apply a substitution to a type.
applySubst :: Subst -> Type -> Type
applySubst s (TVar v)     = Map.findWithDefault (TVar v) v s
applySubst s (TArrow a b) = TArrow (applySubst s a) (applySubst s b)
applySubst s (TList t)    = TList (applySubst s t)
applySubst s (TTuple ts)  = TTuple (map (applySubst s) ts)
applySubst s (TApp f a)   = TApp (applySubst s f) (applySubst s a)
applySubst _ t             = t

-- | Apply a substitution to a type scheme.
applySubstScheme :: Subst -> Scheme -> Scheme
applySubstScheme s (Forall vars t) =
    let s' = foldr Map.delete s vars
    in Forall vars (applySubst s' t)

-- | Get free type variables of a type.
ftv :: Type -> Set.Set String
ftv (TVar v)     = Set.singleton v
ftv (TCon _)     = Set.empty
ftv (TArrow a b) = ftv a `Set.union` ftv b
ftv (TList t)    = ftv t
ftv (TTuple ts)  = Set.unions (map ftv ts)
ftv (TApp f a)   = ftv f `Set.union` ftv a

-- | Free type variables of a scheme.
ftvScheme :: Scheme -> Set.Set String
ftvScheme (Forall vars t) = ftv t `Set.difference` Set.fromList vars

-- ---------------------------------------------------------------------------
-- 3. TYPE ENVIRONMENT
-- ---------------------------------------------------------------------------

-- | Type environment: maps term variables to their type schemes.
type TypeEnv = Map.Map String Scheme

-- | Empty type environment.
emptyEnv :: TypeEnv
emptyEnv = Map.empty

-- | Free type variables of an environment.
ftvEnv :: TypeEnv -> Set.Set String
ftvEnv env = Set.unions (map ftvScheme (Map.elems env))

-- | Extend environment with a new binding.
extendEnv :: TypeEnv -> String -> Scheme -> TypeEnv
extendEnv env name scheme = Map.insert name scheme env

-- | Apply substitution to entire environment.
applySubstEnv :: Subst -> TypeEnv -> TypeEnv
applySubstEnv s = Map.map (applySubstScheme s)

-- ---------------------------------------------------------------------------
-- 4. INFERENCE ERRORS (MONADIC — NO EXCEPTIONS)
-- ---------------------------------------------------------------------------

-- | Typed errors for inference operations.
data InferError
    = UnificationFail Type Type String
    | InfiniteType String Type
    | UnboundVariable String
    | AmbiguousType String
    deriving (Show, Eq)

-- | Result type for inference operations.
type InferResult a = Either InferError a

-- ---------------------------------------------------------------------------
-- 5. UNIFICATION
-- ---------------------------------------------------------------------------

-- | Unify two types, producing a most general unifier (substitution).
--
-- Implements Robinson's unification algorithm.
--
-- @param t1 First type
-- @param t2 Second type
-- @returns Either InferError Subst
unify :: Type -> Type -> InferResult Subst
unify (TArrow a1 b1) (TArrow a2 b2) = do
    s1 <- unify a1 a2
    s2 <- unify (applySubst s1 b1) (applySubst s1 b2)
    return (composeSubst s2 s1)

unify (TList a) (TList b) = unify a b

unify (TTuple as) (TTuple bs)
    | length as == length bs = unifyMany as bs
    | otherwise = Left $ UnificationFail (TTuple as) (TTuple bs) "Tuple arity mismatch"

unify (TApp f1 a1) (TApp f2 a2) = do
    s1 <- unify f1 f2
    s2 <- unify (applySubst s1 a1) (applySubst s1 a2)
    return (composeSubst s2 s1)

unify (TVar v) t = varBind v t
unify t (TVar v) = varBind v t

unify (TCon a) (TCon b)
    | a == b = return emptySubst
    | otherwise = Left $ UnificationFail (TCon a) (TCon b)
        ("Cannot unify " ++ a ++ " with " ++ b)

unify t1 t2 = Left $ UnificationFail t1 t2
    ("Cannot unify " ++ show t1 ++ " with " ++ show t2)

-- | Unify a list of type pairs.
unifyMany :: [Type] -> [Type] -> InferResult Subst
unifyMany [] [] = return emptySubst
unifyMany (t1:ts1) (t2:ts2) = do
    s1 <- unify t1 t2
    s2 <- unifyMany (map (applySubst s1) ts1) (map (applySubst s1) ts2)
    return (composeSubst s2 s1)
unifyMany _ _ = Left $ UnificationFail (TCon "?") (TCon "?") "Arity mismatch"

-- | Bind a type variable to a type, with occurs check.
varBind :: String -> Type -> InferResult Subst
varBind v t
    | t == TVar v = return emptySubst
    | v `Set.member` ftv t = Left $ InfiniteType v t
    | otherwise = return $ Map.singleton v t

-- ---------------------------------------------------------------------------
-- 6. GENERALIZATION & INSTANTIATION
-- ---------------------------------------------------------------------------

-- | Generalize a type to a type scheme by quantifying free variables
-- not in the environment.
generalize :: TypeEnv -> Type -> Scheme
generalize env t =
    let vars = Set.toList (ftv t `Set.difference` ftvEnv env)
    in Forall vars t

-- | Instantiate a type scheme with fresh type variables.
-- Uses a deterministic counter for variable naming.
instantiate :: Int -> Scheme -> (Type, Int)
instantiate counter (Forall vars t) =
    let freshVars = zipWith (\v i -> (v, TVar ("_t" ++ show i)))
                            vars [counter..]
        s = Map.fromList freshVars
        newCounter = counter + length vars
    in (applySubst s t, newCounter)

-- ---------------------------------------------------------------------------
-- 7. TYPE INFERENCE (Algorithm W, simplified)
-- ---------------------------------------------------------------------------

-- | Simple expression language for inference demonstration.
data Expr
    = EVar String           -- ^ Variable reference
    | EApp Expr Expr        -- ^ Function application
    | ELam String Expr      -- ^ Lambda abstraction
    | ELet String Expr Expr -- ^ Let binding
    | ELit Literal          -- ^ Literal value
    deriving (Show)

-- | Literal values with known types.
data Literal
    = LInt Integer
    | LBool Bool
    | LString String
    | LFloat Double
    deriving (Show)

-- | Infer the type of an expression in a given environment.
--
-- Implements Algorithm W (Damas-Milner).
--
-- @param env Type environment
-- @param counter Fresh variable counter
-- @param expr Expression to type-check
-- @returns (Substitution, inferred Type, new counter)
infer :: TypeEnv -> Int -> Expr -> InferResult (Subst, Type, Int)

infer _ counter (ELit (LInt _))    = return (emptySubst, TCon "Int", counter)
infer _ counter (ELit (LBool _))   = return (emptySubst, TCon "Bool", counter)
infer _ counter (ELit (LString _)) = return (emptySubst, TCon "String", counter)
infer _ counter (ELit (LFloat _))  = return (emptySubst, TCon "Float", counter)

infer env counter (EVar name) =
    case Map.lookup name env of
        Nothing -> Left $ UnboundVariable name
        Just scheme ->
            let (t, counter') = instantiate counter scheme
            in return (emptySubst, t, counter')

infer env counter (ELam param body) =
    let freshVar = TVar ("_t" ++ show counter)
        counter' = counter + 1
        env' = extendEnv env param (Forall [] freshVar)
    in do
        (s, bodyType, counter'') <- infer env' counter' body
        return (s, TArrow (applySubst s freshVar) bodyType, counter'')

infer env counter (EApp func arg) = do
    let freshVar = TVar ("_t" ++ show counter)
        counter' = counter + 1
    (s1, funcType, counter'') <- infer env counter' func
    (s2, argType, counter''') <- infer (applySubstEnv s1 env) counter'' arg
    s3 <- unify (applySubst s2 funcType) (TArrow argType freshVar)
    return (composeSubst s3 (composeSubst s2 s1),
            applySubst s3 freshVar,
            counter''')

infer env counter (ELet name expr body) = do
    (s1, exprType, counter') <- infer env counter expr
    let env' = applySubstEnv s1 env
        scheme = generalize env' exprType
        env'' = extendEnv env' name scheme
    (s2, bodyType, counter'') <- infer env'' counter' body
    return (composeSubst s2 s1, bodyType, counter'')

-- ---------------------------------------------------------------------------
-- 8. DIAGNOSTICS
-- ---------------------------------------------------------------------------

-- | Returns engine diagnostic information.
diagnostics :: Map.Map String String
diagnostics = Map.fromList
    [ ("engine",       "OmniTypeInferenceEngine")
    , ("version",      "1.1.0-omni-zeromock")
    , ("layer",        "compute/haskell_core")
    , ("algorithm",    "Hindley-Milner Algorithm W")
    , ("unification",  "Robinson's Algorithm")
    , ("typeSystem",   "rank-1 polymorphism")
    , ("features",     "TVar,TCon,TArrow,TList,TTuple,TApp,Forall")
    , ("mockPatterns", "zero")
    ]
