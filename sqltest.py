import sqlite3


conn = sqlite3.connect("testing.db")
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

c.execute("INSERT INTO DICTIONARY (ID,WORD,N,NS,NL, WM, WIS, WP, MI) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)" ,(1, 'lol1', 1, 1, 1, 0, 0, 0, 0));


                    ### INDEX INCREMENT##
conn.commit()


conn.close()