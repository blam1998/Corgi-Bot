import boto3

client = boto3.client('athena')
s3 = boto3.client('s3')

namedQueries = client.list_named_queries()

#ResultSet = Dict
#Rows = list
#Data = list
#Each data piece is a dictionary with key VarCharValue
#print(results['ResultSet']['Rows'][1]['Data'][0]['VarCharValue'])
#print(len(results['ResultSet']['Rows']))


def Queries(QueryStr: str,path: str):
    #response --> Dict that contains Key QueryExecutionID
    response = client.start_query_execution(
        QueryString = QueryStr,
        QueryExecutionContext={
            'Database': 'corgi'
        },
        ResultConfiguration={
            'OutputLocation': path,
        }
    )

    executionId = response['QueryExecutionId']

    state = 'QUEUED'

    while state in ['RUNNING','QUEUED']:
        res = client.get_query_execution(QueryExecutionId = executionId)
        state = res['QueryExecution']['Status']['State']
        if state in ['SUCCEEDED', 'CANCELLED']:
            break
        if state == 'FAILED':
            print("Failed")

    if state == 'SUCCEEDED':
        print("Succeeded")
        results = client.get_query_results(QueryExecutionId = executionId)

    return results if state == 'SUCCEEDED' else {}








