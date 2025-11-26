from pathlib import Path

class TemplateGenerator:
    def __init__(self, config, output_dir):
        self.config = config
        self.output_dir = Path(output_dir)
        self.language = config['language']
        self.techname = config['language'].lower()
    
    def generate_all(self):
        self._generate_analyser_level()
        self._generate_application_level()
        self._generate_test()
    
    def _generate_analyser_level(self):
        # TODO: implement later
        output_file = self.output_dir / f"{self.techname}_analyser_level.py"
        output_file.write_text("# TODO: implement analyser level\n", encoding='utf-8')
        print(f"✓ Generated stub: {output_file}")
    
    def _generate_application_level(self):
        # TODO: implement later
        output_file = self.output_dir / f"{self.techname}_application_level.py"
        output_file.write_text("# TODO: implement application level\n", encoding='utf-8')
        print(f"✓ Generated stub: {output_file}")
    
    def _generate_test(self):
        # Load test template
        template_path = Path(__file__).parent.parent / "templates" / "test.template"
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # Replace placeholders
        content = template.replace('{{LANGUAGE}}', self.language)
        
        # Write test file
        output_file = self.output_dir / "tests" / f"test_{self.techname}.py"
        output_file.write_text(content, encoding='utf-8')
        print(f"✓ Generated: {output_file}")