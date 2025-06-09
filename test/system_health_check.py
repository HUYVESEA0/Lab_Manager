#!/usr/bin/env python3
"""
Lab Manager - System Health Check
Comprehensive system check for the admin dashboard upgrade
"""

import os
import sys
import json
import time
from pathlib import Path

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_success(message):
    """Print success message"""
    print(f"✅ {message}")

def print_warning(message):
    """Print warning message"""
    print(f"⚠️  {message}")

def print_error(message):
    """Print error message"""
    print(f"❌ {message}")

def print_info(message):
    """Print info message"""
    print(f"ℹ️  {message}")

def check_file_exists(file_path, description):
    """Check if a file exists"""
    if os.path.exists(file_path):
        print_success(f"{description}: {file_path}")
        return True
    else:
        print_error(f"{description} missing: {file_path}")
        return False

def check_css_syntax(file_path):
    """Basic CSS syntax check"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Basic checks
        open_braces = content.count('{')
        close_braces = content.count('}')
        
        if open_braces != close_braces:
            print_warning(f"CSS brace mismatch in {file_path}: {open_braces} '{' vs {close_braces} '}'")
            return False
            
        # Check for common CSS issues
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if line and not line.startswith('/*') and not line.endswith('*/'):
                if line.endswith(';') and '{' in line:
                    print_warning(f"Possible CSS syntax issue in {file_path}:{i}: {line[:50]}...")
                    
        print_success(f"CSS syntax OK: {file_path}")
        return True
        
    except Exception as e:
        print_error(f"Error checking CSS file {file_path}: {e}")
        return False

def check_js_basic_syntax(file_path):
    """Basic JavaScript syntax check"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Basic checks
        open_braces = content.count('{')
        close_braces = content.count('}')
        open_parens = content.count('(')
        close_parens = content.count(')')
        open_brackets = content.count('[')
        close_brackets = content.count(']')
        
        issues = []
        if open_braces != close_braces:
            issues.append(f"Brace mismatch: {open_braces} '{' vs {close_braces} '}'")
        if open_parens != close_parens:
            issues.append(f"Parenthesis mismatch: {open_parens} '(' vs {close_parens} ')'")
        if open_brackets != close_brackets:
            issues.append(f"Bracket mismatch: {open_brackets} '[' vs {close_brackets} ']'")
            
        if issues:
            for issue in issues:
                print_warning(f"JS syntax issue in {file_path}: {issue}")
            return False
            
        print_success(f"JavaScript syntax OK: {file_path}")
        return True
        
    except Exception as e:
        print_error(f"Error checking JS file {file_path}: {e}")
        return False

