
#!/usr/bin/env python3
import requests
import json


class Markit:
    def __init__(self, user_input):
        self.scheme= 'http://'
        self.subdomain = 'dev.'
        self.domain = 'markitondemand.'
        self.tld = 'com'
        self.lookup_path = '/MODApis/Api/v2/Lookup/json'
        self.lookup_querystring = '?input='
        self.quote_path = '/MODApis/Api/v2/Quote/json'
        self.quote_querystring = '?symbol='
        self.endpoint=self.scheme \
                      + self.subdomain \
                      + self.domain \
                      + self.tld 
        self.user_input=user_input

    def __enter__(self):
        return self

    def __exit__(self, type, value ,traceback):
        pass

        
    def quote(self):
        response=json.loads(
                    requests.get(
                        self.endpoint
                        + self.quote_path
                        + self.quote_querystring
                        + self.user_input)
                    .text)
        return response["LastPrice"]

    def lookup(self):
        response=json.loads(
                    requests.get(
                        self.endpoint
                        + self.lookup_path
                        + self.lookup_querystring
                        + self.user_input)
                    .text)
        return response[0]["Symbol"]

