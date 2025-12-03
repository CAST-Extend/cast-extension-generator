#!/usr/bin/env python3
"""
Test script to verify call detection in generated extensions.
Reads configuration from test_configs/*.json and tests against test_data files.

Usage:
    python test_call_detection.py              # Test all languages
    python test_call_detection.py cobol lua    # Test specific languages
"""

import sys
import os
import re
import json
from pathlib import Path

# Directories
BASE_DIR = Path(__file__).parent
TEST_CONFIGS_DIR = BASE_DIR / 'test_configs'
TEST_DATA_DIR = BASE_DIR / 'test_output' / 'test_data'


def load_all_configs():
    """Load all language configurations from test_configs/*.json"""
    configs = {}
    
    for config_file in TEST_CONFIGS_DIR.glob('config_*.json'):
        try:
            with open(config_file, 'r', encoding='utf-8-sig') as f:
                config = json.load(f)
            
            language = config.get('language', '')
            extensions = config.get('extensions', [])
            grammar = config.get('grammar', {})
            
            call_pattern = grammar.get('call_pattern', '')
            keywords = set(k.lower() for k in grammar.get('keywords', []))
            comment = config.get('comment', '//')
            
            if language and call_pattern:
                configs[language.lower()] = {
                    'name': language,
                    'extensions': ['.' + ext.lstrip('.') for ext in extensions],
                    'call_pattern': call_pattern,
                    'keywords': keywords,
                    'comment': comment,
                    'config_file': config_file.name,
                }
        except Exception as e:
            print(f"⚠️  Error loading {config_file.name}: {e}")
    
    return configs


def get_config_for_file(filepath, configs):
    """Get the language configuration for a file based on its extension."""
    ext = Path(filepath).suffix.lower()
    
    for lang_key, config in configs.items():
        if ext in config['extensions']:
            return config
    
    return None


def extract_calls_from_file(filepath, config):
    """Extract all calls from a file using the language's call pattern."""
    call_pattern_str = config['call_pattern']
    keywords = config['keywords']
    comment_char = config['comment']
    
    # Compile pattern with appropriate flags
    try:
        if '\n' in call_pattern_str or '#' in call_pattern_str:
            call_pattern = re.compile(call_pattern_str, re.VERBOSE | re.IGNORECASE)
        else:
            call_pattern = re.compile(call_pattern_str, re.IGNORECASE)
    except re.error as e:
        print(f"  ❌ REGEX ERROR: {e}")
        return []
    
    # Read file
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"  ❌ FILE ERROR: {e}")
        return []
    
    found_calls = []
    
    for line_num, line in enumerate(lines, 1):
        stripped = line.strip()
        
        # Skip comment lines
        if stripped.startswith(comment_char):
            continue
        
        # Find all calls in the line
        for match in call_pattern.finditer(line):
            callee_name = None
            
            # Method 1: Check all named groups
            groups = match.groupdict()
            if groups:
                for group_name, value in groups.items():
                    if value is not None:
                        callee_name = value
                        break
            
            # Method 2: Fallback to numbered groups
            if not callee_name:
                for i in range(1, len(match.groups()) + 1):
                    try:
                        value = match.group(i)
                        if value is not None:
                            callee_name = value
                            break
                    except IndexError:
                        break
            
            if callee_name and callee_name.lower() not in keywords:
                found_calls.append({
                    'name': callee_name,
                    'line': line_num,
                    'context': stripped[:60] + ('...' if len(stripped) > 60 else '')
                })
    
    return found_calls


def find_test_files_for_language(config):
    """Find all test files for a given language configuration."""
    files = []
    
    if not TEST_DATA_DIR.exists():
        return files
    
    for ext in config['extensions']:
        for filepath in TEST_DATA_DIR.glob(f'*{ext}'):
            if filepath.is_file():
                files.append(filepath)
    
    return sorted(files)


def test_language(config, verbose=True):
    """Test call detection for a specific language."""
    lang_name = config['name']
    files = find_test_files_for_language(config)
    
    if not files:
        if verbose:
            print(f"\n⚠️  {lang_name}: No test files found for extensions {config['extensions']}")
        return None
    
    if verbose:
        print(f"\n{'='*70}")
        print(f"  {lang_name} - {len(files)} file(s)")
        print(f"  Config: {config['config_file']}")
        print(f"  Pattern: {config['call_pattern'][:50]}{'...' if len(config['call_pattern']) > 50 else ''}")
        print(f"{'='*70}")
    
    total_calls = 0
    all_calls = []
    
    for filepath in files:
        filename = Path(filepath).name
        calls = extract_calls_from_file(filepath, config)
        
        if verbose:
            print(f"\n  {filename}")
            
            if calls:
                for call in calls:
                    print(f"     Line {call['line']:3d}: {call['name']:<20} ← {call['context']}")
            else:
                print(f"     (no calls detected)")
        
        total_calls += len(calls)
        all_calls.extend(calls)
    
    if verbose:
        print(f"\n  Total calls detected: {total_calls}")
    
    return {
        'language': lang_name,
        'files': len(files),
        'calls': total_calls,
        'call_details': all_calls,
    }


def main():
    # Parse command line arguments
    filter_languages = [arg.lower() for arg in sys.argv[1:]] if len(sys.argv) > 1 else None
    
    print("=" * 70)
    print("  CALL DETECTION TEST")
    print("  Reading configs from: test_configs/")
    print("  Test files from: test_output/test_data/")
    print("=" * 70)
    
    # Load all configurations
    configs = load_all_configs()
    
    if not configs:
        print("❌ No valid configurations found in test_configs/")
        return 1
    
    print(f"\n📋 Found {len(configs)} language configurations:")
    for lang_key, config in sorted(configs.items()):
        print(f"   - {config['name']}: {config['config_file']}")
    
    # Filter languages if specified
    if filter_languages:
        configs = {k: v for k, v in configs.items() if k in filter_languages}
        if not configs:
            print(f"\n❌ No matching languages found for: {filter_languages}")
            print(f"   Available: {list(load_all_configs().keys())}")
            return 1
        print(f"\n🔍 Testing only: {[c['name'] for c in configs.values()]}")
    
    # Test each language
    results = {}
    for lang_key in sorted(configs.keys()):
        config = configs[lang_key]
        result = test_language(config, verbose=True)
        if result:
            results[config['name']] = result
    
    # Summary
    print(f"\n{'='*70}")
    print("  SUMMARY")
    print(f"{'='*70}")
    
    total_calls = 0
    total_files = 0
    
    for lang_name, result in sorted(results.items()):
        status = "✅" if result['calls'] > 0 else "⚠️ "
        print(f"  {status} {lang_name:<12}: {result['calls']:4d} calls in {result['files']} files")
        total_calls += result['calls']
        total_files += result['files']
    
    print(f"\n  📊 Grand total: {total_calls} calls across {total_files} files in {len(results)} languages")
    
    # Show languages without test files
    missing = set(configs.keys()) - set(r.lower() for r in results.keys())
    if missing:
        print(f"\n  ⚠️  Languages without test files: {missing}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
