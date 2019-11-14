from flask import Flask, request, Response, jsonify,json, send_from_directory,redirect, url_for
from flaskext.mysql import MySQL
from datetime import datetime
from flask_cors import CORS
import numpy as np


mysql = MySQL()
app = Flask(__name__,static_url_path='')
CORS(app)

DB = "cooling"
HOST="10.129.149.7"
USER ="writer"
PASSWORD="datapool"

app.config['MYSQL_DATABASE_USER'] = USER
app.config['MYSQL_DATABASE_PASSWORD'] = PASSWORD
app.config['MYSQL_DATABASE_DB'] = DB
app.config['MYSQL_DATABASE_HOST'] = HOST


mysql.init_app(app)

con = mysql.connect()
cur = con.cursor()

#roomConfig
rows=5
cols=[2,3,3,3,3]
maxCol=max(cols)


#sensor config
maxSensor=7
#sensorLocRows=[1,2,3,4,5] #--have to change this 
#sensorLocCols=[2,6,10,14,18,20] #--have to change this
#sensorLocCols=[[(2,29),(7,28),(9,16),(14,15),(18,14)],[(1,27),(6,26),(11,25),(15,13),(20,12),(24,11)],[(1,24),(5,23),(12,22),(16,10),(22,9),(27,8)],[(2,21),(4,20),(8,19),(12,18),(16,17),(21,7),(29,6),(35,5)],[(1,4),(8,3),(13,2),(18,1)]]
#[,,,,,)],[5,6,7,17,18,19,20,21],[1,2,3,4]]
#sensorLocCols=[[1,6,8,13,17],[0,5,10,14,19,23],[0,4,11,15,21,26],[1,3,7,11,15,20,28,34],[0,7,12,17]]

#sensorLoc=[1,2,3,4,5,6,7,8]

#global data structure 
finalTemperatureMatrix=np.zeros((rows,maxCol))

def getSeatData(i):
    #"SELECT * FROM `dht_7` WHERE sensor_id ='temp_k_fck'"
    con = mysql.connect()
    cur = con.cursor()
    query = "select temperature from temperature_analysis where node_id = '%d' and room_name='SEIL_LAB_JAY' order by timestamp desc limit 1" %(i)
    cur.execute(query)
    res = cur.fetchone()
    con.close()
    #print res[0]
    return res[0]



def makeTempMatrix(temp):
    tempMatrix=np.zeros((rows,maxCol))
    print("**********************"+str(len(temp))+"**************")
    tempMatrix[0][0]=temp[0]
    tempMatrix[0][1]=temp[0]

    tempMatrix[1][0]=temp[0]
    tempMatrix[1][1]=temp[0]
    tempMatrix[1][2]=temp[1]

    tempMatrix[2][0]=temp[2]
    tempMatrix[2][1]=temp[2]
    tempMatrix[2][2]=(temp[2]+temp[1])/2

    tempMatrix[3][0]=(temp[2]+temp[4])/2
    tempMatrix[3][1]=(temp[2]+temp[4])/2
    tempMatrix[3][2]=temp[5]

    tempMatrix[4][0]=temp[4]
    tempMatrix[4][1]=temp[4]
    tempMatrix[4][2]=temp[5]
    print(tempMatrix)
    '''
    k=0
    for i in sensorLocRows:
        for j in sensorLocCols:
            #print(i,j,k)
            if(len(temp)>k):
                tempMatrix[i-1][j]=temp[k]
                k=k+1
    
    for i in range(0,rows):
        for j in range(0,cols[i]):
           #colSort=[]
           if(tempMatrix[i][j]==0):
               #print(i,j)
               #colSort[:] = [abs(x - j) for x in sensorLocCols]
               index1=0
               index2=0
               tempI1=0
               tempI2=0
               minimum=28
               secMin=28
               for x in sensorLocCols[i]:
                   #print(x)
                   if (abs(x-j)<minimum):
                       secMin=minimum
                       minimum=abs(x-j)
                       index2=index1
                       index1=x
                       tempI2=tempI1
                       tempI1=x
                   elif(abs(x-j)<secMin):
                       index2=x
                       tempI2=x
                       secMin=abs(x-j)
               #print("first min "+str(index1)+" "+str(tempI1))
               #print("sec min "+str(index2)+" "+str(tempI2))
               #colSort.sort()
               #print(index1)
               #print("val--j"+str(j))
               wt1=float(index1)/(index1+index2)
               wt2=float(index2)/(index1+index2)
               #print(wt1,wt2)
               tempMatrix[i][j]=wt1*tempMatrix[i][index1]+wt2*tempMatrix[i][index2]
               #print(tempMatrix[i][j])
    #print(tempMatrix)
    
    '''
    return (tempMatrix)

'''
@app.route('/getSeats', methods=['POST','GET'])
def getSeats():
    if(request.method == 'GET'):
        global finalTemperatureMatrix
        data=""
        k=1
        for i in range(0,rows):
            for j in range(0,cols[i]):
                data=data+str(k)+":"+str(finalTemperatureMatrix[i][j])+","
                k=k+1        
        cb = request.args.get('callback')
        resp = "%s('%s')" %(cb, data)
        return Response(resp, mimetype='application/javascript')
    elif request.method == 'POST':
        return 'post request not supported'
'''

@app.route('/getSeats', methods=['POST','GET'])
def getSeats():
    if(request.method == 'GET'):
        #global finalTemperatureMatrix
        #loop to extract seat temperature
        temp=[]
        for i in range(1,maxSensor):
            info = getSeatData(i)
            #print(str(i)+" "+str(info))
            temp.append(info)
        #make matrix for other seats
        print(temp)
        tempMatrix=makeTempMatrix(temp)
        #for i in range(0,rows):
        #    for j in range(0,cols[i]):
        #        finalTemperatureMatrix[i][j]=tempMatrix[i][j]
        #data="success"
        #cb = request.args.get('callback')
        #resp = "%s('%s')" %(cb, data)
        #return Response(resp, mimetype='application/javascript')
        data=""
        k=1
        for i in range(0,rows):
            for j in range(0,cols[i]):
                data=data+str(k)+":"+str(tempMatrix[i][j])+","
                k=k+1        
        cb = request.args.get('callback')
        resp = "%s('%s')" %(cb, data)
        return Response(resp, mimetype='application/javascript')
    elif request.method == 'POST':
        return 'post request not supported'


        #return jsonify({'info':d})
        '''response= app.response_class(
            response=json.dumps(l),
            status=200,
            mimetype='application/json'
        )'''
    elif request.method == 'POST':
        return 'post request not supported'

@app.route('/storeFeedback', methods=['POST','GET'])
def storeFeedbac():
    if(request.method == 'POST'):
        print(request.form['options'])
        a=request.form['options'].split(",")
        print (a[0],a[1])
        query = "insert into userFeedback(seatNumber,PMVRating,timestamp,roomName) values('%d','%d','%s','%s')" %(int(a[1]),int(a[0]),datetime.now(),'seil_lab')
        cur.execute(query)
	con.commit()
        #print(a)
    return redirect("http://10.129.149.7/lab_tc_app/seating.html")
    #return app.send_static_file('http://10.129.149.7/ayush/seatingArr.html')	
    #return send_from_directory('/static/','seatingArr.html')
        #return jsonify({'info':d})
    #return send_from_directory('js','seatingArr.html')
    #return render_template('ayush/')


@app.route('/')
def index():
    return 'it works'


if __name__ == '__main__':
    app.run('10.129.149.7',port=7000, debug=True)
