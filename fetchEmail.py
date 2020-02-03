from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import time
import pandas as pd
import pymysql
from sqlalchemy import create_engine
import dateutil.parser as parser
from datetime import datetime
import datetime

SCOPES = 'https://www.googleapis.com/auth/gmail.modify'
user = 'root'
pword = 'root'
database = 'script'
table_name = 'TestEmails'

def main():
   
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('gmail', 'v1', http=creds.authorize(Http()))
    
    try:
        # Call the Gmail API to fetch INBOX
        results = service.users().messages().list(userId='me',labelIds = ['INBOX']).execute()
        messages = []
        if 'messages' in results:
            messages.extend(results['messages'])

        while 'nextPageToken' in results:
            page_token = results['nextPageToken']
            results = service.users().messages().list(userId='me',
                                                        labelIds = ['INBOX'],
                                                        pageToken=page_token).execute()
            messages.extend(results['messages'])
            print(len(messages))

    except errors.HttpError, error:
        print 'An error occurred: %s' % error


    final_list = [ ]
    if not messages:
        print "No messages found."
    else:
        print "Message snippets:"
        for mssg in messages:
            temp_dict = { }
            m_id = mssg['id'] # get id of individual message
            temp_dict['Message_id'] = m_id
            message = service.users().messages().get(userId='me', id=mssg['id']).execute() # fetch the message using API
            payld = message['payload'] # get payload of the message 
            headr = payld['headers'] # get header of the payload

            for one in headr: # getting the Subject
                if one['name'] == 'Subject':
                    msg_subject = one['value']
                    temp_dict['Subject'] = msg_subject
                else:
                    pass

            for two in headr: # getting the date
                if two['name'] == 'Date':
                    msg_date = two['value']
                    try:
                        date_parse = (parser.parse(msg_date))
                    except:
                        pass
                    m_date = (date_parse.date())
                    temp_dict['Date'] = str(m_date)
                else:
                    pass

            for three in headr: # getting the Sender
                if three['name'] == 'From':
                    msg_from = three['value']
                    temp_dict['Sender'] = msg_from
                else:
                    pass

            temp_dict['Snippet'] = message['snippet'] # fetching message snippet

            # service.users().messages().modify(userId='me', id=m_id,body={'removeLabelIds': [], 'addLabelIds': ['UNREAD', 'INBOX']}).execute()
            final_list.append(temp_dict)
    
    engine = create_engine('mysql+pymysql://%s:%s@localhost:3306/%s' %(user, pword, database), echo = False)
    df = pd.DataFrame(final_list)
    df.to_sql(table_name, con = engine, if_exists = 'append', index = False)

if __name__ == '__main__':
    main()
