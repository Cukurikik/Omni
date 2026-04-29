class LabelingFunction:
    """
    OMNI Engine: Snorkel Labeling Function core abstraction.
    """
    def __init__(self, name, f, resources=None):
        self.name = name
        self.f = f
        self.resources = resources or {}

    def __call__(self, x):
        return self.f(x, **self.resources)

def labeling_function(name=None, resources=None):
    """Decorator to define a Snorkel labeling function."""
    def wrapper(f):
        lf_name = name or f.__name__
        return LabelingFunction(lf_name, f, resources)
    return wrapper

# Example Usage in OMNI:
# @labeling_function()
# def keyword_lf(x):
#     return 1 if "money" in x.text.lower() else -1
