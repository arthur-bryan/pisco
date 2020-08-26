.. Pisco documentation master file, created by
   sphinx-quickstart on Wed Aug 26 17:25:27 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Pisco's documentation!
=================================

Scripts to automate the configuration of Cisco devices.
'''''''''''''''''''''''''''''''''''''''''''''''''''''''

- Default basi setup (exec-timeout, logging synchronous, no ip domain-lookup...)
- Change hostnames
- View interfaces IP or status
- Setup Telnet/SSH access
- Erase NVRAM
- And more comming soon...

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Manager
=============

.. automodule:: pisco.manager
    :members:

Device  
=============   

.. automodule:: pisco.device
    :members:

Usage examples:
===============

Configuring one device:
'''''''''''''''''''''''
.. code:: python

    from pisco.manager import Manager
    from pisco.device import Device

    manager = Manager()

    switch1 = Device("10.0.0.10", "admin", "cisco", vty_username="admin")
    switch1.connection_protocol = "ssh"
    switch1.domain_name = 'lab.net'  # set the domain-name (otherwise the default (lan.com) will be set)
    
    manager.add_device(switch1)
    manager.configure_devices()

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
    manager.configure_devices()


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
