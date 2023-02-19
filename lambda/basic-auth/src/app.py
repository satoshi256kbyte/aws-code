
import json
import base64
import boto3

ssm = boto3.client('ssm', region_name='ap-northeast-1')


def lambda_handler(event, context):
    """Lambdaのエントリーポイント
    """

    request = event.get('Records')[0].get('cf').get('request')
    print('--- request ---')
    print(request)
    headers = request.get('headers')
    print('--- headers ---')
    print(headers)
    host = headers.get('host')[0].get('value')
    print('--- host ---')
    print(host)

    authorization_header = headers.get('authorization')

    if not check_authorization_header(authorization_header, host):
        return {
            'headers': {
                'www-authenticate': [
                    {
                        'key': 'WWW-Authenticate',
                        'value': 'Basic'
                    }
                ]
            },
            'status': 401,
            'body': 'Unauthorized'
        }

    return request


def check_authorization_header(authorization_header: list, host: str) -> bool:
    """Basic認証のヘッダーをチェックする
    """
    if not authorization_header:
        return False
        
    ssm_response = ssm.get_parameters(
        Names=['basicauth-parameters'],
        WithDecryption=True
    )

    print('--- ssm_response ---')
    print(ssm_response)

    # パラメータを格納する配列を準備
    params = {}

    # 復号化したパラメータを配列に格納
    for param in ssm_response['Parameters']:
        params[param['Name']] = param['Value']
        
    parameters = json.loads(params['basicauth-parameters'])

    print('--- parameters ---')
    print(parameters)

    if host not in parameters:
        return False

    for account in parameters.get(host):
        user_id = account.get('user_id')
        user_password = account.get('user_password')

        encoded_value = base64.b64encode('{0}:{1}'.format(
            user_id, user_password).encode('utf-8'))
        check_value = 'Basic {0}'.format(encoded_value.decode(encoding='utf-8'))

        if authorization_header[0].get('value') == check_value:
            return True

    return False

