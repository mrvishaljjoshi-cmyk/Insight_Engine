import os
import re

# The "Gold Standard" Nav (6 items: Home, AI, Trade, Chain, History, Me)
nav_html_template = """        <nav class="mobile-nav">
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
    
    # 1. Generate the clean nav for this page
    current_nav = nav_html_template
    for k in ['HOME', 'AI', 'TRADE', 'CHAIN', 'HISTORY', 'ME']:
        current_nav = current_nav.replace(f'[[{k}_ACT]]', 'active' if k == active_key else '')
    
    # 2. Remove ALL existing mobile-nav blocks to prevent duplicates
    # Use non-greedy match to find all <nav class="mobile-nav">...</nav>
    content = re.sub(r'<nav class="mobile-nav">[\s\S]*?</nav>', '', content)
    
    # 3. Inject the clean nav before the first closing </div> that is followed by the first <script
    # This is a safe spot (end of main content container)
    if '<script' in content:
        parts = content.split('<script', 1)
        # Find the last </div> in the first part
        last_div_idx = parts[0].rfind('</div>')
        if last_div_idx != -1:
            new_content = parts[0][:last_div_idx] + current_nav + "\n    " + parts[0][last_div_idx:] + '<script' + parts[1]
            with open(f_path, 'w') as f:
                f.write(new_content)
            print(f"✅ Cleaned and Standardized {filename}")
        else:
            print(f"⚠️ Could not find injection point in {filename}")

