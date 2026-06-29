import sys
import time
import requests
from datetime import datetime
import calendar
import holidays

# ============================
# CONFIG
# ============================
KIMAI_URL = "https://kimai-new.finartz.dev/tr/timesheet/create"
PHPSESSID = "will be overrided"
MAX_ERROR_COUNT = 3

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

tr_holidays = holidays.Turkey(years=datetime.now().year)

# ============================
# ERROR HANDLING
# ============================
def handle_auth_error(payload, r):
    print(
        f"\n❌ {payload['timesheet_edit_form[begin]']} - "
        f"{payload['timesheet_edit_form[end]']} zaman dilimi eklenemedi! "
        f"(HTTP {r.status_code} - {r.text})"
    )

    print("\nNe yapmak istersin?")
    print("1️⃣  Programı sonlandır")
    print("2️⃣  Token ve Session ID yenile")

    choice = input("Seçim (1/2): ").strip()

    if choice == "1":
        print("⛔ Program 3 saniye içinde kapatılıyor...")
        time.sleep(3)
        return "EXIT", None

    elif choice == "2":
        print("\n🔄 Token ve Session ID yenileniyor...")
        new_token = ask_token()
        new_session = ask_sessionid()
        COOKIES["PHPSESSID"] = new_session
        return "REFRESH", new_token
    
    else: 
        print("\n⚠️ Geçersiz seçim yapıldı, program kapatılıyor...")
        time.sleep(3)
        return "EXIT", None


# ============================
# INPUTS
# ============================
def ask_token():
    return input("🔑 Kimai _token gir: ").strip()

def ask_sessionid():
    return input("🔑 Kimai php session id gir: ").strip()

def ask_sprint_planning_days():
    raw = input(
        "📌 Sprint planlama günlerin (ayın kaçında? örn: 1,3 | boş = yok): "
    )
    if not raw:
        return set()
    
    return {int(x.strip()) for x in raw.split(",")}

def ask_leave_days():
    raw = input(
        "📌 İzinli günlerin (ayın kaçında? örn: 1,3 | boş = yok): "
    )
    if not raw:
        return set()
    return {int(x.strip()) for x in raw.split(",")}

def ask_office_days():
    raw = input(
        "📌 Ofis günlerin (ayın kaçında? örn: 1,3 | boş = yok): "
    )
    if not raw:
        return set()
    return {int(x.strip()) for x in raw.split(",")}

def ask_start_month():
    raw = input("▶️ Zaman girişi kaçıncı ay için başlasın? (boş = bulunduğun ay): ").strip()
    current_month = datetime.now().month
    return int(raw) if raw else current_month

def ask_activity():
    # ✅ Geliştirme: Seçilen aktivite id'sini döner, boşsa DEFAULT_DATA'daki aktiviteyi kullanır.
    raw = input("▶️ Tüm ay geçerli olacak aktiviteyi seçin? (Geliştirme = 1, Test = 2, Teknik Analiz = 22, Eğitim = 5 | Boş = Varsayılan): ").strip()
    return int(raw) if raw else DEFAULT_DATA["activity"]

def confirm_description(description):
    # ✅ Geliştirme: Kullanıcıya girilen açıklamayı onaylatır.
    print(f"\n📝 Girilen Genel Açıklama: \"{description}\"")
    choice = input("👉 Bu açıklamayı onaylıyor musunuz? (E/H): ").strip().upper()
    return choice == 'E'

def ask_general_description():
    # ✅ Geliştirme: Genel açıklama alır ve onay mekanizmasını tetikler.
    while True:
        raw = input("▶️ Tüm ay geçerli olacak açıklama metnini giriniz? (Boş ise her gün için ayrı sorulacak): ").strip()
        if not raw:
            return None
        
        if confirm_description(raw):
            return raw
        else:
            print("🔄 Açıklama reddedildi. Lütfen tekrar girin veya boş bırakın.\n")

