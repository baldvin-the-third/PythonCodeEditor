import subprocess
import threading
import time
import os
import tempfile
import signal
import psutil
from typing import Optional, Dict, Any
import shlex
from utils.security import SecurityManager

class CodeExecutor:
    """Service for secure code execution with resource limits"""
    
    def __init__(self):
        self.current_process = None
        self.security_manager = SecurityManager()
        self.execution_lock = threading.Lock()
    
    def execute_code(self, code: str, language: str) -> str:
        """Execute code in a secure environment"""
        with self.execution_lock:
            try:
                # Stop any running process
                self.stop_execution()
                
                # Validate code security
                if not self.security_manager.is_code_safe(code, language):
                    return "❌ Code execution blocked: Security policy violation"
                
                if language == "python":
                    return self._execute_python(code)
                elif language == "javascript":
                    return self._execute_javascript(code)
                elif language == "java":
                    return self._execute_java(code)
                elif language == "cpp":
                    return self._execute_cpp(code)
                else:
                    return f"❌ Execution not supported for {language}"
                    
            except Exception as e:
                return f"❌ Execution error: {str(e)}"
    
    def _execute_python(self, code: str) -> str:
        """Execute Python code"""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            # Execute with resource limits
            cmd = [
                'python3', 
                temp_file
            ]
            
            result = self._run_with_limits(cmd, timeout=10)
            
            # Cleanup
            try:
                os.unlink(temp_file)
            except:
                pass
                
            return result
            
        except Exception as e:
            return f"❌ Python execution error: {str(e)}"
    
    def _execute_javascript(self, code: str) -> str:
        """Execute JavaScript code using Node.js"""
        try:
            # Check if node is available
            if not self._check_command_available('node'):
                return "❌ Node.js not available for JavaScript execution"
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            cmd = ['node', temp_file]
            result = self._run_with_limits(cmd, timeout=10)
            
            # Cleanup
            try:
                os.unlink(temp_file)
            except:
                pass
                
            return result
            
        except Exception as e:
            return f"❌ JavaScript execution error: {str(e)}"
    
    def _execute_java(self, code: str) -> str:
        """Execute Java code"""
        try:
            if not self._check_command_available('javac') or not self._check_command_available('java'):
                return "❌ Java compiler/runtime not available"
            
            # Extract class name from code
            class_name = self._extract_java_class_name(code)
            if not class_name:
                return "❌ Could not find public class in Java code"
            
            # Create temporary directory
            temp_dir = tempfile.mkdtemp()
            java_file = os.path.join(temp_dir, f"{class_name}.java")
            
            # Write code to file
            with open(java_file, 'w') as f:
                f.write(code)
            
            # Compile
            compile_cmd = ['javac', java_file]
            compile_result = self._run_with_limits(compile_cmd, timeout=30, cwd=temp_dir)
            
            if "error" in compile_result.lower():
                return f"❌ Compilation error:\n{compile_result}"
            
            # Execute
            exec_cmd = ['java', '-cp', temp_dir, class_name]
            result = self._run_with_limits(exec_cmd, timeout=10, cwd=temp_dir)
            
            # Cleanup
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            return result
            
        except Exception as e:
            return f"❌ Java execution error: {str(e)}"
    
    def _execute_cpp(self, code: str) -> str:
        """Execute C++ code"""
        try:
            if not self._check_command_available('g++'):
                return "❌ g++ compiler not available"
            
            # Create temporary files
            cpp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.cpp', delete=False)
            cpp_file.write(code)
            cpp_file.close()
            
            exe_file = tempfile.NamedTemporaryFile(delete=False)
            exe_file.close()
            
            # Compile
            compile_cmd = ['g++', '-o', exe_file.name, cpp_file.name]
            compile_result = self._run_with_limits(compile_cmd, timeout=30)
            
            if compile_result and "error" in compile_result.lower():
                return f"❌ Compilation error:\n{compile_result}"
            
            # Execute
            result = self._run_with_limits([exe_file.name], timeout=10)
            
            # Cleanup
            try:
                os.unlink(cpp_file.name)
                os.unlink(exe_file.name)
            except:
                pass
                
            return result
            
        except Exception as e:
            return f"❌ C++ execution error: {str(e)}"
    
    def _run_with_limits(self, cmd: list, timeout: int = 10, cwd: Optional[str] = None) -> str:
        """Run command with resource limits"""
        try:
            # Set resource limits
            env = os.environ.copy()
            env['PYTHONPATH'] = ''  # Clear Python path for security
            
            self.current_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=cwd,
                env=env,
                preexec_fn=self._set_limits
            )
            
            try:
                output, _ = self.current_process.communicate(timeout=timeout)
                return_code = self.current_process.returncode
                
                if return_code == 0:
                    return f"✅ Execution completed:\n{output}" if output else "✅ Execution completed (no output)"
                else:
                    return f"⚠️ Execution completed with errors (exit code {return_code}):\n{output}"
                    
            except subprocess.TimeoutExpired:
                self.current_process.kill()
                return "❌ Execution timeout - process killed"
                
        except Exception as e:
            return f"❌ Process execution error: {str(e)}"
        finally:
            self.current_process = None
    
    def _set_limits(self):
        """Set resource limits for child process"""
        try:
            import resource
            # Limit CPU time to 10 seconds
            resource.setrlimit(resource.RLIMIT_CPU, (10, 10))
            # Limit memory to 128MB
            resource.setrlimit(resource.RLIMIT_AS, (128 * 1024 * 1024, 128 * 1024 * 1024))
        except:
            pass  # Resource limits not available on all systems
    
    def stop_execution(self):
        """Stop currently running execution"""
        if self.current_process:
            try:
                # Kill process tree
                parent = psutil.Process(self.current_process.pid)
                children = parent.children(recursive=True)
                for child in children:
                    child.kill()
                parent.kill()
            except:
                pass
            self.current_process = None
    
    def _check_command_available(self, command: str) -> bool:
        """Check if a command is available in PATH"""
        try:
            subprocess.run([command, '--version'], 
                         capture_output=True, 
                         timeout=5)
            return True
        except:
            return False
    
    def _extract_java_class_name(self, code: str) -> Optional[str]:
        """Extract public class name from Java code"""
        import re
        match = re.search(r'public\s+class\s+(\w+)', code)
        return match.group(1) if match else None
    
    def get_execution_status(self) -> Dict[str, Any]:
        """Get current execution status"""
        return {
            "is_running": self.current_process is not None and self.current_process.poll() is None,
            "process_id": self.current_process.pid if self.current_process else None
        }
