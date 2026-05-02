"# OMNI Compute Layer - Fondant Data Pipeline\
class FondantError(Exception):\
    pass\
\
class Result:\
    def __init__(self, value=None, error=None):\
        self.value = value\
        self.error = error\
        \
    def is_ok(self):\
        retur
<truncated 646 bytes>