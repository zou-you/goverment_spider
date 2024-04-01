nohup python start_project.py --timed_task > logs/cmd.out 2>&1 & echo $! > logs/pids.txt; \
nohup python -m http.server --directory xls_files/ -b 0.0.0.0 9091 > logs/cmd2.out 2>&1 & echo $! >> logs/pids.txt
