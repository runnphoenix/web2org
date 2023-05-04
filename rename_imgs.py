import os

target_dir = '/home/chris/Documents/web2org/intro2PG/images'

for file in os.listdir(target_dir):
	if file.endswith('.png'):
		new_name = file.split('_')[-1]
		os.rename(file, 'math/{}'.format(new_name))
