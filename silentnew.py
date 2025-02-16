import os
import time
import threading
import requests
from datetime import datetime, timedelta

# Coba import pyfiglet dan termcolor, jika tidak ada maka install otomatis
try:
    import pyfiglet
    from termcolor import colored
except ImportError:
    os.system("pip install pyfiglet termcolor")
    import pyfiglet
    from termcolor import colored

# Menampilkan Banner "PEMPEK LAHAT" dengan warna biru
text = "PEMPEK LAHAT"
ascii_art = pyfiglet.figlet_format(text, font="slant")
print(colored(ascii_art, "blue"))

# URL API Silent Protocol
position_url = "https://ceremony-backend.silentprotocol.org/ceremony/position"
ping_url = "https://ceremony-backend.silentprotocol.org/ceremony/ping"
token_file = "tokens.txt"

# Fungsi untuk memuat token dari file dan mengambil nama akun
def load_tokens():
    try:
        tokens = []
        with open(token_file, "r") as file:
            for line in file:
                if "|" in line:
                    name, token = line.strip().split("|", 1)
                    tokens.append((name, token))
                else:
                    tokens.append(("Unknown", line.strip()))  # Jika format tidak sesuai, pakai "Unknown"
        print(f"{len(tokens)} tokens loaded.")
        return tokens
    except Exception as e:
        print(f"Error loading tokens: {e}")
        return []

# Fungsi untuk membuat headers HTTP
def get_headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    }

# Fungsi untuk mendapatkan posisi token dalam antrean
def get_position(name, token):
    try:
        response = requests.get(position_url, headers=get_headers(token))
        if response.status_code == 200:
            data = response.json()
            behind = data.get("behind", 0)
            time_remaining = data.get("timeRemaining", "0m")  # Format biasanya "XXm"
            
            # Hitung estimasi jam selesai
            try:
                minutes_remaining = int(time_remaining.replace("m", ""))  # Ambil angka dari "Xm"
                estimated_completion = datetime.now() + timedelta(minutes=minutes_remaining)
                estimated_time_str = estimated_completion.strftime("%H:%M WIB")
            except ValueError:
                estimated_time_str = "Unknown"

            print(f"[Token {name}] Position: Behind {behind}, Estimasi selesai: {estimated_time_str}")
            return estimated_time_str
        else:
            print(f"[Token {name}] Gagal mendapatkan posisi. Status: {response.status_code}")
    except Exception as e:
        print(f"[Token {name}] Error fetching position: {e}")

# Fungsi untuk mengirim ping ke server
def ping_server(name, token):
    try:
        response = requests.get(ping_url, headers=get_headers(token))
        if response.status_code == 200:
            print(f"[Token {name}] Ping sukses.")
        else:
            print(f"[Token {name}] Ping gagal. Status: {response.status_code}")
    except Exception as e:
        print(f"[Token {name}] Error pinging: {e}")

# Fungsi utama untuk menjalankan proses otomatis
def run_automation(name, token):
    while True:
        get_position(name, token)
        ping_server(name, token)
        time.sleep(10)

# Fungsi utama untuk menjalankan semua token dalam thread
def main():
    tokens = load_tokens()
    if not tokens:
        print("No tokens available. Exiting.")
        return
    
    threads = []
    for i, (name, token) in enumerate(tokens, start=1):
        print(f"Menjalankan Token {i}: {name}")
        thread = threading.Thread(target=run_automation, args=(name, token))
        thread.start()
        threads.append(thread)
    
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()