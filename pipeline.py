from typing import Dict, List, Any, TypedDict
from langgraph.graph import StateGraph, END
from github_parser import GitHubParser
from code_analyzer import StaticAnalyzer
from gemini_analyzer import GeminiAnalyzer
import json

class AnalysisState(TypedDict):
    """State for the analysis pipeline."""
    repo_url: str
    repo_info: Dict[str, Any]
    code_files: List[Dict[str, str]]
    static_issues: List[Dict[str, Any]]
    ai_issues: List[Dict[str, Any]]
    final_report: Dict[str, Any]
    error: str

class IssueAnalyzerPipeline:
    """LangGraph-based pipeline for code analysis."""
    
    def __init__(self):
        self.github_parser = GitHubParser()
        self.static_analyzer = StaticAnalyzer()
        self.gemini_analyzer = GeminiAnalyzer()
        self.workflow = self._create_workflow()
    
    def _create_workflow(self) -> StateGraph:
        """Create the analysis workflow using LangGraph."""
        workflow = StateGraph(AnalysisState)
        
        # Add nodes
        workflow.add_node("parse_repo", self._parse_repository)
        workflow.add_node("extract_files", self._extract_code_files)
        workflow.add_node("static_analysis", self._run_static_analysis)
        workflow.add_node("ai_analysis", self._run_ai_analysis)
        workflow.add_node("generate_report", self._generate_final_report)
        
        # Define the flow
        workflow.set_entry_point("parse_repo")
        workflow.add_edge("parse_repo", "extract_files")
        workflow.add_edge("extract_files", "static_analysis")
        workflow.add_edge("static_analysis", "ai_analysis")
        workflow.add_edge("ai_analysis", "generate_report")
        workflow.add_edge("generate_report", END)
        
        return workflow.compile()
    
    def _parse_repository(self, state: AnalysisState) -> AnalysisState:
        """Parse GitHub repository and get basic info."""
        try:
            print("🔍 Parsing repository...")
            repo_info = self.github_parser.get_repository_info(state["repo_url"])
            parsed_url = self.github_parser.parse_github_url(state["repo_url"])
            
            state["repo_info"] = {
                **repo_info,
                **parsed_url
            }
            print(f"✅ Repository parsed: {repo_info.get('name', 'Unknown')}")
            
        except Exception as e:
            state["error"] = f"Failed to parse repository: {str(e)}"
            print(f"❌ Error parsing repository: {e}")
        
        return state
    
    def _extract_code_files(self, state: AnalysisState) -> AnalysisState:
        """Extract code files from the repository."""
        try:
            print("📁 Extracting code files...")
            
            # Clone repository
            repo_path = self.github_parser.clone_repository(state["repo_url"])
            
            # Extract code files
            code_files = self.github_parser.extract_code_files(repo_path)
            state["code_files"] = code_files
            
            print(f"✅ Extracted {len(code_files)} code files")
            
            # Cleanup
            self.github_parser.cleanup()
            
        except Exception as e:
            state["error"] = f"Failed to extract code files: {str(e)}"
            print(f"❌ Error extracting files: {e}")
            self.github_parser.cleanup()
        
        return state
    
    def _run_static_analysis(self, state: AnalysisState) -> AnalysisState:
        """Run static code analysis."""
        try:
            print("🔧 Running static analysis...")
            
            all_issues = []
            code_files = state.get("code_files", [])
            
            for file_info in code_files:
                issues = self.static_analyzer.analyze_file(
                    file_info["content"],
                    file_info["language"],
                    file_info["path"]
                )
                all_issues.extend(issues)
            
            state["static_issues"] = all_issues
            print(f"✅ Found {len(all_issues)} static analysis issues")
            
        except Exception as e:
            state["error"] = f"Static analysis failed: {str(e)}"
            print(f"❌ Static analysis error: {e}")
        
        return state
    
    def _run_ai_analysis(self, state: AnalysisState) -> AnalysisState:
        """Run AI-powered analysis using Gemini."""
        try:
            # Show which method is being used
            if self.gemini_analyzer.use_cli:
                print("🤖 Running AI analysis using Gemini CLI...")
            elif self.gemini_analyzer.model:
                print("🤖 Running AI analysis using Gemini API...")
            else:
                print("🤖 Running basic AI analysis (fallback mode)...")
            
            all_ai_issues = []
            code_files = state.get("code_files", [])
            
            # Limit AI analysis to prevent overwhelming the API
            files_to_analyze = code_files[:10]  # Analyze top 10 files
            
            for file_info in files_to_analyze:
                # Run logic analysis
                logic_issues = self.gemini_analyzer.analyze_code_logic(
                    file_info["content"],
                    file_info["language"],
                    file_info["path"]
                )
                all_ai_issues.extend(logic_issues)
                
                # Run simulation (for smaller files)
                if len(file_info["content"]) < 5000:  # Only simulate smaller files
                    simulation = self.gemini_analyzer.simulate_code_execution(
                        file_info["content"],
                        file_info["language"]
                    )
                    
                    # Convert simulation results to issues
                    runtime_issues = simulation.get("potential_runtime_issues", [])
                    for issue_text in runtime_issues:
                        all_ai_issues.append({
                            'type': 'runtime_risk',
                            'severity': 'MEDIUM',
                            'title': 'Potential Runtime Issue',
                            'description': issue_text,
                            'line': 1,
                            'suggestion': 'Review code for runtime safety',
                            'file_path': file_info["path"],
                            'source': 'gemini_simulation'
                        })
            
            # Enhance suggestions for all issues
            static_issues = state.get("static_issues", [])
            all_issues = static_issues + all_ai_issues
            enhanced_issues = self.gemini_analyzer.generate_improvement_suggestions(all_issues)
            
            state["ai_issues"] = all_ai_issues
            state["static_issues"] = enhanced_issues[:len(static_issues)]  # Update static issues
            state["ai_issues"] = enhanced_issues[len(static_issues):]      # Update AI issues
            
            print(f"✅ Found {len(all_ai_issues)} AI analysis issues")
            
        except Exception as e:
            state["error"] = f"AI analysis failed: {str(e)}"
            print(f"❌ AI analysis error: {e}")
        
        return state
    
    def _generate_final_report(self, state: AnalysisState) -> AnalysisState:
        """Generate the final analysis report."""
        try:
            print("📊 Generating final report...")
            
            static_issues = state.get("static_issues", [])
            ai_issues = state.get("ai_issues", [])
            all_issues = static_issues + ai_issues
            
            # Categorize issues by severity
            severity_counts = {
                'CRITICAL': 0,
                'HIGH': 0,
                'MEDIUM': 0,
                'LOW': 0,
                'INFO': 0
            }
            
            for issue in all_issues:
                severity = issue.get('severity', 'MEDIUM')
                if severity in severity_counts:
                    severity_counts[severity] += 1
            
            # Categorize by type
            type_counts = {}
            for issue in all_issues:
                issue_type = issue.get('type', 'unknown')
                type_counts[issue_type] = type_counts.get(issue_type, 0) + 1
            
            # Calculate overall score (0-100, higher is better)
            total_issues = len(all_issues)
            critical_weight = severity_counts['CRITICAL'] * 10
            high_weight = severity_counts['HIGH'] * 5
            medium_weight = severity_counts['MEDIUM'] * 2
            low_weight = severity_counts['LOW'] * 1
            
            penalty_score = critical_weight + high_weight + medium_weight + low_weight
            code_files_count = len(state.get("code_files", []))
            
            # Base score calculation
            if code_files_count > 0:
                base_score = max(0, 100 - (penalty_score / code_files_count * 10))
            else:
                base_score = 100 if total_issues == 0 else 50
            
            report = {
                'repository': state.get("repo_info", {}),
                'summary': {
                    'total_issues': total_issues,
                    'files_analyzed': len(state.get("code_files", [])),
                    'overall_score': round(base_score, 1),
                    'severity_breakdown': severity_counts,
                    'issue_types': type_counts
                },
                'issues': all_issues,
                'recommendations': self._generate_recommendations(all_issues),
                'analysis_metadata': {
                    'static_analysis_issues': len(static_issues),
                    'ai_analysis_issues': len(ai_issues),
                    'timestamp': self._get_timestamp()
                }
            }
            
            state["final_report"] = report
            print("✅ Final report generated successfully")
            
        except Exception as e:
            state["error"] = f"Report generation failed: {str(e)}"
            print(f"❌ Report generation error: {e}")
        
        return state
    
    def _generate_recommendations(self, issues: List[Dict]) -> List[str]:
        """Generate high-level recommendations based on issues found."""
        recommendations = []
        
        # Count issues by type
        type_counts = {}
        severity_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        
        for issue in issues:
            issue_type = issue.get('type', 'unknown')
            type_counts[issue_type] = type_counts.get(issue_type, 0) + 1
            
            severity = issue.get('severity', 'MEDIUM')
            if severity in severity_counts:
                severity_counts[severity] += 1
        
        # Generate recommendations based on patterns
        if severity_counts['CRITICAL'] > 0:
            recommendations.append("🚨 Address critical security and logic issues immediately")
        
        if severity_counts['HIGH'] > 3:
            recommendations.append("⚠️ High number of high-severity issues detected - consider code review")
        
        if type_counts.get('security', 0) > 0:
            recommendations.append("🔒 Implement security best practices and input validation")
        
        if type_counts.get('performance', 0) > 2:
            recommendations.append("⚡ Optimize performance bottlenecks for better efficiency")
        
        if type_counts.get('maintainability', 0) > 5:
            recommendations.append("📚 Improve code documentation and maintainability")
        
        if not recommendations:
            recommendations.append("✅ Code quality looks good! Consider regular analysis for continuous improvement")
        
        return recommendations
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def analyze(self, repo_url: str) -> Dict[str, Any]:
        """Run the complete analysis pipeline."""
        try:
            print(f"🚀 Starting analysis for: {repo_url}")
            
            initial_state = AnalysisState(
                repo_url=repo_url,
                repo_info={},
                code_files=[],
                static_issues=[],
                ai_issues=[],
                final_report={},
                error=""
            )
            
            # Run the workflow
            final_state = self.workflow.invoke(initial_state)
            
            if final_state.get("error"):
                return {
                    "success": False,
                    "error": final_state["error"],
                    "report": None
                }
            
            return {
                "success": True,
                "error": None,
                "report": final_state["final_report"]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Pipeline execution failed: {str(e)}",
                "report": None
            }
