/**
 * Nav Manager - Universal Navigation Engine for Insight Engine
 * Author: Vishal Joshi (vishaljoshi9694@gmail.com)
 */

const navItems = [
    { label: 'Overview', icon: 'fas fa-home', url: 'dashboard.html' },
    { label: 'AI Strategy', icon: 'fas fa-bolt', url: 'ai_summary.html' },
    { label: 'Terminal', icon: 'fas fa-crosshairs', url: 'trading.html' },
    { label: 'Option Chain', icon: 'fas fa-list', url: 'options.html' },
    { label: 'History', icon: 'fas fa-history', url: 'ledger.html' },
    { label: 'Signals', icon: 'fas fa-signal', url: 'signals.html' }
];

export function initNavigation() {
    applyViewPreference();
    injectDesktopNav();
    injectMobileNav();
    highlightActive();
    
    window.addEventListener('resize', applyViewPreference);
}

function applyViewPreference() {
    const pref = localStorage.getItem('viewPreference') || 'auto';
    const isMobileDevice = window.innerWidth <= 768;
    document.body.classList.remove('force-mobile', 'force-desktop');
    
    if (pref === 'mobile' || (pref === 'auto' && isMobileDevice)) {
        document.body.classList.add('force-mobile');
    } else {
        document.body.classList.add('force-desktop');
    }
}

function injectDesktopNav() {
    const sidebars = document.querySelectorAll('.sidebar');
    sidebars.forEach(sidebar => {
        const currentPage = window.location.pathname.split('/').pop() || 'dashboard.html';
        
        sidebar.innerHTML = `
            <div class="mb-10 flex items-center px-4 cursor-pointer" onclick="location.href='dashboard.html'">
                <div class="w-12 h-12 bg-blue-600 rounded-2xl flex items-center justify-center shrink-0 shadow-lg border border-blue-400/20">
                    <i class="fas fa-chart-pie text-white text-xl"></i>
                </div>
                <span class="nav-text font-black text-2xl tracking-tighter uppercase ml-4 text-white">INSIGHT</span>
            </div>
            <nav class="flex-grow space-y-3 px-2">
                ${navItems.map(item => `
                    <button onclick="location.href='${item.url}'" 
                        class="w-full flex items-center p-4 transition-all duration-300 rounded-2xl group ${currentPage === item.url ? 'text-blue-400 bg-blue-600/10 shadow-lg shadow-blue-900/10' : 'text-slate-500 hover:bg-slate-900/50 hover:text-slate-300'}">
                        <i class="${item.icon} text-lg w-10 text-center transition-transform group-hover:scale-110"></i>
                        <span class="nav-text text-sm uppercase tracking-widest">${item.label}</span>
                    </button>
                `).join('')}
            </nav>
            <div class="mt-auto pt-6 border-t border-slate-800/50 px-2 pb-4">
                <button onclick="window.showProfile()" class="w-full flex items-center p-4 text-slate-500 hover:bg-slate-900/50 hover:text-slate-300 rounded-2xl group">
                    <i class="fas fa-user-circle text-lg w-10 text-center group-hover:scale-110"></i>
                    <span class="nav-text text-sm uppercase tracking-widest">Account</span>
                </button>
                <button onclick="window.triggerLogout()" class="w-full flex items-center p-4 text-red-500/60 hover:bg-red-500/10 hover:text-red-500 rounded-2xl group">
                    <i class="fas fa-power-off text-lg w-10 text-center group-hover:scale-110"></i>
                    <span class="nav-text text-sm uppercase tracking-widest">Logout</span>
                </button>
            </div>
        `;
    });
}

function injectMobileNav() {
    const navs = document.querySelectorAll('.mobile-nav');
    navs.forEach(nav => {
        const currentPage = window.location.pathname.split('/').pop() || 'dashboard.html';
        
        nav.innerHTML = `
            ${navItems.map(item => `
                <button onclick="location.href='${item.url}'" class="nav-item-m ${currentPage === item.url ? 'active' : ''}">
                    <i class="${item.icon} text-lg"></i>
                    <span>${item.label.split(' ')[0]}</span>
                </button>
            `).join('')}
            <button onclick="location.href='profile.html'" class="nav-item-m ${currentPage === 'profile.html' ? 'active' : ''}">
                <i class="fas fa-user text-lg"></i>
                <span>ME</span>
            </button>
        `;
    });
}

function highlightActive() {
    // Already handled in injection logic, but good for dynamic updates if needed
}

window.triggerLogout = () => { 
    if(confirm('Logout?')) { 
        localStorage.clear(); 
        import('./auth.js').then(m => {
            m.logout();
            window.location.href='login.html';
        });
    } 
};
window.showProfile = () => {
    const modal = document.getElementById('profile-modal');
    if(modal) modal.classList.toggle('hidden');
    else window.location.href = 'profile.html';
};
