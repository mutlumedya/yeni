
import requests
import re
import yaml
import time  # Yeni eklenen
import os

# config.yml dosyasını oku
with open("config.yml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

def generate_m3u():
    m3u_content = "#EXTM3U\n"
    base_prefix = config['base_domain_prefix']
    domain = ""

    # Domain arama (aralığı genişlettim, belki yeni numaralar vardır)
    for i in range(1, 3000):  # 1'den 3000'e kadar dene, gerekirse değiştir
        test_domain = f"{base_prefix}{i}.xyz"
        try:
            response = requests.head(test_domain, timeout=3)
            if response.status_code == 200:
                domain = test_domain
                print(f"Bulunan domain: {domain}")
                break
        except:
            continue

    if not domain:
        print("Çalışır domain bulunamadı. Eski dosyayı koruyorum.")
        return False

    success_count = 0
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
                success_count += 1
        except Exception as e:
            print(f"{channel_name} alınamadı: {e}")

    # Dosyaya kaydet
    with open("goals.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_content)

    print(f"{success_count} kanal eklendi. goals.m3u güncellendi.")
    return True

# Ana döngü: Her 15 dakikada (900 saniye) bir çalıştır
print("Otomatik güncelleme başladı. Her 15 dakikada bir kontrol edilecek. Çıkmak için Ctrl+C bas.")
while True:
    try:
        generate_m3u()
        time.sleep(900)  # 15 dakika bekle
    except KeyboardInterrupt:
        print("\nDurduruldu.")
        break
    except Exception as e:
        print(f"Hata: {e}")
        time.sleep(900)
