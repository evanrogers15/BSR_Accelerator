import random
from datetime import datetime, timedelta
import requests
import time
import os
import json

backload_real_data = 0

if 'DOCKER_INFLUXDB_INIT_ADMIN_TOKEN' in os.environ:
    # Environment variable exists
    var_value = os.environ['DOCKER_INFLUXDB_INIT_ADMIN_TOKEN']
    influx_token = var_value
else:
    print("Environment variable not found")

influx_server_ip = 'influxdb.local'
influx_server_port = '8086'

def read_config_file(file_path):
    with open(file_path, "r") as f:
        data = json.load(f)
    return data

def create_bsr_data(config, delta_field, delta_value, interval_field, interval_value):
    end_time = datetime.utcnow().replace(microsecond=0)
    if delta_field == 'minutes':
        start_time = end_time - timedelta(minutes=delta_value)
    elif delta_field == 'hours':
        start_time = end_time - timedelta(hours=delta_value)
    elif delta_field == 'days':
        start_time = end_time - timedelta(days=delta_value)
    elif delta_field == 'weeks':
        start_time = end_time - timedelta(weeks=delta_value)
    else:
        raise ValueError("Invalid delta_field value. Supported values are 'minutes', 'hours', 'days', 'weeks'.")
    initial_start_time = start_time

    if interval_field == 'seconds':
        interval = timedelta(seconds=interval_value)
    elif interval_field == 'minutes':
        interval = timedelta(minutes=interval_value)
    else:
        raise ValueError("Invalid delta_field value. Supported values are 'minutes', 'hours'")
    with open('bsr_data.txt', mode='w') as file:
        for group in config:
            group_config = config[group]
            appName = group_config["appName"].replace(" ", "_")
            applianceName = group_config["applianceName"].replace(" ", "_")
            host = group_config["host"]
            milestone = group_config["milestone"]
            milestoneName = group_config["milestoneName"]
            userFlowName = group_config["userFlowName"].replace(" ", "_")
            webAppId = group_config["webAppId"]
            webPathId = group_config["webPathId"]
            webUrlTarget = group_config["webUrlTarget"]
            web_tag_category = group_config["web_tag_category"].replace(" ", "_")
            web_tag_value = group_config["web_tag_value"].replace(" ", "_")
            start_time = initial_start_time
            statusCode = 200

            # generate data points for each time interval
            while end_time > start_time:
                # generate a random value for each field at each time interval
                value1 = random.randint(100, 800)
                value2 = random.randint(100, 800)
                value3 = random.randint(100, 800)
                value4 = value1 + value2 + value3

                timestamp_ns = int(start_time.timestamp() * 1000000000)
                line = f'appN_exp,appName={appName},applianceName={applianceName},host={host},milestone={milestone},milestoneName={milestoneName},userFlowName={userFlowName},webAppId={webAppId},webPathId={webPathId},webUrlTarget={webUrlTarget},web_tag_category={web_tag_category},web_tag_value={web_tag_value} ' \
                       f'browserTiming={value1},networkTiming={value2},serverTiming={value3},statusCode={statusCode},webPathStatus="OK",totalTime={value4} {timestamp_ns}'
                file.write(line + '\n')

                start_time += interval
        for group in config:
            group_config = config[group]
            applianceName = group_config["applianceName"].replace(" ", "_")
            connectionType = group_config["connectionType"].replace(" ", "_")
            host = group_config["host"].replace(" ", "_")
            ispName = group_config["ispName"].replace(" ", "_")
            networkType = group_config["networkType"].replace(" ", "_")
            pathId = group_config["pathId"]
            pathUrlTarget = group_config["pathUrlTarget"].replace(" ", "_")
            path_tag_category = group_config["path_tag_category"].replace(" ", "_")
            path_tag_value = group_config["path_tag_value"].replace(" ", "_")
            vpn = group_config["vpn"]

            prev_pathId = None
            start_time = initial_start_time

            # Generate data points for each time interval
            while end_time > start_time:
                # Generate a random value for each field at each time interval
                data_jitter = round(random.uniform(0.01, 2), 2)
                data_loss = round(random.uniform(0.0, 0.1), 2)
                latency = random.randint(2, 8)
                rtt = latency * 2

                timestamp_ns = int(start_time.timestamp() * 1000000000)
                #timestamp_ns = int(start_time.timestamp())

                line = (
                    f'appN_path,applianceName={applianceName},connectionType={connectionType},host={host},'
                    f'ispName={ispName},networkType={networkType},pathId={pathId},pathUrlTarget={pathUrlTarget},'
                    f'path_tag_category={path_tag_category},path_tag_value={path_tag_value},vpn={vpn} '
                    f'dataJitter={data_jitter} {timestamp_ns},webPathStatus="OK"'
                )
                file.write(line + '\n')

                line = (
                    f'appN_path,applianceName={applianceName},connectionType={connectionType},host={host},'
                    f'ispName={ispName},networkType={networkType},pathId={pathId},pathUrlTarget={pathUrlTarget},'
                    f'path_tag_category={path_tag_category},path_tag_value={path_tag_value},vpn={vpn} '
                    f'dataLoss={data_loss} {timestamp_ns},webPathStatus="OK"'
                )
                file.write(line + '\n')

                line = (
                    f'appN_path,applianceName={applianceName},connectionType={connectionType},host={host},'
                    f'ispName={ispName},networkType={networkType},pathId={pathId},pathUrlTarget={pathUrlTarget},'
                    f'path_tag_category={path_tag_category},path_tag_value={path_tag_value},vpn={vpn} '
                    f'latency={latency} {timestamp_ns},webPathStatus="OK"'
                )
                file.write(line + '\n')

                line = (
                    f'appN_path,applianceName={applianceName},connectionType={connectionType},host={host},'
                    f'ispName={ispName},networkType={networkType},pathId={pathId},pathUrlTarget={pathUrlTarget},'
                    f'path_tag_category={path_tag_category},path_tag_value={path_tag_value},vpn={vpn} '
                    f'rtt={rtt} {timestamp_ns},webPathStatus="OK"'
                )
                file.write(line + '\n')

                start_time += interval
                prev_pathId = pathId

