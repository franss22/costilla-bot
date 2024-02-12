import gspread
from varenv import getVar
import json

credentials = json.loads(getVar("GOOGLE"), strict=False)

gc = gspread.service_account_from_dict(credentials)

sh = gc.open("Megamarch")

print(sh.get_worksheet_by_id(0).get("B:B"))