import boto3
import json
#we want to store route number, agency #. maybe the address and stop name, 

####################
####TODO TODO ###first session 
####################

class DynamoClient():

    def __init__(self, tableName):
        self.dynamodb = boto3.resource('dynamodb',endpoint_url="https://dynamodb.us-east-1.amazonaws.com") 
        self.tableName = tableName

    def store_agency_route_stop(self, key, agency_id, stop_id, stop_name):
        table = self.dynamodb.Table(self.tableName)

        try: 
            response = table.put_item(
                Item={
                    'uid': key, #pk
                    'agency_id': agency_id,
                    'stop_id': stop_id,
                    'stop_name': stop_name
                }
            )
        except Exception as e:
            print(e)
            print key, #pk
            print agency_id,
            print stop_id,
            print stop_name
            return False
        else:
            return True

    #return a tuple of success, dictionary of route info
    def get_route_info(self, key):
        table = self.dynamodb.Table(self.tableName)

        try:
            response = table.get_item(
                Key={
                    'uid': key,
                }
            )
        except Exception as e:
            print(e)
        else:
            if 'Item' in response:
                return True, response['Item']
            else: 
                return False, None

