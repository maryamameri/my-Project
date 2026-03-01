import os
import pandas as pd
import re
from datetime import datetime

# Global variables
rootFolder = "./data/processed"
timesheets_folder = "./data/processed"
skipFolder = ["variable"]
skipFile = [
    "1234",
    "1234"
]
verbose = False  # True for additional status logs

importPatients = [1, 2, 3]

data_approval = pd.DataFrame()
data_rejection = pd.DataFrame()
data_avg_approval = pd.DataFrame()
data_std_approval = pd.DataFrame()
data_avg_rejection = pd.DataFrame()
data_std_rejection = pd.DataFrame()


def time_delta_ms(time_start: str, time_end: str):
    """
    Calculate the difference in milliseconds between two timestamps.

    Args:
        time_start (str): The start time in the format "YYYY-MM-DD HH:MM:SS.ssssss".
        time_end (str): The end time in the format "YYYY-MM-DD HH:MM:SS.ssssss".

    Returns:
        The difference in milliseconds between the two timestamps.
    """
    start_dt = datetime.strptime(time_start.strip("\n"), "%Y-%m-%d %H:%M:%S.%f")
    end_dt = datetime.strptime(time_end.strip("\n"), "%Y-%m-%d %H:%M:%S.%f")

    time_difference = end_dt - start_dt
    milliseconds = time_difference.total_seconds() * 1000
    return milliseconds


def process_aufgabe(data_list, patient_number, test_number, step_number, substep_number, pattern_type, time_zero, time_start, time_end):
    """
    Processes CSV files in a directory tree and filters rows based on conditions.

    Parameters:
        data_list (list): List of root folders to process.
        test_number (int): The test number to look for in "Aufgabe_X".
        step_number (int): Not used directly in this function but can be passed.
        substep_number (int): Not used directly in this function but can be passed.
        pattern_type (str): Pattern type ("approval" or "rejection").
        time_start (str): Start of the timestamp range (inclusive).
        time_end (str): End of the timestamp range (inclusive).
    """

    # Only process step 1_1
    if step_number != '1' or substep_number != '1':
        if verbose:
            print(f"Skipped Aufgabe {test_number}.{step_number}.{substep_number} {pattern_type}")
        return

    # Iterate over each folder in the root folder
    for folder in os.scandir(rootFolder):
        # convert folder name to number and compare with patient number
        try:
            folder_patient_number = int(folder.name)
        except:
            continue

        if folder.is_dir() and folder_patient_number == patient_number:
            folder_path = os.path.join(rootFolder, folder.name)

            try:
                # Import Data
                test_number = test_number.lstrip('0')  # remove leading zero '01' -> '1'
                pattern = re.compile(rf"Training_\d+_Aufgabe_{test_number}_")
                if verbose:
                    print(f"Import Patient {patient_number}, Aufgabe {test_number}.{step_number}.{substep_number} {pattern_type}")

                for root, dirs, files in os.walk(folder_path):
                    # Skip folders
                    dirs[:] = [d for d in dirs if not any(skip in d for skip in skipFolder)]

                    for file in files:
                        # Skip files
                        if any(skip in file for skip in skipFile):
                            continue

                        # Process only CSV files for correct Aufgabe
                        if file.endswith('.csv') and pattern.search(file):
                            file_path = os.path.join(root, file)
                            try:
                                # Read the CSV file
                                if verbose:
                                    print("Import file: " + file_path)
                                df = pd.read_csv(file_path)

                                # Ensure the 'timestamp' column exists
                                col_timestamp = 'timestamp'
                                if col_timestamp not in df.columns:
                                    col_timestamp = ' timestamp'
                                if col_timestamp not in df.columns:
                                    print(f"'timestamp' column missing in {file_path}")
                                    continue

                                # Calculate timeframe in ms
                                time_start_s = time_delta_ms(time_zero, time_start) / 1000.0
                                time_end_s = time_delta_ms(time_zero, time_end) / 1000.0
                                filtered_rows = df[(df[col_timestamp] >= time_start_s) & (df[col_timestamp] <= time_end_s)]

                                # Append to the appropriate global DataFrame
                                global data_approval
                                global data_rejection
                                if pattern_type == "approval":
                                    data_approval = pd.concat([data_approval, filtered_rows], ignore_index=True)
                                elif pattern_type == "rejection":
                                    data_rejection = pd.concat([data_rejection, filtered_rows], ignore_index=True)

                            except Exception as e:
                                print(f"\n!!! Error processing file {file_path}: {e}\n")

            except ValueError:
                # Raise an error if parsing fails
                raise ValueError(f"Folder name '{folder.name}' is not a valid patient number!")


