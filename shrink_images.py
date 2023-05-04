import os

img_dir = '.'

for img in os.listdir(img_dir):
	print(img)
	img_ext = img.split('.')[-1]
	img_name = img[: -len(img_ext)-1]
	print(img_name, img_ext)
	proc = os.popen('ffmpeg -i {} -vf scale="iw/2:ih/2" ./shrink/{}'.format(img, img))
	proc.read()
