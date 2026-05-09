module Main exposing (..)

import Browser
import Html exposing (Html, div, text, button, h1, p)
import Html.Events exposing (onClick)

-- Omni Admin Dashboard (Elm)
-- UI & State Management Layer
-- Purely functional frontend representing a strict state machine for monitoring
-- the Omni GPU cluster. Guarantees no runtime exceptions.

-- MODEL
type alias Model =
    { clusterState : ClusterState
    , activeNodes : Int
    }

type ClusterState
    = Offline
    | Booting
    | Online
    | Error String

init : Model
init =
    { clusterState = Offline
    , activeNodes = 0
    }

-- UPDATE
type Msg
    = StartCluster
    | ClusterOnline Int
    | StopCluster

update : Msg -> Model -> Model
update msg model =
    case msg of
        StartCluster ->
            { model | clusterState = Booting }

        ClusterOnline nodes ->
            { model | clusterState = Online, activeNodes = nodes }

        StopCluster ->
            { model | clusterState = Offline, activeNodes = 0 }

-- VIEW
view : Model -> Html Msg
view model =
    div []
        [ h1 [] [ text "Omni Mother Nexus Dashboard" ]
        , p [] [ text ("Status: " ++ stateToString model.clusterState) ]
        , p [] [ text ("Active GPU Nodes: " ++ String.fromInt model.activeNodes) ]
        , viewControls model.clusterState
        ]

stateToString : ClusterState -> String
stateToString state =
    case state of
        Offline -> "Offline"
        Booting -> "Booting..."
        Online -> "Online"
        Error err -> "Error: " ++ err

viewControls : ClusterState -> Html Msg
viewControls state =
    case state of
        Offline ->
            button [ onClick StartCluster ] [ text "Start Cluster" ]

        Booting ->
            button [ onClick (ClusterOnline 4) ] [ text "Simulate Boot Complete" ]

        Online ->
            button [ onClick StopCluster ] [ text "Shutdown" ]

        Error _ ->
            button [ onClick StopCluster ] [ text "Acknowledge Error" ]

-- MAIN
main =
    Browser.sandbox { init = init, update = update, view = view }
