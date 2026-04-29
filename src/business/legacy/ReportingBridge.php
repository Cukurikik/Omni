<?php
namespace Omni\Business;

class ReportingBridge {
    public function generateReport(array $metrics): string {
        if (empty($metrics)) {
            return "No data available";
        }
        $total = array_sum($metrics);
        return "Total Processing Volume: " . $total;
    }
}
