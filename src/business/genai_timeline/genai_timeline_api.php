<?php
// @omni-domain Business Layer (GenAI Timeline API)
// @omni-requirement zero-mock, monadic-error
class OmniResult { public $data; public $error;
    private function __construct($d,$e){$this->data=$d;$this->error=$e;}
    public static function ok($d){return new self($d,null);}
    public static function err($e){return new self(null,$e);}
    public function isOk(){return $this->error===null;}
}
class GenAITimelineAPI {
    private $events = [];
    public function addEvent($id, $name, $date, $category) {
        if (empty($id)||empty($name)) return OmniResult::err("ID and name required.");
        $this->events[$id] = ['name'=>$name,'date'=>$date,'category'=>$category];
        return OmniResult::ok(true);
    }
    public function getTimeline($category = null) {
        $filtered = $category ? array_filter($this->events, fn($e)=>$e['category']===$category) : $this->events;
        usort($filtered, fn($a,$b)=>strcmp($a['date'],$b['date']));
        return OmniResult::ok($filtered);
    }
}
