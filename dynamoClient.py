import boto3
import json
#we want to store route number, agency #. maybe the address and stop name, 

####################
####TODO TODO ###first session 
####################

class DynamoClient():

    def __init__(self, tableName):
        self.dynamodb = dynamodb = boto3.resource('dynamodb',endpoint_url="https://dynamodb.us-east-1.amazonaws.com") 
        self.table = self.dynamodb.Table(tableName)

    def store_agency_route_stop(self, key, agency_id, route_id, stop_name):
        response = self.table.put_item(
            Item={
                'uid': key, #pk
                'agency': agency_id,
                'route': route_id,
                'stop_name': stop_name
            }
        )

    #return a dictionary of route info
    def get_route_info(self, key):
        try:
            response = self.table.get_item(
                Key={
                    'uid': key,
                }
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            return response['Item']

