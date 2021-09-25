import os, sys
import json
import re
from urllib.request import urlretrieve
from tqdm import tqdm
from bs4 import BeautifulSoup
import urllib3
from shutil import copyfile, move

# get the archive path
archive_path = str(sys.argv[1])
print("input file: ", archive_path)

# get archive name and directory
archive_name = archive_path.split('/')[-1]
len_arvhive_name = len(archive_name)
archive_directory = archive_path[:-len_arvhive_name]

# rename the archive name, replace all the blanks with _s
archive_name = archive_name.replace(' ', '_')
os.rename(archive_path, archive_directory + archive_name)

# create a temp directory 
temp_directory = os.path.join(archive_directory, 'temp')
if not os.path.exists(temp_directory):
	os.mkdir(temp_directory)
	
## then move the webarchive in temp directory
archive_path = os.path.join(archive_directory, archive_name)
new_archive_path = os.path.join(temp_directory, archive_name)
copyfile(archive_path, new_archive_path) # copy OR move
#os.rename(archive_path, new_archive_path)

# convert archive into files
process = os.popen('textutil -convert html ' + new_archive_path)
response = process.read()
process.close()

html_name = new_archive_path.split('/')[-1].split('.')[0] + '.html'

# run the simple http server
pss = os.popen('python -m http.server &')
pss.close()

print("Parsing the url ...")
process = os.popen('mercury-parser ' + 'http://localhost:8000/' + 'temp/' + html_name)
response = process.read()
process.close()

# Parsing
print("Getting title...")
res_dict = json.loads(response)
title = res_dict['title']
# get rid of special charcters in title
title = title.replace(" ", "")
title = title.replace("/", "_")
title = re.sub('[（）()：:?？,.，。【】｜丨||""“”]+', '', title)

content = res_dict['content']

# find all the patterns
print("Retrieving image links...")
soup = BeautifulSoup(content, 'html.parser')
img_urls = []
for img_tag in soup.find_all('img'):
	img_urls.append(img_tag.get('src'))

# Making images directory
print("Creating images directory...")
#img_path = os.path.join(dir_path, 'images')
#if not os.path.exists(img_path):
#	os.mkdir(img_path)
# preocess image links
print("Processing images...")
for url in tqdm(img_urls):
	print(url)
	#retrieve local path from url
	local_url = url.split(':')[-1] # get rid of "http(s)://"
	local_url = local_url.split('?')[0]
	local_url = local_url.replace('///', '')
	local_url = local_url.replace('=', '.')
	
#	img_file_path = os.path.join(img_path, local_url)
	print(local_url)
	# replace all the patterns
	content = content.replace(url, local_url)

# write to temp html file
html_path = os.path.join(temp_directory, title + ".html")
f = open(html_path, "w")
f.write(content)
f.close()

# convert to org-mode
print("Converting to org file...")
org_path = os.path.join(temp_directory, title + ".org")
process = os.popen('pandoc -o ' + org_path + ' -f html -t org ' + html_path)
response = process.read()
process.close()

# delete html File
#print("Deleting temp html file...")
#if os.path.exists(html_path):
#	os.remove(html_path)
	
# remove extracted html and archive 
os.remove(os.path.join(temp_directory, html_name))
os.remove(new_archive_path)

# change temp directory name to title
os.rename(temp_directory, os.path.join(archive_directory, title))

# shutdown the httpserver
process = os.popen("ps -ef |grep http.server |grep python |awk '{print $2}' | xargs kill -9")
response = process.read()
process.close()

# move the result to ~/notes
#move(os.path.join(archive_directory, title), "/Users/hanying/notes/")
	
print("All done.\n")
