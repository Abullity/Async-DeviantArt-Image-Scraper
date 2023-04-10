import os
import json
import requests 
from concurrent.futures import ThreadPoolExecutor


def request_url(url):
	data = requests.get(url)
	if not data.ok:
		print("[INVALID URL]", url)
		return 
	return data.content


def save_img(full_sized_url, img_n):
	img_data = request_url(full_sized_url)
	if not img_data:
		print("[NO IMAGE DATA] for the image url", full_sized_url)
		return
	with open(f"IMG_{img_n}.jpg", "wb") as img:
		img.write(img_data)


def get_full_size_url(img_url):
	img_url = "https://backend.deviantart.com/oembed?url=" + img_url
	jsoned = json.loads(request_url(img_url))
	full_sized_url = jsoned['url']
	#img_name = jsoned['title']
	if not full_sized_url:
		print("[NO URL ATTRIBUTE]", img_url)
		return
	return full_sized_url
	

def get_urls(username, urls_scraped=0, url_limit = 20):
	try:
		os.mkdir(username)
		os.chdir(username)
	except FileExistsError:
		print("Account already scrapped!")
		return
	while True:
		response = request_url(f"https://www.deviantart.com/_napi/da-user-profile/api/gallery/contents?username={username}&offset={urls_scraped}&limit={url_limit}&all_folder=true")
		if not response:
			print("No such account")
			return
		jsoned = json.loads(response)
		urls_got_count = len(jsoned['results'])
		if not urls_got_count:
			print("All scraped!")
			break
		urls = (get_full_size_url(jsoned['results'][i]['deviation']['url']) for i in range(urls_got_count))
		with ThreadPoolExecutor() as executor:
			executor.map(save_img, urls, range(urls_scraped, urls_scraped+url_limit+1))	
		urls_scraped += urls_got_count