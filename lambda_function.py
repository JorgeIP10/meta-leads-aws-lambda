from core import start_program


def lambda_handler(event, context):
    start_program()
    
    return {
        'statusCode': 200,
        'body': 'Leads enviados con éxito.'
    }
