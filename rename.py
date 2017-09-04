from os import listdir, rename
from os.path import isfile, join

import os

onlyfiles = [f for f in listdir("/home/luka/Documents/data2/denemovse/metodologija/new_test/10/spam/") if isfile(join("/home/luka/Documents/data2/denemovse/metodologija/new_test/10/spam/", f))]

onlyfiles.sort()


# count = 0

for file in onlyfiles:
 	filename = file[0:-4]
 	filepath_new = "/home/luka/Documents/data2/denemovse/metodologija/new_test/"+filename+"S"+".txt"
  	filepath_old = "/home/luka/Documents/data2/denemovse/metodologija/new_test/10/spam/"+file

 	

 	os.rename(filepath_old, filepath_new)




# filepatham = "/home/luka/Documents/CSDMC2010_SPAM/CSDMC2010_SPAM/ham/"+onlyfiles[count]
# filpathspam = "/home/luka/Documents/CSDMC2010_SPAM/CSDMC2010_SPAM/spam/"+onlyfiles[count]







