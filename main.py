from urllib.parse import urlparse
import requests_cache
import requests
import zipfile
import sys

requests_cache.install_cache("cache")

# Unicode stuff

CROSS_MARK = "\u274C"
CHECK_MARK_BUTTON = "\u2705"

# ANSI colors

ANSI_FG_RED = "\033[0;31m"
ANSI_FG_GREEN = "\033[0;32m"
ANSI_FG_BLUE = "\033[0;34m"

ANSI_RESET = "\033[0m"

def fail():
	print(f"\n{ANSI_FG_RED}Failed to download scene{ANSI_RESET} {CROSS_MARK}")

def success(url):
	print(f"\n{ANSI_FG_GREEN}Downloaded{ANSI_RESET} {url} {ANSI_FG_GREEN}successfully!{ANSI_RESET} {CHECK_MARK_BUTTON}")

def download_image_asset(url, asset, size):
	parsed_scene_url = urlparse(scene_url)

	return requests.get(parsed_scene_url.scheme + "://" + parsed_scene_url.netloc + "/assets/" + parsed_scene_url.fragment + "/" + asset + "/" + str(size) + ".webp")

if 2 > len(sys.argv):
	print(f"{ANSI_FG_RED}ERROR{ANSI_RESET}: You didn't specify a scene URL.")
	fail()
	exit()

scene_url = sys.argv[1]
parsed_scene_url = urlparse(scene_url)

if parsed_scene_url.netloc == "" or (not parsed_scene_url.scheme in ["http", "https"]):
	print(f"{ANSI_FG_RED}ERROR{ANSI_RESET}: Invalid scene URL.")
	fail()
	exit()

print("Downloading JSON data...")

json_response = requests.get(parsed_scene_url.scheme + "://" + parsed_scene_url.netloc + "/api/scene/" + parsed_scene_url.fragment)

if json_response.status_code != 200:
	print(f"{ANSI_FG_RED}ERROR{ANSI_RESET}: The scene {scene_url} does not exist.")
	fail()
	exit()

scene_data = json_response.json()

print("Reading JSON data...")

scene_data = scene_data["scenes"][list(scene_data["scenes"].keys())[0]]

assets = []

for i in scene_data["assets"].keys():
	assets.append({"id": i, "type": scene_data["assets"][i]["type"]})

print("Downloading assets...")

downloaded_assets = []

for i in assets:
	if i["type"] != "image/webp":
		print("Unknown asset type: \"" + i["type"] + "\"")
		continue

	print("Downloading asset:", i["id"])
	
	for j in [1024, 512, 128, 64]:
		response = download_image_asset(scene_url, i["id"], j)

		if response.status_code == 403:
			continue

		downloaded_assets.append({"name": i["id"] + "-" + str(j) + ".webp", "data": response.content})

print("Creating output file...")

with zipfile.ZipFile(parsed_scene_url.fragment + ".zip", "w") as f:
	f.writestr(parsed_scene_url.fragment + ".json", json_response.content)

	for i in downloaded_assets:
		f.writestr(i["name"], i["data"])

success(scene_url)