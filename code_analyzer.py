import tree_sitter
from tree_sitter import Language, Parser
import os
from typing import List, Dict, Any, Optional
from pathlib import Path
import subprocess
import tempfile

class TreeSitterAnalyzer:
    """Code analysis using Tree-sitter for parsing."""
    
    def __init__(self):
        self.parsers = {}
        self.languages = {}
        self._setup_languages()
    
    def _setup_languages(self):
        """Setup Tree-sitter languages."""
        try:
            # Try to build languages if not already built
            self._build_languages()
            
            # Load languages
            language_configs = {
                'python': 'tree-sitter-python',
                'javascript': 'tree-sitter-javascript', 
                'java': 'tree-sitter-java',
                'cpp': 'tree-sitter-cpp',
                'c': 'tree-sitter-c'
            }
            
            for lang_name, lib_name in language_configs.items():
                try:
                    # This is a simplified approach - in production you'd build the .so files
                    parser = Parser()
                    self.parsers[lang_name] = parser
                except Exception as e:
                    print(f"Could not load {lang_name} parser: {e}")
                    
        except Exception as e:
            print(f"Error setting up Tree-sitter: {e}")
    
    def _build_languages(self):
        """Build Tree-sitter language libraries."""
        # This would typically build the .so files, but for simplicity
        # we'll use a fallback approach with basic parsing
        pass
    
    def analyze_code_structure(self, code: str, language: str) -> Dict[str, Any]:
        """Analyze code structure using Tree-sitter."""
        try:
            if language in self.parsers:
                parser = self.parsers[language]
                tree = parser.parse(bytes(code, 'utf8'))
                
                return {
                    'functions': self._extract_functions(tree.root_node, code),
                    'classes': self._extract_classes(tree.root_node, code),
                    'imports': self._extract_imports(tree.root_node, code),
                    'complexity': self._calculate_complexity(tree.root_node),
                    'lines_of_code': len(code.split('\n'))
                }
            else:
                # Fallback to basic analysis
                return self._basic_code_analysis(code, language)
                
        except Exception as e:
            print(f"Error analyzing code structure: {e}")
            return self._basic_code_analysis(code, language)
    
    def _basic_code_analysis(self, code: str, language: str) -> Dict[str, Any]:
        """Basic code analysis without Tree-sitter."""
        lines = code.split('\n')
        
        analysis = {
            'functions': [],
            'classes': [],
            'imports': [],
            'complexity': 1,
            'lines_of_code': len(lines)
        }
        
        # Basic pattern matching for different languages
        if language == 'python':
            for i, line in enumerate(lines):
                line = line.strip()
                if line.startswith('def '):
                    func_name = line.split('(')[0].replace('def ', '')
                    analysis['functions'].append({
                        'name': func_name,
                        'line': i + 1,
                        'parameters': self._extract_parameters(line)
                    })
                elif line.startswith('class '):
                    class_name = line.split('(')[0].replace('class ', '').replace(':', '')
                    analysis['classes'].append({
                        'name': class_name,
                        'line': i + 1
                    })
                elif line.startswith('import ') or line.startswith('from '):
                    analysis['imports'].append(line)
        
        elif language == 'javascript':
            for i, line in enumerate(lines):
                line = line.strip()
                if 'function ' in line:
                    func_name = line.split('function ')[1].split('(')[0]
                    analysis['functions'].append({
                        'name': func_name,
                        'line': i + 1
                    })
                elif line.startswith('class '):
                    class_name = line.split('class ')[1].split(' ')[0]
                    analysis['classes'].append({
                        'name': class_name,
                        'line': i + 1
                    })
        
        return analysis
    
    def _extract_functions(self, node, code: str) -> List[Dict]:
        """Extract function definitions from AST."""
        functions = []
        # Implementation would traverse the AST to find function nodes
        return functions
    
    def _extract_classes(self, node, code: str) -> List[Dict]:
        """Extract class definitions from AST."""
        classes = []
        # Implementation would traverse the AST to find class nodes
        return classes
    
    def _extract_imports(self, node, code: str) -> List[str]:
        """Extract import statements from AST."""
        imports = []
        # Implementation would traverse the AST to find import nodes
        return imports
    
    def _calculate_complexity(self, node) -> int:
        """Calculate cyclomatic complexity."""
        # Basic complexity calculation
        return 1
    
    def _extract_parameters(self, function_line: str) -> List[str]:
        """Extract function parameters from function definition line."""
        try:
            params_str = function_line.split('(')[1].split(')')[0]
            if params_str.strip():
                return [param.strip() for param in params_str.split(',')]
        except:
            pass
        return []

