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

# Import Section
from flask import Flask, render_template, request
import datetime
import requests
from dotenv import load_dotenv
import os
import merakiAPI
import traceback
import asyncio
from aiolimiter import AsyncLimiter

# load all environment variables
load_dotenv()
ORG_NAME = os.environ["MERAKI_ORG_NAME"]


# Global variables
app = Flask(__name__)

limiter = AsyncLimiter(10, 1)
semaphore = asyncio.Semaphore(value=10)


# Methods
# Returns location and time of accessing device
def getSystemTimeAndLocation():
    # request user ip
    userIPRequest = requests.get('https://get.geojs.io/v1/ip.json')
    userIP = userIPRequest.json()['ip']

    # request geo information based on ip
    geoRequestURL = 'https://get.geojs.io/v1/ip/geo/' + userIP + '.json'
    geoRequest = requests.get(geoRequestURL)
    geoData = geoRequest.json()

    #create info string
    location = geoData['country']
    timezone = geoData['timezone']
    current_time=datetime.datetime.now().strftime("%d %b %Y, %I:%M %p")
    timeAndLocation = "System Information: {}, {} (Timezone: {})".format(location, current_time, timezone)

    return timeAndLocation

# separates the hubs and spokes
async def getHubsAndSpokes(net_id, hubs_to_spokes, spokes_to_hubs, semaphore):
    await semaphore.acquire()
    async with limiter:
        vpn_info = merakiAPI.getNetworkVPN(net_id)
        # if network is a hub, add the network id as a key to the hubs_to_spokes dict - spokes to be added later
        if vpn_info["mode"] == "hub":
            hubs_to_spokes[net_id] = []
        # if network is a spoke, add the network id as a key to the spokes_to_hubs dict and assign its value to be the list of associated hubs
        elif vpn_info["mode"] == "spoke":
            spokes_to_hubs[net_id] = vpn_info["hubs"]

        semaphore.release()

# get the config template name
async def getConfigTemplateName(org_id, template_id, network_info, semaphore):
    await semaphore.acquire()
    async with limiter:
        template = merakiAPI.getConfigTemplate(org_id, template_id)
        template_name = template["name"]
        network_info["template"] = template_name

        semaphore.release()

# get the network bandwidth limits of the spoke and then add it to the total bandwidth for the hub
async def getNetworkBandwidthLimits(net_id, spoke_info, hub_info, semaphore):
    await semaphore.acquire()
    async with limiter:
        network_bandwidth = merakiAPI.getNetworkBandwidth(net_id)
        spoke_info["bandwidth_limit_up"] = network_bandwidth["globalBandwidthLimits"]["limitUp"]
        spoke_info["bandwidth_limit_down"] = network_bandwidth["globalBandwidthLimits"]["limitDown"]

        hub_info["bandwidth_limit_up"] += spoke_info["bandwidth_limit_up"]
        hub_info["bandwidth_limit_down"] += spoke_info["bandwidth_limit_down"]

        semaphore.release()

# get the total clients for a spoke and then add it to the total clients in the hub
async def getTotalClients(net_id, spoke_info, hub_info, semaphore):
    await semaphore.acquire()
    async with limiter:
        clients = merakiAPI.getNetworkClients(net_id, 86400)
        num_clients = len(clients)
        spoke_info["num_clients"] = num_clients
        hub_info["num_clients"] += num_clients

        semaphore.release()


##Routes
#Instructions

