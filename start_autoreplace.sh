#!/bin/bash

folder_name="$1"

source ~/CHESNO/chesnovenv/bin/activate
find "$folder_name" -type f -name 2_realty.csv -exec python3 replace_names.py "{}" \;
find "$folder_name" -type f -name 3_vehicles.csv -exec python3 replace_names.py "{}" \;
find "$folder_name" -type f -name 5_donations.csv -exec python3 replace_names.py "{}" \;
find "$folder_name" -type f -name 6_expenses.csv -exec python3 replace_names.py "{}" \;
find "$folder_name" -type f -name 7_liabilities.csv -exec python3 replace_names.py "{}" \;
deactivate
