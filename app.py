import streamlit as st
import pandas as pd
import json
from pipeline import IssueAnalyzerPipeline
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Configure Streamlit page
st.set_page_config(
    page_title="IssueAnalyzer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .severity-critical {
        background-color: #ff4444;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 0.3rem;
        font-weight: bold;
    }
    .severity-high {
        background-color: #ff8800;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 0.3rem;
        font-weight: bold;
    }
    .severity-medium {
        background-color: #ffaa00;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 0.3rem;
        font-weight: bold;
    }
    .severity-low {
        background-color: #88cc00;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 0.3rem;
        font-weight: bold;
    }
    .severity-info {
        background-color: #0088cc;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 0.3rem;
        font-weight: bold;
    }
    .issue-card {
        border-left: 4px solid #ddd;
        border-radius: 0.3rem;
        padding: 0.8rem;
        margin: 0.3rem 0;
        background-color: #fafafa;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .issue-card-critical {
        border-left-color: #ff4444;
        background-color: #fff5f5;
    }
    .issue-card-high {
        border-left-color: #ff8800;
        background-color: #fff8f0;
    }
    .issue-card-medium {
        border-left-color: #ffaa00;
        background-color: #fffbf0;
    }
    .issue-card-low {
        border-left-color: #88cc00;
        background-color: #f8fff0;
    }
    .issue-card-info {
        border-left-color: #0088cc;
        background-color: #f0f8ff;
    }
    .issue-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }
    .issue-title {
        font-weight: 600;
        font-size: 1.1rem;
        color: #333;
        margin: 0;
    }
    .issue-meta {
        font-size: 0.85rem;
        color: #666;
        margin: 0.3rem 0;
    }
    .issue-description {
        margin: 0.5rem 0;
        line-height: 1.4;
    }
    .issue-suggestion {
        background-color: rgba(0,136,204,0.1);
        padding: 0.5rem;
        border-radius: 0.3rem;
        margin-top: 0.5rem;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables."""
    if 'analysis_result' not in st.session_state:
        st.session_state.analysis_result = None
    if 'analyzing' not in st.session_state:
        st.session_state.analyzing = False

def render_severity_badge(severity):
    """Render a colored severity badge."""
    severity_lower = severity.lower()
    return f'<span class="severity-{severity_lower}">{severity}</span>'

def render_compact_issues_table(issues):
    """Render issues in a compact table format."""
    if not issues:
        return
    
    # Prepare data for table
    table_data = []
    for issue in issues:
        table_data.append({
            'Type': issue.get('type', 'unknown'),
            'Severity': issue.get('severity', 'MEDIUM'),
            'Issue': issue.get('title', 'Unknown Issue'),
            'File': issue.get('file_path', 'N/A').split('/')[-1],  # Just filename
            'Line': issue.get('line', 'N/A'),
            'Description': issue.get('description', 'No description')[:100] + '...' if len(issue.get('description', '')) > 100 else issue.get('description', 'No description')
        })
    
    # Create DataFrame and display
    df = pd.DataFrame(table_data)
    
    # Style the dataframe
    def style_severity(val):
        colors = {
            'CRITICAL': 'background-color: #ffebee; color: #c62828; font-weight: bold',
            'HIGH': 'background-color: #fff3e0; color: #ef6c00; font-weight: bold',
            'MEDIUM': 'background-color: #fffde7; color: #f57f17; font-weight: bold',
            'LOW': 'background-color: #f1f8e9; color: #558b2f; font-weight: bold',
            'INFO': 'background-color: #e3f2fd; color: #1565c0; font-weight: bold'
        }
        return colors.get(val, '')
    
    styled_df = df.style.applymap(style_severity, subset=['Severity'])
    
    st.dataframe(
        styled_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Type": st.column_config.TextColumn("Type", width="small"),
            "Severity": st.column_config.TextColumn("Severity", width="small"),
            "Issue": st.column_config.TextColumn("Issue", width="medium"),
            "File": st.column_config.TextColumn("File", width="small"),
            "Line": st.column_config.NumberColumn("Line", width="small"),
            "Description": st.column_config.TextColumn("Description", width="large")
        }
    )

def render_issue_card(issue, index):
    """Render an individual issue card with modern design."""
    severity = issue.get('severity', 'MEDIUM').lower()
    severity_badge = render_severity_badge(issue.get('severity', 'MEDIUM'))
    
    # Create expandable issue card
    with st.expander(f"**{issue.get('title', 'Unknown Issue')}** {severity_badge}", expanded=False):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"""
            <div class="issue-card issue-card-{severity}">
                <div class="issue-description">
                    {issue.get('description', 'No description available')}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Show suggestion in a nice format
            if issue.get('suggestion'):
                st.markdown("**💡 Suggestion:**")
                st.markdown(f"""
                <div class="issue-suggestion">
                    {issue.get('suggestion', 'No suggestion available')}
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            # Metadata in a clean format
            st.markdown("**📋 Details**")
            st.markdown(f"**Type:** `{issue.get('type', 'unknown')}`")
            st.markdown(f"**File:** `{issue.get('file_path', 'N/A')}`")
            st.markdown(f"**Line:** `{issue.get('line', 'N/A')}`")
            
            if issue.get('source'):
                st.markdown(f"**Source:** `{issue.get('source')}`")
        
        # Show enhanced suggestion if available
        if issue.get('enhanced_suggestion'):
            st.markdown("---")
            st.markdown("**🤖 AI-Enhanced Suggestion:**")
            st.info(issue['enhanced_suggestion'])

def render_summary_metrics(report):
    """Render summary metrics."""
    summary = report.get('summary', {})
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Overall Score",
            value=f"{summary.get('overall_score', 0)}/100",
            delta=None
        )
    
    with col2:
        st.metric(
            label="Total Issues",
            value=summary.get('total_issues', 0)
        )
    
    with col3:
        st.metric(
            label="Files Analyzed",
            value=summary.get('files_analyzed', 0)
        )
    
    with col4:
        critical_count = summary.get('severity_breakdown', {}).get('CRITICAL', 0)
        st.metric(
            label="Critical Issues",
            value=critical_count,
            delta=f"-{critical_count}" if critical_count > 0 else "0"
        )

def render_severity_chart(report):
    """Render severity breakdown chart."""
    severity_data = report.get('summary', {}).get('severity_breakdown', {})
    
    if any(severity_data.values()):
        fig = px.bar(
            x=list(severity_data.keys()),
            y=list(severity_data.values()),
            title="Issues by Severity",
            color=list(severity_data.keys()),
            color_discrete_map={
                'CRITICAL': '#ff4444',
                'HIGH': '#ff8800',
                'MEDIUM': '#ffaa00',
                'LOW': '#88cc00',
                'INFO': '#0088cc'
            }
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

def render_type_chart(report):
    """Render issue type breakdown chart."""
    type_data = report.get('summary', {}).get('issue_types', {})
    
    if any(type_data.values()):
        fig = px.pie(
            values=list(type_data.values()),
            names=list(type_data.keys()),
            title="Issues by Type"
        )
        st.plotly_chart(fig, use_container_width=True)

def main():
    """Main Streamlit application."""
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">🔍 IssueAnalyzer</h1>', unsafe_allow_html=True)
    st.markdown("**Analyze GitHub repositories for code issues, bugs, and improvement opportunities**")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # GitHub URL input
        repo_url = st.text_input(
            "GitHub Repository URL",
            placeholder="https://github.com/owner/repo",
            help="Enter the full GitHub repository URL"
        )
        
        # Gemini Configuration Status
        from config import Config
        config = Config()
        
        st.subheader("🤖 AI Analysis Status")
        
        # Show which method is configured
        if config.USE_GEMINI_CLI:
            st.info("🔧 **Configured for:** Gemini CLI")
            st.caption(f"CLI Path: `{config.GEMINI_CLI_PATH}`")
            
            # Check CLI availability
            from gemini_analyzer import GeminiAnalyzer
            analyzer = GeminiAnalyzer()
            if analyzer.use_cli:
                st.success("✅ Gemini CLI is available and working")
            else:
                st.error("❌ Gemini CLI not found - will use API fallback")
                if config.GEMINI_API_KEY:
                    st.warning("🔄 Falling back to Gemini API")
                else:
                    st.error("❌ No API key configured - using basic analysis only")
        else:
            st.info("🌐 **Configured for:** Gemini API")
            if config.GEMINI_API_KEY:
                st.success("✅ Gemini API key configured")
            else:
                st.warning("⚠️ Gemini API key not configured")
                st.info("Add your Gemini API key to .env file for enhanced AI analysis")
        
        # Supported languages
        st.markdown("---")
        st.subheader("🔧 Supported Languages")
        
        # Create a compact display of supported languages
        languages = list(config.SUPPORTED_EXTENSIONS.values())
        
        # Group languages in rows of 2 for compact display
        for i in range(0, len(languages), 2):
            col1, col2 = st.columns(2)
            with col1:
                if i < len(languages):
                    st.markdown(f"• **{languages[i].title()}**")
            with col2:
                if i + 1 < len(languages):
                    st.markdown(f"• **{languages[i + 1].title()}**")
        
        st.caption(f"Total: {len(languages)} languages supported")
        
        # Analysis button
        analyze_button = st.button(
            "🚀 Analyze Repository",
            disabled=not repo_url or st.session_state.analyzing,
            use_container_width=True
        )
        
        if analyze_button and repo_url:
            st.session_state.analyzing = True
            st.rerun()
    
    # Main content area
    if st.session_state.analyzing:
        st.header("🔄 Analysis in Progress")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Initialize pipeline
            pipeline = IssueAnalyzerPipeline()
            
            # Update progress
            progress_bar.progress(20)
            status_text.text("Initializing analysis pipeline...")
            
            # Show which AI method will be used
            from gemini_analyzer import GeminiAnalyzer
            analyzer = GeminiAnalyzer()
            if analyzer.use_cli:
                st.info("🔧 **Using Gemini CLI** for AI analysis")
            elif analyzer.model:
                st.info("🌐 **Using Gemini API** for AI analysis")
            else:
                st.warning("⚠️ **Using fallback analysis** (no AI configured)")
            
            progress_bar.progress(40)
            status_text.text("Running analysis...")
            
            # Run analysis
            result = pipeline.analyze(repo_url)
            
            progress_bar.progress(100)
            status_text.text("Analysis completed!")
            
            # Store result
            st.session_state.analysis_result = result
            st.session_state.analyzing = False
            
            # Show success/error
            if result['success']:
                st.success("✅ Analysis completed successfully!")
            else:
                st.error(f"❌ Analysis failed: {result['error']}")
            
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")
            st.session_state.analyzing = False
            st.rerun()
    
    # Display results
    if st.session_state.analysis_result and not st.session_state.analyzing:
        result = st.session_state.analysis_result
        
        if result['success']:
            report = result['report']
            
            # Repository info
            st.header("📊 Analysis Results")
            repo_info = report.get('repository', {})
            
            if repo_info:
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Repository Information")
                    st.write(f"**Name:** {repo_info.get('name', 'N/A')}")
                    st.write(f"**Description:** {repo_info.get('description', 'N/A')}")
                    st.write(f"**Language:** {repo_info.get('language', 'N/A')}")
                
                with col2:
                    st.subheader("Repository Stats")
                    st.write(f"**Stars:** {repo_info.get('stars', 0):,}")
                    st.write(f"**Forks:** {repo_info.get('forks', 0):,}")
                    st.write(f"**Size:** {repo_info.get('size', 0):,} KB")
            
            # Summary metrics
            st.header("📈 Summary")
            render_summary_metrics(report)
            
            # Charts
            col1, col2 = st.columns(2)
            with col1:
                render_severity_chart(report)
            with col2:
                render_type_chart(report)
            
            # Recommendations
            recommendations = report.get('recommendations', [])
            if recommendations:
                st.header("💡 Recommendations")
                for rec in recommendations:
                    st.info(rec)
            
            # Issues details
            issues = report.get('issues', [])
            if issues:
                st.header("🔍 Issues Analysis")
                
                # View options and filters
                col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                with col1:
                    severity_filter = st.selectbox(
                        "🎯 Severity",
                        ["All"] + sorted(list(set(issue.get('severity', 'MEDIUM') for issue in issues)), 
                                        key=lambda x: {'CRITICAL': 5, 'HIGH': 4, 'MEDIUM': 3, 'LOW': 2, 'INFO': 1}.get(x, 0), reverse=True)
                    )
                
                with col2:
                    type_filter = st.selectbox(
                        "🏷️ Type",
                        ["All"] + sorted(list(set(issue.get('type', 'unknown') for issue in issues)))
                    )
                
                with col3:
                    file_filter = st.selectbox(
                        "📁 File",
                        ["All"] + sorted(list(set(issue.get('file_path', 'N/A') for issue in issues)))
                    )
                
                with col4:
                    view_mode = st.selectbox(
                        "👁️ View",
                        ["Detailed", "Compact"]
                    )
                
                # Apply filters
                filtered_issues = issues
                if severity_filter != "All":
                    filtered_issues = [i for i in filtered_issues if i.get('severity') == severity_filter]
                if type_filter != "All":
                    filtered_issues = [i for i in filtered_issues if i.get('type') == type_filter]
                if file_filter != "All":
                    filtered_issues = [i for i in filtered_issues if i.get('file_path') == file_filter]
                
                # Sort by severity
                severity_order = {'CRITICAL': 5, 'HIGH': 4, 'MEDIUM': 3, 'LOW': 2, 'INFO': 1}
                filtered_issues.sort(key=lambda x: severity_order.get(x.get('severity', 'MEDIUM'), 0), reverse=True)
                
                # Results summary
                st.markdown(f"**📊 Showing {len(filtered_issues)} of {len(issues)} issues**")
                
                if filtered_issues:
                    if view_mode == "Compact":
                        render_compact_issues_table(filtered_issues)
                    else:
                        # Display detailed issues
                        for i, issue in enumerate(filtered_issues):
                            render_issue_card(issue, i)
                else:
                    st.info("🎉 No issues found with the current filters!")
            
            # Export options
            st.header("📤 Export Results")
            col1, col2 = st.columns(2)
            
            with col1:
                # JSON export
                json_data = json.dumps(report, indent=2)
                st.download_button(
                    label="📄 Download JSON Report",
                    data=json_data,
                    file_name=f"issue_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
            
            with col2:
                # CSV export for issues
                if issues:
                    df = pd.DataFrame(issues)
                    csv_data = df.to_csv(index=False)
                    st.download_button(
                        label="📊 Download CSV Issues",
                        data=csv_data,
                        file_name=f"issues_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
        
        else:
            st.error(f"❌ Analysis failed: {result['error']}")
    
    # Footer
    st.markdown("---")
    st.markdown("**IssueAnalyzer** - Powered by Tree-sitter, Gemini AI, and LangGraph")

if __name__ == "__main__":
    main()
