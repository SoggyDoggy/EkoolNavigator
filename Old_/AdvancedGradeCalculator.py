import requests
import time 
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'sec-ch-ua': '"Chromium";v="108", "Opera";v="94", "Not)A;Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0'}
MyCookieJar = {}
Loginpayload = {
    'email':'kingisepp.andri@pjkool.ee',
    'password':'sofy1234',
    'recaptcha':'',
    'two_factor_code':''
}
with requests.Session() as s:
    #Get the base cookies like the ekool_session and XSRF-TOKEN
    print("Hello! Getting base cookies...")
    getHeaders = s.get("https://login.ekool.eu",headers=headers)
    MyCookieJar.update(getHeaders.cookies)
    print(f"Response code: {getHeaders.status_code}")
    print(f"New cookies: {getHeaders.cookies}")
    #Update headers to be ready to log in 
    headers.update({
        'accept':'application/json, text/plain, */*',
        'content-length': '79',
        'content-type': 'application/x-www-form-urlencoded',
        'referer': 'https://login.ekool.eu/',
        'origin':'https://login.ekool.eu',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'x-requested-with':'XMLHttpRequest'})
    print("Rate limiting. 2 Seconds")
    time.sleep(2)
    print("Trying to log in...")
    login = s.post('https://login.ekool.eu/login', data=Loginpayload, headers=headers, cookies=MyCookieJar)
    print(f"Response code: {login.status_code}")
    #Get the new cookies and update headers to get session info
    MyCookieJar.update(login.cookies)
    print(f"New cookies: {login.cookies}")
    headers.update({'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'host':'login.ekool.eu',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user':'?1',
        'upgrade-insecure-requests':'1',
        'TE': 'trailers'})
    print("Rate limiting. 2 seconds")
    time.sleep(2)
    print("Updating user cookies...")
    setuser = s.get('https://login.ekool.eu/set-user', headers=headers, cookies=MyCookieJar)
    print(f"Response code: {setuser.status_code}")
    #Get the new cookies and update headers to navigate to main page
    MyCookieJar.update(setuser.cookies)
    ##UPDATE HEADERS! NEXT SITE: index_et.html