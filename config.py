import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Gemini API configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    
    # Gemini CLI configuration
    USE_GEMINI_CLI = os.getenv('USE_GEMINI_CLI', 'false').lower() == 'true'
    GEMINI_CLI_PATH = os.getenv('GEMINI_CLI_PATH', 'gemini')
    
    # Supported file extensions for analysis
    SUPPORTED_EXTENSIONS = {
        '.py': 'python',
        '.js': 'javascript', 
        '.ts': 'typescript',
        '.java': 'java',
        '.cpp': 'cpp',
        '.c': 'c',
        '.cs': 'c_sharp',
        '.go': 'go',
        '.rb': 'ruby',
        '.php': 'php'
    }
    
    # Issue severity levels
    SEVERITY_LEVELS = {
        'CRITICAL': 5,
        'HIGH': 4,
        'MEDIUM': 3,
        'LOW': 2,
        'INFO': 1
    }
    
    # Maximum files to analyze (to prevent overwhelming the system)
    MAX_FILES_TO_ANALYZE = 50
    
    # Maximum file size in bytes (1MB)
    MAX_FILE_SIZE = 1024 * 1024