class StaticAnalyzer:
    """Static code analysis for finding common issues."""
    
    def __init__(self):
        self.tree_analyzer = TreeSitterAnalyzer()
    
    def analyze_file(self, file_content: str, language: str, file_path: str) -> List[Dict]:
        """Analyze a single file for issues."""
        issues = []
        
        # Get code structure
        structure = self.tree_analyzer.analyze_code_structure(file_content, language)
        
        # Run various analysis checks
        issues.extend(self._check_code_quality(file_content, language, structure))
        issues.extend(self._check_security_issues(file_content, language))
        issues.extend(self._check_performance_issues(file_content, language, structure))
        issues.extend(self._check_maintainability(file_content, language, structure))
        
        # Add file context to issues
        for issue in issues:
            issue['file_path'] = file_path
            
        return issues
    
    def _check_code_quality(self, code: str, language: str, structure: Dict) -> List[Dict]:
        """Check for code quality issues."""
        issues = []
        lines = code.split('\n')
        
        # Check for long functions
        for func in structure.get('functions', []):
            if 'line' in func:
                # Estimate function length (simplified)
                func_lines = 20  # This would be calculated properly
                if func_lines > 50:
                    issues.append({
                        'type': 'code_quality',
                        'severity': 'MEDIUM',
                        'title': 'Long Function',
                        'description': f"Function '{func['name']}' is too long ({func_lines} lines)",
                        'line': func['line'],
                        'suggestion': 'Consider breaking this function into smaller, more focused functions'
                    })
        
        # Check for long lines
        for i, line in enumerate(lines):
            if len(line) > 120:
                issues.append({
                    'type': 'code_quality',
                    'severity': 'LOW',
                    'title': 'Long Line',
                    'description': f'Line {i+1} exceeds 120 characters ({len(line)} characters)',
                    'line': i + 1,
                    'suggestion': 'Break long lines into multiple lines for better readability'
                })
        
        return issues
    
    def _check_security_issues(self, code: str, language: str) -> List[Dict]:
        """Check for potential security issues."""
        issues = []
        lines = code.split('\n')
        
        # Check for hardcoded secrets
        secret_patterns = ['password', 'api_key', 'secret', 'token']
        for i, line in enumerate(lines):
            line_lower = line.lower()
            for pattern in secret_patterns:
                if pattern in line_lower and '=' in line and ('"' in line or "'" in line):
                    issues.append({
                        'type': 'security',
                        'severity': 'HIGH',
                        'title': 'Potential Hardcoded Secret',
                        'description': f'Line {i+1} may contain a hardcoded secret',
                        'line': i + 1,
                        'suggestion': 'Use environment variables or secure configuration for secrets'
                    })
        
        # Language-specific security checks
        if language == 'python':
            for i, line in enumerate(lines):
                if 'eval(' in line:
                    issues.append({
                        'type': 'security',
                        'severity': 'CRITICAL',
                        'title': 'Dangerous eval() Usage',
                        'description': f'Line {i+1} uses eval() which can execute arbitrary code',
                        'line': i + 1,
                        'suggestion': 'Avoid eval(). Use safer alternatives like ast.literal_eval() for simple cases'
                    })
        
        return issues
    
    def _check_performance_issues(self, code: str, language: str, structure: Dict) -> List[Dict]:
        """Check for performance issues."""
        issues = []
        lines = code.split('\n')
        
        if language == 'python':
            # Check for inefficient loops
            for i, line in enumerate(lines):
                if 'for' in line and 'range(len(' in line:
                    issues.append({
                        'type': 'performance',
                        'severity': 'MEDIUM',
                        'title': 'Inefficient Loop',
                        'description': f'Line {i+1} uses range(len()) pattern',
                        'line': i + 1,
                        'suggestion': 'Use enumerate() or iterate directly over the collection'
                    })
        
        return issues
    
    def _check_maintainability(self, code: str, language: str, structure: Dict) -> List[Dict]:
        """Check for maintainability issues."""
        issues = []
        
        # Check for missing docstrings
        if language == 'python':
            for func in structure.get('functions', []):
                # This is simplified - would check if function has docstring
                issues.append({
                    'type': 'maintainability',
                    'severity': 'LOW',
                    'title': 'Missing Documentation',
                    'description': f"Function '{func['name']}' lacks documentation",
                    'line': func.get('line', 1),
                    'suggestion': 'Add docstring to explain function purpose, parameters, and return value'
                })
        
        return issues
