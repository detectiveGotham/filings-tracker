import json, datetime as dt, requests

URL = "https://api.bseindia.com/BseIndiaAPI/api/AnnSubCategoryGetData/w"
S = requests.Session()
S.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.bseindia.com/",
    "Origin": "https://www.bseindia.com"})
try:
    S.get("https://www.bseindia.com/", timeout=30)
except Exception as e:
    print("warmup failed", e)

wl = json.load(open("watchlist.json"))
try:
    old = json.load(open("data.json"))
except Exception:
    old = []
seen = {x["id"] for x in old}
today = dt.date.today()
frm = (today - dt.timedelta(days=3)).strftime("%Y%m%d")
to = today.strftime("%Y%m%d")

new = []
for c in wl:
    try:
        r = S.get(URL, timeout=30, params={
            "pageno": 1, "strCat": "-1", "strPrevDate": frm,
            "strScrip": c["code"], "strSearch": "P",
            "strToDate": to, "strType": "C"})
    except Exception as e:
        print(c["name"], "error", e)
        continue
    print(c["name"], r.status_code)
    if r.status_code != 200:
        continue
    for a in r.json().get("Table", []):
        i = str(a.get("NEWSID"))
        if i in seen:
            continue
        att = a.get("ATTACHMENTNAME")
        new.append({
            "id": i, "name": c["name"], "code": c["code"],
            "date": a.get("NEWS_DT"),
            "subject": a.get("NEWSSUB") or a.get("HEADLINE"),
            "bse_cat": a.get("CATEGORYNAME"),
            "pdf": f"https://www.bseindia.com/xml-data/corpfiling/AttachLive/{att}" if att else None,
        })

data = sorted(new + old, key=lambda x: x["date"] or "", reverse=True)[:1000]
json.dump(data, open("data.json", "w"), indent=1)
print("new items:", len(new))

