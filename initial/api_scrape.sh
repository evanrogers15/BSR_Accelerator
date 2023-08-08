#!/bin/bash

#process to pull performance metrics from Appneta API continuously
read -a appneta_token <<< $appT
read -a appneta_root_url <<< $appURL
instance_count="${#appneta_token[@]}"
read -a demo_data <<< $demoData

bash /initial/influx_bucket_creation.sh
if [ "$demo_data" = "1" ]; then
  python3 /initial/bsr_data_generator.py &
  python3 /initial/calc_create.py &
fi

while true
do
    for ((l=0; l<$instance_count; l++))
    do
        pathSummary=$(curl -s -X GET -H "Authorization: Token ${appneta_token["$l"]}" -H "Accept: application/json" 'https://'${appneta_root_url["$l"]}'/api/v3/path')
        pathStatus=$(curl -s -X GET -H "Authorization: Token ${appneta_token["$l"]}" -H "Accept: application/json" 'https://'${appneta_root_url["$l"]}'/api/v3/path/status')
        webAppSummary=$(curl -s -X GET -H "Authorization: Token ${appneta_token["$l"]}" -H "Accept: application/json" 'https://'${appneta_root_url["$l"]}'/api/beta/webPath')
        webAppAll=$(curl -s -X GET -H "Authorization: Token ${appneta_token["$l"]}" -H "Accept: application/json" 'https://'${appneta_root_url["$l"]}'/api/v3/webPath/data')
        path_all=$(curl -s -X GET -H "Authorization: Token ${appneta_token["$l"]}" -H "Accept: application/json" 'https://'${appneta_root_url["$l"]}'/api/v3/path/data')
        path_all=$(curl -s -X GET -H "Authorization: Token ${appT}" -H "Accept: application/json" 'https://'${appURL}'/api/v3/path/data')

        #path summary variable creation
        pathName=($(echo "$pathSummary" | jq -r '.[].target'))
        pathID=($(echo "$pathSummary" | jq -r '.[].id'))
        path_applianceName=($(echo "$pathSummary" | jq -r '.[].sourceAppliance'))
        appliance_networkType=($(echo "$pathSummary" | jq -r '.[].networkType'))
        appliance_ispName=($(echo "$pathSummary" | jq -r '.[].ispName | @sh | sub(" "; "_";"g")')) && appliance_ispName=(${appliance_ispName[@]//\'/})
        appliance_connectionType=($(echo "$pathSummary" | jq -r '.[].connectionType'))
        appliance_vpn=($(echo "$pathSummary" | jq -r '.[].vpn'))
        pathName_count="${#pathName[@]}"
        pathTagCategory=($(echo "$pathSummary" | jq '.[].tags[0].category')) && pathTagCategory=("${pathTagCategory[@]//\"/}")
        pathTagValue=($(echo "$pathSummary" | jq '.[].tags[0].value')) && pathTagValue=("${pathTagValue[@]//\"/}")

        #path status variable creation
        pathStatus=($(echo "$pathStatus" | jq -r '.[].status'))

        #web app summary variable creation
        webPathId=($(echo "$webAppSummary" | jq -r '.[].id'))
        applianceName=($(echo "$webAppSummary" | jq -r '.[].location.applianceName'))
        webAppName=($(echo "$webAppSummary" | jq -r '.[].webPathConfig.webAppName | @sh | sub(" "; "_";"g")'))
        webAppName=(${webAppName[@]//\'/}) #remove single quotes from webAppName array objects
        webAppId=($(echo "$webAppSummary" | jq -r '.[].webPathConfig.webAppId'))
        userFlowName=($(echo "$webAppSummary" | jq -r '.[].webPathConfig.userFlow | @sh | sub(" "; "_";"g")'))
        userFlowName=(${userFlowName[@]//\'/}) #remove single quotes from userFlowName array objects
        webPathId_count="${#webPathId[@]}"
        webPathId_status=($(echo "$webAppSummary" | jq -r '.[].statusWithMuted | @sh | sub(" "; "_";"g")')) && webPathId_status=(${webPathId_status[@]//\"/}) && webPathId_status=(${webPathId_status[@]//\'/})
        webAppTarget=($(echo "$webAppSummary" | jq -r '.[].target.url | @sh | sub("https://"; "";"g") | sub("http://"; "";"g")')) && webAppTarget=(${webAppTarget[@]//\:*/}) && webAppTarget=(${webAppTarget[@]//\'/}) && webAppTarget=(${webAppTarget[@]//\//})
        webAppTarget_unique=($(printf "%s\n" "${webAppTarget[@]}" | sort -u))
        webAppTagCategory=($(echo "$webAppSummary" | jq '.[].tags[0].category')) && webAppTagCategory=("${webAppTagCategory[@]//\"/}")
        webAppTagValue=($(echo "$webAppSummary" |jq '.[].tags[0].value')) && webAppTagValue=("${webAppTagValue[@]//\"/}")
        webAppTagValue_unique=($(printf "%s\n" "${webAppTagValue[@]}" | sort -u))


        webAppAll=$(cat <<< "$(echo "$webAppAll" | jq 'sort_by(.webPathId)')")
        webAppAll=$(cat <<< "$(echo "$webAppAll" | jq '.[].milestones[] |= {networkTiming: [.["networkTiming"][-1]], serverTiming: [.["serverTiming"][-1]], browserTiming: [.["browserTiming"][-1]], apdexScore: [.["apdexScore"][-1]], totalTime: [.["totalTime"][-1]], basePageSize: [.["basePageSize"][-1]], statusCode: [.["statusCode"][-1]]} | .[].milestones |= map(select(any(.[])))')")

        for ((w=0; w<$webPathId_count; w++))
        do
            milestone_count=$(echo "$webAppAll" | jq '.['$w'].milestones | length')
            milestoneName=($(echo "$webAppSummary" | jq -r '.['"$w"'].userFlow.milestoneDefinitions[].name | @sh | gsub(":| "; "_"; "g")' | tr -s '_')) && milestoneName=("${milestoneName[@]//\'/}")
            #milestoneName=($(echo "$webAppSummary" | jq -r '.[1].userFlow.milestoneDefinitions[].name | @sh | sub(":|(?<!_) "; "_"; "g")')) && milestoneName=("${milestoneName[@]//\'/}")
            #webAppSummary=$(curl -s -X GET -H "Authorization: Token ${appT}" -H "Accept: application/json" 'https://'${appURL}'/api/beta/webPath')
            applianceName_temp=${applianceName[$w]}
            webAppName_temp=${webAppName[$w]}
            userFlowName_temp=${userFlowName[$w]}
            webPathId_status_temp=${webPathId_status[$w]}
            webAppTarget_temp=${webAppTarget[$w]}
            webAppTagCategory_temp=${webAppTagCategory[$w]}
            webAppTagValue_temp=${webAppTagValue[$w]}
            webAppAll=$(jq '.['"$w"'] += {"applianceName": "'"$applianceName_temp"'"}' <<< "$webAppAll")
            webAppAll=$(jq '.['"$w"'] += {"appName": "'"$webAppName_temp"'"}' <<< "$webAppAll")
            webAppAll=$(jq '.['"$w"'] += {"userFlowName": "'"$userFlowName_temp"'"}' <<< "$webAppAll")
            webAppAll=$(jq '.['"$w"'] += {"webPathStatus": "'"$webPathId_status_temp"'"}' <<< "$webAppAll")
            webAppAll=$(jq '.['"$w"'] += {"webUrlTarget": "'"$webAppTarget_temp"'"}' <<< "$webAppAll")
            webAppAll=$(jq '.['"$w"'] += {"web_tag_category": "'"$webAppTagCategory_temp"'"}' <<< "$webAppAll")
            webAppAll=$(jq '.['"$w"'] += {"web_tag_value": "'"$webAppTagValue_temp"'"}' <<< "$webAppAll")
            for ((j=0; j<$milestone_count; j++))
            do
                milestoneName_temp=${milestoneName[$j]}
                webAppAll=$(jq '.['$w'].milestones['$j'] += {"milestoneName": "'"$milestoneName_temp"'"}' <<< "$webAppAll")
                webAppAll=$(jq '.['$w'].milestones['$j'] += {"milestone": '$j'}' <<< "$webAppAll")
            done
        done

        path_all=$(cat <<< "$(echo "$path_all" | jq 'sort_by(.pathId)')")
        path_all=$(cat <<< "$(echo "$path_all" | jq '.[].data.totalCapacity |= [.[-1]] | .[].data.utilizedCapacity |= [.[-1]] | .[].data.availableCapacity |= [.[-1]] | .[].data.latency |= [.[-1]] | .[].data.dataJitter |= [.[-1]] | .[].data.dataLoss |= [.[-1]] | .[].data.voiceJitter |= [.[-1]] | .[].data.voiceLoss |= [.[-1]] | .[].data.mos |= [.[-1]] | .[].data.rtt |= [.[-1]] | .[].dataInbound.totalCapacity |= [.[-1]] | .[].dataInbound.utilizedCapacity |= [.[-1]] | .[].dataInbound.availableCapacity |= [.[-1]] | .[].dataInbound.dataJitter |= [.[-1]] | .[].dataInbound.dataLoss |= [.[-1]] | .[].dataInbound.voiceJitter |= [.[-1]] | .[].dataInbound.voiceLoss |= [.[-1]] | .[].dataInbound.mos |= [.[-1]] | .[].dataInbound.rtt |= [.[-1]] | .[].dataInbound.latency |= [.[-1]] | .[].dataOutbound.totalCapacity |= [.[-1]] | .[].dataOutbound.utilizedCapacity |= [.[-1]] | .[].dataOutbound.availableCapacity |= [.[-1]] | .[].dataOutbound.dataJitter |= [.[-1]] | .[].dataOutbound.dataLoss |= [.[-1]] | .[].dataOutbound.voiceJitter |= [.[-1]] | .[].dataOutbound.voiceLoss |= [.[-1]] | .[].dataOutbound.mos |= [.[-1]] | .[].dataOutbound.rtt |= [.[-1]] | .[].dataOutbound.latency |= [.[-1]]')")

        for ((p=0; p<$pathName_count; p++))
        do
            pathName_temp=${pathName[$p]}
            pathStatus_temp=${pathStatus[$p]}
            pathTagCategory_temp=${pathTagCategory[$p]}
            pathTagValue_temp=${pathTagValue[$p]}
            path_applianceName_temp=${path_applianceName[$p]}
            appliance_connectionType_temp=${appliance_connectionType[$p]}
            appliance_ispName_temp=${appliance_ispName[$p]}
            appliance_networkType_temp=${appliance_networkType[$p]}
            appliance_vpn_temp=${appliance_vpn[$p]}
            path_all="$(jq '.['$p'] += {"applianceName": "'"$path_applianceName_temp"'"}' <<< "$path_all")"
            path_all="$(jq '.['$p'] += {"connectionType": "'"$appliance_connectionType_temp"'"}' <<< "$path_all")"
            path_all="$(jq '.['$p'] += {"ispName": "'"$appliance_ispName_temp"'"}' <<< "$path_all")"
            path_all="$(jq '.['$p'] += {"networkType": "'"$appliance_networkType_temp"'"}' <<< "$path_all")"
            path_all="$(jq '.['$p'] += {"vpn": "'"$appliance_vpn_temp"'"}' <<< "$path_all")"
            path_all="$(jq '.['$p'] += {"pathUrlTarget": "'"$pathName_temp"'"}' <<< "$path_all")"
            path_all="$(jq '.['$p'] += {"pathStatus": "'"$pathStatus_temp"'"}' <<< "$path_all")"
            path_all="$(jq '.['$p'] += {"path_tag_category": "'"$pathTagCategory_temp"'"}' <<< "$path_all")"
            path_all="$(jq '.['$p'] += {"path_tag_value": "'"$pathTagValue_temp"'"}' <<< "$path_all")"
        done
        echo "$webAppAll" > /data/webApp_all_"$l".json
        echo "$path_all" > /data/path_all_"$l".json
    done
    bash /initial/influx_bucket_creation.sh
    sleep 60
done
