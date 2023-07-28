# gve_devnet_thousandeyes_isr_installer

## Contacts
* Charles Llewellyn

## Solution Components
* ThousandEyes
*  Python

## Related Sandbox Environment
This is as a template, project owner to update

This sample code can be tested using a Cisco dCloud demo instance that contains ** *Insert Required Sandbox Components Here* **


## Netconf Setup
On router run the following commands
1. netconf-yang
2. aaa new-model
3. aaa authentication login default local
4. aaa authorizatoin exec default local
5. username netconf privilege 15 password 0 netconf
## Installation/Configuration
1. Insure that NETCONF is running on the devices that you wish to install agent on.
2. Insure that device can be reached via SSH (Protocol that netconf uses)
Replace information in environment file to represent your environment.

```ini
# Netconf Settings
username: exampleusername
password: password123
port: 830
timeout: 10000

# Thousand Eyes Agent Settings
download_url: https://downloads.thousandeyes.com/enterprise-agent/thousandeyes-enterprise-agent-4.4.2.cisco.tar
appid: thousandeyes_enterprise_agent
vlan: 201
token: thousandeyes_token
te_filename: thousandeyes-enterprise-agent-4.4.2.cisco.tar
vpgip: 10.100.152.100
appip: 10.100.152.120

# Example of devices to manage
hosts:
  198.18.130.1:
  198.18.130.2:
  198.18.130.3:
  198.18.130.4:
  198.18.130.5:

```


## Usage

To launch the script use:


    $ python main.py deploy --config environment.ini



# Screenshots

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
