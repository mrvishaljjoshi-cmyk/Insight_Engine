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
        
    # Clean ALL existing navs
    content = re.sub(r'<nav class="mobile-nav">[\s\S]*?</nav>', '', content)
    
    # Inject before the first closing </body>
    if '</body>' in content:
        # We need to ensure it stays INSIDE the mobile-view div if possible
        if '</div>\n\n    <!-- PROFILE MODAL -->' in content:
            new_content = content.replace('</div>\n\n    <!-- PROFILE MODAL -->', current_nav + '\n    </div>\n\n    <!-- PROFILE MODAL -->')
        elif '</div>\n\n    <script type="module">' in content:
            new_content = content.replace('</div>\n\n    <script type="module">', current_nav + '\n    </div>\n\n    <script type="module">')
        else:
            new_content = content.replace('</body>', current_nav + '\n</body>')
            
        with open(f_path, 'w') as f:
            f.write(new_content)
        print(f"✅ Re-unified {filename}")

