"""
Güçlü Şifre Oluşturucu GUI Programı

Bu program, Tkinter arayüzü kullanarak kullanıcının belirlediği kriterlere göre
güvenli (secrets modülü ile) rastgele şifreler oluşturur.

Özellikler:
- Ayarlanabilir uzunluk (6-64 karakter)
- Karakter tipi seçimi (Büyük/Küçük harf, Rakam, Sembol)
- Benzer karakterleri (l, 1, I, O, 0) atlama seçeneği
- Şifre güç göstergesi (zayıf/orta/güçlü) ve ilerleme çubuğu
- Tek tıkla panoya kopyalama (pyperclip)
- Şifre görünürlüğünü aç/kapa (göz butonu)
- Oluşturulan şifreyi JSON dosyasına kaydetme

macOS DÜZELTMESİ:
- Progressbar stil adları, TclError hatasını önlemek için '.Horizontal.TProgressbar'
  olarak güncellendi.
"""

import tkinter as tk
from tkinter import ttk  # Daha modern widget'lar için
from tkinter import messagebox
import secrets
import string
import json
import os
from datetime import datetime

# Panoya kopyalama kütüphanesini kontrol et
try:
    import pyperclip
    PYPERCLIP_AVAILABLE = True
except ImportError:
    PYPERCLIP_AVAILABLE = False
    print("UYARI: 'pyperclip' modülü bulunamadı. Panoya kopyalama özelliği çalışmayacak.")
    print("Kurulum için: pip install pyperclip")

# --- Sabitler ---
SIMILAR_CHARS = {'l', '1', 'I', 'O', '0'}
SAVE_FILE = "kayitli_sifreler.json"


# --- Çekirdek Fonksiyonlar ---

def generate_password(length, use_upper, use_lower, use_digits, use_symbols, exclude_similar):
    """
    Belirlenen kriterlere göre güvenli bir şifre oluşturur.
    """
    
    # Karakter havuzlarını oluştur
    upper = string.ascii_uppercase
    lower = string.ascii_lowercase
    digits = string.digits
    symbols = string.punctuation

    # Benzer karakterleri atla seçiliyse havuzları filtrele
    if exclude_similar:
        upper = ''.join(c for c in upper if c not in SIMILAR_CHARS)
        lower = ''.join(c for c in lower if c not in SIMILAR_CHARS)
        digits = ''.join(c for c in digits if c not in SIMILAR_CHARS)
        symbols = ''.join(c for c in symbols if c not in SIMILAR_CHARS)

    # Seçilen kriterlere göre ana karakter havuzunu ve zorunlu karakterleri belirle
    char_pool = ""
    guaranteed_chars = []

    if use_upper:
        if not upper:  # 'I' ve 'O' çıkarılınca havuz boş kalabilir (teorik)
            messagebox.showwarning("Uyarı", "Benzer karakterler atlanınca büyük harf kalmadı.")
        else:
            char_pool += upper
            guaranteed_chars.append(secrets.choice(upper))

    if use_lower:
        if not lower: # 'l' ve 'o'
            messagebox.showwarning("Uyarı", "Benzer karakterler atlanınca küçük harf kalmadı.")
        else:
            char_pool += lower
            guaranteed_chars.append(secrets.choice(lower))

    if use_digits:
        if not digits: # '1' ve '0'
            messagebox.showwarning("Uyarı", "Benzer karakterler atlanınca rakam kalmadı.")
        else:
            char_pool += digits
            guaranteed_chars.append(secrets.choice(digits))

    if use_symbols:
        char_pool += symbols
        guaranteed_chars.append(secrets.choice(symbols))

    # Eğer hiçbir karakter tipi seçilmemişse
    if not char_pool:
        return None  # Hata durumu

    # Kalan karakterleri ana havuzdan rastgele seç
    remaining_length = length - len(guaranteed_chars)
    
    # Kalan uzunluk negatifse (çok fazla kısıtlama, kısa uzunluk), sadece zorunlu karakterleri karıştır
    if remaining_length < 0:
        password_chars = guaranteed_chars[:length]
    else:
        password_chars = guaranteed_chars + [secrets.choice(char_pool) for _ in range(remaining_length)]

    # Şifrenin son halini güvenli bir şekilde karıştır
    secrets.SystemRandom().shuffle(password_chars)

    return "".join(password_chars)


