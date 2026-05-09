<?php
namespace OmniMoE\Legacy;

// OMNI MOTHER: PHP WordPress/Drupal compatible plugin scaffold

class OmniCMSPlugin {
    public function renderWidget() {
        $bridge = new OmniMoEBridge();
        $status = $bridge->getExpertStatus("expert-1");
        
        echo "<div class='omni-widget'>";
        echo "<h3>Omni MoE Status</h3>";
        echo "<p>Expert 1: " . htmlspecialchars($status['status']) . "</p>";
        echo "</div>";
    }
}
