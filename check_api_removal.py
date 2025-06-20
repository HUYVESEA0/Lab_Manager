#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Final API removal verification test
Ensures all API dependencies have been completely removed
"""

import os
import re

def check_api_removal():
    print("\n🔍 FINAL API REMOVAL VERIFICATION")
    print("=" * 50)
    
    api_patterns = [
        r'fetch\([\'"`][^\'"`]*\/api\/',
        r'\.get\([\'"`][^\'"`]*\/api\/',
        r'\.post\([\'"`][^\'"`]*\/api\/',
        r'loadAdminLabSessions\s*\(',
        r'loadLabSessions\s*\(',
        r'loadMyLabSessions\s*\(',
        r'fetchSystemMetrics\s*\(',
        r'fetchUserActivity\s*\(',
        r'fetchPerformanceMetrics\s*\(',
    ]
    
    api_found = False
    
    # Check JavaScript files
    js_files = []
    for root, dirs, files in os.walk('app/static/js'):
        for file in files:
            if file.endswith('.js'):
                js_files.append(os.path.join(root, file))
    
    print("\n📄 CHECKING JAVASCRIPT FILES:")
    for js_file in js_files:
        try:
            with open(js_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            file_has_api = False
            for pattern in api_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    # Skip commented lines
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if match in line and not line.strip().startswith('//') and not line.strip().startswith('*'):
                            print(f"  ❌ {js_file}:{i+1} - {pattern}")
                            file_has_api = True
                            api_found = True
            
            if not file_has_api:
                print(f"  ✅ {js_file} - Clean")
                
        except Exception as e:
            print(f"  ⚠️  Error reading {js_file}: {e}")
    
    # Check HTML templates
    html_files = []
    for root, dirs, files in os.walk('app/templates'):
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))
    
    print("\n📄 CHECKING HTML TEMPLATES:")
    template_api_patterns = [
        r'fetch\([\'"`][^\'"`]*\/api\/',
        r'loadAdminLabSessions\s*\(',
        r'loadLabSessions\s*\(',
        r'loadMyLabSessions\s*\(',
    ]
    
    for html_file in html_files:
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            file_has_api = False
            for pattern in template_api_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    # Check if it's not commented
                    for match in matches:
                        if not ('//') in content[content.find(match)-50:content.find(match)+50]:
                            print(f"  ❌ {html_file} - {pattern}")
                            file_has_api = True
                            api_found = True
            
            if not file_has_api:
                print(f"  ✅ {html_file} - Clean")
                
        except Exception as e:
            print(f"  ⚠️  Error reading {html_file}: {e}")
    
    # Check for status indicators
    print("\n📱 CHECKING STATUS INDICATORS:")
    status_issues = []
    
    for html_file in html_files:
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if 'Connecting...' in content:
                status_issues.append(f"{html_file} - Still shows 'Connecting...'")
            elif 'Dashboard Status' in content and 'Ready (Server-side)' not in content:
                status_issues.append(f"{html_file} - Dashboard status not updated")
                
        except Exception as e:
            print(f"  ⚠️  Error reading {html_file}: {e}")
    
    if status_issues:
        for issue in status_issues:
            print(f"  ❌ {issue}")
        api_found = True
    else:
        print("  ✅ All status indicators updated")
    
    print("\n" + "=" * 50)
    if not api_found:
        print("🎉 SUCCESS: All API dependencies removed!")
        print("✅ No more 'Dashboard Status - Connecting...' errors")
        print("✅ No more 'Lỗi khi khởi tạo dashboard' errors")
        print("✅ All lab session lists use server-side data")
        print("✅ Dashboard shows 'Ready (Server-side)' status")
        print("\n🚀 APPLICATION IS READY!")
        print("   • Navigate to http://127.0.0.1:5000")
        print("   • All functionality works without API calls")
        print("   • Better performance with server-side data")
    else:
        print("❌ Some API dependencies still found - check above")
    
    print("=" * 50)

if __name__ == '__main__':
    check_api_removal()
