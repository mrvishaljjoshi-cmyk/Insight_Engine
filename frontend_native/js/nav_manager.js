/**
 * Nav Manager - 3D Neon-Pulse Navigation Engine
 * Author: Vishal Joshi (vishaljoshi9694@gmail.com)
 */

const navItems = [
    { label: 'TRADING TERMINAL', icon: 'fas fa-crosshairs', url: 'trading.html' },
    { label: 'MY HOLDINGS', icon: 'fas fa-chart-pie', url: 'dashboard.html' },
    { label: 'AI MARKET GUIDE', icon: 'fas fa-bolt', url: 'ai_summary.html' },
    { label: 'OPTIONS CHAIN', icon: 'fas fa-list', url: 'options.html' },
    { label: 'ALPHA SIGNALS', icon: 'fas fa-signal', url: 'signals.html' },
    { label: 'TRADE HISTORY', icon: 'fas fa-history', url: 'ledger.html' }
];

export function initNavigation() {
    applyViewPreference();
    injectDesktopNav();
    injectMobileNav();
    
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
            <div class="mb-10 flex items-center px-5 py-8 cursor-pointer border-b border-slate-800" onclick="location.href='dashboard.html'">
                <div class="w-10 h-10 bg-slate-900 border border-[#00e5ff] flex items-center justify-center shrink-0 shadow-[0_0_15px_rgba(0,229,255,0.3)]">
                    <i class="fas fa-atom text-[#00e5ff] text-lg animate-pulse"></i>
                </div>
                <span class="nav-text font-black text-xl tracking-tighter ml-4 text-white">INSIGHT_V3</span>
            </div>
            <nav class="flex-grow space-y-1">
                ${navItems.map(item => `
                    <button onclick="location.href='${item.url}'" 
                        class="w-full flex items-center transition-all duration-200 ${currentPage === item.url ? 'active bg-slate-800/50' : 'hover:bg-slate-800/30'}">
                        <i class="${item.icon} text-sm ${currentPage === item.url ? 'text-[#00e5ff]' : 'text-white'}"></i>
                        <span class="nav-text ${currentPage === item.url ? 'text-white font-black' : 'text-white font-bold'}">${item.label}</span>
                    </button>
                `).join('')}
            </nav>
            <div class="mt-auto border-t border-slate-800 pb-6">
                <button onclick="location.href='profile.html'" class="w-full flex items-center hover:bg-slate-800/30">
                    <i class="fas fa-user-shield text-white"></i>
                    <span class="nav-text font-bold text-white">SECURITY CONSOLE</span>
                </button>
                <button onclick="window.triggerLogout()" class="w-full flex items-center hover:bg-red-900/10 group">
                    <i class="fas fa-power-off text-white group-hover:text-red-500"></i>
                    <span class="nav-text font-bold text-white group-hover:text-red-400">DISCONNECT</span>
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
            ${navItems.slice(0, 5).map(item => `
                <button onclick="location.href='${item.url}'" class="nav-item-m ${currentPage === item.url ? 'active' : ''}">
                    <i class="${item.icon} text-lg"></i>
                    <span>${item.label.split(' ')[0]}</span>
                </button>
            `).join('')}
            <button onclick="location.href='profile.html'" class="nav-item-m ${currentPage === 'profile.html' ? 'active' : ''}">
                <i class="fas fa-user-lock text-lg"></i>
                <span>ME</span>
            </button>
        `;
    });
}

window.triggerLogout = () => { 
    if(confirm('DISCONNECT FROM CORE?')) { 
        localStorage.clear(); 
        import('./auth.js').then(m => {
            m.logout();
            window.location.href='login.html';
        });
    } 
};
