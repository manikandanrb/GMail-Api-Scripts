from googleapiclient.discovery import build
from httplib2 import Http
import pandas as pd
import datetime
import pymysql
from sqlalchemy import create_engine
import json
from oauth2client import file, client, tools

SCOPES = 'https://www.googleapis.com/auth/gmail.modify'

RULES_FILE_PATH = 'Rules.json'
user = 'root'
pword = 'root'
database = 'script'
table_name = 'TestEmails'

def must_match_all_rule(data):
    engine = create_engine('mysql+pymysql://%s:%s@localhost:3306/%s' %(user, pword, database), echo = False)
    df = pd.read_sql(table_name, con=engine)
    query_value = ''
    rules = data['conditions']['rules']
    for rule in rules:
        if rule['predicate'] == 'contains':
            query_value += '{0}.str.contains("{1}", case=False) and '.format(rule["field_name"].capitalize() , rule["value"])
        if rule['predicate'] == 'is_less_than':
            query_date = datetime.datetime.now() - datetime.timedelta(days=1)
            date_string = query_date.strftime("%Y-%m-%d") 
            query_value += '(Date < "{0}")'.format(date_string)
    filtered_df = df[['Message_id', 'Sender', 'Subject', 'Date']].query(query_value)
    return filtered_df['Message_id'].to_list()


def atleast_one_rule_must_match(data):
    engine = create_engine('mysql+pymysql://%s:%s@localhost:3306/%s' %(user, pword, database), echo = False)
    df = pd.read_sql(table_name, con=engine)
    query_value = ''
    rules = data['conditions']['rules']
    for rule in rules:
        if rule['predicate'] == 'contains':
            query_value += '{0}.str.contains("{1}", case=False) or '.format(rule["field_name"].capitalize() , rule["value"])
        if rule['predicate'] == 'is_less_than':
            query_date = datetime.datetime.now() - datetime.timedelta(days=1)
            date_string = query_date.strftime("%Y-%m-%d") 
            query_value += '(Date < "{0}")'.format(date_string)
    filtered_df = df[['Message_id', 'Sender', 'Subject', 'Date']].query(query_value)
    return filtered_df['Message_id'].to_list()


def perform_actions(message_ids, actions, service):
    for action in actions:
        if action['action'] == 'move_message':
            to_mailbox = action['to_mailbox']
            for mssg_id in message_ids:
                addLabelIds = [to_mailbox.upper()]
                service.users().messages().modify(userId='me', id=mssg_id ,body={'removeLabelIds': [], 'addLabelIds': addLabelIds}).execute()
        
        if action['action'] == 'mark_as_unread':
            for mssg_id in message_ids:
                service.users().messages().modify(userId='me', id=mssg_id ,body={'removeLabelIds': [], 'addLabelIds': ['UNREAD']}).execute()
        
        if action['action'] == 'mark_as_read':
            for mssg_id in message_ids:
                service.users().messages().modify(userId='me', id=mssg_id ,body={'removeLabelIds': ['UNREAD'], 'addLabelIds': []}).execute()
        
        if action['action'] == 'mark_as_starred':
            for mssg_id in message_ids:
                service.users().messages().modify(userId='me', id=mssg_id ,body={'removeLabelIds': [], 'addLabelIds': ['STARRED']}).execute()


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
        if rule['conditions']['condition_predicate'] == 'all':
            res = must_match_all_rule(rule)
            perform_actions(res, rule['actions'], service)
            print('Success')
        else:
            res = atleast_one_rule_must_match(rule)
            perform_actions(res, rule['actions'], service)
            print('Success')

if __name__ == '__main__':
    main()
