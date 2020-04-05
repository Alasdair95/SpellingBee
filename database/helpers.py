import boto3


class Storage:
    def __init__(self):
        self.client = boto3.client('dynamodb', region_name='eu-west-1')

    def list_my_tables(self):
        tables = self.client.list_tables()
        return tables

# Uncomment to run configurations
# if __name__ == '__main__':
#     storage = Storage()
#     storage.list_my_tables()
