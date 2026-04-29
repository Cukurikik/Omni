<?php
// OMNI Business Layer: valle_licensing.php
// PHP logic for tracking VALL-E commercial licensing.
// Bound: Max 5 active hardware UUIDs per commercial license.

namespace Omni\Semester14\Batch6;

define('MAX_ACTIVE_UUIDS', 5);

class OmniError {
    public int $code;
    public string $message;
    public function __construct(int $c, string $m) { $this->code=$c; $this->message=$m; }
}

class OmniResult {
    public mixed $data;
    public ?OmniError $error;
    public function __construct($d, $e=null) { $this->data=$d; $this->error=$e; }
}

class ValleLicensing {
    private array $registered_uuids = [];

    public function registerDevice(string $uuid): OmniResult {
        if (count($this->registered_uuids) >= MAX_ACTIVE_UUIDS) {
            if (!in_array($uuid, $this->registered_uuids)) {
                return new OmniResult(null, new OmniError(1, "License exceeds 5 active device limit."));
            }
        }
        
        if (!in_array($uuid, $this->registered_uuids)) {
            $this->registered_uuids[] = $uuid;
        }
        
        return new OmniResult(true);
    }
}
