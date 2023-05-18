import random
from datetime import datetime, timedelta
import requests
import time
import os

if 'DOCKER_INFLUXDB_INIT_ADMIN_TOKEN' in os.environ:
    # Environment variable exists
    var_value = os.environ['DOCKER_INFLUXDB_INIT_ADMIN_TOKEN']
    influx_token = var_value
else:
    print("Environment variable not found")

influx_server_ip = 'influxdb.local'
influx_server_port = '8086'
bucket = 'demo_bsr_bucket'

config = {
    "group1": {
        "appName": "BSR",
        "applianceName": "AppNeta-vk35-Site-1",
        "host": "telegraf.local",
        "milestone": "0",
        "userFlowName": "Open",
        "webAppId": "19660",
        "webPathId": "52194",
        "webUrlTarget": "google.com",
        "web_tag_category": "null",
        "web_tag_value": "null",
        "connectionType": "Wired",
        "ispName": "Google",
        "networkType": "WAN",
        "pathId" : "77642",
        "pathUrlTarget" : "google.com",
        "path_tag_category" : "null",
        "path_tag_value": "null",
        "vpn" : "Inactive"
    },
    "group2": {
        "appName": "Check Checking Balance",
        "applianceName": "m70-01",
        "host": "telegraf.local",
        "milestone": "0",
        "userFlowName": "check_checking_balance_workflow",
        "webAppId": "19438",
        "webPathId": "51603",
        "webUrlTarget": "www.bank.com",
        "web_tag_category": "null",
        "web_tag_value": "null",
        "connectionType": "Wired",
        "ispName": "AT&T",
        "networkType": "WAN",
        "pathId" : "70002",
        "pathUrlTarget" : "www.bank.com",
        "path_tag_category" : "null",
        "path_tag_value": "null",
        "vpn" : "Inactive"
    },
    "group3": {
        "appName": "Schedule Transfer",
        "applianceName": "m70-01",
        "host": "telegraf.local",
        "milestone": "0",
        "userFlowName": "schedule_transfer_workflow",
        "webAppId": "19439",
        "webPathId": "51604",
        "webUrlTarget": "www.bank.com",
        "web_tag_category": "null",
        "web_tag_value": "null",
        "connectionType": "Wired",
        "ispName": "AT&T",
        "networkType": "WAN",
        "pathId" : "70003",
        "pathUrlTarget" : "www.bank.com",
        "path_tag_category" : "null",
        "path_tag_value": "null",
        "vpn" : "Inactive"
    },
    "group4": {
        "appName": "Close Account",
        "applianceName": "m70-01",
        "host": "telegraf.local",
        "milestone": "0",
        "userFlowName": "close_account_workflow",
        "webAppId": "19440",
        "webPathId": "51605",
        "webUrlTarget": "www.bank.com",
        "web_tag_category": "null",
        "web_tag_value": "null",
        "connectionType": "Wired",
        "ispName": "AT&T",
        "networkType": "WAN",
        "pathId" : "70004",
        "pathUrlTarget" : "www.bank.com",
        "path_tag_category" : "null",
        "path_tag_value": "null",
        "vpn" : "Inactive"
    },
}

def create_bsr_data(delta_field, delta_value, interval_field, interval_value):
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
            userFlowName = group_config["userFlowName"].replace(" ", "_")
            webAppId = group_config["webAppId"]
            webPathId = group_config["webPathId"]
            webUrlTarget = group_config["webUrlTarget"]
            web_tag_category = group_config["web_tag_category"].replace(" ", "_")
            web_tag_value = group_config["web_tag_value"].replace(" ", "_")
            start_time = initial_start_time

            # generate data points for each time interval
            while end_time > start_time:
                # generate a random value for each field at each time interval
                value = random.randint(100, 800)
                timestamp_ns = int(start_time.timestamp() * 1000000000)
                #timestamp_ns = int(start_time.timestamp())
                line = f'appN_exp,appName={appName},applianceName={applianceName},host={host},milestone={milestone},userFlowName={userFlowName},webAppId={webAppId},webPathId={webPathId},webUrlTarget={webUrlTarget},web_tag_category={web_tag_category},web_tag_value={web_tag_value} ' \
                       f'browserTiming={value} {timestamp_ns}'
                file.write(line + '\n')

                value = random.randint(100, 800)

                line = f'appN_exp,appName={appName},applianceName={applianceName},host={host},milestone={milestone},userFlowName={userFlowName},webAppId={webAppId},webPathId={webPathId},webUrlTarget={webUrlTarget},web_tag_category={web_tag_category},web_tag_value={web_tag_value} ' \
                       f'networkTiming={value} {timestamp_ns}'
                file.write(line + '\n')

                value = random.randint(100, 800)

                line = f'appN_exp,appName={appName},applianceName={applianceName},host={host},milestone={milestone},userFlowName={userFlowName},webAppId={webAppId},webPathId={webPathId},webUrlTarget={webUrlTarget},web_tag_category={web_tag_category},web_tag_value={web_tag_value} ' \
                       f'serverTiming={value} {timestamp_ns}'
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
                    f'dataJitter={data_jitter} {timestamp_ns}'
                )
                file.write(line + '\n')

                line = (
                    f'appN_path,applianceName={applianceName},connectionType={connectionType},host={host},'
                    f'ispName={ispName},networkType={networkType},pathId={pathId},pathUrlTarget={pathUrlTarget},'
                    f'path_tag_category={path_tag_category},path_tag_value={path_tag_value},vpn={vpn} '
                    f'dataLoss={data_loss} {timestamp_ns}'
                )
                file.write(line + '\n')

                line = (
                    f'appN_path,applianceName={applianceName},connectionType={connectionType},host={host},'
                    f'ispName={ispName},networkType={networkType},pathId={pathId},pathUrlTarget={pathUrlTarget},'
                    f'path_tag_category={path_tag_category},path_tag_value={path_tag_value},vpn={vpn} '
                    f'latency={latency} {timestamp_ns}'
                )
                file.write(line + '\n')

                line = (
                    f'appN_path,applianceName={applianceName},connectionType={connectionType},host={host},'
                    f'ispName={ispName},networkType={networkType},pathId={pathId},pathUrlTarget={pathUrlTarget},'
                    f'path_tag_category={path_tag_category},path_tag_value={path_tag_value},vpn={vpn} '
                    f'rtt={rtt} {timestamp_ns}'
                )
                file.write(line + '\n')

                start_time += interval
                prev_pathId = pathId

def send_data_to_influxdb(token):
    url = f"http://{influx_server_ip}:{influx_server_port}/api/v2/write?org=bsr&bucket={bucket}&precision=ns"
    headers = {
        "Authorization": f"Token {token}"
    }
    with open("bsr_data.txt", "rb") as file:
        response = requests.post(url, headers=headers, data=file)
        response.raise_for_status()
print("Starting demo data creation and loading to InfluxDB")
create_bsr_data(delta_field='days', delta_value=60, interval_field='minutes', interval_value=5)
send_data_to_influxdb(influx_token)

while True:
    create_bsr_data(delta_field='minutes', delta_value=1, interval_field='seconds', interval_value=30)
    send_data_to_influxdb(influx_token)
    time.sleep(60)