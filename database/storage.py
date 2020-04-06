import boto3


class Storage:
    def __init__(self, context):
        self.client = boto3.client('dynamodb', region_name='eu-west-1')
        self.context = context

    def list_my_tables(self):
        return self.client.list_tables()

    def get_user_item(self):
        user_id = self.context['System']['user']['userId']
        key = {
            'userId': {'S': user_id}
        }
        table = 'sb_users'
        response = self.client.get_item(Key=key, TableName=table)
        if 'Item' in response.keys():
            return response['Item']
        else:
            return False

    def save_user_item(self, item):
        formatted_item = {
            'userId': {'S': item['userId']},
            'premium': {'BOOL': item['premium']}
        }
        self.client.put_item(Item=formatted_item, TableName='sb_users')


# Uncomment to run configurations
if __name__ == '__main__':

    # Test get_user_item:
    # context = {'System': {'user': {'userId': 'abc124'}}}
    # storage = Storage(context)
    # storage.get_user_item()

    # Test save_user_item:
    context = {'System': {'user': {'userId': 'abc12'}}}
    user_item = {
        'userId': context['System']['user']['userId'],
        'premium': False
    }
    storage = Storage(context)
    storage.save_user_item(user_item)
