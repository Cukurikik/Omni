// Omni Fusion Bench Desktop (Vala)
// Desktop UI Layer: Native GTK desktop app for model fusion management.

using Gtk;

public class OmniFusionApp : Application {
    public OmniFusionApp () {
        Object (application_id: "dev.omni.fusionbench", flags: ApplicationFlags.FLAGS_NONE);
    }

    protected override void activate () {
        var window = new ApplicationWindow (this);
        window.title = "Omni Fusion Bench";
        window.set_default_size (800, 600);
        
        var label = new Label ("Fusion Bench Core: Linear Merging Active");
        window.add (label);
        
        window.show_all ();
    }

    public static int main (string[] args) {
        var app = new OmniFusionApp ();
        return app.run (args);
    }
}
