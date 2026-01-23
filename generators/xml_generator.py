import json
from pathlib import Path
from xml.dom import minidom
import xml.etree.ElementTree as ET

class CastXMLGenerator:
    def __init__(self, config, output_dir):
        self.config = config
        self.output_dir = Path(output_dir)
        
        self.language = config['language']
        self.file_no = config['file_no']
        self.extensions = config['extensions']
        self.comment = config.get('comment', '#')
        self.multiline_comment = config.get('multiline_comment')
        self.objects = config['objects']
        
        self.id_range_start = 2_000_000 + (self.file_no * 1000)
        self.id_range_end = self.id_range_start + 999
        
        self.rid_counter = 4
        self.object_rids = {}
    
    def _get_rid(self, name):
        if name not in self.object_rids:
            self.object_rids[name] = self.rid_counter
            self.rid_counter += 1
        return self.object_rids[name]
    
    def _get_parent_name(self, parent_value):
        """
        Determine the Enlighten tree parent based on object hierarchy.
        
        The parent value comes from objects config and determines the tree structure.
        This is critical for Imaging to display the correct object hierarchy.
        """
        # Special case: 'file' means top-level object
        if parent_value == 'file':
            return f"Enlighten{self.language}"
        
        # Otherwise, use the parent object type as the tree parent
        # This creates the proper hierarchy: Program > Class > Method
        return f"{self.language}{parent_value}"
    
    def _get_inherited_categories(self, obj_name, parent_value):
        categories = ["UAObject", f"{self.language} Artifacts"]
        
        if obj_name == "Program":
            categories.insert(1, "METRICABLE")
            categories.insert(2, self.language)
        
        module_like = ["Module", "Package", "Namespace", "Schema", "Library", "DataArea"]
        if obj_name in module_like or parent_value in module_like:
            categories.append(f"{self.language} Module")
            if self.language not in categories:
                categories.insert(2, self.language)
        
        if obj_name == "Project":
            categories[0] = "UAProject"
            if self.language not in categories:
                categories.insert(1, self.language)
            if f"{self.language} Module" not in categories:
                categories.append(f"{self.language} Module")
        
        return categories
    
    def generate_metamodel(self):
        root = ET.Element('metaModel')
        root.set('file_level', 'client')
        root.set('file_no', str(self.file_no))
        
        comment = ET.Comment(f' ID range is {self.id_range_start} to {self.id_range_end} ')
        root.append(comment)
        
        root.append(ET.Comment(' ========================================================= '))
        root.append(ET.Comment('       CATEGORIES                                           '))
        root.append(ET.Comment(' ========================================================= '))
        
        self._add_categories(root)
        
        root.append(ET.Comment(' ========================================================= '))
        root.append(ET.Comment('       TYPES                                               '))
        root.append(ET.Comment(' ========================================================= '))
        
        self._add_enlighten_group(root)
        self._add_object_types(root)
        
        # Add Project type at the end - required for CAST UA to find the project
        self._add_project_type(root)
        
        return self._prettify_xml(root)
    
    def _add_project_type(self, parent):
        """Add the Project type required by CAST UA framework."""
        parent.append(ET.Comment(f' {self.language} project '))
        
        type_elem = ET.SubElement(parent, 'type')
        type_elem.set('name', f'{self.language}Project')
        type_elem.set('rid', str(self._get_rid('Project')))
        
        desc = ET.SubElement(type_elem, 'description')
        desc.text = f'{self.language} Project'
        
        ET.SubElement(type_elem, 'inheritedCategory', name='UAProject')
        ET.SubElement(type_elem, 'inheritedCategory', name=self.language)
        ET.SubElement(type_elem, 'inheritedCategory', name=f'{self.language} Module')
    
    def _add_categories(self, parent):
        cat = ET.SubElement(parent, 'category')
        cat.set('name', self.language)
        cat.set('rid', '0')
        
        desc = ET.SubElement(cat, 'description')
        desc.text = self.language
        
        attr = ET.SubElement(cat, 'attribute')
        attr.set('name', 'extensions')
        extensions_str = ';'.join(f"*.{ext}" for ext in self.extensions)
        attr.set('stringValue', extensions_str)
        
        ET.SubElement(cat, 'inheritedCategory', name='UniversalLanguage')
        ET.SubElement(cat, 'inheritedCategory', name='CsvLanguage')
        
        cat = ET.SubElement(parent, 'category')
        cat.set('name', f"{self.language} Artifacts")
        cat.set('rid', '1')
        desc = ET.SubElement(cat, 'description')
        desc.text = f"{self.language} Artifacts"
        ET.SubElement(cat, 'inheritedCategory', name='APM Client Language Artifacts')
        
        cat = ET.SubElement(parent, 'category')
        cat.set('name', f"{self.language} Module")
        cat.set('rid', '2')
        desc = ET.SubElement(cat, 'description')
        desc.text = f"{self.language} Module category"
        ET.SubElement(cat, 'inheritedCategory', name='APM Client Modules')
    
    def _add_enlighten_group(self, parent):
        type_elem = ET.SubElement(parent, 'type')
        type_elem.set('name', f"Enlighten{self.language}")
        type_elem.set('rid', '3')
        
        desc = ET.SubElement(type_elem, 'description')
        desc.text = self.language
        
        tree = ET.SubElement(type_elem, 'tree')
        tree.set('parent', 'EnlightenUniversalObjects')
        tree.set('category', 'EnlightenTree')
    
    def _add_object_types(self, parent):
        descriptions = {
            "Program": f"{self.language} Program",
            "Project": f"{self.language} Project",
            "Package": f"{self.language} Package",
            "Namespace": f"{self.language} Namespace",
            "Module": f"{self.language} Module",
            "Schema": f"{self.language} Schema",
            "Library": f"{self.language} Library",
            "Section": f"{self.language} Section",
            "DataArea": f"{self.language} Data Area",
            "Class": f"{self.language} Class",
            "Interface": f"{self.language} Interface",
            "Struct": f"{self.language} Struct",
            "Enum": f"{self.language} Enumeration",
            "Record": f"{self.language} Record",
            "Union": f"{self.language} Union",
            "Trait": f"{self.language} Trait",
            "Method": f"Method in a {self.language} Class",
            "Function": f"Standalone {self.language} Function",
            "Procedure": f"{self.language} Procedure",
            "Subroutine": f"{self.language} Subroutine",
            "Lambda": f"{self.language} Lambda Function",
            "Constructor": f"Constructor in a {self.language} Class",
            "Destructor": f"Destructor in a {self.language} Class",
            "Paragraph": f"{self.language} Paragraph",
            "Job": f"{self.language} Job",
            "Step": f"{self.language} Step",
            "Proc": f"{self.language} Proc",
            "Table": f"{self.language} Table",
            "View": f"{self.language} View",
            "Trigger": f"{self.language} Trigger",
            "Index": f"{self.language} Index",
            "Sequence": f"{self.language} Sequence",
            "Cursor": f"{self.language} Cursor",
            "Variable": f"{self.language} Variable",
            "Constant": f"{self.language} Constant",
            "Property": f"Property in a {self.language} Class",
            "Field": f"Field in a {self.language} Class",
            "Attribute": f"Attribute in a {self.language} Class",
            "DataItem": f"{self.language} Data Item",
            "FileDescriptor": f"{self.language} File Descriptor",
            "Annotation": f"{self.language} Annotation",
            "Decorator": f"{self.language} Decorator",
            "Macro": f"{self.language} Macro",
            "Template": f"{self.language} Template",
            "Generic": f"{self.language} Generic Type",
            "Event": f"{self.language} Event",
            "Delegate": f"{self.language} Delegate",
            "Label": f"{self.language} Label"
        }
        
        for obj_name, obj_def in self.objects.items():
            # Support both new format (dict) and legacy format (string)
            if isinstance(obj_def, dict):
                parent_value = obj_def.get('parent', 'file')
            else:
                parent_value = obj_def
            
            type_elem = ET.SubElement(parent, 'type')
            type_elem.set('name', f"{self.language}{obj_name}")
            type_elem.set('rid', str(self._get_rid(obj_name)))
            
            desc = ET.SubElement(type_elem, 'description')
            desc.text = descriptions.get(obj_name, f"{self.language} {obj_name}")
            
            categories = self._get_inherited_categories(obj_name, parent_value)
            for cat in categories:
                ET.SubElement(type_elem, 'inheritedCategory', name=cat)
            
            if obj_name == "Program":
                attr = ET.SubElement(type_elem, 'attribute')
                attr.set('name', 'AUTO_FOLDER_THRESHOLD')
                attr.set('intValue', '1')
            
            tree = ET.SubElement(type_elem, 'tree')
            tree.set('parent', self._get_parent_name(parent_value))
            tree.set('category', 'EnlightenTree')
    
    def _escape_regex(self, text):
        """Escape special regex characters for use in LanguagePattern XML."""
        # Characters that need escaping in regex
        special_chars = ['\\', '.', '^', '$', '*', '+', '?', '{', '}', '[', ']', '(', ')', '|']
        result = text
        for char in special_chars:
            result = result.replace(char, '\\' + char)
        return result
    
    def generate_language_pattern(self):
        root = ET.Element('languagePattern')
        root.set('id', self.language)
        
        comment_elem = ET.SubElement(root, 'comment')
        begin = ET.SubElement(comment_elem, 'begin')
        # Escape the comment character for regex
        escaped_comment = self._escape_regex(self.comment)
        begin.text = f"<![CDATA[{escaped_comment}]]>"
        end = ET.SubElement(comment_elem, 'end')
        end.text = "<![CDATA[[\\r\\n]]]>"
        multiline = ET.SubElement(comment_elem, 'multiline')
        multiline.text = "false"
        
        if self.multiline_comment:
            comment_elem = ET.SubElement(root, 'comment')
            begin = ET.SubElement(comment_elem, 'begin')
            # Escape special regex characters
            escaped_begin = self._escape_regex(self.multiline_comment['begin'])
            begin.text = f"<![CDATA[{escaped_begin}]]>"
            end = ET.SubElement(comment_elem, 'end')
            escaped_end = self._escape_regex(self.multiline_comment['end'])
            end.text = f"<![CDATA[{escaped_end}]]>"
            multiline = ET.SubElement(comment_elem, 'multiline')
            multiline.text = "true"
        
        return self._prettify_xml(root)
    
    def _prettify_xml(self, elem):
        rough_string = ET.tostring(elem, encoding='utf-8')
        reparsed = minidom.parseString(rough_string)
        pretty = reparsed.toprettyxml(indent='\t', encoding='utf-8').decode('utf-8')
        
        pretty = pretty.replace('&lt;![CDATA[', '<![CDATA[')
        pretty = pretty.replace(']]&gt;', ']]>')
        
        return pretty
    
    def generate_xmls(self):
        lang_dir = self.output_dir / 'configuration' / 'Languages' / self.language
        lang_dir.mkdir(parents=True, exist_ok=True)
        
        metamodel_content = self.generate_metamodel()
        metamodel_file = lang_dir / f"{self.language}MetaModel.xml"
        with open(metamodel_file, 'w', encoding='utf-8') as f:
            f.write(metamodel_content)
        print(f"[OK] Generated: {metamodel_file}")
        
        pattern_content = self.generate_language_pattern()
        pattern_file = lang_dir / f"{self.language}LanguagePattern.xml"
        with open(pattern_file, 'w', encoding='utf-8') as f:
            f.write(pattern_content)
        print(f"[OK] Generated: {pattern_file}")