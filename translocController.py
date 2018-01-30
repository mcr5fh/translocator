from __future__ import print_function
import datetime
import unirest
import logging
import geocoder
import time
from geopy.distance import great_circle

class TranslocController():
    OVER_QUERY_LIMIT = "OVER_QUERY_LIMIT"
    STOP_RADIUS = 0.25

    def __init__(self):
        logging.basicConfig(filename='trans.log', level=logging.DEBUG)
        self.local_address = ""
        self.agency_long_name = ""

        self.local_agency_id = -1
        self.local_route_number = -1
        self.local_stop_id = -1
        self.local_stop_id = -1

        self.local_nearby_stops = []
        self.local_nearby_stop_ids = []
        self.getting_options = False

    def set_location(self, address):
        #local_address = address
        base_agency_url = "https://transloc-api-1-2.p.mashape.com/agencies.json?callback=call&"
        geo_area = self.get_geo_area_string(address)
        if geo_area == None:
            print("Invalid address. Unable to set location.")
            return False

        response = unirest.get(base_agency_url + geo_area,
                               headers={
                                   "X-Mashape-Key": "P5XVDHDhPEmshrYNeT29XndUunS4p1EPDrOjsnosBj9nVdvjit",
                                   "Accept": "application/json"
                               }
                               )
        # check to make sure that there is a transloc agency nearby
        if (len(response.body['data']) == 0):
            print("Found no transloc nearby")
            return False

        print(response.body['data'][0]['long_name'])
        print(response.body['data'][0]['agency_id'])
        self.local_address = address
        self.local_agency_id = response.body['data'][0]['agency_id']
        self.acgency_long_name = response.body['data'][0]['long_name']

    # Will return a list of strings of the stops in the vicinity
    def set_closest_stop(self, address=None):
        if(address != None):
            if(self.set_location(address) == False):
                return []

        if(self.local_agency_id == -1):
            logging.error('Agency id has not been set')
            print('Agency id has not been set')
            return []

        base_stop_url = "https://transloc-api-1-2.p.mashape.com/stops.json?agencies=" + str(self.local_agency_id) + "&callback=call&"
        geo_area = self.get_geo_area_string(address)

        response = unirest.get(base_stop_url,
                               headers={
                                   "X-Mashape-Key": "P5XVDHDhPEmshrYNeT29XndUunS4p1EPDrOjsnosBj9nVdvjit",
                                   "Accept": "application/json"
                               }
                               )
        # print(response.body)
        
        g = geocoder.google(address)
        addr_cords = g.latlng

        stop_list_str = []
        stop_list_id = []
        for stop_data in response.body['data']:
            stop_cords = (stop_data['location']['lat'], stop_data['location']['lng'])
            if(great_circle(stop_cords, addr_cords).miles < self.STOP_RADIUS):
                stop_list_str.append(stop_data['name'].encode('utf8'))
                stop_list_id.append(stop_data['stop_id'])

        print(stop_list_str)
        self.local_nearby_stops = stop_list_str
        self.local_nearby_stop_ids = stop_list_id
        return stop_list_str

    # returns the minutes until the next bus
    # Response of -1 is no bus times
    # Response of -99 is API error
    def get_next_bus_arrival(self, agency_id, stop_num):
        base_url = "https://transloc-api-1-2.p.mashape.com/arrival-estimates.json?agencies="
        base_url += str(agency_id)
        base_url += "&callback=call&stops="
        base_url += str(stop_num)

        response = unirest.get(base_url,
                               headers={
                                   "X-Mashape-Key": "P5XVDHDhPEmshrYNeT29XndUunS4p1EPDrOjsnosBj9nVdvjit",
                                   "Accept": "application/json"
                               }
                               )
        # accesses the first (next arriving bus from the list)
        try:
            if len(response.body['data']) == 0:
                print("No available bus times")
                return -1
            next_arrival_time = response.body['data'][0]['arrivals'][0]['arrival_at']
            # gives us something like this: '2016-12-22T17:31:55-05:00'
            # take off the time zone: '-05:00'
            next_time_formatted = next_arrival_time[:-6]
            # its +5 hours in the utc format from transloc
            time_zone = next_arrival_time[-6:]
            time_zone_offset = int(time_zone[1:3])
            # create a date time object from it
            next_time_dtobj = datetime.datetime.strptime(
                next_time_formatted, '%Y-%m-%dT%H:%M:%S')
            next_time_dtobj += datetime.timedelta(0,
                                                  time_zone_offset * 60 * 60)

            time_delta = next_time_dtobj - datetime.datetime.now()
            delta_mins = time_delta.seconds / 60

            return delta_mins
        except Exception as e:
            print("Api error getting bus time: Response body: " + str(response.body))
            print(e)
            return -99

    # Return a string containing the "geo-box" long/lat coordinates of an address
    # Return None if the address couldn't be found
    def get_geo_area_string(self, address):
        print("Getting geo area for: " + address)
        g = geocoder.google(
            address, key="AIzaSyC2NbM2cmbj7O2MNqfFTyQI9uT0RX4PzP0")
        #<[OK] Google - Geocode [608 Preston Pl, Charlottesville, VA 22903, USA]>
        # g.bbox
        # {'northeast': [38.0429164802915, -78.49673836970848], 'southwest': [38.0402185197085, -78.49943633029149]}

        # Google has a 1 second throttle limit, so wait for one second then
        # retry
        for x in range(0, 10):
            if g.error == self.OVER_QUERY_LIMIT:
                print("Throttled, sleeping for 1.5 sec")
                time.sleep(1.5)
                g = geocoder.google(address)
            else:
                break
        print(g)

        # If bbox is still null, the address cant be found
        if not g.bbox:
            print("Cannot find address")
            return None

        # just goes in order as you'd expect from the api
        try:
            #Trim the coordinates for a larger radius
            return "geo_area=" + str(g.bbox['northeast'][0])[:8] + "%2C+" \
                + str(g.bbox['northeast'][1])[:8] + "%7C" \
                + str(g.bbox['southwest'][0])[:8] + "%2C+"  \
                + str(g.bbox['southwest'][1])[:8]
        except Exception as e:
            print("Unable to find address: " + address)
            print(e)
            return []

# ---------- Getters and Setters ----------
    def get_getting_options(self):
        return self.getting_options

    def set_getting_options(self, status):
        self.getting_options = status

    def set_stop_id_from_stop_list(self, stop_list_index):
        self.local_stop_id = self.local_nearby_stop_ids[stop_list_index]

    def set_stop_id(self, stop_id):
        self.local_stop_id = stop_id

    def get_stop_id(self):
        return self.local_stop_id

    def set_agency_id(self, a_id):
        self.local_agency_id = a_id

    def get_agency_id(self):
        return self.local_agency_id

    def get_closest_stop_list(self):
        return self.local_nearby_stops
