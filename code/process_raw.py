import os
import csv

colnames = [
        "start_time",
        "start_id",
        "start_name",
        "end_time",
        "end_id",
        "end_name",
        "time",
        "account_type",
        "start_lat",
        "start_lon",
        "start_docks",
        "end_lat",
        "end_lon",
        "end_docks"
    ]
station_switch = {
    'x-30158': '30158',
    '30084-A': '30084'
}
station_switch_list = list(station_switch.keys())

def process_raw_files(raw_path: str = "raw/", out_path: str = "data/") -> None:
    """ Given folders duplicated to path, generate csvs at out_path

    Args:
        raw_path: path of raw folder
        out_path: path of ourput folder

    """
    raw_dirs = os.listdir(raw_path)
    for subdir in raw_dirs:
        if 'season' in subdir:
            process_season_dir(raw_path+subdir+"/"+subdir+"/", out_path)
        else:
            process_nonseason_dir(raw_path+subdir+"/", out_path)

def process_season_dir(dir_path: str, out_path: str) -> None:
    """ Get data as list from directory in season format.

    Args:
        dir_path: path of subdirectory to process
        out_path: path to put output csv
    
    """

    files = os.listdir(dir_path)

    stations = {}
    station_file_path = dir_path+"".join([f for f in files if "ocation" in f])
    with open(station_file_path) as f:
        reader = csv.reader(f)
        for row in reader:
            stations[row[0]] = row[2:]
    station_list = list(stations.keys())
    
    output = []
    history_file_path = dir_path+"".join([f for f in files if "history" in f])
    convert_ms = False
    convert_cols = False
    with open(history_file_path) as f:
        reader = csv.reader(f)
        for row in reader:
            if row[2] in station_switch_list:
                row[2] = station_switch[row[2]]
            if row[5] in station_switch_list:
                row[5] = station_switch[row[5]]
            if row[2] in station_list:
                row += stations[row[2]]
            else:
                if row[-2] == 'Account type':
                    convert_cols = True
                if "ms" in row[-2]:
                    convert_ms = True
                row += [''*3]
            if row[5] in station_list:
                row += stations[row[5]]
                if convert_cols:
                    t = row[-8]
                    row[-8] = row[-7]
                    row[-7] = t
                if convert_ms:
                    try:
                        row[-8] = float(row[-8])/1000
                    except:
                        print(row)
                else:
                    row[-8] = float(row[-8])
            else:
                row += [''*3]
            output.append(row)
    
    year = station_file_path[19:23]
    output[0] = colnames

    with open(out_path+year+"_processed.csv", 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(output)

def process_nonseason_dir(dir_path: str, out_path: str) -> None:
    """ Get data as list from directory in nonseason format.

    Args:
        dir_path: path of subdirectory to process
        out_path: path to put output csv
    
    """

    files = os.listdir(dir_path)

if __name__ == "__main__":
    process_raw_files()