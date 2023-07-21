# Ayron Horz - 149430
# Guilherme Azambuja - 149429
# Pablo Guaicurus - 149449
# Rafaela Barcelos - 149438
# https://github.com/gvlk/traceroute-analysis
# leia o README

from argparse import ArgumentParser
from traceroute_parser import TracerouteParser

# stats_88 -> Netflix
# stats_89 -> HBO
# stats_90 -> StarPlus

if __name__ == '__main__':
    parser = ArgumentParser(description="Traceroute Analysis Tool")
    parser.add_argument("measurements_path", help="Path to the measurements data directory")
    parser.add_argument("-w", "--write_traceroute_data", action="store_true", help="Write traceroute data")
    parser.add_argument("-c", "--generate_csv_tables", action="store_true", help="Generate CSV tables")
    parser.add_argument("-g", "--generate_charts", action="store_true", help="Generate charts")
    args = parser.parse_args()

    traceroute_parser = TracerouteParser(args.measurements_path)

    if args.write_traceroute_data or not any([args.generate_csv_tables, args.generate_charts]):
        traceroute_parser.write_traceroute_data()

    if args.generate_csv_tables or not any([args.write_traceroute_data, args.generate_charts]):
        traceroute_parser.generate_csv_tables()

    if args.generate_charts or not any([args.write_traceroute_data, args.generate_csv_tables]):
        traceroute_parser.generate_charts()
