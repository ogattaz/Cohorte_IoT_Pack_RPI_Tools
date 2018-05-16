import os

ssid="Y.Phone"
password="Danst0ncu1"

os.system("""" echo
    country=GB
    ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
    update_config=1
""")
os.system("wpa_passphrase '{}' '{}' << /etc/wpa_supplicant/wpa_supplicant.conf".format(ssid,password))
os.system("wpa_cli -i wlan0 reconfigure")
os.system("dhclient wlan0")
