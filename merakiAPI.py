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
    try:
        response = DASHBOARD.organizations.getOrganizationNetworks(org_id, total_pages='all')

        return response
    except Exception as e:
        print("There was an error getting the networks of the organization with org id " + org_id)
        print(e)

        return None


#Get network devices
def getNetworkRouters(org_id, net_ids):
    try:
        response = DASHBOARD.organizations.getOrganizationDevices(org_id, networkIds=net_ids, productTypes=["appliance"])

        return response
    except Exception as e:
        print("There was an error getting the routers from the networks in the organization with org id " + org_id)
        print(e)

        return None


def getConfigTemplate(org_id, template_id):
    try:
        response = DASHBOARD.organizations.getOrganizationConfigTemplate(org_id, template_id)

        return response
    except Exception as e:
        print("There was an error getting the configuration template information with template id " + template_id)
        print(e)

        return None


def getNetworkClients(net_id, timespan):
    try:
        response = DASHBOARD.networks.getNetworkClients(net_id, timespan=timespan, total_pages="all")

        return response
    except Exception as e:
        print("There was an error getting the clients of the network with net id " + net_id)
        print(e)

        return None


def getNetworkVPN(net_id):
    try:
        response = DASHBOARD.appliance.getNetworkApplianceVpnSiteToSiteVpn(net_id)

        return response
    except Exception as e:
        print("There was an error getting the site to site VPN information of the network with net id " + net_id)
        print(e)

        return None


def getNetworkBandwidth(net_id):
    try:
        response = DASHBOARD.appliance.getNetworkApplianceTrafficShapingUplinkBandwidth(net_id)

        if "wan2" in response["bandwidthLimits"].keys():
            up_bandwidth = response["bandwidthLimits"]["wan1"]["limitUp"] + response["bandwidthLimits"]["wan2"]["limitUp"]
            down_bandwidth = response["bandwidthLimits"]["wan1"]["limitDown"] + response["bandwidthLimits"]["wan2"]["limitDown"]
        else:
            up_bandwidth = response["bandwidthLimits"]["wan1"]["limitUp"]
            down_bandwidth = response["bandwidthLimits"]["wan1"]["limitDown"]

        bandwidth_limits = {
            "up": up_bandwidth,
            "down": down_bandwidth
        }

        return bandwidth_limits
    except Exception as e:
        print("There was an error getting the network bandwidth information for network with net id " + net_id)
        print(e)

        return None


def getAppliancePerformance(router):
    try:
        response = DASHBOARD.appliance.getDeviceAppliancePerformance(router)

        return response
    except Exception as e:
        print("There was an error getting the appliance performance of the router " + router)
        print(e)

        return None


def usage():
    print("Usage: merakiAPI.py", file=sys.stderr)
    sys.exit(1)


def main(argv):
    print("This file is for defining functions. Please don't run it on its own. It doesn't do anything.")
    

if __name__ == "__main__":
    sys.exit(main(sys.argv))