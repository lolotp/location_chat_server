from sessions import *
from protocol import *
import os,select,time
import config;
import functools
import bcrypt
import psycopg2
import psycopg2.pool

CONN_STRING = "dbname="+config.DB_NAME+" host="+config.DB_HOST+" user="+config.DB_USERNAME+" password="+config.DB_PASSWORD+" port="+config.DB_PORT+" sslmode=require async=1"

CONN_POOL = psycopg2.pool.ThreadedConnectionPool(32,32,database=config.DB_NAME, host=config.DB_HOST, user=config.DB_USERNAME, password=config.DB_PASSWORD, port=config.DB_PORT, sslmode='require',async=1)

def wait(conn, timeout = 5.0):
    start = time.time()
    elapsed = 0
    while elapsed < timeout:
        state = conn.poll()
        print 'conn.poll() returned ', state
        if state == psycopg2.extensions.POLL_OK:
            return
        elif state == psycopg2.extensions.POLL_WRITE:
            select.select([], [conn.fileno()], [conn.fileno()], timeout-elapsed)
        elif state == psycopg2.extensions.POLL_READ:
            select.select([conn.fileno()], [], [conn.fileno()], timeout-elapsed)
        else:
            raise psycopg2.OperationalError("poll() returned %s" % state)
        elapsed = time.time() - start
    print 'timeout error'
    raise psycopg2.OperationalError("timeout time taken: %f" % elapsed)
    

def get_user_password(id, callback):
    ret = ''
    try:
        conn = CONN_POOL.getconn()
        print 'waiting on connection'
        wait(conn)
        cursor = conn.cursor()
        cursor.execute("SELECT password_digest FROM users WHERE id = %d" % (id))
        print 'waiting on execute'
        wait(conn)
        records = cursor.fetchall()
        print 'records obtained', records
        ret = records[0][0]
    except psycopg2.OperationalError as err:
        print err
        conn.cancel()
        conn.close()
        conn = psycopg2.connect(CONN_STRING)
    finally:
        CONN_POOL.putconn(conn)
    reactor.callFromThread(callback,ret)


#CONN_POOL_ADBAPI = adbapi.ConnectionPool("psycopg2",database='daec2fqh6004nj', host='ec2-23-21-79-183.compute-1.amazonaws.com', user='uekjhfc7r0fsb3', password='peplenk3n9ndksnmlrpc3n8gqm', port='5802', sslmode='require') 

def get_password_defer(userId):
    return CONN_POOL_ADBAPI.runQuery("SELECT password_digest FROM users WHERE id = %d" % (userId))

def get_user_password_async(userId, callback):
    get_password_defer(userId).addCallback(callback)

def processDbPassword(chatProtocol, receivedPwd, newUser, dbPassword):
    chatProtocol.user = newUser
    try:
        hashed = dbPassword
    except:
        hashed = ''

    if hashed == '' or bcrypt.hashpw(receivedPwd,hashed) != hashed:
        chatProtocol.message(CMD_REAUTH, str(chr(ERR_WRONG_PASSWORD)))
        return
    rememberToken = os.urandom(TOKEN_LENGTH).encode('hex')
    STORED_SESSIONS[rememberToken] = chatProtocol.user
    chatProtocol.message(CMD_TOKEN, rememberToken)

def processJoin(chatProtocol, content):
    user = User()
    user.userId = struct.unpack('<I', content[:4])[0]
    password = content[4:]
    callback = functools.partial(processDbPassword, chatProtocol, password, user)
    reactor.callInThread(get_user_password, user.userId, callback)
    return
registerProcessor(CMD_JOIN, processJoin)
