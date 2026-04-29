<?php
namespace OmniFramework\Semester14\Batch8\Business;

class OmniResult { public bool $isOk; public mixed $value; public ?string $error;
    public function __construct(bool $ok, mixed $val = null, ?string $err = null) {
        $this->isOk = $ok; $this->value = $val; $this->error = $err;
    }
}

class RAGWebController {
    private const MAX_QUERY_LEN = 4096;
    private const MAX_TOP_K = 100;

    public function search(string $query, int $topK = 10): OmniResult {
        if (empty($query)) return new OmniResult(false, null, "Empty query");
        if (strlen($query) > self::MAX_QUERY_LEN) return new OmniResult(false, null, "Query exceeds limit");
        if ($topK > self::MAX_TOP_K) return new OmniResult(false, null, "topK exceeds " . self::MAX_TOP_K);
        return new OmniResult(true, ["results" => [], "total" => 0]);
    }

    public function ingest(string $title, string $content): OmniResult {
        if (empty($title)) return new OmniResult(false, null, "Title required");
        if (strlen($content) > 10_000_000) return new OmniResult(false, null, "Content exceeds 10MB");
        return new OmniResult(true, ["docId" => uniqid(), "status" => "indexed"]);
    }
}
