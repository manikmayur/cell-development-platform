#!/usr/bin/env python3
"""
Comprehensive test script for the complete material loading system
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.material_data import (
    get_available_materials, 
    get_all_materials,
    load_material_from_file,
    get_default_material_data,
    get_default_anode_data,
    get_default_binder_data,
    get_default_casing_data,
    get_default_foil_data,
    get_default_electrolyte_data,
    get_default_separator_data,
    get_default_coa_data
)

def test_complete_material_system():
    """Test the complete material loading system with all categories"""
    print("=== Complete Material System Test ===\n")
    
    # Test 1: Get all available materials across all categories
    print("1. Testing get_all_materials() - All Categories:")
    all_materials = get_all_materials()
    for category, materials in all_materials.items():
        print(f"   {category}: {materials} ({len(materials)} items)")
    print()
    
    # Test 2: Test specific materials from each category
    print("2. Testing material loading from each category:")
    test_cases = [
        ('NMC811', 'cathodes'),
        ('Graphite', 'anodes'), 
        ('PVDF', 'binders'),
        ('Aluminum_3003', 'casings'),
        ('Aluminum_Foil', 'foils'),
        ('LiPF6_EC_DMC', 'electrolytes'),
        ('PE', 'separators')
    ]
    
    for material, category in test_cases:
        data = load_material_from_file(material, category)
        if data:
            cost_info = ""
            if 'cost' in data:
                cost = data['cost']
                if 'per_kg' in cost:
                    cost_info = f" - ${cost['per_kg']}/kg"
                elif 'per_liter' in cost:
                    cost_info = f" - ${cost['per_liter']}/L"
                elif 'per_m2' in cost:
                    cost_info = f" - ${cost['per_m2']}/m²"
            print(f"   ✓ {material} ({category}): {data.get('name', 'Unknown')}{cost_info}")
        else:
            print(f"   ✗ Failed to load {material} from {category}")
    print()
    
    # Test 3: Test backward compatibility functions
    print("3. Testing backward compatibility functions:")
    compatibility_tests = [
        ('get_default_material_data', 'NMC811', get_default_material_data),
        ('get_default_anode_data', 'Graphite', get_default_anode_data),
        ('get_default_binder_data', 'PVDF', get_default_binder_data),
        ('get_default_casing_data', 'Steel_316L', get_default_casing_data),
        ('get_default_foil_data', 'Copper_Foil', get_default_foil_data),
        ('get_default_electrolyte_data', 'LiTFSI_EC_DMC', get_default_electrolyte_data),
        ('get_default_separator_data', 'PP', get_default_separator_data)
    ]
    
    for func_name, material, func in compatibility_tests:
        try:
            data = func(material)
            if data:
                print(f"   ✓ {func_name}('{material}'): {data.get('name', 'Unknown')}")
            else:
                print(f"   ✗ {func_name}('{material}') returned None")
        except Exception as e:
            print(f"   ✗ {func_name}('{material}') failed: {e}")
    print()
    
    # Test 4: Test CoA data extraction
    print("4. Testing CoA data extraction:")
    coa_data = get_default_coa_data('NMC811')
    if coa_data:
        print(f"   ✓ CoA Data for NMC811:")
        print(f"     - Capacity: {coa_data.get('capacity', 'N/A')} mAh/g")
        print(f"     - D50: {coa_data.get('D50', 'N/A')} μm")
        print(f"     - BET: {coa_data.get('BET', 'N/A')} m²/g")
    else:
        print("   ✗ CoA data extraction failed")
    print()
    
    # Test 5: Test cost data extraction across categories
    print("5. Testing cost data extraction:")
    cost_tests = [
        ('NMC811', 'cathodes', 'per_kg'),
        ('Aluminum_Foil', 'foils', 'per_m2'),
        ('LiPF6_EC_DMC', 'electrolytes', 'per_liter'),
        ('PE_PP_Trilayer', 'separators', 'per_m2')
    ]
    
    for material, category, cost_unit in cost_tests:
        data = load_material_from_file(material, category)
        if data and 'cost' in data:
            if cost_unit in data['cost']:
                cost_value = data['cost'][cost_unit]
                if isinstance(cost_value, dict):
                    # Handle multi-thickness pricing (foils)
                    print(f"   {material}: Multiple prices available - {list(cost_value.keys())}")
                else:
                    print(f"   {material}: ${cost_value}/{cost_unit.split('_')[1]}")
            else:
                print(f"   {material}: Cost data available but not {cost_unit}")
        else:
            print(f"   {material}: No cost data found")
    print()
    
    # Test 6: Count total materials
    total_materials = sum(len(materials) for materials in all_materials.values())
    print(f"6. System Summary:")
    print(f"   Total material categories: {len(all_materials)}")
    print(f"   Total materials available: {total_materials}")
    print(f"   Categories: {', '.join(all_materials.keys())}")
    print()
    
    print("=== Complete Material System Test Complete ===")

if __name__ == "__main__":
    test_complete_material_system()