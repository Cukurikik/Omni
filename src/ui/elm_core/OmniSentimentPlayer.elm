module OmniSentimentPlayer exposing (main)
-- Omni Sentiment Player (Elm) — Ref: leduckhai/Sentiment-Reasoning
import Browser
import Html exposing (Html, div, text, button)
import Html.Events exposing (onClick)

type Model = Idle | Analyzing | Done String
type Msg = Start | Finish String

init : () -> (Model, Cmd Msg)
init _ = (Idle, Cmd.none)

update : Msg -> Model -> (Model, Cmd Msg)
update msg _ = case msg of
    Start -> (Analyzing, Cmd.none)
    Finish label -> (Done label, Cmd.none)

view : Model -> Html Msg
view model = div [] [ text (stateStr model), button [onClick Start] [text "Analyze"] ]

stateStr : Model -> String
stateStr m = case m of
    Idle -> "Ready"
    Analyzing -> "Processing..."
    Done l -> "Result: " ++ l

main = Browser.element { init = init, update = update, view = view, subscriptions = \_ -> Sub.none }
