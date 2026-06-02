#!/usr/bin/env python3
"""
Test script for the Chinese Data Classifier application.
Tests the classifier and verifies basic functionality.
"""

import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from data_classifier import DataClassifier

def test_classifier():
    """Test the DataClassifier with various inputs."""
    print("=" * 60)
    print("TESTING CHINESE DATA CLASSIFIER")
    print("=" * 60)
    
    classifier = DataClassifier()
    
    # Test data: Chinese names, ID cards, and phone numbers
    test_data = [
        ("张三", "Name", "Chinese name"),
        ("李四", "Name", "Chinese name"),
        ("王五", "Name", "Chinese name"),
        ("110101199003071234", "ID Card", "Valid 18-digit ID card"),
        ("110101199003071234", "ID Card", "Valid ID card with checksum"),
        ("13812345678", "Phone", "Valid China Mobile number"),
        ("13912345678", "Phone", "Valid China Mobile number"),
        ("15512345678", "Phone", "Valid China Unicom number"),
        ("17612345678", "Phone", "Valid China Telecom number"),
        ("abc123", "Unknown", "Invalid data"),
        ("12345", "Unknown", "Invalid phone (too short)"),
        ("", "Unknown", "Empty string"),
    ]
    
    print("\n1. TESTING INDIVIDUAL VALIDATORS")
    print("-" * 60)
    
    passed = 0
    failed = 0
    
    for data, expected, description in test_data:
        if expected == "Name":
            result = classifier.is_chinese_name(data)
        elif expected == "ID Card":
            result = classifier.is_valid_id_card(data)
        elif expected == "Phone":
            result = classifier.is_valid_phone(data)
        else:
            result = False
        
        status = "✓ PASS" if result == (expected != "Unknown") else "✗ FAIL"
        if result == (expected != "Unknown"):
            passed += 1
        else:
            failed += 1
        
        print(f"{status}: {description}")
        print(f"       Input: '{data}'")
        print(f"       Expected: {expected}, Got: {result}")
        print()
    
    print(f"Results: {passed} passed, {failed} failed")
    
    # Test file processing
    print("\n2. TESTING FILE PROCESSING")
    print("-" * 60)
    
    # Create test file
    test_file = "test_input.txt"
    test_content = """张三
李四
王五
110101199003071234
13812345678
15912345678
invalid_data
"""
    
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    print(f"Created test file: {test_file}")
    
    # Read and classify
    with open(test_file, 'r', encoding='utf-8') as f:
        data_list = [line.strip() for line in f.readlines() if line.strip()]
    
    results = classifier.classify_data(data_list)
    
    # Count results
    name_count = sum(1 for r in results if r['classification'] == 'Name')
    id_count = sum(1 for r in results if r['classification'] == 'ID Card')
    phone_count = sum(1 for r in results if r['classification'] == 'Phone')
    unknown_count = sum(1 for r in results if r['classification'] == 'Unknown')
    
    print("\nClassification Results:")
    print(f"  Names: {name_count}")
    print(f"  ID Cards: {id_count}")
    print(f"  Phones: {phone_count}")
    print(f"  Unknown: {unknown_count}")
    print(f"  Total: {len(results)}")
    
    print("\nDetailed Classification:")
    for result in results:
        print(f"  {result['data']:20} -> {result['classification']}")
    
    # Test CSV export
    print("\n3. TESTING CSV EXPORT")
    print("-" * 60)
    
    csv_file = "test_results.csv"
    success = classifier.save_to_csv(results, csv_file)
    
    if success:
        print(f"✓ Successfully saved results to: {csv_file}")
        # Show file contents
        with open(csv_file, 'r', encoding='utf-8') as f:
            print("\nCSV File Contents:")
            print(f.read())
    else:
        print(f"✗ Failed to save CSV file")
    
    # Test drag-and-drop availability
    print("\n4. TESTING DRAG-AND-DROP AVAILABILITY")
    print("-" * 60)
    
    try:
        from tkinterdnd2 import DND_FILES, getdata
        print("✓ tkinterdnd2 is installed and available")
        print("  Drag-and-drop feature: ENABLED")
    except ImportError:
        print("✗ tkinterdnd2 is NOT installed")
        print("  Drag-and-drop feature: DISABLED")
        print("  Fix: Run 'pip install tkinterdnd2'")
    
    print("\n" + "=" * 60)
    print("TESTING COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_classifier()
