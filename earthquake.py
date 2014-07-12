import json
import pprint as pp

#import datetime #time.date.fromtimestamp doesn't return time, just the date portion
import time #this is better than datetime

#import urllib

import oauth2 as oauth
import urllib2 as urllib

import ConfigParser

def read_feed(url_feed):
    """
    reads data feed into memory
    Input:  url_feed is a str of the URL
    Output: returns dictionary of geojson
    """
    url_handle = urllib.urlopen(url_feed)
    #recent = url_handle.readline() #get most recent event (first line of feed)
    return json.load(url_handle)
    #loads takes string para, load takes file stream/handle

def load_data(filename):
    """
    for reading a local .json file
    """
    with open(filename) as infile_handle:
        return json.load(infile_handle)

def get_time(time_input):   #N00B mistake: can't name input time, b/c of name conflit with time library!!!
    """
    Input: time is a long representing the MILLIseconds since epoch
    Output: YYYY-MM-DD HH:MM:SS 24HR UTC string repr time
    """
    return time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(time_input))

def print_data(json_data):
    #for feature in json_data["features"]: #to iterate across all features

    feature = json_data["features"][0] #get most recent event
    #feature_id = feature["properties"]["id"]
    timestamp = get_time(feature["properties"]["time"]/1000)

    if feature["properties"]["tsunami"] == 1: #tsunami flag true
        print("POSSIBILE TSUNAMI! http://www.tsunami.gov")

    print("Mag: %s ") % (feature["properties"]["mag"])
    print("#earthquake %s") % (feature["properties"]["place"])
    print("@ %s") % (timestamp)
    #print("Coordinate: %s") % (feature["geometry"]["coordinates"])
    print("%s") % (feature["properties"]["url"])
    #TODO: make URL shorter by changing to bitly twitter automatically converts all urls to t.co


    #print("Tsunami warning!: %s") % (feature["properties"]["tsunami"])
    print ("#quake\n")

def login_twitter(url, method, parameters):
    #read in configuration sets from config file into vars
    config = ConfigParser.ConfigParser()
    config.read('twitterkeys.config')
    api_key = config.get('Twitter API Keys', 'api_key')
    api_secret = config.get('Twitter API Keys', 'api_secret')
    access_token_key = config.get('Twitter API Keys', 'access_token_key')
    access_token_secret = config.get('Twitter API Keys', 'access_token_secret')

    _debug = 0

    #create oauth credentials using api keys and tokens
    oauth_token    = oauth.Token(key=access_token_key, secret=access_token_secret)
    oauth_consumer = oauth.Consumer(key=api_key, secret=api_secret)

    signature_method_hmac_sha1 = oauth.SignatureMethod_HMAC_SHA1()

    http_method = "GET"


    http_handler  = urllib.HTTPHandler(debuglevel=_debug)
    https_handler = urllib.HTTPSHandler(debuglevel=_debug)

    #Construct, sign, and open a twitter request using the hard-coded credentials above.
    req = oauth.Request.from_consumer_and_token(oauth_consumer,
                                             token=oauth_token,
                                             http_method=http_method,
                                             http_url=url, 
                                             parameters=parameters)

    req.sign_request(signature_method_hmac_sha1, oauth_consumer, oauth_token)

    headers = req.to_header()

    if http_method == "POST":
        encoded_post_data = req.to_postdata()
    else:
        encoded_post_data = None
        url = req.to_url()

    opener = urllib.OpenerDirector()
    opener.add_handler(http_handler)
    opener.add_handler(https_handler)

    response = opener.open(url, encoded_post_data)

    return response
    """
    #TODO: change from reading json data to posting stuff to twitter
    """
    

def run_program():
    url = "https://stream.twitter.com/1.1/statuses/filter.json?locations=-179.148611,18.910833,-66.947028,71.388889"
    #southwestern most point of USA (long,lat) -179.148611,18.910833
    #northeastern most point of USA (long,lat) -66.947028,71.388889
    parameters = []
    response = login_twitter(url, "GET", parameters)
    for line in response:
        print line.strip()

    #data = load_data("all_hour.geojson")
    #data = load_data("all_day.geojson")

    all_hourly = "http://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"

    #data = read_feed(all_hourly)
    #pp.pprint(data)

    #print_data(data)



if __name__ == "__main__":
    run_program()
