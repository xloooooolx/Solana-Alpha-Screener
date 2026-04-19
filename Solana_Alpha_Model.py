import urllib.request
import json
import csv
import math
import ssl

# 1. 破解 Mac 本地 SSL 证书拦截
ssl._create_default_https_context = ssl._create_unverified_context

API_KEY = "370265914c084d98ba8d85e9bd8e3449"
url = "https://public-api.birdeye.so/defi/token_trending"

req = urllib.request.Request(url)
req.add_header('accept', 'application/json')
req.add_header('x-chain', 'solana')
req.add_header('X-API-KEY', API_KEY)
req.add_header('User-Agent',
               'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

print("📡 戴上面具，正在穿透 Birdeye 防火墙获取全网趋势数据...")

try:
    response = urllib.request.urlopen(req)
    raw_data = json.loads(response.read())
    data = raw_data.get('data', {}).get('tokens', [])

    results = []
    print(f"🧮 成功抓取到 {len(data)} 个热门代币！正在进行自动化特征清洗...")

    for token in data:
        symbol = token.get('symbol', 'Unknown')
        address = token.get('address', '')

        # 兼容 Birdeye 可能更改的所有字段命名，降低门槛到 10 刀防止漏网之鱼
        liquidity = float(token.get('liquidity') or 0)
        volume = float(token.get('volume24hUSD') or token.get('v24hUSD') or token.get('volume24h') or 0)

        if liquidity > 10 and volume > 10:
            score = (0.5 * math.log10(liquidity)) + (0.5 * math.log10(volume))

            results.append({
                'Token': symbol,
                'Contract_Address': address,
                'Liquidity(USD)': round(liquidity, 2),
                'Volume_24h(USD)': round(volume, 2),
                'Math_Alpha_Score': round(score, 3)
            })

    # 兜底判断：如果抓到了数据并且成功清洗
    if len(results) > 0:
        results.sort(key=lambda x: x['Math_Alpha_Score'], reverse=True)
        filename = "Alpha_Tokens_Report.csv"
        fieldnames = ['Token', 'Contract_Address', 'Liquidity(USD)', 'Volume_24h(USD)', 'Math_Alpha_Score']

        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

        print(f"✅ 完美击破！模型运行完毕，请双击左侧目录的：{filename}")
    else:
        print("\n⚠️ 警报：找到了数据，但字段对不上。这是服务器发来的第一条【原始底牌】，请截图发给我！")
        if len(data) > 0:
            # 开启 X光透视，打印一条原始数据看看它的键值名到底叫什么
            print(json.dumps(data[0], indent=2, ensure_ascii=False))
        else:
            print("服务器返回了空列表。")

except Exception as e:
    print(f"❌ 发生致命错误: {e}")