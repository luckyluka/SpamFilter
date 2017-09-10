from __future__ import division
import os
from collections import Counter
import pprint
import itertools
import pandas as pd
import numpy as np
import sqlite3
import math
from heapq import nlargest
import nltk
import re
import time 

start_time = time.time()



all_word_probs = 1
joint_prob = 1
joint_word_prob = 1

wordinspamprob = 0
wordprob = 0
spamprob = 0


total_prob = 0

words_in_mail = 0
number_mails = 1
number_spam_mails = 0
number_ham_mails = 0



n = 0
nl = 0
ns = 0
idn = 1 

mi = 0   
all_mis = 0
inp = 0
mi_list = []
mi_sorted = []
top_mi = 0

predval = 0
actval = 0
countmiss = 0
counthit = 0
undefined = 0
hitpositive = 0
hitnegative = 0
falsepositive = 0
falsenegative = 0

conn = sqlite3.connect("test.db")
c = conn.cursor()
count_words = 0




c.execute('''CREATE TABLE IF NOT EXISTS DICTIONARY
       (ID INT PRIMARY KEY  NOT NULL,
        WORD     TEXT UNIQUE NOT NULL,
        N               INT NOT NULL,
        NS              INT NOT NULL,
        NL              INT NOT NULL,
        WM              INT NOT NULL,
        WIS             INT NOT NULL, 
        WP              INT NOT NULL,
        MI              INT NOT NULL, 
        WIH             INT NOT NULL);''')

emails = [os.path.join("/home/luka/Documents/FAKS/metodologija/all_data/ready",f) for f in os.listdir("/home/luka/Documents/FAKS/metodologija/all_data/ready")]    



