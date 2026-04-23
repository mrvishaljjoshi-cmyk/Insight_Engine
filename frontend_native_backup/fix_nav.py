import glob
import re

nav_html = """        <nav class="mobile-nav">
            <button onclick="location.href='dashboard.html'" class="nav-item-m __HOME_ACTIVE__"><i class="fas fa-home text-lg"></i><span>HOME</span></button>
            <button onclick="location.href='ai_summary.html'" class="nav-item-m __AI_ACTIVE__"><i class="fas fa-bolt text-lg"></i><span>AI</span></button>
            <button onclick="location.href='trading.html'" class="nav-item-m __TRADE_ACTIVE__"><i class="fas fa-crosshairs text-lg"></i><span>TRADE</span></button>
            <button onclick="location.href='options.html'" class="nav-item-m __CHAIN_ACTIVE__"><i class="fas fa-list text-lg"></i><span>CHAIN</span></button>
            <button onclick="location.href='ledger.html'" class="nav-item-m __HISTORY_ACTIVE__"><i class="fas fa-history text-lg"></i><span>HISTORY</span></button>
            <button onclick="location.href='profile.html'" class="nav-item-m __ME_ACTIVE__"><i class="fas fa-user text-lg"></i><span>ME</span></button>
        </nav>"""

files = {
    'dashboard.html': 'HOME',
    'ai_summary.html': 'AI',
    'trading.html': 'TRADE',
    'options.html': 'CHAIN',
    'ledger.html': 'HISTORY',
    'profile.html': 'ME'
}

for filename, active_tab in files.items():
    f = 'ACTIVE/Insight_Engine/frontend_native/' + filename
    try:
        with open(f, 'r') as file:
            content = file.read()
    except FileNotFoundError:
        continue
    
    # Generate nav for this specific page
    current_nav = nav_html
    for tab in ['HOME', 'AI', 'TRADE', 'CHAIN', 'HISTORY', 'ME']:
        if tab == active_tab:
            current_nav = current_nav.replace(f'__{tab}_ACTIVE__', 'active')
        else:
            current_nav = current_nav.replace(f'__{tab}_ACTIVE__', '')
            
    # Replace the existing nav. Match <nav class="mobile-nav"> ... </nav>
    pattern = r'<nav class="mobile-nav">[\s\S]*?</nav>'
    if re.search(pattern, content):
        content = re.sub(pattern, current_nav, content)
        with open(f, 'w') as file:
            file.write(content)
        print(f"Updated nav in {f}")
    else:
        print(f"Could not find mobile-nav in {f}")
