import boto3
from datetime import datetime, timedelta
import os
import random
import time
from typing import List, Dict, Any, Optional


def lambda_handler(event: Dict[str, Any], context: Optional[Any]) -> Dict[str, Any]:

    all_records_1: List[Dict[str, Any]] = []
    all_records_2: List[Dict[str, Any]] = []

    measure_values: List[Dict[str, Any]] = []
    for i in range(10):
        measure_values.append(
            {
                'Name': f'sample_measure_1_{i}',
                'Value': f'{i}',
                'Type': 'DOUBLE'
            }
        )

    for j in range(10000):

        time.sleep(0.01)

        # 今の時刻を取得
        current_time_in_millis = int(time.time() * 1000)
        # n時間前のタイムスタンプ、ここを調整して登録可能なデータ、または登録不可のデータを作成する
        two_hours_ago = datetime.now() - timedelta(hours=2)
        two_hours_ago_time_in_millis = int(two_hours_ago.timestamp() * 1000)

        all_records_1.append({
            'Dimensions': [
                {'Name': 'region',
                    'Value': f'ap-northeast-{random.randint(1, 2)}'},
                {'Name': 'az', 'Value': f'az-{random.randint(1, 2)}'},
                {'Name': 'hostname', 'Value': f'host-{random.randint(1, 10)}'},
            ],
            'MeasureName': 'multi-measure',
            'MeasureValueType': 'MULTI',
            'MeasureValues': measure_values,
            'Time': str(current_time_in_millis),
            'TimeUnit': 'MILLISECONDS'
        })
        all_records_2.append({
            'Dimensions': [
                {'Name': 'region',
                    'Value': f'ap-northeast-{random.randint(1, 2)}'},
                {'Name': 'az', 'Value': f'az-{random.randint(1, 2)}'},
                {'Name': 'hostname', 'Value': f'host-{random.randint(1, 10)}'},
            ],
            'MeasureName': 'multi-measure',
            'MeasureValueType': 'MULTI',
            'MeasureValues': measure_values,
            'Time': str(two_hours_ago_time_in_millis),
            'TimeUnit': 'MILLISECONDS'
        })

    timestream_write_client = boto3.client(
        'timestream-write', region_name=os.environ['REGION'])

    print('1-1')
    print(datetime.now())
    chunk_size = 100
    for c in range(0, len(all_records_1), chunk_size):
        chunk = all_records_1[c:c+chunk_size]
        print(chunk)
        timestream_write_client.write_records(
            DatabaseName=event.get('database_name'),
            TableName=event.get('table_name'),
            Records=chunk
        )
    print(datetime.now())
    print('1-2')

    print('2-1')
    print(datetime.now())
    chunk_size = 100
    for c in range(0, len(all_records_2), chunk_size):
        chunk = all_records_2[c:c+chunk_size]
        timestream_write_client.write_records(
            DatabaseName=event.get('database_name'),
            TableName=event.get('table_name'),
            Records=chunk
        )
    print(datetime.now())
    print('2-2')

    return {
        'statusCode': 200
    }
