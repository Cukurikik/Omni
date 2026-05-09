// OMNI UI & Historical Archival Layer
// ActionScript 3.0 implementation
// Compiles to a SWF allowing legacy browser environments or archival kiosks 
// to interface with the modern Omni Universal API over REST.

package com.omni.legacy {
    import flash.display.Sprite;
    import flash.events.Event;
    import flash.events.IOErrorEvent;
    import flash.net.URLLoader;
    import flash.net.URLRequest;
    import flash.net.URLRequestMethod;
    import flash.net.URLVariables;
    import flash.text.TextField;
    import flash.text.TextFormat;

    public class OmniLegacyClient extends Sprite {
        
        private var outputText:TextField;
        private var apiUrl:String = "http://api.omniframework.dev/api/v1/infer";

        public function OmniLegacyClient() {
            setupUI();
            requestInference("Generate a brief explanation of ActionScript 3.0");
        }

        private function setupUI():void {
            outputText = new TextField();
            outputText.width = 700;
            outputText.height = 500;
            outputText.wordWrap = true;
            outputText.multiline = true;
            outputText.border = true;
            
            var format:TextFormat = new TextFormat();
            format.font = "Arial";
            format.size = 14;
            outputText.defaultTextFormat = format;
            
            addChild(outputText);
            outputText.text = "OMNI Archival Client Initialized. Requesting data...\n";
        }

        private function requestInference(prompt:String):void {
            var request:URLRequest = new URLRequest(apiUrl);
            request.method = URLRequestMethod.POST;
            
            // Constructing JSON payload manually for AS3 compatibility
            var jsonPayload:String = "{\"prompt\":\"" + prompt + "\", \"max_tokens\": 100}";
            request.data = jsonPayload;
            request.contentType = "application/json";

            var loader:URLLoader = new URLLoader();
            loader.addEventListener(Event.COMPLETE, onResponseReceived);
            loader.addEventListener(IOErrorEvent.IO_ERROR, onError);
            
            try {
                loader.load(request);
            } catch (error:Error) {
                outputText.appendText("Security or Sandbox Error: " + error.message + "\n");
            }
        }

        private function onResponseReceived(event:Event):void {
            var loader:URLLoader = URLLoader(event.target);
            outputText.appendText("\n--- Omni Response ---\n" + loader.data + "\n");
        }

        private function onError(event:IOErrorEvent):void {
            outputText.appendText("\nNetwork Error connecting to Omni Engine: " + event.text + "\n");
        }
    }
}
