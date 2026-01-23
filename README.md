# ⏱️ Kimai Timesheet CLI

Kimai kullananlar için aylık timesheet girişlerini otomatikleştiren interaktif bir CLI aracı.

-  Python ile çalıştır
-  EXE olarak indir–çalıştır
-  Sprint planning, izin, resmi tatil destekli
-  Ofis / ev günü etiketleme
- Günlük açıklamaları interaktif sorar

# 🚀 Hızlı Başlangıç (EXE)

Python kurulu değil mi? Hiç sorun değil.

dist/ klasörüne git

KimaiZamanGirisi.exe dosyasını çalıştır

Terminalde sorulan bilgileri gir


# 🐍 Python ile Çalıştırmak İsteyenler
1. Repoyu klonla
2. Bağımlılıkları kur
pip install -r requirements.txt
3. Script’i çalıştır
python src/kimai_script_with_desc.py

# 🧠 Script Ne Yapar?

Script, içinde bulunulan ay için hafta içi günleri dolaşır ve her gün için uygun timesheet kayıtlarını Kimai’ye gönderir.

# Otomatik yönetilen senaryolar

## 🟥 Resmi tatiller (Türkiye)

Gün boyu tek kayıt açılır. Aktivite otomatik olarak Resmi Tatil olur

## 🟣 Sprint Planning günleri

Kullanıcıdan girilen günler (ayın kaçında olduğu)

Gün boyu tek kayıt: Sprint Review + Sprint Planlama + Retrospective

## 🟡 İzin günleri

Gün boyu tek kayıt

Aktivite: İzinli

## 🟢 Normal çalışma günleri

09:00–12:00 → açıklama sorulur

Otomatik olarak “Daily Toplantısı, …” ile başlar

12:00–13:00 → öğle arası (aktivite id: 30)

13:00–18:00 → açıklama sorulur

## 🏢 Ofis / Ev Günleri

Script çalışırken ayrıca ofis günleri sorulur.

Ofis günü olan tarihler için @ofis tag’i kullanılır

Diğer günlerde Varsayılan tag (@ev) kullanılır

Bu sayede Kimai tarafında:

ofis / remote filtrelemesi

raporlama
çok daha kolay olur.

## 🧾 Bugün İçin Özel Davranış

Eğer script bugün çalıştırılıyorsa:

13:00–18:00 kaydının açıklamasına otomatik olarak
“, Kimai Zaman Girişi” eklenir

Bu, manuel girilen günlerle karışmaması için bilinçli bir tercihtir.

# 🔐 Script Çalışırken Sorulan Bilgiler

Script çalışırken interaktif olarak şunları ister:

▶️ Ayın kaçıncı gününden başlansın

🔑 Kimai _token

🔑 PHPSESSID

📌 Sprint planning günleri (ayın kaçında? örn: 3,17)

📌 İzin günleri (örn: 8,22)

📌 Ofis günleri (örn: 1,5,12)

Hiçbiri repoya hardcoded değildir
Token ve session sadece runtime’da kullanılır 👍

## Token ve Session Bilgisi

Bu script **token ve session bilgilerini kalıcı olarak saklamaz**.  
Tüm bilgiler **sadece runtime sırasında** kullanıcıdan alınır.

### `_token` Nasıl Alınır?
1. Kimai arayüzünü aç
2. Yeni bir timesheet oluştur (Create)
3. Tarayıcı DevTools → Network sekmesi
4. Create request’ini aç
5. Request **payload** içindeki `_token` değerini kopyala

### `PHPSESSID` Nasıl Alınır?
1. Aynı request’te
2. **Request Headers → Cookie**
3. `PHPSESSID=...` değerini kopyala

Script çalışırken bu değerler terminal üzerinden sorulur ve **sadece o çalıştırma için kullanılır**.

🔐 Güvenlik nedeniyle hiçbir bilgi dosyaya yazılmaz.

# ⚠️ Önemli Notlar

Script hafta sonları için kayıt açmaz. Mesai yaparsanız zaman girişlerini manual girmeniz gerekecek.
Öğle arası (12:00–13:00) açıklamasızdır.
Ay bazlı çalışır (geçmiş / gelecek ay seçimi yoktur).
Türkiye resmi tatilleri holidays kütüphanesiyle otomatik alınır.

Her gün tamamlandıktan sonra kimai anasayfası güncellenip her kaydın başarılı şekilde oluştuğunu görüp diğer günlere devam edilmesi önerilir. 

# 🛠️ EXE Build Etmek (Geliştiriciler İçin)
pip install pyinstaller
pyinstaller --onefile --console src/kimai_script_with_desc.py

Oluşan dosya:

dist/kimai-timesheet-cli.exe

# 🤝 Katkı

PR, issue ve önerilere tamamen açık 🙌
Token ve PHPSESSIONID'yı kullanıcı adı ve parolası ile dinamik şekilde alabilecek bir geliştirme yapılabilir.
Script özellikle kişisel akışlara göre kolayca özelleştirilebilir.