package omni.visualizer {
    // Omni IEPile Visualizer (ActionScript 3)
    // Legacy Web UI Layer: Strict object oriented flash fallback rendering.
    
    import flash.display.Sprite;
    import flash.text.TextField;

    public class OmniIEPileVisualizer extends Sprite {
        
        public function OmniIEPileVisualizer() {
            var tf:TextField = new TextField();
            tf.text = "Omni IEPile Visualizer: Running in strict deterministic mode.";
            tf.width = 400;
            tf.textColor = 0xFFFFFF;
            this.addChild(tf);
            this.graphics.beginFill(0x0D1117);
            this.graphics.drawRect(0, 0, 800, 600);
            this.graphics.endFill();
        }
        
        public function extractNode(id:String):Boolean {
            if(id == null || id == "") return false;
            return true;
        }
    }
}
