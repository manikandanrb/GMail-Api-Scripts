from processEmail import filter_messages, perform_actions
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

def test_process_email():
    data = {
        "rule_id": 1,
        "description": "rule_1",
        "conditions": {
            "condition_predicate": "all",
            "rules": [
                {
                    "field_name": "from",
                    "predicate": "contains",
                    "value": "happyfox"                
                },
                {
                    "field_name": "subject",
                    "predicate": "contains",
                    "value": "application"                
                },
                {
                    "field_name": "date_received",
                    "predicate": "is_less_than",
                    "value": "2"                
                }
            ]
        },
        "actions": [
            {
                "action": "move_message",
                "to_mailbox": "inbox"
            },
            {
                "action": "mark_as_read"
            }
        ]
    }

    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('gmail', 'v1', http=creds.authorize(Http()))

    message_ids = ['16ffa01975649b7d', '16fed4aacabe52f2', '16fed3d54eb852af']
    assert filter_messages(data) == message_ids
    assert perform_actions(message_ids, data['actions'], service) == True