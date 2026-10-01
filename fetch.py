import json, datetime as dt, requests

URL = "https://api.bseindia.com/BseIndiaAPI/api/AnnSubCategoryGetData/w"
H = {"User-Agent": "Mozilla/5.0",
     "Referer": "https://www.bseindia.com/",
     "Origin": "https://www.bseindia.com"}

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
    r = requests.get(URL, headers=H, timeout=30, params={
        "pageno": 1, "strCat": "-1", "strPrevDate": frm,
        "strScrip": c["code"], "strSearch": "P",
        "strToDate": to, "strType": "C"})
    print(c["name"], r.status_code)
    r.raise_for_status()
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
