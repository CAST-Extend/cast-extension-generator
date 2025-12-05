# CAST Extension Generator

A **100% generic** tool to automatically generate CAST Universal Analyzer extensions for any programming language using a simple JSON configuration file.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Configuration Reference](#configuration-reference)
- [Quality of Grammar Inputs](#quality-of-grammar-inputs)
- [How It Works](#how-it-works)
- [Link Detection](#link-detection)
- [Extending Generated Extensions](#extending-generated-extensions)
- [Custom Parsing Override](#custom-parsing-override)
- [Analysis Summary Output](#analysis-summary-output)
- [Limitations](#limitations)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

---

## Overview

The CAST Extension Generator creates fully functional CAST analyzer extensions from a single configuration file. Instead of writing Python code manually, you define:

- **Language metadata** (name, file extensions, version)
- **Object types** to detect (classes, functions, methods, etc.)
- **Grammar patterns** (regex patterns to identify code structures)

The generator produces a complete extension with:

- Analyzer-level code (2-pass parsing architecture)
- Module-level parsing logic
- Application-level hooks for cross-technology analysis
- XML metamodel and language pattern files
- Test scaffolding

---

## Quick Start

### 1. Create a Configuration File

Create a JSON file (e.g., `config_mylang.json`):

```json
{
  "language": "MyLang",
  "namespace": "uc",
  "file_no": 50,
  "version": "1.0.0",
  "author": "Your Name",
  "extensions": ["ml", "mylang"],
  "tags": "MyLang Extension",
  "comment": "//",
  "multiline_comment": { "begin": "/*", "end": "*/" },
  "objects": {
    "Program": { "parent": "file", "pattern_keys": [] },
    "Function": { "parent": "Program", "pattern_keys": ["function"] }
  },
  "grammar": {
    "block_delimiters": "braces",
    "patterns": {
      "function": ["^\\s*func\\s+(?P<name>\\w+)\\s*\\("]
    },
    "call_pattern": "\\b(\\w+)\\s*\\(",
    "keywords": ["if", "else", "for", "while", "return"]
  }
}
```

### 2. Get Your file_no

Before generating the extension, you need to reserve a unique `file_no` for your language:

1. Go to the CAST SharePoint UA Corner:
   ```
   https://castsoftware.sharepoint.com/sites/CoffeeMachine/SitePages/UA-Corner.aspx
   ```

2. Reserve a range of IDs (e.g., `2,193,000 - 2,193,999`)

3. Calculate your `file_no` using this formula:
   ```
   file_no = (start_id - 2,000,000) / 1,000
   ```

   **Example:**
   ```
   Reserved range: 2,193,000 - 2,193,999
   file_no = (2,193,000 - 2,000,000) / 1,000 = 193
   ```

4. Use this `file_no` in your configuration file

### 3. Generate the Extension

```bash
python generate_extension.py config_mylang.json output_folder
```

### 4. Deploy to CAST Imaging

To use your extension in CAST Imaging:

1. **Create the NuGet package**
   
   Navigate to your generated extension folder and run the batch file:
   ```bash
   cd output_folder/com.castsoftware.uc.mylang
   .\plugin-to-nupkg.bat
   ```
   This creates a `.nupkg` file in the extension folder.

2. **Copy the package to CAST extensions folder**
   
   Copy the generated `.nupkg` file to:
   ```
   C:\Cast\ProgramData\CAST\AIP-Console-Standalone\data\shared\extensions\
   ```

3. **Handle conflicts with existing extensions (if needed)**
   
   If your extension conflicts with an existing CAST product extension (e.g., you're creating a custom Go extension while the official Go extension exists), you need to disable the conflicting extension:
   
   1. Open **CAST Admin Center**
   2. Go to **Extensions** → **Strategy** → **All Extensions**
   3. Search for the product extension you want to disable (e.g., `com.castsoftware.go`)
   4. Click the **Deny List** toggle to disable it

4. **Run the analysis**
   
   Once the extension is deployed (and conflicts resolved):
   1. Create a new application or use an existing one in CAST Console
   2. Run **Fast Scan** to detect source files
   3. Run **Deep Analysis** to analyze the code with your extension

### Creating an Analysis Unit Manually

Since the generated extension doesn't include a DMT discoverer, files won't be automatically detected during Fast Scan. You need to manually create an Analysis Unit:

1. **Run Fast Scan** on your application

2. **Wait for the Configuration tab** to become active (left panel, grayed out until Fast Scan completes)

3. **Go to Configuration** → Click on **Universal Technology**

4. **Click the +ADD button** to create a new Analysis Unit

5. **Fill in the fields:**
   - **Name**: Your technology name (e.g., "Go", "Lua", "MyLang")
   - **Package**: `main_sources`
   - **Select Languages**: Choose your technology from the dropdown list

6. **Save and run Deep Analysis**

Your extension's analyzer will now be triggered for the files matching your language's extensions.

> **Note:** This manual approach works for development and testing. For production/distribution, you'll want to implement a proper DMT discoverer so the extension is fully "plug and play" without manual configuration.

### 5. Validate the MetaModel Configuration (Optional)

If you want to verify that the generated MetaModel XML files are valid before running tests, you can use the UA Package Assistant:

1. Open the UA Package Assistant:
   ```
   C:\ProgramData\Microsoft\Windows\Start Menu\Programs\CAST 8.x\UAPackageAssistant.exe
   ```

2. Browse to your generated extension folder (the one containing the XML files)

3. **Important:** Check the box "Validate package MetaModel file only"

4. Click "Validate"

5. Check the Report section for any errors

If validation is successful, you'll see "Validation successful" in the Report section.

### 5. Test the Extension

Open the generated extension folder in your IDE (PyCharm for example) and configure the Python interpreter to use the CAST 8.3 Python 3.4:

```
C:/Cast/ProgramFiles/CAST/8.3/ThirdParty/Python34/python.exe
```

Then run the test file `tests/test_language.py` from your IDE's test explorer.

---

## Configuration Reference

### Top-Level Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `language` | string | ✓ | Language name (Python, Ruby, Go…) |
| `namespace` | string | ✓ | Extension namespace: "uc", "labs", or "product" (see below) |
| `file_no` | integer | ✓ | Unique file number used for CAST IDs |
| `version` | string | ✓ | Semantic version (e.g., "1.0.0") |
| `author` | string | ✓ | Extension author |
| `extensions` | array | ✓ | File extensions without dot |
| `tags` | string | ✓ | NuGet package tags |
| `comment` | string | ✓ | Single-line comment prefix |
| `multiline_comment` | object | ✓ | Multi-line comment delimiters |

#### Namespace Values

The `namespace` field determines the extension naming convention:

| Value | Extension ID | Use Case |
|-------|-------------|----------|
| `uc` | `com.castsoftware.uc.language` | User Community extensions (community-contributed) |
| `labs` | `com.castsoftware.labs.language` | Labs extensions (experimental/preview) |
| `product` | `com.castsoftware.language` | Product extensions (official CAST extensions) |

### Choosing Which Objects to Create

Before defining your `objects` configuration, understand what makes an object **useful** in CAST/Imaging.

#### The Two Types of Useful Objects

| Type | Description | Examples | Role in Imaging |
|------|-------------|----------|-----------------|
| **Callables** | Code that can be executed/called | Function, Method, Procedure, Constructor | Source AND target of call links |
| **Containers** | Organize and group callables | Class, Module, Package, Struct | Define hierarchy, appear in navigation tree |

#### What This Generator Creates

The generator creates **callLinks** between objects. A callLink represents "A calls B":

```
┌─────────────┐     callLink      ┌─────────────┐
│  Function A │ ────────────────► │  Function B │
│   (caller)  │                   │   (callee)  │
└─────────────┘                   └─────────────┘
```

For an object to participate in call analysis, it must be either:
- A **caller** (contains code that calls other functions)
- A **callee** (can be called by other code)

#### Objects You Should Create

✅ **Functions/Methods** - The core callable units of your language
```json
"Function": { "parent": "Program", "pattern_keys": ["function"] },
"Method": { "parent": "Class", "pattern_keys": ["method"] }
```

✅ **Containers that group callables** - Organize the hierarchy
```json
"Class": { "parent": "Program", "pattern_keys": ["class"] },
"Module": { "parent": "Program", "pattern_keys": ["module"] }
```

✅ **Constructors** (if your language has them) - They are callable
```json
"Constructor": { "parent": "Class", "pattern_keys": ["constructor"] }
```

#### Objects You Should NOT Create

❌ **Imports/Includes** - Declarations, not executable code
- The generator doesn't create import/dependency links
- They add noise without value

❌ **Annotations/Decorators** - Metadata, not callable
- Better represented as properties on the annotated object
- Cannot be source or target of calls

❌ **Fields/Attributes** - Data, not callable
- Unless your language allows field access as function calls
- Consider if they provide architectural value

❌ **Local Variables/Parameters** - Too granular
- Scope too limited, no cross-file relevance
- Would bloat the model without insights

❌ **Type definitions** (Enum, Typedef, Interface without methods)
- These define types but don't contain executable code
- Exception: Interface with default method implementations

#### Decision Flowchart

```
Is this code element...
    │
    ├─► Callable (can be invoked)? ──────────────► ✅ CREATE IT
    │
    ├─► A container for callables? ──────────────► ✅ CREATE IT (for hierarchy)
    │
    ├─► A declaration (import, typedef)? ────────► ❌ SKIP IT
    │
    └─► Data-only (field, variable)? ────────────► ❌ SKIP IT (usually)
```

#### Real-World Examples

| Language | Recommended Objects | Excluded |
|----------|--------------------| ---------|
| Java | Package, Class, Interface, Method, Constructor | Import, Field, Annotation, Enum |
| Python | Module, Class, Function, Method | Import, Decorator, Variable |
| Go | Struct, Interface, Function, Method | Import, Type alias, Const |
| COBOL | Program, Section, Paragraph | Data Division items |
| Rust | Struct, Impl, Function, Method | Enum, Trait, Use statement |

### Objects Configuration

The `objects` section defines the **hierarchy of code elements** your extension will detect.

```json
"objects": {
  "Program": { "parent": "file", "pattern_keys": [] },
  "Class": { "parent": "Program", "pattern_keys": ["class"] },
  "Method": { "parent": "Class", "pattern_keys": ["method"] }
}
```

**Key concepts:**

- **`parent`**: Where this object type can exist
  - `"file"` = directly under the source file (top-level container)
  - Another object type name = nested inside that type

- **`pattern_keys`**: Which grammar patterns detect this object type
  - Empty array `[]` for auto-created objects (like `Program`)
  - References pattern names from `grammar.patterns`

**Example hierarchy:**

```
File
└── Program (auto-created container)
    ├── Class (detected by "class" pattern)
    │   └── Method (detected by "method" pattern)
    └── Function (detected by "function" pattern)
```

### Grammar Configuration

The `grammar` section defines **how to parse** the source code.

#### `block_delimiters`

How code blocks are delimited. This affects how the parser determines where functions/classes end.

| Value | Description | Languages |
|-------|-------------|-----------|
| `braces` | Blocks use `{` and `}` | Go, Java, Rust, C, JS |
| `end_keyword` | Blocks end with "end" or "function...end" | Ruby, Lua, Elixir |
| `indentation` | Blocks defined by indentation | Python, YAML |
| `sequential` | No nested blocks, sequential processing | COBOL, Assembly |

#### `patterns`

Regex patterns to detect code structures. Each pattern **must** have a named capture group `(?P<name>...)` to extract the object's name.

```json
"patterns": {
  "class": ["^\\s*class\\s+(?P<name>\\w+)"],
  "function": ["^\\s*def\\s+(?P<name>\\w+)\\s*\\("],
  "method": ["^\\s+def\\s+(?P<name>\\w+)\\s*\\("]
}
```

**Tips:**

- Use `^\\s*` to match from line start with optional leading whitespace
- Use `^\\s+` (with `+`) to require indentation (for nested elements)
- Multiple patterns per type are supported (array of strings)
- Patterns are tested in order; first match wins

**Special capture group - `receiver`:**

For languages like Go where methods have receivers, you can capture the receiver type:

```json
"method": ["^\\s*func\\s+\\(\\w+\\s+\\*?(?P<receiver>\\w+)\\)\\s+(?P<name>\\w+)"]
```

This pattern matches `func (s *Server) Start()` and extracts:

- `receiver` = "Server"
- `name` = "Start"

#### `call_pattern`

Regex pattern to detect function/method calls. Group 1 (or named group `callee`) captures the called function name.

```json
"call_pattern": "\\b(\\w+)\\s*\\("
```

This matches `functionName(` and captures `functionName`.

#### `keywords`

Language keywords to **exclude** from call detection. Without this, control structures like `if(condition)` would be detected as function calls.

```json
"keywords": ["if", "else", "for", "while", "return", "class", "def"]
```

---

## Quality of Grammar Inputs

> ⚠️ **The quality of analysis results directly depends on the quality of your grammar configuration.**

The generator produces a **generic parser** that relies entirely on regex patterns. Unlike dedicated language parsers with full AST support, this approach has inherent limitations. Understanding these limitations helps you write better configurations.

### The Importance of Well-Designed Patterns

#### Object Detection Patterns

Your `patterns` configuration determines what the analyzer can "see" in source code. Poor patterns lead to:

| Problem | Consequence |
|---------|-------------|
| Too broad patterns | False positives (detecting non-objects) |
| Too narrow patterns | Missed objects (low detection rate) |
| Missing capture groups | Objects created without names |
| Incorrect anchoring | Duplicate or misplaced objects |

**Best Practices:**

1. **Always anchor patterns** with `^` when matching line starts
2. **Use named capture groups** `(?P<name>...)` for clarity
3. **Test patterns extensively** on real code samples before deployment
4. **Order patterns from most specific to least specific**

```json
// Good: Specific, anchored, with named group
"function": ["^\\s*function\\s+(?P<name>\\w+)\\s*\\("]

// Bad: Too broad, will match comments and strings
"function": ["function (\\w+)"]
```

#### Call Pattern Quality

The `call_pattern` is critical for link detection. A poorly designed call pattern will either:
- Miss real function calls → Low link count
- Match non-calls (keywords, comments) → False positive links

**Recommended patterns by language family:**

```json
// C-style languages (function())
"call_pattern": "\\b([a-zA-Z_]\\w*)\\s*\\("

// Method chains (obj.method())
"call_pattern": "(?:\\.|:)([a-zA-Z_]\\w*)\\s*\\(|\\b([a-zA-Z_]\\w*)\\s*\\("

// Lua (obj:method() and obj.method())
"call_pattern": "(?:\\.|:)([a-zA-Z_]\\w*)\\s*\\(|\\b([a-zA-Z_]\\w*)\\s*\\("
```

#### Keywords: The Safety Net

The `keywords` list prevents false positive calls. **Missing keywords = garbage links.**

```json
// Incomplete: "if(" will be detected as a call to "if"
"keywords": ["return", "class"]

// Complete: All control structures excluded
"keywords": ["if", "else", "for", "while", "return", "class", "def",
             "function", "end", "do", "then", "local", "not", "and", "or"]
```

### Block Delimiter Selection

Choosing the wrong `block_delimiters` causes the parser to incorrectly determine function boundaries, leading to:
- Calls attributed to wrong callers
- Objects with wrong parent relationships
- Incorrect line number ranges

| Language | Correct Setting | Wrong Setting Effect |
|----------|-----------------|---------------------|
| Lua | `end_keyword` | With `braces`: functions never "end", calls misattributed |
| Go | `braces` | With `end_keyword`: parser looks for nonexistent "end" |
| Python | `indentation` | With `braces`: all code appears as top-level |
| COBOL | `sequential` | With others: paragraphs not detected properly |

### Testing Your Configuration

Before deploying, always:

1. **Create test files** with representative code samples
2. **Run the analyzer** and check the summary output
3. **Verify object counts** match your expectations
4. **Check link detection** - are real calls detected?
5. **Look for false positives** - are non-calls being linked?

```bash
# Generate extension
python generate_extension.py config_mylang.json test_output

# Run tests to see the analysis summary
python -m unittest tests.test_mylang.TestMyLangAnalyzerLevel.test_analyzer_level
```

The analysis summary will show you exactly what was detected:
- Objects by file
- Intra-file calls (within same file)
- Inter-file calls (across files)

---

## How It Works

### 2-Pass Analysis Architecture

CAST analyzers use a 2-pass architecture for robust parsing:

#### Pass 1: Light Parsing (`start_file`)

For each source file:

1. Read the file content
2. Build a coarse AST (Abstract Syntax Tree) using regex patterns
3. Create CAST objects for detected structures (classes, functions, etc.)
4. Store the module in a library for Pass 2

**What gets created:** Objects with names, types, and source locations.

#### Pass 2: Full Parsing (`end_analysis`)

After all files are processed:

1. Re-scan each module for function/method calls
2. Resolve calls to their target objects using the symbol table
3. Create links between caller and callee objects
4. Clean up memory

**What gets created:** Links (call relationships) between objects.

### Symbol Resolution

When a call like `helper()` is detected:

1. **Exact match**: Look for `helper` in the global symbol table
2. **Same-file match**: Prefer symbols from the same source file
3. **Short name match**: Look up by the function name alone

This allows resolution across files without requiring import analysis.

---

## Link Detection

### What CAN Be Detected

The generic parser can reliably detect:

| Call Type | Example | Detection |
|-----------|---------|-----------|
| Direct function calls | `processData()` | ✓ Supported |
| Qualified calls | `utils.processData()` | ✓ Last segment |
| Method calls | `obj.save()` | ✓ Last segment |
| Constructor calls | `new MyClass()` | ✓ Supported |

### What CANNOT Be Detected

Due to the limitations of regex-based parsing without full semantic analysis:

| Call Type | Example | Why It Fails |
|-----------|---------|--------------|
| Variable method calls | `x.method()` | Unknown variable type |
| Dynamic calls | `send(:method)` | Name resolved at runtime |
| Polymorphic calls | `animal.speak()` | Type ambiguity (Dog/Cat…) |
| Callback/closure calls | `callback()` | No reference tracking |
| Import-based resolution | `from x import y` | Needs full import analysis |

### Improving Link Detection

For better detection, you can extend the generated code (see next section).

---

## Extending Generated Extensions

The generated extensions are designed to be **extensible**. Here are the key extension points:

### 1. Custom Call Extraction

Override `_extract_calls()` in the module class:

```python
class MyLangModule(MyLangModule):
    def _extract_calls(self):
        # Call parent implementation
        super()._extract_calls()
        # Add custom call detection
        for i, line in enumerate(self.source_content.splitlines(), 1):
            # Detect special call patterns
            match = re.search(r'invoke\s*\(\s*["\'](\w+)["\']', line)
            if match:
                self.pending_links.append({
                    'caller': self._get_context_for_line(i),
                    'callee': match.group(1),
                    'type': 'dynamic_call',
                    'line': i
                })
```

### 2. Parser Registry

Register custom handlers for specific AST node types:

```python
from mylang_module import register_custom_handler

def handle_special_block(node, module):
    """Custom handler for special block types."""
    # Process the node
    # Create additional objects or links
    pass

register_custom_handler('special_block', handle_special_block)
```

### 3. Custom Symbol Resolution

Override `resolve_symbol()` in the Library class for smarter resolution:

```python
class MyLangLibrary(MyLangLibrary):
    def resolve_symbol(self, name, context_module=None):
        # Try standard resolution first
        result = super().resolve_symbol(name, context_module)
        if result:
            return result
        # Custom resolution logic
        # e.g., check import statements, type annotations, etc.
        return self._resolve_from_imports(name, context_module)
```

### 4. Application-Level Cross-Technology Links

Use the application level extension for cross-technology analysis:

```python
class MyLangApplicationExtension(ApplicationLevelExtension):
    def end_application(self, application):
        # Find all MyLang functions
        functions = application.search_objects(category='MyLangFunction')
        # Find database tables from SQL analyzer
        tables = application.search_objects(category='Table')
        # Create cross-technology links based on naming conventions
        for func in functions:
            for table in tables:
                if table.get_name().lower() in func.get_name().lower():
                    create_link('useLink', func, table)
```

---

## Extending the MetaModel

The generator creates a basic MetaModel with types and categories for your objects. For advanced use cases, you may want to extend the generated MetaModel XML files to add custom **categories**, **properties**, or **link types**.

### When to Extend the MetaModel

Consider extending when you need:

- **Custom properties** on objects (e.g., complexity metrics, security flags)
- **New link types** beyond `callLink` (e.g., `useLink`, `readLink`, `inheritLink`)
- **APM categories** for dashboard integration
- **Quality rule categories** for CAST rules

### MetaModel Files Location

After generation, you'll find these XML files in `configuration/`:

```
configuration/
├── Languages/
│   └── mylang/
│       └── MyLangLanguagePattern.xml    # Language patterns
└── SDK/
    └── MyLangMetaModel.xml              # Types, categories, properties
```

### Adding Custom Categories

Categories are inherited attributes that group objects. Add them in `MyLangMetaModel.xml`:

```xml
<!-- Add after existing categories -->

<!-- Category for objects that access databases -->
<category name="CAST_MyLang_DatabaseAccessor" id="YOUR_UNIQUE_ID">
    <description>Objects that access database resources</description>
    <property name="accessedTables" type="stringList" id="YOUR_PROP_ID">
        <description>List of database tables accessed</description>
    </property>
</category>

<!-- Category for security-sensitive objects -->
<category name="CAST_MyLang_SecuritySensitive" id="YOUR_UNIQUE_ID_2">
    <description>Objects handling sensitive data</description>
    <property name="securityLevel" type="integer" id="YOUR_PROP_ID_2">
        <description>Security level (1=low, 2=medium, 3=high)</description>
    </property>
</category>
```

Then inherit the category in your object types:

```xml
<type name="CAST_MyLang_Function" id="...">
    <!-- ... existing attributes ... -->
    <inheritedCategory name="CAST_MyLang_DatabaseAccessor"/>
    <inheritedCategory name="CAST_MyLang_SecuritySensitive"/>
</type>
```

### Adding Custom Properties

Properties store data on objects. Define them within categories:

```xml
<category name="CAST_MyLang_Metrics" id="YOUR_UNIQUE_ID">
    <description>Custom metrics for MyLang objects</description>
    
    <!-- Integer property -->
    <property name="cyclomaticComplexity" type="integer" id="YOUR_PROP_ID">
        <description>Cyclomatic complexity of the function</description>
    </property>
    
    <!-- String property -->
    <property name="author" type="string" id="YOUR_PROP_ID_2">
        <description>Author from code comments</description>
    </property>
    
    <!-- String list property -->
    <property name="annotations" type="stringList" id="YOUR_PROP_ID_3">
        <description>List of annotations on this object</description>
    </property>
    
    <!-- Reference to another object -->
    <property name="overrides" type="reference" id="YOUR_PROP_ID_4">
        <description>Reference to overridden method</description>
    </property>
</category>
```

### Adding Custom Link Types

Beyond `callLink`, you can create custom link types for specific relationships:

```xml
<!-- In your MetaModel XML -->
<link name="CAST_MyLang_InheritLink" id="YOUR_LINK_ID">
    <description>Inheritance relationship</description>
    <!-- Link properties if needed -->
</link>

<link name="CAST_MyLang_UseLink" id="YOUR_LINK_ID_2">
    <description>Usage relationship (reads/writes)</description>
    <property name="accessType" type="string" id="YOUR_PROP_ID">
        <description>read, write, or readwrite</description>
    </property>
</link>
```

Then use them in your code:

```python
from cast.analysers import create_link

# In your module or application level code
create_link('CAST_MyLang_InheritLink', child_class, parent_class)
create_link('CAST_MyLang_UseLink', function, variable)
```

### Setting Properties in Code

After defining properties, set them in your Python code:

```python
# In your module class
def _create_object(self, name, obj_type, line, end_line):
    obj = super()._create_object(name, obj_type, line, end_line)
    
    # Set custom properties
    obj.set_property('cyclomaticComplexity', self._calculate_complexity())
    obj.set_property('author', self._extract_author_comment())
    obj.set_property('annotations', self._get_annotations())
    
    return obj
```

### ID Management

Every category, property, type, and link needs a **unique ID**. Use the same range as your `file_no`:

```
Your reserved range: 2,193,000 - 2,193,999

Suggested allocation:
- Types:      2,193,000 - 2,193,099
- Categories: 2,193,100 - 2,193,499
- Properties: 2,193,500 - 2,193,799
- Links:      2,193,800 - 2,193,899
```

### Integrating with CAST Dashboards (APM)

To make your objects appear in CAST dashboards, inherit APM categories:

```xml
<type name="CAST_MyLang_Function" id="...">
    <!-- For transaction tracking -->
    <inheritedCategory name="APM Methods"/>
    <inheritedCategory name="APM Client Language Artifacts"/>
    
    <!-- For inventory views -->
    <inheritedCategory name="APM Inventory Methods"/>
</type>

<type name="CAST_MyLang_Class" id="...">
    <inheritedCategory name="APM Sources"/>
    <inheritedCategory name="APM Classes"/>
</type>
```

### Validation

After modifying the MetaModel, validate it:

1. Open **UA Package Assistant**:
   ```
   C:\ProgramData\Microsoft\Windows\Start Menu\Programs\CAST 8.x\UAPackageAssistant.exe
   ```

2. Browse to your extension folder

3. Check **"Validate package MetaModel file only"**

4. Click **Validate** and check for errors

---

## Custom Parsing Override

When the generic regex-based parser doesn't meet your needs, you can override specific parsing methods. This is useful when:

- **Regex limitations** prevent accurate detection
- **Language-specific constructs** require custom handling
- **Configuration quality** issues cause false positives/negatives
- **Performance optimization** is needed for large codebases

### Architecture Overview

The generated module class has these key methods you can override:

```
┌─────────────────────────────────────────────────────────────┐
│                    Module Class                             │
├─────────────────────────────────────────────────────────────┤
│  OBJECT CREATION                                            │
│  ├─ _extract_object()      → Creates objects from patterns │
│  ├─ _register_object()     → Registers object in table     │
│  └─ _find_block_end()      → Determines object boundaries  │
├─────────────────────────────────────────────────────────────┤
│  CALL DETECTION                                             │
│  ├─ _extract_calls()       → Finds function calls          │
│  ├─ _build_line_context_map() → Maps lines to callers      │
│  └─ _get_keywords()        → Returns keywords to exclude   │
├─────────────────────────────────────────────────────────────┤
│  LINK RESOLUTION                                            │
│  ├─ resolve()              → Resolves pending calls        │
│  └─ save_links()           → Creates CAST links            │
└─────────────────────────────────────────────────────────────┘
```

### Override Examples

#### Example 1: Custom Object Extraction

When regex patterns can't capture complex language constructs:

```python
# In mylang_module.py (generated file, create a subclass)

import re
from mylang_module import MyLangModule as BaseModule

class MyLangModuleExtended(BaseModule):
    """Extended module with custom object extraction."""
    def _extract_object(self, source, pattern_name, pattern_regex, line_offset=0):
        """Override to handle special constructs."""
        # Handle anonymous functions specially
        if pattern_name == 'anonymous_function':
            return self._extract_anonymous_functions(source, line_offset)
        # Handle multi-line declarations
        if pattern_name == 'class':
            return self._extract_multiline_class(source, line_offset)
        # Fall back to default regex-based extraction
        return super()._extract_object(source, pattern_name, pattern_regex, line_offset)

    def _extract_anonymous_functions(self, source, line_offset):
        """Custom extraction for anonymous functions."""
        objects = []
        # Custom parsing logic here
        lines = source.splitlines()
        for i, line in enumerate(lines, 1):
            if 'lambda' in line or '=>' in line:
                # Create custom object
                obj = self._create_custom_object(
                    name=f'anonymous_{i}',
                    obj_type='Function',
                    line=line_offset + i
                )
                objects.append(obj)
        return objects
```

#### Example 2: Custom Call Detection

When the `call_pattern` regex misses or incorrectly matches calls:

```python
class MyLangModuleExtended(BaseModule):
    """Extended module with custom call detection."""
    def _extract_calls(self):
        """Override to add custom call detection logic."""
        # First, run the standard extraction
        super()._extract_calls()
        # Then add custom patterns
        self._detect_dynamic_invocations()
        self._detect_decorator_calls()
        self._filter_false_positives()

    def _detect_dynamic_invocations(self):
        """Detect send/invoke style dynamic calls."""
        pattern = re.compile(r'\b(?:send|invoke|call)\s*[:\(]\s*[\'"](\w+)[\'"]')
        line_to_context = self._build_line_context_map()
        for i, line in enumerate(self.source_content.splitlines(), 1):
            for match in pattern.finditer(line):
                self.pending_links.append({
                    'caller': line_to_context.get(i, self.path),
                    'callee': match.group(1),
                    'type': 'dynamic_call',
                    'line': i
                })

    def _filter_false_positives(self):
        """Remove known false positive calls."""
        # Filter out calls that match certain patterns
        self.pending_links = [
            link for link in self.pending_links
            if not self._is_false_positive(link)
        ]

    def _is_false_positive(self, link):
        """Check if a link is a false positive."""
        callee = link['callee']
        # Example: filter out common utilities that aren't real calls
        false_positives = {'print', 'log', 'debug', 'assert'}
        return callee.lower() in false_positives
```

#### Example 3: Custom Block End Detection

When `block_delimiters` doesn't match your language:

```python
class MyLangModuleExtended(BaseModule):
    """Extended module with custom block detection."""
    def _find_block_end(self, lines, start_line, start_col=0):
        """Override for custom block detection.
        Example: Language uses 'BEGIN...END' blocks.
        """
        depth = 1
        for i in range(start_line, len(lines)):
            line = lines[i]
            # Count BEGIN keywords (increase depth)
            depth += len(re.findall(r'\bBEGIN\b', line, re.IGNORECASE))
            # Count END keywords (decrease depth)
            ends = len(re.findall(r'\bEND\b', line, re.IGNORECASE))
            depth -= ends
            if depth <= 0:
                return i + 1  # Return 1-based line number
        # If no END found, return last line
        return len(lines)
```

#### Example 4: Enhanced Symbol Resolution

When cross-file references need special handling:

```python
from mylang_module import MyLangLibrary as BaseLibrary

class MyLangLibraryExtended(BaseLibrary):
    """Extended library with import-aware resolution."""
    def __init__(self):
        super().__init__()
        self.import_map = {}  # module -> {alias: fullname}

    def resolve_symbol(self, name, context_module=None):
        """Override to check imports before global lookup."""
        # First, check if this is an imported symbol
        if context_module:
            imports = self.import_map.get(context_module.path, {})
            if name in imports:
                imported_fullname = imports[name]
                obj = self.objects.get(imported_fullname)
                if obj:
                    return (obj, imported_fullname)
        # Fall back to standard resolution
        return super().resolve_symbol(name, context_module)

    def register_import(self, module_path, alias, fullname):
        """Register an import for later resolution."""
        if module_path not in self.import_map:
            self.import_map[module_path] = {}
        self.import_map[module_path][alias] = fullname
```

### Integration Pattern

To use your custom classes, create a separate file and import it:

```python
# custom_mylang_module.py

from mylang_module import MyLangModule, MyLangLibrary
from mylang_analyser_level import MyLangAnalyserLevel

class MyLangModuleExtended(MyLangModule):
    # Your overrides here
    pass

class MyLangLibraryExtended(MyLangLibrary):
    # Your overrides here
    pass

# Monkey-patch the analyser to use extended classes
original_create_module = MyLangAnalyserLevel._create_module

def patched_create_module(self, file):
    module = MyLangModuleExtended()
    module.set_file(file)
    return module

MyLangAnalyserLevel._create_module = patched_create_module
```

### Key Data Structures

When overriding, you'll work with these structures:

```python
# self.objects - Dictionary of created objects
# Key: fullname (e.g., "file.lua.ClassName.methodName")
# Value: CAST CustomObject

# self.pending_links - List of calls to resolve
# Each entry: {'caller': str, 'callee': str, 'type': str, 'line': int}

# self.object_lines - Line ranges for objects
# Key: fullname
# Value: (start_line, end_line)

# self.ast - Parsed AST structure
# List of: {'type': str, 'name': str, 'fullname': str,
#           'start_line': int, 'end_line': int, 'children': [...]}
```

---

## Analysis Summary Output

After analysis completes, the extension outputs a formatted summary:

```
╔══════════════════════════════════════════════════════════════╗
║              Lua ANALYSIS SUMMARY                            ║
╚══════════════════════════════════════════════════════════════╝

┌─── OBJECTS CREATED (14 total) ───
│
│  utils.lua
│    └─ log (Function)
│
│  user_service.lua
│    └─ UserService:create_user (Function)
│    └─ UserService:get_user (Function)
│    └─ new (Function)
│
└─── LINKS CREATED (4 total) ───

     Intra-file calls (2):
        user_service.lua:
           create_user → new (L12)
           get_user → new (L18)

     Inter-file calls (2):
        order_service.lua::run_integrity_check → user_service.lua::get_user (L20)
        order_service.lua::create_order → models.lua::Order:new (L13)

════════════════════════════════════════════════════════════════
```

### Understanding the Summary

- **Objects**: Grouped by source file, showing type
- **Intra-file calls**: Calls within the same file
- **Inter-file calls**: Calls across different files
- **Line numbers**: `(L12)` indicates the line where the call occurs

Use this summary to validate your configuration:
- Low object count? Check your patterns
- No links? Check your `call_pattern` and `keywords`
- Wrong grouping? Check `block_delimiters`

---

## Limitations

### Regex-Based Parsing Limitations

1. **No semantic analysis**: Can't determine variable types or resolve imports
2. **No control flow analysis**: Can't trace function references through variables
3. **Limited context**: Regex patterns match line-by-line with limited lookahead
4. **No AST manipulation**: Can't transform or refactor code

### When to Build a Custom Analyzer

Consider building a dedicated analyzer (not using this generator) when you need:

- Full type inference
- Import/dependency resolution
- Control flow analysis
- Data flow analysis
- Complex language features (macros, metaprogramming)

### Practical Expectations

For most languages, expect to detect:

- **80-90%** of direct function/method calls
- **50-70%** of total call relationships (including those through variables)

The remaining calls require semantic analysis or manual extension.

---

## Examples

### Go Configuration

```json
{
  "language": "Go",
  "namespace": "uc",
  "file_no": 32,
  "version": "1.0.0",
  "extensions": ["go"],
  "comment": "//",
  "multiline_comment": { "begin": "/*", "end": "*/" },
  "objects": {
    "Program": { "parent": "file", "pattern_keys": [] },
    "Struct": { "parent": "Program", "pattern_keys": ["struct"] },
    "Function": { "parent": "Program", "pattern_keys": ["function"] },
    "Method": { "parent": "Struct", "pattern_keys": ["method"] }
  },
  "grammar": {
    "block_delimiters": "braces",
    "patterns": {
      "struct": ["^\\s*type\\s+(?P<name>\\w+)\\s+struct\\s*\\{"],
      "function": ["^\\s*func\\s+(?!\\()(?P<name>\\w+)\\s*\\("],
      "method": ["^\\s*func\\s+\\(\\w+\\s+\\*?(?P<receiver>\\w+)\\)\\s+(?P<name>\\w+)\\s*\\("]
    },
    "call_pattern": "\\b(\\w+)\\s*\\(",
    "keywords": ["if", "else", "for", "switch", "return", "func", "type", "struct"]
  }
}
```

### Ruby Configuration

```json
{
  "language": "Ruby",
  "namespace": "uc",
  "file_no": 31,
  "version": "1.0.0",
  "extensions": ["rb", "rake"],
  "comment": "#",
  "multiline_comment": { "begin": "=begin", "end": "=end" },
  "objects": {
    "Program": { "parent": "file", "pattern_keys": [] },
    "Class": { "parent": "Program", "pattern_keys": ["class"] },
    "Module": { "parent": "Program", "pattern_keys": ["module"] },
    "Method": { "parent": "Class", "pattern_keys": ["instance_method"] },
    "ClassMethod": { "parent": "Module", "pattern_keys": ["class_method"] }
  },
  "grammar": {
    "block_delimiters": "end_keyword",
    "patterns": {
      "class": ["^\\s*class\\s+(?P<name>[A-Z]\\w*)"],
      "module": ["^\\s*module\\s+(?P<name>[A-Z]\\w*)"],
      "instance_method": ["^\\s+def\\s+(?P<name>[a-z_][\\w?!]*)"],
      "class_method": ["^\\s+def\\s+self\\.(?P<name>[\\w?!]+)"]
    },
    "call_pattern": "\\b(\\w+)[?!]?\\s*[\\(]",
    "keywords": ["if", "else", "end", "class", "module", "def", "return", "yield"]
  }
}
```