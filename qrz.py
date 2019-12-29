

# qrz.py - Functions to query the QRZ.com database


import requests
import xmltodict




class QRZerror(Exception):
    pass


class CallsignNotFound(Exception):
    pass



class QRZ:

    QRZ_BASE_URL = 'http://xmldata.qrz.com/xml/current/'
    

    def __init__(self, username, password):
        self._session = None
        self._session_key = None

        self.username = username
        self.password = password


    def _get_session(self):
        url = self.QRZ_BASE_URL + '?username={}&password={}'.\
                                   format(self.username, self.password)
        self._session = requests.Session()
        self._session.verify = False
        r = self._session.get(url)

        if r.status_code == 200:
            raw_session = xmltodict.parse(r.content)
            self._session_key = raw_session['QRZDatabase']['Session']['Key']
            if self._session_key:
                return True
        raise Exception('could not get QRZ session')


    def callsignData(self, callsign, retry=True, verbose=True):
        if self._session_key is None:
            self._get_session()

        url = self.QRZ_BASE_URL + f'?s={self._session_key}&callsign={callsign}'

        r = self._session.get(url)
        # print(f"DEBUG qrz.callsignData(): {r}")

        if r.status_code != 200:
            raise Exception("Error Querying: Response code {}".\
                            format(r.status_code))

        raw = xmltodict.parse(r.content).get('QRZDatabase')
        if not raw:
            raise QRZerror('Unexpected API Result')

        # print(f"DEBUG qrz.callsignData(): {raw}")
        
        if raw['Session'].get('Error'):
            errormsg = raw['Session'].get('Error')
            if 'Session Timeout' in errormsg or 'Invalid session key' in errormsg:
                if retry:
                    self._session_key = None
                    self._session = None

                    return self.callsign(callsign, retry=False)
                else:
                    pass
            elif "not found" in errormsg.lower():
                raise CallsignNotFound(errormsg)

            raise QRZerror(raw['Session'].get('Error'))

        else:
            callData = raw.get('Callsign')
            if callData:
                if verbose:
                    print(f"Rcvd QRZ data for: {callsign}")
                return callData

        raise Exception("Unhandled Error during Query")

    
            
