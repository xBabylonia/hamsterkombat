import requests
import json
import time
from datetime import datetime
from itertools import cycle
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

def load_tokens(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file]

def get_headers(token):
    return {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Authorization': f'Bearer {token}',
        'Connection': 'keep-alive',
        'Content-Length': '0',
        'Origin': 'https://hamsterkombat.io',
        'Referer': 'https://hamsterkombat.io/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
    }

def authenticate(token):
    url = 'https://api.hamsterkombat.io/auth/me-telegram'
    headers = get_headers(token)
    response = requests.post(url, headers=headers)
    return response

def sync_clicker(token):
    url = 'https://api.hamsterkombat.io/clicker/sync'
    headers = get_headers(token)
    response = requests.post(url, headers=headers)
    return response

def claim_daily(token):
    url = 'https://api.hamsterkombat.io/clicker/check-task'
    headers = get_headers(token)
    headers['accept'] = 'application/json'
    headers['content-type'] = 'application/json'
    data = json.dumps({"taskId": "streak_days"})
    response = requests.post(url, headers=headers, data=data)
    return response

def tap(token, max_taps, available_taps):
    url = 'https://api.hamsterkombat.io/clicker/tap'
    headers = get_headers(token)
    headers['accept'] = 'application/json'
    headers['content-type'] = 'application/json'
    data = json.dumps({"count": max_taps, "availableTaps": available_taps, "timestamp": int(time.time())})
    response = requests.post(url, headers=headers, data=data)
    return response

def main():
    tokens = load_tokens('tokens.txt')
    token_cycle = cycle(tokens)
    
    while True:
        token = next(token_cycle)
        # Authenticate
        response = authenticate(token)
        if response.status_code == 200:
            user_data = response.json()
            username = user_data['telegramUser']['username']
            print(Fore.GREEN + Style.BRIGHT + f"\n======[{Fore.WHITE + Style.BRIGHT} {username} {Fore.GREEN + Style.BRIGHT}]======")
            # Sync Clicker
            response = sync_clicker(token)
            if response.status_code == 200:
                clicker_data = response.json()['clickerUser']
                print(Fore.YELLOW + Style.BRIGHT + f"[ Level ] : {clicker_data['level']}")
                print(Fore.YELLOW + Style.BRIGHT + f"[ Total Earned ] : {int(clicker_data['totalCoins'])}")
                print(Fore.YELLOW + Style.BRIGHT + f"[ Coin ] : {int(clicker_data['balanceCoins'])}")
                print(Fore.YELLOW + Style.BRIGHT + f"[ Energy ] : {clicker_data['availableTaps']}")

                boosts = clicker_data['boosts']
                boost_max_taps_level = boosts.get('BoostMaxTaps', {}).get('level', 0)
                boost_earn_per_tap_level = boosts.get('BoostEarnPerTap', {}).get('level', 0)
                
                print(Fore.GREEN + Style.BRIGHT + f"[ Max Energy ] : {boost_max_taps_level}")
                print(Fore.GREEN + Style.BRIGHT + f"[ Level Tap ] : {boost_earn_per_tap_level}")
                print(Fore.GREEN + f"\r[ Checkin Daily ] : Checking...", end="", flush=True)

                time.sleep(1)
                # Check Task
                response = claim_daily(token)
                if response.status_code == 200:
                    daily_response = response.json()['task']
                    if daily_response['isCompleted']:
                        print(Fore.GREEN + Style.BRIGHT + f"\r[ Checkin Daily ] Days {daily_response['days']} | Completed", flush=True)
                    else:
                        print(Fore.RED + Style.BRIGHT + f"\r[ Checkin Daily ] Days {daily_response['days']} | Belum saat nya claim daily", flush=True)

                else:
                    print(Fore.RED + Style.BRIGHT + f"\r[ Checkin Daily ] Gagal cek daily {response.status_code}", flush=True)
                print(Fore.GREEN + f"\r[ Tap Status ] : Tapping ...", end="", flush=True)
                response = tap(token, clicker_data['maxTaps'], clicker_data['availableTaps'])
                if response.status_code == 200:
                    print(Fore.GREEN + Style.BRIGHT + "\r[ Tap Status ] : Tapped            ", flush=True)
                else:
                    print(Fore.RED + Style.BRIGHT + "\r[ Tap Status ] : Gagal Tap           ", flush=True)

                    break
                time.sleep(1) 
            else:
                print(Fore.RED + Style.BRIGHT + f"Gagal mendapatkan info user {response.status_code}")
        elif response.status_code == 401:
            error_data = response.json()
            if error_data.get("error_code") == "NotFound_Session":
                print(Fore.RED + Style.BRIGHT + f"=== [ Token Invalid {token} ] ===")
            else:
                print(Fore.RED + Style.BRIGHT + "Authentication failed with unknown error")

        time.sleep(1)  # Add delay to prevent spamming the server

if __name__ == "__main__":
    main()
