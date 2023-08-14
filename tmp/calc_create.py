import requests
import time
import os
import argparse

if 'DOCKER_INFLUXDB_INIT_ADMIN_TOKEN' in os.environ:
    influxdb_token = os.environ['DOCKER_INFLUXDB_INIT_ADMIN_TOKEN']
else:
    print("Environment variable not found")
    exit(1)

influxdb_url = "http://influxdb:8086"
headers = {
    "Authorization": f"Token {influxdb_token}", "Content-Type": "application/json",
}

def generate_flux_script_url(name, every_value, every_unit, final_bucket, target, historic_range_value, historic_range_unit):
    flux_script = f'''
    option task = {{name: "{name}", every: {every_value}{every_unit}}}

    raw_bucket = "bsr_bucket"
    final_bucket = "{final_bucket}"
    path = "{target}"
    webApp =
        from(bucket: "bsr_bucket")
            |> range(start: -{historic_range_value}{historic_range_unit})
            |> filter(fn: (r) => r["webUrlTarget"] == path)
            |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")

    pathStats =
        from(bucket: "bsr_bucket")
            |> range(start: -{historic_range_value}{historic_range_unit})
            |> filter(fn: (r) => r["pathUrlTarget"] == path)
            |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")

    finalBSR_table =
        join(tables: {{webApp: webApp, pathStats: pathStats}}, on: ["_time"])
            |> map(fn: (r) => ({{r with _finalBSR_browserTiming: r.browserTiming * .001}}))
            |> map(fn: (r) => ({{r with _finalBSR_serverTiming: r.serverTiming * .001}}))
            |> map(fn: (r) => ({{r with _finalBSR_networkTiming: r.networkTiming * .001}}))
            |> map(fn: (r) => ({{r with _finalBSR_latency: r.latency * .01}}))
            |> map(fn: (r) => ({{r with _finalBSR_dataLoss: r.dataLoss * 1.0}}))
            |> map(
                fn: (r) =>
                    ({{r with _appN_exp_BSR:
                            r._finalBSR_browserTiming + r._finalBSR_networkTiming
                                +
                                r._finalBSR_serverTiming,
                    }}),
            )
            |> map(fn: (r) => ({{r with _appN_path_BSR: r._finalBSR_latency + r._finalBSR_dataLoss}}))
            |> map(fn: (r) => ({{r with _appN_total_BSR: r._appN_exp_BSR + r._appN_path_BSR}}))
            |> map(
                fn: (r) =>
                    ({{r with _adjBSR:
                            if r.webPathStatus == "OK" or r.totalBSR != 0.0 or r.pathStatus == "OK" then
                                r._appN_total_BSR
                            else
                                100.0,
                    }}),
            )
            |> map(fn: (r) => ({{r with _finalBSR: 100.0 - r._adjBSR}}))
            |> keep(
                columns: [
                    "_finalBSR",
                    "_time",
                    "appName",
                    "userFlowName",
                    "_adjBSR",
                    "_finalBSR_networkTiming",
                    "_finalBSR_serverTiming",
                    "_finalBSR_browserTiming",
                    "_finalBSR_latency",
                    "_finalBSR_dataLoss",
                    "_appN_path_BSR",
                    "_appN_exp_BSR",
                ],
            )
            |> to(
                bucket: final_bucket,
                measurementColumn: "appName",
                tagColumns: ["pathName", "userFlowName"],
                fieldFn: (r) =>
                    ({{
                        "finalBSR": r._finalBSR,
                        "adjBSR": r._adjBSR,
                        "finalBSR_network": r._finalBSR_networkTiming,
                        "finalBSR_server": r._finalBSR_serverTiming,
                        "finalBSR_browser": r._finalBSR_browserTiming,
                        "finalBSR_latency": r._finalBSR_latency,
                        "finalBSR_dataLoss": r._finalBSR_dataLoss,
                        "finalBSR_path_BSR": r._appN_path_BSR,
                        "finalBSR_exp_BSR": r._appN_exp_BSR,
                    }}),
            )
    '''
    return flux_script

