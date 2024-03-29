import random
from datetime import datetime, timedelta
import time

from modules.utility import delete_data_file, read_config_file
from modules.influx import send_data_to_influxdb, generate_flux_script_tag, send_tasks, start_task, wait_for_task_success, delete_task

demo_data_config_file = "/initial/demo_config.json"
existing_tests_config_file = "/initial/config_existing_test.json"

def create_bsr_data(config, data_file_name, delta_field, delta_value, interval_field, interval_value):
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
    with open(data_file_name, mode='w') as file:
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
                totalCapacity = 200
                utilizedCapacity = random.randint(70, 150)
                availableCapacity = totalCapacity - utilizedCapacity

                # totalCapacity = availableCapacity + utilizedCapacity

                timestamp_ns = int(start_time.timestamp() * 1000000000)

                line = (
                    f'appN_path,applianceName={applianceName},connectionType={connectionType},host={host},'
                    f'ispName={ispName},networkType={networkType},pathId={pathId},pathUrlTarget={pathUrlTarget},'
                    f'path_tag_category={path_tag_category},path_tag_value={path_tag_value},vpn={vpn} '
                    f'dataJitter={data_jitter},dataLoss={data_loss},latency={latency},rtt={rtt},'
                    f'availableCapacity={availableCapacity},utilizedCapacity={utilizedCapacity},totalCapacity={totalCapacity},'
                    f'pathStatus="OK" {timestamp_ns}'
                )
                file.write(line + '\n')

                start_time += interval
                prev_pathId = pathId

def bsr_demo_create_continous_data(influxdb_token):
    config_demo_tests = read_config_file(demo_data_config_file)
    data_file_name = "bsr_demo_continous_data.txt"
    while True:
        delete_data_file(data_file_name)
        create_bsr_data(config_demo_tests, data_file_name, delta_field='minutes', delta_value=2,
                        interval_field='seconds', interval_value=60)
        send_data_to_influxdb(influxdb_token, "demo_bsr_bucket", data_file_name)
        time.sleep(120)

def bsr_demo_send_backfill_data(influxdb_token, backfill_length):
    data_file_name = "bsr_demo_backload_data"
    config_demo_tests = read_config_file(demo_data_config_file)
    create_bsr_data(config_demo_tests, data_file_name, delta_field='days', delta_value=backfill_length,
                    interval_field='minutes', interval_value=5)
    send_data_to_influxdb(influxdb_token, "demo_bsr_bucket", data_file_name)
    delete_data_file(data_file_name)

def bsr_real_send_backfill_data(influxdb_token, backfill_length):
    config_existing_tests = read_config_file(existing_tests_config_file)
    data_file_name = "bsr_real_backload_data.txt"
    create_bsr_data(config_existing_tests, data_file_name, delta_field='days', delta_value=backfill_length,
                    interval_field='minutes', interval_value=5)
    send_data_to_influxdb(influxdb_token, "bsr_bucket", data_file_name)
    delete_data_file(data_file_name)

def bsr_send_flux_task_continous(org_id, name_value, raw_bucket_value, final_bucket_value, tag_category, tag_value):
    e_value = "1"
    e_unit = "m"
    h_r_value = "60"
    h_r_unit = "m"
    flux_script = generate_flux_script_tag(name_value, e_value, e_unit, raw_bucket_value, final_bucket_value,
                                           tag_category, tag_value, h_r_value, h_r_unit)
    task_id = send_tasks(flux_script, name_value, org_id)
    start_task(task_id)

def bsr_send_calculation_backfill(org_id, name_value, raw_bucket_value, final_bucket_value, tag_category, tag_value, backload_h_r_value):
    e_value = "30"
    e_unit = "d"
    h_r_unit = "d"
    flux_script = generate_flux_script_tag(name_value, e_value, e_unit, raw_bucket_value, final_bucket_value,
                                           tag_category, tag_value, backload_h_r_value, h_r_unit)
    task_id = send_tasks(flux_script, name_value, org_id)
    start_task(task_id)
    wait_for_task_success(task_id)
    delete_task(task_id)