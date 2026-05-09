-- OMNI Framework - Elm Frontend for KeyBERT Insights
module OmniKeyBERTDashboard exposing (main)

import Browser
import Html exposing (Html, div, h1, text, ul, li, span)
import Html.Attributes exposing (style, class)

type alias Keyword =
    { word : String, confidence : Float }

type alias Model =
    { keywords : List Keyword }

init : () -> ( Model, Cmd Msg )
init _ =
    ( { keywords = 
        [ { word = "Artificial Intelligence", confidence = 0.98 }
        , { word = "Distributed Systems", confidence = 0.85 }
        , { word = "Semantic Search", confidence = 0.72 }
        ] 
      }
    , Cmd.none 
    )

type Msg = NoOp

update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    ( model, Cmd.none )

view : Model -> Html Msg
view model =
    div [ style "padding" "40px", style "background-color" "#0d1117", style "color" "#c9d1d9", style "font-family" "Inter, sans-serif" ]
        [ h1 [ style "color" "#58a6ff" ] [ text "OMNI KeyBERT Extractions" ]
        , ul [ style "list-style" "none", style "padding" "0" ]
            (List.map viewKeyword model.keywords)
        ]

viewKeyword : Keyword -> Html Msg
viewKeyword kw =
    li [ style "background" "#161b22", style "margin-bottom" "10px", style "padding" "15px", style "border-radius" "6px", style "border" "1px solid #30363d" ]
        [ span [ style "font-weight" "bold", style "font-size" "18px" ] [ text kw.word ]
        , span [ style "float" "right", style "color" "#2ea043" ] [ text ("Confidence: " ++ String.fromFloat kw.confidence) ]
        ]

main =
    Browser.element
        { init = init
        , update = update
        , subscriptions = \_ -> Sub.none
        , view = view
        }
