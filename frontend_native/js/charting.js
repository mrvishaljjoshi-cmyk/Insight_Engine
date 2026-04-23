/**
 * Insight V3 - Charting Engine (Lightweight Charts)
 * Author: Vishal Joshi (vishaljoshi9694@gmail.com)
 */

export function createChart(containerId, color = '#00f2ff') {
    const container = document.getElementById(containerId);
    if (!container) return null;

    const chart = LightweightCharts.createChart(container, {
        width: container.clientWidth,
        height: container.clientHeight,
        layout: {
            backgroundColor: '#000000',
            textColor: '#555',
        },
        grid: {
            vertLines: { color: '#080808' },
            horzLines: { color: '#080808' },
        },
        crosshair: {
            mode: LightweightCharts.CrosshairMode.Normal,
        },
        rightPriceScale: {
            borderColor: '#111',
        },
        timeScale: {
            borderColor: '#111',
            timeVisible: true,
            secondsVisible: false,
        },
    });

    const series = chart.addAreaSeries({
        topColor: color + '44',
        bottomColor: color + '00',
        lineColor: color,
        lineWidth: 2,
    });

    // Generate some mock historical data if empty
    const data = [];
    let time = Math.floor(Date.now() / 1000) - 100 * 60;
    let price = 22450;
    for (let i = 0; i < 100; i++) {
        data.append({ time: time, value: price });
        time += 60;
        price += (Math.random() - 0.5) * 10;
    }
    series.setData(data);

    window.addEventListener('resize', () => {
        chart.resize(container.clientWidth, container.clientHeight);
    });

    return { chart, series };
}