def ask_start_day():
    raw = input("▶️ Zaman girişi kaçıncı günden başlansın? (boş = ay başı): ").strip()
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
def create_timesheet_for_day(date_obj, token, sprint_planning_days, leave_days, office_days, activity_id, general_desc):
    date_str = date_obj.strftime("%Y-%m-%d")

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
            ("09:00", "18:00", 7, "Sprint Review + Sprint Planlama + Retrospective")
        ]

    # 🟡 Leave
    elif is_leave_day:
        intervals = [
            ("09:00", "18:00", 12, "İzinli")
        ]
        print(f"İznin sisteme işlendi. Umarım dinlenebilmişsindir. 🌸")
    
    # 🟢 Normal
    else:
        # ✅ Geliştirme: Eğer genel açıklama varsa sormadan kullan, yoksa tek tek sor.
        if general_desc:
            desc_map = {
                ("09:00", "12:00"): f"Daily Toplantısı, {general_desc}",
                ("13:00", "18:00"): general_desc
            }
        else:
            desc_map = ask_descriptions(date_obj)

        intervals = [
            ("09:00", "12:00", activity_id, desc_map[("09:00", "12:00")]),
            ("12:00", "13:00", 30, ""),
            ("13:00", "18:00", activity_id, desc_map[("13:00", "18:00")]),
        ]

    error_count = 0
    # POST
    for start, end, act, description in intervals:
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
            "timesheet_edit_form[activity]": act,
            "timesheet_edit_form[description]": description,
            "timesheet_edit_form[tags]": tags,
            "timesheet_edit_form[_token]": token
        }

        success = False
        while not success:
            r = requests.post(
                KIMAI_URL,
                headers=HEADERS,
                cookies=COOKIES,
                data=payload
            )

            if r.status_code == 200:
                success = True
                error_count = 0  # ✅ başarı → hata sayacı reset
                print(f'{payload["timesheet_edit_form[begin]"]} + {payload["timesheet_edit_form[end]"]} zaman dilimi oluşturuldu!')
                break

            error_count += 1

            # 3 hata olduysa otomatik çık
            if error_count >= MAX_ERROR_COUNT:
                print("\n⛔ Üst üste çok fazla hata alındı.")
                print("⏳ Program 3 saniye içinde sonlandırılacak...")
                return "EXIT"

            action, new_token = handle_auth_error(payload, r)

            if action == "REFRESH":
                payload["timesheet_edit_form[_token]"] = new_token
                continue  # 🔁 yeni token ve session id ile isteği yeniden dene

            elif action == "EXIT":
                return action  # sadece fonksiyondan çık

    return "OK"

# ============================
# MONTH
# ============================
def create_timesheets_for_month(token, sprint_planning_days, leave_days, office_days, start_day, start_month, activity_id, general_desc):
    if start_month:
        selected_month_first_day = datetime(datetime.now().year, start_month, 1)
        month = selected_month_first_day.month
        year = selected_month_first_day.year    
    else:
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
            result = create_timesheet_for_day(date_obj, token, sprint_planning_days, leave_days, office_days, activity_id, general_desc)

            if result == "EXIT": return

    print("\n✅ Helal olsun bir ayı daha tamamladın!")
    
    if month == 12:
        print("\n🎉 Yeni yılın şimdiden kutlu olsun! Sağlık, huzur ve bol commit’li bir yıl 🎄")

# ============================
# MAIN
# ============================
if __name__ == "__main__":
    try:
        print("🚀 Kimai Zaman Girişi Scripti Başladı!\n")
        
        start_month = ask_start_month()
        start_day = ask_start_day()
        activity_id = ask_activity()
        general_desc = ask_general_description() # ✅ Geliştirme

        token = ask_token()
        phpsessionid = ask_sessionid()
        COOKIES["PHPSESSID"] = phpsessionid

        sprint_planning_days = ask_sprint_planning_days()
        leave_days = ask_leave_days()
        office_days = ask_office_days()
        
        create_timesheets_for_month(
            token, sprint_planning_days, leave_days, office_days, 
            start_day, start_month, activity_id, general_desc
        )

    except KeyboardInterrupt:
        sys.exit(0)