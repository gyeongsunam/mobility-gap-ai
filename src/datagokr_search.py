import re, sys, requests, html
def search(q, dtype="FILE"):
    s=requests.Session(); s.headers.update({"User-Agent":"Mozilla/5.0"})
    r=s.get("https://www.data.go.kr/tcs/dss/selectDataSetList.do", params={"keyword":q,"dType":dtype,"perPage":"20"}, timeout=60)
    out=[]
    for m in re.finditer(r'<a href="(/data/(\d+)/(fileData|standard|openapi)\.do)">(.*?)</a>(.*?)</ul>', r.text, re.S):
        title=re.sub(r'<[^>]+>','',m.group(4)); title=re.sub(r'\s+',' ',html.unescape(title)).strip()
        body=m.group(5)
        org=re.search(r'제공기관</strong>(.*?)</li>', body, re.S); upd=re.search(r'수정일</strong>(.*?)</li>', body, re.S)
        org=re.sub(r'\s+',' ',re.sub(r'<[^>]+>','',org.group(1))).strip() if org else ''
        upd=re.sub(r'\s+',' ',re.sub(r'<[^>]+>','',upd.group(1))).strip() if upd else ''
        out.append((m.group(2), m.group(3), title, org, upd))
    return out
if __name__=="__main__":
    for q in sys.argv[1:]:
        print("==",q)
        for x in search(q)[:10]: print("  ",x)
