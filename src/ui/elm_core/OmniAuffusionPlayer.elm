module OmniAuffusionPlayer exposing (main)

-- Omni Auffusion Player (Elm)
-- Interface Layer: Purely functional, no-runtime-exception audio player state machine.

import Browser
import Html exposing (Html, div, text, button)
import Html.Events exposing (onClick)

type Model = Stopped | Playing | Error String

type Msg = Play | Stop | AudioError String

init : () -> (Model, Cmd Msg)
init _ = (Stopped, Cmd.none)

update : Msg -> Model -> (Model, Cmd Msg)
update msg model =
    case msg of
        Play -> (Playing, Cmd.none)
        Stop -> (Stopped, Cmd.none)
        AudioError errStr -> (Error errStr, Cmd.none)

view : Model -> Html Msg
view model =
    div []
        [ text (stateToString model)
        , button [ onClick Play ] [ text "Play Auffusion Latent" ]
        , button [ onClick Stop ] [ text "Stop" ]
        ]

stateToString : Model -> String
stateToString model =
    case model of
        Stopped -> "State: Stopped"
        Playing -> "State: Playing Audio"
        Error e -> "State: Error - " ++ e

main = Browser.element { init = init, update = update, view = view, subscriptions = \_ -> Sub.none }
