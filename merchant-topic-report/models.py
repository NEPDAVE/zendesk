import requests
import datetime
import os
from datetime import timedelta
from collections import Counter

#https://perka.zendesk.com/api/v2/search.json?query=created%3E2016-03-10+created%3C2016-03-14+type%3Aticket
#view_id for testing
#50598826

zendesk_url = 'https://perka.zendesk.com/api/v2/'

class ReportingPeriod(object):
    def __init__(self, start=None, end=None, view_id=None):
        print "Initializing"
        self.start = start
        self.end = end
        self.format_start()
        self.format_end()
        self.view_id = view_id
        self.topic_counts = {}
        print "Getting Tickets"
        self.tickets = self.get_tickets()
        print "Filtering Tickets"
        self.filtered_tickets = self.filter_tickets()
        print "Counting Topics"
        self.count_topics()

    def get_tickets(self):
        if not self.view_id:
            response_key = 'results'

            start_date = datetime.date.today() - timedelta(days=self.start)
            formatted_start = start_date.strftime('%Y-%m-%d')

            print(formatted_start)

            end_date = datetime.date.today() - timedelta(days=self.end)
            formatted_end = end_date.strftime('%Y-%m-%d')

            print(formatted_end)

            url = "{}search.json?query=created>={}+created<{}+type:ticket".format(
                zendesk_url, formatted_start, formatted_end)
        else:
            response_key = 'rows'
            url = "{}views/{}/execute.json".format(zendesk_url, self.view_id)
        responses = []
        print "Gathering Tickets"
        s = requests.Session()
        while url:
            r = s.get(url, auth=(os.environ['ZENDESK_EMAIL'],
                                 os.environ['ZENDESK_PASSWORD']))
            response = r.json()
            url = response['next_page']
            print "Quering URL"
            responses.append(response)

        tickets = []
        ten_day_call = []

        for response in responses:
            for ticket in response[response_key]:
                tickets.append(ticket)

        return tickets

    def get_field_value(self, ticket, field_id):
        for field in ticket['custom_fields']:
            if field['id'] == field_id:
                break
        return field['value']

    def filter_tickets(self):
        filtered_tickets = []

        #Filter out unwanted tickets
        #FIXME you should make this filtering better. What if you want tickets_total?
        for ticket in self.tickets:
            if (self.get_field_value(ticket, 21818500) == 'merchant__current' or
                    self.get_field_value(ticket, 21671704) != '10_day_call'):
                    filtered_tickets.append(ticket)
            #if self.get_field_value(ticket, 21671704) != '10_day_call':
            #    filtered_tickets.append(ticket)

        self.tickets_total = len(filtered_tickets)

        return filtered_tickets

    def count_topics(self):
        topics = []

        for ticket in self.filtered_tickets:
            topic = self.get_field_value(ticket, 22956890)
            if not topic:
                topic = 'unknown'
            topics.append(topic)

        self.topic_counts = dict(Counter(topics).most_common())

    def format_start(self):
        start_date = datetime.date.today() - timedelta(days=self.start)
        formatted_start = start_date.strftime('%Y-%m-%d')

        return formatted_start

    def format_end(self):
        end_date = datetime.date.today() - timedelta(days=(self.end + 1))
        formatted_end = end_date.strftime('%Y-%m-%d')

        return formatted_end
