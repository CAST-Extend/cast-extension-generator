from pathlib import Path
import shutil

class StructureGenerator:
    def __init__(self, config, output_dir):
        self.config = config
        self.output_dir = Path(output_dir)
        self.language = config['language']
        self.techname = config['language'].lower()
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
        
        tcc_file = self.output_dir / "configuration" / "TCC" / f"Base_{self.language}.TCCSetup"
        tcc_file.write_text(f"# TCC Setup for {self.language}\n", encoding='utf-8')
        
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