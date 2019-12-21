
from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse, Body, Media, Message
import requests as r
import os

api_key_ = os.environ.get('api-key', None)

headers = {'Content-Type': 'application/json',
           'api-key': api_key_}

app = Flask(__name__)


@app.route("/bot", methods=['GET', 'POST'])
def incoming_sms():

    body_text = request.values.get('Body', None).lower().split()
    body_text_lower = request.values.get('Body', None).lower()

    resp = MessagingResponse()
    message = Message()

    if all(each in ['hello', 'hi', 'welcome', 'howdy', 'speak', 'hey'] for each in body_text):

        quote_ = '\U0001f44b Welcome to AirRules, a text message-based search engine for SCAQMD rules powered by Envera Consulting. \n\n\u2705Here\'s how it works: You simply text us the air quality rules you\'re looking for, in a specific format, and we\'ll search though all of the current SCAQMD rules and regulations and send you the ones that are relevent to you ... in seconds ... all from your cell phone. That\'s it! \n\n\u2705 Please search using the format \'Send rules for INSERT EQUIPMENT TYPE OR TOPIC\' Ready to try it out? \n\n\u2705Here\'s an example: Send rules for diesel engines \n\nMsg & data rates may apply. \nText STOP to opt-out. \nText HELP for more information.'

        # message.media(media_url)
        message.body(quote_)

        resp.append(message)

    elif 'for' in body_text:

        def connection_string(x, top):
            endpoint = 'https://airrules-search.search.windows.net/indexes'
            api_version = 'docs?api-version=2019-05-06'
            index = '/demoindex/'
            search_term = "&search=" + '%20'.join(x.split(' ')) + '&$top=' + str(top)
            return endpoint + index + api_version + search_term

        def query_extract(x, y):
            try:
                return '%20'.join(x.split(' ')[x.split(' ').index(y) + 1:])
            except ValueError:
                return x

        query = query_extract(body_text_lower, 'for')

        query_format = ' '.join(query.split('%20'))

        r_ = r.get(connection_string(query, 5), headers=headers)
        if r_.status_code == 200:

            index_list = r_.json()

            rule_name_ = [each['metadata_storage_name'].split('.')[0] for each in index_list['value']]
            url_path_ = [each['metadata_storage_path'] for each in index_list['value']]

            results_json = [{'rule_name': x, 'url_path': y} for x, y in zip(rule_name_, url_path_)]

            quote_body = '\n\n---\n'.join([str(rule) + ' ' + '\n' + str(url) for rule, url in zip(rule_name_, url_path_)])

            header_quote = 'AirRules by Envera Consulting:'

            opt_out = 'Text STOP to opt-out'

            body = 'Here are the top 5 rules for'

            cta = 'For more info about air quality rules, visit https://www.enveraconsulting.com'

            quote_ = header_quote + '\n\n' + body + ' ' + query_format + ':' + '\n\n' + quote_body + '\n\n' + cta + '\n\n' + opt_out

            resp.message(quote_)

        else:
            quote_ = 'I could not retrieve your document at this time, sorry.'
            resp.message(quote_)

    else:
        resp.message("I don't understand what you are asking for. Please try again.")

    return str(resp)


if __name__ == "__main__":
    app.run(debug=True)
