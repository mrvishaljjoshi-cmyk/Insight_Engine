import glob
import re

final_modal = """<!-- Profile Modal -->
    <div id="profile-modal" class="hidden fixed inset-0 bg-black/90 backdrop-blur-xl z-[150] flex items-center justify-center p-6">
        <div class="glass p-10 rounded-[2.5rem] max-w-md w-full border-blue-500/20 shadow-2xl relative max-h-[90vh] overflow-y-auto custom-scrollbar">
            <div id="profile-view-section">
                <h2 class="text-2xl font-black mb-6">Profile Settings</h2>
                <div class="space-y-4 mb-8">
                    <div class="p-4 bg-slate-900/50 rounded-2xl border border-slate-800">
                        <p class="text-[9px] font-black text-slate-500 uppercase mb-1">Account Holder</p>
                        <p id="view-username" class="font-black text-white text-lg">--</p>
                    </div>
                    <div class="p-4 bg-slate-900/50 rounded-2xl border border-slate-800">
                        <p class="text-[9px] font-black text-slate-500 uppercase mb-1">Email Address</p>
                        <p id="view-email" class="font-bold text-slate-300">--</p>
                    </div>
                    <div class="p-4 bg-slate-900/50 rounded-2xl border border-slate-800">
                        <p class="text-[9px] font-black text-slate-500 uppercase mb-1">Mobile No</p>
                        <p id="view-mobile" class="font-bold text-slate-300">--</p>
                    </div>
                    <div class="p-4 bg-slate-900/50 rounded-2xl border border-slate-800">
                        <p class="text-[9px] font-black text-slate-500 uppercase mb-1">Telegram Connection</p>
                        <div class="flex justify-between items-center">
                            <p id="view-telegram" class="font-bold text-slate-300">Not Linked</p>
                            <button onclick="window.open('https://t.me/vjinsight_bot', '_blank')" class="text-[8px] bg-blue-600/20 text-blue-400 px-3 py-1 rounded-lg font-black uppercase border border-blue-500/20">Link Now</button>
                        </div>
                    </div>
                </div>
                <div class="grid grid-cols-2 gap-3 mb-4">
                    <button onclick="toggleProfileEdit(true)" class="py-4 bg-blue-600 rounded-2xl font-black text-xs uppercase tracking-widest text-white shadow-lg">Edit Info</button>
                    <button onclick="togglePasswordSection(true)" class="py-4 bg-slate-800 rounded-2xl font-black text-xs uppercase tracking-widest text-white">Security</button>
                </div>
                <button onclick="toggleProfile()" class="w-full py-4 bg-slate-900 rounded-2xl font-black text-xs uppercase border border-slate-800 text-slate-500">Close</button>
            </div>

            <div id="profile-edit-section" class="hidden">
                <h2 class="text-2xl font-black mb-6">Edit Profile</h2>
                <div class="space-y-4 mb-8">
                    <div>
                        <label class="text-[9px] uppercase font-black text-slate-500 block mb-2">Username</label>
                        <input type="text" id="profile-user" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm font-bold text-white outline-none">
                    </div>
                    <div>
                        <label class="text-[9px] uppercase font-black text-slate-500 block mb-2">Email</label>
                        <input type="email" id="profile-email" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm font-bold text-white outline-none">
                    </div>
                    <div>
                        <label class="text-[9px] uppercase font-black text-slate-500 block mb-2">Mobile</label>
                        <input type="text" id="profile-mobile" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm font-bold text-white outline-none">
                    </div>
                    <div>
                        <label class="text-[9px] uppercase font-black text-slate-500 block mb-2">Telegram ID</label>
                        <input type="text" id="profile-telegram" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm font-bold text-white outline-none" placeholder="@username">
                    </div>
                </div>
                <div class="space-y-3">
                    <button onclick="window.updateProfile()" id="btn-update-profile" class="w-full py-4 bg-blue-600 rounded-xl font-black text-xs uppercase tracking-widest text-white">Save Changes</button>
                    <button onclick="toggleProfileEdit(false)" class="w-full py-4 bg-slate-900 rounded-xl font-black text-xs uppercase border border-slate-800 text-slate-500">Cancel</button>
                </div>
            </div>

            <div id="profile-password-section" class="hidden">
                <h2 class="text-2xl font-black mb-6 text-red-500">Security Update</h2>
                <div class="space-y-4 mb-8">
                    <div>
                        <label class="text-[9px] uppercase font-black text-slate-500 block mb-2">Current Password</label>
                        <input type="password" id="pass-current" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm font-bold text-white outline-none">
                    </div>
                    <div>
                        <label class="text-[9px] uppercase font-black text-slate-500 block mb-2">New Password</label>
                        <input type="password" id="pass-new" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm font-bold text-white outline-none">
                    </div>
                </div>
                <div class="space-y-3">
                    <button onclick="window.changePassword()" id="btn-change-pass" class="w-full py-4 bg-red-600 rounded-xl font-black text-xs uppercase tracking-widest text-white">Update Password</button>
                    <button onclick="togglePasswordSection(false)" class="w-full py-4 bg-slate-900 rounded-xl font-black text-xs uppercase border border-slate-800 text-slate-500">Back</button>
                </div>
            </div>
        </div>
    </div>"""

files = ['ai_summary.html', 'trading.html', 'options.html', 'admin.html', 'dashboard.html']
for filename in files:
    f = 'ACTIVE/Insight_Engine/frontend_native/' + filename
    with open(f, 'r') as file:
        content = file.read()
    
    # Replace the entire profile-modal div
    pattern = r'<div id="profile-modal"[\s\S]*?</div>\s*</div>\s*</div>'
    if re.search(pattern, content):
        content = re.sub(pattern, final_modal, content)
        with open(f, 'w') as file:
            file.write(content)
        print(f"Updated {f}")

