.. Pisco documentation master file, created by
   sphinx-quickstart on Wed Aug 26 17:25:27 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Pisco's documentation!
=================================

Scripts to automate the configuration of Cisco devices.
'''''''''''''''''''''''''''''''''''''''''''''''''''''''

- Default basic setup
- Change hostnames
- Create/delete VLANs
- View interfaces IP or status
- Setup Telnet/SSH access
- Erase NVRAM
- And more comming soon...

.. toctree::
   :maxdepth: 2
   :caption: Contents:

pisco - Manager
===============

.. automodule:: pisco.manager
    :members:

pisco - Device  
===============   

.. automodule:: pisco.device
    :members:

Usage examples:
===============

The currently avaliable configuration keys are:
'''''''''''''''''''''''''''''''''''''''''''''''

-  'DEFAULT\_CONFIG': configure exec-timeout, logging synchronous, no ip domain-lookup...
-  'SET\_HOSTNAME': change the device hostname.
-  'CREATE\_VLAN': create individual or multiples VLANs.
-  'DELETE\_VLAN': delete individual or multiples VLANs.
-  'SETUP\_SSH\_ONLY': set the VTY transport input for SSH access only.
-  'SETUP\_TELNET\_ONLY': set the VTY transport input for TELNET access only.
-  'SETUP\_SSH\_TELNET': set the VTY transport input for both SSH and Telnet access.
-  'ERASE\_NVRAM': erase the startup-config and vlan.dat 
-  'SHOW\_INTERFACE\_IP': show a brief of the current IP configuration of the interfaces.
-  'SHOW\_INTERFACES\_STATUS': show the current status of the interfaces.

Configuring one device:
'''''''''''''''''''''''
.. code:: python

    from pisco.manager import Manager
    from pisco.device import Device

    # Creating VLANs 10, 20 and 30 on a switch over SSH
    manager = Manager()

    switch1 = Device("10.0.0.10", "admin", "cisco", vty_username="admin")
    switch1.connection_protocol = "ssh"
    switch1.domain_name = 'lab.net'  # set the domain-name (otherwise the default (lan.com) will be set)
    
    manager.add_device(switch1)
    manager.vlans_to_configure = '10', '20', '30'  # set the VLAN numbers to configure (needed when setting up VLANs)
    manager.configure_devices('CREATE_VLAN')

Configuring various devices:
''''''''''''''''''''''''''''
.. code:: python

    from pisco.manager import Manager
    from pisco.device import Device
     
    ips = ['10.0.0.10','10.0.0.12','10.0.0.14','10.0.0.5']
    manager = Manager()
 
    for ip in ips:
        device = Device("10.0.0.10", "admin", "cisco", vty_username="admin")
        device.connection_protocol = "ssh"
        manager.add_device(device)
    manager.configure_devices('DEFAULT_CONFIG', 'SETUP_SSH_TELNET', 'SHOW_INTERFACES_IP')


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