#Index
@app.route('/')
async def meraki():
    try:
        # Get the organization ID and networks in that organization specified in .env
        org_id = merakiAPI.getOrganizationId(ORG_NAME)
        networks = merakiAPI.getNetworks(org_id)
        net_dict = {} # map net_id to networks to stop making so many API calls
        for net in networks:
            net_dict[net["id"]] = {key: net[key] for key in net if key != "id"}

        top_utilization = merakiAPI.getTopAppliancesByUtilization(org_id)
        for item in top_utilization:
            network_id = item["network"]["id"]
            utilization = item["utilization"]["average"]["percentage"]
            net_dict[network_id]["utilization"] = utilization

        hubs_to_spokes = {} # map the hub network ids to their spoke networks
        spokes_to_hubs = {} # map spoke network ids to their hub networks

        tasks = []

        # iterate through the networks to get the VPN information for the applicable networks
        for network in networks:
            net_id = network["id"]
            # the network VPN information can only be retrieved from networks with MX appliances
            if "appliance" in network["productTypes"]:
                tasks.append(getHubsAndSpokes(net_id, hubs_to_spokes, spokes_to_hubs, semaphore))

        await asyncio.wait(tasks)
        # some spoke networks have no associated hub (make it make sense idk), these spokes will be grouped under the key "None" in the hubs_to_spokes dict
        hubs_to_spokes["None"] = []

        # iterate through the spokes in the spokes_to_hubs dict and their corresponding hubs
        for spoke in spokes_to_hubs:
            for hub in spokes_to_hubs[spoke]:
                # if the hub is not None, add it to the list of spokes associated with the hub in the hubs_to_spokes dict
                if hub["hubId"] is not None:
                    hubs_to_spokes[hub["hubId"]].append(spoke)
                # if the hub is None, then it will be grouped under the key "None" in the hubs_to_spokes dict
                else:
                    hubs_to_spokes["None"].append(spoke)

        hubs_and_spokes_structure = [] # this dictionary will pass the necessary information to the web page

        tasks = []

        # iterate through the hubs in the hubs_to_spokes dict and then retrieve the network information
        for hub in hubs_to_spokes:
            hub_network_info = {} # this dictionary will hold the necessary network information for the hub - then it will be appended to the hubs_and_spokes_structure
            hub_network_info["id"] = hub

            # if hub is not None then we can get network information about it
            if hub != "None":
                if "utilization" in net_dict[hub].keys():
                    hub_network_info["utilization"] = net_dict[hub]["utilization"]
                else:
                    hub_network_info["utilization"] = ""

                hub_network_info["name"] = net_dict[hub]["name"]

                # if the hub network is bound to a configuration template, then we need to get the template name to add to the hub_network_info dict
                if net_dict[hub]["isBoundToConfigTemplate"]:
                    template_id = net_dict[hub]["configTemplateId"]
                    tasks.append(getConfigTemplateName(org_id, template_id, hub_network_info, semaphore))
                else:
                    hub_network_info["template"] = None

                # set the clients and bandwidth variables to 0 for the hubs before summing up the total of the spokes
                hub_network_info["num_clients"] = 0
                hub_network_info["bandwidth_limit_up"] = 0
                hub_network_info["bandwidth_limit_down"] = 0

            # if the hub is None, then there is no network information to be retrieved
            else:
                hub_network_info["name"] = "None"
                hub_network_info["template"] = "None"
                hub_network_info["num_clients"] = 0
                hub_network_info["bandwidth_limit_up"] = 0
                hub_network_info["bandwidth_limit_down"] = 0
                hub_network_info["utilization"] = ""

            # the spokes key of the hub_network_info dict will be a list of all the spoke network information
            hub_network_info["spokes"] = []
            # iterate through spokes associated with the hub
            for spoke in hubs_to_spokes[hub]:
                spoke_network_info = {} # this dictionary will hold the necessary network information for the spoke - then it will be appended to the hub_network_info["spokes] list
                if "utilization" in net_dict[spoke].keys():
                    spoke_network_info["utilization"] = net_dict[spoke]["utilization"]
                else:
                    spoke_network_info["utilization"] = ""
                    
                spoke_network_info["id"] = spoke

                spoke_network_info["name"] = net_dict[spoke]["name"]

                # if the spoke network is bound to a configuration template, then we need to get the template name to add to the spoke_network_info dict
                if net_dict[spoke]["isBoundToConfigTemplate"]:
                    template_id = net_dict[spoke]["configTemplateId"]
                    tasks.append(getConfigTemplateName(org_id, template_id, spoke_network_info, semaphore))

                    # if the network is bound to a template, then we have to make the bandwidth API call with the template id
                    # calculate the network bandwidth of the spoke then add it to the spoke_network_info dict (there is a up and down limit)
                    tasks.append(getNetworkBandwidthLimits(template_id, spoke_network_info, hub_network_info, semaphore))
                else:
                    spoke_network_info["template"] = None

                    # the network bandwidth API call only works with networks not bound to a template
                    tasks.append(getNetworkBandwidthLimits(spoke, spoke_network_info, hub_network_info, semaphore))

                # calculate the number of network clients associated with the spoke in the last 24 hours and then add it to the spoke_network_info dict
                tasks.append(getTotalClients(spoke, spoke_network_info, hub_network_info, semaphore))

                

                # add this spoke to the list of spokes associated with the hub
                hub_network_info["spokes"].append(spoke_network_info)

            # add key to hub_network_info that shows the total number of spokes associated with the hub
            hub_network_info["num_spokes"] = len(hub_network_info["spokes"])

            # add the hub with all its information and list of spokes to the hubs_and_spokes_structure list
            hubs_and_spokes_structure.append(hub_network_info)

        await asyncio.wait(tasks)
        
        return render_template('merakiAPI.html', org_name=ORG_NAME, hubs_and_spokes=hubs_and_spokes_structure, hiddenLinks=False, timeAndLocation=getSystemTimeAndLocation())
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        return render_template('merakiAPI.html', hiddenLinks=False, error=True, errormessage="", errorcode=e, timeAndLocation=getSystemTimeAndLocation())


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
