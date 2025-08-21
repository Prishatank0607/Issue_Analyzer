import google.generativeai as genai
from typing import List, Dict, Any
import json
import subprocess
import tempfile
import os
from config import Config

class GeminiAnalyzer:
    """Gemini AI integration for advanced code analysis and logic simulation."""
    
    def __init__(self):
        self.config = Config()
        self.use_cli = self.config.USE_GEMINI_CLI
        
        if self.use_cli:
            # Check if Gemini CLI is available
            if self._check_cli_availability():
                self.model = None  # We'll use CLI instead
                print("✅ Using Gemini CLI for analysis")
            else:
                print("⚠️ Gemini CLI not found, falling back to API")
                self.use_cli = False
        
        if not self.use_cli:
            if self.config.GEMINI_API_KEY:
                genai.configure(api_key=self.config.GEMINI_API_KEY)
                self.model = genai.GenerativeModel('gemini-pro')
                print("✅ Using Gemini API for analysis")
            else:
                self.model = None
                print("Warning: Neither Gemini CLI nor API configured. Using fallback analysis.")
    
    def _check_cli_availability(self) -> bool:
        """Check if Gemini CLI is available."""
        try:
            result = subprocess.run(
                [self.config.GEMINI_CLI_PATH, '--version'], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def _analyze_with_cli(self, prompt: str) -> str:
        """Analyze code using Gemini CLI."""
        try:
            # Create temporary file for the prompt
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
                temp_file.write(prompt)
                temp_file_path = temp_file.name
            
            # Run Gemini CLI
            result = subprocess.run([
                self.config.GEMINI_CLI_PATH,
                'generate',
                '--file', temp_file_path
            ], capture_output=True, text=True, timeout=60)
            
            # Clean up temporary file
            os.unlink(temp_file_path)
            
            if result.returncode == 0:
                return result.stdout
            else:
                print(f"Gemini CLI error: {result.stderr}")
                return ""
                
        except Exception as e:
            print(f"Error running Gemini CLI: {e}")
            return ""
    
    def analyze_code_logic(self, code: str, language: str, file_path: str) -> List[Dict]:
        """Analyze code logic using Gemini AI (CLI or API)."""
        if self.use_cli:
            return self._analyze_with_cli_logic(code, language, file_path)
        elif not self.model:
            return self._fallback_logic_analysis(code, language, file_path)
        
        try:
            prompt = self._create_analysis_prompt(code, language, file_path)
            response = self.model.generate_content(prompt)
            
            # Parse the response to extract issues
            return self._parse_gemini_response(response.text, file_path)
            
        except Exception as e:
            print(f"Error with Gemini analysis: {e}")
            return self._fallback_logic_analysis(code, language, file_path)
    
    def _analyze_with_cli_logic(self, code: str, language: str, file_path: str) -> List[Dict]:
        """Analyze code logic using Gemini CLI."""
        try:
            prompt = self._create_analysis_prompt(code, language, file_path)
            response_text = self._analyze_with_cli(prompt)
            
            if response_text:
                return self._parse_gemini_response(response_text, file_path)
            else:
                return self._fallback_logic_analysis(code, language, file_path)
                
        except Exception as e:
            print(f"Error with Gemini CLI analysis: {e}")
            return self._fallback_logic_analysis(code, language, file_path)
    
    def _create_analysis_prompt(self, code: str, language: str, file_path: str) -> str:
        """Create a detailed prompt for Gemini analysis."""
        return f"""
Analyze the following {language} code for potential issues, bugs, and improvements.
File: {file_path}

Code:
```{language}
{code}
```

Please identify:
1. Logic errors or potential bugs
2. Code smell and design issues
3. Performance problems
4. Security vulnerabilities
5. Maintainability concerns

For each issue found, provide:
- Type of issue
- Severity level (CRITICAL, HIGH, MEDIUM, LOW, INFO)
- Line number (if applicable)
- Description of the problem
- Suggested improvement

Format your response as JSON with this structure:
{{
    "issues": [
        {{
            "type": "logic_error|security|performance|maintainability|code_smell",
            "severity": "CRITICAL|HIGH|MEDIUM|LOW|INFO",
            "title": "Brief title",
            "description": "Detailed description",
            "line": line_number,
            "suggestion": "Improvement suggestion"
        }}
    ]
}}

Focus on practical, actionable feedback that will improve code quality.
"""
    
    def _parse_gemini_response(self, response_text: str, file_path: str) -> List[Dict]:
        """Parse Gemini's response to extract issues."""
        try:
            # Try to extract JSON from the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx]
                parsed = json.loads(json_str)
                
                issues = parsed.get('issues', [])
                for issue in issues:
                    issue['file_path'] = file_path
                    issue['source'] = 'gemini'
                
                return issues
            else:
                # Fallback: parse text response
                return self._parse_text_response(response_text, file_path)
                
        except json.JSONDecodeError:
            return self._parse_text_response(response_text, file_path)
    
    def _parse_text_response(self, response_text: str, file_path: str) -> List[Dict]:
        """Parse text response when JSON parsing fails."""
        issues = []
        lines = response_text.split('\n')
        
        current_issue = {}
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for issue indicators
            if any(keyword in line.lower() for keyword in ['issue:', 'problem:', 'bug:', 'error:']):
                if current_issue:
                    issues.append(current_issue)
                current_issue = {
                    'type': 'logic_error',
                    'severity': 'MEDIUM',
                    'title': line,
                    'description': line,
                    'line': 1,
                    'suggestion': 'Review and fix the identified issue',
                    'file_path': file_path,
                    'source': 'gemini'
                }
        
        if current_issue:
            issues.append(current_issue)
            
        return issues
    
    def _fallback_logic_analysis(self, code: str, language: str, file_path: str) -> List[Dict]:
        """Fallback analysis when Gemini is not available."""
        issues = []
        lines = code.split('\n')
        
        # Basic logic checks
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            # Check for common logic issues
            if language == 'python':
                # Check for bare except clauses
                if line_stripped == 'except:':
                    issues.append({
                        'type': 'logic_error',
                        'severity': 'MEDIUM',
                        'title': 'Bare Except Clause',
                        'description': 'Bare except clause catches all exceptions',
                        'line': i + 1,
                        'suggestion': 'Specify the exception type or use Exception',
                        'file_path': file_path,
                        'source': 'fallback'
                    })
                
                # Check for potential division by zero
                if '/' in line_stripped and 'if' not in line_stripped:
                    issues.append({
                        'type': 'logic_error',
                        'severity': 'HIGH',
                        'title': 'Potential Division by Zero',
                        'description': 'Division operation without zero check',
                        'line': i + 1,
                        'suggestion': 'Add validation to ensure divisor is not zero',
                        'file_path': file_path,
                        'source': 'fallback'
                    })
        
        return issues
    
    def simulate_code_execution(self, code: str, language: str) -> Dict[str, Any]:
        """Simulate code execution to find runtime issues."""
        if not self.model:
            return {'simulation_results': 'Gemini not available for simulation'}
        
        try:
            prompt = f"""
Simulate the execution of this {language} code and identify potential runtime issues:

```{language}
{code}
```

Consider:
1. Null pointer exceptions
2. Array/list bounds errors
3. Type mismatches
4. Resource leaks
5. Infinite loops
6. Memory issues

Provide a brief analysis of what could go wrong during execution.
"""
            
            response = self.model.generate_content(prompt)
            return {
                'simulation_results': response.text,
                'potential_runtime_issues': self._extract_runtime_issues(response.text)
            }
            
        except Exception as e:
            return {'simulation_results': f'Simulation failed: {str(e)}'}
    
    def _extract_runtime_issues(self, simulation_text: str) -> List[str]:
        """Extract potential runtime issues from simulation results."""
        issues = []
        lines = simulation_text.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in 
                   ['exception', 'error', 'crash', 'fail', 'issue', 'problem']):
                issues.append(line.strip())
        
        return issues
    
    def generate_improvement_suggestions(self, issues: List[Dict]) -> List[Dict]:
        """Generate detailed improvement suggestions using Gemini."""
        if not self.model or not issues:
            return issues
        
        try:
            # Group issues by file for batch processing
            files_issues = {}
            for issue in issues:
                file_path = issue.get('file_path', 'unknown')
                if file_path not in files_issues:
                    files_issues[file_path] = []
                files_issues[file_path].append(issue)
            
            enhanced_issues = []
            for file_path, file_issues in files_issues.items():
                enhanced = self._enhance_suggestions_for_file(file_issues, file_path)
                enhanced_issues.extend(enhanced)
            
            return enhanced_issues
            
        except Exception as e:
            print(f"Error enhancing suggestions: {e}")
            return issues
    
    def _enhance_suggestions_for_file(self, issues: List[Dict], file_path: str) -> List[Dict]:
        """Enhance suggestions for issues in a specific file."""
        try:
            issues_summary = "\n".join([
                f"- {issue['title']}: {issue['description']}" 
                for issue in issues
            ])
            
            prompt = f"""
For the file {file_path}, I found these issues:
{issues_summary}

Please provide detailed, actionable improvement suggestions for each issue.
Include specific code examples where helpful.
Focus on best practices and modern coding standards.

Format as: Issue -> Detailed Suggestion
"""
            
            response = self.model.generate_content(prompt)
            suggestions = response.text.split('\n')
            
            # Enhance original issues with better suggestions
            for i, issue in enumerate(issues):
                if i < len(suggestions) and suggestions[i].strip():
                    issue['enhanced_suggestion'] = suggestions[i].strip()
            
            return issues
            
        except Exception as e:
            print(f"Error enhancing suggestions for {file_path}: {e}")
            return issues
