# squad-anti-crasher-sentinel
Lightweight Python log parser, A2S heartbeat monitor &amp; RCON auto-ban tool for Squad server security.
## 🚀 Özellikler
- **Log Parser:** Buffer overflow ve RPC exploit izlerini 50ms frekansla tarar.
- **Auto-Ban (RCON):** Şüpheli paket spam'i atan oyuncuyu tespit edip anında yasaklamaya gönderir.
- **DDoS / Heartbeat Monitor:** Sunucunun A2S yanıtını dinler, düşme durumunda Discord Webhook'a bildirim atar.
- **Whitelist Desteği:** Yönetici ve seeder hesapları için koruma katmanı.

## 🛠️ Kurulum
1. Gerekli kütüphaneleri yükleyin:
   `pip install requests python-a2s mcrcon`
2. `bot.py` içindeki konfigürasyon alanlarını doldurun.
3. Çalıştırın:
   `python bot.py`
