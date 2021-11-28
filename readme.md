# About
This project is for deploying wiki js app using docker containers, ansible and vagrant.

# Requirements
- os: 
  - local: ubuntu 21
  - remote: ubuntu 20
- os packages:
  - on host pc:
    - git 2.30.2 
    - make 4.3
    - vagrant 2.2.19
    - virtualbox 6.1
  - ansible will install on virtual host:
    - docker 20.10.11
    - docker-compose 1.26.2
    - python 2.7.18

# demo start
- install packages from "Requirements -> os packages -> on host pc"
- clone git project
```shell
git clone https://github.com/Saamoot/photoneo-test.git
```
- change working dir
```shell
cd photoneo-test
```
- start virtual host, during startup you will be prompted to select network adapter which will be used as bridge
  for virtual host machine
```shell
make vagratStartHost
```
- finish first time wiki js setup
  - get virtual host ip with command `make vagrantHostIp`
  - open browser and visit page `http://{virtual-host-ip}`
  - set admin user name and password
  - set site url `http://{virtual-host-ip}`
  - submit
- (optional) login to wiki js and enable graphql api
  - login using credentials from previous step
  - got to page `http://{virtual-host-ip}/a/api`
  - press "enable api" button
  - create api key by pressing "new api key" and save value to file `.../photoneo-test/workdir/wiki-js-token`
- create home page:
  - manual by visiting `http://{virtual-host-ip}/e/en/home`
  - via python script (this need previous optional step enable graphql wiki)
```shell
make pythonRunCreatePage
```
- dump application data into zip file
  - data only
```shell
make pythonRunDatabaseScriptDump
```
  - full pg_dump
```shell
make pythonRunDatabasePgDump
```