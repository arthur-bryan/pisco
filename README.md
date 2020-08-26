[![Open Source](https://img.shields.io/badge/-Open%20Source%3F%20Yes%21-3066be?logo=Github&logoColor=white&link=https://github.com/arthur-bryan/pisco)](https://github.com/arthur-bryan/pisco)
[![Status Badge](https://img.shields.io/badge/status-development-3066be)](https://github.com/arthur-bryan/pisco)
![GitHub](https://img.shields.io/github/license/arthur-bryan/pisco?color=blue)
[![GitHub tag (latest by date)](https://img.shields.io/github/v/tag/arthur-bryan/pisco)](https://github.com/arthur-bryan/pisco/tags)
[![Python Badge](https://img.shields.io/badge/-Python%203.7+-3066be?logo=Python&logoColor=white&link=https://www.python.org/)](https://www.python.org/)
![GitHub repo size](https://img.shields.io/github/repo-size/arthur-bryan/pisco)

![pisco](https://usr-images.githubusercontent/34891953/91322086-b15c9700-e795-11ea-8a30-e7ef610baeef.GIF)

# Pisco
##### Scripts to automate the configuration of Cisco devices.

* Change hostnames
* Setup VLANs
* Setup users and passwords
* Setup Telnet/SSH access
* View interfaces info
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
* On this example, all devices have the same user/pass login and enable secrets, and
  all will be accessed over telnet.
* By default, the domain name on device will be 'lan.com' but you can specify it using the 
  domain_name property as shown below.

#### Configuring one device:

```python
switch1 = Device("10.0.0.10", "admin", "cisco", vty_username="admin")
switch1.connection_protocol = "ssh"
switch1.domain_name = "lab.lan"	# sets the domain name on device.

manager = Manager()
manager.add_device(switch1)
manager.configure_devices()
```

#### Configuring various devices:

```python
ips = ['10.0.0.10', '10.0.0.11', '10.0.0.12', '10.0.0.13', '10.0.0.14']

manager = Manager()

for ip in ips:
    device = Device(ip, "admin", "cisco", vty_username="admin")
    device.connection_protocol = "telnet"
    manager.add_device(device)

manager.configure_devices()	# here the devices won't have the domain name set and default will be "lan.com"
```

#### You can also retrieve de device credentials from the user at runtime (use modules like getpass when prompting passwords).

#### Any help will be welcome.

