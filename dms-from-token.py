import json
import pandas as pd
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

COOKIES_FILE = "cookies-dms.txt"

# === BACA INPUT ===
df_input = pd.read_excel("input.xlsx")
results = []

def load_cookies(context, cookies_path):
    """Load cookies dari file JSON ke context Playwright."""
    cookies = json.loads(Path(cookies_path).read_text())
    context.add_cookies(cookies)
    print(f"🍪 {len(cookies)} cookies dimuat dari {cookies_path}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=100, args=["--start-maximized"])
    context = browser.new_context(no_viewport=True)

    # === LOAD COOKIES DARI FILE ===
    if Path(COOKIES_FILE).exists():
        load_cookies(context, COOKIES_FILE)
    else:
        print(f"❌ File cookies {COOKIES_FILE} tidak ditemukan. Jalankan ambil-token-login dulu.")
        browser.close()
        exit(1)

    page = context.new_page()
    page.goto("https://dms-siasn.bkn.go.id/", wait_until="networkidle")
    print("🌐 Halaman DMS SIASN dibuka pakai cookies (tanpa login).")

    # === CEK APAKAH LOGIN MASIH VALID ===
    if "Login" in page.content():
        print("⚠️ Cookies expired atau sesi tidak valid. Harus login ulang.")
        browser.close()
        exit(1)
    else:
        print("✅ Login valid. Mulai proses data.")

    # === LOOP PER NIP ===
    try:
        index = 0
        while index < len(df_input):
            page = context.new_page()
            page.bring_to_front()
            page.goto("https://dms-siasn.bkn.go.id/", wait_until="networkidle")
            nip = str(df_input.iloc[index]["nip"]).strip()
            print(f"\n🔍 Memproses NIP [baris {index + 1}]: {nip}")

            nama = "Error saat proses"
            try:
                # Isi NIP
                page.fill('input[placeholder="Masukan Nomor Induk Pegawai"]', nip)
                time.sleep(1)

                # Klik tombol "Load Data"
                page.click('button:has-text("Load Data")')
                page.wait_for_load_state("networkidle")
                time.sleep(2)

                # Klik tombol verifikasi
                try:
                    verif_btn = page.locator('button[data="Lanjut Verifikasi"]')
                    if not verif_btn.is_visible():
                        verif_btn = page.locator('button[data="Verifikasi"]')
                    verif_btn.click()
                    time.sleep(2)

                    # Ambil nama ASN
                    try:
                        nama_elem = page.locator('//div[contains(text(), "Nama")]/following-sibling::div')
                        nama = nama_elem.inner_text(timeout=3000).strip()
                    except:
                        nama = "Nama tidak ditemukan"

                except:
                    print("⚠️ Tombol Verifikasi tidak ditemukan.")
                    nama = "Tombol Verifikasi tidak ditemukan"

            except Exception as e:
                print(f"❌ Error saat proses NIP {nip}: {e}")
                nama = "Error saat proses"

            results.append({"nip": nip, "nama": nama})

            # Interaksi manual
            while True:
                action = input("➡️ Ketik [n]ext, [b]ack, [r]eload, [exit], angka (go to row), atau ENTER untuk next: ").strip().lower()
                if action == "" or action == "n":
                    index += 1
                    break
                elif action == "b":
                    if index > 0:
                        index -= 1
                        results.pop()
                    break
                elif action == "r":
                    print("🔄 Reload halaman...")
                    page.reload(wait_until="networkidle")
                    time.sleep(5)
                    break
                elif action == "exit":
                    raise KeyboardInterrupt
                elif action.isdigit():
                    target = int(action)
                    if 1 <= target <= len(df_input):
                        index = target - 1
                        break
                    else:
                        print(f"🚫 Baris {target} tidak valid.")
                else:
                    print("❌ Input tidak dikenali.")

    except KeyboardInterrupt:
        print("\n⛔ Dihentikan pengguna.")
    finally:
        pd.DataFrame(results).to_excel("report.xlsx", index=False)
        print("✅ Selesai. Hasil disimpan di 'report.xlsx'.")
        input("Tekan ENTER untuk menutup browser...")
        browser.close()
