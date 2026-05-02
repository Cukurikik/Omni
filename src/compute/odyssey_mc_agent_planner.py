"# OMNI Compute Layer - Odyssey MC Agent Planner\
class OdysseyError(Exception):\
    pass\
\
class Result:\
    def __init__(self, value=None, error=None):\
        self.value = value\
        self.error = error\
        \
    def is_ok(self):\
        re
<truncated 719 bytes>