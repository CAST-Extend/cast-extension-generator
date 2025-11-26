from pathlib import Path

class GitignoreGenerator:
    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
    
    def generate(self):
        gitignore_content = """__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
*.nupkg
*.log
.vscode/
.idea/
*.swp
*.swo
*~
"""
        gitignore_file = self.output_dir / ".gitignore"
        gitignore_file.write_text(gitignore_content, encoding='utf-8')
        print(f"✓ Generated: {gitignore_file}")