import os, sys
import subprocess
import json
import re
from urllib.request import urlretrieve
from tqdm import tqdm
from bs4 import BeautifulSoup
import urllib3

from ascii_magic import AsciiArt
import base64
import requests

# Problems:
	# some urls are not correctly fetched
	# some websites reject the connection
	
# maybe a better way is downloading the webarchive file, 
# then retrieve information from that 

url = str(sys.argv[1])
print("Target url: ", url)

print("Parsing the url ...")
process = os.popen('mercury-parser ' + url + ' --header.User-Agent="Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1"')
response = process.read()
process.close()

print("Getting title...")
res_dict = json.loads(response)
title = res_dict['title']
# get rid of special charcters in title
title = title.replace(" ", "_")
title = title.replace("/", "_")
title = re.sub('[（）()：:?？,.，。【】｜丨|]+', '', title)
print(title)

# Make a directory for all the files
print("Creating directory...")
cwd = os.getcwd()
dir_path = os.path.join(cwd, title)
if not os.path.exists(dir_path):
	os.mkdir(dir_path)

# recover the img links
print("Fixing image links...")
content = res_dict['content']
content.replace('\\"', '')

# find all the patterns
print("Retrieving image links...")
soup = BeautifulSoup(content, 'html.parser')

img_urls = []
for img_tag in tqdm(soup.find_all('img')):
	img_url = img_tag.get('src')

	if img_url[0] == '/':
		url_parts = url.split('/')
		len_host_url = len(url_parts[0]) + len(url_parts[2]) + 2
		host_url = url[:len_host_url]
		img_url = host_url + img_url
		print(img_url)
	img_urls.append(img_url)
	
	img_name = img_url.split('/')[-1]

	# using cacaview
	'''
	tmp_img_path = './{}'.format(img_name)
	response = requests.get(img_url)
	with open(tmp_img_path, 'wb') as f:
		f.write(response.content)
	process = subprocess.Popen('cacaview {}'.format(tmp_img_path), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
	ascii_art, error = process.communicate()
	#print(ascii_art.decode())
	htmlStr = "<pre>\n {} </pre>\n".format(ascii_art.decode())
	'''
	
	ascii_art = AsciiArt.from_url(img_url)
	htmlStr = "<pre>\n {} </pre>\n".format(ascii_art.to_html(columns=200, width_ratio=2, monochrome=False))
	tmp_soup = BeautifulSoup(htmlStr, 'html.parser')
	tmp_tag = tmp_soup.find('pre')
	img_tag.insert_after(tmp_tag)

	img_tag.decompose()

	
'''
# Making images directory
print("Creating images directory...")
img_path = os.path.join(dir_path, 'images')
if not os.path.exists(img_path):
	os.mkdir(img_path)

# process image links
print("Processing images...")
for url in tqdm(img_urls_whole):
	#retrieve local path from url
	local_url = url.split('//')[-1] # get rid of "http(s)://"
	local_url = local_url.split('?')[0]
	local_url = local_url.replace('/', '_')
	local_url = local_url.replace('=', '.')
	local_url = local_url.replace('%', '_')
	img_file_path = os.path.join(img_path, local_url)
	try:
		urlretrieve(url, img_file_path)
	except Exception as e:
		print(e)
		continue
	# replace all the patterns
	#content = content.replace(url, "images/"+local_url)
'''

# write to temp html file
html_path = os.path.join(dir_path, title+".html")
f = open(html_path, "w")
f.write(str(soup))
f.close()

# convert to org-mode
print("Converting to txt file...")
org_path = os.path.join(dir_path, title + ".txt")
process = os.popen('pandoc -o ' + org_path + ' -f html -t plain ' + html_path)
response = process.read()
process.close()

# delete html File
#print("Deleting temp html file...")
#if os.path.exists(html_path):
#	os.remove(html_path)
	
print("All done.\n")
