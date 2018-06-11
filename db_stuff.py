import sqlite3

conn = sqlite3.connect("./yt-captions.db")
# conn.execute('''create table youtube (url varchar2(50),
#                      lasttimestamp varchar2(50),
#                      captionsd varchar2(500));''')
cursor = conn.cursor()
cursor.execute('''select * from youtube;''')
for row in cursor:
    # row[0] returns the first column in the query (name), row[1] returns email column.
    print('{0} : {1}, {2}'.format(row['url'], row['lasttimestamp'], row['captionsd']))