def check_template_syntax(file_path):
    """Basic template syntax check"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for common template issues
        issues = []
        
        # Check for balanced Jinja2 tags
        open_blocks = content.count('{% ')
        close_blocks = content.count(' %}')
        if open_blocks != close_blocks:
            issues.append(f"Jinja2 block mismatch: {open_blocks} vs {close_blocks}")
            
        open_vars = content.count('{{ ')
        close_vars = content.count(' }}')
        if open_vars != close_vars:
            issues.append(f"Jinja2 variable mismatch: {open_vars} vs {close_vars}")
            
        # Check for common HTML issues
        if '<html>' in content and '</html>' not in content:
            issues.append("HTML tag not closed: <html>")
        if '<body>' in content and '</body>' not in content:
            issues.append("HTML tag not closed: <body>")
            
        if issues:
            for issue in issues:
                print_warning(f"Template issue in {file_path}: {issue}")
            return False
            
        print_success(f"Template syntax OK: {file_path}")
        return True
        
    except Exception as e:
        print_error(f"Error checking template file {file_path}: {e}")
        return False

def main():
    """Main system check"""
    print_header("LAB MANAGER - SYSTEM HEALTH CHECK")
    print_info("Checking admin dashboard upgrade components...")
    
    # Define file paths
    base_path = Path(__file__).parent
    
    files_to_check = {
        "CSS Files": [
            (base_path / "app/static/css/admin.css", "Admin Base CSS"),
            (base_path / "app/static/css/system_dashboard.css", "System Dashboard CSS"),
            (base_path / "app/static/css/admin_tables.css", "Admin Tables CSS"),
        ],
        "JavaScript Files": [
            (base_path / "app/static/js/system_dashboard.js", "System Dashboard JS"),
            (base_path / "app/static/js/admin_tables.js", "Admin Tables JS"),
            (base_path / "app/static/js/admin_performance_monitor.js", "Performance Monitor JS"),
        ],
        "Template Files": [
            (base_path / "app/templates/admin/system_admin_dashboard.html", "System Admin Dashboard"),
            (base_path / "app/templates/base.html", "Base Template"),
            (base_path / "app/templates/index.html", "Index Template"),
        ],
        "Python Files": [
            (base_path / "app/models.py", "Database Models"),
            (base_path / "app/routes/admin.py", "Admin Routes"),
            (base_path / "app/__init__.py", "App Initialization"),
            (base_path / "run.py", "Application Runner"),
        ],
        "Documentation": [
            (base_path / "doc/complete_admin_system_upgrade.md", "Complete Upgrade Guide"),
            (base_path / "doc/testing_deployment_checklist.md", "Testing Checklist"),
            (base_path / "README.md", "Project README"),
        ]
    }
    
    total_checks = 0
    passed_checks = 0
    
    # Check file existence
    print_header("FILE EXISTENCE CHECK")
    for category, files in files_to_check.items():
        print(f"\n🔍 {category}:")
        for file_path, description in files:
            total_checks += 1
            if check_file_exists(file_path, description):
                passed_checks += 1
    
    # Syntax checks
    print_header("SYNTAX VALIDATION")
    
    # CSS syntax checks
    print("\n🎨 CSS Files:")
    for file_path, description in files_to_check["CSS Files"]:
        if os.path.exists(file_path):
            total_checks += 1
            if check_css_syntax(file_path):
                passed_checks += 1
    
    # JavaScript syntax checks
    print("\n⚡ JavaScript Files:")
    for file_path, description in files_to_check["JavaScript Files"]:
        if os.path.exists(file_path):
            total_checks += 1
            if check_js_basic_syntax(file_path):
                passed_checks += 1
    
    # Template syntax checks
    print("\n📄 Template Files:")
    for file_path, description in files_to_check["Template Files"]:
        if os.path.exists(file_path):
            total_checks += 1
            if check_template_syntax(file_path):
                passed_checks += 1
    
    # Feature checks
    print_header("FEATURE VERIFICATION")
    
    # Check for modern CSS features
    print("\n🔧 Modern CSS Features:")
    admin_css_path = base_path / "app/static/css/admin.css"
    if os.path.exists(admin_css_path):
        with open(admin_css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
            
        features = {
            "--admin-": "CSS Custom Properties (Variables)",
            "@media": "Responsive Design Media Queries",
            "flexbox": "Flexbox Layout",
            "transform": "CSS Transforms",
            "transition": "CSS Transitions",
            "box-shadow": "Modern Box Shadows",
            "border-radius": "Rounded Corners",
        }
        
        for feature, description in features.items():
            total_checks += 1
            if feature in css_content:
                print_success(f"{description}")
                passed_checks += 1
            else:
                print_warning(f"{description} not found")
    
    # Check JavaScript features
    print("\n⚡ JavaScript Features:")
    dashboard_js_path = base_path / "app/static/js/system_dashboard.js"
    if os.path.exists(dashboard_js_path):
        with open(dashboard_js_path, 'r', encoding='utf-8') as f:
            js_content = f.read()
            
        features = {
            "class ": "ES6 Classes",
            "async ": "Async/Await",
            "addEventListener": "Event Listeners",
            "querySelector": "Modern DOM Selection",
            "fetch": "Modern HTTP Requests",
        }
        
        for feature, description in features.items():
            total_checks += 1
            if feature in js_content:
                print_success(f"{description}")
                passed_checks += 1
            else:
                print_warning(f"{description} not found")
    
    # Performance Monitor Check
    print("\n🚀 Performance Monitor:")
    perf_monitor_path = base_path / "app/static/js/admin_performance_monitor.js"
    if os.path.exists(perf_monitor_path):
        with open(perf_monitor_path, 'r', encoding='utf-8') as f:
            perf_content = f.read()
            
        features = {
            "PerformanceObserver": "Performance API Monitoring",
            "memory": "Memory Usage Tracking",
            "navigator.connection": "Network Status Monitoring",
            "largestContentfulPaint": "Core Web Vitals",
            "cumulativeLayoutShift": "Layout Stability Tracking",
        }
        
        for feature, description in features.items():
            total_checks += 1
            if feature in perf_content:
                print_success(f"{description}")
                passed_checks += 1
            else:
                print_warning(f"{description} not implemented")
    
    # Summary
    print_header("SYSTEM CHECK SUMMARY")
    
    success_rate = (passed_checks / total_checks) * 100 if total_checks > 0 else 0
    
    print(f"\n📊 Overall Results:")
    print(f"   Total Checks: {total_checks}")
    print(f"   Passed: {passed_checks}")
    print(f"   Failed: {total_checks - passed_checks}")
    print(f"   Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print_success("System is in excellent condition! 🎉")
    elif success_rate >= 75:
        print_warning("System is in good condition with minor issues 👍")
    elif success_rate >= 50:
        print_warning("System has some issues that should be addressed 🔧")
    else:
        print_error("System has significant issues requiring attention! 🚨")
    
    print("\n" + "="*60)
    print("Health check completed!")
    print("="*60)
    
    return success_rate >= 75

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
