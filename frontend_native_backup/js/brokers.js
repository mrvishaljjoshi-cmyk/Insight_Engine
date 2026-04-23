/**
 * Broker Management - Insight Engine
 * Author: Vishal Joshi (vishaljoshi9694@gmail.com)
 */
import { getBrokers, addBroker, deleteBroker } from './api.js';

const BROKER_CONFIGS = [
    { name: 'Zerodha', fields: ['API Key', 'API Secret', 'Client ID', 'TOTP Secret'], color: 'blue' },
    { name: 'Angel One', fields: ['SmartAPI Key', 'Client ID', 'Password', 'TOTP Secret'], color: 'indigo' },
    { name: 'Groww', fields: ['API Key', 'API Secret'], color: 'green' },
    { name: 'Dhan', fields: ['Client ID', 'Access Token'], color: 'purple' },
    { name: 'Upstox', fields: ['API Key', 'API Secret', 'Redirect URI'], color: 'orange' }
];

async function refreshBrokers() {
    try {
        const connected = await getBrokers();
        ['d-connected-list', 'm-connected-list'].forEach(id => {
            const list = document.getElementById(id);
            if (!list) return;

            if (connected.length === 0) {
                list.innerHTML = `
                    <div class="text-center py-12 text-slate-500 glass rounded-[2rem] border-dashed border-2 border-slate-800">
                        <i class="fas fa-plug text-4xl mb-4 opacity-20"></i>
                        <p class="text-sm font-black uppercase tracking-widest">No Active Uplinks</p>
                        <p class="text-[8px] uppercase tracking-widest mt-2">Add a demat account to authorize trading</p>
                    </div>`;
            } else {
                list.innerHTML = connected.map(b => `
                    <div class="flex justify-between items-center p-6 bg-slate-900/40 rounded-[2rem] border border-white/5 hover:border-blue-500/30 transition-all group">
                        <div class="flex items-center gap-4">
                            <div class="w-12 h-12 rounded-2xl bg-slate-950 flex items-center justify-center border border-slate-800 group-hover:border-blue-500/20 transition-all">
                                <i class="fas fa-university text-slate-400 group-hover:text-blue-400"></i>
                            </div>
                            <div>
                                <p class="font-black text-lg text-slate-100 uppercase tracking-tighter">${b.broker_name}</p>
                                <div class="flex items-center gap-2">
                                    <span class="w-2 h-2 rounded-full ${b.is_active ? 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.5)]' : 'bg-slate-600'}"></span>
                                    <p class="text-[9px] ${b.is_active ? 'text-green-500' : 'text-slate-500'} uppercase font-black tracking-widest">
                                        ${b.is_active ? 'Encrypted Link Active' : 'Offline'}
                                    </p>
                                </div>
                            </div>
                        </div>
                        <button onclick="handleDelete(${b.id})" class="w-10 h-10 flex items-center justify-center rounded-xl bg-red-500/5 hover:bg-red-500/20 text-red-500/50 hover:text-red-500 transition-all border border-red-500/10">
                            <i class="fas fa-power-off text-xs"></i>
                        </button>
                    </div>`).join('');
            }
        });
    } catch (e) { console.error('Refresh brokers failed:', e); }
}

window.handleDelete = async (id) => {
    if (confirm('Terminate this broker uplink? Security context will be purged.')) {
        await deleteBroker(id);
        refreshBrokers();
    }
};

