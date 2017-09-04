from os import listdir, rename
from os.path import isfile, join

import os

onlyfiles = [f for f in listdir("/home/luka/Documents/data2/denemovse/metodologija/all_data/TRAINING_NEW") if isfile(join("/home/luka/Documents/data2/denemovse/metodologija/all_data/TRAINING_NEW", f))]

onlyfiles.sort()


count = 0


with open("/home/luka/Documents/data2/denemovse/metodologija/all_data/SPAMTrain.label") as f:
  
	while True:
		a = f.readline()

	   	if not a:
	   		print "end of file"
	   		break

	   	print onlyfiles[count]
		print a
		

		filepath = "/home/luka/Documents/CSDMC2010_SPAM/CSDMC2010_SPAM/TRAINING_NEW/"+onlyfiles[count]
		

		filepatham = "/home/luka/Documents/data2/denemovse/metodologija/all_data//ham/"+onlyfiles[count]
		filpathspam = "/home/luka/Documents/data2/denemovse/metodologija/all_data//spam/"+onlyfiles[count]
		

		if a[0]=="0":
			print "spam"
			os.rename(filepath, filpathspam)

		if a[0]=="1":
			print "ham"		
			os.rename(filepath,filepatham) 

		print "-----------"
		count = count + 1



