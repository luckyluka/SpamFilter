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
#from nltk.stem.lancaster import LancasterStemmer

#from nltk.tokenize import RegexpTokenizer

#toker = RegexpTokenizer(r'((?<=[^\w\s])\w(?=[^\w\s])|(\W))+', gaps=True)


filet = open("word_test.txt","a")

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


conn = sqlite3.connect("test.db")
c = conn.cursor()


print "DB opened successfully"

c.execute('''CREATE TABLE IF NOT EXISTS DICTIONARY
       (ID INT PRIMARY KEY  NOT NULL,
        WORD     TEXT UNIQUE NOT NULL,
        N               INT NOT NULL,
        NS              INT NOT NULL,
        NL              INT NOT NULL,
        WM              INT NOT NULL,
        WIS             INT NOT NULL, 
        WP              INT NOT NULL,
        MI              INT NOT NULL);''')
print "Table created successfully";

#conn.text_factory = str
emails = [os.path.join("/home/luka/Documents/data2/denemovse/metodologija/all_data/ready",f) for f in os.listdir("/home/luka/Documents/data2/denemovse/metodologija/all_data/ready")]    



for mail in emails: 
    print mail
    
    mailcheck = mail[-5:-4]
    
    print "MAIL NUMBER:", number_mails  
    
    
    if mailcheck == "H":
        print "this mail is HAM"
        number_ham_mails = number_ham_mails + 1
        actval = 0
    elif mailcheck == "S":
        print "this mail is SPAM"
        number_spam_mails = number_spam_mails + 1
        actval = 1
    else:
        pass

        
    with open(mail) as m:     
    #################### WORD PROCESSING ##################################################

        for i,line in enumerate(m):
            words = line.split() 
            for word in words:

                print "MAIL NUMBER#: ", number_mails

                ############ INCREMENT WORD COUNTER #####################
                words_in_mail = words_in_mail + 1
                #########################################################
                word = word.decode("utf-8")
                word = word.lower()
                print word
                #word = toker.tokenize(word)
                #word = word.translate(None, string.punctuation)


            
                word = re.sub(r'[^\w\s]','',word)

                
                #cleanr = re.compile('<.*?>')
                #word = re.sub(cleanr, '', word)
                
                ########### DELIMITER CONDITIONS ########################
                if word == ">" or word =="|" or word =="{" or word == "}" or word == ">>" or word == "[" or word == "]" \
                or word == "#" or word == "*" or word == "-" or word == "<a" or word == "/>" or word == "</tr>"\
                or word == "<td" or word == "--" or word == "<p" or word == "<TR>" or word =="<TD" or word == "<tr>" or word == "=":
                    continue
                    
                print "WORD: ", word

                ##### CHECK IF WORD EXIST AND INSERT IF NOT EXISTS############
                count = c.execute("SELECT count(*) FROM DICTIONARY WHERE WORD = ?", (word,))
                for row in count:
                    test = row[0]
 
                #print "TEST: ", test   
                if test == 0:
                    print "NEW WORD"
                    ################## START WITH ONE FOR ZERO DIVISION REASONS ############
                    

                    if actval == 0:
                        print "ACTVAL:0"
                        ns = 0
                        nl = 1
                        n = 1
                        c.execute("INSERT OR IGNORE INTO DICTIONARY (ID,WORD,N,NS,NL, WM, WIS, WP, MI) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (idn, word, n, ns, nl, 1, 0, 0, 0));
                    else:
                        print "ACTVAL:1"
                        ns = 1
                        nl = 0
                        n = 1
                        c.execute("INSERT OR IGNORE INTO DICTIONARY (ID,WORD,N,NS,NL, WM, WIS, WP, MI) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (idn, word, n, ns, nl, 1, 0, 0, 0));
                    conn.commit()
                    ### INDEX INCREMENT##
                    idn = idn + 1

                    spamprob = float(number_spam_mails / number_mails)  ### PROBABILITY OF MAIL BEING A SPAM MAIL
                    hamprob = float(number_ham_mails / number_mails)

                    
                    wordinspamprob = float(ns / n) #### PROBABILITY OF WORD BEING IN A SPAM MAIL

                    wordinhamprob = float(nl / n) #### PROBABILITY OF WORD BEING IN A SPAM MAIL
                    
                    #filet.write("%s, %s, %s, %s,   INSERT\n" %(word, ns, number_mails, wordinspamprob))
                    
                    wordprob = wordinspamprob * spamprob + wordinhamprob * hamprob  ##### PROBABILITY OF WORD APPEARING IN A MAIL
                 
                    print mail
                    

                    ###################### UPDATE PROB DATA ########################################


                    c.execute("UPDATE DICTIONARY SET WIS = ? WHERE WORD=?", (wordinspamprob, word))
                    c.execute("UPDATE DICTIONARY SET WP = ? WHERE WORD=?", (wordprob, word))
                

                    conn.commit()

               


                    ####################### MI INDEX CALC ######################
                    print wordprob
                    print spamprob
                    print wordinspamprob
                    try:
                        mi = math.log((wordinspamprob)/(wordprob*spamprob))
                    except Exception as e:
                        mi = 0
                    

                    c.execute("UPDATE DICTIONARY SET MI = ? WHERE WORD=?", (mi, word))
                    
                    conn.commit()
                else:
                    print "KNOWN WORD"
                    pass
                    #print "known word-----------------------------"
                ################### mark that word is in message ###############################
                

                get_data = c.execute("SELECT WM FROM DICTIONARY WHERE WORD = ?", (word,))
                foc = 0
                for data in get_data:
                    foc = data[0]

        
                #######################################################################################



                ########## UPDATE STATS FOR WORD ############################### do not increment if word already appeared in mail
                if foc == 0:
                    print "WORD PRESENT IN CURRENT MAIL FOR THE FIRST TIME"
                    c.execute("UPDATE DICTIONARY SET WM = ? WHERE WORD=?", (1, word))
                    conn.commit()
                    #### GET STATS FOR WORD################################################################
                    get_data  = c.execute("SELECT N, NS, NL, COUNT(N) FROM DICTIONARY WHERE WORD = ?", (word,))
                    
                    word_frequency = 0
                    spam_word_frequency = 0
                    ham_word_frequency = 0
                    
                    for data in get_data:
                        
                        word_frequency = data[0]
                        spam_word_frequency = data[1]
                        ham_word_frequency = data[2]
                        word_count = data[3]

                    print word_frequency
                    print spam_word_frequency
                    print ham_word_frequency

                    ns = spam_word_frequency
                    nl = ham_word_frequency

                    n = word_frequency + 1
                    c.execute("UPDATE DICTIONARY SET N = ? WHERE WORD=?", (n, word))
                    
                    if mailcheck == "S":
                        
                        ns = ns + 1
                        c.execute("UPDATE DICTIONARY SET NS = ? WHERE WORD=?", (ns, word)) 
                        print "spam"
                    
                    elif mailcheck == "H":
                        
                        nl = nl + 1
                        c.execute("UPDATE DICTIONARY SET NL = ? WHERE WORD=?", (nl, word))
                        print "ham"
                    else:
                        pass
                    ################################################################
                    conn.commit()


                    spamprob = float(number_spam_mails / number_mails)  ### PROBABILITY OF MAIL BEING A SPAM MAIL
                    hamprob = float(number_ham_mails / number_mails)
                    print "ns:", ns
                    print "number mails:", number_mails
                    wordinspamprob = float(ns / n) #### PROBABILITY OF WORD BEING IN A SPAM MAIL
                    
                    wordinhamprob = float(nl / n) #### PROBABILITY OF WORD BEING IN A SPAM MAIL

                    #filet.write("%s, %s, %s, %s,   UPDATE\n" %(word, ns, number_mails, wordinspamprob))
                    
                    wordprob = wordinspamprob * spamprob + wordinhamprob * hamprob   ##### PROBABILITY OF WORD APPEARING IN A MAIL
                    
                    print word_frequency
                    print spam_word_frequency
                    print ham_word_frequency

                    

                    ###################### UPDATE PROB DATA ########################################


                    c.execute("UPDATE DICTIONARY SET WIS = ? WHERE WORD=?", (wordinspamprob, word))
                    c.execute("UPDATE DICTIONARY SET WP = ? WHERE WORD=?", (wordprob, word))
                

                    conn.commit()

               


                    ####################### MI INDEX CALC ######################
                    print wordprob
                    print spamprob
                    print wordinspamprob
                    try:
                        mi = math.log((wordinspamprob)/(wordprob*spamprob))
                    except Exception as e:
                        mi = 0
                    

                    c.execute("UPDATE DICTIONARY SET MI = ? WHERE WORD=?", (mi, word))
                    conn.commit()
                else:
                    print "WORD ALREADY PRESENT IN MAIL"
    #raw_input("ustav")                
    ################################################################
    ################### CALCULATE PROBS ###########################
    print "###################################################################"
    print "#################ACTUAL PROBABILITY CALCULATION ###################"
    print "###################################################################"
    get_data  = c.execute("SELECT WIS, WP, MI FROM DICTIONARY  WHERE WM = ? ORDER BY MI DESC LIMIT 60 ", (1,))        
    
    all_word_in_spam_probs = 1
 

    mi_list_prob = []
    mi_list_word_prob = []

    for data in get_data:            
        all_word_in_spam_probs = data[0]
        all_word_probs = data[1]
        
        #all_mis = data[2]
        #print all_mis

        if all_word_probs == 0:
            all_word_probs = 1

        if all_word_in_spam_probs == 0:
            all_word_in_spam_probs = 1
        

        ##joint_prob = joint_prob * all_word_in_spam_probs
        ##joint_word_prob = joint_word_prob * all_word_probs
        #perhaps an array 
        mi_list_prob.append(all_word_in_spam_probs)
        mi_list_word_prob.append(all_word_probs)
        
        
    print mi_list_prob
    print "################"
    print mi_list_word_prob

    result_joint_prob = np.prod(np.array(mi_list_prob))
    result_joint_word_prob = np.prod(np.array(mi_list_word_prob))

    print "##############"
    print result_joint_prob
    print result_joint_word_prob
    print "##############"
    #print joint_prob
    #print joint_word_prob
    print "##############"
    #if joint_word_prob == 0:
    #    joint_word_prob = 1
    
    print "##############"
    print words_in_mail
    print number_mails
    print "##############"
    
    total_prob = (spamprob * result_joint_prob )/ result_joint_word_prob

    #print "j_prob:",joint_prob
    #print "J_w_prob:",joint_word_prob
    print total_prob
    #file = open("tot_prob.txt","a")
    #file.write("%s, %s, %s, %s\n" %(total_prob, spamprob, result_joint_prob, result_joint_word_prob))

    #inp = raw_input("PRESS ANY KEY TO CONTINUE")
    #raw_input("PRESS ANY KEY TO CONTINUE")

    if total_prob < 0.5:
        predval = 0
    elif total_prob > 0.5:
        predval = 1



    file = open("eff.txt","a")


    if predval == actval:
        print "HIT"
        counthit = counthit + 1
        
    else:
        print "MISS"
        countmiss = countmiss + 1
        

    eff = float(counthit/number_mails)

    file.write("%s\n" %eff)
    print "predval:", predval
    print "actval:", actval
    print "counthit:", counthit
    print "countmiss:", countmiss

    

    print words_in_mail
    ###### RESET WORDS IN MAIL COUNTER ##############
    words_in_mail = 0
    #################################################
        
    ######### INCREMENT MAIL COUNTER ##############
    number_mails = number_mails + 1
    ###############################################




    c.execute("UPDATE DICTIONARY SET WM = ? WHERE WM = ?", (0,1))        
    conn.commit()
    #raw_input("ustav")

        # add correctness check: whether filter was right or wrong
    print "############################################################################"

print "HIT ACCURACY: ",  counthit/number_mails