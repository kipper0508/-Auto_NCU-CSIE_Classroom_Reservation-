# Auto_NCU-CSIE_Classroom_Reservation

### Require
* Python3
* Python3 Lib : See in require.txt

### Usage
```shell
usage: python3 clock.py [-h] [--config CONFIG] [-c CLASSROOM]

optional arguments:
  -h, --help            show this help message and exit
  --config CONFIG       default: config.json
  -c CLASSROOM, --classroom CLASSROOM       classrooms are defined in config.json (default: default_room)
``` 

### How to Use
* Make sure you have installed the requirement.
    ```shell
    pip3 install -r require.txt
    ```
* Create config.json
    ```shell
    cp config.json.example config.json
    ```
* Set these parameters in config.json
    * portal account&password
    * cellphone number
    * teacher's name
    * date
        * only can reserve 14 days early
        * Target mode-> "sign_online_day" : "using_classroom_day"
        * or use "EVERY" tag
            * Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday
            * Default reserve the week after next
        * If "EVERY" tag and Target mode is in conflict, default using Target mode setting
    * cid table
        * A203 : 6
        * A204 : 7
        * A205 : 8
        * A206 : 9
        * A207 : 11
        * 208 : 12
        * A209 : 13
        * A210 : 14
        * A211 : 15
        * A301 : 17
        * A302 : 18
        * A303 : 25
        * A306 : 26
        * B217 : 27
        * B223 : 23
        * B226 : 21
        * B323 : 24 
        * B326 : 22
    * start&end period table
        * 0 : "08:00-08:50",
        * 1 : "09:00-09:50",
        * 2 : "10:00-10:50",
        * 3 : "11:00-11:50",
        * 4 : "12:00-12:50",
        * 5 : "13:00-13:50",
        * 6 : "14:00-14:50",
        * 7 : "15:00-15:50",
        * 8 : "16:00-16:50",
        * 9 : "17:00-17:50",
        * 10 : "18:00-18:50",
        * 11 : "19:00-19:50",
        * 12 : "20:00-20:50",
        * 13 : "21:00-21:50"

* Set the script executable.
    ```shell
    $ sudo chmod 777 Auto_clock/clock.py
    ```

* Config the crontab.
    * your  "sign_online_day" in config.json have to be the same as the day in crontab



