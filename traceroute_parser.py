from json import loads, dump
from os import listdir
from typing import Dict, List, Union, Optional
from ripe.atlas.sagan import TracerouteResult

ProbeData = List[Dict[str, int]]
ProbesData = Dict[int, ProbeData]
TracerouteData = Dict[str, Union[int, ProbesData]]


class TracerouteParser:

    def __init__(self, measurements_path: str, output_directory: Optional[str] = "") -> None:
        self.measurements_path = measurements_path
        if output_directory:
            self.output_directory = output_directory
        else:
            self.output_directory = measurements_path.split("/")[0]

    @staticmethod
    def parse_traceroute_data(data: List) -> TracerouteData:
        stats: ProbesData = dict()

        for probe_data in data:
            probe = TracerouteResult(probe_data)
            probe_id = int(probe.probe_id)
            if probe_id not in stats:
                stats[probe_id] = list()

            latencies = list()
            for hop in probe.hops:
                if hop.median_rtt:
                    latencies.append(hop.median_rtt)
            average_latency = round(sum(latencies) / len(latencies))

            stats[probe_id].append(
                {
                    "created": probe.created_timestamp,
                    "average_latency": average_latency,
                    "total_hops": probe.total_hops
                }
            )

        return {
            "measurement_id": data[0]["msm_id"],
            "probes": stats
        }

    def write_traceroute_data(self) -> None:
        for file_name in listdir(self.measurements_path):
            with open(f"{self.measurements_path}/{file_name}", "r") as file:
                json_data = file.read()

            traceroute_stats = self.parse_traceroute_data(loads(json_data))
            output_file_path = f"{self.output_directory}/stats_{traceroute_stats['measurement_id']}"

            with open(output_file_path, "w") as output_file:
                dump(traceroute_stats, output_file, indent=4)

            print("Statistics saved to:", output_file_path)
