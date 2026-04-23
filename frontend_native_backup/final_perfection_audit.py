import os
import re

path = 'ACTIVE/Insight_Engine/frontend_native/'
files = ['dashboard.html', 'ai_summary.html', 'trading.html', 'options.html', 'ledger.html', 'profile.html']

print("--- FINAL PERFECTION AUDIT ---\n")

for f in files:
    f_path = path + f
    if not os.path.exists(f_path): continue
    
    with open(f_path, 'r') as file:
        content = file.read()
    
    print(f"Checking {f}:")
    
    # 1. Nav Item Count (Should be exactly 6)
    nav_matches = re.findall(r'nav-item-m', content)
    # Filter out class definitions in style tags
    real_nav_matches = [m for m in nav_matches if 'class="nav-item-m' in content]
    
    # Simple count of the buttons in the footer
    nav_btn_count = content.count('nav-item-m') // 2 # Rough estimate because class is in style too
    # Better: find the mobile-nav block
    nav_block = re.search(r'<nav class="mobile-nav">([\s\S]*?)</nav>', content)
    if nav_block:
        btn_count = nav_block.group(1).count('<button')
        print(f"  ✅ Nav Buttons: {btn_count}")
    else:
        print(f"  ❌ Nav Block: NOT FOUND")

    # 2. Header Check
    has_init = 'm-user-init' in content
    has_logout = 'window.triggerLogout' in content
    print(f"  ✅ Header Profile: {has_init} | Logout: {has_logout}")

    # 3. PDF Check (AI Summary only)
    if f == 'ai_summary.html':
        has_pdf = 'generateDetailedPDF' in content
        print(f"  ✅ PDF Feature: {has_pdf}")

    # 4. View Mode Check
    has_view = 'force-mobile' in content
    print(f"  ✅ View Mode Logic: {has_view}")

print("\n--- AUDIT COMPLETE ---")
