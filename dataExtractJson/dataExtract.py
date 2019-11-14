from flask import Flask, request, Response, jsonify,json
from flaskext.mysql import MySQL
from datetime import datetime


mysql = MySQL()
app = Flask(__name__)

DB = "seil_sensor_data"
HOST="mysql.seil.cse.iitb.ac.in"
USER ="root"
PASSWORD="MySQL@seil"

app.config['MYSQL_DATABASE_USER'] = USER
app.config['MYSQL_DATABASE_PASSWORD'] = PASSWORD
app.config['MYSQL_DATABASE_DB'] = DB
app.config['MYSQL_DATABASE_HOST'] = HOST


mysql.init_app(app)

con = mysql.connect()
cur = con.cursor()



#sensor config
maxSensor=5

def getSeatData(i):
    #"SELECT * FROM `dht_7` WHERE sensor_id ='temp_k_fck'"
    query = "select temperature from dht_7 where sensor_id ='temp_k_fck' and id = '%d' order by TS desc limit 1" %(i)
    cur.execute(query)
    res = cur.fetchone()
    print res
    return res[0]




        # dict={}
        # loop to extract seat temperature
        #for i in range(1,maxSensor):
@app.route('/getSeats', methods=['POST','GET'])
def getSeats():
    if(request.method == 'GET'):
        #l=[]
        #loop to extract seat temperature
        d={}
        for i in range(1,maxSensor):
            info = getSeatData(i)
            #give color combination
            #make matrix for other seats
            d[i]=info
            #l.append({'1':str(info), '2':'Red'})
        return jsonify({'info':d})
        '''response= app.response_class(
            response=json.dumps(l),
            status=200,
            mimetype='application/json'
        )
        #resp = "%s('%s')" %(cb, info)
        #return Response(resp, mimetype='application/json')
        return response'''
    elif request.method == 'POST':
        return 'post request not supported'



@app.route('/')
def index():
    return 'it works'


if __name__ == '__main__':
    app.run('0.0.0.0',port=7000, debug=True)
