#!/usr/bin/env python3
"""Test script to verify template compilation"""

from jinja2 import Environment, FileSystemLoader, select_autoescape
import os

def test_templates():
    """Test if templates can be compiled without errors"""
    
    template_dir = os.path.join(os.path.dirname(__file__), 'app', 'templates')
    
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(['html', 'xml'])
    )
    
    templates_to_test = [
        'admin/users.html',
        'admin/admin_create_user.html'
    ]
    
    print("Testing template compilation...")
    
    for template_name in templates_to_test:
        try:
            template = env.get_template(template_name)
            print(f"✓ {template_name} - OK")
        except Exception as e:
            print(f"✗ {template_name} - ERROR: {e}")
    
    print("\nTemplate test completed!")

if __name__ == "__main__":
    test_templates()
