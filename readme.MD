# Requirements

 - Virtualenv
 - Flask
 - Flask MySQLDB (lib)
 - Numpy
 - Pandas

## Config
In the folder

> src\config.py

Replace the MySQL Credentials for user 

## Installation
In the repository root folder, first initialize the virtual environment

    virtualenv -p python3 env
Then, with powershell, type in the terminal:

    . \env\Scripts\activate
Following the installations:

    pip install flask flask_mysqldb numpy pandas
Then, run the file 

> src\app.py