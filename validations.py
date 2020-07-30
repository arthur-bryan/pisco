def validate_ip(ip):
    result = True
    splitted_ip = ip.split('.')
    if len(splitted_ip) != 4:
        result = False
        raise ValueError("[!] Invalid IP!")
    for octet in splitted_ip:
        if int(octet) < 0 or int(octet) > 255:
            result = False
            raise ValueError("[!] Invalid IP!")
    return result, ip

