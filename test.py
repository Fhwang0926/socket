from urllib.parse import urlparse
import http.client as http_

def chk_http_type(url):
  url = urlparse(url)
  conn = http_.HTTPConnection(url.netloc)
  conn.request("HEAD", url.path)
  if conn.getresponse():
    return "http"
  else:
    return "https"

if __name__ == "__main__":
  url = "http://httpbin.org"
  url_https = "https://" + url.split("//")[1]
  if check_url(url_https):
    print("Nice, you can load it with https")
  else:
    if check_url(url):
      print("https didn't load, but you can use http")
  if check_url(url):
    print("Nice, it does load with http too")