def generate_flux_script_tag(name, every_value, every_unit, raw_bucket, final_bucket, tag_category, tag_value, historic_range_value, historic_range_unit):
    flux_script = f'''
    option task = {{name: "{name}", every: {every_value}{every_unit}}}

    raw_bucket = "{raw_bucket}"
    final_bucket = "{final_bucket}"
    tag_category = "{tag_category}"
    tag_value = "{tag_value}"
    webApp =
        from(bucket: raw_bucket)
            |> range(start: -{historic_range_value}{historic_range_unit})
            |> filter(fn: (r) => r["web_tag_category"] == tag_category and r["web_tag_value"] == tag_value)
            |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")

    pathStats =
        from(bucket: raw_bucket)
            |> range(start: -{historic_range_value}{historic_range_unit})
            |> filter(fn: (r) => r["path_tag_category"] == tag_category and r["path_tag_value"] == tag_value)
            |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")

    finalBSR_table =
        join(tables: {{webApp: webApp, pathStats: pathStats}}, on: ["_time"])
            |> map(fn: (r) => ({{r with _finalBSR_browserTiming: r.browserTiming * .001}}))
            |> map(fn: (r) => ({{r with _finalBSR_serverTiming: r.serverTiming * .001}}))
            |> map(fn: (r) => ({{r with _finalBSR_networkTiming: r.networkTiming * .001}}))
            |> map(fn: (r) => ({{r with _finalBSR_latency: r.latency * .01}}))
            |> map(fn: (r) => ({{r with _finalBSR_dataLoss: r.dataLoss * 1.0}}))
            |> map(
                fn: (r) =>
                    ({{r with _appN_exp_BSR:
                            r._finalBSR_browserTiming + r._finalBSR_networkTiming
                                +
                                r._finalBSR_serverTiming,
                    }}),
            )
            |> map(fn: (r) => ({{r with _appN_path_BSR: r._finalBSR_latency + r._finalBSR_dataLoss}}))
            |> map(fn: (r) => ({{r with _appN_total_BSR: r._appN_exp_BSR + r._appN_path_BSR}}))
            |> map(
                fn: (r) =>
                    ({{r with _adjBSR:
                            if r.webPathStatus == "OK" or r.totalBSR != 0.0 or r.pathStatus == "OK" then
                                r._appN_total_BSR
                            else
                                100.0,
                    }}),
            )
            |> map(fn: (r) => ({{r with _finalBSR: 100.0 - r._adjBSR}}))
            |> keep(
                columns: [
                    "_finalBSR",
                    "_time",
                    "appName",
                    "userFlowName",
                    "_adjBSR",
                    "_finalBSR_networkTiming",
                    "_finalBSR_serverTiming",
                    "_finalBSR_browserTiming",
                    "_finalBSR_latency",
                    "_finalBSR_dataLoss",
                    "_appN_path_BSR",
                    "_appN_exp_BSR",
                ],
            )
            |> to(
                bucket: final_bucket,
                measurementColumn: "appName",
                tagColumns: ["pathName", "userFlowName"],
                fieldFn: (r) =>
                    ({{
                        "finalBSR": r._finalBSR,
                        "adjBSR": r._adjBSR,
                        "finalBSR_network": r._finalBSR_networkTiming,
                        "finalBSR_server": r._finalBSR_serverTiming,
                        "finalBSR_browser": r._finalBSR_browserTiming,
                        "finalBSR_latency": r._finalBSR_latency,
                        "finalBSR_dataLoss": r._finalBSR_dataLoss,
                        "finalBSR_path_BSR": r._appN_path_BSR,
                        "finalBSR_exp_BSR": r._appN_exp_BSR,
                    }}),
            )
    '''
    return flux_script

def send_tasks(task_script, task_name, org_id):
    data = {
        "name": task_name, "every": "1m", "orgID": org_id, "org": "bsr",
        # Define the task's schedule here or use option_task["every"] to use the value from the option task
        "flux": task_script,
    }

    url = f"{influxdb_url}/api/v2/tasks"
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 201:
        print(f"Task '{task_name}' was successfully sent to InfluxDB.")
        task_id = response.json().get("id")
        return task_id
    else:
        print(
            f"Failed to send task '{task_name}' to InfluxDB. Status code: {response.status_code}, Error: {response.text}")

