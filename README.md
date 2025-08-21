# IssueAnalyzer

A comprehensive GitHub repository analysis tool that identifies code issues, bugs, and improvement opportunities using advanced static analysis and AI-powered insights.

🔗 [IssueAnalyzer](https://issueanalyzer.streamlit.app/)

## Features

- **GitHub Integration**: Analyze any public GitHub repository by URL
- **Multi-Language Support**: Python, JavaScript, Java, C++, C, C#, Go, Ruby, PHP
- **Static Code Analysis**: Tree-sitter based parsing for accurate code structure analysis
- **AI-Powered Analysis**: Gemini AI integration for logic simulation and advanced issue detection
- **Pipeline Orchestration**: LangGraph-based workflow for efficient processing
- **Interactive Dashboard**: Streamlit frontend with visualizations and filtering
- **Comprehensive Reports**: Detailed issue reports with severity levels and improvement suggestions

## How to run the projetc

### Prerequisites
- Python 3.8+
- Git
- Gemini API key (optional, for enhanced AI analysis)
- Gemini CLI

### Installation

1. **Clone the repository**:

   ```bash
   git clone <https://github.com/Prishatank0607/Issue_Analyzer>
   cd IssueAnalyzer
   ```

3. **Install dependencies**:
   
   ```bash
   pip install -r requirements.txt
   ```
   
4. **Configure API keys** (optional):
   
   ```bash
   cp .env.example .env
   # Edit .env, add your Gemini API key and Gemini CLI path
   ```

6. **Run the application**:
   
   ```bash
   streamlit run app.py
   ```

8. **Open your browser** and navigate to `http://localhost:8501`

## Deployment

### **Streamlit Cloud Deployment**

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io/)
   - Connect your GitHub repository
   - Set environment variables:
     - `GEMINI_API_KEY`: Your GEMINI API key
   - Deploy!


## Configuration

### Environment Variables

Create a `.env` file with the following variables:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### Supported File Types

- Python (`.py`)
- JavaScript (`.js`)
- TypeScript (`.ts`)
- Java (`.java`)
- C++ (`.cpp`)
- C (`.c`)
- C# (`.cs`)
- Go (`.go`)
- Ruby (`.rb`)
- PHP (`.php`)

##  Analysis Types

### Static Analysis
- Code quality issues
- Security vulnerabilities
- Performance problems
- Maintainability concerns
- Code smells

### AI-Powered Analysis
- Logic error detection
- Runtime issue simulation
- Advanced pattern recognition
- Context-aware suggestions

## Architecture

```
IssueAnalyzer/
├── app.py                 # Streamlit frontend
├── pipeline.py            # LangGraph orchestration
├── github_parser.py       # GitHub repository handling
├── code_analyzer.py       # Static analysis (Tree-sitter)
├── gemini_analyzer.py     # AI analysis (Gemini)
├── config.py             # Configuration management
├── requirements.txt      # Python dependencies
└── README.md            # Documentation
```

## Analysis Workflow

1. **Repository Parsing**: Clone and extract code files from GitHub
2. **Static Analysis**: Tree-sitter based code structure analysis
3. **AI Analysis**: Gemini-powered logic simulation and issue detection
4. **Report Generation**: Comprehensive analysis report with recommendations
5. **Visualization**: Interactive dashboard with charts and filters

## Issue Severity Levels

- **CRITICAL**: Security vulnerabilities, logic errors that could cause crashes
- **HIGH**: Performance issues, potential bugs
- **MEDIUM**: Code quality issues, maintainability concerns
- **LOW**: Style issues, minor improvements
- **INFO**: Informational suggestions

## Usage Examples

### Analyze a Repository

1. Open the Streamlit app
2. Enter a GitHub repository URL (e.g., `https://github.com/owner/repo`)
3. Click "Analyze Repository"
4. View the comprehensive analysis report

### Export Results

- **JSON Report**: Complete analysis data
- **CSV Issues**: Tabular format for spreadsheet analysis

## Development

### Project Structure

- `github_parser.py`: Handles GitHub repository cloning and file extraction
- `code_analyzer.py`: Static analysis using Tree-sitter
- `gemini_analyzer.py`: AI-powered analysis and suggestions
- `pipeline.py`: LangGraph workflow orchestration
- `app.py`: Streamlit web interface
- `config.py`: Configuration and constants

### Adding New Languages

1. Add language extension to `SUPPORTED_EXTENSIONS` in `config.py`
2. Update Tree-sitter language setup in `code_analyzer.py`
3. Add language-specific analysis rules

### Extending Analysis

1. Add new analysis functions to `StaticAnalyzer` class
2. Update `GeminiAnalyzer` prompts for new issue types
3. Modify pipeline workflow in `pipeline.py`

## Security & Privacy

- Repository data is processed locally and temporarily
- No code is stored permanently
- API keys are handled securely via environment variables
- Temporary directories are cleaned up after analysis


## Contribution

Contributions are welcome! Feel free to open issues or pull requests for any improvements or new features related to data analysis, model development, visualization techniques, or application development. Let's work together!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request


## Troubleshooting

### Common Issues

1. **Tree-sitter build errors**: Install build tools for your platform
2. **Gemini API errors**: Check API key configuration
3. **Memory issues**: Reduce `MAX_FILES_TO_ANALYZE` in config
4. **Git clone failures**: Check repository URL and permissions

### Getting Help

- Check the logs in the Streamlit interface
- Review error messages in the terminal
- Ensure all dependencies are installed correctly

## Future Enhancements

- [ ] Support for more programming languages
- [ ] Integration with other AI models
- [ ] Batch analysis for multiple repositories
- [ ] CI/CD integration
- [ ] Custom rule configuration
- [ ] Historical analysis tracking

---

**Built using Tree-sitter, Gemini AI, LangGraph, and Streamlit**
