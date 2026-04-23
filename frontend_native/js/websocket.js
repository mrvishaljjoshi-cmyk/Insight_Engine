/** Author: Vishal Joshi (vishaljoshi9694@gmail.com) **/
const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const WS_BASE = `${protocol}//${window.location.host}`;

let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 5;
const RECONNECT_DELAY = 3000;

/**
 * Initialize WebSocket for market data
 * @param {function} onTick - Callback function for market ticks
 * @param {string} symbol - Market symbol (default: NIFTY 50)
 * @returns {WebSocket} WebSocket instance
 */
export function initMarketWS(onTick, symbol = 'NIFTY 50') {
    const socket = new WebSocket(`${WS_BASE}/api/ws/market-data`);

    socket.onopen = () => {
        console.log('WebSocket connected');
        reconnectAttempts = 0;
        updateStatus('online');
    };

    socket.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            if (data.error) {
                console.error('WebSocket error:', data.error);
                return;
            }
            onTick(data);
        } catch (e) {
            console.error('Failed to parse WebSocket message:', e);
        }
    };

    socket.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason);
        updateStatus('offline');

        if (!event.wasClean && reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
            reconnectAttempts++;
            console.log(`Reconnecting... Attempt ${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS}`);
            setTimeout(() => initMarketWS(onTick, symbol), RECONNECT_DELAY * reconnectAttempts);
        }
    };

    socket.onerror = (error) => {
        console.error('WebSocket error:', error);
        updateStatus('error');
    };

    return socket;
}

/**
 * Update connection status indicator
 * @param {string} status - 'online', 'offline', or 'error'
 */
function updateStatus(status) {
    const statusEl = document.getElementById('system-status');
    const miniStatusEl = document.getElementById('m-system-status-mini');
    if (!statusEl && !miniStatusEl) return;

    const statusConfig = {
        online: {
            className: 'bg-slate-950 px-4 py-2 rounded-full border border-slate-800 text-[10px] font-black uppercase tracking-widest text-green-400 flex items-center',
            html: '<span class="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></span>System Online',
            miniHtml: '<span class="w-1.5 h-1.5 bg-green-500 rounded-full mr-1 animate-pulse"></span>Pulse Active'
        },
        offline: {
            className: 'bg-slate-950 px-4 py-2 rounded-full border border-slate-800 text-[10px] font-black uppercase tracking-widest text-red-400 flex items-center',
            html: '<span class="w-2 h-2 bg-red-500 rounded-full mr-2"></span>System Offline',
            miniHtml: '<span class="w-1.5 h-1.5 bg-red-500 rounded-full mr-1"></span>Pulse Offline'
        },
        error: {
            className: 'bg-slate-950 px-4 py-2 rounded-full border border-slate-800 text-[10px] font-black uppercase tracking-widest text-yellow-400 flex items-center',
            html: '<span class="w-2 h-2 bg-yellow-500 rounded-full mr-2"></span>Connection Error',
            miniHtml: '<span class="w-1.5 h-1.5 bg-yellow-500 rounded-full mr-1"></span>Pulse Error'
        }
    };

    const config = statusConfig[status] || statusConfig.offline;
    
    if (statusEl) {
        statusEl.className = config.className;
        statusEl.innerHTML = config.html;
    }
    
    if (miniStatusEl) {
        miniStatusEl.innerHTML = config.miniHtml;
        miniStatusEl.className = `text-[7px] font-black uppercase tracking-widest mt-1 flex items-center ${status === 'online' ? 'text-green-400' : status === 'error' ? 'text-yellow-400' : 'text-red-400'}`;
    }
}

/**
 * Close WebSocket connection
 * @param {WebSocket} socket - WebSocket instance
 */
export function closeWebSocket(socket) {
    if (socket && socket.readyState === WebSocket.OPEN) {
        socket.close(1000, 'User disconnected');
    }
}
