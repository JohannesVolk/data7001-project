from util import *
import traceback
import datetime
try:
	collect_data(iterations=1000, time_interval=30)
except Exception as e:
    # Get the current date and time
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Write the error message and traceback to a file
    with open('error_log.txt', 'a') as f:
        f.write(f"{now} - An error occurred: {e}\n")
        f.write(traceback.format_exc())
        f.write('\n')
    print("An error occurred. See error_log.txt for details.")

aggregate_csvs()
