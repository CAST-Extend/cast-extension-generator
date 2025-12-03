from pathlib import Path


class TemplateGenerator:
    """
    Generates Python source files from templates for CAST extensions.
    
    Handles:
    - Analyzer level (2-pass architecture)
    - Module class (parsing logic)
    - Application level (cross-technology)
    - Test files
    """
    
    def __init__(self, config, output_dir):
        self.config = config
        self.output_dir = Path(output_dir)
        self.language = config['language']
        self.techname = config['language'].lower()
        self.template_dir = Path(__file__).parent.parent / "templates"
        
        # Build placeholder mappings
        self._build_placeholders()
    
    def _build_placeholders(self):
        """Build the placeholder dictionary from config."""
        # File extensions list for the analyzer
        extensions = self.config.get('extensions', [])
        extensions_list = ', '.join([f"'.{ext}'" for ext in extensions])
        
        # Comment syntax
        comment = self.config.get('comment', '//')
        
        # Grammar patterns (new format with multiple patterns per type)
        grammar = self.config.get('grammar', {})
        patterns = grammar.get('patterns', {})
        
        # Build patterns dict as Python code
        patterns_code = self._build_patterns_code(patterns)
        
        call_pattern = grammar.get('call_pattern', r'\b(\w+)\s*\(')
        keywords = grammar.get('keywords', ['if', 'else', 'for', 'while', 'return'])
        
        # Format keywords as Python set literal content
        keywords_set = ',\n'.join([f"            '{kw}'" for kw in keywords])
        
        # Object hierarchy (new format)
        objects_config = self.config.get('objects', {})
        objects_code = self._build_objects_code(objects_config)
        
        # Class names
        self.placeholders = {
            '{{LANGUAGE}}': self.language,
            '{{ANALYZER_CLASS}}': f'{self.language}AnalyzerExtension',
            '{{MODULE_CLASS}}': f'{self.language}Module',
            '{{APPLICATION_CLASS}}': f'{self.language}ApplicationExtension',
            '{{MODULE_FILE}}': f'{self.techname}_module',
            '{{MODULE_FILE_IMPORT}}': f'{self.techname}_module',
            '{{EXTENSIONS_LIST}}': extensions_list,
            '{{COMMENT}}': comment,
            # Grammar patterns (new format)
            '{{PATTERNS_DICT}}': patterns_code,
            '{{CALL_PATTERN}}': call_pattern,
            '{{KEYWORDS_SET}}': keywords_set,
            # Object hierarchy
            '{{OBJECTS_CONFIG}}': objects_code,
        }
    
    def _build_patterns_code(self, patterns):
        """Build Python code for patterns dictionary with multiple patterns per type."""
        if not patterns:
            # Default patterns if none provided
            patterns = {
                'class': [r'^\s*class\s+(?P<name>\w+)'],
                'function': [r'^\s*function\s+(?P<name>\w+)'],
                'method': [r'^\s+(?P<name>\w+)\s*\(']
            }
        
        lines = []
        for obj_type, pattern_list in patterns.items():
            patterns_str = ', '.join([f"r'{p}'" for p in pattern_list])
            lines.append(f"            '{obj_type}': [{patterns_str}],")
        
        return '\n'.join(lines)
    
    def _build_objects_code(self, objects_config):
        """
        Build Python code for object hierarchy configuration.
        
        New format:
        {
          "Program": {"parent": "file", "pattern_keys": []},
          "Class": {"parent": "Program", "pattern_keys": ["class"]},
          ...
        }
        
        Legacy format (still supported):
        {
          "Program": "file",
          "Class": "Program",
          ...
        }
        """
        lines = []
        
        for obj_type, obj_def in objects_config.items():
            if isinstance(obj_def, dict):
                # New format
                parent = obj_def.get('parent', 'file')
                pattern_keys = obj_def.get('pattern_keys', [])
                patterns_str = ', '.join([f"'{p}'" for p in pattern_keys])
                lines.append(f"        '{obj_type}': {{'parent': '{parent}', 'pattern_keys': [{patterns_str}]}},")
            else:
                # Legacy format - convert to new format with inferred pattern_keys
                parent = obj_def
                # Infer pattern key from lowercase object type
                pattern_key = obj_type.lower()
                if parent == 'file':
                    # Program type - no pattern
                    lines.append(f"        '{obj_type}': {{'parent': '{parent}', 'pattern_keys': []}},")
                else:
                    lines.append(f"        '{obj_type}': {{'parent': '{parent}', 'pattern_keys': ['{pattern_key}']}},")
        
        return '\n'.join(lines)
    
    def _apply_placeholders(self, content):
        """Apply all placeholders to template content."""
        for placeholder, value in self.placeholders.items():
            content = content.replace(placeholder, value)
        return content
    
    def _load_template(self, template_name):
        """Load a template file."""
        template_path = self.template_dir / template_name
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def generate_all(self):
        """Generate all template-based files."""
        self._generate_module()  # Generate module first (imported by analyzer)
        self._generate_analyser_level()
        self._generate_application_level()
        self._generate_test()
    
    def _generate_module(self):
        """Generate the module class file."""
        template = self._load_template('module.template')
        content = self._apply_placeholders(template)
        
        output_file = self.output_dir / f"{self.techname}_module.py"
        output_file.write_text(content, encoding='utf-8')
        print(f"✓ Generated: {output_file}")
    
    def _generate_analyser_level(self):
        """Generate the analyzer level file."""
        template = self._load_template('analyser_level.template')
        content = self._apply_placeholders(template)
        
        output_file = self.output_dir / f"{self.techname}_analyser_level.py"
        output_file.write_text(content, encoding='utf-8')
        print(f"✓ Generated: {output_file}")
    
    def _generate_application_level(self):
        """Generate the application level file."""
        template = self._load_template('application_level.template')
        content = self._apply_placeholders(template)
        
        output_file = self.output_dir / f"{self.techname}_application_level.py"
        output_file.write_text(content, encoding='utf-8')
        print(f"✓ Generated: {output_file}")
    
    def _generate_test(self):
        """Generate the test file."""
        template = self._load_template('test.template')
        content = self._apply_placeholders(template)
        
        # Write test file
        output_file = self.output_dir / "tests" / f"test_{self.techname}.py"
        output_file.write_text(content, encoding='utf-8')
        print(f"✓ Generated: {output_file}")