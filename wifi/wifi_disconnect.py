import os


os.system("""" echo
    country=GB
    ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
    update_config=1
""")
os.system("ifconfig wlan0 down")
os.system("ifconfig wlan0 up")
