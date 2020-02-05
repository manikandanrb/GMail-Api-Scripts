<b>CONDITIONS BASED ON THE ACTIONS TO PERFORM IN GMAIL USING GMAIL API</b>

<b>MYSQL CREATE TABLE QUERY</b>\
create table emails(\
    id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY,\
    Sender TEXT NOT NULL,  
    Receiver TEXT NOT NULL,\
    Date date NOT NULL,\
    Snippet TEXT NOT NULL,\
    Subject TEXT NOT NULL,\
    Message_id TEXT NOT NULL\
);

<b>Subject and Snippet field column data values utfmb4 convert query:</b>\
ALTER TABLE emails CHANGE COLUMN Snippet Snippet TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL;   

<b>Steps to run the scripts:</b>\
1.Clone this repo\
2.Create MYSQL Database and Table as mentioned table name and columns in fetchEmail.py or Use it create table query above.\
3.GMAIL API console configure credentials and download credentials.json file and paste it project directory.\
4.Install relevant dependencies.\
5.Run fetchEmail.py script.\
6.Run processEmail.py script.

<b>Reference</b>: https://developers.google.com/gmail/api/quickstart/python