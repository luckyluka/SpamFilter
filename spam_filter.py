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
        WM              INT NOT NULL,
        WIS             INT NOT NULL, 
        WP              INT NOT NULL);''')
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
                    
                    ################## START WITH ONE FOR ZERO DIVISION REASONS ############
                    n = 1
                    nl = 1
                    ns = 1

                    
                    c.execute("INSERT OR IGNORE INTO DICTIONARY (ID,WORD,N,NS,NL, PWS, WM, WIS, WP) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (idn, word, n, nl, ns, word_spam_prob, "0", "0", "0"));
                    ### INDEX INCREMENT##
                    idn = idn + 1
                    
                conn.commit()
                
                #### GET STATS FOR WORD######
                get_data  = c.execute("SELECT N, NS, NL FROM DICTIONARY WHERE WORD = ?", (word,))
                
                word_frequency = 0
                spam_word_frequency = 0
                ham_word_frequency = 0
                
                for data in get_data:
                    
                    word_frequency = data[0]
                    spam_word_frequency = data[1]
                    ham_word_frequency = data[2]
                                      
                ########## UPDATE STATS FOR WORD ###############################
                
                n = word_frequency + 1
                if mailcheck == "S":
                    ns = spam_word_frequency + 1 
                else:
                    nl = ham_word_frequency + 1

                
                
                c.execute("UPDATE DICTIONARY SET N = ? WHERE WORD=?", (n, word))
                c.execute("UPDATE DICTIONARY SET NS = ? WHERE WORD=?", (ns, word))
                c.execute("UPDATE DICTIONARY SET NL = ? WHERE WORD=?", (nl, word))

                if mailcheck == "H":
                    c.execute("UPDATE DICTIONARY SET WM = ? WHERE WORD=?", ("0", word))
                else:
                    c.execute("UPDATE DICTIONARY SET WM = ? WHERE WORD=?", ("1", word))
                
                conn.commit()

                
                
                ############## GET WORD STATS AFTER UPDATE ###################################
                get_data = c.execute("SELECT N, NS, NL FROM DICTIONARY WHERE WORD = ?", (word,))
                for data in get_data:
                    
                    word_frequency = data[0]
                    spam_word_frequency = data[1]
                    ham_word_frequency = data[2]                    


                ################# BAYES - CALCULATE PROBABILITIES ###############################

                try:
                    spamprob = float(number_spam_mails / number_mails)
                    print "spam prob:", spamprob
                except ZeroDivisionError:
                    spamprob = 0
                    print "err"

                try:
                    wordinspamprob = float(ns / number_mails)
                    print "word in spam prob:", wordinspamprob
                except ZeroDivisionError:
                    wordinspamprob = 0
                    print "err"

                try:
                    wordprob =float(n / number_mails)
                    print "word prob:", wordprob
                except ZeroDivisionError:
                    wordprob = 0
                    print "err"

                try:
                    word_spam_prob = float(spamprob * wordinspamprob) / wordprob
                    print "SPAM PROBABILITY GIVEN WORD:", word_spam_prob
                except ZeroDivisionError:
                    word_spam_prob = 0
                    print "err"
                
                ###################### UPDATE PROB DATA ########################################
                c.execute("UPDATE DICTIONARY SET PWS = ? WHERE WORD=?", (word_spam_prob, word))
                c.execute("UPDATE DICTIONARY SET WM = ? WHERE WORD=?", ("1", word))
                c.execute("UPDATE DICTIONARY SET WIS = ? WHERE WORD=?", (wordinspamprob, word))
                c.execute("UPDATE DICTIONARY SET WP = ? WHERE WORD=?", (wordprob, word))

                conn.commit()
                
                
                
                
                
        print words_in_mail
        ###### RESET WORDS IN MAIL COUNTER ##############
        words_in_mail = 0
        #################################################


        get_data  = c.execute("SELECT WIS, WP FROM DICTIONARY WHERE WM = ?", ("1",))        
        
        all_word__in_spam_probs = 0
        all_word_probs = 0
        joint_prob = 1
        joint_word_prob = 1
        
        for data in get_data:            
            all_word_in_spam_probs = data[0]
            all_word_probs = data[1]
 
            

            joint_prob = joint_prob * all_word_in_spam_probs
            joint_word_prob = joint_word_prob * all_word_probs
    

        total_prob = joint_prob / joint_word_prob
        print "mail number:", number_mails  
        print "TOTAL PROBABILITY:", total_prob

        c.execute("UPDATE DICTIONARY SET WM = ? WHERE WM = ?", ("0","1"))        
        conn.commit()

        # add correctness check: whether filter was right or wrong

print "Records created succesfull"


# add count all spam/ham words in mail
# 