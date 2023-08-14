import multiprocessing

from modules.influx import create_buckets, get_orgs
from modules.bsr_tasks import bsr_send_flux_task_continous, bsr_send_calculation_backfill, bsr_demo_send_backfill_data, bsr_demo_create_continous_data, bsr_real_send_backfill_data
import argparse
import os
import threading

import os
import shutil

def main():
    # Create directories
    os.makedirs('/data/influx', exist_ok=True)  # Create /data/influx if it doesn't exist

    # Copy files
    shutil.copy2('/initial/grafana.ini', '/config/grafana.ini')  # Copy with metadata
    shutil.copy2('/initial/telegraf.conf', '/config/telegraf.conf')  # Copy with metadata
    shutil.copy2('/initial/influxdb_ds.yml', '/config/influxdb_ds.yml')  # Copy with metadata

    bucket = ["bsr_bucket", "bsr_final_1m", "bsr_final_5m", "bsr_final_60m", "demo_bsr_bucket", "demo_bsr_final"]

    if 'DOCKER_INFLUXDB_INIT_ADMIN_TOKEN' in os.environ:
        # Environment variable exists
        var_value = os.environ['DOCKER_INFLUXDB_INIT_ADMIN_TOKEN']
        influxdb_token = var_value
    else:
        print("Environment variable not found")

    org_id = get_orgs()
    create_buckets(org_id, bucket)

    background_demo_data = multiprocessing.Process(target=bsr_demo_create_continous_data(influxdb_token))
    background_demo_data.start()

    bsr_demo_send_backfill_data(influxdb_token, 60)

    raw_bucket = "demo_bsr_bucket"
    final_bucket = "demo_bsr_final"

    bsr_send_flux_task_continous(org_id=org_id, name_value="banking_savings", raw_bucket_value=raw_bucket,
                       final_bucket_value=final_bucket, tag_category="bsr", tag_value="banking_savings")
    bsr_send_flux_task_continous(org_id=org_id, name_value="banking_create_checking", raw_bucket_value=raw_bucket,
                       final_bucket_value=final_bucket, tag_category="bsr", tag_value="banking_create_checking")
    bsr_send_flux_task_continous(org_id=org_id, name_value="banking_pay_bills", raw_bucket_value=raw_bucket,
                       final_bucket_value=final_bucket, tag_category="bsr", tag_value="banking_pay_bills")
    bsr_send_flux_task_continous(org_id=org_id, name_value="banking_transfer", raw_bucket_value=raw_bucket,
                       final_bucket_value=final_bucket, tag_category="bsr", tag_value="banking_transfer")

    bsr_send_calculation_backfill(org_id=org_id, name_value="banking_savings", raw_bucket_value=raw_bucket,
                                 final_bucket_value=final_bucket, tag_category="bsr", tag_value="banking_savings", backload_h_r_value=60)
    bsr_send_calculation_backfill(org_id=org_id, name_value="banking_create_checking", raw_bucket_value=raw_bucket,
                                  final_bucket_value=final_bucket, tag_category="bsr", tag_value="banking_create_checking",
                                  backload_h_r_value=60)
    bsr_send_calculation_backfill(org_id=org_id, name_value="banking_pay_bills", raw_bucket_value=raw_bucket,
                                  final_bucket_value=final_bucket, tag_category="bsr",
                                  tag_value="banking_pay_bills", backload_h_r_value=60)
    bsr_send_calculation_backfill(org_id=org_id, name_value="banking_transfer", raw_bucket_value=raw_bucket,
                                  final_bucket_value=final_bucket, tag_category="bsr",
                                  tag_value="banking_transfer", backload_h_r_value=60)


if __name__ == "__main__":
    main()