for mail in emails: 
    
    mailcheck = mail[-5:-4]
    
    print "MAIL NUMBER:", number_mails  
    
    
    if mailcheck == "H":
        number_ham_mails = number_ham_mails + 1
        actval = 0
    elif mailcheck == "S":
        number_spam_mails = number_spam_mails + 1
        actval = 1
    else:
        pass

        
    with open(mail) as m:     
    #################### WORD PROCESSING ##################################################

        for i,line in enumerate(m):
            words = line.split() 
            for word in words:


                ############ INCREMENT WORD COUNTER #####################
                words_in_mail = words_in_mail + 1
                #########################################################
                word = word.decode("utf-8")
                word = word.lower()
             
            
                word = re.sub(r'[^\w\s]','',word)
                ########### DELIMITER CONDITIONS ########################
                if word == ">" or word =="|" or word =="{" or word == "}" or word == ">>" or word == "[" or word == "]" \
                or word == "#" or word == "*" or word == "-" or word == "<a" or word == "/>" or word == "</tr>"\
                or word == "<td" or word == "--" or word == "<p" or word == "<TR>" or word =="<TD" or word == "<tr>" or word == "=":
                    continue
                    

                ##### CHECK IF WORD EXIST AND INSERT IF NOT EXISTS############
                count = c.execute("SELECT count(*) FROM DICTIONARY WHERE WORD = ?", (word,))
                for row in count:
                    test = row[0]
                    
                
                if test == 0:
                    
                    if actval == 0:
                        ns = 1
                        nl = 2
                        n = 2
                        c.execute("INSERT OR IGNORE INTO DICTIONARY (ID,WORD,N,NS,NL, WM, WIS, WP, MI, WIH) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (idn, word, n, ns, nl, 1, 0, 0, 0, 0));
                    else:
                        ns = 2
                        nl = 1
                        n = 2
                        c.execute("INSERT OR IGNORE INTO DICTIONARY (ID,WORD,N,NS,NL, WM, WIS, WP, MI, WIH) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (idn, word, n, ns, nl, 1, 0, 0, 0, 0));
                    conn.commit()
                    ### INDEX INCREMENT##
                    idn = idn + 1

                    spamprob = float(number_spam_mails / number_mails)  ### PROBABILITY OF MAIL BEING A SPAM MAIL
                    hamprob = float(number_ham_mails / number_mails)
                    wordinspamprob = float(ns / n) #### PROBABILITY OF WORD BEING IN A SPAM MAIL
                    wordinhamprob = float(nl / n) #### PROBABILITY OF WORD BEING IN A SPAM MAIL
                    ###################### UPDATE PROB DATA ########################################
                    c.execute("SELECT COUNT (*) FROM DICTIONARY")
                    nuber_of_words_in_dictionary = c.fetchone()[0]
                    ####################### MI INDEX CALC ######################
                    try:
                        mi = math.log((wordinspamprob)/((2 / nuber_of_words_in_dictionary)*spamprob))
                    except Exception as e:
                        mi = 0
                    c.execute("UPDATE DICTIONARY SET WIS = ?, WIH = ?, MI = ? WHERE WORD=?", (wordinspamprob, wordinhamprob, mi, word))
                    conn.commit()
                else:
                    pass
                ################### mark that word is in message ###############################
                

                get_data = c.execute("SELECT WM FROM DICTIONARY WHERE WORD = ?", (word,))
                foc = 0
                for data in get_data:
                    foc = data[0]

                #######################################################################################
                ########## UPDATE STATS FOR WORD ############################### do not increment if word already appeared in mail
                if foc == 0:
                    #c.execute("UPDATE DICTIONARY SET WM = ? WHERE WORD=?", (1, word))
                    conn.commit()
                    #### GET STATS FOR WORD################################################################
                    get_data  = c.execute("SELECT N, NS, NL FROM DICTIONARY WHERE WORD = ?", (word,))
                    
                    word_frequency = 0
                    spam_word_frequency = 0
                    ham_word_frequency = 0
                    
                    for data in get_data:
                        
                        word_frequency = data[0]
                        spam_word_frequency = data[1]
                        ham_word_frequency = data[2]
                        

                    ns = spam_word_frequency
                    nl = ham_word_frequency
                    n = word_frequency + 1


                    if mailcheck == "S":
                        
                        ns = ns + 1
                        
                    
                    elif mailcheck == "H":
                        
                        nl = nl + 1
                    else:
                        pass


                    spamprob = float(number_spam_mails / number_mails)  ### PROBABILITY OF MAIL BEING A SPAM MAIL
                    hamprob = float(number_ham_mails / number_mails)

                    wordinspamprob = float(ns / n) #### PROBABILITY OF WORD BEING IN A SPAM MAIL
                    wordinhamprob = float(nl / n) #### PROBABILITY OF WORD BEING IN A SPAM MAIL 


                    c.execute("SELECT COUNT (*) FROM DICTIONARY")
                    number_of_words_in_dictionary = c.fetchone()[0]
                    ####################### MI INDEX CALC ######################
                    
                    try:
                        mi = math.log((wordinspamprob)/((n/number_of_words_in_dictionary)*spamprob))
                    except Exception as e:
                        mi = 0

                    c.execute("UPDATE DICTIONARY SET N = ?, NS = ?, NL = ?, WIS = ?, WIH = ?, MI = ?,  WM = ? WHERE WORD=?", (n, ns, nl, wordinspamprob, wordinhamprob, mi, 1,  word))
                    ################################################################
                    conn.commit()
                else:
					pass               
    ################################################################
    ################### CALCULATE PROBS ###########################
    ###################################################################"
    #################ACTUAL PROBABILITY CALCULATION ###################"
    ###################################################################"
    get_data  = c.execute("SELECT WIS, WIH FROM DICTIONARY  WHERE WM = ? ORDER BY MI DESC LIMIT 75 ", (1,))        
    #get_data  = c.execute("SELECT WIS, WIH FROM DICTIONARY  WHERE WM = ?", (1,))        
    
    all_words_in_spam_probs = 1
    all_words_in_ham_probs = 1

    mi_list_prob_spam = []
    mi_list_prob_ham = []

    for data in get_data:            
        all_words_in_spam_probs = data[0]
        all_words_in_ham_probs = data[1]

        if all_words_in_spam_probs == 0:
            all_word_in_spam_probs = 1

        if all_words_in_ham_probs == 0:
            all_words_in_ham_probs = 1

        mi_list_prob_spam.append(all_words_in_spam_probs)
        mi_list_prob_ham.append(all_words_in_ham_probs)

    #print "MI LIST_ham:", mi_list_prob_ham
    #print "MI LIST_spam:", mi_list_prob_spam
    result_joint_prob_spam = np.prod(np.array(mi_list_prob_spam))
    result_joint_prob_ham = np.prod(np.array(mi_list_prob_ham))
    

    try:
    	total_prob = spamprob * result_joint_prob_spam / ((result_joint_prob_spam * spamprob) + (result_joint_prob_ham * hamprob))
    	#total_prob = spamprob * result_joint_prob_spam  / hamprob * result_joint_prob_ham 
    except Exception as e:
    	print "DIVISION BY ZERO"
    
    


    
    ######## TWO WAY ####################

     
    if total_prob >= 0.5:
    	predval = 1
    else:
    	predval = 0
    
    

    ######## THREE_WAY ##################

    #if total_prob > 0.10 and total_prob < 0.90:
    #	predval = 2
    #elif total_prob >= 0.90:
    #	predval = 1
    #elif total_prob <= 0.10: 
    #	predval = 0

    #print "ACTUAL VALUE: ", actval
    #print "PRED VALUE: ", predval
    #print "TOTAL PROB: ", total_prob
    #print "SPAM PROB: ", spamprob
    #print "HAM PROB: ", hamprob
    #print "RESULT JOINT PROB SPAM: ", result_joint_prob_spam
    #print "RESULT JOINT PROB HAM: ", result_joint_prob_ham


    file1 = open("eff1.txt","a")
    #file2 = open("eff2.txt","a")
    #file3 = open("eff3.txt","a")
    file4 = open("tot_p.txt", "a")

    ### 
    ### actval - 0  ham
    ### actval - 1 spam

    if predval == actval:
        counthit = counthit + 1 
        if predval == 1:
        	hitpositive = hitpositive + 1
        else:
        	hitnegative = hitnegative + 1
        print "HIT"

    else:
    	countmiss = countmiss + 1
    	if predval == 1:	
        	falsenegative = falsenegative + 1
        if predval == 0:
        	falsepositive = falsepositive + 1
        if predval == 2:
        	undefined = undefined + 1
        print "MISS"
    #print raw_input("SPACE TO CONTINUE")
    peff = float(counthit/number_mails)
    neff = float(countmiss/number_mails)
    ueff = float(undefined/number_mails)
    
    
    file1.write("%s\n" %peff)
    #file2.write("%s\n" %neff)
    #file3.write("%s\n" %ueff)
    file4.write("%s\n" %total_prob)
       
    ######### INCREMENT MAIL COUNTER ##############
    number_mails = number_mails + 1
    ################################################




    c.execute("UPDATE DICTIONARY SET WM = ? WHERE WM = ?", (0,1))        
    conn.commit()

elapsed_time = time.time() - start_time

print "HIT ACCURACY: ",  counthit/number_mails
print "MISS ACCURACY: ",  countmiss/number_mails
print "UNDECIDED ACCURACY: ",  undefined/number_mails
print "##################"
print "HIT POSITIVE: ", hitpositive/number_mails
print "HIT NEGATIVE: ", hitnegative/number_mails
print "FALSE POSITIVE: ", falsepositive/number_mails
print "FALSE NEGATIVE: ", falsenegative/number_mails

print "TIME ELAPSED: ", elapsed_time/60



print "###########################"
print "# HIT ACCURACY: ",  counthit
print "# MISS ACCURACY: ",  countmiss
print "# UNDECIDED ACCURACY: ",  undefined
print "##################"
print "# HIT POSITIVE: ", hitpositive
print "# HIT NEGATIVE: ", hitnegative
print "# FALSE POSITIVE: ", falsepositive
print "# FALSE NEGATIVE: ", falsenegative