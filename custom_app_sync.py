#!/usr/bin/env python3 

###############################################################
#### Custom App sync between Prisma Access and Prisma SDWAN
#### Author: Darshna Subashchandran
################################################################

import prisma_sase
import time
import cloudgenix
import ipaddress
from urllib.parse import urlparse

PRISMASASE_CLIENT_ID ="ds-alerting-automation@1228584868.iam.panserviceaccount.com"
PRISMASASE_CLIENT_SECRET="37f1fed4-37a1-441c-b074-01a697c8a1cd"
TSGID = 1228584868

#Login to controller
sdk = prisma_sase.API(controller="https://api.sase.paloaltonetworks.com", ssl_verify=False)
sdk.set_debug(3)
sdk.interactive.login_secret(client_id=PRISMASASE_CLIENT_ID, client_secret=PRISMASASE_CLIENT_SECRET, tsg_id=TSGID)

#Define Globals
pa_custom_app_list = []
synced_app_list = []
app_name_list = []
reduced_sdwan_app_functionality_list = []


#Get the Applications from Prisma Access
url = "https://api.sase.paloaltonetworks.com/sse/config/v1/applications?folder=Shared&limit=5000"
sdk.remove_header('X-PANW-Region')
resp = sdk.rest_call(url=url, method="GET")
#prisma_sase.jd(resp)
cnt = 0

if resp.cgx_status:
    datalist = resp.json()['data']
    for data in datalist:
        try:
            id = data["id"]
            pa_custom_app_list.append(data)
            cnt +=1
        except:
            pass

#Pull all apps tagged with pa-synced-custom-app
resp = sdk.get.appdefs()
if resp.cgx_status:
    applist = resp.cgx_content.get("items", None)
    for app in applist:
        try:
            if app["tags"] == ["pa-synced"]:
                synced_app_list.append(app["display_name"])
                
        except:
            pass

else:
    pass


#Extract the relevant payload from PA custom App and use it to create Prisma SDWAN App
#The Custom Apps already created in Prisma SDWAN or omitted.
for pa_custom_app in pa_custom_app_list:
    
    #Update the flag
    skip_app = False

    domain_name = ""
    domain_name_list = []
   
    
    try:
        app_name = pa_custom_app["name"]
        signatures = pa_custom_app["signature"]
        domain_flag = False

        if app_name in synced_app_list:
            skip_app = True

        
        for signature in signatures:            
            try:
                signature_and_conditions = signature["and_condition"]
                for signature_and_condition in signature_and_conditions:
                    signature_or_conditions = signature_and_condition["or_condition"]
                    for signature_or_condition in signature_or_conditions:
                        context = signature_or_condition["operator"]["pattern_match"]["context"]
                        if context in ["http-req-host-header", "http-req-headers", "ssl-req-chello-sni","ssl-rsp-certificate"]:                            
                            domain_name = signature_or_condition["operator"]["pattern_match"]["pattern"]
                            #check domain name for ip address
                            new_domain_name = domain_name.replace('\\','')
                            new_domain_name = new_domain_name.replace('\\', '')
                            try:
                                ip_object = ipaddress.ip_address(new_domain_name)
                            except:
                                domain_flag = True
                                if new_domain_name[0] == "*":
                                    modified_domain_name = new_domain_name[1:]
                                elif new_domain_name[0:2] == ".*":
                                    modified_domain_name = new_domain_name[2:]
                                else:
                                    modified_domain_name = new_domain_name[0:]

                                domain_name_list.append(modified_domain_name)
                            try: 
                                qualifier = signature_or_condition["operator"]["pattern_match"]["qualifier"]
                                if skip_app!= True:
                                    reduced_sdwan_app_functionality_list.append(app_name)
                            except:
                                pass                                
                        else:
                            if domain_flag == True:
                                if skip_app!=True:
                                    reduced_sdwan_app_functionality_list.append(app_name)
                            else:
                                skip_app = True
                            
            except:
                skip_app = True
    except:
        skip_app = True
    
    domain_name_list = list(set(domain_name_list))


    #Max allowed domains in a single app in SDWAN is 16, if PA domain list > 16 , skip app config.
    if len(domain_name_list) > 16:
        skip_app = True


    #Replicate the app from Prisma Access and Prisma SDWAN if the config can be replicated.
    if skip_app!=True:
        null = None
        true = True
        false = False
        app_name_list.append(pa_custom_app["name"])
        payload = {
            "tags": [
                "pa-synced"
            ],
            "description": null,
            "app_type": "custom",
            "display_name": pa_custom_app["name"],
            "abbreviation": pa_custom_app["name"][0:3],
            "domains": domain_name_list,
            "transfer_type": "transactional",
            "ingress_traffic_pct": 50,
            "conn_idle_timeout": 3600,
            "path_affinity": "strict",
            "tcp_rules": null,
            "udp_rules": null,
            "ip_rules": null,
            "session_timeout": null,
            "aggregate_flows": null,
            "order_number": 1,
            "overrides_allowed": null,
            "system_app_overridden": null,
            "parent_id": null,
            "use_parentapp_network_policy": null,
            "is_deprecated": null,
            "app_unreachability_detection": true,
            "network_scan_application": false,
            "p_sub_category": null,
            "supported_engines": null,
            "p_parent_id": null,
            "category": pa_custom_app["category"],
            "p_category": "saas"
        }
        

        resp = sdk.post.appdefs(data=payload)
        sdk.set_debug(3)
        if resp.cgx_status:
            print("SUCCESS: Custom App {} created".format(pa_custom_app["name"]))
        else:
            app_name_list.remove(pa_custom_app["name"])
            print("ERR: Could not create Custom App {}".format(pa_custom_app["name"]))
          

print("\n Apps successfully replicated from Prisma Access to Prisma SDWAN: {}".format(app_name_list))
print("\n Apps replicated from Prisma Access to Prisma SDWAN with reduced configuration : {}".format(list(set(reduced_sdwan_app_functionality_list))))
        



