from translocController import TranslocController
t = TranslocController()
# t.set_location("608 Preston Pl, Charlottesville, VA 22903")
t.get_geo_area_string("421 McCormick Rd, Charlottesville, VA 22904")
t.set_closest_stop("421 McCormick Rd, Charlottesville, VA 22904")
print(t.get_closest_stop_list())
# res = t.get_next_bus_arrival(347, 4123822)
# print res
# import datetime
# import unirest
# import logging
# import geocoder

# g = geocoder.google("218 14th St NW, Charlottesville, VA 22903")
# #<[OK] Google - Geocode [608 Preston Pl, Charlottesville, VA 22903, USA]>
# # g.bbox
# # {'northeast': [38.0429164802915, -78.49673836970848], 'southwest': [38.0402185197085, -78.49943633029149]}

# #just goes in order as you'd expect from the api

# base_url = "https://transloc-api-1-2.p.mashape.com/agencies.json?callback=call&"
# geo_area = "geo_area="+str(g.bbox['northeast'][0])+"%2C+"+ str(g.bbox['northeast'][1]) + "%7C" \
#                 + str(g.bbox['southwest'][0])+"%2C+"+ str(g.bbox['southwest'][1])

# response = unirest.get(base_url + geo_area,
#   headers={
#     "X-Mashape-Key": "P5XVDHDhPEmshrYNeT29XndUunS4p1EPDrOjsnosBj9nVdvjit",
#     "Accept": "application/json"
#   }
# )

# print response.body['data']
# if (len(response.body['data']) == 0 ):
# 	print "dead"
