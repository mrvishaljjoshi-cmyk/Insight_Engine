import os
import re

nav_template = """        <nav class="mobile-nav">
            <button onclick="location.href='dashboard.html'" class="nav-item-m [[HOME_ACT]]"><i class="fas fa-home text-lg"></i><span>HOME</span></button>
            <button onclick="location.href='ai_summary.html'" class="nav-item-m [[AI_ACT]]"><i class="fas fa-bolt text-lg"></i><span>AI</span></button>
            <button onclick="location.href='trading.html'" class="nav-item-m [[TRADE_ACT]]"><i class="fas fa-crosshairs text-lg"></i><span>TRADE</span></button>
            <button onclick="location.href='options.html'" class="nav-item-m [[CHAIN_ACT]]"><i class="fas fa-list text-lg"></i><span>CHAIN</span></button>
            <button onclick="location.href='ledger.html'" class="nav-item-m [[HISTORY_ACT]]"><i class="fas fa-history text-lg"></i><span>HISTORY</span></button>
            <button onclick="location.href='profile.html'" class="nav-item-m [[ME_ACT]]"><i class="fas fa-user text-lg"></i><span>ME</span></button>
        </nav>"""

pages = {
    'dashboard.html': 'HOME',
    'ai_summary.html': 'AI',
    'trading.html': 'TRADE',
    'options.html': 'CHAIN',
    'ledger.html': 'HISTORY',
    'profile.html': 'ME'
}

path = 'ACTIVE/Insight_Engine/frontend_native/'

for filename, active_key in pages.items():
    f_path = path + filename
    if not os.path.exists(f_path): continue
    
    with open(f_path, 'r') as f:
        content = f.read()
        
    current_nav = nav_template
    for k in ['HOME', 'AI', 'TRADE', 'CHAIN', 'HISTORY', 'ME']:
        current_nav = current_nav.replace(f'[[{k}_ACT]]', 'active' if k == active_key else '')
        
    # Standardize the mobile nav block replacement (very aggressive cleanup)
    # This finds anything that looks like a mobile nav and replaces it with the clean template
    content = re.sub(r'<nav class="mobile-nav">[\s\S]*?</nav>', current_nav, content)
    
    # Ensure it's not duplicated in other areas
    content = content.replace('nav-item-m nav-item-m', 'nav-item-m')
    
    with open(f_path, 'w') as f:
        f.write(content)
    print(f"🧹 Cleaned Nav in {filename}")

