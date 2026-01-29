#!/usr/bin/env python3
"""
Direct test of the problematic template code with Jinja2
"""
from jinja2 import Template

# Test the exact problematic code
test_cases = [
    ('{{ "%.4f"|format(value) if value else "N/A" }}', {'value': 2550.00}, '2550.0000'),
    ('{{ "%.4f"|format(value) if value else "N/A" }}', {'value': None}, 'N/A'),
    ('{{ "%.4f"|format(value) if value else "N/A" }}', {'value': 0}, 'N/A'),
]

print("Testing Jinja2 template filters with None values:\n")

for template_str, context, expected in test_cases:
    try:
        t = Template(template_str)
        result = t.render(**context)
        status = "✓" if result == expected else "✗"
        print(f"{status} Template: {template_str}")
        print(f"  Input: {context}")
        print(f"  Output: {result}")
        print(f"  Expected: {expected}")
        print()
    except Exception as e:
        print(f"✗ Template: {template_str}")
        print(f"  Input: {context}")
        print(f"  ERROR: {e}")
        print()

print("All template filter tests completed!")
