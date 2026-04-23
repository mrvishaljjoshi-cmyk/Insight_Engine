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

def restore(filename, key):
    f_path = path + filename
    with open(f_path, 'r') as f:
        content = f.read()
    
    # 1. Strip ALL existing navs
    content = re.sub(r'<nav class="mobile-nav">[\s\S]*?</nav>', '', content)
    
    # 2. Build new nav
    current_nav = nav_template
    for k in ['HOME', 'AI', 'TRADE', 'CHAIN', 'HISTORY', 'ME']:
        current_nav = current_nav.replace(f'[[{k}_ACT]]', 'active' if k == key else '')
    
    # 3. Find the best injection point. 
    # Usually we want it at the end of the mobile-view div.
    if '<div class="mobile-view">' in content:
        # We look for the main element closing
        if '</main>' in content:
            content = content.replace('</main>', '</main>\n' + current_nav)
        else:
            # fallback before script
            content = content.replace('<script', current_nav + '\n    <script', 1)
            
    with open(f_path, 'w') as f:
        f.write(content)
    print(f"Restored nav in {filename}")

for f, k in pages.items():
    restore(f, k)