def start_task(task_id):
    url = f"{influxdb_url}/api/v2/tasks/{task_id}/runs"
    response = requests.post(url, headers=headers)

    if response.status_code == 201:
        run_id = response.json()["id"]
        print(f"Task ID {task_id} started successfully. Run ID: {run_id}")
    else:
        print(f"Failed to start Task ID {task_id}. Status code: {response.status_code}, Error: {response.text}")

def get_task_status(task_id):
    url = f"{influxdb_url}/api/v2/tasks/{task_id}/runs"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        runs = response.json()["runs"]
        if len(runs) > 0:
            most_recent_run = runs[0]
            status = most_recent_run["status"]
            return status
        else:
            print(f"No runs found for Task ID {task_id}.")
    else:
        print(
            f"Failed to get task runs for Task ID {task_id}. Status code: {response.status_code}, Error: {response.text}")

def get_orgs():
    url = f"{influxdb_url}/api/v2/orgs"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        orgs_data = response.json()["orgs"]  # Access the 'orgs' list
        for org in orgs_data:
            if org["name"] == "bsr":
                return org["id"]
        return None  # Organization not found
    else:
        print(f"Failed to retrieve organizations. Status code: {response.status_code}")
        return None

def wait_for_task_success(task_id):
    while True:
        status = get_task_status(task_id)
        if status == "success":
            print(f"Task ID {task_id} completed successfully.")
            break
        elif status is None:
            print(f"Failed to retrieve status for Task ID {task_id}.")
            break
        else:
            print(f"Task ID {task_id} is still running. Current status: {status}. Waiting...")
            time.sleep(10)  # Adjust the time interval (in seconds) between checks as needed

def delete_task(task_id):
    url = f"{influxdb_url}/api/v2/tasks/{task_id}"
    response = requests.delete(url, headers=headers)

    if response.status_code == 204:
        print(f"Task ID {task_id} deleted successfully.")
    else:
        print(f"Failed to delete Task ID {task_id}. Status code: {response.status_code}, Error: {response.text}")

def main():
    parser = argparse.ArgumentParser(
        description="Script will create InfluxDB Tasks used to create BSR perfection score data")

    parser.add_argument("--name", required=True, help="InfluxDB Task Name")
    parser.add_argument("--tag_category", required=True, help="Value for Tag Category")
    parser.add_argument("--tag_value", required=True, help="Value for Tag Value")
    parser.add_argument("--backload", required=True, choices=['y', 'n'], help="Process historical raw data")
    parser.add_argument("--days", type=int, required=lambda ns: ns.backload == 'y',
                        help="Number of days for backload (required if backload is 'y')")
    parser.add_argument("--initial_bucket", required=True, help="Value for raw data bucket")
    parser.add_argument("--final_bucket", required=True, help="Value for final BSR bucket")

    args = parser.parse_args()

    org_id = get_orgs()

    name_value = args.name
    tag_category = args.tag_category
    tag_value = args.tag_value
    backload = args.backload
    backload_h_r_value = args.days
    raw_bucket_value = args.initial_bucket
    final_bucket_value = args.final_bucket

    e_value = "1"
    e_unit = "m"
    h_r_value = "60"
    h_r_unit = "m"
    flux_script = generate_flux_script_tag(name_value, e_value, e_unit, raw_bucket_value, final_bucket_value,
                                           tag_category, tag_value, h_r_value, h_r_unit)
    task_id = send_tasks(flux_script, name_value, org_id)
    start_task(task_id)

    if backload == 'y':
        e_value = "30"
        e_unit = "d"
        h_r_unit = "d"
        flux_script = generate_flux_script_tag(name_value, e_value, e_unit, raw_bucket_value, final_bucket_value,
                                               tag_category, tag_value, backload_h_r_value, h_r_unit)
        task_id = send_tasks(flux_script, name_value, org_id)
        start_task(task_id)
        wait_for_task_success(task_id)
        delete_task(task_id)

if __name__ == "__main__":
    main()
