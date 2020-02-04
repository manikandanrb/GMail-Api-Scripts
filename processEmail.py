from googleapiclient.discovery import build
from httplib2 import Http
import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta
import pymysql
from sqlalchemy import create_engine
import json
from oauth2client import file, client, tools

SCOPES = 'https://www.googleapis.com/auth/gmail.modify'

RULES_FILE_PATH = 'Rules.json'
user = 'root'
pword = 'root'
database = 'script'
table_name = 'emails'
condition_predicate = {
    'all': 'AND',
    'any': 'OR'
}

table_field_name = {
    'from': 'Sender',
    'to': 'Receiver',
    'subject': 'Subject'
}

'''
    Filter messages given conditions
'''
def filter_messages(data):
    engine = create_engine('mysql+pymysql://%s:%s@localhost:3306/%s' %(user, pword, database), echo = False)
    rules = data['conditions']['rules']
    condition_operator = condition_predicate.get(data['conditions']['condition_predicate']) 
    query_value = ''
    if len(rules) > 0 :
        query_value += 'SELECT * FROM {0} WHERE '.format(table_name)
        for rule in rules:
            # Contains 
            if rule['predicate'] == 'contains':
                query_value += '{0} LIKE "%%{1}%%" {2} '.format(table_field_name.get(rule["field_name"]), rule["value"], condition_operator)
            
            # Does not contains 
            if rule['predicate'] == 'does_not_contains':
                query_value += '{0} NOT LIKE "%%{1}%%" {2} '.format(table_field_name.get(rule["field_name"]), rule["value"], condition_operator)
            
            # Equals
            if rule['predicate'] == 'equals':
                query_value += '{0} = "{1}" {2} '.format(table_field_name.get(rule["field_name"]), rule["value"], condition_operator)
            
            # Does not equals
            if rule['predicate'] == 'does_not_equals':
                query_value += '{0} != "{1}" {2} '.format(table_field_name.get(rule["field_name"]), rule["value"], condition_operator)

            # Is less than
            if rule['predicate'] == 'is_less_than':
                query_date = datetime.datetime.now() - datetime.timedelta(days=int(rule["value"]))
                date_string = query_date.strftime("%Y-%m-%d") 
                query_value += 'Date < "{0}"'.format(date_string)
            
            # Is greater than
            if rule['predicate'] == 'is_greater_than':
                query_date = datetime.datetime.now() - datetime.timedelta(days=int(rule["value"]))
                date_string = query_date.strftime("%Y-%m-%d") 
                query_value += 'Date > "{0}"'.format(date_string)

                '''
                    Months based query date snippet
                '''
                # query_date = datetime.datetime.now() - datetime.relativedelta(months=int(rule["value"]))
                # date_string = query_date.strftime("%Y-%m-%d") 
                # query_value += 'Date > "{0}"'.format(date_string)
            
    df = pd.read_sql(query_value, con=engine)
    return df['Message_id'].to_list()


'''
    Perform actions condition matched messages
'''
def perform_actions(message_ids, actions, service):
    for action in actions:
        removeLabelIds = []
        addLabelIds = []

        # Move message action 
        if action['action'] == 'move_message':
            to_mailbox = action['to_mailbox']
            addLabelIds = [to_mailbox.upper()]

        # Mark as unread
        elif(action['action'] == 'mark_as_unread'):
            addLabelIds.extend(['UNREAD'])

        # Mark as read
        elif(action['action'] == 'mark_as_read'):
            removeLabelIds.extend(['UNREAD'])

        '''
            Perform action on cloud message using GMail Api services
        '''
        for mssg_id in message_ids:
            service.users().messages().modify(userId='me', id=mssg_id ,body={'removeLabelIds': removeLabelIds, 'addLabelIds': addLabelIds}).execute()

def main():
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('gmail', 'v1', http=creds.authorize(Http()))
    
    with open(RULES_FILE_PATH) as f:
        rules = json.load(f)
    
    for rule in rules:
        #filter messages base on the conditions
        result = filter_messages(rule)
        print('Filter message count- {0}'.format(len(result)))
        #perform actions on these messages
        perform_actions(result, rule['actions'], service)
        print('Success')


if __name__ == '__main__':
    main()
