import _sslfixer
import webbrowser
import random
import requests
import string
from wxUI import two_factor_auth
class AuthenticationError(Exception):
    pass

class ValidationError(Exception):
    pass

class C2DMError(Exception):
    pass

client_id = '2685278'
client_secret = 'lxhD8OD7dMsqtXIm5IUY'
api_ver='5.70'
scope = 'all'
user_agent = 'KateMobileAndroid/47-427 (Android 6.0.1; SDK 23; armeabi-v7a; samsung SM-G900F; ru)'
android_id = '4119748609680577006'
android_token = '5228540069896927210'
api_url = 'https://api.vk.com/method/'

def requestAuth(login, password, scope=scope):
    if not (login or password):
        raise ValueError
    url = 'https://oauth.vk.com/token?grant_type=password&2fa_supported=1&client_id='+client_id+'&client_secret='+client_secret+'&username='+login+'&password='+password+'&v='+api_ver+'&scope='+scope
    headers = {
    'User-Agent': user_agent
    }
    r = requests.get(url, headers=headers)
    if r.status_code == 200 and 'access_token' in r.text:
        res = r.json()
        access_token = res['access_token']
        user_id = str(res['user_id'])
        return access_token, user_id
    else:
        # Two factor auth is not supported in this method as it returns invalid code all the time.
#        t = r.json()
#        print t
#        q = requests.get(t["redirect_uri"], headers=headers)
#        print q.text
#        code, remember = two_factor_auth()
#        url = 'https://oauth.vk.com/token?grant_type=password&client_id='+client_id+'&client_secret='+client_secret+'&username='+login+'&password='+password+'&v='+api_ver+'&scope='+scope+'&code='+code+'&remember_device='+str(int(remember))
#        print url
#        r = requests.get(url, headers=headers)
#        print r.text
        raise AuthenticationError(r.text)

def getReceipt(user_id):
    if not user_id:
        raise ValueError
    url = 'https://android.clients.google.com/c2dm/register3'
    headers = {
    'Authorization': 'AidLogin {0}:{1}'.format(android_id, android_token),
    'app': 'com.perm.kate',
    'Gcm-ver': '11951438',
    'Gcm-cert': 'ca7036ce4c5abe56b9f4439ea275171ceb0d35a4',
    #'User-Agent': 'Android-GCM/1.5 (klte NJH47F)',
    'content-type': 'application/x-www-form-urlencoded',
    }
    data = {
    'X-subtype': '54740537194',
    'X-X-subscription': '54740537194',
    'X-X-subtype': '54740537194',
    'X-app_ver': '427',
    'X-kid': '|ID|1|',
    #'X-osv': '23',
    'X-cliv': 'iid-9452000',
    'X-gmsv': '11951438',
    'X-X-kid': '|ID|1|',
    'X-appid': ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(11)),
    'X-scope': 'id'+user_id,
    'X-subscription': '54740537194',
    'X-app_ver_name': '47',
    'app': 'com.perm.kate',
    'sender': '54740537194',
    'device': android_id,
    'cert': 'ca7036ce4c5abe56b9f4439ea275171ceb0d35a4',
    'app_ver': '427',
    'gcm_ver': '11951438'
    }
    r = requests.post(url, headers=headers, data=data)
    if r.status_code == 200 and 'token' in r.text:
        return r.text[13:]
    else:
        raise C2DMError(r.text)

def validateToken(token, receipt):
    if not (token or receipt):
        raise ValueError
    url = api_url+'auth.refreshToken?access_token='+token+'&receipt='+receipt+'&v='+api_ver
    headers = {'User-Agent': user_agent}
    r = requests.get(url, headers=headers)
    if r.status_code == 200 and 'token' in r.text:
        res = r.json()
        received_token = res['response']['token']
        if token == received_token or received_token is None :
            raise ValidationError(r.text)
        else:
            return received_token
    else:
        raise ValidationError(r.text)
