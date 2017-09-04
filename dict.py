from __future__ import division
import os
from collections import Counter
import pprint
import itertools
import pandas as pd
import numpy as np


import sqlite3
conn = sqlite3.connect("test.db")
c = conn.cursor()
print "DB opened successfully"

c.execute('''CREATE TABLE IF NOT EXISTS DICTIONARY
       (ID INT PRIMARY KEY  NOT NULL,
        WORD     TEXT UNIQUE NOT NULL,
        N               INT NOT NULL,
        NS              INT NOT NULL,
        NL              INT NOT NULL,
        PWS             INT NOT NULL,
        WM              INT NOT NULL);''')
print "Table created successfully";

conn.text_factory = str
emails = [os.path.join("/home/luka/Documents/data2/denemovse/metodologija/small_sample",f) for f in os.listdir("/home/luka/Documents/data2/denemovse/metodologija/small_sample")]    
all_words = []   
mailnumber = 1
words_in_mail = 0
number_mails = 0
number_spam_mails = 0
number_ham_mails = 0

word_spam_prob = 0

n = 0
nl = 0
ns = 0
idn = 1    
sth = 0
for mail in emails: 
    
    ######### INCREMENT MAIL COUNTER ##############
    number_mails = number_mails + 1
    ###############################################

    mailcheck = mail[-5:-4]
    
    print mail
    print "MAIL:",mailcheck
    if mailcheck == "H":
        print "this mail is HAM"
    else:
        print "this mail is SPAM"


    with open(mail) as m: 

        ############### CHECK IF MAIL IS HAM OR SPAM #################################   
        
        if mailcheck == "H":
            number_ham_mails = number_ham_mails + 1
        else:
            number_spam_mails = number_spam_mails + 1

        
        #################### WORD PROCESSING ##################################################
        
        for i,line in enumerate(m):
            words = line.split() 
            for word in words:

                ############ INCREMENT WORD COUNTER #####################
                words_in_mail = words_in_mail + 1
                #########################################################
                word = word.lower()
                
                ########### DELIMITER CONDITIONS ########################
                if word == ">" or word =="|" or word =="{" or word == "}" or word == ">>" or word == "[" or word == "]" or word == "#" or word == "*" or word == "-" or word == "<a" or word == "/>" or word == "</tr>" or word == "<td" or word == "--" or word == "<p" or word == "<TR>" or word =="<TD" or word == "<tr>" or word == "=":
                    continue
                    
                print "WORD: ",word
                
                ##### CHECK IF WORD EXIST AND INSERT IF NOT EXISTS############
                count = c.execute("SELECT count(*) FROM DICTIONARY WHERE WORD = ?", (word,))
                for row in count:
                    test = row[0]
                    
                if test == 0:
                    n = 0
                    nl = 0
                    ns = 0
                    
                    c.execute("INSERT OR IGNORE INTO DICTIONARY (ID,WORD,N,NS,NL, PWS, WM) VALUES (?, ?, ?, ?, ?, ?, ?)", (idn, word, n, nl, ns, word_spam_prob, "0"));
                    idn = idn + 1
                    
                conn.commit()
                
                #### GET STATS FOR WORD######
                check = c.execute("SELECT N, NS, NL FROM DICTIONARY WHERE WORD = ?", (word,))
                number = 0
                numberspam = 0
                numberlegitimate = 0
                for row2 in check:
                    
                    number = row2[0]
                    numberspam = row2[1]
                    numberlegitimate = row2[2]
                                      
                ########## UPDATE STATS FOR WORD ###############################
                
                n = number + 1
                if mailcheck == "S":
                    ns = numberspam + 1 
                else:
                    nl = numberlegitimate + 1
                
                
                c.execute("UPDATE DICTIONARY SET N = ? WHERE WORD=?", (n, word))
                c.execute("UPDATE DICTIONARY SET NS = ? WHERE WORD=?", (ns, word))
                c.execute("UPDATE DICTIONARY SET NL = ? WHERE WORD=?", (nl, word))
                conn.commit()

                number2 = 0
                numberspam2 = 0
                numberlegitimate2 = 0
                
                ############## GET WORD STATS AFTER UPDATE ###################################
                check2 = c.execute("SELECT N, NS, NL FROM DICTIONARY WHERE WORD = ?", (word,))
                for row3 in check2:
                    number2 = row3[0]
                    numberspam2 = row3[1]
                    numberlegitimate2 = row3[2]                    


                ################# BAYES - CALCULATE PROBABILITIES ###############################

                try:
                    spamprob = float(number_spam_mails / number_mails)
                except ZeroDivisionError:
                    spamprob = 0

                try:
                    wordinspamprob = float(ns / number_mails)
                except ZeroDivisionError:
                    wordinspamprob = 0

                try:
                    wordprob =float(n / number_mails)
                except ZeroDivisionError:
                    wordprob = 0

                try:
                    word_spam_prob = float(spamprob * wordinspamprob) / wordprob
                except ZeroDivisionError:
                    word_spam_prob = 0
                
                ###################### UPDATE PROB DATA ########################################
                c.execute("UPDATE DICTIONARY SET PWS = ? WHERE WORD=?", (word_spam_prob, word))
                c.execute("UPDATE DICTIONARY SET WM = ? WHERE WORD=?", ("1", word))
                conn.commit()

                n = number2
                ns = numberspam2
                nl = numberlegitimate2                
                
                
                
        print words_in_mail
        ###### RESET WORDS IN MAIL COUNTER ##############
        words_in_mail = 0
        
        print "mail number:", number_mails        
    

print "Records created succesfull"

    # ##################################
    #     dictionary = Counter(all_words)
    #     list_to_remove = dictionary.keys()
    #     for item in list_to_remove:
    #     	if item.isalpha() == False: 
    #     		del dictionary[item]
    #     	elif len(item) == 1:
    #     		del dictionary[item]
    #     	elif item == '>':
    #     		del dictionary[item]
    #     dictionary = dictionary.most_common(3000)
    ###################################################
    # for word in mail_words:
    #     for key, value in dictionary:
    #         print key
    #         print word
    #         if key == word:
    #             print "it is the same!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"

# pprint.pprint(Counter(all_words).most_common(1000))
# print "------------------------------------------"
# print "mail: ", mailcount
# print "##########################################"
# mailcount = mailcount + 1
