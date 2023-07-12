import json

def calculate_statistics(json_data):
    data = json.loads(json_data)
    
    statistics = {
        "latency": {},
        "hop_count": {}
    }

    for prob_data in data:
        prob_id = prob_data["prb_id"]
        if prob_id not in statistics["latency"]:
            statistics["latency"][prob_id] = []
        if prob_id not in statistics["hop_count"]:
            statistics["hop_count"][prob_id] = []

        for hop in prob_data["result"]:
            for result in hop["result"]:
                if "x" not in result:
                    rtt = result.get("rtt")
                    if rtt is not None:
                        statistics["latency"][prob_id].append(rtt)
                    ttl = result.get("ttl")
                    if ttl is not None:
                        statistics["hop_count"][prob_id].append(ttl)

    for prob_id in statistics["latency"]:
        latency_values = statistics["latency"][prob_id]
        statistics["latency"][prob_id] = {
            "average": sum(latency_values) / len(latency_values),
            "count": len(latency_values)
        }

    for prob_id in statistics["hop_count"]:
        hop_count_values = statistics["hop_count"][prob_id]
        statistics["hop_count"][prob_id] = {
            "average": sum(hop_count_values) / len(hop_count_values),
            "count": len(hop_count_values)
        }

    return statistics

# List to store the statistics from all files
statistics_list = []

# List of file paths
file_paths = ["file3.json"]

# Read and calculate statistics from each file
for file_path in file_paths:
    with open(file_path, "r") as file:
        json_data = file.read()
        statistics = calculate_statistics(json_data)
        statistics_list.append(statistics)

# Write the statistics to a new JSON file
output_file_path = "statistics.json"
with open(output_file_path, "w") as output_file:
    json.dump(statistics_list, output_file, indent=4)

print("Statistics saved to:", output_file_path)


#{
#  "latency": {
#    "prob_id": {
#      "average": valor_da_media,
#      "count": quantidade_de_medicoes
#    },
#   ...
#  },
#  "hop_count": {
#    "prob_id": {
#      "average": valor_da_media,
#      "count": quantidade_de_medicoes
#    },
#    ...
#  }
#}
