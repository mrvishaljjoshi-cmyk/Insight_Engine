/** Author: Vishal Joshi (vishaljoshi9694@gmail.com) **/
import { getBrokers } from './api.js';
import { initMarketWS } from './websocket.js';

let chart, candlestickSeries;
let priceHistory = [];
let lastPrice = 22500;

function initChart() {
    const container = document.getElementById('chart-container');
    if (!container) return;

    chart = LightweightCharts.createChart(container, {
        layout: {
            background: { color: 'transparent' },
            textColor: '#94a3b8'
        },
        grid: {
            vertLines: { color: 'rgba(30, 41, 59, 0.2)' },
            horzLines: { color: 'rgba(30, 41, 59, 0.2)' }
        },
        rightPriceScale: {
            borderColor: 'rgba(30, 41, 59, 0.5)',
            scaleMargins: {
                top: 0.1,
                bottom: 0.1
            }
        },
        timeScale: {
            borderColor: 'rgba(30, 41, 59, 0.5)',
            timeVisible: true,
            secondsVisible: false
        },
        crosshair: {
            mode: LightweightCharts.CrosshairMode.Normal
        }
    });

    candlestickSeries = chart.addCandlestickSeries({
        upColor: '#3b82f6',
        downColor: '#ef4444',
        borderVisible: false,
        wickUpColor: '#3b82f6',
        wickDownColor: '#ef4444'
    });

    window.addEventListener('resize', () => {
        if (chart && container) {
            chart.applyOptions({
                width: container.clientWidth,
                height: container.clientHeight
            });
        }
    });

    chart.timeScale().fitContent();
}

async function updateBrokerStats() {
    try {
        const connected = await getBrokers();
        const count = document.getElementById('broker-count');
        if (count) count.innerText = connected.length;
    } catch (e) {
        console.error('Update stats failed:', e);
    }
}

function formatPrice(price) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        maximumFractionDigits: 2
    }).format(price);
}

function updatePriceDisplay(tick) {
    const priceEl = document.getElementById('nifty-price');
    if (!priceEl) return;

    const price = tick.price;
    const prevPrice = lastPrice;
    lastPrice = price;

    priceEl.innerText = formatPrice(price);

    // Color based on change
    if (price > prevPrice) {
        priceEl.className = 'text-4xl font-black text-blue-400 transition-colors duration-300';
    } else if (price < prevPrice) {
        priceEl.className = 'text-4xl font-black text-red-400 transition-colors duration-300';
    }

    // Reset color after animation
    setTimeout(() => {
        priceEl.className = 'text-4xl font-black text-blue-400 transition-colors duration-300';
    }, 500);
}

function init() {
    initChart();
    updateBrokerStats();

    initMarketWS((tick) => {
        updatePriceDisplay(tick);

        if (candlestickSeries && tick.ohlc) {
            const time = Math.floor(tick.unix_timestamp);
            candlestickSeries.update({
                time: time,
                open: tick.ohlc.open,
                high: tick.ohlc.high,
                low: tick.ohlc.low,
                close: tick.ohlc.close
            });
        }
    });
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
