import os
import csv

colnames = [
        "start_time",
        "start_name",
        "start_id",
        "end_time",
        "end_name",
        "end_id",
        "time",
        "account_type",
        "start_lat",
        "start_lon",
        "start_docks",
        "end_lat",
        "end_lon",
        "end_docks"
]
extra_colnames = [
    "bikeid",
    "birth year",
    "gender",
    "bike type"
]

station_switch = {
    'x-30158': '30158',
    '30084-A': '30084'
}
station_switch_list = list(station_switch.keys())

nonseason_field_order_one = [1,3,4,2,7,8,0,12,5,6,16,9,10,17,11,13,14,15]
nonseason_field_order_two = [2,5,4,3,7,6,13,12,8,9,14,10,11,15,16,17,18,1]

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
    nonseason_years = [path[0:4] for path in raw_dirs if path[0] != "N"]
    unique_years = []
    for year in nonseason_years:
        if year not in unique_years:
            unique_years.append(year)
    for year in unique_years:
        process_nonseason_year(year, out_path)
    

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
            stations[row[0]] = row[2:5]
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
                row += ['','','']
            if row[5] in station_list:
                row += stations[row[5]]
                if convert_cols:
                    t = row[6]
                    row[6] = row[7]
                    row[7] = t
                if convert_ms:
                    row[6] = float(row[6])/1000
                else:
                    row[6] = float(row[6])
            else:
                row += ['','','']
            output.append(row[:14])
    
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

    output = []
    tripdata_file_path = dir_path+"".join([f for f in files if "tripdata" in f])
    with open(tripdata_file_path) as f:
        reader = csv.reader(f)
        field_order = None
        for row in reader:
            row += ["","","","","",""]
            if field_order is None:
                if row[0] == "tripduration":
                    field_order = nonseason_field_order_one
                elif row[0] == "ride_id":
                    field_order = nonseason_field_order_two
            row = [row[ix] for ix in field_order]
            if 'trip' not in row[6] and 'ride' not in row[6] and row[6] != '':
                row[6] = float(row[6])
            output.append(row[:18])
        output[0] = colnames + extra_colnames
    
    year_month = tripdata_file_path[4:10]

    with open(out_path+year_month+"_temporary.csv", 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(output)

def process_nonseason_year(year: str, out_path: str) -> None:
    """ Combine monthly files into annual file.

    Args:
        year: year of annual file.
        out_path: location of temp files and new annual file.

    """

    files = os.listdir(out_path)
    annual_files = [f for f in files if f[:4] == year]
    output = [[]]
    for monthly_path in annual_files:
        skipped = False
        with open(out_path+monthly_path) as f:
            reader = csv.reader(f)
            for row in reader:
                if not skipped:
                    skipped = True
                else:
                    output.append(row)
        os.remove(out_path+monthly_path)
    output[0] = colnames+extra_colnames

    with open(out_path+year+"_processed.csv", 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(output)


if __name__ == "__main__":
    process_raw_files()