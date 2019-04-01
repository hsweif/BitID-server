import soco
import yeelight
from netifaces import interfaces, AF_INET, ifaddresses

if __name__ == '__main__':
    # select interface if needed.
    data = [ifaddresses(i) for i in interfaces()]
    interface = False
    for d in data:
        if d.get(AF_INET):
            # use the WLAN interface
            if d[AF_INET][0]['addr'].startswith('192.168.3'):
                interface = d[AF_INET][0]['addr']
    sonos = list(soco.discover(timeout=10, interface_addr=interface))[0]
    bulb = yeelight.Bulb(yeelight.discover_bulbs(timeout=10, interface=interface)[0].get('ip'))

    try:
        print(sonos)
        if sonos:
            sonos.play_mode = 'REPEAT_ONE'
            sonos.play_uri('http://img.tukuppt.com/newpreview_music/09/01/52/5c89f044e48f61497.mp3')
            sonos.play()
            sonos.volumn = 6

        print(bulb)
        if bulb:
            bulb.toggle()
    except KeyboardInterrupt as e:
        if sonos:
            sonos.stop()
        if bulb:
            bulb.turn_off()