import time
import pandas as pd
from datetime import datetime
import psycopg2
import threading
import logging

def createDB():
    conn = psycopg2.connect("dbname=dq user=dq")
    cur = conn.cursor()
    cur.execute("""CREATE TABLE distortions(
        ticker text,
        fastAvat integer,
        slowAvat integer,
        avatScore integer, 
        σIndex integer,
        volatilityScore integer,
        macdReversal integer,
        breakout integer,
        emaCrossFast integer,
        emaCrossSlow integer,
        ddCross integer,
        ddPoke integer,
        hurst integer,
        score integer,
        inputDate timestamp
        )
    """)
    cur.execute("""CREATE TABLE target(
        ticker text,
        target7dLong numeric(10,6),
        upside7dLongPerc numeric(10,6),
        stop7dLong numeric(10,6), 
        downside7dLongPerc numeric(10,6),
        target7dShort numeric(10,6),
        upside7dShortPerc numeric(10,6),
        stop7dShort numeric(10,6),
        downside7dShortPerc numeric(10,6),
        inputDate timestamp
        )
    """)
    conn.commit()
def cleanDB(table):
    conn = psycopg2.connect(user="postgres", password="WY-6)aTuiI|jsrGa&Dg[[r%{;]Y5!53:^n4$$;aN:Zxr(4(z8O", host="database-quant.coniwvjhjdwz.us-west-2.rds.amazonaws.com", port="5432")
    cur = conn.cursor()
    logging.warning('Deleting table ' + str(table) + ' history!')
    sql = "DELETE FROM " + str(table) + " where inputDate < (current_date - 120)"
    #sql = "DELETE FROM distortions"
    cur.execute(sql)
    conn.commit()
    cur.close()
def insertDB(data, table):
    dt = datetime.now()
    conn = psycopg2.connect(user="postgres", password="WY-6)aTuiI|jsrGa&Dg[[r%{;]Y5!53:^n4$$;aN:Zxr(4(z8O", host="database-quant.coniwvjhjdwz.us-west-2.rds.amazonaws.com", port="5432")
    cur = conn.cursor()
    data.insert(loc=0, column='inputDate', value=dt)
    cols = ", ".join([str(i) for i in data.columns.tolist()])
    logging.warning('Inserting into ' + str(table) + ' table!')
    for i, row in data.iterrows():
        try:
            sql = "INSERT INTO " + str(table) + " (" + cols + ") VALUES (" + "%s,"*(len(row)-1) + "%s)"
            cur.execute(sql, tuple(row))
            conn.commit()
        except:
            logging.warning('Error inserting. Getting next one!')
            conn.rollback()
    cur.close()
def processDistortions(name):
    logging.warning("Executing " + str(name) + " quant algo!")
    df = pd.read_excel('dashboard_online_quant.xlsx', 'Distortions')
    df = df[['TICKER','Fast AVAT','slow AVAT','AVAT Score','σ ','Volatility Score','MACD Reversal','Breakout','EMA Cross Fast','EMA Cross Slow','DD Cross','DD Poke','Hurst','SCORE']]
    df.columns = ['ticker','fastAvat','slowAvat','avatScore','σIndex','volatilityScore','macdReversal','breakout','emaCrossFast','emaCrossSlow','ddCross','ddPoke','hurst','score']
    cleanDB('Distortions')
    insertDB(df, 'Distortions')
        
def processTarget(name):
    logging.warning("Executing " + str(name) + " quant algo!")
    df = pd.read_excel('dashboard_online_quant.xlsx', 'Target')
    df = df[['TICKER','TARGET 7D Long','UPSIDE 7D Long','STOP 7D Long','DOWNSIDE 7D Long','TARGET 7D Short','UPSIDE 7D Short','STOP 7D Short','DOWNSIDE 7D Short']]
    df.columns = ['ticker','target7dLong','upside7dLongPerc','stop7dLong','downside7dLongPerc','target7dShort','upside7dShortPerc','stop7dShort','downside7dShortPerc']
    cleanDB('Target')
    insertDB(df, 'Target')

if __name__ == '__main__':
    while True:
        try:
            threads = list()
            x = threading.Thread(target=processDistortions, args=('Distortions',))
            threads.append(x)
            x.start()
            y = threading.Thread(target=processTarget, args=('Target',))
            threads.append(y)
            y.start()
            logging.warning("Waiting Threads to finish...")
            for index, thread in enumerate(threads):
                thread.join()
            logging.warning('Sleeping for next round...')
            time.sleep(300)
        except:
            print("Houston we have a problem! Rebooting...")
            time.sleep(10)