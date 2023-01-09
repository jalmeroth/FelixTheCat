import network


def disable_ap_mode():
    """Disable default AP-mode."""
    ap_if = network.WLAN(network.AP_IF)
    ap_if.active(False)
    print("AP-mode disabled.")
    del ap_if


def do_connect(ssid, password):
    """Connect to WiFi."""
    disable_ap_mode()
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("connecting to network...")
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            pass
    print("network config:", wlan.ifconfig())
