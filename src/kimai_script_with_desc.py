import requests
from datetime import datetime
import calendar
import holidays

# ============================
# CONFIG
# ============================
KIMAI_URL = "https://kimai-new.finartz.dev/tr/timesheet/create"
PHPSESSID = "will be overrided"

DEFAULT_DATA = {
    "customer": 11,
    "project": 68,
    "activity": 1,
    "tags": "@ev, "
}

HEADERS = {
    "Accept": "*/*",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest"
}

COOKIES = {
    "PHPSESSID": PHPSESSID
}

TODAY = datetime.now().date()

tr_holidays = holidays.Turkey(years=2025)

# ============================
# INPUTS
# ============================
def ask_token():
    return input("🔑 Kimai _token gir: ").strip()

def ask_sessionid():
    return input("🔑 Kimai php session id gir: ").strip()

def ask_sprint_planning_days():
    raw = input(
        "📌 Sprint planning perşembeleri (ayın kaçıncı perşembeleri? örn: 1,3): "
    )
    return {int(x.strip()) for x in raw.split(",")}

def ask_leave_days():
    raw = input(
        "📌 İzinli günlerin (ayın kaçında? örn: 1,3): "
    )
    return {int(x.strip()) for x in raw.split(",")}

def ask_office_days():
    raw = input(
        "📌 Ofis günlerin (ayın kaçında? örn: 1,3): "
    )
    return {int(x.strip()) for x in raw.split(",")}


def ask_start_day():
    raw = input("▶️ Kaçıncı günden başlansın? (boş = ayın başı): ").strip()
    return int(raw) if raw else 1

def ask_descriptions(date_obj):
    print(f"\n📝 {date_obj.strftime('%Y-%m-%d')} tarihi açıklamaları:")
    
    return {
        ("09:00", "12:00"): "Daily Toplantısı, " + input("  09:00–12:00: "),
        ("13:00", "18:00"): input("  13:00–18:00: ")
    }


# ============================
# CREATE DAY
# ============================
def create_timesheet_for_day(date_obj, token, sprint_planning_days, leave_days, office_days):
    date_str = date_obj.strftime("%Y-%m-%d")
    responses = []

    is_leave_day = date_obj.day in leave_days
    is_office_day = date_obj.day in office_days
    is_planning_day = date_obj.day in sprint_planning_days
    holiday_name = tr_holidays.get(date_obj.date())

    # 🟥 Resmi Tatil
    if holiday_name:
        intervals = [
            ("09:00", "18:00", 14, holiday_name or "Resmi Tatil")
        ]
        print(f"🎉 Bugün {holiday_name}! Güzel bir gün olsun 🌸")

    # 🟣 Sprint Planning
    elif is_planning_day:
        intervals = [
            ("09:00", "18:00", DEFAULT_DATA["activity"],
            "Sprint Review + Sprint Planlama + Retrospective")
        ]

    # 🟡 Leave
    elif is_leave_day:
        intervals = [
            ("09:00", "18:00", 12, "İzinli")
        ]
        print(f"İznin sisteme işlendi. Umarım dinlenebilmişsindir. 🌸")
    # 🟢 Normal
    else:
        desc_map = ask_descriptions(date_obj)
        intervals = [
            ("09:00", "12:00", DEFAULT_DATA["activity"], desc_map[("09:00", "12:00")]),
            ("12:00", "13:00", 30, ""),
            ("13:00", "18:00", DEFAULT_DATA["activity"], desc_map[("13:00", "18:00")]),
        ]

    # POST
    for start, end, activity, description in intervals:
        # ✅ Bugün ve 13-18 aralığıysa ekle
        if date_obj.date() == TODAY and start == "13:00" and end == "18:00":
            description += ", Kimai Zaman Girişi"

        if is_office_day:
            tags = "@ofis, "
        else:
            tags = DEFAULT_DATA["tags"]

        payload = {
            "timesheet_edit_form[begin]": f"{date_str} {start}",
            "timesheet_edit_form[end]": f"{date_str} {end}",
            "timesheet_edit_form[duration]": "",
            "timesheet_edit_form[customer]": DEFAULT_DATA["customer"],
            "timesheet_edit_form[project]": DEFAULT_DATA["project"],
            "timesheet_edit_form[activity]": activity,
            "timesheet_edit_form[description]": description,
            "timesheet_edit_form[tags]": tags,
            "timesheet_edit_form[_token]": token
        }

        print(f'{payload["timesheet_edit_form[begin]"]} + {payload["timesheet_edit_form[end]"]} zaman dilimi oluşturuldu!')
        r = requests.post(
                KIMAI_URL,
                headers=HEADERS,
                cookies=COOKIES,
                data=payload
            )

        responses.append((payload["timesheet_edit_form[begin]"], payload["timesheet_edit_form[end]"]))

    return responses

# ============================
# MONTH
# ============================
def create_timesheets_for_current_month(token, sprint_planning_days, leave_days, office_days, start_day):
    today = datetime.now()
    year = today.year
    month = today.month

    num_days = calendar.monthrange(year, month)[1]

    print(f"\n📆 İşlenen ay: {year}-{month:02d}")

    for day in range(start_day, num_days + 1):
        date_obj = datetime(year, month, day)

        # hafta içi
        if date_obj.weekday() <= 4:
            print(f"\n📅 {date_obj.strftime('%Y-%m-%d')}")
            create_timesheet_for_day(date_obj, token, sprint_planning_days, leave_days, office_days)

    print("\n✅ Helal olsun bir ayı daha tamamladın!")
    
    if month == 12:
        print("\n🎉 Yeni yılın şimdiden kutlu olsun! Sağlık, huzur ve bol commit’li bir yıl 🎄")

# ============================
# MAIN
# ============================
if __name__ == "__main__":
    start_day = ask_start_day()

    token = ask_token()
    phpsessionid = ask_sessionid()
    COOKIES["PHPSESSID"] = phpsessionid

    sprint_planning_days = ask_sprint_planning_days()
    leave_days = ask_leave_days()
    office_days = ask_office_days()
    create_timesheets_for_current_month(token, sprint_planning_days, leave_days, office_days, start_day)
