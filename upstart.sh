#FIX ME 

#Automate the start up process

pip3 install virtualenv
virtualenv run/lib
source run/lib/bin/activate

pip3 install flask requests sqlite3

python3 run/src/login.py