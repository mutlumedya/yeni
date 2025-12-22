import requests
import re
import yaml

# config.yml dosyasını oku
with open("config.yml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

# M3U içeriği
m3u_content = "#EXTM3U\n"

# Trgoals domain kontrol
base_prefix = config['base_domain_prefix']
domain = ""

for i in range(config['domain_start'], config['domain_end']):
    test_domain = f"{base_prefix}{i}.xyz"
    try:
        response = requests.head(test_domain, timeout=3)
        if response.status_code == 200:
            domain = test_domain
            break
    except:
        continue

if not domain:
    print("Çalışır bir domain bulunamadı.")
    exit()

print(f"Bulunan domain: {domain}")

# Kanalları çek
for channel_id, channel_name in config['channels'].items():
    channel_url = f"{domain}/channel.html?id={channel_id}"
    try:
        r = requests.get(channel_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
        match = re.search(r'const baseurl = "(.*?)"', r.text)
        if match:
            baseurl = match.group(1)
            stream_url = f"{baseurl}{channel_id}.m3u8"
            full_url = f"{config['proxy_base']}{stream_url}"
            m3u_content += f'#EXTINF:-1 tvg-logo="{config["logo_url"]}" group-title="{config["group_title"]}", {channel_name}\n'
            m3u_content += f'{full_url}\n'
            print(f"{channel_name} eklendi.")
    except Exception as e:
        print(f"{channel_name} alınamadı: {e}")
        continue

# Dosyaya kaydet
with open("goals.m3u", "w", encoding="utf-8") as f:
    f.write(m3u_content)

print("goals.m3u başarıyla oluşturuldu.")
