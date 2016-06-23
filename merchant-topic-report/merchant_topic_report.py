#flask_main_merchant_topic.py
import math
import flask
from flask import Flask, render_template, request
from models import ReportingPeriod

app = Flask(__name__)

def calculate_statistics(p1, p2):
    report_data = {}

    p1_set = set(p1.topic_counts.keys())
    p2_set = set(p2.topic_counts.keys())

    common = p1_set & p2_set
    #.update will update a dictionary in another one
    report_data.update(calculate_percent_change(p1, p2, common))
    p1_unique = p1_set - p2_set
    report_data.update(calculate_percent_change(p1, p2, p1_unique))
    p2_unique = p2_set - p1_set
    report_data.update(calculate_percent_change(p1, p2, p2_unique))

    return report_data

def calculate_percent_change(p1, p2, topics):
    report_data = {}
    for topic in topics:
        report_data[topic] = {}
        #.get will return a default value, in this case 0 if topic not in p1
        p1_count = p1.topic_counts.get(topic, 0)
        p2_count = p2.topic_counts.get(topic, 0)
        if p1_count:
            percent_change = 100 * round((p2_count - p1_count) / float(p1_count), 2)
        else:
            percent_change = 'nan'

        report_data[topic]['first_period_count'] = p1_count
        report_data[topic]['second_period_count'] = p2_count
        report_data[topic]['percent_change'] = percent_change

    return report_data

def calculate_period_totals_data(p1_tickets_total, p2_tickets_total):
    period_totals_data = {}

    period_totals_data['p1_tickets_total'] = p1_tickets_total
    period_totals_data['p2_tickets_total'] = p2_tickets_total
    period_totals_data['percent_change'] = 100 * round((p2_tickets_total - p1_tickets_total) / float(p1_tickets_total), 2)

    return period_totals_data


@app.route("/")
def hello():
    #FIXME
    #What is happening here? What is request.args?
    period_length = int(request.args.get("length", 14))

    #FIXME
    #Is this the best place to put the start and end dates?
    #How can we get these dates from user input?
    #p1 = ReportingPeriod(view_id=49596853)
    p1 = ReportingPeriod(start=(period_length * 2), end=period_length)
    p2 = ReportingPeriod(start=period_length, end=0)

    report_data = calculate_statistics(p1, p2)
    period_totals_data = calculate_period_totals_data(p1.tickets_total, p2.tickets_total)


    data = {
        'x': 'x',
        'columns': [
            ['x'],
            ['former period'],
            ['latter period'],
            ],
        'type': 'bar',
        'colors': {
            'former period': '#0000FF',
            'latter period': '#00FF00',
            }
        }

    for topic in report_data:
        data['columns'][0].append(str(topic))
        data['columns'][1].append(report_data[topic]['first_period_count'])
        data['columns'][2].append(report_data[topic]['second_period_count'])

    params = {
        'report_data': report_data,
        'period_totals_data': period_totals_data,
        'p1': p1,
        'p2': p2,
        'data': data
         }

    print data
    return render_template('merchant_topic_report.html', **params)

if __name__ == "__main__":
    app.run(debug=True)
    #app.run(debug=True, host='192.168.2.20')
