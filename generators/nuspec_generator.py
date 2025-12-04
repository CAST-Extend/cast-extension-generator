from pathlib import Path

class NuspecGenerator:
    def __init__(self, config, output_dir):
        self.config = config
        self.output_dir = Path(output_dir)
    
    def generate(self):
        template_path = Path(__file__).parent.parent / "templates" / "plugin.nuspec.template"
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # Build extension ID: for 'product' namespace, don't include namespace in ID
        namespace = self.config['namespace']
        language_lower = self.config['language'].lower()
        if namespace == 'product':
            extension_id = f"com.castsoftware.{language_lower}"
        else:
            extension_id = f"com.castsoftware.{namespace}.{language_lower}"
        
        replacements = {
            '{{EXTENSION_ID}}': extension_id,
            '{{NAMESPACE}}': namespace,
            '{{LANGUAGE_LOWER}}': language_lower,
            '{{VERSION}}': self.config['version'],
            '{{LANGUAGE}}': self.config['language'],
            '{{AUTHOR}}': self.config['author'],
            '{{EXTENSIONS_UPPER}}': ', '.join(ext.upper() for ext in self.config['extensions']),
            '{{TAGS}}': self.config['tags']
        }
        
        content = template
        for key, value in replacements.items():
            content = content.replace(key, value)
        
        output_file = self.output_dir / "plugin.nuspec"
        output_file.write_text(content, encoding='utf-8')
        print(f"[OK] Generated: {output_file}")