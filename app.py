from threading import Lock
from flask import Flask, render_template, session, request, jsonify, url_for
from flask_socketio import SocketIO, emit, disconnect
import MySQLdb       
import math
import time
import configparser as ConfigParser
import random
import serial

async_mode = None

app = Flask(__name__)


config = ConfigParser.ConfigParser()
config.read('config.cfg')
myhost = config.get('mysqlDB', 'host')
myuser = config.get('mysqlDB', 'user')
mypasswd = config.get('mysqlDB', 'passwd')
mydb = config.get('mysqlDB', 'db')
print(myhost)


app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock() 

ser= serial.Serial("/dev/ttyS0")
ser.baudrate = 9600

def background_thread(args):
    count = 0  
    dataCounter = 0
    q = 0
    dataList = []  
    db = MySQLdb.connect(host=myhost,user=myuser,passwd=mypasswd,db=mydb)
    dbV = 'nieco' 
    while True:
        if args:
            print('Moje args: ')
            print(args)
            #A = dict(args).get('A')
            dbV = dict(args).get('db_value')         
        #else:
        #    print('nemam args')
        A = 1
        #print A
        print(dbV) 
        print(args)
        socketio.sleep(2)
        count += 1
        dataCounter +=1
        q+=1
        h = ser.readline()
        h = h.decode()
        t = ser.readline()
        t = t.decode()
        p = ser.readline()
        p = p.decode()
        p=float(p)
        h=float(h)
        t=float(t)        
        if dbV == 'start':
          dataDict = {            
            "h": h,
            "t": t,
            "p": p,
            "x": dataCounter}
          dataList.append(dataDict)
        else:
          if len(dataList)>0:
            print(str(dataList))            
            fuj = str(dataList).replace("'", "\"")
            print(fuj)
            cursor = db.cursor()
            cursor.execute("SELECT MAX(id) FROM graph")
            maxid = cursor.fetchone()
            cursor.execute("INSERT INTO graph (id, hodnoty) VALUES (%s, %s)", (maxid[0] + 1, fuj))
            db.commit()
            fo = open("static/files/test.txt","a+")
            fo.write("%s\r\n" %fuj)
            fo.close()
          dataList = []
          dataCounter = 0
        socketio.emit('my_response', {'datah': h, 'datat': t,'datap': p,'datax': dataCounter,'dataq': q}, namespace='/test')  
    db.close()

#@app.route('/')
#def index():
 #   return render_template('index.html', async_mode=socketio.async_mode)

@app.route('/')
def hello():
    return render_template('tabs.html')

@app.route('/index', methods=['GET', 'POST'])
def gauge():
    return render_template('index.html', async_mode=socketio.async_mode)

# @app.route('/write')
# def write2file():
  #   fo = open("static/files/test.txt","a+")
    #for i in dataList:
   #    fo.write(dataList[i])
    # fuj = '%fuj'
    # fo.write("%s\r\n" %fuj)
#     return "done"

# @app.route('/graph', methods=['GET', 'POST'])
# def graph():
#     return render_template('graph.html', async_mode=socketio.async_mode)

# @app.route('/graphlive', methods=['GET', 'POST'])
# def graphlive():
#    return render_template('graphlive.html', async_mode=socketio.async_mode)

#@app.route('/gauge', methods=['GET', 'POST'])
#def gauge():
#    return render_template('gauge.html', async_mode=socketio.async_mode)

@app.route('/db')
def db():
  db = MySQLdb.connect(host=myhost,user=myuser,passwd=mypasswd,db=mydb)
  cursor = db.cursor()
  cursor.execute('''SELECT  hodnoty FROM  graph WHERE id=1''')
  rv = cursor.fetchall()
  return str(rv)    

@app.route('/dbdata/<string:num>', methods=['GET', 'POST'])
def dbdata(num):
  db = MySQLdb.connect(host=myhost,user=myuser,passwd=mypasswd,db=mydb)
  cursor = db.cursor()
  print(num)
  cursor.execute("SELECT hodnoty FROM  graph WHERE id=%s", num)
  rv = cursor.fetchone()
  return str(rv[0])
    
@socketio.on('my_event', namespace='/test')
def test_message(message):   
    session['receive_count'] = session.get('receive_count', 0) + 1 
    session['A'] = message['value']    
    emit('my_response',
         {'data': message['value'], 'count': session['receive_count']})

@socketio.on('db_event', namespace='/test')
def db_message(message):
    #print('moj message: ', message)
    print('teraz message: ')
    print(message)
    #dbV = message['value']
    #session['receive_count'] = session.get('receive_count', 0) + 1 
    session['db_value'] = message['value']    
    #emit('my_response',
      #   {'data': message['value'], 'count': session['receive_count']})
@app.route('/read/<string:num>')
def readmyfile(num):
    fo = open("static/files/test.txt","r")
    rows = fo.readlines()
    return rows[int(num)-1]


@socketio.on('disconnect_request', namespace='/test')
def disconnect_request():
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']})
    disconnect()

@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread, args=session._get_current_object())
   # emit('my_response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)


if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=80, debug=True)