def calculate_strength(password, length, has_upper, has_lower, has_digits, has_symbols):
    """
    Şifrenin gücünü basit bir skor ve etiket ile hesaplar.
    """
    # DÜZELTME: Varsayılan stil adı, platform uyumluluğu için
    # TProgressbar'ın varsayılan adını (veya sadece yatay olanı) kullanır.
    default_style = "Horizontal.TProgressbar"
    
    if not password:
        return "...", 0, default_style
        
    score = 0
    
    # 1. Uzunluk Puanı (Maks 50 puan)
    if length < 8:
        score += length * 2
    elif length < 12:
        score += length * 3
    elif length < 16:
        score += length * 4
    else:
        score += length * 4  # 64'e kadar
    
    score = min(score, 50) # Uzunluktan max 50 puan
    
    # 2. Çeşitlilik Puanı (Maks 50 puan)
    types_count = sum([has_upper, has_lower, has_digits, has_symbols])
    
    if types_count == 1:
        score += 5   # Sadece rakam veya sadece harf
    elif types_count == 2:
        score += 15
    elif types_count == 3:
        score += 35
    elif types_count == 4:
        score += 50  # Tüm tipler mevcut
        
    # Toplam skoru 100'e sabitle
    score = min(score, 100)

    # Skora göre etiket ve renk belirle
    # DÜZELTME: Stil adlarına ".Horizontal" eklendi
    if score < 35:
        label = "Zayıf"
        style = "danger.Horizontal.TProgressbar"
    elif score < 65:
        label = "Orta"
        style = "warning.Horizontal.TProgressbar"
    elif score < 85:
        label = "Güçlü"
        style = "success.Horizontal.TProgressbar"
    else:
        label = "Çok Güçlü"
        style = "success.Horizontal.TProgressbar"
        
    return label, score, style


# --- Ana GUI Uygulama Sınıfı ---

class PasswordGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Güçlü Şifre Oluşturucu")
        self.root.geometry("450x550") # Pencere boyutunu biraz büyüttük
        self.root.resizable(False, False)

        # Stil tanımlamaları (Progressbar renkleri için)
        self.style = ttk.Style(self.root)
        # Stil (theme) seçimi, platforma göre daha iyi görünüm sağlar
        try:
            self.style.theme_use('clam') # 'clam', 'alt', 'default', 'vista', 'xpnative'
        except tk.TclError:
            pass # Bazı sistemlerde 'clam' olmayabilir

        # DÜZELTME: macOS hatasını önlemek için stil adlarına '.Horizontal' eklendi
        self.style.configure("danger.Horizontal.TProgressbar", background='#dc3545') # Kırmızı
        self.style.configure("warning.Horizontal.TProgressbar", background='#ffc107') # Sarı
        self.style.configure("success.Horizontal.TProgressbar", background='#28a745') # Yeşil

        # --- Değişkenler ---
        self.length_var = tk.IntVar(value=16)
        self.upper_var = tk.BooleanVar(value=True)
        self.lower_var = tk.BooleanVar(value=True)
        self.digits_var = tk.BooleanVar(value=True)
        self.symbols_var = tk.BooleanVar(value=True)
        self.exclude_var = tk.BooleanVar(value=False)
        
        self.password_var = tk.StringVar()
        self.strength_text_var = tk.StringVar(value="Güç: ...")
        self.feedback_var = tk.StringVar()

        # Ana çerçeve
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Widget'lar ---
        self.create_widgets(main_frame)

    def create_widgets(self, container):
        # Başlık
        title_label = ttk.Label(container, text="Güçlü Şifre Oluşturucu", 
                                font=("Helvetica", 16, "bold"))
        title_label.pack(pady=(0, 15))

        # --- Ayarlar Çerçevesi ---
        settings_frame = ttk.Labelframe(container, text="Kriterler", padding="10")
        settings_frame.pack(fill=tk.X, pady=5)

        # Uzunluk Kaydırıcısı
        len_frame = ttk.Frame(settings_frame)
        len_label = ttk.Label(len_frame, text="Şifre Uzunluğu:")
        self.len_value_label = ttk.Label(len_frame, text="16", width=3, anchor="e")
        len_slider = ttk.Scale(len_frame, from_=6, to=64,
                               variable=self.length_var, command=self.update_len_label,
                               orient=tk.HORIZONTAL)
        len_label.pack(side=tk.LEFT)
        len_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.len_value_label.pack(side=tk.LEFT)
        len_frame.pack(fill=tk.X, pady=5)

        # Onay Kutuları (Checkboxes)
        chk_upper = ttk.Checkbutton(settings_frame, text="Büyük Harf (A-Z)", variable=self.upper_var)
        chk_upper.pack(anchor=tk.W)
        
        chk_lower = ttk.Checkbutton(settings_frame, text="Küçük Harf (a-z)", variable=self.lower_var)
        chk_lower.pack(anchor=tk.W)
        
        chk_digits = ttk.Checkbutton(settings_frame, text="Rakam (0-9)", variable=self.digits_var)
        chk_digits.pack(anchor=tk.W)
        
        chk_symbols = ttk.Checkbutton(settings_frame, text="Sembol (!@#$%)", variable=self.symbols_var)
        chk_symbols.pack(anchor=tk.W)
        
        separator = ttk.Separator(settings_frame, orient='horizontal')
        separator.pack(fill='x', pady=10)

        chk_exclude = ttk.Checkbutton(settings_frame, 
                                      text="Benzer Karakterleri Atla (l, 1, I, O, 0)", 
                                      variable=self.exclude_var)
        chk_exclude.pack(anchor=tk.W)

        # --- Oluştur Butonu ---
        generate_btn = ttk.Button(container, text="Oluştur", 
                                  command=self.on_generate, style="Accent.TButton") # Windows 11 stili
        generate_btn.pack(fill=tk.X, pady=10)

        # --- Sonuç Çerçevesi ---
        result_frame = ttk.Labelframe(container, text="Oluşturulan Şifre", padding="10")
        result_frame.pack(fill=tk.X, pady=5)

        result_entry_frame = ttk.Frame(result_frame)
        
        self.password_entry = ttk.Entry(result_entry_frame, textvariable=self.password_var, 
                                        font=("Courier", 12), state="readonly", show="*")
        self.password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Göz butonu
        self.eye_btn = ttk.Button(result_entry_frame, text="👁", width=3, 
                                  command=self.toggle_visibility)
        self.eye_btn.pack(side=tk.LEFT, padx=(5, 0))
        result_entry_frame.pack(fill=tk.X, pady=(0, 5))

        # Kopyala ve Kaydet Butonları (Yan yana)
        button_frame = ttk.Frame(result_frame)
        self.copy_btn = ttk.Button(button_frame, text="Panoya Kopyala", command=self.on_copy)
        self.copy_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        self.save_btn = ttk.Button(button_frame, text="Kaydet", command=self.on_save)
        self.save_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        button_frame.pack(fill=tk.X, pady=5)
        
        # --- Güç Göstergesi ---
        strength_frame = ttk.Labelframe(container, text="Şifre Gücü", padding="10")
        strength_frame.pack(fill=tk.X, pady=5)
        
        self.strength_label = ttk.Label(strength_frame, textvariable=self.strength_text_var)
        self.strength_label.pack(anchor=tk.W)
        
        # DÜZELTME: Sorunlu 'style' parametresi kaldırıldı.
        # Artık stilini 'calculate_strength' fonksiyonundan dinamik olarak alacak.
        self.strength_bar = ttk.Progressbar(strength_frame, orient=tk.HORIZONTAL, 
                                            length=100, mode='determinate')
        self.strength_bar.pack(fill=tk.X, pady=5)
        
        # --- Geri Bildirim ve Güvenlik Notu ---
        self.feedback_label = ttk.Label(container, textvariable=self.feedback_var, 
                                        foreground="blue", anchor=tk.W)
        self.feedback_label.pack(fill=tk.X, pady=(10, 0))

        security_note = ttk.Label(container, 
                                  text="Güvenlik Notu: Şifreleriniz sadece yerel\n"
                                       "'kayitli_sifreler.json' dosyasına kaydedilir.",
                                  font=("Helvetica", 8, "italic"),
                                  foreground="gray")
        security_note.pack(pady=(10, 0), anchor=tk.S, side=tk.BOTTOM)


    # --- Olay Yöneticileri (Event Handlers) ---

    def update_len_label(self, value):
        """Kaydırıcı hareket ettikçe uzunluk etiketini günceller."""
        self.len_value_label.config(text=f"{int(float(value)):>2}")

    def on_generate(self):
        """'Oluştur' butonuna tıklandığında tetiklenir."""
        # Değerleri al
        length = self.length_var.get()
        use_upper = self.upper_var.get()
        use_lower = self.lower_var.get()
        use_digits = self.digits_var.get()
        use_symbols = self.symbols_var.get()
        exclude_similar = self.exclude_var.get()

        # Hiçbiri seçilmemişse uyar
        if not (use_upper or use_lower or use_digits or use_symbols):
            messagebox.showerror("Hata", "En az bir karakter tipi seçmelisiniz!")
            return
            
        # Şifreyi oluştur
        password = generate_password(length, use_upper, use_lower, 
                                     use_digits, use_symbols, exclude_similar)
        
        if password:
            self.password_var.set(password)
            self.clear_feedback()
            
            # Şifreyi göster (eğer gizliyse)
            self.password_entry.config(show="")
            self.eye_btn.config(text="🙈")

            # Entry widget'ını geçici olarak 'normal' yapıp seç
            self.password_entry.config(state="normal")
            self.password_entry.select_range(0, tk.END)
            self.password_entry.icursor(tk.END)
            self.password_entry.config(state="readonly")
            
            # Güç göstergesini güncelle
            self.update_strength_indicator(password, length, use_upper, 
                                           use_lower, use_digits, use_symbols)
        else:
            messagebox.showerror("Hata", "Geçerli kriterlerle şifre oluşturulamadı.")


    def on_copy(self):
        """'Panoya Kopyala' butonuna tıklandığında tetiklenir."""
        if not PYPERCLIP_AVAILABLE:
            self.show_feedback("Hata: 'pyperclip' modülü yüklü değil!", "red")
            return
            
        password = self.password_var.get()
        if password:
            try:
                pyperclip.copy(password)
                self.show_feedback("Panoya kopyalandı!", "green")
            except Exception as e:
                self.show_feedback(f"Kopyalama hatası: {e}", "red")
        else:
            self.show_feedback("Önce bir şifre oluşturun.", "orange")

    def on_save(self):
        """'Kaydet' butonuna tıklandığında tetiklenir."""
        password = self.password_var.get()
        if not password:
            self.show_feedback("Kaydedilecek bir şifre yok.", "orange")
            return

        # Kaydedilecek veri
        new_entry = {
            "tarih": datetime.now().isoformat(),
            "sifre": password
        }

        data = []
        # Mevcut dosyayı oku
        try:
            if os.path.exists(SAVE_FILE):
                with open(SAVE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if not isinstance(data, list): # Dosya bozuksa
                        data = []
        except json.JSONDecodeError:
            data = [] # Dosya bozuksa veya boşsa
        
        # Yeni veriyi ekle ve dosyaya yaz
        data.append(new_entry)
        
        try:
            with open(SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self.show_feedback(f"'{SAVE_FILE}' dosyasına kaydedildi.", "blue")
        except IOError as e:
            self.show_feedback(f"Dosya yazma hatası: {e}", "red")


    def toggle_visibility(self):
        """Şifrenin görünürlüğünü açar/kapatır."""
        if self.password_entry.cget('show') == '*':
            self.password_entry.config(show="")
            self.eye_btn.config(text="🙈") # Gizle
        else:
            self.password_entry.config(show="*")
            self.eye_btn.config(text="👁") # Göster
            
    def update_strength_indicator(self, password, length, use_upper, use_lower, use_digits, use_symbols):
        """Şifre gücü etiketini ve ilerleme çubuğunu günceller."""
        label, score, style = calculate_strength(password, length, use_upper, 
                                                 use_lower, use_digits, use_symbols)
        
        self.strength_text_var.set(f"Güç: {label} ({score}%)")
        self.strength_bar['value'] = score
        self.strength_bar.config(style=style)

    def show_feedback(self, message, color):
        """Kullanıcıya geri bildirim mesajı gösterir."""
        self.feedback_var.set(message)
        self.feedback_label.config(foreground=color)
        # 3 saniye sonra mesajı temizle
        self.root.after(3000, self.clear_feedback)

    def clear_feedback(self):
        """Geri bildirim mesajını temizler."""
        self.feedback_var.set("")


# --- Programı Başlat ---

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGeneratorApp(root)
    root.mainloop()