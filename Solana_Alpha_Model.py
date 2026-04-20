import urllib.request
import json
import csv
import math
import ssl

# 忽略本地 SSL 验证 (Mac 环境)
ssl._create_default_https_context = ssl._create_unverified_context

API_KEY = "370265914c084d98ba8d85e9bd8e3449"
url = "https://public-api.birdeye.so/defi/token_trending"

req = urllib.request.Request(url)
req.add_header('accept', 'application/json')
req.add_header('x-chain', 'solana')
req.add_header('X-API-KEY', API_KEY)
req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

print("INFO: Requesting trending tokens from Birdeye API...")

try:
    response = urllib.request.urlopen(req)
    raw_data = json.loads(response.read())
    data = raw_data.get('data', {}).get('tokens', [])

    results = []
    print(f"INFO: Successfully fetched {len(data)} tokens. Starting data cleaning and scoring...")

    for token in data:
        symbol = token.get('symbol', 'Unknown')
        address = token.get('address', '')

        # 提取流动性与交易量指标
        liquidity = float(token.get('liquidity') or 0)
        volume = float(token.get('volume24hUSD') or token.get('v24hUSD') or token.get('volume24h') or 0)

        # 过滤极低流动性资产并进行对数平滑处理
        if liquidity > 10 and volume > 10:
            score = (0.5 * math.log10(liquidity)) + (0.5 * math.log10(volume))

            results.append({
                'Token': symbol,
                'Contract_Address': address,
                'Liquidity(USD)': round(liquidity, 2),
                'Volume_24h(USD)': round(volume, 2),
                'Alpha_Score': round(score, 3)
            })

    if len(results) > 0:
        # 按得分降序排列
        results.sort(key=lambda x: x['Alpha_Score'], reverse=True)
        filename = "Alpha_Tokens_Report.csv"
        fieldnames = ['Token', 'Contract_Address', 'Liquidity(USD)', 'Volume_24h(USD)', 'Alpha_Score']

        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

        print(f"SUCCESS: Model execution completed. Results saved to {filename}")
    else:
        print("WARNING: Data fetched but fields mismatched.")
        if len(data) > 0:
            print(json.dumps(data[0], indent=2, ensure_ascii=False))
        else:
            print("ERROR: Server returned an empty list.")

except Exception as e:
    print(f"ERROR: Execution failed. {e}")
