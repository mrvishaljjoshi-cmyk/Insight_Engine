import glob
import re

new_modal = """<!-- Profile Modal -->
    <div id="profile-modal" class="hidden fixed inset-0 bg-black/90 backdrop-blur-xl z-[150] flex items-center justify-center p-6">
        <div class="glass p-10 rounded-[2.5rem] max-w-md w-full border-blue-500/20 shadow-2xl relative max-h-[90vh] overflow-y-auto custom-scrollbar">
            <h2 class="text-2xl font-black mb-6">Profile Settings</h2>
            <div class="space-y-4">
                <div class="p-5 bg-slate-900/50 rounded-2xl border border-slate-800 mb-4">
                    <h4 class="text-[10px] font-black uppercase text-blue-400 mb-3 tracking-widest">Connect Intelligence</h4>
                    <button onclick="window.open('https://t.me/vjinsight_bot', '_blank')" class="w-full py-3 bg-blue-600 rounded-xl font-black text-[10px] uppercase tracking-widest mb-2 flex items-center justify-center gap-2">
                        <i class="fab fa-telegram-plane"></i> Link Telegram Bot
                    </button>
                    <p class="text-[9px] text-slate-500 text-center">Get AI reports on @vjinsight_bot</p>
                </div>
                <div>
                    <label class="text-[9px] uppercase font-black text-slate-600 block mb-2 tracking-widest">Username</label>
                    <input type="text" id="profile-user" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm font-bold focus:border-blue-500 outline-none">
                </div>
                <div>
                    <label class="text-[9px] uppercase font-black text-slate-600 block mb-2 tracking-widest">Email Address</label>
                    <input type="email" id="profile-email" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm font-bold focus:border-blue-500 outline-none">
                </div>
                <div>
                    <label class="text-[9px] uppercase font-black text-slate-600 block mb-2 tracking-widest">Mobile Number</label>
                    <input type="text" id="profile-mobile" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm font-bold focus:border-blue-500 outline-none" placeholder="+91">
                </div>
                <div>
                    <label class="text-[9px] uppercase font-black text-slate-600 block mb-2 tracking-widest">Telegram ID / Username</label>
                    <input type="text" id="profile-telegram" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm font-bold focus:border-blue-500 outline-none" placeholder="@username">
                </div>
                <div class="flex gap-4 pt-4">
                    <button onclick="window.updateProfile()" id="btn-update" class="flex-1 bg-blue-600 hover:bg-blue-500 py-4 rounded-xl font-black text-xs uppercase tracking-widest shadow-lg transition-all">Request Update</button>
                    <button onclick="toggleProfile()" class="flex-1 bg-slate-900 py-4 rounded-xl font-black text-xs uppercase border border-slate-800 transition-all">Close</button>
                </div>
            </div>
        </div>
    </div>"""

files = ['ai_summary.html', 'trading.html', 'options.html', 'admin.html', 'dashboard.html']
for filename in files:
    f = 'ACTIVE/Insight_Engine/frontend_native/' + filename
    with open(f, 'r') as file:
        content = file.read()
    
    # Use regex to find <!-- Profile Modal --> or <div id="profile-modal" ... up to the next <script type="module">
    pattern = r'<!-- Profile Modal -->[\s\S]*?<script type="module">'
    if re.search(pattern, content):
        new_content = re.sub(pattern, new_modal + '\n\n    <script type="module">', content)
        with open(f, 'w') as file:
            file.write(new_content)
        print(f"Updated {f}")
    else:
        # try without <!-- Profile Modal -->
        pattern2 = r'<div id="profile-modal"[\s\S]*?<script type="module">'
        if re.search(pattern2, content):
            new_content = re.sub(pattern2, new_modal + '\n\n    <script type="module">', content)
            with open(f, 'w') as file:
                file.write(new_content)
            print(f"Updated {f}")
