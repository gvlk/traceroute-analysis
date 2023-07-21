# Traceroute Analysis Tool with RIPE Atlas Measurements
This Python tool is designed for analyzing traceroute data from RIPE Atlas measurements and generating various statistics, CSV tables, and charts based on the collected information. It is particularly useful for studying network latency and hop count measurements over time for different probes.

## Installation
To use this tool, first clone this repository to your local machine:
```bash
git clone https://github.com/gvlk/traceroute-analysis.git
```
This tool has some external dependencies. Before running it, make sure to install the required packages using ``pip``:
```bash
pip install -r requirements.txt
```

## Usage
You can run the Traceroute Analysis Tool via the terminal with the following command-line arguments:
```bash
python main.py [-w] [-c] [-g] measurements_path
```
### Arguments
``measurements_path``: Path to the directory containing the raw traceroute measurements exported from RIPE Atlas in JSON format.  

The Traceroute Analysis Tool provides the following functionalities:

#### Write Traceroute Data
``-w``, ``--write_traceroute_data``: This command will read the raw traceroute data files in the specified directory and store the parsed data in the internal format for further analysis.

#### Generate CSV Tables
``-c``, ``--generate_csv_tables``: By running this command, the tool will process the traceroute data and generate CSV tables summarizing the average latency, total hops, and creation timestamps for each probe.

#### Generate Charts
``-g``, ``--generate_charts``: This option will create charts based on the traceroute data. The charts display average latency and average hop count for each hour of the day and over the entire period.

#### Running All Three Methods
If you run the tool without specifying any of the above options, it will execute all three methods in the previous order.

### Input Data Format
The input data for the Traceroute Analysis Tool should be raw traceroute measurements exported from RIPE Atlas. These measurements come in JSON format. The ``write_traceroute_data()`` method processes these JSON files and creates new JSON files that are used by the ``generate_csv_tables()`` method to generate CSV tables.

## Acknowledgments
This project was inspired by the need to analyze traceroute data and gain insights into network performance and latency.

## Contributions
Contributions to this project are welcome! If you encounter any issues or have suggestions for improvements, feel free to open an issue or create a pull request with your proposed changes.

## Credits
This project is maintained by Guilherme Azambuja.