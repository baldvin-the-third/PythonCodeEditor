import ast
import re
from typing import Dict, List, Any
from services.language_handler import LanguageHandler

class CodeAnalyzer:
    """Service for analyzing code quality and detecting issues"""
    
    def __init__(self):
        self.language_handler = LanguageHandler()
        self.python_builtin_functions = {
            'print', 'len', 'range', 'str', 'int', 'float', 'list', 'dict', 'set',
            'tuple', 'bool', 'type', 'isinstance', 'hasattr', 'getattr', 'setattr',
            'min', 'max', 'sum', 'abs', 'round', 'sorted', 'reversed', 'enumerate',
            'zip', 'map', 'filter', 'any', 'all'
        }
    
    def analyze_code(self, code: str, language: str) -> Dict[str, Any]:
        """Comprehensive code analysis"""
        analysis = {
            "errors": [],
            "warnings": [],
            "suggestions": [],
            "metrics": {},
            "quality_score": 0,
            "refactoring_suggestions": []
        }
        
        try:
            # Basic syntax validation
            syntax_result = self.language_handler.validate_syntax(code, language)
            if not syntax_result["valid"]:
                analysis["errors"].extend([
                    {"line": err["line"], "message": err["message"], "type": "syntax"}
                    for err in syntax_result["errors"]
                ])
            
            # Get code metrics
            analysis["metrics"] = self.language_handler.get_code_metrics(code, language)
            
            # Language-specific analysis
            if language == "python":
                self._analyze_python(code, analysis)
            elif language == "javascript":
                self._analyze_javascript(code, analysis)
            elif language == "java":
                self._analyze_java(code, analysis)
            elif language == "cpp":
                self._analyze_cpp(code, analysis)
            
            # Calculate quality score
            analysis["quality_score"] = self._calculate_quality_score(analysis)
            
        except Exception as e:
            analysis["errors"].append({
                "line": 0,
                "message": f"Analysis error: {str(e)}",
                "type": "internal"
            })
        
        return analysis
    
    def _analyze_python(self, code: str, analysis: Dict[str, Any]):
        """Python-specific code analysis"""
        lines = code.split('\n')
        
        try:
            tree = ast.parse(code)
            
            # Check for common Python issues
            for node in ast.walk(tree):
                # Unused variables (simplified check)
                if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                    var_name = node.id
                    if var_name.startswith('_') and len(var_name) > 1:
                        continue  # Skip private variables
                    
                    # Check if variable is used later
                    var_used = any(
                        n.id == var_name and isinstance(n.ctx, ast.Load)
                        for n in ast.walk(tree) if isinstance(n, ast.Name)
                    )
                    
                    if not var_used and var_name not in self.python_builtin_functions:
                        analysis["warnings"].append({
                            "line": node.lineno,
                            "message": f"Variable '{var_name}' assigned but never used",
                            "type": "unused_variable"
                        })
                
                # Check for bare except clauses
                if isinstance(node, ast.ExceptHandler) and node.type is None:
                    analysis["warnings"].append({
                        "line": node.lineno,
                        "message": "Bare 'except:' clause should specify exception type",
                        "type": "bare_except"
                    })
                
                # Check for too many arguments
                if isinstance(node, ast.FunctionDef) and len(node.args.args) > 5:
                    analysis["warnings"].append({
                        "line": node.lineno,
                        "message": f"Function '{node.name}' has too many arguments ({len(node.args.args)})",
                        "type": "too_many_args"
                    })
                
                # Check for missing docstrings
                if isinstance(node, ast.FunctionDef) and not ast.get_docstring(node):
                    analysis["suggestions"].append({
                        "line": node.lineno,
                        "message": f"Function '{node.name}' should have a docstring",
                        "type": "missing_docstring"
                    })
        
        except SyntaxError:
            pass  # Already handled in syntax validation
        
        # Check line lengths
        for i, line in enumerate(lines, 1):
            if len(line) > 79:
                analysis["warnings"].append({
                    "line": i,
                    "message": f"Line too long ({len(line)} > 79 characters)",
                    "type": "line_length"
                })
        
        # Check for TODO/FIXME comments
        for i, line in enumerate(lines, 1):
            if re.search(r'#\s*(TODO|FIXME|XXX)', line, re.IGNORECASE):
                analysis["suggestions"].append({
                    "line": i,
                    "message": "Unresolved TODO/FIXME comment",
                    "type": "todo"
                })
        
        # Python-specific refactoring suggestions
        if "import *" in code:
            analysis["refactoring_suggestions"].append(
                "Avoid wildcard imports (import *), import specific functions instead"
            )
        
        if re.search(r'\beval\b', code):
            analysis["refactoring_suggestions"].append(
                "Consider alternatives to eval() for security reasons"
            )
    
    def _analyze_javascript(self, code: str, language: str):
        """JavaScript-specific code analysis"""
        lines = code.split('\n')
        
        # Check for var usage (prefer let/const)
        for i, line in enumerate(lines, 1):
            if re.search(r'\bvar\s+\w+', line):
                analysis["suggestions"].append({
                    "line": i,
                    "message": "Consider using 'let' or 'const' instead of 'var'",
                    "type": "var_usage"
                })
        
        # Check for == vs ===
        for i, line in enumerate(lines, 1):
            if re.search(r'[^=!]==[^=]', line):
                analysis["warnings"].append({
                    "line": i,
                    "message": "Consider using '===' for strict equality",
                    "type": "loose_equality"
                })
    
    def _analyze_java(self, code: str, analysis: Dict[str, Any]):
        """Java-specific code analysis"""
        lines = code.split('\n')
        
        # Check for missing access modifiers
        for i, line in enumerate(lines, 1):
            if re.search(r'^\s*class\s+\w+', line) and not re.search(r'\b(public|private|protected)\b', line):
                analysis["suggestions"].append({
                    "line": i,
                    "message": "Consider adding access modifier to class",
                    "type": "missing_access_modifier"
                })
    
    def _analyze_cpp(self, code: str, analysis: Dict[str, Any]):
        """C++ specific code analysis"""
        lines = code.split('\n')
        
        # Check for missing includes
        has_iostream = any('#include <iostream>' in line for line in lines)
        has_cout = any('cout' in line for line in lines)
        
        if has_cout and not has_iostream:
            analysis["errors"].append({
                "line": 1,
                "message": "Missing #include <iostream> for cout usage",
                "type": "missing_include"
            })
    
    def _calculate_quality_score(self, analysis: Dict[str, Any]) -> int:
        """Calculate overall code quality score (1-10)"""
        base_score = 10
        
        # Deduct points for issues
        error_penalty = len(analysis["errors"]) * 2
        warning_penalty = len(analysis["warnings"]) * 1
        suggestion_penalty = len(analysis["suggestions"]) * 0.5
        
        # Consider code metrics
        metrics = analysis.get("metrics", {})
        
        # Penalize very long functions (if we can detect them)
        if metrics.get("code_lines", 0) > 100:
            base_score -= 1
        
        # Reward documentation
        if metrics.get("comment_lines", 0) > 0:
            comment_ratio = metrics["comment_lines"] / max(metrics.get("code_lines", 1), 1)
            if comment_ratio > 0.1:  # More than 10% comments
                base_score += 1
        
        final_score = base_score - error_penalty - warning_penalty - suggestion_penalty
        return max(1, min(10, int(final_score)))
    
    def get_refactoring_suggestions(self, code: str, language: str) -> List[str]:
        """Get specific refactoring suggestions"""
        suggestions = []
        
        if language == "python":
            # Check for long functions
            functions = self.language_handler.extract_functions(code, language)
            for func in functions:
                # Count lines in function (simplified)
                func_lines = len([line for line in code.split('\n')[func['line']-1:] 
                                if line.strip() and not line.strip().startswith('#')])
                if func_lines > 20:
                    suggestions.append(f"Function '{func['name']}' is too long, consider breaking it down")
            
            # Check for duplicate code patterns
            lines = [line.strip() for line in code.split('\n') if line.strip()]
            for i, line in enumerate(lines):
                if lines.count(line) > 1 and len(line) > 10:
                    suggestions.append(f"Duplicate code found: '{line[:30]}...', consider extracting to function")
                    break
        
        return suggestions
    
    def detect_code_smells(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Detect common code smells"""
        smells = []
        
        # Long parameter lists
        functions = self.language_handler.extract_functions(code, language)
        for func in functions:
            if len(func.get('args', [])) > 4:
                smells.append({
                    "type": "long_parameter_list",
                    "line": func['line'],
                    "message": f"Function '{func['name']}' has too many parameters",
                    "severity": "medium"
                })
        
        # Large classes (simplified check)
        classes = self.language_handler.extract_classes(code, language)
        for cls in classes:
            class_lines = len([line for line in code.split('\n') if line.strip()])
            if class_lines > 100:
                smells.append({
                    "type": "large_class",
                    "line": cls['line'],
                    "message": f"Class '{cls['name']}' is too large",
                    "severity": "high"
                })
        
        return smells
    
    def suggest_performance_improvements(self, code: str, language: str) -> List[str]:
        """Suggest performance improvements"""
        suggestions = []
        
        if language == "python":
            # Check for inefficient loops
            if re.search(r'for\s+\w+\s+in\s+range\s*\(\s*len\s*\(', code):
                suggestions.append("Use 'for item in list' instead of 'for i in range(len(list))'")
            
            # Check for string concatenation in loops
            if re.search(r'for.*:\s*\n\s*.*\+=.*["\']', code, re.MULTILINE):
                suggestions.append("Consider using join() for string concatenation in loops")
        
        elif language == "javascript":
            # Check for inefficient DOM queries
            if 'document.getElementById' in code and code.count('document.getElementById') > 3:
                suggestions.append("Cache DOM element references instead of repeated queries")
        
        return suggestions
