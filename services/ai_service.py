import os
import json
import logging
from typing import List, Dict, Any, Optional
import jedi
from openai import OpenAI
from google import genai
from google.genai import types

class AIService:
    """Service for AI-powered code suggestions using local and cloud models"""
    
    def __init__(self):
        self.openai_client = None
        self.gemini_client = None
        self._setup_clients()
    
    def _setup_clients(self):
        """Initialize AI clients"""
        # Setup OpenAI
        openai_key = os.environ.get("OPENAI_API_KEY")
        if openai_key:
            self.openai_client = OpenAI(api_key=openai_key)
        
        # Setup Gemini
        gemini_key = os.environ.get("GEMINI_API_KEY")
        if gemini_key:
            self.gemini_client = genai.Client(api_key=gemini_key)
    
    def get_suggestions(self, code: str, language: str, provider: str = "local") -> List[Dict[str, Any]]:
        """Get code suggestions based on provider"""
        try:
            if provider == "local":
                return self._get_local_suggestions(code, language)
            elif provider == "openai" and self.openai_client:
                return self._get_openai_suggestions(code, language)
            elif provider == "gemini" and self.gemini_client:
                return self._get_gemini_suggestions(code, language)
            else:
                return self._get_local_suggestions(code, language)
        except Exception as e:
            logging.error(f"Error getting suggestions: {e}")
            return []
    
    def _get_local_suggestions(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Get local code suggestions using Jedi for Python"""
        suggestions = []
        
        if language == "python":
            try:
                # Use Jedi for Python completions
                script = jedi.Script(code=code)
                completions = script.completions()
                
                for completion in completions[:5]:
                    suggestions.append({
                        "title": f"Complete with {completion.name}",
                        "description": completion.docstring() or f"Add {completion.name}",
                        "code": code + completion.complete,
                        "type": "completion"
                    })
            except Exception as e:
                logging.error(f"Jedi completion error: {e}")
        
        # Add basic suggestions for all languages
        suggestions.extend(self._get_basic_suggestions(code, language))
        
        return suggestions
    
    def _get_openai_suggestions(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Get suggestions from OpenAI GPT-5"""
        try:
            # the newest OpenAI model is "gpt-5" which was released August 7, 2025.
            # do not change this unless explicitly requested by the user
            prompt = f"""
            Analyze this {language} code and provide 3 intelligent suggestions for improvement:
            
            ```{language}
            {code}
            ```
            
            For each suggestion, provide:
            1. A brief title
            2. A description of what it improves
            3. The improved code
            
            Respond in JSON format:
            {{"suggestions": [
                {{
                    "title": "suggestion title",
                    "description": "what this improves",
                    "code": "improved code",
                    "type": "improvement"
                }}
            ]}}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-5",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                max_completion_tokens=2048
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get("suggestions", [])
            
        except Exception as e:
            logging.error(f"OpenAI suggestion error: {e}")
            return self._get_local_suggestions(code, language)
    
    def _get_gemini_suggestions(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Get suggestions from Google Gemini"""
        try:
            prompt = f"""
            Analyze this {language} code and provide 3 intelligent suggestions for improvement:
            
            ```{language}
            {code}
            ```
            
            For each suggestion, provide:
            1. A brief title
            2. A description of what it improves
            3. The improved code
            
            Respond in JSON format with an array of suggestions.
            """
            
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            
            if response.text:
                result = json.loads(response.text)
                return result.get("suggestions", [])
            
        except Exception as e:
            logging.error(f"Gemini suggestion error: {e}")
            return self._get_local_suggestions(code, language)
    
    def _get_basic_suggestions(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Get basic code improvement suggestions"""
        suggestions = []
        lines = code.split('\n')
        
        # Check for common improvements
        if language == "python":
            # Check for missing docstrings
            if any(line.strip().startswith('def ') for line in lines):
                if not any('"""' in line or "'''" in line for line in lines):
                    suggestions.append({
                        "title": "Add docstrings",
                        "description": "Functions should have docstrings for better documentation",
                        "code": code,
                        "type": "documentation"
                    })
            
            # Check for long lines
            long_lines = [i+1 for i, line in enumerate(lines) if len(line) > 79]
            if long_lines:
                suggestions.append({
                    "title": "Fix long lines",
                    "description": f"Lines {long_lines[:3]} exceed 79 characters",
                    "code": code,
                    "type": "style"
                })
        
        return suggestions
    
    def get_code_explanation(self, code: str, language: str, provider: str = "openai") -> str:
        """Get explanation of code functionality"""
        try:
            if provider == "openai" and self.openai_client:
                prompt = f"Explain what this {language} code does:\n\n```{language}\n{code}\n```"
                
                response = self.openai_client.chat.completions.create(
                    model="gpt-5",
                    messages=[{"role": "user", "content": prompt}],
                    max_completion_tokens=1024
                )
                
                return response.choices[0].message.content
                
            elif provider == "gemini" and self.gemini_client:
                prompt = f"Explain what this {language} code does:\n\n```{language}\n{code}\n```"
                
                response = self.gemini_client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                
                return response.text or "Could not generate explanation"
        
        except Exception as e:
            logging.error(f"Error getting code explanation: {e}")
            
        return "Code explanation not available"
    
    def generate_documentation(self, code: str, language: str) -> str:
        """Generate documentation for the code"""
        try:
            if self.openai_client:
                prompt = f"""
                Generate comprehensive documentation for this {language} code:
                
                ```{language}
                {code}
                