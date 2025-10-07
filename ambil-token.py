from playwright.sync_api import sync_playwright
import json
import time

# === KONFIGURASI ===
URL = "https://dms-siasn.bkn.go.id/"
USERNAME = "199402242018011001"
PASSWORD = "199402242018011001Aa!"
COOKIE_FILE = "cookies-dms.txt"

def safe_click(page, selector, desc="element"):
    """Coba klik elemen jika ada"""
    try:
        if page.locator(selector).is_visible():
            page.click(selector)
            print(f"✅ Klik {desc}")
            return True
        else:
            print(f"⚠️ {desc} tidak terlihat.")
            return False
    except Exception:
        print(f"⚠️ {desc} tidak ditemukan.")
        return False

def safe_fill(page, selector, text, desc="field"):
    """Coba isi field jika ada"""
    try:
        if page.locator(selector).is_visible():
            page.fill(selector, text)
            print(f"✅ Isi {desc}")
            return True
        else:
            print(f"⚠️ {desc} tidak terlihat.")
            return False
    except Exception:
        print(f"⚠️ {desc} tidak ditemukan.")
        return False

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=100)
    context = browser.new_context()
    page = context.new_page()

    print(f"🌐 Membuka {URL} ...")
    page.goto(URL, wait_until="networkidle")

    # === LOGIN ===
    print("🔐 Mencoba login otomatis...")

    safe_click(page, 'button:has-text("Login")', "tombol Login")
    time.sleep(2)

    safe_fill(page, '#username', USERNAME, "username")
    safe_fill(page, '#password', PASSWORD, "password")

    safe_click(page, 'input[value="Sign In"]', "tombol Sign In")

    print("📲 Masukkan OTP secara manual di halaman browser.")
    input("Tekan ENTER di sini jika login sudah berhasil... ")

    # === SIMPAN COOKIE ===
    cookies = context.cookies()
    with open(COOKIE_FILE, "w", encoding="utf-8") as f:
        json.dump(cookies, f, indent=2, ensure_ascii=False)

    print(f"✅ Semua cookie disimpan ke '{COOKIE_FILE}' ({len(cookies)} cookies).")

    print("🧭 Browser dibiarkan terbuka untuk inspeksi manual.")
    input("Tekan ENTER untuk menutup browser...")
    browser.close()
