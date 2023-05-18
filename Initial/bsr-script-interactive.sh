#!/bin/bash

menu_from_array ()
{
    select value; do
    # Check the selected menu item number
    if [ 1 -le "$REPLY" ] && [ "$REPLY" -le $# ];
    then
    break;
    else
    echo -e "\nWrong selection: Select any number from 1-$#\n"
    fi
    done
}

docker_containers=($(docker ps --format '{{.Names}}' | grep 'api_utility'))
version_options=('url' 'tag')
version_granularity_options=("workflow" "milestone")
calc_aggregation_window_options=(1 5 60)

echo -e "\nSelect BSR API Utility Container from List Below:"
menu_from_array "${docker_containers[@]}"
container=$value

ap_URL=$(docker exec $container bash -c 'echo $appURL')
read -a instances <<< $ap_URL
instance_count="${#instances[@]}" 

for ((m=0; m<$instance_count; m++))
    do
        temp_data=$(docker exec $container bash -c "cat /data/webApp_all_"$m".json")
        temp_webAppTarget+=($( jq -r '.[].webUrlTarget' <<< "$temp_data"))
        temp_webAppTagValue+=($( jq -r '.[].web_tag_value' <<< "$temp_data"))
        temp_webAppName+=($( jq -r '.[].appName' <<< "$temp_data"))
    done

temp_webAppTarget+=($(printf "%s\n" "${temp_webAppTarget[@]}" | sort -u ))
temp_webAppTagValue=($(printf "%s\n" "${temp_webAppTagValue[@]}" | sort -u | tr -d null))
temp_webAppName=($(printf "%s\n" "${temp_webAppName[@]}" | sort -u ))

echo -e "\nPlease select desired calculation version: "
menu_from_array "${version_options[@]}"
version=$value

echo -e "\nCalculation Granularity: "
menu_from_array "${version_granularity_options[@]}"
version_granularity=$value

echo -e "\nAggregation Time Period (in minutes): "
menu_from_array "${calc_aggregation_window_options[@]}"
calc_aggregation_window=$value

echo -e "\nPlease enter Application Name of desired Business Service: \n"
menu_from_array "${temp_webAppName[@]}"
app_name_final=$value

docker exec $container bash -c "./initial/bsr_calc_script.sh $version $version_granularity $value $calc_aggregation_window"