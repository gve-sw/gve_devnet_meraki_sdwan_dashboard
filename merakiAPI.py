""" Copyright (c) 2023 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
           https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

#How to retrieve an Meraki api key: https://developer.cisco.com/meraki/api-v1/#!getting-started/find-your-organization-id
#Meraki Dashboard API call documentation: https://developer.cisco.com/meraki/api-v1/#!overview/api-key

# Import Section
import meraki
import os, sys
from dotenv import load_dotenv

# load all environment variables
load_dotenv()

BASE_URL = "https://api.meraki.com/api/v1"

DASHBOARD = meraki.DashboardAPI(
            api_key=os.environ['MERAKI_API_TOKEN'],
            base_url=BASE_URL,
            print_console=False,
            suppress_logging=True)


#API calls
#Organizations
def getOrganizations():
    response = DASHBOARD.organizations.getOrganizations()

    return response

#Get specific organization ID
def getOrganizationId(org_name):
    organizations = getOrganizations()
    for org in organizations:
        if org["name"] == org_name:
            return org["id"]

    return None

#Networks
def getNetworks(org_id):
    response = DASHBOARD.organizations.getOrganizationNetworks(
        org_id, total_pages='all'
    )

    return response

#Get network
def getNetwork(net_id):
    response = DASHBOARD.networks.getNetwork(net_id)

    return response

#Get network devices
def getNetworkRouters(org_id, net_ids):
    response = DASHBOARD.organizations.getOrganizationDevices(org_id, networkIds=net_ids, productTypes=["appliance"])

    return response

def getConfigTemplates(org_id):
    response = DASHBOARD.organizations.getOrganizationConfigTemplates(org_id)

    return response


def getConfigTemplate(org_id, template_id):
    response = DASHBOARD.organizations.getOrganizationConfigTemplate(org_id, template_id)

    return response


def getNetworkDevices(net_id):
    response = DASHBOARD.networks.getNetworkDevices(net_id)

    return response


def getNetworkTraffic(net_id, timespan):
    response = DASHBOARD.networks.getNetworkTraffic(net_id, timespan=timespan)

    return response


def getNetworkClients(net_id, timespan):
    response = DASHBOARD.networks.getNetworkClients(net_id, timespan=timespan)

    return response


def getNetworkVPN(net_id):
    response = DASHBOARD.appliance.getNetworkApplianceVpnSiteToSiteVpn(net_id)

    return response


def getNetworkBandwidth(net_id):
    response = DASHBOARD.appliance.getNetworkApplianceTrafficShaping(net_id)

    return response


def getTopAppliancesByUtilization(org_id):
    response = DASHBOARD.organizations.getOrganizationSummaryTopAppliancesByUtilization(org_id)

    return response


def getAppliancePerformance(router):
    response = DASHBOARD.appliance.getDeviceAppliancePerformance(router)

    return response


def usage():
    print("Usage: merakiAPI.py", file=sys.stderr)
    sys.exit(1)


def main(argv):
    print("This file is for defining functions. Please don't run it on its own. It doesn't do anything.")
    #pprint(getNetworkBandwidth('L_793196484370632441'))
    #top_utilization = getTopAppliancesByUtilization("940024")
    #network_by_utilization = {}
    #for item in top_utilization:
    #    network_id = item["network"]["id"]
    #    utilization = item["utilization"]["average"]["percentage"]

    #    network_by_utilization[network_id] = utilization

    #pprint(network_by_utilization)

if __name__ == "__main__":
    sys.exit(main(sys.argv))

