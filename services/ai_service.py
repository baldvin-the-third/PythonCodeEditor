import ast
import re
import logging
from typing import List, Dict, Any, Optional
import jedi

class AlgorithmSuggester:
    """Suggests algorithms and design patterns based on code context"""
    
    ALGORITHMS = {
        "sorting": {
            "quicksort": '''def quicksort(arr):
    """QuickSort: O(n log n) average, O(n²) worst case"""
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)''',
            
            "mergesort": '''def mergesort(arr):
    """MergeSort: O(n log n) guaranteed, stable sorting"""
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = mergesort(arr[:mid])
    right = mergesort(arr[mid:])
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
    return result''',
        },
        
        "search": {
            "binary_search": '''def binary_search(arr, target):
    """Binary Search: O(log n) for sorted arrays"""
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1''',
            
            "dfs": '''def dfs(graph, start, visited=None):
    """Depth-First Search: O(V+E) graph traversal"""
    if visited is None:
        visited = set()
    visited.add(start)
    for neighbor in graph[start]:
        if neighbor not in visited:
            dfs(graph, neighbor, visited)
    return visited''',
        },
        
        "data_structures": {
            "linked_list": '''class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None
    
    def append(self, data):
        if not self.head:
            self.head = Node(data)
            return
        current = self.head
        while current.next:
            current = current.next
        current.next = Node(data)''',
        },
        
        "machine_learning": {
            "linear_regression": '''import numpy as np

class LinearRegression:
    """Simple Linear Regression with Gradient Descent"""
    def __init__(self):
        self.weights = None
        self.bias = None
    
    def fit(self, X, y, learning_rate=0.01, epochs=1000):
        n_samples, n_features = X.shape
        self.weights = np.zeros(n_features)
        self.bias = 0
        
        for _ in range(epochs):
            y_pred = np.dot(X, self.weights) + self.bias
            dw = (1/n_samples) * np.dot(X.T, (y_pred - y))
            db = (1/n_samples) * np.sum(y_pred - y)
            
            self.weights -= learning_rate * dw
            self.bias -= learning_rate * db
    
    def predict(self, X):
        return np.dot(X, self.weights) + self.bias''',
        }
    }

    CODE_SNIPPETS = {
        "file_operations": '''# Read file
with open('file.txt', 'r') as f:
    content = f.read()

# Write file
with open('output.txt', 'w') as f:
    f.write('Hello, World!')''',
        
        "error_handling": '''try:
    result = risky_operation()
except ValueError as e:
    print(f"Value error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
finally:
    cleanup()''',
        
        "decorators": '''from functools import wraps
import time

def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end-start:.4f}s")
        return result
    return wrapper''',
    }

class AIService:
    """Enhanced AI Service with algorithm suggestions and ML integration"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.algorithm_suggester = AlgorithmSuggester()
    
    def get_suggestions(self, code: str, language: str, provider: str = "local") -> List[Dict[str, Any]]:
        """Get enhanced code suggestions with algorithms and snippets"""
        try:
            suggestions = self._get_local_suggestions(code, language)
            
            # Add algorithm suggestions based on context
            algorithm_suggestions = self._suggest_algorithms(code, language)
            suggestions.extend(algorithm_suggestions)
            
            # Add code snippet suggestions
            snippet_suggestions = self._suggest_snippets(code, language)
            suggestions.extend(snippet_suggestions)
            
            return suggestions[:10]  # Return top 10 suggestions
        except Exception as e:
            self.logger.error(f"Error getting suggestions: {e}")
            return []
    
    def _suggest_algorithms(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Suggest relevant algorithms based on code context"""
        suggestions = []
        
        if language != "python":
            return suggestions
        
        code_lower = code.lower()
        
        # Detect sorting needs
        if any(word in code_lower for word in ['sort', 'order', 'arrange']):
            for name, impl in self.algorithm_suggester.ALGORITHMS['sorting'].items():
                suggestions.append({
                    "title": f"Implement {name.replace('_', ' ').title()}",
                    "description": f"Efficient {name} algorithm for sorting data",
                    "code": impl,
                    "type": "algorithm",
                    "category": "sorting"
                })
        
        # Detect search needs
        if any(word in code_lower for word in ['search', 'find', 'locate']):
            for name, impl in self.algorithm_suggester.ALGORITHMS['search'].items():
                suggestions.append({
                    "title": f"Implement {name.replace('_', ' ').upper()}",
                    "description": f"{name.upper()} algorithm for efficient searching",
                    "code": impl,
                    "type": "algorithm",
                    "category": "search"
                })
        
        # Detect data structure needs
        if any(word in code_lower for word in ['list', 'tree', 'graph', 'node']):
            for name, impl in self.algorithm_suggester.ALGORITHMS['data_structures'].items():
                suggestions.append({
                    "title": f"Add {name.replace('_', ' ').title()}",
                    "description": f"Implement {name} data structure",
                    "code": impl,
                    "type": "data_structure",
                    "category": "data_structures"
                })
        
        # Detect ML/AI needs
        if any(word in code_lower for word in ['predict', 'classify', 'train', 'model', 'machine learning', 'ml']):
            for name, impl in self.algorithm_suggester.ALGORITHMS['machine_learning'].items():
                suggestions.append({
                    "title": f"Implement {name.replace('_', ' ').title()}",
                    "description": f"Machine learning: {name} algorithm",
                    "code": impl,
                    "type": "ml_algorithm",
                    "category": "machine_learning"
                })
        
        return suggestions[:5]
    
    def _suggest_snippets(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Suggest useful code snippets"""
        suggestions = []
        
        if language != "python":
            return suggestions
        
        code_lower = code.lower()
        
        # File operation snippets
        if 'file' in code_lower or 'read' in code_lower or 'write' in code_lower:
            suggestions.append({
                "title": "File Operations Pattern",
                "description": "Common file reading and writing patterns",
                "code": self.algorithm_suggester.CODE_SNIPPETS['file_operations'],
                "type": "snippet"
            })
        
        # Error handling
        if 'try' not in code and len(code.split('\n')) > 5:
            suggestions.append({
                "title": "Add Error Handling",
                "description": "Robust error handling pattern",
                "code": self.algorithm_suggester.CODE_SNIPPETS['error_handling'],
                "type": "snippet"
            })
        
        # Decorators
        if 'def' in code and 'decorator' in code_lower:
            suggestions.append({
                "title": "Decorator Pattern",
                "description": "Function decorator with timing example",
                "code": self.algorithm_suggester.CODE_SNIPPETS['decorators'],
                "type": "snippet"
            })
        
        return suggestions[:3]
    
    def _get_local_suggestions(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Get local code suggestions using Jedi"""
        suggestions = []
        
        if language == "python":
            try:
                script = jedi.Script(code=code)
                completions = script.completions()
                
                for completion in completions[:2]:
                    suggestion_code = code
                    if completion.complete:
                        suggestion_code = code + completion.complete
                    
                    suggestions.append({
                        "title": f"Complete: {completion.name}",
                        "description": completion.docstring()[:100] if completion.docstring() else f"Add {completion.type}: {completion.name}",
                        "code": suggestion_code,
                        "type": "completion"
                    })
            except Exception as e:
                self.logger.debug(f"Jedi completion error: {e}")
        
        return suggestions
