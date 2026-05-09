module Omni.State

import Data.Vect

-- OMNI Dependent Types Layer
-- Idris implementation of a state machine verified at compile-time.
-- It is literally impossible to compile code that transitions states illegally.

data NodeState = Offline | Syncing | Active

-- Define allowable transitions using dependent types
data Transition : NodeState -> NodeState -> Type where
  TurnOn   : Transition Offline Syncing
  SyncDone : Transition Syncing Active
  TurnOff  : Transition state Offline

-- A verified sequence of state transitions
data StatePath : NodeState -> NodeState -> Type where
  Start : StatePath s s
  Step  : Transition s1 s2 -> StatePath s2 s3 -> StatePath s1 s3

-- Proof that we can safely move from Offline to Active
powerUpNode : StatePath Offline Active
powerUpNode = Step TurnOn (Step SyncDone Start)

-- Example of a compile-time failure if uncommented:
-- invalidTransition : StatePath Offline Active
-- invalidTransition = Step SyncDone Start -- Type mismatch! SyncDone expects Syncing, not Offline.

-- Represents a cluster of N nodes safely
record Cluster (n : Nat) where
  constructor MkCluster
  nodes : Vect n NodeState

initialCluster : Cluster 3
initialCluster = MkCluster [Offline, Offline, Offline]
