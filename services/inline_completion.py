import re
from typing import List, Dict, Optional, Tuple

class InlineCompletionService:
    """Service for generating intelligent inline code completions"""
    
    COMMON_PATTERNS = {
        "prime": {
            "triggers": ["prime", "is_prime", "check prime"],
            "completion": '''def is_prime(n):
    """Check if a number is prime"""
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True'''
        },
        
        "palindrome": {
            "triggers": ["palindrome", "is_palindrome", "check palindrome"],
            "completion": '''def is_palindrome(s):
    """Check if a string is a palindrome"""
    s = s.lower().replace(" ", "")
    return s == s[::-1]'''
        },
        
        "fibonacci": {
            "triggers": ["fibonacci", "fib"],
            "completion": '''def fibonacci(n):
    """Generate fibonacci sequence up to n terms"""
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    elif n == 2:
        return [0, 1]
    
    fib = [0, 1]
    for i in range(2, n):
        fib.append(fib[i-1] + fib[i-2])
    return fib'''
        },
        
        "factorial": {
            "triggers": ["factorial", "fact"],
            "completion": '''def factorial(n):
    """Calculate factorial of n"""
    if n == 0 or n == 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result'''
        },
        
        "binary_search": {
            "triggers": ["binary search", "binary_search", "bsearch"],
            "completion": '''def binary_search(arr, target):
    """Binary search in sorted array"""
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1'''
        },
        
        "bubble_sort": {
            "triggers": ["bubble sort", "bubble_sort"],
            "completion": '''def bubble_sort(arr):
    """Bubble sort algorithm"""
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr'''
        },
        
        "reverse_string": {
            "triggers": ["reverse", "reverse string"],
            "completion": '''def reverse_string(s):
    """Reverse a string"""
    return s[::-1]'''
        },
        
        "count_vowels": {
            "triggers": ["count vowel", "vowel count"],
            "completion": '''def count_vowels(s):
    """Count vowels in a string"""
    vowels = "aeiouAEIOU"
    return sum(1 for char in s if char in vowels)'''
        },
        
        "gcd": {
            "triggers": ["gcd", "greatest common divisor"],
            "completion": '''def gcd(a, b):
    """Calculate greatest common divisor"""
    while b:
        a, b = b, a % b
    return a'''
        },
        
        "lcm": {
            "triggers": ["lcm", "least common multiple"],
            "completion": '''def lcm(a, b):
    """Calculate least common multiple"""
    return abs(a * b) // gcd(a, b)

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a'''
        },
        
        "for_loop": {
            "triggers": ["for i in range"],
            "completion": '''for i in range(10):
    print(i)'''
        },
        
        "while_loop": {
            "triggers": ["while"],
            "completion": '''while condition:
    # Your code here
    pass'''
        },
        
        "if_else": {
            "triggers": ["if "],
            "completion": '''if condition:
    # True case
    pass
else:
    # False case
    pass'''
        },
        
        "try_except": {
            "triggers": ["try:"],
            "completion": '''try:
    # Your code here
    pass
except Exception as e:
    print(f"Error: {e}")'''
        },
        
        "class_basic": {
            "triggers": ["class "],
            "completion": '''class MyClass:
    def __init__(self):
        pass
    
    def method(self):
        pass'''
        },
        
        "read_file": {
            "triggers": ["read file", "open file"],
            "completion": '''with open('filename.txt', 'r') as f:
    content = f.read()
    print(content)'''
        },
        
        "write_file": {
            "triggers": ["write file", "save file"],
            "completion": '''with open('filename.txt', 'w') as f:
    f.write('Hello, World!')'''
        },
        
        "list_comprehension": {
            "triggers": ["list comprehension", "[x for"],
            "completion": '''result = [x for x in range(10) if x % 2 == 0]'''
        },
        
        "dict_comprehension": {
            "triggers": ["dict comprehension", "{k:"],
            "completion": '''result = {k: v for k, v in enumerate(items)}'''
        },
        
        "lambda": {
            "triggers": ["lambda"],
            "completion": '''square = lambda x: x ** 2'''
        },
        
        "decorator": {
            "triggers": ["@", "decorator"],
            "completion": '''def my_decorator(func):
    def wrapper(*args, **kwargs):
        print("Before function call")
        result = func(*args, **kwargs)
        print("After function call")
        return result
    return wrapper

@my_decorator
def my_function():
    print("Inside function")'''
        }
    }
    
    def __init__(self):
        self.last_code = ""
        self.last_suggestion = None
    
    def get_inline_completion(self, code: str, cursor_position: Optional[int] = None) -> Optional[Dict]:
        """Get intelligent inline code completion based on current context"""
        
        if not code.strip():
            return None
        
        code_lower = code.lower()
        lines = code.split('\n')
        last_line = lines[-1].strip().lower() if lines else ""
        
        # Check for pattern matches
        for pattern_name, pattern_data in self.COMMON_PATTERNS.items():
            for trigger in pattern_data["triggers"]:
                # Check if user is typing something that matches a trigger
                if trigger.lower() in code_lower or trigger.lower() in last_line:
                    # Check if this is a new trigger (not already completed)
                    if pattern_data["completion"] not in code:
                        return {
                            "type": "pattern",
                            "pattern_name": pattern_name,
                            "completion": pattern_data["completion"],
                            "description": f"Complete {pattern_name.replace('_', ' ')} pattern",
                            "trigger": trigger
                        }
        
        # Context-aware line completion
        line_completion = self._get_line_completion(lines)
        if line_completion:
            return line_completion
        
        return None
    
    def _get_line_completion(self, lines: List[str]) -> Optional[Dict]:
        """Get context-aware next line completion"""
        if not lines:
            return None
        
        last_line = lines[-1].strip()
        
        # Function definition continuation
        if last_line.startswith("def ") and last_line.endswith(":"):
            func_name = last_line[4:last_line.index("(")].strip()
            return {
                "type": "line",
                "completion": f'    """Description of {func_name}"""\n    pass',
                "description": "Add docstring and body"
            }
        
        # Class definition continuation
        if last_line.startswith("class ") and last_line.endswith(":"):
            return {
                "type": "line",
                "completion": '    def __init__(self):\n        pass',
                "description": "Add constructor"
            }
        
        # If statement continuation
        if last_line.startswith("if ") and last_line.endswith(":"):
            return {
                "type": "line",
                "completion": '    pass',
                "description": "Add if body"
            }
        
        # For loop continuation
        if last_line.startswith("for ") and last_line.endswith(":"):
            # Extract variable name
            match = re.search(r'for\s+(\w+)', last_line)
            if match:
                var_name = match.group(1)
                return {
                    "type": "line",
                    "completion": f'    print({var_name})',
                    "description": "Add loop body"
                }
        
        # While loop continuation
        if last_line.startswith("while ") and last_line.endswith(":"):
            return {
                "type": "line",
                "completion": '    pass',
                "description": "Add while body"
            }
        
        # Try block continuation
        if last_line == "try:":
            return {
                "type": "line",
                "completion": '    pass\nexcept Exception as e:\n    print(f"Error: {e}")',
                "description": "Add try-except block"
            }
        
        # Import statement suggestions
        if last_line.startswith("import ") or last_line.startswith("from "):
            return None  # Don't autocomplete imports
        
        # Common method patterns
        if "print" in last_line.lower() and "(" in last_line and ")" not in last_line:
            return {
                "type": "line",
                "completion": ')',
                "description": "Close print statement"
            }
        
        return None
    
    def get_snippet_suggestions(self, partial_code: str) -> List[Dict]:
        """Get multiple snippet suggestions based on partial code"""
        suggestions = []
        partial_lower = partial_code.lower().strip()
        
        if not partial_lower:
            # Show popular snippets when empty
            popular = ["prime", "palindrome", "fibonacci", "factorial", "binary_search"]
            for pattern_name in popular:
                pattern_data = self.COMMON_PATTERNS[pattern_name]
                suggestions.append({
                    "name": pattern_name.replace("_", " ").title(),
                    "code": pattern_data["completion"],
                    "description": f"Implement {pattern_name.replace('_', ' ')}"
                })
            return suggestions
        
        # Find matching patterns
        for pattern_name, pattern_data in self.COMMON_PATTERNS.items():
            for trigger in pattern_data["triggers"]:
                if trigger.lower().startswith(partial_lower) or partial_lower in trigger.lower():
                    suggestions.append({
                        "name": pattern_name.replace("_", " ").title(),
                        "code": pattern_data["completion"],
                        "description": f"Implement {pattern_name.replace('_', ' ')}",
                        "match_score": self._calculate_match_score(partial_lower, trigger.lower())
                    })
                    break
        
        # Sort by match score
        suggestions.sort(key=lambda x: x.get("match_score", 0), reverse=True)
        return suggestions[:5]
    
    def _calculate_match_score(self, partial: str, trigger: str) -> float:
        """Calculate how well the partial matches the trigger"""
        if partial == trigger:
            return 1.0
        if trigger.startswith(partial):
            return 0.9
        if partial in trigger:
            return 0.7
        
        # Calculate fuzzy match
        matches = sum(1 for c in partial if c in trigger)
        return matches / len(trigger) if trigger else 0
    
    def suggest_next_lines(self, code: str, num_lines: int = 3) -> Optional[str]:
        """Suggest next lines based on code context"""
        if not code.strip():
            return None
        
        lines = code.split('\n')
        last_line = lines[-1].strip()
        
        # Detect patterns and suggest continuations
        suggestions = []
        
        # If there's a function without implementation
        if last_line.startswith("def ") and last_line.endswith(":"):
            func_match = re.search(r'def\s+(\w+)\s*\((.*?)\)', last_line)
            if func_match:
                func_name = func_match.group(1)
                params = func_match.group(2)
                
                # Smart suggestions based on function name
                if "sum" in func_name.lower() or "add" in func_name.lower():
                    return f'    """Add numbers together"""\n    return sum({params.split(",")[0].strip()} for _ in range(10))'
                elif "print" in func_name.lower():
                    return f'    """Print information"""\n    print({params.split(",")[0].strip() if params else ""})'
                else:
                    return f'    """TODO: Implement {func_name}"""\n    pass'
        
        # Suggest loop bodies
        if "for " in last_line and last_line.endswith(":"):
            var_match = re.search(r'for\s+(\w+)', last_line)
            if var_match:
                var = var_match.group(1)
                return f'    print({var})\n    # Process {var} here'
        
        return None
