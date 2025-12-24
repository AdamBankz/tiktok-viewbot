import requests, sys, json, uuid, time, os
import concurrent.futures
from colorama import init, Fore, Back, Style

os.system('cls' if os.name=='nt' else 'clear')
init(autoreset=True)  # Initialize colorama
API="https://zefame-free.com/api_free.php?action=config"

names = {
    229: "TikTok Views",
    228: "TikTok Followers",
    232: "TikTok Free Likes",
    235: "TikTok Free Shares",
    236: "TikTok Free Favorites"
}

if len(sys.argv) > 1:
    with open(sys.argv[1]) as f:
        data = json.load(f)
else:
    data = requests.get("https://zefame-free.com/api_free.php?action=config").json()

services = data.get('data', {}).get('tiktok', {}).get('services', [])
print(f"{Fore.CYAN}Available Services:{Style.RESET_ALL}")
for i, service in enumerate(services, 1):
    sid = service.get('id')
    name = names.get(sid, service.get('name', '').strip())
    rate = service.get('description', '').strip()
    if rate:
        rate = f"[{rate.replace('vues', 'views').replace('partages', 'shares').replace('favoris', 'favorites')}]"
    
    status = f"{Fore.GREEN}[WORKING]{Style.RESET_ALL}" if service.get('available') else f"{Fore.RED}[DOWN]{Style.RESET_ALL}"
    print(f"{i}. {name}  —  {status}  {Fore.CYAN}{rate}{Style.RESET_ALL}")

print(f"\n{Fore.YELLOW}Running ALL available services concurrently...{Style.RESET_ALL}")

profile_url = input('Enter profile URL: ').strip()
video_url = input('Enter video URL: ').strip()

if not profile_url or not video_url:
    print(f"{Fore.RED}Both profile URL and video URL are required!{Style.RESET_ALL}")
    sys.exit()

# Check video ID
id_check = requests.post("https://zefame-free.com/api_free.php?", data={"action": "checkVideoId", "link": video_url})
video_id = id_check.json().get("data", {}).get("videoId")
if not video_id:
    print(f"{Fore.RED}Failed to parse video ID!{Style.RESET_ALL}")
    sys.exit()

print(f"{Fore.GREEN}Parsed Video ID: {video_id}{Style.RESET_ALL}\n")

def run_service(service):
    """Run a single service and return results"""
    service_id = service.get('id')
    service_name = names.get(service_id, service.get('name', '').strip())
    
    if not service.get('available'):
        print(f"{Fore.RED}[DOWN]{Style.RESET_ALL} {service_name}: Service unavailable")
        return
    
    while True:
        try:
            # Use profile URL for followers service, video URL for others
            if service_id == 228:  # TikTok Followers
                link_to_use = profile_url
                video_id_to_use = ""  # No video ID needed for followers
            else:
                link_to_use = video_url
                video_id_to_use = video_id
            
            order = requests.post("https://zefame-free.com/api_free.php?action=order", 
                                data={"service": service_id, "link": link_to_use, 
                                     "uuid": str(uuid.uuid4()), "videoId": video_id_to_use})
            result = order.json()
            
            if result.get("success"):
                print(f"{Fore.GREEN}[SUCCESS]{Style.RESET_ALL} {service_name}: {json.dumps(result, separators=(',',':'))}")
                next_available = result.get("data", {}).get("nextAvailable")
                if next_available:
                    try:
                        wait_time = float(next_available)
                        current_time = time.time()
                        if wait_time > current_time:
                            sleep_duration = wait_time - current_time
                            if sleep_duration > 0:
                                time.sleep(sleep_duration)
                    except:
                        time.sleep(10)
                else:
                    time.sleep(10)
            else:
                print(f"{Fore.YELLOW}[ERROR]{Style.RESET_ALL} {service_name}: {result.get('message', 'Unknown error')}")
                time.sleep(10)
                
        except Exception as e:
            print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} {service_name}: {str(e)}")
            time.sleep(10)

print(f"{Fore.CYAN}Starting infinite concurrent execution of all services...{Style.RESET_ALL}")
print(f"{Fore.YELLOW}Press Ctrl+C to stop{Style.RESET_ALL}\n")

while True:
    try:
        # Run all services concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(services)) as executor:
            futures = [executor.submit(run_service, service) for service in services]
            # Wait for all workers to start (they run infinitely)
            concurrent.futures.wait(futures)
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Stopping execution...{Style.RESET_ALL}")
        break
    except Exception as e:
        print(f"{Fore.RED}Unexpected error: {str(e)}{Style.RESET_ALL}")
        time.sleep(5)  # Wait before retrying

print(f"\n{Fore.GREEN}Program stopped by user{Style.RESET_ALL}")
