import re
import os
from typing import List, Set

class SecurityManager:
    """Manager for code execution security policies"""
    
    def __init__(self):
        # Dangerous patterns that should be blocked
        self.dangerous_patterns = {
            "python": [
                r'\beval\s*\(',
                r'\bexec\s*\(',
                r'\b__import__\s*\(',
                r'\bgetattr\s*\(',
                r'\bsetattr\s*\(',
                r'\bdelattr\s*\(',
                r'\bglobals\s*\(',
                r'\blocals\s*\(',
                r'\bvars\s*\(',
                r'\bdir\s*\(',
                r'\bopen\s*\(',
                r'subprocess\.',
                r'os\.',
                r'sys\.',
                r'\bfile\s*\(',
                r'\binput\s*\(',
                r'\braw_input\s*\(',
                r'import\s+os',
                r'import\s+sys',
                r'import\s+subprocess',
                r'from\s+os\s+import',
                r'from\s+sys\s+import',
                r'from\s+subprocess\s+import',
            ],
            "javascript": [
                r'\beval\s*\(',
                r'Function\s*\(',
                r'setTimeout\s*\(',
                r'setInterval\s*\(',
                r'document\.write\s*\(',
                r'innerHTML\s*=',
                r'outerHTML\s*=',
                r'location\.',
                r'window\.',
                r'XMLHttpRequest',
                r'fetch\s*\(',
                r'require\s*\(',
            ],
            "java": [
                r'Runtime\.getRuntime\s*\(\)',
                r'ProcessBuilder',
                r'System\.exit\s*\(',
                r'Class\.forName\s*\(',
                r'Method\.invoke\s*\(',
                r'java\.io\.File',
                r'java\.nio\.file',
                r'java\.lang\.reflect',
                r'java\.net\.URL',
                r'java\.net\.Socket',
            ],
            "cpp": [
                r'system\s*\(',
                r'exec\s*\(',
                r'popen\s*\(',
                r'#include\s*<cstdlib>',
                r'#include\s*<unistd\.h>',
                r'#include\s*<sys/',
                r'malloc\s*\(',
                r'free\s*\(',
                r'delete\s+',
                r'new\s+\w+\[',
            ]
        }
        
        # Allowed standard library functions
        self.allowed_imports = {
            "python": {
                'math', 'random', 'datetime', 'json', 'urllib', 'hashlib',
                'base64', 'itertools', 'functools', 'collections', 'typing',
                'dataclasses', 'enum', 'decimal', 'fractions'
            },
            "javascript": {
                'Math', 'Date', 'JSON', 'Array', 'Object', 'String', 'Number', 'Boolean'
            }
        }
    
    def is_code_safe(self, code: str, language: str) -> bool:
        """Check if code is safe to execute"""
        try:
            # Check for dangerous patterns
            if self._contains_dangerous_patterns(code, language):
                return False
            
            # Check imports/includes
            if not self._are_imports_safe(code, language):
                return False
            
            # Check code length (prevent extremely long code)
            if len(code) > 10000:  # 10KB limit
                return False
            
            # Language-specific checks
            if language == "python":
                return self._is_python_safe(code)
            elif language == "javascript":
                return self._is_javascript_safe(code)
            elif language == "java":
                return self._is_java_safe(code)
            elif language == "cpp":
                return self._is_cpp_safe(code)
            
            return True
            
        except Exception:
            # If any error occurs during security check, err on the side of caution
            return False
    
    def _contains_dangerous_patterns(self, code: str, language: str) -> bool:
        """Check if code contains dangerous patterns"""
        patterns = self.dangerous_patterns.get(language, [])
        
        for pattern in patterns:
            if re.search(pattern, code, re.IGNORECASE | re.MULTILINE):
                return True
        
        return False
    
    def _are_imports_safe(self, code: str, language: str) -> bool:
        """Check if imports/includes are safe"""
        if language == "python":
            # Extract import statements
            import_matches = re.findall(r'^(?:from\s+(\w+(?:\.\w+)*)\s+)?import\s+(.+)$', code, re.MULTILINE)
            
            for module, items in import_matches:
                base_module = (module or items.split('.')[0]).split('.')[0]
                allowed = self.allowed_imports.get(language, set())
                
                if base_module not in allowed and base_module not in {
                    'builtins', '', 'typing', 'dataclasses', 'enum'
                }:
                    # Check if it's a dangerous module
                    dangerous_modules = {
                        'os', 'sys', 'subprocess', 'importlib', '__builtin__',
                        'ctypes', 'marshal', 'pickle', 'shelve', 'socket',
                        'urllib2', 'httplib', 'ftplib', 'telnetlib', 'smtplib'
                    }
                    
                    if base_module in dangerous_modules:
                        return False
        
        elif language == "cpp":
            # Check for dangerous includes
            dangerous_includes = {
                'cstdlib', 'unistd.h', 'sys/', 'windows.h', 'winbase.h'
            }
            
            includes = re.findall(r'#include\s*[<"]([^>"]+)[>"]', code)
            for include in includes:
                if any(dangerous in include for dangerous in dangerous_includes):
                    return False
        
        return True
    
    def _is_python_safe(self, code: str) -> bool:
        """Python-specific safety checks"""
        # Check for attribute access on dangerous objects
        dangerous_attrs = [
            r'\.__.*__',  # Dunder methods
            r'\.func_code',
            r'\.gi_code',
            r'\.cr_code',
        ]
        
        for pattern in dangerous_attrs:
            if re.search(pattern, code):
                return False
        
        # Check for dangerous built-ins usage
        if re.search(r'\b(compile|eval|exec|globals|locals|vars)\s*\(', code):
            return False
        
        return True
    
    def _is_javascript_safe(self, code: str) -> bool:
        """JavaScript-specific safety checks"""
        # Check for prototype manipulation
        if re.search(r'\.prototype\s*[=\[]', code):
            return False
        
        # Check for constructor access
        if re.search(r'\.constructor', code):
            return False
        
        return True
    
    def _is_java_safe(self, code: str) -> bool:
        """Java-specific safety checks"""
        # Check for reflection usage
        if re.search(r'\.getClass\s*\(\)', code):
            return False
        
        # Check for native method calls
        if re.search(r'\bnative\s+', code):
            return False
        
        return True
    
    def _is_cpp_safe(self, code: str) -> bool:
        """C++-specific safety checks"""
        # Check for pointer arithmetic beyond basic usage
        if re.search(r'\*\s*\(\s*\w+\s*\+', code):
            return False
        
        # Check for inline assembly
        if re.search(r'asm\s*\(', code, re.IGNORECASE):
            return False
        
        return True
    
    def get_security_violations(self, code: str, language: str) -> List[str]:
        """Get list of security violations in code"""
        violations = []
        
        patterns = self.dangerous_patterns.get(language, [])
        for pattern in patterns:
            if re.search(pattern, code, re.IGNORECASE | re.MULTILINE):
                violations.append(f"Dangerous pattern detected: {pattern}")
        
        if len(code) > 10000:
            violations.append("Code too long (>10KB)")
        
        return violations
    
    def sanitize_output(self, output: str) -> str:
        """Sanitize execution output to remove potential sensitive information"""
        # Remove file system paths
        output = re.sub(r'/[/\w.-]+', '[PATH_REMOVED]', output)
        output = re.sub(r'[A-Za-z]:\\[\\w.-]+', '[PATH_REMOVED]', output)
        
        # Remove IP addresses
        output = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '[IP_REMOVED]', output)
        
        # Limit output length
        if len(output) > 5000:
            output = output[:5000] + "\n... [Output truncated for security]"
        
        return output
