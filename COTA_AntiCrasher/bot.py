import os
import re
import time
import asyncio
import requests
import a2s
from mcrcon import MCRcon

# ==================== KONFİGÜRASYON ====================
DISCORD_WEBHOOK_URL = "WEBHOOK_LINKINI_BURAYA_YAPIŞTIR"
LOG_FILE_PATH = r"C:\SquadServer\SquadGame\Saved\Logs\SquadServer.log"

SERVER_IP = "127.0.0.1"        # Sunucu IP
SERVER_QUERY_PORT = 27165     # Squad A2S Query Port
RCON_PORT = 21114             # Squad RCON Port
RCON_PASSWORD = "RCON_SIFRENIZ" # Squad RCON Şifresi

WHITELIST_STEAM_IDS = [
    "76561198000000000"
]

CHECK_INTERVAL = 5
# =======================================================

def execute_rcon_ban(steam_id, reason="Automated Security: Fecurity/Crasher Exploit Detected"):
    if steam_id in WHITELIST_STEAM_IDS:
        print(f"[WHITELIST] {steam_id} korumalı listede.")
        return False
    try:
        with MCRcon(SERVER_IP, RCON_PASSWORD, port=RCON_PORT) as mcr:
            command = f"AdminBan {steam_id} 0 {reason}"
            response = mcr.command(command)
            print(f"[RCON BAN] {steam_id} yasaklandı: {response}")
            return True
    except Exception as e:
        print(f"[RCON ERROR] Ban atılamadı: {e}")
        return False

def send_discord_alert(title, description, color=15158332, fields=None):
    embed = {
        "title": title,
        "description": description,
        "color": color,
        "footer": {"text": "COTA Squad Sentinel • Anti-Fecurity Module"}
    }
    if fields:
        embed["fields"] = fields
    try:
        requests.post(DISCORD_WEBHOOK_URL, json={"embeds": [embed]}, timeout=5)
    except Exception as e:
        print(f"[ERROR] Webhook hatası: {e}")

async def monitor_logs():
    print("[INIT] Anti-Crasher Log Parser aktif...")
    while not os.path.exists(LOG_FILE_PATH):
        await asyncio.sleep(2)

    with open(LOG_FILE_PATH, "r", encoding="utf-8", errors="ignore") as file:
        file.seek(0, os.SEEK_END)
        
        crasher_patterns = [
            r"Reliable buffer overflow",
            r"UNetConnection::Tick",
            r"Received corrupt packet",
            r"Channel bundle overflow",
            r"RPC_KillServer",
            r"Invalid Entity ID",
            r"RPC_Overflow"
        ]
        
        join_pattern = r"Join succeeded:\s*(.+)\s*\(OnlineIDs:\s*EOS:\s*([a-f0-9]+)\s*steam:\s*(\d+)\)"
        recent_players = []
        violation_timestamps = []

        while True:
            line = file.readline()
            if not line:
                await asyncio.sleep(0.05)
                continue

            join_match = re.search(join_pattern, line)
            if join_match:
                player_name = join_match.group(1)
                steam_id = join_match.group(3)
                recent_players.append({"name": player_name, "steam_id": steam_id, "time": time.time()})
                if len(recent_players) > 15:
                    recent_players.pop(0)

            for pattern in crasher_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    now = time.time()
                    violation_timestamps.append(now)
                    violation_timestamps = [t for t in violation_timestamps if now - t <= 3]

                    if len(violation_timestamps) >= 3:
                        target_steam_id = None
                        target_name = "Bilinmeyen Oyuncu"
                        
                        if recent_players:
                            last_player = recent_players[-1]
                            target_steam_id = last_player["steam_id"]
                            target_name = last_player["name"]

                        ban_status = "Başarısız"
                        if target_steam_id and execute_rcon_ban(target_steam_id):
                            ban_status = "OTOMATİK BANLANDI ⛔"

                        send_discord_alert(
                            title="🚨 FECURITY SPAM / CRASHER TESPİT EDİLDİ!",
                            description=f"Yüksek frekansta paket spam'i yakalandı.\n\n**Log:**\n```{line.strip()[:1000]}```",
                            color=15158332,
                            fields=[
                                {"name": "Şüpheli Oyuncu", "value": target_name, "inline": True},
                                {"name": "Steam ID", "value": f"[{target_steam_id}](https://steamcommunity.com/profiles/{target_steam_id})" if target_steam_id else "Yok", "inline": True},
                                {"name": "Aksiyon", "value": ban_status, "inline": False}
                            ]
                        )
                        violation_timestamps.clear()
                    break

async def monitor_heartbeat():
    print("[INIT] Heartbeat Monitor aktif...")
    is_down = False
    while True:
        try:
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(None, lambda: a2s.info((SERVER_IP, SERVER_QUERY_PORT), timeout=3))
            if is_down:
                send_discord_alert(title="✅ SUNUCU NORMALE DÖNDÜ", description="A2S yanıt veriyor.", color=3066993)
                is_down = False
        except Exception:
            if not is_down:
                send_discord_alert(title="🚨 SUNUCU DÜŞTÜ / DDOS!", description="A2S yanıt veremiyor.", color=15158332)
                is_down = True
        await asyncio.sleep(CHECK_INTERVAL)

async def main():
    send_discord_alert("🤖 Anti-Crasher Sentinel Hazır", "Fecurity Auto-Ban ve DDoS Takip Sistemi Aktif.", color=3066993)
    await asyncio.gather(monitor_logs(), monitor_heartbeat())

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("[EXIT] Kapatıldı.")