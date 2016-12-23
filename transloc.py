import urllib2
import json
#import pymysql
#import re
import unirest
#pymysql.install_as_MySQLdb()

#transloc API
from translocController import TranslocController

transController = TranslocController()
#
first_session = True


def lambda_handler(event, context):
    if (event["session"]["application"]["applicationId"] !=
            "amzn1.ask.skill.7a1c9174-26ed-4dcb-a02d-8be0b35a6947"):
        raise ValueError("Invalid Application ID")
    
    if event["session"]["new"]:
        on_session_started({"requestId": event["request"]["requestId"]}, event["session"])

    if event["request"]["type"] == "LaunchRequest":
        return on_launch(event["request"], event["session"])
    elif event["request"]["type"] == "IntentRequest":
        return on_intent(event["request"], event["session"])
    elif event["request"]["type"] == "SessionEndedRequest":
        return on_session_ended(event["request"], event["session"])

def on_session_started(session_started_request, session):
    print "Starting new session."

def on_launch(launch_request, session):
    return get_welcome_response()

def on_intent(intent_request, session):
    intent = intent_request["intent"]
    intent_name = intent_request["intent"]["name"]

    if intent_name == "GetNearestBus":
        return get_nearest_bus(intent)
    elif intent_name = "ConfigureLocation":
        return configure_location(intent)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")

def on_session_ended(session_ended_request, session):
    print "Ending session."
    # Cleanup goes here...

def handle_session_end_request():
    card_title = "Translocator - Thanks"
    speech_output = "Thank you for using the translocator skill.  See you next time!"
    should_end_session = True

    return build_response({}, build_speechlet_response(card_title, speech_output, None, should_end_session))

def get_nearest_bus(intent):
    session_attributes = {}
    card_title = "Transloc nearest bus time"
    speech_output = "You're trying to get a bus time. Awesome."
    reprompt_text = "I'm not sure what you're asking for. "
    should_end_session = False

    ###########
    #CODE HERE
    ##########
    #hard coded
    min_till_bus = transController.get_next_bus_arrival(347, 4123822)

    speech_output = "Next bus is in " + str(min_till_bus) + " minutes"

    return build_response(session_attributes, build_speechlet_response(
    card_title, speech_output, reprompt_text, should_end_session))

def configure_location(intent):
    session_attributes = {}
    card_title = "Translocator configure location"
    speech_output = "The address you provided does not match the required format. Please try again."
    reprompt_text = "Please provide a valid address. An example is 608 Preston Place, Charlottesville Virginia."
    should_end_session = False

    if "address" in intent["slots"]:
        addr = intent["slots"]["address"]["value"]

        ###########
        #CODE HERE
        ###########
        stop_list = transController.get_closest_stop("608 Preston Pl, Charlottesville, VA 22903")
        if(len(stop_list) > 1):
            ###########
            #prompt for list
            ###########

            speech_output = "The following stops are available in your area: "
            for index, val in enumerate(stop_list):
                speech_output += "Option " + str(index) + ": " + val ", "

            speech_output = speech_output[:-2]
            speech_output += ". Select the desired option by saying 'option' and the corresponding number."

        else:
            #speech_output = "The address you provided is " + addr
            speech_output = "Your stop is now set to" + stop_list[0]

    return build_response(session_attributes, build_speechlet_response(
    card_title, speech_output, reprompt_text, should_end_session))

def get_option(intent):
    session_attributes = {}
    card_title = "Translocator get option"
    speech_output = "This was not a valid option. Please try again."
    reprompt_text = "Please provide a valid option."
    should_end_session = False

    if "option" in intent["slots"]:
        option = intent["slots"]["address"]["value"]

        ###########
        #CODE HERE
        ###########
        stop_list = transController.get_closest_stop("608 Preston Pl, Charlottesville, VA 22903")
        if(len(stop_list) > 1):
            ###########
            #prompt for list
            ###########

            speech_output = "The following stops are available in your area: "
            for index, val in enumerate(stop_list):
                speech_output += "Option " + str(index) + ": " + val ", "

            speech_output = speech_output[:-2]
            speech_output += ". Select the desired option by saying 'option' and the corresponding number."

        else:
            #speech_output = "The address you provided is " + addr
            speech_output = "Your stop is now set to" + stop_list[0]

    return build_response(session_attributes, build_speechlet_response(
    card_title, speech_output, reprompt_text, should_end_session))    


def get_welcome_response():
    session_attributes = {}
    card_title = "Translocator"
    speech_output = "Welcome to the Translocator skill."
    if first_session:
        speech_output += "Configure your device's location using the " \
        "'configure' keyword followed by your address."

    reprompt_text = "You can ask when the next bus is coming to your nearest stop." \
                    "You can also configure your device's location by saying configure followed by your address."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        "outputSpeech": {
            "type": "PlainText",
            "text": output
        },
        "card": {
            "type": "Simple",
            "title": title,
            "content": output
        },
        "reprompt": {
            "outputSpeech": {
                "type": "PlainText",
                "text": reprompt_text
            }
        },
        "shouldEndSession": should_end_session
    }

def build_response(session_attributes, speechlet_response):
    return {
        "version": "1.0",
        "sessionAttributes": session_attributes,
        "response": speechlet_response
    }

# def course_when(intent):
#     session_attributes = {}
#     card_title = "LOUIE course times"
#     speech_output = "I'm not sure which course you wanted. " \
#                     "Please try again."
#     reprompt_text = "I'm not sure which course you wanted. " \
#                     "Try asking about Four thousand seven hundred forty for example."
#     should_end_session = False


