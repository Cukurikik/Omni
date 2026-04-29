<?php

namespace Omni\Business\DailyPaper;

class PaperAggregator {
    public function aggregate(array $sources): array {
        $allPapers = [];
        foreach ($sources as $source) {
            // Simulated fetch
            $allPapers[] = [
                'title' => "Paper from $source",
                'timestamp' => time()
            ];
        }
        return $allPapers;
    }
}
