import json
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError

COOKIES_FILE = "cookies-dms.txt"

URL_VALIDASI = "https://peremajaan-siasn.bkn.go.id/validasiUsulan"
URL_PROFILE = "https://peremajaan-siasn.bkn.go.id/viewProfile"


def safe_action(action, desc=""):
    """Jalankan aksi dengan penanganan error ringan."""
    try:
        action()
    except TimeoutError:
        print(f"⏱ Timeout saat {desc}")
    except Exception as e:
        print(f"⚠️ Gagal {desc}: {e}")


def load_cookies(context):
    if not Path(COOKIES_FILE).exists():
        print("🚫 cookies-dms.txt tidak ditemukan. Jalankan ambil-token.py dulu.")
        exit(1)

    try:
        cookies = json.loads(Path(COOKIES_FILE).read_text())
        context.add_cookies(cookies)
        print(f"🍪 {len(cookies)} cookies dimuat dari {COOKIES_FILE}")
    except Exception as e:
        print(f"⚠️ Gagal load cookies: {e}")
        exit(1)


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=100, args=["--start-maximized"])
        context = browser.new_context()

        load_cookies(context)

        page_validasi = None
        page_profile = None

        print("💡 Tekan:")
        print("   1️⃣ → Buka tab Validasi Usulan")
        print("   2️⃣ → Buka tab View Profile")
        print("   q️⃣ → Keluar\n")

        while True:
            cmd = input("➡️  Input perintah: ").strip().lower()

            if cmd == "1":
                if not page_validasi or page_validasi.is_closed():
                    page_validasi = context.new_page()
                safe_action(lambda: page_validasi.goto(URL_VALIDASI, wait_until="domcontentloaded"),
                            "buka halaman Validasi Usulan")
                print("✅ Halaman Validasi Usulan dibuka")

            elif cmd == "2":
                if not page_profile or page_profile.is_closed():
                    page_profile = context.new_page()
                safe_action(lambda: page_profile.goto(URL_PROFILE, wait_until="domcontentloaded"),
                            "buka halaman View Profile")
                print("✅ Halaman View Profile dibuka")

            elif cmd == "q":
                print("👋 Keluar...")
                break

            else:
                print("❓ Perintah tidak dikenali (gunakan 1 / 2 / q)")

        browser.close()


if __name__ == "__main__":
    main()
