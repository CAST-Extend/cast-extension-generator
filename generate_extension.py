#!/usr/bin/env python3
import json
import sys
from pathlib import Path
from generators.xml_generator import CastXMLGenerator
from generators.structure_generator import StructureGenerator
from generators.gitignore_generator import GitignoreGenerator
from generators.nuspec_generator import NuspecGenerator
from generators.template_generator import TemplateGenerator

def load_config(config_path):
    with open(config_path, 'r', encoding='utf-8-sig') as f:
        return json.load(f)

def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_extension.py <config_input.json> [output_dir]")
        sys.exit(1)
    
    config_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else '.'
    
    config = load_config(config_path)
    
    language = config['language']
    namespace = config['namespace']
    techname = language.lower()
    
    # If namespace is 'product', don't include it in the extension name
    if namespace == 'product':
        extension_dir = Path(output_dir) / f"com.castsoftware.{techname}"
    else:
        extension_dir = Path(output_dir) / f"com.castsoftware.{namespace}.{techname}"
    
    print(f"Generating CAST extension: {extension_dir}")
    
    struct_gen = StructureGenerator(config, extension_dir)
    struct_gen.create_structure()
    
    xml_gen = CastXMLGenerator(config, extension_dir)
    xml_gen.generate_xmls()
    
    gitignore_gen = GitignoreGenerator(extension_dir)
    gitignore_gen.generate()
    
    nuspec_gen = NuspecGenerator(config, extension_dir)
    nuspec_gen.generate()
    
    template_gen = TemplateGenerator(config, extension_dir)
    template_gen.generate_all()
    
    print(f"\n Extension generated successfully: {extension_dir}")

if __name__ == '__main__':
    main()