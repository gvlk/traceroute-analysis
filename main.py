# Ayron Horz - 149430
# Guilherme Azambuja - 149429
# Pablo Guaicurus - 149449
# Rafaela Barcelos - 149438
# https://github.com/gvlk/traceroute-analysis
# leia o README

from traceroute_parser import TracerouteParser

# stats_88 -> Netflix
# stats_89 -> HBO
# stats_90 -> StarPlus

MEASUREMENTS_PATH = "data/raw_measurements"

if __name__ == '__main__':
    traceroute_parser = TracerouteParser(MEASUREMENTS_PATH)
    traceroute_parser.write_traceroute_data()
    traceroute_parser.generate_csv_tables()
    traceroute_parser.generate_charts()
