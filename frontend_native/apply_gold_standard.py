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

# The "Gold Standard" Nav (6 items)
nav_template = """        <nav class="mobile-nav">
            <button onclick="location.href='dashboard.html'" class="nav-item-m [[HOME_ACT]]"><i class="fas fa-home text-lg"></i><span>HOME</span></button>
            <button onclick="location.href='ai_summary.html'" class="nav-item-m [[AI_ACT]]"><i class="fas fa-bolt text-lg"></i><span>AI</span></button>
            <button onclick="location.href='trading.html'" class="nav-item-m [[TRADE_ACT]]"><i class="fas fa-crosshairs text-lg"></i><span>TRADE</span></button>
            <button onclick="location.href='options.html'" class="nav-item-m [[CHAIN_ACT]]"><i class="fas fa-list text-lg"></i><span>CHAIN</span></button>
            <button onclick="location.href='ledger.html'" class="nav-item-m [[HISTORY_ACT]]"><i class="fas fa-history text-lg"></i><span>HISTORY</span></button>
            <button onclick="location.href='profile.html'" class="nav-item-m [[ME_ACT]]"><i class="fas fa-user text-lg"></i><span>ME</span></button>
        </nav>"""

header_template = """<header class="p-6 flex justify-between items-center glass sticky top-0 z-[1000]">
            <h2 class="text-xl font-black tracking-tighter uppercase">[[PAGE_TITLE]]</h2>
            <div class="flex gap-3">
                <button onclick="window.showProfile()" class="w-9 h-9 bg-blue-600 rounded-xl flex items-center justify-center font-black shadow-lg" id="m-user-init">U</button>
                <button onclick="window.triggerLogout()" class="w-9 h-9 bg-slate-800 rounded-xl flex items-center justify-center text-red-500 border border-slate-700"><i class="fas fa-power-off"></i></button>
            </div>
        </header>"""

for filename, active_key in files.items():
    f_path = path + filename
    if not os.path.exists(f_path): continue
    
    with open(f_path, 'r') as f:
        content = f.read()
    
    # 1. Standardize Header
    page_titles = {'HOME':'PORTFOLIO', 'AI':'AI STRATEGY', 'TRADE':'TERMINAL', 'CHAIN':'OPTIONS', 'HISTORY':'LEDGER', 'ME':'PROFILE'}
    current_header = header_template.replace('[[PAGE_TITLE]]', page_titles[active_key])
    
    # Replace anything between <div class="mobile-view"> and the next <main
    pattern_header = r'<div class="mobile-view">[\s\S]*?<main'
    content = re.sub(pattern_header, '<div class="mobile-view">\n        ' + current_header + '\n\n        <main', content)

    # 2. Standardize Nav
    current_nav = nav_template
    for k in ['HOME', 'AI', 'TRADE', 'CHAIN', 'HISTORY', 'ME']:
        current_nav = current_nav.replace(f'[[{k}_ACT]]', 'active' if k == active_key else '')
    
    # Replace existing nav block
    content = re.sub(r'<nav class="mobile-nav">[\s\S]*?</nav>', current_nav, content)
    
    # Ensure it is actually present if it wasn't replaced (some files might have broken nav tags)
    if '<nav class="mobile-nav">' not in content:
        # Inject before </body>
        content = content.replace('</body>', current_nav + '\n</body>')

    # 3. Specific fix for trading.html overlapping (Force vertical stack)
    if filename == 'trading.html':
        content = content.replace('grid-cols-2 gap-4', 'grid-cols-1 gap-4')
        content = content.replace('p-4 space-y-6', 'p-4 space-y-8')

    with open(f_path, 'w') as f:
        f.write(content)
    print(f"✅ Gold Standard Applied: {filename}")

