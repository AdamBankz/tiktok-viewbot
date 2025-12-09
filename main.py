import requests, sys, json, uuid, time, os, re, datetime
from colorama import init, Fore, Style

os.system('cls' if os.name=='nt' else 'clear')
init(autoreset=True)

order_logs = []

ansi_escape = re.compile(r'\x1b\[[0-9;]*m')

def visible_len(s):
    return len(ansi_escape.sub('', s))

def expand_period(text):
    text = text.replace("min", "minutes")
    text = text.replace("mins", "minutes")
    text = text.replace("hr", "hour")
    text = text.replace("hrs", "hours")
    text = text.replace("h", "hours")

    text = re.sub(r'(\d)(hour)', r'\1 hour', text)
    text = re.sub(r'(\d)(hours)', r'\1 hours', text)
    text = text.replace("1 hours", "1 hour")
    return text

preferred_order = [228, 229, 232, 236, 235, 999]

names = {
    229: "TikTok Views",
    228: "TikTok Followers",
    232: "TikTok Likes",
    235: "TikTok Shares",
    236: "TikTok Favorites"
}

if len(sys.argv) > 1:
    with open(sys.argv[1]) as f:
        data = json.load(f)
else:
    data = requests.get("https://zefame-free.com/api_free.php?action=config").json()

all_services = data.get('data', {}).get('tiktok', {}).get('services', [])

logs_entry = {
    "id": 999,
    "name": "Logs",
    "description": "",
    "available": True
}

all_services.append(logs_entry)

services = sorted(all_services, key=lambda s: preferred_order.index(s.get('id')) if s.get('id') in preferred_order else 999)

lines = []
lengths = []

for i, service in enumerate(services, 1):
    sid = service.get('id')

    if sid == 999:
        line = f"{Fore.CYAN}{i}.{Style.RESET_ALL} {Fore.GREEN}[WORKING]{Style.RESET_ALL} Logs"
        lines.append(line)
        lengths.append(visible_len(line))
        continue

    name = names.get(sid, service.get('name', '').strip())
    raw_rate = service.get('description', '').strip()
    rate = ""

    if raw_rate:
        r = raw_rate.replace("vues", "views").replace("partages", "shares").replace("favoris", "favorites")
        parts = r.split(" ")
        amount = parts[0]
        srv = parts[1]
        period = expand_period(" ".join(parts[3:]))
        rate = f"{Fore.GREEN}{amount} {srv} every {period}{Style.RESET_ALL}"

    status = f"{Fore.GREEN}[WORKING]{Style.RESET_ALL}" if service.get("available") else f"{Fore.RED}[DOWN]{Style.RESET_ALL}"

    line = (
        f"{Fore.CYAN}{i}.{Style.RESET_ALL} "
        f"{status} "
        f"{name:<35} │ {rate}"
    )
    lines.append(line)
    lengths.append(visible_len(line))

if lines:
    max_len = max(lengths)
    top = "┌" + "─" * (max_len + 2) + "┐"
    bottom = "└" + "─" * (max_len + 2) + "┘"

    print(f"{Fore.LIGHTWHITE_EX}Services powered by: ZeFame{Style.RESET_ALL}")
    print(top)
    for line, ln in zip(lines, lengths):
        padding = " " * (max_len - ln)
        print(f"│ {line}{padding} │")
    print(bottom)

print(f"\n{Fore.CYAN}Please select an option:{Style.RESET_ALL} ", end="")
choice = input().strip()
if not choice:
    sys.exit()

try:
    idx = int(choice)
    if idx < 1 or idx > len(services):
        print("Out of range")
        sys.exit()
except:
    print("Invalid")
    sys.exit()

selected = services[idx - 1]
sid = selected.get("id")

if sid == 999:
    print("\nORDER HISTORY\n")
    if not order_logs:
        print("There are no logged records of orders yet.\n")
        sys.exit()
    for entry in order_logs:
        print(entry)
    print()
    sys.exit()

if sid == 228:
    user_input = input("Enter profile URL: ")
else:
    user_input = input("Enter video URL: ")

print()

id_check = requests.post(
    "https://zefame-free.com/api_free.php?",
    data={"action": "checkVideoId", "link": user_input}
)

video_id = id_check.json().get("data", {}).get("videoId")
print(f"Parsed Video ID: {video_id}\n")

while True:
    order = requests.post(
        "https://zefame-free.com/api_free.php?action=order",
        data={
            "service": selected.get("id"),
            "link": user_input,
            "uuid": str(uuid.uuid4()),
            "videoId": video_id
        }
    )

    result = order.json()
    success = result.get("success", False)

    service_name = names.get(sid, "Unknown")

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if success:
        print(Fore.GREEN + "Order was sent successfully, please be patient" + Style.RESET_ALL)
        order_logs.append(f"[{timestamp}] ({service_name}): Successful")
    else:
        print(Fore.RED + "Something went wrong, please try again" + Style.RESET_ALL)
        order_logs.append(f"[{timestamp}] ({service_name}): Unsuccessful")

    wait = result.get("data", {}).get("nextAvailable")

    if wait:
        try:
            wait = float(wait)
            now = time.time()

            if wait > now:
                total = wait - now
                finish_time = datetime.datetime.fromtimestamp(wait).strftime("%H:%M:%S")
                print("\nNext available in:")

                bar_length = 40
                start = time.time()

                while time.time() < wait:
                    elapsed = time.time() - start
                    progress = min(elapsed / total, 1)
                    filled = int(progress * bar_length)
                    empty = bar_length - filled

                    bar = "█" * filled + "░" * empty
                    remaining = int(wait - time.time())

                    print(f"\r[{bar}] {remaining} seconds left ({finish_time})", end="")
                    time.sleep(0.1)

                print("\n")
        except:
            pass