import boto3
import random
import string
import datetime

def lambda_handler(event, context):

    s3_bucket = event['s3_bucket']
    s3_key = event['s3_key']
    instance_id = event['instance_id']
    timeout = int(event['timeout'])

    # EC2 Systems Managerのクライアントを作成
    ssm_client = boto3.client('ssm')
    
    try:
        # ランダム文字列を生成
        random_string = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))

        # 現在の日時を取得し、年月日時分秒をプレフィックスに加える
        current_datetime = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        script_name = current_datetime + '_' + random_string + '_script.sh'

        # EC2インスタンスに対してRunCommandを発行
        # S3からスクリプトをダウンロードして実行させる
        response = ssm_client.send_command(
            InstanceIds=[instance_id],
            DocumentName='AWS-RunShellScript',
            Parameters={'commands': ['aws s3 cp s3://{}/{} /tmp/{} && chmod +x /tmp/{} && /tmp/{}'.format(s3_bucket, s3_key, script_name, script_name, script_name)]},
            TimeoutSeconds=timeout,
        )

        # コマンドの実行結果を取得
        command_id = response['Command']['CommandId']

        # コマンドの実行状況をポーリングして待機
        waiter = ssm_client.get_waiter('command_executed')
        waiter.wait(
            InstanceId=instance_id,
            CommandId=command_id,
            WaiterConfig={
                'Delay': 10,  # ポーリング間隔を10秒に設定
                'MaxAttempts': 60  # 最大ポーリング回数を60回に設定 (合計10分)
            }
        )

        # コマンドの実行結果を取得
        command_result = ssm_client.get_command_invocation(
            InstanceId=instance_id,
            CommandId=command_id
        )
        print(command_result)

        # コマンドの実行結果判定
        if command_result['Status'] != 'Success':
            raise Exception('Command execution failed.')

        # 正常終了
        return {
            'statusCode': 200,
            'body': 'Command executed successfully'
        }

    except Exception as e:
        # 異常終了
        return {
            'statusCode': 500,
            'body': str(e)
        }
