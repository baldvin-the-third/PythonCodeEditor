import ast
import re
from typing import List, Dict, Optional, Tuple
import jedi

class SmartCodeCompletion:
    """Advanced code completion using pattern analysis and AST parsing"""
    
    def __init__(self):
        self.code_patterns = self._load_all_patterns()
        
    def _load_all_patterns(self) -> Dict:
        """Load comprehensive code patterns for intelligent completion"""
        return {
            # Mathematical and algorithmic patterns
            "is_prime": {
                "triggers": ["def is_prime", "prime", "check prime"],
                "context_keywords": ["prime", "number", "check"],
                "code": """def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True"""
            },
            
            "is_palindrome": {
                "triggers": ["def is_palindrome", "palindrome", "check palindrome"],
                "context_keywords": ["palindrome", "string", "reverse"],
                "code": """def is_palindrome(s):
    s = ''.join(c.lower() for c in s if c.isalnum())
    return s == s[::-1]"""
            },
            
            "fibonacci_recursive": {
                "triggers": ["def fibonacci", "fib", "fibonacci sequence"],
                "context_keywords": ["fibonacci", "fib", "sequence"],
                "code": """def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)"""
            },
            
            "fibonacci_iterative": {
                "triggers": ["fib iter", "fibonacci list"],
                "context_keywords": ["fibonacci", "list", "sequence"],
                "code": """def fibonacci_sequence(n):
    fib = [0, 1]
    for i in range(2, n):
        fib.append(fib[i-1] + fib[i-2])
    return fib"""
            },
            
            "factorial": {
                "triggers": ["def factorial", "factorial", "fact"],
                "context_keywords": ["factorial", "multiply"],
                "code": """def factorial(n):
    if n == 0 or n == 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result"""
            },
            
            "binary_search": {
                "triggers": ["def binary_search", "binary search", "bsearch"],
                "context_keywords": ["binary", "search", "sorted", "array"],
                "code": """def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1"""
            },
            
            "bubble_sort": {
                "triggers": ["def bubble_sort", "bubble sort"],
                "context_keywords": ["bubble", "sort", "swap"],
                "code": """def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break
    return arr"""
            },
            
            "merge_sort": {
                "triggers": ["def merge_sort", "merge sort"],
                "context_keywords": ["merge", "sort", "divide"],
                "code": """def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result"""
            },
            
            "quick_sort": {
                "triggers": ["def quick_sort", "quick sort", "qsort"],
                "context_keywords": ["quick", "sort", "pivot"],
                "code": """def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)"""
            },
            
            "linear_search": {
                "triggers": ["def linear_search", "linear search", "find"],
                "context_keywords": ["linear", "search", "find"],
                "code": """def linear_search(arr, target):
    for i in range(len(arr)):
        if arr[i] == target:
            return i
    return -1"""
            },
            
            "reverse_string": {
                "triggers": ["def reverse", "reverse string"],
                "context_keywords": ["reverse", "string"],
                "code": """def reverse_string(s):
    return s[::-1]"""
            },
            
            "count_vowels": {
                "triggers": ["def count_vowels", "count vowel", "vowels"],
                "context_keywords": ["count", "vowel"],
                "code": """def count_vowels(s):
    vowels = 'aeiouAEIOU'
    return sum(1 for char in s if char in vowels)"""
            },
            
            "gcd": {
                "triggers": ["def gcd", "gcd", "greatest common"],
                "context_keywords": ["gcd", "divisor", "common"],
                "code": """def gcd(a, b):
    while b:
        a, b = b, a % b
    return a"""
            },
            
            "lcm": {
                "triggers": ["def lcm", "lcm", "least common"],
                "context_keywords": ["lcm", "multiple", "common"],
                "code": """def lcm(a, b):
    return abs(a * b) // gcd(a, b)

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a"""
            },
            
            "sum_of_digits": {
                "triggers": ["def sum_digits", "sum of digits"],
                "context_keywords": ["sum", "digit"],
                "code": """def sum_of_digits(n):
    return sum(int(digit) for digit in str(abs(n)))"""
            },
            
            "is_even": {
                "triggers": ["def is_even", "even number"],
                "context_keywords": ["even", "number"],
                "code": """def is_even(n):
    return n % 2 == 0"""
            },
            
            "is_odd": {
                "triggers": ["def is_odd", "odd number"],
                "context_keywords": ["odd", "number"],
                "code": """def is_odd(n):
    return n % 2 != 0"""
            },
            
            "power": {
                "triggers": ["def power", "exponent"],
                "context_keywords": ["power", "exponent"],
                "code": """def power(base, exp):
    result = 1
    for _ in range(exp):
        result *= base
    return result"""
            },
            
            "max_in_list": {
                "triggers": ["def max", "find max", "maximum"],
                "context_keywords": ["max", "maximum", "largest"],
                "code": """def find_max(arr):
    if not arr:
        return None
    max_val = arr[0]
    for num in arr[1:]:
        if num > max_val:
            max_val = num
    return max_val"""
            },
            
            "min_in_list": {
                "triggers": ["def min", "find min", "minimum"],
                "context_keywords": ["min", "minimum", "smallest"],
                "code": """def find_min(arr):
    if not arr:
        return None
    min_val = arr[0]
    for num in arr[1:]:
        if num < min_val:
            min_val = num
    return min_val"""
            },
            
            "remove_duplicates": {
                "triggers": ["def remove_duplicates", "unique", "duplicates"],
                "context_keywords": ["remove", "duplicate", "unique"],
                "code": """def remove_duplicates(arr):
    return list(set(arr))"""
            },
            
            "find_duplicates": {
                "triggers": ["def find_duplicates", "duplicates"],
                "context_keywords": ["find", "duplicate"],
                "code": """def find_duplicates(arr):
    seen = set()
    duplicates = set()
    for item in arr:
        if item in seen:
            duplicates.add(item)
        else:
            seen.add(item)
    return list(duplicates)"""
            },
            
            "flatten_list": {
                "triggers": ["def flatten", "flatten list"],
                "context_keywords": ["flatten", "nested", "list"],
                "code": """def flatten_list(nested_list):
    result = []
    for item in nested_list:
        if isinstance(item, list):
            result.extend(flatten_list(item))
        else:
            result.append(item)
    return result"""
            },
            
            "matrix_transpose": {
                "triggers": ["def transpose", "matrix transpose"],
                "context_keywords": ["transpose", "matrix"],
                "code": """def transpose(matrix):
    return [[matrix[j][i] for j in range(len(matrix))] 
            for i in range(len(matrix[0]))]"""
            },
            
            "read_file": {
                "triggers": ["open(", "read file", "with open"],
                "context_keywords": ["read", "file", "open"],
                "code": """with open('filename.txt', 'r') as f:
    content = f.read()"""
            },
            
            "write_file": {
                "triggers": ["write file", "save file"],
                "context_keywords": ["write", "file", "save"],
                "code": """with open('filename.txt', 'w') as f:
    f.write('content')"""
            },
            
            "try_except": {
                "triggers": ["try:", "try except"],
                "context_keywords": ["try", "except", "error"],
                "code": """try:
    # Your code here
    pass
except Exception as e:
    print(f"Error: {e}")"""
            },
            
            "class_definition": {
                "triggers": ["class ", "define class"],
                "context_keywords": ["class"],
                "code": """class MyClass:
    def __init__(self, param):
        self.param = param
    
    def method(self):
        return self.param"""
            },
        }
    
    def analyze_and_predict(self, code: str, cursor_line: int = -1) -> Optional[Dict]:
        """Analyze code and predict next lines intelligently"""
        if not code.strip():
            return self._get_starter_suggestion()
        
        lines = code.split('\n')
        last_line = lines[-1].strip() if lines else ""
        code_lower = code.lower()
        
        # Check for exact pattern matches
        for pattern_name, pattern in self.code_patterns.items():
            for trigger in pattern["triggers"]:
                if trigger.lower() in last_line.lower() or trigger.lower() in code_lower:
                    # Check if pattern not already in code
                    if pattern["code"] not in code:
                        return {
                            "completion": pattern["code"],
                            "type": "pattern",
                            "confidence": 0.95,
                            "description": f"Complete {pattern_name.replace('_', ' ')}"
                        }
        
        # Context-aware next line prediction
        next_line = self._predict_next_line(lines)
        if next_line:
            return next_line
        
        # Use Jedi for intelligent completions
        jedi_completion = self._get_jedi_completion(code)
        if jedi_completion:
            return jedi_completion
        
        return None
    
    def _predict_next_line(self, lines: List[str]) -> Optional[Dict]:
        """Predict the next line based on context"""
        if not lines:
            return None
        
        last_line = lines[-1].strip()
        
        # Function definition - suggest docstring and body
        if last_line.startswith("def ") and last_line.endswith(":"):
            func_match = re.search(r'def\s+(\w+)\s*\((.*?)\)', last_line)
            if func_match:
                func_name = func_match.group(1)
                params = func_match.group(2)
                
                # Smart suggestions based on function name
                if "prime" in func_name.lower():
                    return {
                        "completion": """    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True""",
                        "type": "next_line",
                        "confidence": 0.9,
                        "description": "Prime number check implementation"
                    }
                elif "palindrome" in func_name.lower():
                    return {
                        "completion": """    s = ''.join(c.lower() for c in s if c.isalnum())
    return s == s[::-1]""",
                        "type": "next_line",
                        "confidence": 0.9,
                        "description": "Palindrome check implementation"
                    }
                elif "factorial" in func_name.lower():
                    return {
                        "completion": """    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)""",
                        "type": "next_line",
                        "confidence": 0.9,
                        "description": "Factorial implementation"
                    }
                elif "fibonacci" in func_name.lower() or "fib" in func_name.lower():
                    return {
                        "completion": """    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)""",
                        "type": "next_line",
                        "confidence": 0.9,
                        "description": "Fibonacci implementation"
                    }
                elif "sum" in func_name.lower():
                    return {
                        "completion": f"""    \"\"\"Calculate sum\"\"\"\n    return sum({params.split(',')[0].strip() if params else 'values'})""",
                        "type": "next_line",
                        "confidence": 0.8,
                        "description": "Sum calculation"
                    }
                else:
                    return {
                        "completion": f'    """TODO: Implement {func_name}"""\n    pass',
                        "type": "next_line",
                        "confidence": 0.7,
                        "description": "Add function body"
                    }
        
        # Class definition - suggest __init__
        if last_line.startswith("class ") and last_line.endswith(":"):
            class_name = re.search(r'class\s+(\w+)', last_line)
            if class_name:
                return {
                    "completion": """    def __init__(self):
        pass""",
                    "type": "next_line",
                    "confidence": 0.85,
                    "description": "Add constructor"
                }
        
        # For loop - suggest body
        if last_line.startswith("for ") and last_line.endswith(":"):
            var_match = re.search(r'for\s+(\w+)', last_line)
            if var_match:
                var = var_match.group(1)
                return {
                    "completion": f'    print({var})',
                    "type": "next_line",
                    "confidence": 0.75,
                    "description": "Add loop body"
                }
        
        # If statement - suggest body
        if last_line.startswith("if ") and last_line.endswith(":"):
            return {
                "completion": '    pass',
                "type": "next_line",
                "confidence": 0.7,
                "description": "Add if body"
            }
        
        # While loop - suggest body
        if last_line.startswith("while ") and last_line.endswith(":"):
            return {
                "completion": '    pass',
                "type": "next_line",
                "confidence": 0.7,
                "description": "Add while body"
            }
        
        return None
    
    def _get_jedi_completion(self, code: str) -> Optional[Dict]:
        """Use Jedi for intelligent Python completions"""
        try:
            script = jedi.Script(code=code)
            completions = script.complete()  # type: ignore
            
            if completions:
                top_completion = completions[0]
                if hasattr(top_completion, 'complete') and top_completion.complete:
                    return {
                        "completion": code + top_completion.complete,
                        "type": "jedi",
                        "confidence": 0.6,
                        "description": f"Complete: {top_completion.name}"
                    }
        except (AttributeError, Exception):
            pass
        
        return None
    
    def _get_starter_suggestion(self) -> Dict:
        """Suggest starter code when editor is empty"""
        return {
            "completion": """def greet(name):
    return f"Hello, {name}!"

print(greet("World"))""",
            "type": "starter",
            "confidence": 0.5,
            "description": "Start with a simple function"
        }
    
    def get_all_suggestions(self, partial_code: str) -> List[Dict]:
        """Get multiple suggestions for autocomplete dropdown"""
        suggestions = []
        partial_lower = partial_code.lower().strip()
        
        if not partial_lower:
            # Show popular patterns
            popular = ["is_prime", "is_palindrome", "fibonacci_recursive", 
                      "factorial", "binary_search", "bubble_sort"]
            for pattern_name in popular:
                if pattern_name in self.code_patterns:
                    pattern = self.code_patterns[pattern_name]
                    suggestions.append({
                        "name": pattern_name.replace("_", " ").title(),
                        "code": pattern["code"],
                        "description": f"Implement {pattern_name.replace('_', ' ')}"
                    })
            return suggestions
        
        # Find matching patterns
        for pattern_name, pattern in self.code_patterns.items():
            match_score = 0
            
            # Check triggers
            for trigger in pattern["triggers"]:
                if partial_lower in trigger.lower():
                    match_score = max(match_score, 0.9)
                elif any(word in trigger.lower() for word in partial_lower.split()):
                    match_score = max(match_score, 0.7)
            
            # Check context keywords
            for keyword in pattern.get("context_keywords", []):
                if keyword.lower() in partial_lower:
                    match_score = max(match_score, 0.6)
            
            if match_score > 0:
                suggestions.append({
                    "name": pattern_name.replace("_", " ").title(),
                    "code": pattern["code"],
                    "description": f"Implement {pattern_name.replace('_', ' ')}",
                    "score": match_score
                })
        
        # Sort by score
        suggestions.sort(key=lambda x: x.get("score", 0), reverse=True)
        return suggestions[:10]
