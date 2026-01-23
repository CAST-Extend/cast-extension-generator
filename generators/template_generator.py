from pathlib import Path


class TemplateGenerator:
    """
    Generates Python source files from templates for CAST extensions.
    
    Handles:
    - Analyzer level (2-pass architecture)
    - Module class (parsing logic)
    - Application level (cross-technology)
    - Test files
    - Extension README
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
        
        # Comment syntax - escape backslashes for Python string safety
        comment = self.config.get('comment', '//')
        comment_escaped = comment.replace('\\', '\\\\')
        
        # Grammar patterns (new format with multiple patterns per type)
        grammar = self.config.get('grammar', {})
        patterns = grammar.get('patterns', {})
        
        # Block delimiter style (braces, end_keyword, indentation)
        block_delimiters = grammar.get('block_delimiters', 'braces')
        
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
            '{{COMMENT}}': comment_escaped,
            # Grammar patterns (new format)
            '{{PATTERNS_DICT}}': patterns_code,
            '{{CALL_PATTERN}}': call_pattern,
            '{{KEYWORDS_SET}}': keywords_set,
            # Object hierarchy
            '{{OBJECTS_CONFIG}}': objects_code,
            # Block delimiter style
            '{{BLOCK_DELIMITERS}}': block_delimiters,
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
            patterns_str = ', '.join([repr(p) for p in pattern_list])
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
        self._generate_extension_readme()  # Generate README for the extension
    
    def _generate_extension_readme(self):
        """Generate the extension's README.md with proper Pass 1/Pass 2 documentation."""
        # Get first extension
        extensions = self.config.get('extensions', ['txt'])
        first_extension = extensions[0]
        
        # Format extensions for display
        extensions_formatted = ', '.join([f'`*.{ext}`' for ext in extensions])

        # List of detected objects with descriptions
        objects_config = self.config.get('objects', {})
        objects_lines = []
        for obj_type, obj_def in objects_config.items():
            if isinstance(obj_def, dict):
                parent = obj_def.get('parent', 'file')
            else:
                parent = obj_def
            
            if parent == 'file':
                objects_lines.append(f"- **{obj_type}**: Top-level container for all code structures")
            else:
                objects_lines.append(f"- **{obj_type}**: {obj_type} definitions inside {parent}")
        
        objects_list = '\n'.join(objects_lines) if objects_lines else "- (Default object types)"

        # Multiline comment info
        multiline_comment_info = ""
        if self.config.get('multiline_comment'):
            ml_begin = self.config['multiline_comment'].get('begin', '/*')
            ml_end = self.config['multiline_comment'].get('end', '*/')
            multiline_comment_info = f"\n- **Multi-line comments**: `{ml_begin} ... {ml_end}`"

        # Block delimiters description
        grammar = self.config.get('grammar', {})
        block_delimiters = grammar.get('block_delimiters', 'braces')
        block_delim_desc = {
            'braces': 'Curly braces `{...}`',
            'end_keyword': 'End keyword (e.g. `end`, `endif`)',
            'indentation': 'Indentation-based (Python style)',
            'sequential': 'Sequential blocks (COBOL style)'
        }.get(block_delimiters, block_delimiters)

        # Namespace handling
        namespace = self.config.get('namespace', 'uc')
        namespace_lower = 'uc' if namespace == 'product' else namespace

        # Comment for README
        comment = self.config.get('comment', '//')
        
        # Extended placeholders for README
        readme_placeholders = {
            **self.placeholders,
            '{{VERSION}}': self.config.get('version', '1.0.0'),
            '{{AUTHOR}}': self.config.get('author', 'CAST'),
            '{{NAMESPACE}}': namespace,
            '{{NAMESPACE_LOWER}}': namespace_lower,
            '{{EXTENSIONS_LIST_FORMATTED}}': extensions_formatted,
            '{{FIRST_EXTENSION}}': first_extension,
            '{{OBJECTS_LIST}}': objects_list,
            '{{MULTILINE_COMMENT_INFO}}': multiline_comment_info,
            '{{TECHNAME}}': self.techname,
            '{{BLOCK_DELIMITERS}}': block_delim_desc,
            '{{COMMENT}}': comment,  # Use raw comment, not escaped version
        }

        # Load and apply the template
        template = self._load_template('extension_readme.template')
        content = template
        for placeholder, value in readme_placeholders.items():
            content = content.replace(placeholder, str(value))

        # Write the README
        output_file = self.output_dir / "README.md"
        output_file.write_text(content, encoding='utf-8')
        print(f"[OK] Generated: {output_file}")
    
    def _generate_module(self):
        """Generate the module class file."""
        template = self._load_template('module.template')
        content = self._apply_placeholders(template)
        
        output_file = self.output_dir / f"{self.techname}_module.py"
        output_file.write_text(content, encoding='utf-8')
        print(f"[OK] Generated: {output_file}")
    
    def _generate_analyser_level(self):
        """Generate the analyzer level file."""
        template = self._load_template('analyser_level.template')
        content = self._apply_placeholders(template)
        
        output_file = self.output_dir / f"{self.techname}_analyser_level.py"
        output_file.write_text(content, encoding='utf-8')
        print(f"[OK] Generated: {output_file}")
    
    def _generate_application_level(self):
        """Generate the application level file."""
        template = self._load_template('application_level.template')
        content = self._apply_placeholders(template)
        
        output_file = self.output_dir / f"{self.techname}_application_level.py"
        output_file.write_text(content, encoding='utf-8')
        print(f"[OK] Generated: {output_file}")
    
    def _generate_test(self):
        """Generate the test file."""
        template = self._load_template('test.template')
        content = self._apply_placeholders(template)
        
        # Write test file
        output_file = self.output_dir / "tests" / f"test_{self.techname}.py"
        output_file.write_text(content, encoding='utf-8')
        print(f"[OK] Generated: {output_file}")