def send_data_to_influxdb(token, bucket):
    url = f"http://{influx_server_ip}:{influx_server_port}/api/v2/write?org=bsr&bucket={bucket}&precision=ns"
    headers = {
        "Authorization": f"Token {token}"
    }
    with open("bsr_data.txt", "rb") as file:
        retries = 5
        delay = 5  # Delay in seconds between retries
        while retries > 0:
            try:
                response = requests.post(url, headers=headers, data=file)
                response.raise_for_status()
                break  # If successful, break out of the loop
            except requests.exceptions.RequestException as e:
                print(f"Failed to send data to InfluxDB: {e}")
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
                retries -= 1
        else:
            print("Failed to send data to InfluxDB after multiple retries.")

def delete_data_file():
    file_path = "bsr_data.txt"
    if os.path.exists(file_path):
        os.remove(file_path)

if __name__ == "__main__":
    if backload_real_data == 1:
        config_existing_tests = read_config_file("config_existing_tests.json")
        create_bsr_data(config_existing_tests, delta_field='days', delta_value=60, interval_field='minutes', interval_value=5)
        send_data_to_influxdb(influx_token, "bsr_bucket")
        delete_data_file()

    config_demo_tests = read_config_file("demo_config.json")
    create_bsr_data(config_demo_tests, delta_field='days', delta_value=60, interval_field='minutes', interval_value=5)
    send_data_to_influxdb(influx_token, "demo_bsr_bucket")
    delete_data_file()

    while True:
        delete_data_file()
        create_bsr_data(config_demo_tests, delta_field='minutes', delta_value=2, interval_field='seconds', interval_value=60)
        send_data_to_influxdb(influx_token, "demo_bsr_bucket")
        time.sleep(120)