"""
Example: parse JSON.
"""

from peglet import *

# N.B. The grammar at
# http://www.udacity.com/view#Course/cs212/CourseRev/apr2012/Unit/207010/Nugget/152008
# uses . for '.' and this accepts any character there, right? Looks like a bug.
# Another: ftpaddress's (; ftptype) should be optional.
# Another: port: digits should not have (| path)
# Another?: path: void | ...  (wrong order for PEG parsing)

def maker(name):
    return lambda value: (name, value)

mk_host     = maker('host')
mk_path     = maker('path')
mk_search   = maker('search')
mk_fragment = maker('fragment')
mk_port     = maker('port')

# Following http://www.w3.org/Addressing/URL/5_BNF.html
# but leaving out some of the alternatives for url.
# This clearly isn't the modern definition of an httpaddress
# (see the 'right=wrong' example below).
url_parse = Parser(r"""
start         = url $

url           = httpaddress | ftpaddress | mailtoaddress

ftpaddress    = ftp:// login [/] path opt_ftptype
opt_ftptype   = ; ftptype | 

login         = opt_userpass hostport
opt_userpass  = user : password @
              | user @
              | 
user          = alphanum2 user
              | alphanum2
password      = alphanum2 password
              | alphanum2
alphanum2     = alpha | digit | [-_.+]

ftptype       = [AE] formcode
              | [I]
              | [L] digits
formcode      = [NTC]

mailtoaddress = mailto: xalphas @ hostname

httpaddress   = http:// hostport opt_path opt_search opt_fragment
opt_path      = / path       join mk_path | 
opt_search    = [?] search   join mk_search | 
opt_fragment  = # fragmentid join mk_fragment | 

hostport      = host : port
              | host

host          = host_syntax   join mk_host
host_syntax   = hostname | hostnumber
hostname      = ialpha ([.]) hostname
              | ialpha
hostnumber    = digits ([.]) digits ([.]) digits ([.]) digits

port          = digits   join mk_port

path          = segment (/) path
              | segment
              | 
segment       = xpalphas

search        = xalphas ([+]) search
              | xalphas

fragmentid    = xalphas

xalpha        = alpha | digit | safe | extra | escape
xalphas       = xalpha xalphas
              | xalpha

xpalpha       = xalpha | [+]
xpalphas      = xpalpha xpalphas
              | xpalpha

ialpha        = alpha xalphas
              | alpha

alpha         = ([a-zA-Z])
digit         = (\d)
safe          = ([$_@.&+-])
extra         = ([!*"'(),])
escape        = (%) hex hex 
hex           = ([\dA-Fa-f])
digits        = (\d+)
alphanum      = alpha | digit
alphanums     = alphanum alphanums
              | alphanum

reserved      = [=;/#?: ]
national      = [{}|\[\]\\^~]
punctuation   = [<>]
""", **globals())

## attempt(url_parse, 'true')
## attempt(url_parse, 'http://google.com')
#. (('host', 'google.com'),)
## url_parse('http://en.wikipedia.org/wiki/Uniform_resource_locator')
#. (('host', 'en.wikipedia.org'), ('path', 'wiki/Uniform_resource_locator'))
## attempt(url_parse, 'http://wry.me/fun/toys/yes.html?right=wrong#fraggle')
## url_parse('http://wry.me/fun/toys/yes.html?rightwrong#fraggle')
#. (('host', 'wry.me'), ('path', 'fun/toys/yes.html'), ('search', 'rightwrong'), ('fragment', 'fraggle'))
