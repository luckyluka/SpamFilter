from os import listdir, rename
from os.path import isfile, join

import os
import io

onlyfiles = [f for f in listdir("/home/luka/Documents/data2/denemovse/metodologija/all_data/joined/") if isfile(join("/home/luka/Documents/data2/denemovse/metodologija/all_data/joined/", f))]

onlyfiles.sort()


# count = 0

for file in onlyfiles:


  	
  	filepath_old = "/home/luka/Documents/data2/denemovse/metodologija/all_data/joined/"+file
  	filepath_new = "/home/luka/Documents/data2/denemovse/metodologija/all_data/ready/"+file

 	
	with io.open(filepath_old,'r',encoding='ISO-8859-15') as f:
	    text = f.read()
	# process Unicode text
	with io.open(filepath_new,'w',encoding='utf8') as f:
	    f.write(text)

 
