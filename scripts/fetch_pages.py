import urllib.request, sys
paths=['/','/products/','/products/login/','/login/','/products/register/','/cart/','/products/checkout/']
for p in paths:
    url='http://127.0.0.1:8000'+p
    try:
        resp=urllib.request.urlopen(url, timeout=5)
        data=resp.read().decode('utf-8','ignore')
        print('---',p,'STATUS',resp.getcode(),'LEN',len(data))
    except Exception as e:
        print('---',p,'ERROR',repr(e))
