import ast
import re
import logging
from typing import List, Dict, Any, Optional
import jedi

class AIService:
    """Service for AI-powered code suggestions using local models only"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_suggestions(self, code: str, language: str, provider: str = "local") -> List[Dict[str, Any]]:
        """Get code suggestions using local intelligence only"""
        try:
            return self._get_local_suggestions(code, language)
        except Exception as e:
            self.logger.error(f"Error getting suggestions: {e}")
            return []
    
    def _get_local_suggestions(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Get local code suggestions using language-specific analyzers"""
        suggestions = []
        
        if language == "python":
            suggestions.extend(self._get_python_suggestions(code))
        elif language == "javascript":
            suggestions.extend(self._get_javascript_suggestions(code))
        elif language == "java":
            suggestions.extend(self._get_java_suggestions(code))
        elif language == "cpp":
            suggestions.extend(self._get_cpp_suggestions(code))
        
        return suggestions[:5]
    
    def _get_python_suggestions(self, code: str) -> List[Dict[str, Any]]:
        """Get Python-specific suggestions using Jedi and AST analysis"""
        suggestions = []
        
        try:
            script = jedi.Script(code=code)
            completions = script.completions()
            
            for completion in completions[:3]:
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
        
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if not ast.get_docstring(node):
                        suggested_code = self._add_python_docstring(code, node)
                        suggestions.append({
                            "title": f"Add docstring to {node.name}()",
                            "description": "Functions should have docstrings describing their purpose",
                            "code": suggested_code,
                            "type": "documentation"
                        })
                        break
                
                if isinstance(node, ast.ExceptHandler) and node.type is None:
                    suggestions.append({
                        "title": "Specify exception type",
                        "description": f"Bare except clauses should specify exception types",
                        "code": code,
                        "type": "best_practice"
                    })
                    break
        except:
            pass
        
        lines = code.split('\n')
        long_lines = [i+1 for i, line in enumerate(lines) if len(line) > 79]
        if long_lines:
            suggestions.append({
                "title": "Fix line length",
                "description": f"Lines {long_lines[:3]} exceed PEP 8 recommendation (79 chars)",
                "code": code,
                "type": "style"
            })
        
        if not any('import' in line for line in lines):
            suggestions.append({
                "title": "Consider imports",
                "description": "Add necessary import statements at the top",
                "code": code,
                "type": "structure"
            })
        
        return suggestions
    
    def _add_python_docstring(self, code: str, node: ast.FunctionDef) -> str:
        """Add a docstring to a Python function"""
        lines = code.split('\n')
        func_line = node.lineno - 1
        
        if func_line + 1 < len(lines):
            indent = len(lines[func_line]) - len(lines[func_line].lstrip())
            docstring = f'{" " * (indent + 4)}"""Function description."""'
            lines.insert(func_line + 1, docstring)
        
        return '\n'.join(lines)
    
    def _get_javascript_suggestions(self, code: str) -> List[Dict[str, Any]]:
        """Get JavaScript-specific suggestions"""
        suggestions = []
        lines = code.split('\n')
        
        if any(re.search(r'\bvar\s+\w+', line) for line in lines):
            suggestions.append({
                "title": "Use let/const instead of var",
                "description": "Modern JavaScript prefers let and const over var for better scoping",
                "code": re.sub(r'\bvar\s+', 'const ', code),
                "type": "modernization"
            })
        
        if any(re.search(r'[^=!]==[^=]', line) for line in lines):
            suggestions.append({
                "title": "Use strict equality (===)",
                "description": "Use === for type-safe comparisons instead of ==",
                "code": code,
                "type": "best_practice"
            })
        
        if 'function' in code and '=>' not in code:
            suggestions.append({
                "title": "Consider arrow functions",
                "description": "Arrow functions provide cleaner syntax for callbacks",
                "code": code,
                "type": "modernization"
            })
        
        if any('console.log' in line for line in lines):
            suggestions.append({
                "title": "Add error handling",
                "description": "Consider wrapping console.log calls in try-catch blocks",
                "code": code,
                "type": "robustness"
            })
        
        return suggestions
    
    def _get_java_suggestions(self, code: str) -> List[Dict[str, Any]]:
        """Get Java-specific suggestions"""
        suggestions = []
        lines = code.split('\n')
        
        if not any('public class' in line or 'class' in line for line in lines):
            suggestions.append({
                "title": "Add class definition",
                "description": "Java code should be organized in classes",
                "code": code,
                "type": "structure"
            })
        
        if any('System.out.println' in line for line in lines) and not any('try' in line for line in lines):
            suggestions.append({
                "title": "Add exception handling",
                "description": "Consider adding try-catch blocks for robust error handling",
                "code": code,
                "type": "robustness"
            })
        
        if not any(re.search(r'(public|private|protected)', line) for line in lines if 'class' in line):
            suggestions.append({
                "title": "Add access modifiers",
                "description": "Classes and methods should have explicit access modifiers",
                "code": code,
                "type": "best_practice"
            })
        
        return suggestions
    
    def _get_cpp_suggestions(self, code: str) -> List[Dict[str, Any]]:
        """Get C++ specific suggestions"""
        suggestions = []
        lines = code.split('\n')
        
        has_iostream = any('#include <iostream>' in line for line in lines)
        has_cout = any('cout' in line for line in lines)
        
        if has_cout and not has_iostream:
            suggestions.append({
                "title": "Add #include <iostream>",
                "description": "cout requires iostream header",
                "code": "#include <iostream>\n\n" + code,
                "type": "fix"
            })
        
        if 'using namespace std' not in code and 'std::' not in code and has_cout:
            suggestions.append({
                "title": "Add namespace declaration",
                "description": "Use 'using namespace std;' or prefix with 'std::'",
                "code": "#include <iostream>\nusing namespace std;\n\n" + code,
                "type": "improvement"
            })
        
        if not any('int main' in line for line in lines):
            suggestions.append({
                "title": "Add main function",
                "description": "C++ programs need a main() function as entry point",
                "code": code,
                "type": "structure"
            })
        
        return suggestions
    
    def get_code_explanation(self, code: str, language: str, provider: str = "local") -> str:
        """Get explanation of code functionality using local analysis"""
        try:
            if language == "python":
                return self._explain_python_code(code)
            elif language == "javascript":
                return self._explain_javascript_code(code)
            elif language == "java":
                return self._explain_java_code(code)
            elif language == "cpp":
                return self._explain_cpp_code(code)
        except Exception as e:
            self.logger.error(f"Error explaining code: {e}")
        
        return "Local code analysis available. This code defines functions and logic for your program."
    
    def _explain_python_code(self, code: str) -> str:
        """Explain Python code using AST analysis"""
        explanation = []
        
        try:
            tree = ast.parse(code)
            
            functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            imports = [node.names[0].name for node in ast.walk(tree) if isinstance(node, ast.Import)]
            
            if imports:
                explanation.append(f"Imports: {', '.join(imports)}")
            if classes:
                explanation.append(f"Defines classes: {', '.join(classes)}")
            if functions:
                explanation.append(f"Defines functions: {', '.join(functions)}")
            
            return " | ".join(explanation) if explanation else "Python code structure"
        except:
            return "Python code with basic operations"
    
    def _explain_javascript_code(self, code: str) -> str:
        """Explain JavaScript code"""
        functions = re.findall(r'function\s+(\w+)', code)
        arrow_funcs = re.findall(r'const\s+(\w+)\s*=.*=>', code)
        
        if functions or arrow_funcs:
            all_funcs = functions + arrow_funcs
            return f"JavaScript code defining: {', '.join(all_funcs)}"
        return "JavaScript code with logic and operations"
    
    def _explain_java_code(self, code: str) -> str:
        """Explain Java code"""
        classes = re.findall(r'class\s+(\w+)', code)
        methods = re.findall(r'(?:public|private|protected)?\s*(?:static\s+)?[\w<>\[\]]+\s+(\w+)\s*\(', code)
        
        if classes:
            return f"Java class: {classes[0]}" + (f" with methods: {', '.join(methods[:3])}" if methods else "")
        return "Java code structure"
    
    def _explain_cpp_code(self, code: str) -> str:
        """Explain C++ code"""
        has_main = 'int main' in code
        classes = re.findall(r'class\s+(\w+)', code)
        includes = re.findall(r'#include\s*<(\w+)>', code)
        
        parts = []
        if includes:
            parts.append(f"Uses: {', '.join(includes)}")
        if classes:
            parts.append(f"Classes: {', '.join(classes)}")
        if has_main:
            parts.append("Contains main function")
        
        return " | ".join(parts) if parts else "C++ code structure"
    
    def generate_documentation(self, code: str, language: str) -> str:
        """Generate documentation for the code using local analysis"""
        try:
            if language == "python":
                return self._generate_python_docs(code)
            else:
                return f"# Code Documentation\n\n{self.get_code_explanation(code, language)}"
        except Exception as e:
            self.logger.error(f"Error generating documentation: {e}")
            return "Documentation generation available for local code analysis."
    
    def _generate_python_docs(self, code: str) -> str:
        """Generate documentation for Python code"""
        try:
            tree = ast.parse(code)
            docs = ["# Code Documentation\n"]
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    args = [arg.arg for arg in node.args.args]
                    docs.append(f"## Function: {node.name}")
                    docs.append(f"- Arguments: {', '.join(args) if args else 'None'}")
                    docstring = ast.get_docstring(node)
                    if docstring:
                        docs.append(f"- Description: {docstring}")
                    docs.append("")
                
                elif isinstance(node, ast.ClassDef):
                    docs.append(f"## Class: {node.name}")
                    docstring = ast.get_docstring(node)
                    if docstring:
                        docs.append(f"- Description: {docstring}")
                    docs.append("")
            
            return "\n".join(docs)
        except:
            return "# Documentation\n\nPython code analysis"
