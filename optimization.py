#script is called every 10 min
import mysql.connector
from datetime import datetime, timedelta
#import numpy as np
import time;
# importing the requests library 
import requests , json
#mysql = MySQL()

DB = "cooling"
HOST="10.129.149.7"
USER ="writer"
PASSWORD="datapool"

DELAY=1 #time to wait in minutes

#app.config['MYSQL_DATABASE_USER'] = USER
#app.config['MYSQL_DATABASE_PASSWORD'] = PASSWORD
#app.config['MYSQL_DATABASE_DB'] = DB
#app.config['MYSQL_DATABASE_HOST'] = HOST



#db columns: seatNumber | PMVRating | timestamp | roomName | temperature

zones=["F1A","F2A"]
SeatNumberZones={"F2A":[1,2,3,4,5,6,7,8],"F1A":[6,7,8,9,10,11,12,13,14]}
NumOfPplFeelingUnComfort=0 #In each zone
totalNumOfppl=16
thershold=int(0.10*totalNumOfppl) #thershold on Number of ppl feeling uncomfortable to change temperature 



  
# api-endpoint 
FETCH_URL = "http://seil.cse.iitb.ac.in:1337/equipment"
ACTUATE_URL_ROOT = "http://seil.cse.iitb.ac.in:1337/equipment/actuate/"
# defining a params dict for the parameters to be sent to the API 
PARAMS = {'location':7}  # this will change depending upon which location we are callibrating
HEADERS = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjp7InVzZXJuYW1lIjoic2VpbEBjc2UuaWl0Yi5hYy5pbiJ9LCJpYXQiOjE1NTUxNjEwNTAsImV4cCI6MTU4NjY5NzA1MH0.D_EnHNCKxwefyW9F3oKO4eDP3WKdJnX6nPF-V9dGp5w"}


def change_temp(AC_serial, temp_diff):
    print("here")
    PARAMS['serial']=AC_serial  # set the serial of the AC in param
    r = requests.get(url = FETCH_URL, params = PARAMS, headers= HEADERS) 
    data = r.json()
    print(data[0]["properties"]["state"])
    print("****************************************************")
    id = data[0]["id"]
    data[0]["properties"]["state"]["temperature"] += temp_diff
    print(data[0]["properties"]["state"]["temperature"])
    if(data[0]["properties"]["state"]["temperature"]<16 or data[0]["properties"]["state"]["temperature"]>31):
        print("here")
        return False
    print ("Setting temperature of %d to %d"%(id, data[0]["properties"]["state"]["temperature"] ))
    data = {'msg':"T"+str(data[0]["properties"]["state"]["temperature"]), 'state':data[0]["properties"]["state"]}
    print(data) 
    #r = requests.post(url = ACTUATE_URL_ROOT+str(id), headers= HEADERS, json=data) 
    r= requests.post(url = ACTUATE_URL_ROOT+str(id), data=json.dumps(data),  headers=HEADERS, verify=False)

#change_temp("F1A",-5)



def check_Num_Of_Ppl_Uncomfortable_from_given_ts(zoneNum,timestamp):
    con = mysql.connector.connect(host=HOST,user=USER,passwd=PASSWORD,database=DB)
    cur = con.cursor()
    query = "select seatNumber,PMVRating from userFeedback where timestamp > '%s'" %(timestamp)
    #print(query)
    cur.execute(query)
    res = cur.fetchall()
    con.close()
    count=0
    rating=[]
    for row in res:
        if row[0] in SeatNumberZones[zoneNum]:
            count=count+1
            rating.append(row[1])
    print(count,rating)
    
    return count,rating

def mainFunction():
    for zone in zones:
        print("zone is "+zone)
        currts = (datetime.now() - timedelta(minutes=DELAY)).strftime("%Y-%m-%d %H:%M:%S")
        NumOfPplFeelingUnComfort,number_Of_pos_neg_Rating=check_Num_Of_Ppl_Uncomfortable_from_given_ts(zone,currts)
        if NumOfPplFeelingUnComfort>=thershold:
            #Take action Algo
            neg_nos = [num for num in number_Of_pos_neg_Rating if num < 0]
            pos_nos = [num for num in number_Of_pos_neg_Rating if num > 0] 
            numberOfposRating,numberOfnegRating=len(pos_nos),len(neg_nos)
            print(numberOfposRating,numberOfnegRating)
            if(numberOfposRating==0):
                change_temp(zone,+1)
            elif(numberOfnegRating==0):
                change_temp(zone,-1)
            elif(numberOfposRating>numberOfnegRating):
                change_temp(zone,-1)
            elif(numberOfposRating<numberOfnegRating):
                change_temp(zone,+1)

while(True):
    print("*****************************")
    mainFunction()
    time.sleep(DELAY*60)
