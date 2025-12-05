from pathlib import Path
import shutil

class StructureGenerator:
    def __init__(self, config, output_dir):
        self.config = config
        self.output_dir = Path(output_dir)
        self.language = config['language']
        self.techname = config['language'].lower()
        self.extensions = config['extensions']
        self.comment = config.get('comment', '#')
        self.multiline_comment = config.get('multiline_comment')
        self.static_dir = Path(__file__).parent.parent / "static"
    
    def create_structure(self):
        dirs = [
            f"configuration/Languages/{self.language}/res",
            "configuration/TCC",
            "licenses",
            "tests/test_data"
        ]
        
        for d in dirs:
            (self.output_dir / d).mkdir(parents=True, exist_ok=True)
        
        (self.output_dir / "tests" / "__init__.py").touch()
        
        # Create valid TCCSetup XML file
        tcc_file = self.output_dir / "configuration" / "TCC" / f"Base_{self.language}.TCCSetup"
        tcc_content = f'''<setup version="1.0.0.0" encoding="UTF-8">
<associations package="Base_{self.language}" version="1.0.0" encoding="UTF-8" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="CAST-Sets.xsd">
</associations>
<prefixes version="1.0.0.0" encoding="UTF-8">
</prefixes>
<ignoredtables version="1.0.0.0" encoding="UTF-8">
</ignoredtables>
</setup>'''
        tcc_file.write_text(tcc_content, encoding='utf-8')
        
        # Create LanguagePattern.xml for comment detection
        self._create_language_pattern()
        
        # Copy license from static/
        license_src = self.static_dir / "COPYING.LESSER.txt"
        license_dst = self.output_dir / "licenses" / "COPYING.LESSER.txt"
        shutil.copy(license_src, license_dst)
        
        # Copy bat from static/
        bat_src = self.static_dir / "plugin-to-nupkg.bat"
        bat_dst = self.output_dir / "plugin-to-nupkg.bat"
        shutil.copy(bat_src, bat_dst)
        
        # Copy cast_upgrade files from static/
        upgrade_py_src = self.static_dir / "cast_upgrade_1_6_23.py"
        upgrade_py_dst = self.output_dir / "cast_upgrade_1_6_23.py"
        shutil.copy(upgrade_py_src, upgrade_py_dst)
        
        upgrade_zip_src = self.static_dir / "lib_cast_upgrade_1_6_23.zip"
        upgrade_zip_dst = self.output_dir / "lib_cast_upgrade_1_6_23.zip"
        shutil.copy(upgrade_zip_src, upgrade_zip_dst)
        
        readme = self.output_dir / "README.md"
        readme.write_text(f"# {self.language} Extension\n\nCAST Extension for {self.language} analysis.\n", encoding='utf-8')
        
        print(f"[OK] Created base structure: {self.output_dir}")
    
    def _create_language_pattern(self):
        """Create LanguagePattern.xml for comment detection."""
        # Escape special XML characters in comment patterns
        comment_escaped = self.comment.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        # Build multiline comment section if defined
        multiline_section = ""
        if self.multiline_comment:
            ml_begin = self.multiline_comment.get('begin', '/*')
            ml_end = self.multiline_comment.get('end', '*/')
            ml_begin_escaped = ml_begin.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            ml_end_escaped = ml_end.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            multiline_section = f'''
        <!-- Multi-line comment -->
        <comment>
                <begin><![CDATA[[{ml_begin_escaped}]]]></begin>
                <end><![CDATA[[{ml_end_escaped}]]]></end>
                <multiline>true</multiline>
        </comment>'''
        
        content = f'''<?xml version="1.0" encoding="utf-8"?>

<languagePattern id="{self.language}">

        <!-- Single line comment -->
        <comment>
                <begin><![CDATA[[{comment_escaped}]]]></begin>
                <end><![CDATA[[\\r\\n]]]></end>
                <multiline>false</multiline>
        </comment>
{multiline_section}
</languagePattern>
'''
        filepath = self.output_dir / "configuration" / "Languages" / self.language / f"{self.language}LanguagePattern.xml"
        filepath.write_text(content, encoding='utf-8')
        print(f"[OK] Generated: {filepath}")