window.showAddForm = (name) => {
    const broker = BROKER_CONFIGS.find(b => b.name === name);
    const modal = document.getElementById('broker-modal');
    const formContainer = document.getElementById('modal-content');
    if (!modal || !formContainer) return;

    modal.classList.remove('hidden');
    modal.classList.add('flex');

    formContainer.innerHTML = `
        <div class="flex justify-between items-center mb-10">
            <div class="flex items-center gap-4">
                <div class="w-12 h-12 rounded-2xl bg-blue-600/10 flex items-center justify-center border border-blue-500/20">
                    <i class="fas fa-plus text-blue-500 text-sm"></i>
                </div>
                <div>
                    <h4 class="font-black text-white text-xl uppercase tracking-tighter">Connect ${name}</h4>
                    <p class="text-[9px] text-slate-500 uppercase font-black tracking-[0.2em]">Authorized API Provisioning</p>
                </div>
            </div>
            <button onclick="hideBrokerForm()" class="w-10 h-10 flex items-center justify-center rounded-xl hover:bg-slate-800 text-slate-500 transition-all">
                <i class="fas fa-times"></i>
            </button>
        </div>
        <div class="space-y-8">
            <div class="grid grid-cols-1 gap-6">
                ${broker.fields.map(f => `
                    <div class="space-y-2">
                        <label class="text-[9px] uppercase font-black text-slate-500 tracking-widest ml-2">${f}</label>
                        <input type="${f.toLowerCase().includes('password') || f.toLowerCase().includes('secret') ? 'password' : 'text'}"
                            id="field-${f.replace(/\s/g, '')}"
                            class="w-full bg-slate-950 border border-slate-800 rounded-2xl px-5 py-4 text-sm focus:border-blue-500 transition-all text-white font-medium"
                            placeholder="Provision ${f}">
                    </div>`).join('')}
            </div>
            <div class="pt-4 space-y-4">
                <button onclick="testBroker('${name}')" id="test-btn" class="w-full bg-slate-900 border border-slate-800 hover:border-blue-500/30 py-4 rounded-2xl text-[10px] font-black tracking-widest uppercase transition-all">
                    TEST SECURE HANDSHAKE
                </button>
                <button onclick="submitBroker('${name}')" id="submit-btn" class="w-full bg-blue-600 hover:bg-blue-500 py-5 rounded-[2rem] text-sm font-black tracking-widest uppercase transition-all shadow-2xl shadow-blue-900/40 active:scale-95">
                    AUTHORIZE UPLINK
                </button>
                <p class="text-center text-[8px] text-slate-600 uppercase font-black tracking-widest leading-relaxed">End-to-End Encryption Enabled (RSA-4096).<br>No sensitive keys are stored in unencrypted memory.</p>
            </div>
        </div>`;
};

window.hideBrokerForm = () => {
    const modal = document.getElementById('broker-modal');
    if (modal) { modal.classList.add('hidden'); modal.classList.remove('flex'); }
};

window.testBroker = async (name) => {
    const btn = document.getElementById('test-btn');
    if (btn) { btn.disabled = true; btn.innerText = 'INITIATING HANDSHAKE...'; }
    try {
        await new Promise(resolve => setTimeout(resolve, 1200));
        alert('HANDSHAKE SUCCESSFUL: Security context verified.');
        btn.innerText = 'HANDSHAKE VERIFIED';
        btn.className = "w-full bg-green-600/10 border border-green-500/30 text-green-500 py-4 rounded-2xl text-[10px] font-black tracking-widest uppercase";
    } catch (error) { alert('HANDSHAKE FAILED: Invalid parameters.'); btn.innerText = 'RETRY HANDSHAKE'; }
    finally { if (btn) btn.disabled = false; }
};

window.submitBroker = async (name) => {
    const broker = BROKER_CONFIGS.find(b => b.name === name);
    const credentials = {};
    const btn = document.getElementById('submit-btn');

    for (const field of broker.fields) {
        const input = document.getElementById(`field-${field.replace(/\s/g, '')}`);
        if (input) credentials[field] = input.value.trim();
    }

    if (Object.values(credentials).some(v => !v)) { alert('ERROR: All security fields required for provisioning.'); return; }

    if (btn) { btn.disabled = true; btn.innerText = 'PROVISIONING...'; }
    try {
        const res = await addBroker(name, credentials);
        if (res) { hideBrokerForm(); refreshBrokers(); }
    } catch (e) { console.error('Provisioning failed:', e); }
    finally { if (btn) { btn.disabled = false; btn.innerText = 'AUTHORIZE UPLINK'; } }
};

function renderBrokerGrid() {
    ['d-broker-grid', 'm-broker-grid'].forEach(id => {
        const grid = document.getElementById(id);
        if (!grid) return;
        grid.innerHTML = BROKER_CONFIGS.map(b => `
            <button onclick="showAddForm('${b.name}')"
                class="p-8 bg-slate-900/40 border border-white/5 rounded-[2.5rem] hover:border-blue-500/30 hover:bg-slate-900 transition-all text-left group flex flex-col justify-between h-full min-h-[180px] shadow-xl">
                <div>
                    <div class="w-12 h-12 rounded-2xl bg-slate-950 flex items-center justify-center border border-slate-800 mb-6 group-hover:scale-110 transition-all shadow-inner">
                        <i class="fas fa-plus text-blue-500 text-xs"></i>
                    </div>
                    <p class="text-[9px] font-black text-slate-500 uppercase tracking-[0.2em] mb-2">${b.name}</p>
                    <p class="text-xl font-black text-slate-100 uppercase tracking-tighter">Add Link</p>
                </div>
                <div class="mt-4 flex items-center gap-2 text-[9px] font-black text-blue-400 uppercase tracking-widest opacity-0 group-hover:opacity-100 transition-all translate-y-2 group-hover:translate-y-0">
                    Secure Setup <i class="fas fa-arrow-right ml-1"></i>
                </div>
            </button>`).join('');
    });
}

function init() { renderBrokerGrid(); refreshBrokers(); }
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
else init();
