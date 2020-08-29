[![Open Source](https://img.shields.io/badge/-Open%20Source%3F%20Yes%21-3066be?logo=Github&logoColor=white&link=https://github.com/arthur-bryan/pisco)](https://github.com/arthur-bryan/pisco)
[![Status Badge](https://img.shields.io/badge/status-development-3066be)](https://github.com/arthur-bryan/pisco)
![GitHub](https://img.shields.io/github/license/arthur-bryan/pisco?color=blue)
[![GitHub tag (latest by date)](https://img.shields.io/github/v/tag/arthur-bryan/pisco)](https://github.com/arthur-bryan/pisco/tags)
[![Python Badge](https://img.shields.io/badge/-Python%203.7+-3066be?logo=Python&logoColor=white&link=https://www.python.org/)](https://www.python.org/)
![GitHub repo size](https://img.shields.io/github/repo-size/arthur-bryan/pisco)


![pisco](https://user-images.githubusercontent.com/34891953/91322086-b15c9700-e795-11ea-8a30-e7ef610baeef.GIF)


# Pisco
##### Scripts to automate the configuration of Cisco devices.

* Default basic setup
* Change hostnames
* Create/delete VLANs
* View interfaces IP or status
* Setup Telnet/SSH access
* Erase NVRAM
* And more comming soon...

### Installation

Recomended the use of a python virtual environment.

```sh
$ git clone https://github.com/arthur-bryan/pisco
$ cd pisco
$ sudo python3 setup.py install	
```

### Uninstall package and dependencies

```sh
$ sudo python3 -m pip uninstall pisco
```


### Usage examples:

* Make sure the devices have IP, Telnet/SSH vty logins and enable secret configured already.
* On this example, all devices have the same user/pass login and enable secrets.
* By default, the domain name on device will be 'lan.com' but you can specify it using the 
  domain_name property as shown below.

#### The currently avaliable configuration keys are:

- 'DEFAULT_CONFIG': configure exec-timeout, logging synchronous, no ip domain-lookup...
- 'SET_HOSTNAME': change the device hostname.
- 'CREATE_VLAN': create individual or multiple VLANs.
- 'DELETE_VLAN': delete individual or multiple VLANs.
- 'SETUP_SSH_ONLY': set the VTY transport input for SSH access only.
- 'SETUP_TELNET_ONLY': set the VTY transport input for TELNET access only.
- 'SETUP_SSH_TELNET': set the VTY transport input for both SSH and Telnet access.
- 'ERASE_NVRAM': erase the startup-config and vlan.dat
- 'SHOW_INTERFACE_IP': show a brief of the current IP configuration of the interfaces.
- 'SHOW_INTERFACES_STATUS': show the current status of the interfaces.


#### Configuring one device:

```python
from pisco.manager import Manager
from pisco.device import Device

# Create VLANs 10, 20 and 30 on a switch over ssh.

switch1 = Device("10.0.0.10", "admin", "cisco", vty_username="admin")
switch1.connection_protocol = "ssh"
switch1.domain_name = "lab.lan"	# sets the domain name on device.

manager = Manager()
manager.add_device(switch1)
manager.vlans_to_configure = '10', '20', '30' # the number of VLANs to configure (must be set always when configuring VLANs)
manager.configure_devices('CREATE_VLAN')
```

#### Configuring various devices:

```python
from pisco.manager import Manager
from pisco.device import Device

# Enable Telnet and SSH VTY transport inputs and then show the status of the interfaces.

ips = ['10.0.0.10', '10.0.0.11', '10.0.0.12', '10.0.0.13', '10.0.0.14']

manager = Manager()

for ip in ips:
    device = Device(ip, "admin", "cisco", vty_username="admin")
    device.connection_protocol = "telnet"   # connection over telnet
    manager.add_device(device)

manager.configure_devices('DEFAULT_CONFIG', 'SETUP_SSH_TELNET', 'SHOW_INTERFACES_STATUS')	# here the devices won't have the domain name set and default will be "lan.com"
```

#### You can also retrieve de device credentials from the user at runtime (use modules like getpass when prompting passwords).

#### Any help will be welcome.
