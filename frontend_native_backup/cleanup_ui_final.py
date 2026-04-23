import os
import re

path = 'ACTIVE/Insight_Engine/frontend_native/'
pages = {
    'dashboard.html': 'HOME',
    'ai_summary.html': 'AI',
    'trading.html': 'TRADE',
    'options.html': 'CHAIN',
    'ledger.html': 'HISTORY',
    'profile.html': 'ME'
}

nav_template = """        <nav class="mobile-nav">
            <button onclick="location.href='dashboard.html'" class="nav-item-m [[HOME_ACT]]"><i class="fas fa-home text-lg"></i><span>HOME</span></button>
            <button onclick="location.href='ai_summary.html'" class="nav-item-m [[AI_ACT]]"><i class="fas fa-bolt text-lg"></i><span>AI</span></button>
            <button onclick="location.href='trading.html'" class="nav-item-m [[TRADE_ACT]]"><i class="fas fa-crosshairs text-lg"></i><span>TRADE</span></button>
            <button onclick="location.href='options.html'" class="nav-item-m [[CHAIN_ACT]]"><i class="fas fa-list text-lg"></i><span>CHAIN</span></button>
            <button onclick="location.href='ledger.html'" class="nav-item-m [[HISTORY_ACT]]"><i class="fas fa-history text-lg"></i><span>HISTORY</span></button>
            <button onclick="location.href='profile.html'" class="nav-item-m [[ME_ACT]]"><i class="fas fa-user text-lg"></i><span>ME</span></button>
        </nav>"""

def fix_page(filename, key):
    f_path = path + filename
    with open(f_path, 'r') as f:
        content = f.read()
    
    # 1. Strip ALL existing mobile-nav blocks
    content = re.sub(r'<nav class="mobile-nav">[\s\S]*?</nav>', '', content)
    
    # 2. Fix the layout - Ensure nav is just before the end of the mobile-view div
    current_nav = nav_template
    for k in ['HOME', 'AI', 'TRADE', 'CHAIN', 'HISTORY', 'ME']:
        current_nav = current_nav.replace(f'[[{k}_ACT]]', 'active' if k == key else '')
    
    # Find the mobile-view div and its closing tag
    if '<div class="mobile-view">' in content:
        # Split at mobile-view
        parts = content.split('<div class="mobile-view">', 1)
        # In the second part, find the main container end
        # This is tricky, so let's find the </main> tag and put it after that
        if '</main>' in parts[1]:
            main_parts = parts[1].split('</main>', 1)
            # Reconstruct: part0 + mobile-view + main + </main> + nav + part2
            new_content = parts[0] + '<div class="mobile-view">' + main_parts[0] + '</main>\n' + current_nav + main_parts[1]
            content = new_content
            
    with open(f_path, 'w') as f:
        f.write(content)

for f, k in pages.items():
    fix_page(f, k)
    print(f"Fixed UI structure in {f}")

