# PEGASUS INTRODUCTION

Pegasus is an automation framework which manages a fleet of virtual machines of various operating systems, executes 
code and cyber attacks on them, conducts detailed analysis on the event logs and displays custom reports.
 
##### Development Modules
- Controller Module
- TestBed Generator Module
- Job Manager
- Windows activity Manager
- Mac activity Manager
- Test Execution Manager
- Reporting Managers
- Analytics Manager

Design of the automation frmework is as follows.

![Alt text](static/project_images/design.jpg?raw=true "Design")


### Feature Highlights

#### Test Suite Execution

- Multiple test suites chained together
- Jenkins triggered build run 
- Realtime test run tracking and monitoring

![Alt text](static/project_images/end_to_end.png?raw=true "End-to-End Test Suite Progress and Tracking")

#### Execute TestSuites on machines


![Alt text](static/project_images/run_functional.jpg?raw=true "Run TestSuite")


#### Reports 

- Detailed reports of test runs

![Alt text](static/project_images/reports.jpg?raw=true "Custom Reports ")



#### Summary Statistics

- Statistics of various kinds of runs summarized in tables with attached report links

![Alt text](static/project_images/dashboard.jpg?raw=true "Summary Stats")


#### TestLink integration

Tests added in testlink are automatically triggged by the automation and the results are emailed to the subsribed parties.

![Alt text](static/project_images/testlink.jpg?raw=true "TestLink Integration")


#### Run Custom Test Suites
 
 - Customized the type of test you want ot run within a virtual machine
 
![Alt text](static/project_images/run_custom_tests.jpg?raw=true "Run Custom Tests")


#### Django Rest API Framework

- Rest API framework is deployed and few API endpoints are exposed. The data coming from the API can be displayed as per the user need.
- React.js/Vue.js single page applications integrate very nicely with Django Rest API framework


![Alt text](static/project_images/rest_api.jpg?raw=true "Rest API Framework")




# Automation Server Deployment
Deployment steps are as follows.

### 1.1 Environment

- Machine: Ubuntu Desktop 16.04 x64 or Ubuntu 14
 
- Hard Disk: 500G

- RAM: 16GB

- Cores: 8 


The script needs to run on a Linux (Ubuntu) machine. It needs the client Windows virtual machines to be present on the local network. Setup the ubuntu machine by installing the required python version, pip, and other tools.

- Python 3.5.2 > install, Python 3.8 preferred

`sudo apt update`

`sudo apt install software-properties-common`

`sudo add-apt-repository ppa:deadsnakes/ppa`

`sudo apt update`

`sudo apt install python3.8`

`python3.8 --version`

- Install pip

`sudo python3.8 -m easy_install pip`

`sudo apt install python3.8-distutils (optional)`

`pip3 install --upgrade pip (optional)`

`export LC_ALL="en_US.UTF-8"  (optional)`

`export LC_CTYPE="en_US.UTF-8"  (optional)`

`sudo dpkg-reconfigure locales (optional)`


- Install virtual env

`sudo pip3 install virtualenv virtualenvwrapper`

- Install NGINX

`sudo apt-get install nginx`

`sudo apt-get install python3.8-dev`

`sudo pip3 install uwsgi`

Add your project configuration file to `/etc/nginx/sites-available/pegasusautomation.conf`
Make sure to change the paths in the conf file according to your directory structure

`sudo ln -s /etc/nginx/sites-available/pegasusautomation.conf /etc/nginx/sites-enabled/`


https://uwsgi-docs.readthedocs.io/en/latest/tutorials/Django_and_nginx.html

# Elasticsearch
Install elasticsearch on Ubuntu and install it's chrome elasticsearch head or firefox elasticvue for UI access.



## 1.2 Server Setup

- Copy the automation code to a local git repository

- Create a virtual environment `env` in the project base dir and activate the virtual environment
 virtualenv env

`source env/bin/activate`

- Install requirements
 
`pip3 install Django==3.1`

`pip install -r requirements.txt`

Note: if you are not able to install via requirements.txt simply install individual modules : pip3 install <module-name>

- The project secret key should be placed in the /etc/secret_key.txt file in the local ubuntu system. The secret key is commented out in the settings.py file. Please make sure to add this secret key in the above mentioned created file and remove it from the settings.py

- In each standalone script, there is a user-configurable python file called ‘settings.py’. It has the changes that a user is required to modify in order to set up his environment. Add your automation server IP, virtual machine info, and network details in settings.py 

- (This one-time step can also be done using Automation UI. Navigate to VM Manager > Add  User)The user needs to add the  account credentials and the virtual machine credentials in an SQLite database. These credentials are encrypted using the Python Cryptography module the Fernet AES algorithm. Run secrets.py script to add account username/password and virtual machine username/passwords. The script is located in the <project_root>/secrets/secrets.py. (If you want to change the credentials either delete the database and create another one or update it manually.)

`python <project_root>/secrets/secrets.py`

- Create a media folder in the base dir and add sub-folder ‘downloads’ to it. Also change the media_url in settings.py

- Use linux ‘truncate’ command to create files of different sizes and save it to <base-dir>/media/downloads

`truncate -s 100M 100MB`

