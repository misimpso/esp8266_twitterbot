import network
import ntptime

sta_if = network.WLAN(network.STA_IF)

if not sta_if.isconnected():
    print("Connecting to network ...")
    sta_if.active(True)
    sta_if.connect("The Internet", "honeybunny")
    while not sta_if.isconnected():
        pass
    print("Connected!")

ntptime.settime()
