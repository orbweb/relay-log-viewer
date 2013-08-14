relay-log-viewer
================

manage.py Commands
------------------
```bash
# Sum Dataflow*.txt log columns
$ ./manage.py parse_dataflow

# Parse hourly logs and link them with their corresponding Relay*.txt entries
$ ./manage.py parse_logs
$ ./manage.py parse_hourly
```

Configuration
------------
Config files for saving state of the last Relay*.txt and hourly logs are located
in `log_parser/logs/`, in the files `config.json` and `hourly_config.json`.
These store the last log file parsed, so they are not looked at twice.  You can
specify the locations of the log files in `log_parser/settings.py` under the
`LOGS_PATH` variable.
