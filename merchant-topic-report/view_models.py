import requests
import json
from collections import Counter
import pandas as pd

#FIXME:put these into environment variables
with open('zendesk_email.txt', 'r') as e:
    email = e.read()

class ReportingPeriod(object):
    def __init__(self, view_id):
        self.view_id = view_id
        self.topic_counts = {}
        self.get_tickets()

    def count_topics(self):
        topics = []
        for ticket in self.tickets:
            topic = ticket['custom_fields'][3]['value']
            if not topic:
                topic = 'unknown'

            topics.append(topic)

        self.topic_counts = dict(Counter(topics).most_common())


        def get_tickets(self):
        """ Function will GET json object for specified view. Zendesk only returns 100 items at a time.
        This function will also 'paginate' to the next page using a 'session' so that all the pages
        are returned as a single json object. Look at json['next_page'] if 'null' if nothing.
        If there is a next page this value will be a url. Then the function loops through
        the responses to get the tickets and adds each ticket as an item in the list call
        tickets. """

        URL = "https://perka.zendesk.com/api/v2/views/" + str(self.view_id) + "/execute.json"

        responses = []

        while URL:
            s = requests.Session()
            r = s.get(URL, auth=(email, os.environ["ZENDESK_PASSWORD"]))
            response = r.json()
            URL = response['next_page']
            responses.append(response)

        self.tickets = []
        for response in responses:
            for ticket in response['rows']:
                self.tickets.append(ticket)

        return responses