# return timesheet csv filename with highest identifier number
def get_newest_timesheet(filenames):
    if len(filenames) < 1:
        print(f"Error! Filenames contains no elements")
        return ''

    if len(filenames) == 1:
        return filenames[0]

    highest_num = -1
    highest_file = None

    for filename in filenames:
        match = re.search(r'_app_(\d+)', filename)
        if match:
            num = int(match.group(1))
            if num > highest_num:
                highest_num = num
                highest_file = filename

    return highest_file


# Scan timesheet csv files and import corresponding data
def import_data():
    """
    Imports and processes patient data from CSV files located in specified folders.
    The function scans through patient folders, reads CSV files, and processes data based on specific patterns.
    It calculates mean and standard deviation for approval and rejection data for each patient and appends the results
    to global data frames.
    Patterns:
        - pattern_time_rejection: Matches labels indicating the start of a rejection test.
        - pattern_time_approval: Matches labels indicating the start of an approval test.
        - pattern_rejection: Matches labels indicating rejection steps.
        - pattern_approval: Matches labels indicating approval steps.
    Global Variables:
        - data_approval: DataFrame to store approval data.
        - data_rejection: DataFrame to store rejection data.
        - data_avg_approval: DataFrame to store average approval data.
        - data_std_approval: DataFrame to store standard deviation of approval data.
        - data_avg_rejection: DataFrame to store average rejection data.
        - data_std_rejection: DataFrame to store standard deviation of rejection data.
    Parameters:
        None
    Returns:
        None
    Raises:
        ValueError: If both zero_timestamp_approval and zero_timestamp_rejection are None.
        ValueError: If an invalid pattern type is encountered.
    Notes:
        - The function assumes that the CSV files contain a 'label' column and a 'timestamp' column.
        - The function processes data for patients listed in the importPatients list.
        - Verbose output can be enabled by setting the verbose variable to True.
    """
    pattern_time_rejection = r"^coping_ng_(\d+)$"
    pattern_time_approval = r"^training_pg_(\d+)$"
    pattern_rejection = r"^coping_ng_(\d+)_step(\d+)_(\d+)$"
    pattern_approval = r"^training_pg_(\d+)_step(\d+)_(\d+)$"

    for patient_folder in os.scandir(timesheets_folder):
        # Get patient number from folder name
        try:
            patient_number = int(patient_folder.name)
        except (ValueError, IndexError) as e:
            # Raise an error if parsing is not successful
            print(f"Error! Failed to parse patient number {patient_folder.name}")
            continue

        if not patient_number in importPatients:
            if verbose:
                print(f"Skip patient {patient_number}")
            continue

        for root, _, files in os.walk(patient_folder):
            # find all timesheet files in folder
            timesheet_csv = []
            for file in files:
                if file.endswith('.csv'):
                    if any(skip in file for skip in skipFile):
                        continue
                    timesheet_csv.append(file)

            # check if timesheets exist and pick newest one
            if len(timesheet_csv) > 0:
                file = get_newest_timesheet(timesheet_csv)
                file_path = os.path.join(root, file)
                print(f"Patient {patient_number} - Processing file: {file_path}")

                # Read the CSV file
                df = pd.read_csv(file_path)

                # Ensure "label" column exists
                if 'label' not in df.columns:
                    print(f"Skipping file {file} as 'label' column is missing.")
                    continue

                current_data = []
                current_test, first_timestamp, current_step, current_substep, current_pattern_type, current_time = None, None, None, None, None, None
                match_found = False
                zero_timestamp_rejection, zero_timestamp_approval = None, None

                for _, row in df.iterrows():
                    label = row.get("label", "")
                    time = row.get("timestamp", "")

                    if not isinstance(label, str) or not label.strip():
                        try:
                            # Check if zero_timestamp was found
                            if zero_timestamp_rejection is None and zero_timestamp_approval is None:
                                raise ValueError("Both zero_timestamp_approval and zero_timestamp_rejection are None!")

                            # Set zero_timestamp based on the current_pattern_type
                            if current_pattern_type == 'rejection':
                                zero_timestamp = zero_timestamp_rejection
                            elif current_pattern_type == 'approval':
                                zero_timestamp = zero_timestamp_approval
                            else:
                                raise ValueError(f"Invalid pattern type: {current_pattern_type}")

                        except ValueError as e:
                            # Handle the error case
                            print(f"Error: {e}")

                        # If current_data contains data, process it
                        if current_data:
                            process_aufgabe(
                                pd.DataFrame(current_data),
                                patient_number,
                                current_test,
                                current_step,
                                current_substep,
                                current_pattern_type,
                                zero_timestamp,
                                first_timestamp,
                                current_time
                            )
                            current_data = []
                            current_test, first_timestamp, current_step, current_substep, current_pattern_type, current_time = None, None, None, None, None, None
                            match_found = False
                        continue

                    # Match against pattern
                    match_time_rejection = re.match(pattern_time_rejection, label)
                    match_time_approval = re.match(pattern_time_approval, label)
                    match_rejection = re.match(pattern_rejection, label)
                    match_approval = re.match(pattern_approval, label)

                    # get timestamp of start of test
                    if match_time_rejection:
                        zero_timestamp_rejection = time
                        zero_timestamp_approval = None
                    elif match_time_approval:
                        zero_timestamp_approval = time
                        zero_timestamp_rejection = None

                    if match_rejection:
                        current_pattern_type = 'rejection'
                    elif match_approval:
                        current_pattern_type = 'approval'

                    # get data of Aufgabe from csv
                    if match_rejection or match_approval:
                        try:
                            # Check if zero_timestamp was found
                            if zero_timestamp_rejection is None and zero_timestamp_approval is None:
                                raise ValueError("Both zero_timestamp_approval and zero_timestamp_rejection are None!")

                            # Set zero_timestamp based on the current_pattern_type
                            if current_pattern_type == 'rejection':
                                zero_timestamp = zero_timestamp_rejection
                            elif current_pattern_type == 'approval':
                                zero_timestamp = zero_timestamp_approval
                            else:
                                raise ValueError(f"Invalid pattern type: {current_pattern_type}")

                        except ValueError as e:
                            # Handle the error case
                            print(f"Error: {e}")

                            # Check if zero_timestamp was found
                            if zero_timestamp_rejection is None and zero_timestamp_approval is None:
                                raise ValueError("Both zero_timestamp_approval and zero_timestamp_rejection are None!")

                            # Set zero_timestamp based on the current_pattern_type
                            if current_pattern_type == 'rejection':
                                zero_timestamp = zero_timestamp_rejection
                            elif current_pattern_type == 'approval':
                                zero_timestamp = zero_timestamp_approval
                            else:
                                raise ValueError(f"Invalid pattern type: {current_pattern_type}")

                        except ValueError as e:
                            # Handle the error case
                            print(f"Error: {e}")

                        # If current_data contains data, process it
                        if current_data:
                            process_aufgabe(
                                pd.DataFrame(current_data),
                                patient_number,
                                current_test,
                                current_step,
                                current_substep,
                                current_pattern_type,
                                zero_timestamp,
                                first_timestamp,
                                current_time
                            )
                            current_data = []
                            current_test, first_timestamp, current_step, current_substep, current_pattern_type, current_time = None, None, None, None, None, None
                            match_found = False

                    if match_rejection:
                        current_test, current_step, current_substep = match_rejection.groups()
                        first_timestamp = time
                        current_time = time
                        current_pattern_type = "rejection"
                        match_found = True
                    else:
                        # Match against approval pattern
                        if match_approval:
                            current_test, current_step, current_substep = match_approval.groups()
                            first_timestamp = time
                            current_time = time
                            current_pattern_type = "approval"
                            match_found = True
                        else:
                            # If no match and no prior match, continue to the next row
                            if not match_found:
                                continue
                            # Otherwise, add row to current_data
                            current_data.append(row)
                            current_time = time
                            continue

                    # Add current row to current_data
                    current_data.append(row)

                # Process any remaining data after the loop ends
                if current_data:
                    process_aufgabe(
                        pd.DataFrame(current_data),
                        patient_number,
                        current_test,
                        current_step,
                        current_substep,
                        current_pattern_type,
                        zero_timestamp,
                        first_timestamp,
                        current_time
                    )

                # after import all data of one patient, calculate mean and std of all patient data
                global data_approval
                global data_rejection
                global data_avg_approval
                global data_std_approval
                global data_avg_rejection
                global data_std_rejection

                # approval
                data_approval = data_approval.apply(pd.to_numeric, errors='coerce')
                mean_values = data_approval.aggregate('mean', skipna=True)  # Calculate the mean of all numeric columns using aggregate
                mean_df = mean_values.to_frame().T  # Convert the series of means into a DataFrame
                mean_df.insert(0, 'patient', patient_number)  # Append a 'patient' column at the beginning with the patient number
                data_avg_approval = pd.concat([data_avg_approval, mean_df], ignore_index=True)  # Append the mean data to

                std_values = data_approval.aggregate('std', skipna=True)  # Calculate the std of all numeric columns using aggregate
                std_df = std_values.to_frame().T  # Convert the series of std into a DataFrame
                std_df.insert(0, 'patient', patient_number)  # Append a 'patient' column at the beginning with the patient number
                data_std_approval = pd.concat([data_std_approval, std_df], ignore_index=True)  # Append the std data

                # rejection
                data_rejection = data_rejection.apply(pd.to_numeric, errors='coerce')
                mean_values = data_rejection.aggregate('mean', skipna=True)  # Calculate the mean of all numeric columns using aggregate
                mean_df = mean_values.to_frame().T  # Convert the series of means into a DataFrame
                mean_df.insert(0, 'patient', patient_number)  # Append a 'patient' column at the beginning with the patient number
                data_avg_rejection = pd.concat([data_avg_rejection, mean_df], ignore_index=True)  # Append the mean data

                std_values = data_rejection.aggregate('std', skipna=True)  # Calculate the std of all numeric columns using aggregate
                std_df = std_values.to_frame().T  # Convert the series of std into a DataFrame
                std_df.insert(0, 'patient', patient_number)  # Append a 'patient' column at the beginning with the patient number
                data_std_rejection = pd.concat([data_std_rejection, std_df], ignore_index=True)  # Append the std data

                # clear data Frames for next patient
                data_approval = pd.DataFrame()
                data_rejection = pd.DataFrame()

                if verbose:
                    print(f"\n\n\nPatient {patient_number} import successful!")
                    print("\n____________\nData Approval\n____________")
                    print("\ndata_avg_approval")
                    print(data_avg_approval)
                    print("\ndata_std_approval")
                    print(data_std_approval)
                    print("\n____________\nData Rejection\n____________")
                    print("\ndata_avg_rejection")
                    print(data_avg_rejection)
                    print("\ndata_std_rejection")
                    print(data_std_rejection)

            else:
                continue


# Export DataFrames to csv
def store_DataFrames(outputFolder):
    # Create output folder
    os.makedirs(outputFolder, exist_ok=True)

    # Export DataFrames
    data_avg_approval.to_csv(os.path.join(outputFolder, 'data_approval_avg.csv'), index=False)
    data_std_approval.to_csv(os.path.join(outputFolder, 'data_approval_std.csv'), index=False)
    data_avg_rejection.to_csv(os.path.join(outputFolder, 'data_rejection_avg.csv'), index=False)
    data_std_rejection.to_csv(os.path.join(outputFolder, 'data_rejection_std.csv'), index=False)

    print(f"DataFrames stored to {outputFolder}")


# Main
import_data()
store_DataFrames('Import_Data')
print("\nFinish ʕ•ᴥ•ʔ\n")
