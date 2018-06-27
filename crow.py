import crow
import pprint

email = 'xxx@yyy.com'
password = 'xxxxxxx'
mac = '0000000000'

p = pprint.PrettyPrinter(indent=4)

if __name__ == '__main__':
    with crow.Session(email, password) as session:
        # panels = session.get_panels()
        # print("Panels: ", panels)
        panel = session.get_panel(mac)
        print("Panel: ")
        p.pprint(panel)
        # zones = session.get_zones(panel.get('id'))
        # print("Zones: ")
        # p.pprint(zones)
        areas = session.get_area(panel.get('id'), 0)
        p.pprint(areas)
