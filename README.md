# 🛡️ Güçlü Şifre Oluşturucu (Python Tkinter)

Bu proje, Python ve Tkinter kütüphanesi kullanılarak geliştirilmiş, kullanıcı dostu bir arayüze (GUI) sahip rastgele ve güvenli şifre oluşturma uygulamasıdır.

## 🚀 Açıklama

Uygulamanın amacı, kullanıcıların belirlediği kriterlere (uzunluk, karakter tipi vb.) göre kriptografik olarak güvenli (`secrets` modülü ile) şifreler üretmek ve bu şifreleri tek tıkla panoya kopyalamaktır.

## ✨ Temel Özellikler

* **Ayarlanabilir Uzunluk:** 6 - 64 karakter arası şifre uzunluğu belirleme.
* **Karakter Tipi Seçimi:**
    * Büyük Harf (A-Z)
    * Küçük Harf (a-z)
    * Rakam (0-9)
    * Sembol (!@#$%)
* **Benzer Karakterleri Atlama:** `l, 1, I, O, 0` gibi karışabilecek karakterleri şifreye dahil etmeme seçeneği.
* **Güvenli Üretim:** Şifreler, Python'un `secrets` modülü ile üretilir.
* **Şifre Güç Göstergesi:** Üretilen şifrenin gücünü (Zayıf, Orta, Güçlü) renkli bir ilerleme çubuğu ile gösterir.
* **Tek Tıkla Kopyalama:** Üretilen şifreyi `pyperclip` kütüphanesi ile sistem panosuna kopyalar.
* **Şifre Gizleme/Gösterme:** "Göz" butonu ile şifre görünürlüğü açılıp kapatılabilir.
* **Kayıt Özelliği:** Üretilen şifreleri (isteğe bağlı olarak) tarih bilgisiyle birlikte yerel bir `kayitli_sifreler.json` dosyasına kaydeder.

## ⚙️ Gereksinimler

Programın panoya kopyalama özelliği için `pyperclip` kütüphanesine ihtiyacı vardır.

```bash
pip install pyperclip
