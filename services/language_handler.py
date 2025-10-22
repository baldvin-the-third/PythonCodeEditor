import re
from typing import Dict, List, Optional, Any
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import TerminalFormatter
import ast
import tokenize
import io

class LanguageHandler:
    """Handler for language-specific operations"""
    
    def __init__(self):
        self.language_configs = {
            "python": {
                "extensions": [".py"],
                "keywords": ["def", "class", "if", "else", "elif", "for", "while", "try", "except", "import"],
                "comment_prefix": "#",
                "multiline_comment": ('"""', '"""')
            },
            "javascript": {
                "extensions": [".js", ".jsx"],
                "keywords": ["function", "var", "let", "const", "if", "else", "for", "while", "try", "catch"],
                "comment_prefix": "//",
                "multiline_comment": ('/*', '*/')
            },
            "java": {
                "extensions": [".java"],
                "keywords": ["public", "private", "class", "interface", "if", "else", "for", "while", "try", "catch"],
                "comment_prefix": "//",
                "multiline_comment": ('/*', '*/')
            },
            "cpp": {
                "extensions": [".cpp", ".cc", ".cxx"],
                "keywords": ["int", "char", "float", "double", "class", "struct", "if", "else", "for", "while"],
                "comment_prefix": "//",
                "multiline_comment": ('/*', '*/')
            }
        }
    
    def detect_language(self, code: str) -> str:
        """Detect programming language from code content"""
        if not code.strip():
            return "python"  # Default
        
        # Check for language-specific patterns
        patterns = {
            "python": [
                r"def\s+\w+\s*\(",
                r"import\s+\w+",
                r"from\s+\w+\s+import",
                r"print\s*\(",
                r"if\s+__name__\s*==\s*[\"']__main__[\"']"
            ],
            "javascript": [
                r"function\s+\w+\s*\(",
                r"var\s+\w+\s*=",
                r"let\s+\w+\s*=",
                r"const\s+\w+\s*=",
                r"console\.log\s*\(",
                r"document\.",
                r"window\."
            ],
            "java": [
                r"public\s+class\s+\w+",
                r"public\s+static\s+void\s+main",
                r"System\.out\.println",
                r"import\s+java\.",
                r"@Override"
            ],
            "cpp": [
                r"#include\s*<\w+>",
                r"int\s+main\s*\(",
                r"std::",
                r"cout\s*<<",
                r"cin\s*>>",
                r"using\s+namespace\s+std"
            ]
        }
        
        # Score each language
        scores = {}
        for lang, lang_patterns in patterns.items():
            score = 0
            for pattern in lang_patterns:
                if re.search(pattern, code, re.IGNORECASE | re.MULTILINE):
                    score += 1
            scores[lang] = score
        
        # Return language with highest score
        if scores:
            detected = max(scores.items(), key=lambda x: x[1])
            if detected[1] > 0:
                return detected[0]
        
        return "python"  # Default fallback
    
    def get_syntax_highlighting(self, code: str, language: str) -> str:
        """Get syntax highlighted code"""
        try:
            lexer = get_lexer_by_name(language)
            formatter = TerminalFormatter()
            return highlight(code, lexer, formatter)
        except:
            return code  # Return original if highlighting fails
    
    def extract_functions(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Extract function definitions from code"""
        functions = []
        
        if language == "python":
            try:
                tree = ast.parse(code)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        functions.append({
                            "name": node.name,
                            "line": node.lineno,
                            "args": [arg.arg for arg in node.args.args],
                            "docstring": ast.get_docstring(node)
                        })
            except:
                pass
        
        elif language in ["javascript", "java", "cpp"]:
            # Use regex patterns for other languages
            if language == "javascript":
                pattern = r"function\s+(\w+)\s*\(([^)]*)\)"
            elif language == "java":
                pattern = r"(?:public|private|protected)?\s*(?:static\s+)?[\w<>\[\]]+\s+(\w+)\s*\(([^)]*)\)"
            else:  # cpp
                pattern = r"[\w<>\[\]*&]+\s+(\w+)\s*\(([^)]*)\)"
            
            for match in re.finditer(pattern, code, re.MULTILINE):
                line_num = code[:match.start()].count('\n') + 1
                functions.append({
                    "name": match.group(1),
                    "line": line_num,
                    "args": [arg.strip() for arg in match.group(2).split(',') if arg.strip()],
                    "docstring": None
                })
        
        return functions
    
    def extract_classes(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Extract class definitions from code"""
        classes = []
        
        if language == "python":
            try:
                tree = ast.parse(code)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        classes.append({
                            "name": node.name,
                            "line": node.lineno,
                            "bases": [ast.unparse(base) if hasattr(ast, 'unparse') else str(base) 
                                    for base in node.bases],
                            "docstring": ast.get_docstring(node)
                        })
            except:
                pass
        
        elif language in ["javascript", "java", "cpp"]:
            if language == "javascript":
                pattern = r"class\s+(\w+)(?:\s+extends\s+(\w+))?\s*\{"
            elif language == "java":
                pattern = r"(?:public|private)?\s*class\s+(\w+)(?:\s+extends\s+(\w+))?"
            else:  # cpp
                pattern = r"class\s+(\w+)(?:\s*:\s*(?:public|private|protected)\s+(\w+))?"
            
            for match in re.finditer(pattern, code, re.MULTILINE):
                line_num = code[:match.start()].count('\n') + 1
                classes.append({
                    "name": match.group(1),
                    "line": line_num,
                    "bases": [match.group(2)] if len(match.groups()) > 1 and match.group(2) else [],
                    "docstring": None
                })
        
        return classes
    
    def get_imports(self, code: str, language: str) -> List[str]:
        """Extract import statements from code"""
        imports = []
        
        if language == "python":
            try:
                tree = ast.parse(code)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        module = node.module or ""
                        for alias in node.names:
                            imports.append(f"{module}.{alias.name}" if module else alias.name)
            except:
                pass
        
        else:
            # Use regex for other languages
            patterns = {
                "javascript": [r"import\s+.*?from\s+['\"]([^'\"]+)['\"]", r"require\s*\(\s*['\"]([^'\"]+)['\"]"],
                "java": [r"import\s+([\w.]+)"],
                "cpp": [r"#include\s*[<\"]([^>\"]+)[>\"]"]
            }
            
            for pattern in patterns.get(language, []):
                for match in re.finditer(pattern, code, re.MULTILINE):
                    imports.append(match.group(1))
        
        return imports
    
    def validate_syntax(self, code: str, language: str) -> Dict[str, Any]:
        """Validate syntax for given language"""
        result = {"valid": True, "errors": []}
        
        if language == "python":
            try:
                ast.parse(code)
            except SyntaxError as e:
                result["valid"] = False
                result["errors"].append({
                    "line": e.lineno,
                    "column": e.offset,
                    "message": e.msg,
                    "type": "SyntaxError"
                })
        
        # For other languages, we'd need language-specific parsers
        # This is a simplified validation
        return result
    
    def get_code_metrics(self, code: str, language: str) -> Dict[str, Any]:
        """Get code quality metrics"""
        lines = code.split('\n')
        
        metrics = {
            "total_lines": len(lines),
            "code_lines": len([line for line in lines if line.strip() and not self._is_comment(line, language)]),
            "comment_lines": len([line for line in lines if self._is_comment(line, language)]),
            "blank_lines": len([line for line in lines if not line.strip()]),
            "functions": len(self.extract_functions(code, language)),
            "classes": len(self.extract_classes(code, language))
        }
        
        # Calculate complexity (simplified)
        complexity_keywords = ['if', 'else', 'elif', 'for', 'while', 'try', 'except', 'catch', 'switch', 'case']
        complexity = sum(line.lower().count(keyword) for line in lines for keyword in complexity_keywords)
        metrics["complexity"] = complexity
        
        return metrics
    
    def _is_comment(self, line: str, language: str) -> bool:
        """Check if line is a comment"""
        line = line.strip()
        if not line:
            return False
        
        config = self.language_configs.get(language, {})
        comment_prefix = config.get("comment_prefix", "#")
        
        return line.startswith(comment_prefix)
    
    def get_language_info(self, language: str) -> Dict[str, Any]:
        """Get information about a programming language"""
        return self.language_configs.get(language, {})