`truncate -s 1G 1GB`

`truncate -s 10G 10GB`

`truncate -s 20G 20GB`

- Install and deploy elasticsearch on another machine and configure the Elasticsearch and IP port in the automation in apps/report_manager/translate.py and apps/report_manager/event_comparison.py

- Test your project by running the following

`sudo python3 manage.py runserver 0.0.0.0:8000`

If development server is successfully running, kill it and deploy the production server
 
- Before running nginx, you have to collect all Django static files in the static folder. 

`sudo python3 manage.py collectstatic`

- Start the production server in the main project directory in a screen or place it in a cronjob

`uwsgi --socket pegasusautomation.sock --module pegasusautomation.wsgi --chmod-socket=666 --master --processes 4 --threads 2` 

- Give appropriate file permissions in another terminal
	
	`sudo chmod -R 664 .`

## 1.3 Running the Production Server

- Access the automation UI from a browser

`https://<serverip>:8000/login`

- One time automation configuration :  Add  User and virtual Machines

## Jenkins Setup

To integrate automatic build testing triggers on JEnkins, 

- Install and setup Jenkins
- Install SSH plugin and add remote servers

Create a new Build

- A user pushes the Collector agent to Git repository microagent-windows, 'release/Agent Version'
- On the Jenkins server, a new Freestyle project is created
- The project is parameterized
- A batch script is added which specifies the certificates and buildall.bat to run as a pre-build action
- SSH server needs to be selected from a drop-down menu
- Post Request to Automation Server via CURL
- Archive the executable and log files
- Notify the stakeholders via email

MAke sure that the build name you add is identical to the one specified in 'decw_version' in the cURL POST request to Django serevr. The automation would later on search for this build in the specified location and use it for installation/uninstallation. 



# 2. ESXi setup

ESXi setup is required for the automation to run. Later on, support for Xen server will also be added. The machines need to be prepared for automation to run.

# 2.1 Pre-requisites on a Windows Virtual machine
The Windows machine needs to have 
- OpenSSH installed and running
- Full Administrator privileges 
- Enable powershell remotesigned policy
- VMware Tools should be installed and running

# 2.1.1 OpenSSH on Windows

Install OpenSSH and run the ssh service

https://winscp.net/eng/docs/guide_windows_openssh_server

# 2.2 Prerequisites for WinSAT testing
- Excel and other Office applications need to be installed for file monitoring
- Make sure the C:\automation-data\winsat\bin\monitor.bat is running in the background.


# WinSAT Testing
All the variables, paths, and metadata regarding the WinSAT module are present in apps/testbeds/apps.py in class PerformanceTestBedsConfig. 

The types of tests are configured by tweaking the dictionary comprehensive_test. You can enable or disable runs.


Please note that depending upon the virtual machine type, processing speed, and background activity the WinSAT instance might take more time than usual. Please monitor your runs and tweak wait_time and retry count variables in the PerformanceTestBedsConfig. The automation tries the runs again if time out occurs and this might cause additional overheads.

Note: Enable random and sequential reads by uncommenting the relevant lines in class PerformanceTestBedsConfig, dictionary comprehensive_test

 




# Project setup

- When this repo is cloned make sure to create a new local_settings.py file in pegasusautomation folder and paste your local 
paths there.

- Install redis server on your machine using `sudo apt-get install redis-server` or by building the redis source file. You can test that Redis is working properly by typing this into your terminal:
`
$ redis-cli ping
`
. Redis should reply with PONG.
 https://redis.io/download
 
 - Setup MySQL remote database server
    `sudo apt-get install mysql-server python3-dev default-libmysqlclient-dev build-essential mysqlclient`
    
 - Run celery `celery -A pegasusautomation worker -l info`
    
    
    
# User changes


- Every app has an AppConfig class in app.py which contain the hardcoded paths/metadata. 
    The user can change the paths there during deployment. The testcase scripts are copied to the remote machine at 
    `C:\automation-data`.
    
    
    
# Virtual machine setup

- Install SSH https://github.com/PowerShell/Win32-OpenSSH/wiki/Install-Win32-OpenSSH
- Enable powershell remotesigned policy
- Make sure to create a task in task scheduler named as "automation". automation triggers this task that runs c:\automation-data\run.bat file and runs UI programs. this is a crucial step.


# Performance Testing

- Automation uses Winsat and perfmon tools for performance testing.
- To increase the performance counters, get the full list of counters here. 
`powershell Get-Counter -ListSet *`
or Alphabetical list `Get-Counter -ListSet * | Sort-Object -Property CounterSetName | Format-Table -AutoSize`


# Limitations and known Issues

- Paramiko SSH access from a Linux server to a Windows machine is unstable. For now the automation retries and reconnects 
 to the machines which is performance intensive.
- For now, under the free ESXi license, we cannot create snapshots. Therefore the snapshot needs to be created manually 
and specified by the user 


# Sanity runs
Make sure that you have <>/results/sanity expected csv already present or copied
Make sure you allow 8000 and 8002 prts in server firewall
sudo iptables -A INPUT -p tcp --dport 8002 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 8000 -j ACCEPT

sudo systemctl start elasticsearch

# DB lock
sudo fuser -k db.sqlite3