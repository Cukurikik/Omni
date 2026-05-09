module OmniFramework.Compute.OmniMonadTransformers where

import Control.Monad.Trans.Maybe
import Control.Monad.Trans.State
import Control.Monad.IO.Class (liftIO)

type OmniStack a = MaybeT (StateT Int IO) a

runOmniStack :: Int -> OmniStack a -> IO (Maybe a, Int)
runOmniStack initialState stack = runStateT (runMaybeT stack) initialState

processOmniEvent :: Int -> OmniStack String
processOmniEvent eventId = do
    currentState <- lift get
    if eventId > 0
        then do
            lift $ put (currentState + 1)
            liftIO $ putStrLn $ "Processed OMNI event: " ++ show eventId
            return "Success"
        else MaybeT $ return Nothing
