# CAST Extension Generator

A tool to generate CAST Universal Analyzer extension **scaffolds** for any programming language. The generator automates object detection and creation, while link detection (both same-technology and cross-technology) requires manual, technology-specific implementation.

## Table of Contents

- [What This Generator Does](#what-this-generator-does)
- [What This Generator Does NOT Do](#what-this-generator-does-not-do)
- [Why Generic Link Detection Is Impossible](#why-generic-link-detection-is-impossible)
- [3-Level Architecture](#3-level-architecture)
- [Quick Start](#quick-start)
- [Configuration Reference](#configuration-reference)
- [Implementing Link Detection (Pass 2)](#implementing-link-detection-pass-2)
- [Implementing Cross-Technology Links (Application Level)](#implementing-cross-technology-links-application-level)
- [CAST SDK Reference](#cast-sdk-reference)
- [Using LLMs to Assist Implementation](#using-llms-to-assist-implementation)
- [Deployment](#deployment)

---

## What This Generator Does

The generator **automatically** produces:

| Component | Generated Automatically | Status |
|-----------|------------------------|--------|
| Extension structure | ✅ Yes | Complete scaffold |
| MetaModel XML | ✅ Yes | Object types and categories |
| Language patterns XML | ✅ Yes | File extensions, comments |
| Pass 1: Object detection | ✅ Yes | Fully functional |
| Pass 1: Object creation | ✅ Yes | Fully functional |
| Pass 2: Skeleton methods | ✅ Yes | Empty templates with documentation |
| Application Level: Template | ✅ Yes | Empty template with documentation |
| Test scaffolding | ✅ Yes | Ready to extend |
| NuGet packaging | ✅ Yes | Build scripts included |

**Pass 1 is fully automatic.** You define regex patterns in the config file, and the generator produces code that:
- Detects classes, functions, methods, and other structures
- Creates CAST objects with proper types and hierarchy
- Sets bookmarks for source code navigation
- Builds a global symbol table for resolution

---

## What This Generator Does NOT Do

The generator **does NOT** produce:

| Component | Generated | Reason |
|-----------|-----------|--------|
| Pass 2: Call detection | ❌ Skeleton only | Requires technology-specific parsing |
| Pass 2: Call resolution | ❌ Skeleton only | Requires semantic analysis |
| Pass 2: Link creation | ❌ Skeleton only | Depends on resolution |
| Application Level: Cross-tech links | ❌ Template only | Requires custom matching logic |
| Import analysis | ❌ Not implemented | Language-specific semantics |
| Type inference | ❌ Not implemented | Requires full parser |

**Pass 2 methods and Application Level are empty skeletons.** You must implement technology-specific logic.

---

## Why Generic Link Detection Is Impossible

### The Core Problem: Same-Technology Links

Consider this simple Python code:

```python
def process(data):
    data.add(item)  # Which add() is this?
```

Without knowing the **type** of `data`, we cannot determine which `add()` method is being called. Is it:
- `list.add()`?
- `set.add()`?
- `CustomClass.add()`?

A regex-based parser cannot answer this question. It lacks:

1. **Type information** - Variables don't carry type annotations in most languages
2. **Import resolution** - We don't know what modules are imported
3. **Control flow analysis** - The type might change at runtime
4. **Inheritance chains** - Method resolution depends on class hierarchy

### The Core Problem: Cross-Technology Links

Now consider linking between technologies:

```python
# Python code
def fetch_user_data():
    result = call_api("/api/users")  # Which Java endpoint is this?
```

```java
// Java code
@RequestMapping("/api/users")
public Users getUsers() { ... }

@RequestMapping("/api/user/{id}")
public User getUserById() { ... }
```

To create accurate cross-technology links, you need:

1. **Technology-specific knowledge** - How does Python call Java? REST? gRPC? Direct?
2. **Naming conventions** - Does your project follow specific patterns?
3. **Multiple conditions** - Name matching alone creates false positives
4. **Context analysis** - Parse source code for concrete evidence (URLs, table names, etc.)

### False Positives Are Worse Than Missing Links

Creating a link from `fetch_user_data()` to the wrong endpoint or database table is **worse** than creating no link at all:

- **False positives** corrupt architectural analysis
- **False positives** mislead developers about dependencies
- **False positives** cannot be easily identified and removed

The previous generic implementation attempted heuristics (same-file preference, single-candidate matching), but these still produced unacceptable false positive rates.

### The Honest Solution

Rather than pretend generic link detection works, this generator:

1. **Fully automates** what CAN be done generically (object detection)
2. **Provides skeletons** with detailed documentation for what CANNOT
3. **Empowers developers** to implement correct, technology-specific logic
4. **Separates concerns** between same-technology links (Pass 2) and cross-technology links (Application Level)

---

## 3-Level Architecture

CAST analyzers use a 3-level architecture:

```
┌─────────────────────────────────────────────────────────────────────┐
│                         PASS 1: AUTOMATIC                          │
│                     (Fully implemented by generator)                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  start_file(file)                                                   │
│  ├── Read source file                                               │
│  ├── Parse with regex patterns                                      │
│  ├── Detect: Classes, Functions, Methods, etc.                     │
│  ├── Create CAST objects with types and bookmarks                  │
│  └── Store in library for Pass 2                                    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                     PASS 2: MANUAL IMPLEMENTATION                   │
│                (Skeleton only - YOU must implement)                 │
│                  Same-technology link detection                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  end_analysis()                                                     │
│  ├── full_parse()     → Detect calls (YOUR CODE)                   │
│  ├── resolve()        → Resolve targets (YOUR CODE)                │
│  └── save_links()     → Create links (YOUR CODE)                   │
│                                                                     │
│  Available data:                                                    │
│  ├── self.objects     → All objects in this file                   │
│  ├── self.object_lines → Line ranges for each object               │
│  ├── library.symbols  → All objects across all files               │
│  └── library.symbols_by_name → Objects indexed by short name       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                 APPLICATION LEVEL: MANUAL IMPLEMENTATION            │
│                (Template only - YOU must implement)                 │
│                 Cross-technology link detection                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  end_application(application)                                       │
│  └── Create links between different technologies (YOUR CODE)       │
│                                                                     │
│  Available data:                                                    │
│  ├── application.search_objects() → Find objects by type/name      │
│  ├── application.objects()        → All objects (all technologies) │
│  ├── application.get_files()      → All analyzed files             │
│  └── open_source_file()           → Read source code               │
│                                                                     │
│  Use cases:                                                         │
│  ├── Your Language → Database Tables                               │
│  ├── Your Language → Java/C# REST APIs                             │
│  ├── Your Language → Configuration files                           │
│  └── Your Language → Message Queues/Topics                         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Pass 1: What Happens Automatically

For each source file, the generator's code:

1. **Reads** the file content
2. **Matches** regex patterns from your config
3. **Creates** CAST `CustomObject` instances
4. **Sets** parent relationships based on hierarchy config
5. **Saves** bookmarks for F11 code navigation
6. **Registers** objects in a global symbol table

### Pass 2: What You Must Implement (Same-Technology Links)

After all files are processed, you must implement:

1. **Call detection** (`full_parse()`) - Find call sites in source code
2. **Call resolution** (`resolve()`) - Match calls to target objects within your technology
3. **Link creation** (`save_links()`) - Use CAST SDK to create links

The generated module file contains **detailed documentation** in each skeleton method explaining exactly what to implement.

### Application Level: What You Must Implement (Cross-Technology Links)

After **all analyzer-level extensions** (Java, SQL, your technology, etc.) have completed:

1. **Find objects** from your technology and other technologies
2. **Implement matching logic** with multiple conditions to avoid false positives
3. **Create cross-technology links** using CAST SDK

The generated `*_application_level.py` file contains an **empty template** with documentation and helper methods.

**Example scenarios:**
- Your language function → SQL Table
- Your language code → Java REST endpoint
- Your language module → Configuration file
- Your language publisher → Message Queue

---

## Quick Start

### 1. Create Configuration File

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
    "Class": { "parent": "Program", "pattern_keys": ["class"] },
    "Function": { "parent": "Program", "pattern_keys": ["function"] },
    "Method": { "parent": "Class", "pattern_keys": ["method"] }
  },
  "grammar": {
    "block_delimiters": "braces",
    "patterns": {
      "class": ["^\\s*class\\s+(?P<name>\\w+)"],
      "function": ["^\\s*func\\s+(?P<name>\\w+)\\s*\\("],
      "method": ["^\\s+func\\s+(?P<name>\\w+)\\s*\\("]
    },
  }
}
```

### 2. Get Your file_no

Before generating the extension, reserve a unique `file_no`:

1. Go to the CAST SharePoint UA Corner:
   ```
   https://castsoftware.sharepoint.com/sites/CoffeeMachine/SitePages/UA-Corner.aspx
   ```

2. Reserve a range of IDs (e.g., `2,193,000 - 2,193,999`)

3. Calculate your `file_no`:
   ```
   file_no = (start_id - 2,000,000) / 1,000
   ```

### 3. Generate the Extension

```bash
python generate_extension.py config_mylang.json outputs/
```

### 4. Run Tests (Object Detection)

```bash
cd outputs/com.castsoftware.uc.mylang
python -m pytest tests/
```

### 5. Implement Link Detection (Pass 2)

Open `mylang_module.py` and implement:
- `full_parse()` - Technology-specific call detection
- `resolve()` - Technology-specific call resolution  
- `save_links()` - Link creation using CAST SDK

### 6. Implement Cross-Technology Links (Application Level)

Open `mylang_application_level.py` and implement:
- `end_application()` - Cross-technology link creation

### 7. Deploy

```bash
.\plugin-to-nupkg.bat
# Copy .nupkg to CAST extensions folder
```

---

## Configuration Reference

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `language` | string | Language name (e.g., "Python", "Go") |
| `namespace` | string | "uc", "labs", or "product" |
| `file_no` | integer | Unique ID range (reserve at CAST UA Corner) |
| `version` | string | Semantic version (e.g., "1.0.0") |
| `extensions` | array | File extensions without dot |
| `objects` | object | Object type hierarchy |
| `grammar.patterns` | object | Regex patterns for object detection |

### Objects Configuration

```json
"objects": {
  "Program": { "parent": "file", "pattern_keys": [] },
  "Class": { "parent": "Program", "pattern_keys": ["class"] },
  "Method": { "parent": "Class", "pattern_keys": ["method"] }
}
```

- **`parent`**: Where this object type lives in hierarchy
  - `"file"` = Top-level container (Program)
  - Object type name = Nested inside that type
  
- **`pattern_keys`**: Which patterns detect this type
  - Empty `[]` for auto-created objects (Program)
  - References pattern names from `grammar.patterns`

### Grammar Patterns

```json
"grammar": {
  "block_delimiters": "braces",
  "patterns": {
    "class": ["^\\s*class\\s+(?P<name>\\w+)"],
    "function": ["^\\s*func\\s+(?P<name>\\w+)"]
  },
  "keywords": ["if", "else", "for", "while"]
}
```

- **`block_delimiters`**: How code blocks end
  - `"braces"` - `{...}` (Go, Java, C)
  - `"end_keyword"` - `end` keyword (Ruby, Lua)
  - `"indentation"` - Whitespace (Python)
  - `"sequential"` - Block ends when the next one starts (COBOL, Assembly, REXX)

- **`patterns`**: Regex with `(?P<name>...)` capture group

- **`keywords`**: Reserved words — optional, not injected into generated code. Can be included in the config as documentation for the developer implementing Pass 2.

---

## Implementing Link Detection (Pass 2)

### Step 1: Understand the Data Structures

After Pass 1 completes, you have access to:

```python
# In the module class:
self.objects           # {fullname: CustomObject} - All objects in this file
self.object_lines      # {fullname: (start, end)} - Line ranges
self.source_content    # Raw source code string
self.path              # File path

# In the library (passed to resolve()):
library.symbols        # {fullname: CustomObject} - ALL objects across ALL files
library.symbols_by_name # {short_name: [fullnames]} - For resolution
```

### Step 2: Implement full_parse()

Detect calls in the source code:

```python
def full_parse(self):
    if not self.source_content:
        return
    
    lines = self.source_content.splitlines()
    for line_num, line in enumerate(lines, 1):
        # Your technology-specific call detection
        # Example: Match "functionName(" pattern
        for match in re.finditer(r'\b(\w+)\s*\(', line):
            callee_name = match.group(1)
            
            # Skip language keywords
            if callee_name in self._get_keywords():
                continue
            
            # Find caller (which function contains this line)
            caller = self._find_caller_for_line(line_num)
            
            # Store for resolution
            self.pending_links.append({
                'caller': caller,
                'callee': callee_name,
                'line': line_num
            })
```

### Step 3: Implement resolve()

Match callee names to actual objects:

```python
def resolve(self, library):
    for link_info in self.pending_links:
        callee_name = link_info['callee']
        
        # Strategy 1: Same-file resolution (highest confidence)
        for fullname, obj in self.objects.items():
            if fullname.endswith('.' + callee_name):
                link_info['resolved_callee'] = obj
                link_info['resolved_callee_fullname'] = fullname
                break
        
        # Strategy 2: Cross-file resolution (only if unambiguous)
        if 'resolved_callee' not in link_info:
            candidates = library.symbols_by_name.get(callee_name, [])
            if len(candidates) == 1:
                fullname = candidates[0]
                link_info['resolved_callee'] = library.symbols[fullname]
                link_info['resolved_callee_fullname'] = fullname
```

### Step 4: Implement save_links()

Create links using the CAST SDK:

```python
def save_links(self):
    from cast.analysers import create_link, Bookmark
    
    links_created = 0
    for link_info in self.pending_links:
        if 'resolved_callee' not in link_info:
            continue
        
        caller_obj = self.objects.get(link_info['caller'])
        callee_obj = link_info['resolved_callee']
        line = link_info.get('line', 0)
        
        if caller_obj and callee_obj:
            # Create bookmark for navigation
            bookmark = Bookmark(self.file, line, 1, line, -1)
            
            # Create the link
            create_link('callLink', caller_obj, callee_obj, bookmark)
            links_created += 1
    
    return links_created
```

---

## Implementing Cross-Technology Links (Application Level)

### When to Use Application Level

Use Application Level when you need to link your technology's objects to objects from **other technologies**:

| Scenario | Example |
|----------|---------|
| **Database access** | Your language → SQL Table |
| **API calls** | Your language → Java/C# REST endpoint |
| **Message queues** | Your language → Queue/Topic |
| **Configuration** | Your language → XML/JSON config |
| **External services** | Your language → Web service |

### Step 1: Implement end_application()

Open the generated `*_application_level.py` file and implement the matching logic:

```python
def end_application(self, application):
    """
    Create cross-technology links after all analyzers complete.
    """
    from cast.application import create_link
    
    # Find your technology's objects
    my_functions = list(
        application.search_objects(category='MyLangFunction')
    )
    
    # Find objects from other technologies
    db_tables = list(application.search_objects(category='Table'))
    java_methods = list(application.search_objects(category='JV_Method'))
    
    # Implement matching logic with MULTIPLE conditions
    links_created = 0
    
    for func in my_functions:
        func_name = func.get_name().lower()
        
        # Example: Link to database tables
        for table in db_tables:
            table_name = table.get_name().lower()
            
            # Use multiple conditions to avoid false positives!
            if (table_name in func_name and 
                len(table_name) > 3 and  # Avoid short names
                func_name.startswith(('get_', 'query_', 'fetch_'))):
                
                create_link('useLink', func, table)
                links_created += 1
    
    if links_created > 0:
        print(f"[MyLang] Created {links_created} cross-technology links")
```

### Step 2: Best Practices

#### ✅ DO:

1. **Use multiple matching conditions**
   ```python
   if (name_matches and pattern_matches and context_matches):
       create_link(...)
   ```

2. **Validate name length**
   ```python
   if table_name in func_name and len(table_name) > 3:
       # Avoids matching "id", "db", etc.
   ```

3. **Parse source code for evidence**
   ```python
   from cast.application import open_source_file
   source = open_source_file(func.get_file()).read()
   if 'SELECT * FROM ' + table_name in source:
       create_link('useLink', func, table)
   ```

#### ❌ DON'T:

1. **Don't match on short names alone**
2. **Don't create links without evidence**
3. **Don't forget error handling**

### Available APIs

```python
# Search for objects
objects = application.search_objects(category='ObjectType')
objects = application.search_objects(name='MyObject')

# Iterate all objects
for obj in application.objects():
    print(obj.get_name(), obj.get_type())

# Read source files
from cast.application import open_source_file
source = open_source_file(file_path)
content = source.read()

# Create links
from cast.application import create_link
create_link('callLink', source_obj, target_obj)
```

**Complete API Documentation:**
📖 [Application Level API Reference](https://cast-projects.github.io/Extension-SDK/doc/code_reference.html#application-level)

---

## CAST SDK Reference

### create_link()

Creates a relationship between two objects in the CAST knowledge base.

```python
from cast.analysers import create_link, Bookmark

# Basic usage
create_link('callLink', caller_obj, callee_obj)

# With source location (enables F11 navigation)
bookmark = Bookmark(file, line, col, end_line, end_col)
create_link('callLink', caller_obj, callee_obj, bookmark)
```

**Parameters:**
- `link_type` (str): Predefined link type (see below)
- `caller` (CustomObject): Source object
- `callee` (CustomObject): Target object
- `bookmark` (Bookmark, optional): Source location

### Predefined Link Types

**IMPORTANT:** You cannot invent new link types. Only these predefined types are available:

| Link Type | Meaning | Use Case |
|-----------|---------|----------|
| `callLink` | Function/method invocation | foo() calls bar() |
| `useLink` | Read/write access | Function uses variable |
| `relyonLink` | Dependency | Module depends on library |
| `inheritLink` | Inheritance | Class extends parent |
| `referLink` | Reference | Code mentions constant |

Custom link types can be defined in MetaModel XML, but this requires advanced knowledge of the CAST metamodel.

### Bookmark

Enables F11 navigation to source code.

```python
from cast.analysers import Bookmark

# Bookmark(file, start_line, start_col, end_line, end_col)
bookmark = Bookmark(self.file, 42, 1, 42, -1)
# -1 for end_col means "end of line"
```

### CustomObject

Objects are created in Pass 1, but here's the reference:

```python
from cast.analysers import CustomObject

obj = CustomObject()
obj.set_type('MyLangFunction')     # Object type from MetaModel
obj.set_name('myFunction')          # Short name
obj.set_fullname('path/file.ml.myFunction')  # Unique identifier
obj.set_parent(parent_obj)          # Parent in hierarchy
obj.set_guid(unique_string)         # Deterministic GUID
obj.save()                          # Persist to knowledge base
obj.save_position(bookmark)         # Set source location
```

---

## Using LLMs to Assist Implementation

Large Language Models can significantly accelerate both Pass 2 and Application Level implementation:

### For Pass 2 (Same-Technology Links)

#### 1. Understanding the Language

Ask an LLM to explain the calling conventions of your target language:

> "Explain all the ways functions can be called in Lua, including method calls, 
> metamethod invocations, and dynamic calls. Provide regex patterns that would 
> match each calling style."

#### 2. Generating Detection Patterns

> "Write a Python regex pattern that matches Go method calls of the form 
> `receiver.Method()` where the receiver can be a variable, pointer dereference, 
> or type assertion."

#### 3. Resolution Strategies

> "In Ruby, how would you resolve a method call `obj.process()` to its 
> definition, considering: method_missing, included modules, class reopening, 
> and refinements? Which cases can be resolved statically?"

### For Application Level (Cross-Technology Links)

#### 1. Understanding Cross-Technology Patterns

> "In a typical Java + Python microservices architecture, what are the common 
> patterns for Python code calling Java REST endpoints? How would you detect 
> these calls in Python source code?"

#### 2. Database Access Patterns

> "What are the common naming conventions for functions that access database 
> tables in Python? Generate matching logic that links Python functions to SQL 
> tables based on these conventions."

#### 3. Configuration Matching

> "How would you match Python code that reads configuration files to actual 
> XML/JSON configuration objects? What evidence in the source code would 
> indicate a dependency?"

### Workflow

1. Generate extension scaffold with this tool
2. Use an LLM to understand the target language's semantics
3. Implement `full_parse()` with LLM assistance (Pass 2)
4. Test on real code, iterate with LLM help
5. Implement `resolve()` for unambiguous cases (Pass 2)
6. Implement `end_application()` for cross-technology links (Application Level)
7. Deploy and validate

---

## Deployment

### 1. Build NuGet Package

```bash
cd outputs/com.castsoftware.uc.mylang
.\plugin-to-nupkg.bat
```

### 2. Deploy to CAST

Copy the `.nupkg` file to:
```
C:\Cast\ProgramData\CAST\AIP-Console-Standalone\data\shared\extensions\
```

### 3. Create Analysis Unit

Since the extension doesn't include a DMT discoverer:

1. Run **Fast Scan** on your application
2. Start **Deep Analysis**
3. Go to **Config tab** → **Universal Technology**
4. Click **+ADD** to create Analysis Unit
5. Fill in: Name, Package (`main_sources`), Language
6. Save and continue

### 4. Validate MetaModel (Optional)

Use the UA Package Assistant to validate:

1. Open: `C:\ProgramData\Microsoft\Windows\Start Menu\Programs\CAST 8.x\UAPackageAssistant.exe`
2. Browse to extension folder
3. Check "Validate package MetaModel file only"
4. Click "Validate"

---

## Examples

### Minimal Configuration (Objects Only)

```json
{
  "language": "Simple",
  "namespace": "uc",
  "file_no": 99,
  "version": "1.0.0",
  "author": "Developer",
  "extensions": ["sim"],
  "tags": "Simple Extension",
  "comment": "#",
  "objects": {
    "Program": { "parent": "file", "pattern_keys": [] },
    "Function": { "parent": "Program", "pattern_keys": ["function"] }
  },
  "grammar": {
    "block_delimiters": "braces",
    "patterns": {
      "function": ["^\\s*fn\\s+(?P<name>\\w+)"]
    }
  }
}
```

### Go Configuration

```json
{
  "language": "Go",
  "namespace": "uc",
  "file_no": 32,
  "version": "1.0.0",
  "author": "CAST",
  "extensions": ["go"],
  "tags": "Go Extension",
  "comment": "//",
  "multiline_comment": { "begin": "/*", "end": "*/" },
  "objects": {
    "Program": { "parent": "file", "pattern_keys": [] },
    "Struct": { "parent": "Program", "pattern_keys": ["struct"] },
    "Interface": { "parent": "Program", "pattern_keys": ["interface"] },
    "Function": { "parent": "Program", "pattern_keys": ["function"] },
    "Method": { "parent": "Struct", "pattern_keys": ["method"] }
  },
  "grammar": {
    "block_delimiters": "braces",
    "patterns": {
      "struct": ["^\\s*type\\s+(?P<name>\\w+)\\s+struct\\s*\\{"],
      "interface": ["^\\s*type\\s+(?P<name>\\w+)\\s+interface\\s*\\{"],
      "function": ["^\\s*func\\s+(?!\\()(?P<name>\\w+)\\s*\\("],
      "method": ["^\\s*func\\s+\\(\\w+\\s+\\*?(?P<receiver>\\w+)\\)\\s+(?P<name>\\w+)\\s*\\("]
    },
  }
}
```

---

## License

LGPL - See COPYING.LESSER.txt