#     if "coursenum" in intent["slots"]:
#         course_num = intent["slots"]["coursenum"]["value"]

#         course_num_s = course_num.encode('utf8')
#         num = re.sub('[,]', '', course_num_s)
#         #station_code = get_station_code(station_name.lower())

#         conn = pymysql.connect(host='uvaclasses.martyhumphrey.info', port=3306, user='UVAClasses', passwd='WR6V2vxjBbqNqbts', db='uvaclasses')
#         cur = conn.cursor()

#         #check course
#         executeString = '''Select 1 from CS1172Data where number = "%s" ''' % (num)

#         cur.execute(executeString)
#         if cur.fetchall():
#             speech_output = ""
#             executeString = '''Select
#                 DISTINCT Days
#                 from CS1172Data where
#                 NUMBER = "%s"

#                 ''' % (num)

#             cur.execute(executeString)

#             string = "course " + num + " meets at the following times: "
#             count = 0
#             for (meetingTime) in cur:
#                 first = meetingTime[0]
#                 #do some string manipulation
#                 first = re.sub('(Tu)', 'Tuesday ', first)
#                 first = re.sub('(Th)', 'Thursday ', first)
#                 first = re.sub('(Mo)', 'Monday ', first)
#                 first = re.sub('(We)', 'Wednesday ', first)
#                 first = re.sub('(Fr)', 'Friday ', first)
#                 first = re.sub('( - )', ' to ', first)
#                 if(count !=0):
#                     string += ",  {" + first + "}"
#                 else:
#                     string += "{" + first + "}"
#                 count = count + 1


#             speech_output += string
#             reprompt_text = ""

#         cur.close()
#         conn.close()

#     return build_response(session_attributes, build_speechlet_response(
#         card_title, speech_output, reprompt_text, should_end_session))

# def course_where(intent):
#     session_attributes = {}
#     card_title = "LOUIE course locations"
#     speech_output = "I'm not sure which course you wanted. " \
#                     "Please try again."
#     reprompt_text = "I'm not sure which course you wanted. " \
#                     "Try asking about Four thousand seven hundred forty for example."
#     should_end_session = False


#     if "coursenum" in intent["slots"]:
#         course_num = intent["slots"]["coursenum"]["value"]

#         course_num_s = course_num.encode('utf8')
#         num = re.sub('[,]', '', course_num_s)
#         #station_code = get_station_code(station_name.lower())

#         conn = pymysql.connect(host='uvaclasses.martyhumphrey.info', port=3306, user='UVAClasses', passwd='WR6V2vxjBbqNqbts', db='uvaclasses')
#         cur = conn.cursor()

#         #check course
#         executeString = '''Select 1 from CS1172Data where number = "%s" ''' % (num)

#         cur.execute(executeString)
#         if cur.fetchall():
#             speech_output = ""
#             executeString = '''Select
#                 DISTINCT Room
#                 from CS1172Data where
#                 NUMBER = "%s"

#                 ''' % (num)

#             cur.execute(executeString)

#             string = "course " + num + " meets at the following locations: "
#             count = 0
#             for (meetingTime) in cur:
#                 first = meetingTime[0]
                
#                 first = re.sub('(Bldg)', 'Building', first)
#                 first = re.sub('(Engr)', 'Engineering', first)


#                 if(count !=0):
#                     string += ",  {" + first + "}"
#                 else:
#                     string += "{" + first + "}"
#                 count = count + 1


#             speech_output += string
#             reprompt_text = ""

#         cur.close()
#         conn.close()

#     return build_response(session_attributes, build_speechlet_response(
#         card_title, speech_output, reprompt_text, should_end_session))

# def course_seats(intent):
#     session_attributes = {}
#     card_title = "LOUIE course locations"
#     speech_output = "I'm not sure which course you wanted. " \
#                     "Please try again."
#     reprompt_text = "I'm not sure which course you wanted. " \
#                     "Try asking about Four thousand seven hundred forty for example."
#     should_end_session = False


#     if "coursenum" in intent["slots"]:
#         course_num = intent["slots"]["coursenum"]["value"]

#         course_num_s = course_num.encode('utf8')
#         num = re.sub('[,]', '', course_num_s)

#         #station_code = get_station_code(station_name.lower())

#         conn = pymysql.connect(host='uvaclasses.martyhumphrey.info', port=3306, user='UVAClasses', passwd='WR6V2vxjBbqNqbts', db='uvaclasses')
#         cur = conn.cursor()

#         #check course
#         executeString = '''Select 1 from CS1172Data where number = "%s" ''' % (num)

#         cur.execute(executeString)
#         if cur.fetchall():
#             speech_output = ""
            
#             executeString = '''Select
#             SUM(EnrollmentLimit) from CS1172Data where
#             NUMBER = "%s" 
#             ''' % (num)

#             cur.execute(executeString)

#             for val in cur:
#                 offered = val[0]

#             executeString = '''Select
#             SUM(Enrollment) from CS1172Data where
#             NUMBER = "%s" 

#             ''' % (num)

#             cur.execute(executeString)

#             for val in cur:
#                 taken = val[0]

#             avail = offered - taken
#             availStr = str(avail)

#             #string = "There are " + str(three) + "seats available in course " + num
#             string = "There are {0} seats available in course {1}".format(availStr, num)

#             speech_output += string
#             reprompt_text = ""

#         cur.close()
#         conn.close()

#     return build_response(session_attributes, build_speechlet_response(
#         card_title, speech_output, reprompt_text, should_end_session))

