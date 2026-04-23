import os
import re

path = 'ACTIVE/Insight_Engine/frontend_native/'
files = ['dashboard.html', 'ai_summary.html', 'trading.html', 'options.html', 'ledger.html', 'profile.html']

def fix_css(filename):
    f_path = path + filename
    if not os.path.exists(f_path): return
    
    with open(f_path, 'r') as f:
        content = f.read()
    
    # Correct the CSS Display rules
    # OLD: body.force-mobile .mobile-view { display: none; ... }
    # NEW: body.force-mobile .mobile-view { display: flex !important; ... }
    
    # 1. Fix mobile view display when forced
    content = re.sub(
        r'body\.force-mobile\s+\.mobile-view\s*\{\s*display:\s*none;?', 
        'body.force-mobile .mobile-view { display: flex !important;', 
        content
    )
    
    # 2. Fix desktop view display when forced (ensure it's flex)
    content = re.sub(
        r'body\.force-desktop\s+\.desktop-view\s*\{\s*display:\s*none;?', 
        'body.force-desktop .desktop-view { display: flex !important;', 
        content
    )

    # 3. Ensure the base .mobile-view is hidden by default to avoid flash
    if '.mobile-view { display: none;' not in content:
         content = content.replace('.mobile-view {', '.mobile-view { display: none;')

    with open(f_path, 'w') as f:
        f.write(content)
    print(f"✅ Fixed CSS Display in {filename}")

for f in files:
    fix_css(f)
