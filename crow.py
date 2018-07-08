import asyncio
import crow_security
import pprint
import config

email = config.email
password = config.password
mac = config.mac

p = pprint.PrettyPrinter(indent=4)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    with crow_security.Session(email, password) as session:
        # panels = session.get_panels()
        # print("Panels: ", panels)
        panel = session.get_panel(mac)
        print("Panel: ")
        p.pprint(panel)
        # zones = session.get_zones(panel.get('id'))
        # print("Zones: ")
        # p.pprint(zones)
        areas = panel.get_areas()
        p.pprint(areas)

        def on_message(msg):
            print("Message reveived:")
            p.pprint(msg)

    loop.run_until_complete(session.ws_connect(panel.id, on_message))
