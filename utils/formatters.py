import subprocess
import tempfile
import os
from typing import Optional

class CodeFormatter:
    """Code formatting utilities for different languages"""
    
    @staticmethod
    def format_python(code: str) -> Optional[str]:
        """Format Python code using Black"""
        try:
            # Try autopep8 first (more lenient)
            result = subprocess.run(
                ['python3', '-m', 'autopep8', '--aggressive', '--aggressive', '-'],
                input=code,
                text=True,
                capture_output=True,
                timeout=10
            )
            
            if result.returncode == 0 and result.stdout:
                return result.stdout
            
            # Fallback to basic formatting
            return CodeFormatter._basic_python_format(code)
            
        except Exception:
            return CodeFormatter._basic_python_format(code)
    
    @staticmethod
    def _basic_python_format(code: str) -> str:
        """Basic Python formatting without external tools"""
        lines = code.split('\n')
        formatted_lines = []
        indent_level = 0
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                formatted_lines.append('')
                continue
            
            # Adjust indent level before adding line
            if stripped.startswith(('else:', 'elif ', 'except', 'except:', 'finally:')):
                current_indent = max(0, indent_level - 1)
            elif stripped.startswith(('def ', 'class ', 'if ', 'for ', 'while ', 'try:', 'with ')):
                current_indent = indent_level
            else:
                current_indent = indent_level
            
            # Add formatted line
            formatted_lines.append('    ' * current_indent + stripped)
            
            # Adjust indent level after adding line
            if stripped.endswith(':') and not stripped.startswith('#'):
                if any(stripped.startswith(kw) for kw in ['def ', 'class ', 'if ', 'for ', 'while ', 'try:', 'with ', 'else:', 'elif ', 'except', 'finally:']):
                    indent_level += 1
            elif stripped in ['pass', 'break', 'continue', 'return'] or (stripped.startswith('return ') and stripped != 'return'):
                if indent_level > 0:
                    indent_level -= 1
        
        return '\n'.join(formatted_lines)
    
    @staticmethod
    def format_javascript(code: str) -> Optional[str]:
        """Format JavaScript code using Prettier (if available)"""
        try:
            # Try prettier if available
            result = subprocess.run(
                ['npx', 'prettier', '--stdin-filepath', 'temp.js'],
                input=code,
                text=True,
                capture_output=True,
                timeout=10
            )
            
            if result.returncode == 0 and result.stdout:
                return result.stdout
                
        except Exception:
            pass
        
        # Basic JavaScript formatting
        return CodeFormatter._basic_javascript_format(code)
    
    @staticmethod
    def _basic_javascript_format(code: str) -> str:
        """Basic JavaScript formatting"""
        lines = code.split('\n')
        formatted_lines = []
        indent_level = 0
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                formatted_lines.append('')
                continue
            
            # Decrease indent for closing braces
            if stripped.startswith('}'):
                indent_level = max(0, indent_level - 1)
            
            # Add formatted line
            formatted_lines.append('  ' * indent_level + stripped)
            
            # Increase indent after opening braces
            if stripped.endswith('{'):
                indent_level += 1
            elif stripped.startswith('}') and stripped.endswith('{'):
                indent_level += 1
        
        return '\n'.join(formatted_lines)
    
    @staticmethod
    def format_java(code: str) -> Optional[str]:
        """Format Java code"""
        # Basic Java formatting (similar to JavaScript but with different conventions)
        return CodeFormatter._basic_java_format(code)
    
    @staticmethod
    def _basic_java_format(code: str) -> str:
        """Basic Java formatting"""
        lines = code.split('\n')
        formatted_lines = []
        indent_level = 0
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                formatted_lines.append('')
                continue
            
            # Decrease indent for closing braces
            if stripped.startswith('}'):
                indent_level = max(0, indent_level - 1)
            
            # Add formatted line
            formatted_lines.append('    ' * indent_level + stripped)
            
            # Increase indent after opening braces
            if stripped.endswith('{'):
                indent_level += 1
        
        return '\n'.join(formatted_lines)
    
    @staticmethod
    def format_cpp(code: str) -> Optional[str]:
        """Format C++ code using clang-format (if available)"""
        try:
            result = subprocess.run(
                ['clang-format', '--style=Google'],
                input=code,
                text=True,
                capture_output=True,
                timeout=10
            )
            
            if result.returncode == 0 and result.stdout:
                return result.stdout
                
        except Exception:
            pass
        
        # Basic C++ formatting
        return CodeFormatter._basic_cpp_format(code)
    
    @staticmethod
    def _basic_cpp_format(code: str) -> str:
        """Basic C++ formatting"""
        lines = code.split('\n')
        formatted_lines = []
        indent_level = 0
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                formatted_lines.append('')
                continue
            
            # Handle preprocessor directives
            if stripped.startswith('#'):
                formatted_lines.append(stripped)
                continue
            
            # Decrease indent for closing braces
            if stripped.startswith('}'):
                indent_level = max(0, indent_level - 1)
            
            # Add formatted line
            formatted_lines.append('    ' * indent_level + stripped)
            
            # Increase indent after opening braces
            if stripped.endswith('{'):
                indent_level += 1
        
        return '\n'.join(formatted_lines)

def format_code(code: str, language: str) -> Optional[str]:
    """Format code for the specified language"""
    formatter_map = {
        'python': CodeFormatter.format_python,
        'javascript': CodeFormatter.format_javascript,
        'java': CodeFormatter.format_java,
        'cpp': CodeFormatter.format_cpp
    }
    
    formatter = formatter_map.get(language)
    if formatter:
        return formatter(code)
    
    return None
