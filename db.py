
# db.py - sqlite3 database class


import datetime
import re
import sqlite3
from inspect import currentframe, getframeinfo

from qrz import *


# An sqlite database that mirrors my LOTW database. The real purpose
# of this database is to track QSL cards. The LOTW database is the
# master database and this database is updated from that. This
# database contains several tables.

class LogDatabase:

    def __init__(self, dbFile):
        # try to connect to sqlite database, if database doesn't
        # exist, it will be created. Then check if the log table
        # exists, if not create it
        self.databaseFile = dbFile

        with sqlite3.connect(dbFile) as conn:

            sql =  "CREATE TABLE IF NOT EXISTS metadata "
            sql += "(metadata_id integer primary key, "
            sql += "last_db_sync varchar(16)"
            sql += ")"
            for row in conn.execute(sql):
                print(row)

            sql =  "CREATE TABLE IF NOT EXISTS lotwlog "
            sql += "(lotw_id integer primary key, "
            sql += "call varchar(16), band varchar(8), "
            sql += "freq float(20, 10), mode varchar(8), "
            sql += "app_lotw_modegroup varchar(16), "
            sql += "qso_date varchar(16), time_on varchar(16), "
            sql += "qsl_rcvd varchar(8), qslrdate varchar(16), "
            sql += "callsigndata_id int, "
            sql += "qslcard_id int, "
            sql += "FOREIGN KEY (callsigndata_id) "
            sql += "REFERENCES callsigndata(callsigndata_id), "
            sql += "FOREIGN KEY (qslcard_id) "
            sql += "REFERENCES qslcard(qslcard_id)"
            sql += ")"
            for row in conn.execute(sql):
                print(row)

            sql = "CREATE TABLE IF NOT EXISTS callsigndata "
            sql += "(callsigndata_id integer primary key, "
            sql += "call varchar(16), fname varchar(256), name varchar(256), "
            sql += "addr1 varchar(256), addr2 varchar(256), state varchar(8), "
            sql += "zip varchar(8), country varchar(256), lat varchar(16), "
            sql += "lon varchar(16), grid varchar(8), county varchar(256), "
            sql += "timezone varchar(32))"
            for row in conn.execute(sql):
                print(row)

            sql = "CREATE TABLE IF NOT EXISTS qslcard "
            sql += "(qslcard_id integer primary key, qslrcvd varchar(64), "
            sql += "qslsent varchar(64), logstation_qsl varchar(256), "
            sql += "rcvddate varchar(16), sentdate varchar(16))"
            for row in conn.execute(sql):
                print(row)

            sql = "SELECT SQLITE_VERSION()"
            for row in conn.execute(sql):
                print('sqlite version: ', row[0])

            


    def syncLotwLog(self, logDict):
        # This method updates or inserts logging data from LOTW. The
        # LOTW database is the master database so this database tracks
        # any changes to that with the exception of the QSL Card
        # fields.

        print('Downloading LOTW data and insert/update into local database...')
        
        numRecordsInserted = 0
        numRecordsUpdated = 0

        with sqlite3.connect(self.databaseFile) as conn:
            cur = conn.cursor()

            for elem in logDict:
                # debug
                # print('-----------------------------------------------------------------')
                # print('elem: ', elem)

                sql =  "SELECT * FROM lotwlog WHERE "
                sql += "call='{}' AND mode='{}' AND band='{}' ".\
                              format(elem['call'], elem['mode'], elem['band'])
                sql += "AND qso_date='{}'".format(elem['qso_date'])
                # print('select: ', sql)
                
                cur.execute(sql)
                if cur.fetchone() == None:
                    # log entry from LOTW is not in database, insert this new record
                    
                    # print('log entry {} not in database, insert...'.\
                    #       format(elem['call']))
                    
                    sql =  "INSERT INTO lotwlog "
                    sql += "(call, band, freq, mode, app_lotw_modegroup, qso_date, "
                    sql += "time_on, qsl_rcvd"
                    if 'qslrdate' in elem:
                        sql += ", qslrdate) "
                    else:
                        sql += ") "
                    sql += "VALUES ('{}', '{}', '{}', ".\
                           format(elem['call'], elem['band'], elem['freq'])
                    sql += "'{}', '{}', '{}', '{}', '{}'".\
                           format(elem['mode'], elem['app_lotw_modegroup'],
                                  elem['qso_date'], elem['time_on'],
                                  elem['qsl_rcvd'])
                    if 'qslrdate' in elem:
                        # won't have qslrdate unless QSL is true, so
                        # check if that key is in the dict
                        sql += ", '{}')".format(elem['qslrdate'])
                    else:
                        sql += ")"
                    print('insert: ', sql)
                    cur.execute(sql)
                    numRecordsInserted += cur.rowcount
                    for row in cur.fetchall():
                        print('insert: ', row)
                else:
                    # print('log entry {} in database, update...'.\
                    #       format(elem['call']))
                    
                    # Do an UPDATE to update the records values from the
                    # LOTW data if the record already exists in the
                    # database
                    sql =  "UPDATE lotwlog SET "
                    sql += "qsl_rcvd='{}' ".format(elem['qsl_rcvd'])
                    if 'qslrdate' in elem:
                        # won't have qslrdate unless QSL is true, so
                        # check if that key is in the dict
                        sql += ", qslrdate='{}' ".format(elem['qslrdate'])
                    sql += "WHERE call='{}' AND band='{}' AND freq='{}' ".\
                                        format(elem['call'], elem['band'],
                                               elem['freq'])
                    sql += "AND mode='{}' AND qso_date='{}' ".format(elem['mode'],
                                                                     elem['qso_date'])
                    sql += "AND time_on='{}'".format(elem['time_on'])
                    # print('update: ', sql)
                    cur.execute(sql)
                    numRecordsUpdated += cur.rowcount
                    for row in cur.fetchall():
                        print('update: ', row)

            print('Records inserted: ', numRecordsInserted)
            print('Records updated:  ', numRecordsUpdated)


    def _syncQRZData(self, qrzUsername, qrzPassword):
        # This method inserts or updates in the 'callsigndata' table,
        # which contains callsign information from the QRZ
        # database. The callsigndata table has a 'one-to-many'
        # relationship with the lotwlog table. Each QSO in the lotwlog
        # table contains a foreign key that points to the callsign
        # information contained in the callsigndatata table linking
        # the callsign information of the QSO. This is a private
        # method that is executed either serially for some program
        # functions or as a background process for others.

        print('Updating QRZ callsign information in the local database...')

        # Init QRZ connection object
        qrz = QRZ(qrzUsername, qrzPassword)

        # Query the lotwlog table for records that don't have the
        # foreigh key callsigndata_id set. This indicates that there
        # is no callsign data for linked for that QSO. Store the
        # information about these records in a list for further
        # processing.
        lotwList = []
        conn = sqlite3.connect(self.databaseFile)
        cur = conn.cursor()

        sql = "SELECT lotw_id, call from lotwlog WHERE callsigndata_id IS NULL"
        cur.execute(sql)
        for row in cur.fetchall():
            lotwList.append(row)

        # Loop over the list of QSOs needing callsign data and either
        # get the callsign data or link the callsign data, if it
        # already exists in the callsigndata table, to the QSO record
        # in the lotwlog table.
        for i in lotwList:
            # debug
            # print('lotw: ', i)

            try:
                callData = qrz.callsignData(i[1])
                # print('call: ', callData)

                sql =  "INSERT OR REPLACE INTO callsigndata "
                colSql = "("
                valSql = "VALUES ("

                if 'call' in callData:
                    colSql += "call"
                    valSql += "'{}'".format(callData['call'])
                if 'fname' in callData:
                    colSql += ", fname"
                    valSql += ", '{}'".format(callData['fname'])
                if 'name' in callData:
                    colSql += ", name"
                    valSql += ", '{}'".format(callData['name'])
                if 'addr1' in callData:
                    colSql += ", addr1"
                    valSql += ", '{}'".format(callData['addr1'])
                if 'addr2' in callData:
                    colSql += ", addr2"
                    valSql += ", '{}'".format(callData['addr2'])
                if 'state' in callData:
                    colSql += ", state"
                    valSql += ", '{}'".format(callData['state'])
                if 'zip' in callData:
                    colSql += ", zip"
                    valSql += ", '{}'".format(callData['zip'])
                if 'country' in callData:
                    colSql += ", country"
                    valSql += ", '{}'".format(callData['country'])
                if 'lat' in callData:
                    colSql += ", lat"
                    valSql += ", '{}'".format(callData['lat'])
                if 'lon' in callData:
                    colSql += ", lon"
                    valSql += ", '{}'".format(callData['lon'])
                if 'grid' in callData:
                    colSql += ", grid"
                    valSql += ", '{}'".format(callData['grid'])
                if 'county' in callData:
                    colSql += ", county"
                    valSql += ", '{}'".format(callData['county'])
                if 'TimeZone' in callData:
                    colSql += ", timezone"
                    valSql += ", '{}'".format(callData['TimeZone'])

                colSql += ")"
                valSql += ")"
                sql += colSql + " " + valSql
                # print('sql: ', sql)
                # print('------------------------------------------------------------------------------')
                cur.execute(sql)
                for row in cur.fetchall():
                    print('callsigndata insert: ', row)
                conn.commit()

                # Now insert the callsigndata record's primary key
                # into the foreign key in the lotwlog record to
                # establish the link between the callsign data and the
                # QSO record
                sql =  "UPDATE lotwlog set callsigndata_id = "
                sql += "(SELECT callsigndata_id FROM callsigndata "
                sql += "WHERE call = '{}')".format(callData['call'])
                sql += " WHERE call = '{}'".format(callData['call'])
                # print('sql: ', sql)
                
                cur.execute(sql)
                for row in cur.fetchall():
                    print('callsigndata_id insert: ', row)
                conn.commit()
                # print('===============================================================================')

            except CallsignNotFound:
                print("_syncQRZData() Callsign {} not in QRZ database".format(i[1]))
            except Exception as e:
                print("_syncQRZData() Caught exception '{}' for callsign {}".format(e, i[1]))

        # update metadata table with date-time group of last DB sync
        sql =  "UPDATE metadata SET last_db_sync = {}".format(self._getDTG_UTC())
        sql += " WHERE metadata_id = 1"

        # debug
        # frameinfo = getframeinfo(currentframe())
        # print('{}: {}: {}'.format(frameinfo.filename, frameinfo.lineno, sql))
        
        cur.execute(sql)
        for row in cur.fetchall():
            print('metadata update: ', row)
        conn.commit()
        
        conn.close()


    def syncQRZData(self, qrzUsername, qrzPassword):
        self._syncQRZData(qrzUsername, qrzPassword)


    def syncQRZDataBackground(self, qrzUsername, qrzPassword):
        pass
    
        
    # perform an SQL query of the local database
    def doDBQuery(self, sql):
        resultLst = []
        
        with sqlite3.connect(self.databaseFile) as conn:
            for row in conn.execute(sql):
                resultLst.append(row)

        return resultLst
        
            
    def getDBLOTWDuplicates(self):
        resultLst = []
        
        with sqlite3.connect(self.databaseFile) as conn:
            sql = "SELECT call, band, qso_date, mode, time_on, count(*) FROM lotwlog "
            sql += "GROUP BY call, band, qso_date, mode, time_on HAVING count(*) > 1"
            for row in conn.execute(sql):
                resultLst.append(row)

        return resultLst


    def getDBCallSignDuplicates(self):
        resultLst = []
        
        with sqlite3.connect(self.databaseFile) as conn:
            sql = "SELECT call, count(*) FROM callsigndata "
            sql += "GROUP BY call HAVING count(*) > 1"
            for row in conn.execute(sql):
                resultLst.append(row)

        return resultLst
    

    def fixDBCallSignDuplicates(self):

        dupLst = self.getDBCallSignDuplicates()

        conn = sqlite3.connect(self.databaseFile)
        cur = conn.cursor()

        for i in dupLst:
            call = i[0]

            # Get the callsigndata_id associated of this callsign
            sql = "SELECT callsigndata_id FROM callsigndata "
            sql += "WHERE call = '{}'".format(call)
            cur.execute(sql)
            callIDLst = cur.fetchall()
            for id in callIDLst:
                callID = id[0]

                sql = "SELECT * from lotwlog WHERE callsigndata_id = {}".format(callID)
                cur.execute(sql)
                if cur.fetchone() is None:
                    # This callsigndata_id isn't in lotwlog and is a
                    # duplicate, so it should be deleted
                    sql = "DELETE FROM callsigndata "
                    sql += "WHERE callsigndata_id = {}".format(callID)
                    cur.execute(sql)
                    conn.commit()
                    print('deleted duplicate callsigndata record for id: ', id[0])

        conn.close()



    # Return the date-time group of UTC
    def _getDTG_UTC(self):
        utc = datetime.datetime.utcnow()
        return utc.strftime('%Y%m%d%H%M')
        
