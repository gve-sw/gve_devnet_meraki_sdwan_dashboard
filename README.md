# GVE DevNet Meraki SDWAN Dashboard
This repository contains the code for a Flask app that displays hub and spoke load information from a Meraki organization Specifically, the app shows the network type (hub or spoke), network name, number of clients per network, the up bandwidth limit, the down bandwidth limit, the name of the configuration template if one exists, the utilization percentage if the network is in the top 10 of utilization in the organization, and the number of spokes if the network is a hub. The number of clients, up bandwidth limit, and down bandwidth limit of the hub networks is determined by summing the corresponding information from the spoke networks associated with that hub.

![/IMAGES/meraki_sdwan_dashboard_workflow.png](/IMAGES/meraki_sdwan_dashboard_workflow.png)

## Contacts
* Danielle Stacy

## Solution Components
* Python 3.10
* Flask
* Meraki SDK
* Meraki MX

## Prerequisites
#### Meraki API Keys
In order to use the Meraki API, you need to enable the API for your organization first. After enabling API access, you can generate an API key. Follow these instructions to enable API access and generate an API key:
1. Login to the Meraki dashboard.
2. In the left-hand menu, navigate to `Organization > Settings > Dashboard API access`.
3. Click on `Enable access to the Cisco Meraki Dashboard API`.
4. Go to `My Profile > API access`.
5. Under API access, click on `Generate API key`.
6. Save the API key in a safe place. The API key will only be shown once for security purposes, so it is very important to take note of the key then. In case you lose the key, then you have to revoke the key and a generate a new key. Moreover, there is a limit of only two API keys per profile.

> For more information on how to generate an API key, please click [here](https://developer.cisco.com/meraki/api-v1/#!authorization/authorization). 

> Note: You can add your account as Full Organization Admin to your organizations by following the instructions [here](https://documentation.meraki.com/General_Administration/Managing_Dashboard_Access/Managing_Dashboard_Administrators_and_Permissions).

## Installation/Configuration
1. Clone this repository with `git clone https://github.com/gve-sw/gve_devnet_meraki_sdwan_dashboard.git`.
2. Set up a Python virtual environment. Make sure Python 3 is installed in your environment, and if not, you may download Python [here](https://www.python.org/downloads/). Reminder that this code was written with Python 3.10, so it is recommended to install Python 3.10. Once Python 3 is installed in your environment, you can activate the virtual environment with the instructions found [here](https://docs.python.org/3/tutorial/venv.html).
3. Install the requirements with `pip3 install -r requirements.txt`.
4. Add Meraki API key obtained in the Prerequisites section and the name of the Meraki organization you would like to view to environment variables in the `.env` file.
```
MERAKI_API_TOKEN="provide Meraki API key here"
MERAKI_ORG_NAME="provide Meraki organization name here"
```

## Usage
To start the web app, use the command:
```
$ flask run
```
> Note: If you experience the following runtime error when you try to start the web app after following the above instructions: `RuntimeError: Install Flask with the 'async' extra in order to use async views`, then enter the command `pip3 install 'Flask[async]'` in the console.

Then access the app in your browser of choice at the address `http://127.0.0.1:5000`. 
Once the page loads (it will take a minute due to the number of API calls needed to make for each network in the organization), it will display the network load information about the hub networks. 

![/IMAGES/sdwan_dash_hubs.png](/IMAGES/sdwan_dash_hubs.png)

To see the network load information about the spoke networks, click on the row of the hub network whose spokes you'd like to view.

![/IMAGES/sdwan_dash_spokes.png](/IMAGES/sdwan_dash_spokes.png)

![/IMAGES/0image.png](/IMAGES/0image.png)

### LICENSE

Provided under Cisco Sample Code License, for details see [LICENSE](LICENSE.md)

### CODE_OF_CONDUCT

Our code of conduct is available [here](CODE_OF_CONDUCT.md)

### CONTRIBUTING

See our contributing guidelines [here](CONTRIBUTING.md)

#### DISCLAIMER:
<b>Please note:</b> This script is meant for demo purposes only. All tools/ scripts in this repo are released for use "AS IS" without any warranties of any kind, including, but not limited to their installation, use, or performance. Any use of these scripts and tools is at your own risk. There is no guarantee that they have been through thorough testing in a comparable environment and we are not responsible for any damage or data loss incurred with their use.
You are responsible for reviewing and testing any scripts you run thoroughly before use in any non-testing environment.
