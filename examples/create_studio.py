from http.cookiejar import MozillaCookieJar
from json import load

from ytstudio.ytstudio import Studio

# Create using a cookies.txt file and a separate file for the session token
jar = MozillaCookieJar('cookies.txt')
jar.load()
with open('token') as fp:
    token = fp.read()

with Studio(jar, token) as studio:
    ...


# Create using the original login.json file
with open('login.json') as fp:
    cookies = load(fp)

with Studio(cookies) as studio:
    ...
