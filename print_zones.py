from parser import Map_parser
parsed = Map_parser("maps/easy/03_basic_capacity.txt")
data = parsed.parser()
for name, z in data.zones.items():
    print(name, z.zone_type)
