"""
ML Model Configuration for Enhanced Code Suggestions
"""

ML_MODEL_CONFIG = {
    "code_completion": {
        "enabled": True,
        "description": "Context-aware code completions"
    },
    "code_classification": {
        "enabled": True,
        "description": "Classifies code patterns"
    }
}

COMPLEXITY_PATTERNS = {
    "O(1)": ["constant", "direct_access"],
    "O(log n)": ["binary_search", "tree_operations"],
    "O(n)": ["linear_search", "single_loop"],
    "O(n log n)": ["merge_sort", "quick_sort"],
    "O(n²)": ["nested_loops", "bubble_sort"]
}

DESIGN_PATTERNS = {
    "singleton": {
        "python": '''class Singleton:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance''',
        "indicators": ["single_instance", "global_state"]
    },
    "factory": {
        "python": '''class Factory:
    @staticmethod
    def create(obj_type):
        if obj_type == 'A':
            return ObjectA()
        return ObjectB()''',
        "indicators": ["create", "instantiate"]
    }
}
