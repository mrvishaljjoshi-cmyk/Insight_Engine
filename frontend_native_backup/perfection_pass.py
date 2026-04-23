import os
import re

path = 'ACTIVE/Insight_Engine/frontend_native/'
files = {
    'dashboard.html': 'HOME',
    'ai_summary.html': 'AI',
    'trading.html': 'TRADE',
    'options.html': 'CHAIN',
    'ledger.html': 'HISTORY',
    'profile.html': 'ME'
}

# The Perfection-Level Unified Nav
nav_template = """        <nav class="mobile-nav">
            <button onclick="location.href='dashboard.html'" class="nav-item-m [[HOME_ACT]]"><i class="fas fa-home text-lg"></i><span>HOME</span></button>
            <button onclick="location.href='ai_summary.html'" class="nav-item-m [[AI_ACT]]"><i class="fas fa-bolt text-lg"></i><span>AI</span></button>
            <button onclick="location.href='trading.html'" class="nav-item-m [[TRADE_ACT]]"><i class="fas fa-crosshairs text-lg"></i><span>TRADE</span></button>
            <button onclick="location.href='options.html'" class="nav-item-m [[CHAIN_ACT]]"><i class="fas fa-list text-lg"></i><span>CHAIN</span></button>
            <button onclick="location.href='ledger.html'" class="nav-item-m [[HISTORY_ACT]]"><i class="fas fa-history text-lg"></i><span>HISTORY</span></button>
            <button onclick="location.href='profile.html'" class="nav-item-m [[ME_ACT]]"><i class="fas fa-user text-lg"></i><span>ME</span></button>
        </nav>"""

# High-End Mobile Header Cluster
header_cluster = """<div class="flex gap-3">
                <button onclick="window.showProfile()" class="w-9 h-9 bg-blue-600 rounded-xl flex items-center justify-center font-black shadow-lg" id="m-user-init">U</button>
                <button onclick="window.triggerLogout()" class="w-9 h-9 bg-slate-800 rounded-xl flex items-center justify-center text-red-500 border border-slate-700"><i class="fas fa-power-off"></i></button>
            </div>"""

for filename, active_key in files.items():
    f_path = path + filename
    if not os.path.exists(f_path): continue
    
    with open(f_path, 'r') as f:
        content = f.read()
    
    # 1. Fix Bottom Nav
    current_nav = nav_template
    for k in ['HOME', 'AI', 'TRADE', 'CHAIN', 'HISTORY', 'ME']:
        current_nav = current_nav.replace(f'[[{k}_ACT]]', 'active' if k == active_key else '')
    
    content = re.sub(r'<nav class="mobile-nav">[\s\S]*?</nav>', current_nav, content)

    # 2. Fix Mobile Header Buttons (Top Right)
    # Match the header's flex container for mobile
    pattern_header = r'<div class="flex gap-3">[\s\S]*?</button>\s*</div>'
    if re.search(pattern_header, content):
        content = re.sub(pattern_header, header_cluster, content)
    
    # 3. Specific fix for trading.html scramble
    if filename == 'trading.html':
        content = content.replace('grid-cols-2 gap-4', 'grid-cols-1 gap-4') # Stack inputs vertically
        content = content.replace('z-[1000] z-[1000]', 'z-[1000]') # Fix double z-index
        
    # 4. Clean up any broken body tags or duplicates
    content = content.replace('nav-item-m nav-item-m', 'nav-item-m')
    
    # 5. Fix z-index across all sticky headers
    content = content.replace('glass sticky top-0', 'glass sticky top-0 z-[1000]')
    content = content.replace('z-[1000] z-[1000]', 'z-[1000]') # Prevent triple z-index
    
    with open(f_path, 'w') as f:
        f.write(content)
    print(f"✨ Perfected {filename}")

