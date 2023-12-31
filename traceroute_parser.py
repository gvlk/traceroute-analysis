from csv import writer, DictWriter, DictReader
from datetime import datetime
from json import load, loads, dump
from os import listdir
from re import search
from typing import Dict, List, Union, Optional

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from requests import get
from ripe.atlas.sagan import TracerouteResult

ProbeData = List[Dict[str, int]]
ProbesData = Dict[int, Dict[str, Union[str, ProbeData]]]
TracerouteData = Dict[str, Union[int, ProbesData]]


class TracerouteParser:
    MEASUREMENTS = {
        57017288: "Netflix",
        57017289: "HBO",
        57017290: "StarPlus",
    }

    COLOR_SET = {
        "#1f77b4",  # Dark Blue
        "#ff7f0e",  # Dark Orange
        "#2ca02c",  # Dark Green
        "#d62728",  # Dark Red
        "#9467bd",  # Dark Purple
        "#8c564b",  # Dark Brown
        "#e377c2",  # Pink
        "#7f7f7f",  # Dark Gray
        "#bcbd22",  # Dark Yellow
        "#17becf",  # Light Blue
        "#ffbb78",  # Light Orange
        "#98df8a",  # Light Green
        "#ff9896",  # Light Red
        "#c5b0d5",  # Light Purple
        "#c49c94",  # Light Brown
        "#f7b6d2",  # Light Pink
        "#c7c7c7",  # Light Gray
        "#dbdb8d",  # Light Yellow
    }

    def __init__(self, measurements_path: str, output_directory: Optional[str] = "") -> None:
        self.measurements_path = measurements_path
        if output_directory:
            self.output_directory = output_directory
        else:
            self.output_directory = measurements_path.split("/")[0]

        self.probe_origin = dict()

    def parse_raw_data(self, data: List) -> TracerouteData:
        """
        Recebe o arquivo JSON original e retorna um novo JSON contendo apenas o relevante para o projeto.
        """
        stats: ProbesData = dict()

        for probe_data in data:
            probe = TracerouteResult(probe_data)
            probe_id = int(probe.probe_id)
            if probe_id not in stats:
                stats[probe_id] = {
                    "origin": self.get_location(probe.source_address, probe_id),
                    "data": list()
                }

            latencies = list()
            for hop in probe.hops:
                if hop.median_rtt:
                    latencies.append(hop.median_rtt)
            average_latency = round(sum(latencies) / len(latencies))

            # Hops sem resposta não são contados.
            stats[probe_id]["data"].append(
                {
                    "created": probe.created_timestamp,
                    "average_latency": average_latency,
                    "total_hops": probe.total_hops,
                }
            )

        filepath = f"{self.output_directory}/probe_origin.json"
        with open(filepath, "w") as output_file:
            dump(self.probe_origin, output_file, indent=4, ensure_ascii=False)

        return {
            "measurement_id": data[0]["msm_id"],
            "probes": stats
        }

    def write_traceroute_data(self) -> None:
        """
        Gera arquivos JSON que contem as informações relevantes para a análise com base nos arquivos de medições
        exportados pelo RIPE Atlas.
        """
        for file_name in listdir(self.measurements_path):
            with open(f"{self.measurements_path}/{file_name}", "r") as file:
                json_data = file.read()

            traceroute_stats = self.parse_raw_data(loads(json_data))

            filepath = f"{self.output_directory}/stats_{traceroute_stats['measurement_id']}.json"
            with open(filepath, "w") as output_file:
                dump(traceroute_stats, output_file, indent=4, ensure_ascii=False)

            print(f"stats_{traceroute_stats['measurement_id']}.json saved at {self.output_directory}")

    def generate_csv_tables(self) -> None:
        """
        Gera tabelas .csv com base nos arquivos JSON gerados pelo método write_traceroute_data().
        """
        for file_name in listdir(self.output_directory):
            if file_name[-5:] != ".json" or file_name[:5] != "stats":
                continue

            with open(f"{self.output_directory}/{file_name}", "r") as input_file:
                json_data = input_file.read()
            measurement_data: TracerouteData = loads(json_data)

            data = [
                [
                    "Probe_ID", "Origin", "Average_Latency", "Total_Hops", "Created_At"
                ]
            ]

            for probe_id, probe_info in measurement_data["probes"].items():
                origin = probe_info["origin"]
                for probe_sample in probe_info["data"]:
                    timestamp = probe_sample["created"]
                    data.append(
                        [
                            probe_id,
                            origin,
                            probe_sample["average_latency"],
                            probe_sample["total_hops"],
                            datetime.fromtimestamp(timestamp).strftime("%H:%M %d/%m/%y")
                        ]
                    )

            filepath = f"{self.output_directory}/table_{measurement_data['measurement_id']}.csv"
            with open(filepath, mode="w", newline="") as output_file:
                writer(output_file, delimiter=";").writerows(data)

            print(f"table_{measurement_data['measurement_id']}.csv saved at {self.output_directory}")

    def generate_charts(self) -> None:
        """
        Gera gráficos baseados nas informações das tabelas .csv geradas pelo método generate_csv_tables(). Uma única
        imagem será gerada para cada tabela.
        """
        for file_name in listdir(self.output_directory):
            if file_name[-4:] != ".csv" or file_name[:5] != "table":
                continue

            measurement_id = int(search(r'\d+', file_name).group())
            if measurement_id in self.MEASUREMENTS:
                suptitle = f"Measurements for {self.MEASUREMENTS[measurement_id]}"
            else:
                suptitle = f"Measurements {file_name[:-4]}"

            # Setup.
            fig, axs = plt.subplots(2, 2, figsize=(12, 10))
            fig.suptitle(suptitle, fontsize=20)
            color_set = self.COLOR_SET.copy()
            hours = [hour for hour in range(24)]
            start_date = datetime(2023, 7, 6, 0, 0, 0)
            end_date = datetime(2023, 7, 8, 23, 59, 59)

            axs[0, 0].set_title("Average Latency for All Probes\nby Hour of Day (in miliseconds)", fontsize=14)
            axs[0, 0].grid(True)
            axs[0, 0].set_xlabel("Time of day")
            axs[0, 0].set_xticks(hours)
            axs[0, 0].set_xticklabels([f"{hour:02d}h" for hour in hours])
            axs[0, 0].tick_params(axis='x', rotation=45, labelsize=7)
            axs[0, 0].set_ylabel("Average latency")
            axs[0, 0].yaxis.set_major_formatter('{x:.0f}ms')
            axs[0, 0].tick_params(axis='y', labelsize=9)

            axs[0, 1].set_title("Average Hop Count for All Probes\nby Hour of Day", fontsize=14)
            axs[0, 1].grid(True)
            axs[0, 1].set_xlabel("Time of day")
            axs[0, 1].set_xticks(hours)
            axs[0, 1].set_xticklabels([f"{hour:02d}h" for hour in hours])
            axs[0, 1].tick_params(axis='x', rotation=45, labelsize=7)
            axs[0, 1].set_ylabel("Average hops")
            axs[0, 1].yaxis.set_major_locator(ticker.MultipleLocator(base=1))
            axs[0, 1].yaxis.set_minor_locator(ticker.MultipleLocator(base=0.5))
            axs[0, 1].tick_params(axis='y', labelsize=9)

            axs[1, 0].set_title("Probes Average Latency\nover 69 Hours (in miliseconds)", fontsize=14)
            axs[1, 0].grid(True)
            axs[1, 0].set_xlabel("Created at")
            axs[1, 0].xaxis.set_major_locator(mdates.HourLocator(interval=6))
            axs[1, 0].xaxis.set_major_formatter(mdates.DateFormatter("%d %Hh"))
            axs[1, 0].set_xlim(start_date, end_date)
            axs[1, 0].tick_params(axis='x', rotation=45, labelsize=9)
            axs[1, 0].set_ylabel("Average latency")
            axs[1, 0].yaxis.set_major_formatter('{x:.0f}ms')
            axs[1, 0].tick_params(axis='y', labelsize=9)

            axs[1, 1].set_title("Probes Average Hop Count\nover 69 Hours", fontsize=14)
            axs[1, 1].grid(True)
            axs[1, 1].set_xlabel("Created at")
            axs[1, 1].xaxis.set_major_locator(mdates.HourLocator(interval=6))
            axs[1, 1].xaxis.set_major_formatter(mdates.DateFormatter("%d %Hh"))
            axs[1, 1].set_xlim(start_date, end_date)
            axs[1, 1].tick_params(axis='x', rotation=45, labelsize=9)
            axs[1, 1].set_ylabel("Average hops")
            axs[1, 1].tick_params(axis='y', labelsize=9)

            fieldnames = ("Probe_ID", "Origin", "Average_Latency", "Total_Hops", "Created_At")
            with open(f"{self.output_directory}/{file_name}", "a") as input_file:
                input_file.write("\n")
                DictWriter(input_file, delimiter=";", fieldnames=fieldnames).writerow(
                    {
                        "Probe_ID": "xxx",
                        "Origin": "xxx",
                        "Average_Latency": "xxx",
                        "Total_Hops": "xxx",
                        "Created_At": "xxx"
                    }
                )

            # Lê cada arquivo .csv e cria 4 tabelas para cada.
            with open(f"{self.output_directory}/{file_name}", "r") as input_file:
                csv_reader = DictReader(input_file, delimiter=";", fieldnames=fieldnames)
                next(csv_reader)

                x_time = list()
                y_latencies = list()
                y_latencies_24 = list()
                y_hops = list()
                y_hops_24 = list()
                y_latencies_maxes = list()
                y_hops_maxes = list()
                for _ in range(24):
                    y_latencies_24.append([])
                    y_hops_24.append([])

                probe_id = ""
                probe_origin = ""
                for row in csv_reader:

                    if probe_id != row["Probe_ID"] and probe_id != "":
                        y_latencies_maxes.append(max(y_latencies))
                        y_hops_maxes.append(max(y_hops))
                        color = color_set.pop()
                        axs[1, 0].plot(
                            x_time, y_latencies, label=f"{probe_origin}", color=color, linewidth=1.5
                        )
                        axs[1, 1].plot(
                            x_time, y_hops, label=f"{probe_origin}", color=color, linewidth=1.5
                        )
                        y_latencies.clear()
                        y_hops.clear()
                        x_time.clear()
                        if row["Probe_ID"] == "xxx":
                            break

                    time = datetime.strptime(row["Created_At"], "%H:%M %d/%m/%y")
                    x_time.append(time)
                    y_latencies.append(int(row["Average_Latency"]))
                    y_hops.append(int(row["Total_Hops"]))
                    y_latencies_24[time.hour].append(int(row["Average_Latency"]))
                    y_hops_24[time.hour].append(int(row["Total_Hops"]))
                    probe_id = row["Probe_ID"]
                    probe_origin = row["Origin"]

            y_latencies_averages = [sum(sublist) / len(sublist) for sublist in y_latencies_24]
            latency_amp = max(y_latencies_averages) - min(y_latencies_averages)
            axs[0, 0].yaxis.set_major_locator(ticker.MultipleLocator(base=5 if latency_amp >= 5 else 1))
            axs[0, 0].yaxis.set_minor_locator(ticker.MultipleLocator(base=1 if latency_amp >= 5 else 0.5))
            axs[0, 0].plot(hours, y_latencies_averages, label=f"Overall average", linewidth=1.5)

            y_hops_averages = [sum(sublist) / len(sublist) for sublist in y_hops_24]
            hops_amp = max(y_hops_averages) - min(y_hops_averages)
            axs[0, 1].yaxis.set_major_locator(ticker.MultipleLocator(base=0.5 if hops_amp >= 1 else 0.1))
            axs[0, 1].yaxis.set_minor_locator(ticker.MultipleLocator(base=0.25 if hops_amp >= 1 else 0.05))
            axs[0, 1].plot(hours, y_hops_averages, label=f"Overall average", linewidth=1.5)

            latency_amp = max(y_latencies_maxes) - min(y_latencies_maxes)
            axs[1, 0].yaxis.set_major_locator(ticker.MultipleLocator(base=50 if latency_amp >= 150 else 25))
            axs[1, 0].yaxis.set_minor_locator(ticker.MultipleLocator(base=25 if latency_amp >= 150 else 12.5))

            hops_amp = max(y_hops_maxes) - min(y_hops_maxes)
            axs[1, 1].yaxis.set_major_locator(ticker.MultipleLocator(base=5 if hops_amp >= 20 else 3))
            axs[1, 1].yaxis.set_minor_locator(ticker.MultipleLocator(base=2.5 if hops_amp >= 20 else 1))

            plt.legend(loc='upper left', bbox_to_anchor=(1.05, 0.9))

            plt.tight_layout(pad=3.0)
            plt.savefig(f"{self.output_directory}/chart_{measurement_id}.png", bbox_inches='tight', dpi=900)
            print(f"chart_{measurement_id}.png saved at {self.output_directory}")
            plt.clf()

    def get_location(self, ip_address: str, probe_id: int) -> str:
        """
        Retorna informações da localização baseado no IP utilizando a IPAPI. Se a conexão gerar um erro,
        o método buscará a informação de localização em um arquivo “probe_origin.json”.
        """
        if probe_id in self.probe_origin:
            return self.probe_origin[probe_id]
        else:
            response = get(f"https://ipapi.co/{ip_address}/json/").json()

            if response.get("error"):
                if response.get("reason") == "RateLimited":
                    print("Limite de requisições da para IPAPI atingido.")
                try:
                    with open(f"{self.output_directory}/probe_origin.json", "r") as file:
                        probes = load(file)
                    location = probes.get(str(probe_id))
                    if location:
                        self.probe_origin[probe_id] = location
                        return location
                    else:
                        return "N/A"
                except FileNotFoundError:
                    return "N/A"

            city = response.get("city")
            region_code = response.get("region_code")
            self.probe_origin[probe_id] = f"{city}, {region_code}"
            return self.probe_origin[probe_id]
