import aiohttp
import xml.etree.ElementTree as ET

async def get_latest_news(symbol: str) -> str:
    try:
        url = f"https://news.google.com/rss/search?q={symbol}+NSE+stock+india&hl=en-IN&gl=IN&ceid=IN:en"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers={'User-Agent': 'Mozilla/5.0'}) as response:
                if response.status == 200:
                    xml_data = await response.text()
                    root = ET.fromstring(xml_data)
                    items = root.findall('.//item')
                    headlines = []
                    for item in items[:4]: # Top 4
                        title = item.find('title').text
                        headlines.append(f"- {title}")
                        
                    if headlines:
                        return "Real-Time News Headlines:\\n" + "\\n".join(headlines)
        return f"No recent major news found for {symbol}."
    except Exception as e:
        print(f"News fetch error for {symbol}: {e}")
        return f"Recent market data available for {symbol}, but direct news feed is temporarily offline."
