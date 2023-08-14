import os
import requests
import time

# Initialize variables
influxdb_token = os.getenv("DOCKER_INFLUXDB_INIT_ADMIN_TOKEN")
existing_buckets = []
bucket = ["bsr_bucket", "bsr_final_1m", "bsr_final_5m", "bsr_final_60m", "demo_bsr_bucket", "demo_bsr_final"]
max_attempts = 5
wait_seconds = 5
influxdb_url = "http://influxdb:8086"
headers = {
    "Authorization": f"Token {influxdb_token}", "Content-Type": "application/json",
}

# Function to fetch existing buckets
def fetch_existing_buckets(token):
    response = requests.get("http://influxdb:8086/api/v2/buckets", headers={"Authorization": f"Token {token}"})
    return [b["name"] for b in response.json()["buckets"]]

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

def main():
    # Get DOCKER_INFLUXDB_INIT_ADMIN_TOKEN from environment variables
    org_id = get_orgs()
    url = f"{influxdb_url}/api/v2/buckets"

    # Bucket creation with retries
    for bucket_temp in bucket:
        attempts = 0

        while attempts < max_attempts:
            existing_buckets = fetch_existing_buckets(influxdb_token)

            if bucket_temp not in existing_buckets:
                response = requests.post(
                    url,
                    headers=headers,
                    json={"name": bucket_temp, "orgID": org_id}
                )

                if response.status_code == 201:
                    print(f"{bucket_temp} created.")
                    break
                else:
                    attempts += 1
                    time.sleep(wait_seconds)
            else:
                print(f"{bucket_temp} already exists.")
                break
        else:
            print(f"Failed to create {bucket_temp} after {max_attempts} attempts.")

if __name__ == "__main__":
    main()

