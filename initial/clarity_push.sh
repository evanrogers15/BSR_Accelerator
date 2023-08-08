#!/bin/bash

#get org info
curl -o /data/influx/orgs.json -X GET -H "Content-type: application/json" -H "Authorization: Token $DOCKER_INFLUXDB_INIT_ADMIN_TOKEN" 'http://influxdb:8086/api/v2/orgs' 

influx_org_id=($( jq -r '.orgs[].id' /data/influx/orgs.json))
influx_org_name=($( jq -r '.orgs[].name' /data/influx/orgs.json))
clarity_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9eyJzdWIiOiJhZG1pbiIsImlzcyI6Imh0dHBzOi8vcHBtLmNhLmNvbSIsImdlbngiOiI2MTE4ZGVhYWYyODQ2M2M0NmVmNDU2ZDYxZTIzNmI3NiIsImV4cCI6MTY3MjQ0NDgwMCwidXNlciI6MSwianRpIjoiOTQ0M2VmOTItMmQ1YS00MzQxLTk5YWYtYTk5NDllMGRiN2ZjIiwidGVuYW50IjoiY2xhcml0eSJ9.z-9zC7hx6QFXC9KZI8v5Q84TUqjV2O34gCJD1UIlohQ


curl -X 'PATCH' "http://influxdb:8086/api/v2/orgs/$influx_org_id/secrets" \
--header "Content-type: application/json" \
--header "Authorization: Token $DOCKER_INFLUXDB_INIT_ADMIN_TOKEN" \
--data-raw '{
    "clarity_key1": "'$clarity_token'"
  }'

curl -X 'POST' "http://influxdb:8086/api/v2/buckets" \
--header "Content-type: application/json" \
--header "Authorization: Token $DOCKER_INFLUXDB_INIT_ADMIN_TOKEN" \
--data-raw '{
    "name": "clarity_bucket",
    "orgID": "'$influx_org_id'"
  }'

for ((l=0; l<4; l++))
do
curl -X 'POST' \
  "http://influxdb:8086/api/v2/tasks" \
  --header "Authorization: Token $DOCKER_INFLUXDB_INIT_ADMIN_TOKEN" \
  --header 'Content-Type: application/json' \
  --data-raw '{
        "orgID" : "'$influx_org_id'",
        "org" : "bsr",
        "flux": "import \"http\"\nimport \"json\"\n\noption task = {name: \"clarity_openAccess_milestone0\", every: 30m}\n\nfrom(bucket: \"bsr_final_bucket\")\n    |\u003e range(start: -5m)\n    |\u003e filter(fn: (r) =\u003e r[\"appName\"] == \"Browse_Sports_Tickets\")\n    //|\u003e filter(fn: (r) =\u003e r[\"milestone\"] == \"0\")\n    |\u003e pivot(rowKey: [\"_time\"], columnKey: [\"_field\"], valueColumn: \"_value\")\n    |\u003e map(fn: (r) =\u003e ({r with name: \"Check Savings Balance\"}))\n    |\u003e map(fn: (r) =\u003e ({r with _value: r.adjBSR}))\n    |\u003e last()\n    |\u003e map(\n        fn: (r) =\u003e\n            ({r with jsonStr:\n string(\n v:\n json.encode(\n                                v: {\n \"z_bsr_current_score\": r.finalBSR,\n \"name\": r.name,\n \"objectType\": \"bsr_staging\",\n \"z_bsr_data_value\": r.adjBSR,\n \"z_bsr_group\": \"Visa\",\n \"z_bsr_type\": \"web\", },\n ),\n ),\n }),\n    )\n    |\u003e map(\n        fn: (r) =\u003e\n  ({r with statusCode:\n  http.post(\n  url: \"https://cps167.clarityrox.com/ppm/rest/v1/custBsrStagings\",\n  headers: {\n  Authorization: \"Bearer $clarity_token\", \"x-api-ppm-client\": \"EvanAPI\",\n  \"Content-type\": \"application/json\",\n  },\n  data: bytes(v: r.jsonStr),\n  ),\n }),\n )\n    |\u003e to(\n        bucket: \"clarity_bucket\",\n        measurementColumn: \"appName\",\n        tagColumns: [\"pathId\", \"appName\", \"milestone\", \"pathName\"],\n fieldFn: (r) =\u003e ({\"finalBSR\": r._finalBSR, \"adjBSR\": r._adjBSR, \"statusCode\": r.statusCode}),\n    )"
  }' 
done




