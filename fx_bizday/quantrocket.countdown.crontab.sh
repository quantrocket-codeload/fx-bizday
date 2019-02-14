# Crontab commands for fx-bizday
# Intended to be run in timezone America/New_York

# Crontab syntax cheat sheet
# .------------ minute (0 - 59)
# |   .---------- hour (0 - 23)
# |   |   .-------- day of month (1 - 31)
# |   |   |   .------ month (1 - 12) OR jan,feb,mar,apr ...
# |   |   |   |   .---- day of week (0 - 6) (Sunday=0 or 7)  OR sun,mon,tue,wed,thu,fri,sat
# |   |   |   |   |
# *   *   *   *   *   command to be executed

# make sure IB Gateway is running each weekday
0 2 * * mon-fri quantrocket launchpad start

# Update historical database, wait for it to finish, then trade fx-bizday each weekday at 3 AM, 11 AM, and 4 PM. This command "paper trades" 
# fx-bizday by logging orders to flightlog; to live or paper trade with IB, send orders to blotter instead:
#     ... quantrocket moonshot trade 'fx-bizday' | quantrocket blotter order -f -
0 3,11,16 * * mon-fri quantrocket history collect 'fiber-1h' && quantrocket history wait 'fiber-1h' && quantrocket moonshot trade 'fx-bizday' | quantrocket flightlog log -n 'quantrocket.moonshot'

# stop IB Gateway at end of day
0 18 * * mon-fri quantrocket launchpad stop