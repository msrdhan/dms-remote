import json
import time
import openpyxl
from pathlib import Path
from playwright.sync_api import sync_playwright

EXCEL_FILE = "data_pns_prioritas.xlsx"
URL_LOGIN = "https://dms-siasn.bkn.go.id/"
URL_PAGE = "https://dms-siasn.bkn.go.id/personal/pns_prioritas"
COOKIES_FILE = "cookies-dms.txt"


def load_cookies(context, cookies_path):
    try:
        cookies = json.loads(Path(cookies_path).read_text())
        context.add_cookies(cookies)
        print(f"🍪 {len(cookies)} cookies dimuat dari {cookies_path}")
    except Exception as e:
        print(f"[WARN] Tidak bisa memuat cookies: {e}")


def save_to_excel(headers, rows):
    try:
        file_exists = Path(EXCEL_FILE).exists()
        if file_exists:
            wb = openpyxl.load_workbook(EXCEL_FILE)
            ws = wb.active
        else:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.append(headers)

        for row in rows:
            ws.append(row)

        wb.save(EXCEL_FILE)
        print(f"[INFO] {len(rows)} baris disimpan ke {EXCEL_FILE}")
    except Exception as e:
        print(f"[ERROR] Gagal simpan ke Excel: {e}")


def extract_table(page):
    try:
        headers = page.locator("table thead th").all_inner_texts()
        rows_elements = page.locator("table tbody tr").all()
        rows = []

        for row_el in rows_elements:
            cells = row_el.locator("td").all_inner_texts()
            if any(cells):
                rows.append(cells)

        return headers, rows
    except Exception as e:
        print(f"[WARN] Gagal ambil tabel: {e}")
        return [], []


def mode_otomatis(page):
    print("[INFO] Mode otomatis dimulai...")
    while True:
        try:
            page.wait_for_load_state("networkidle", timeout=60000)
            headers, rows = extract_table(page)

            if not rows:
                print("[INFO] Tidak ada data lagi. Kembali ke menu utama.")
                break

            save_to_excel(headers, rows)

            next_btn = page.locator("button:has-text('Next')")
            if next_btn.is_disabled():
                print("[INFO] Tombol Next tidak aktif. Kembali ke menu.")
                break

            next_btn.click()
            page.wait_for_timeout(2000)

        except Exception as e:
            print(f"[WARN] Gagal di mode otomatis: {e}")
            break


def mode_manual(page):
    print("[INFO] Mode manual dimulai.")
    while True:
        command = input("Tekan ENTER untuk ambil halaman berikut / ketik 'b' untuk kembali / 'exit' untuk keluar: ").strip().lower()
        if command == "exit":
            print("[INFO] Keluar dari program.")
            exit(0)
        elif command == "b":
            print("[INFO] Kembali ke menu utama.")
            break

        try:
            headers, rows = extract_table(page)
            if not rows:
                print("[INFO] Tidak ada data di halaman ini.")
            else:
                save_to_excel(headers, rows)

            next_btn = page.locator("button:has-text('Next')")
            next_btn.click()
            page.wait_for_timeout(2000)
        except Exception as e:
            print(f"[WARN] Gagal di mode manual: {e}")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=100, args=["--start-maximized"])
        page = browser.new_page()

        try:
            load_cookies(page.context, COOKIES_FILE)
            print("[INFO] Membuka halaman data prioritas...")
            page.goto(URL_PAGE, timeout=60000)
            page.wait_for_load_state("networkidle", timeout=60000)

            headers, _ = extract_table(page)
            if headers:
                save_to_excel(headers, [])

            while True:
                mode = input("\nPilih mode (1 = auto, 2 = manual, exit = keluar): ").strip().lower()

                if mode == "1":
                    mode_otomatis(page)
                elif mode == "2":
                    mode_manual(page)
                elif mode == "exit":
                    print("[INFO] Program selesai.")
                    break
                else:
                    print("[WARN] Pilihan tidak dikenal.")

        except Exception as e:
            print(f"[ERROR] Exception utama: {e}")
        finally:
            print("[INFO] Menutup browser...")
            browser.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[INFO] Dihentikan oleh user.")
    except Exception as e:
        print(f"[FATAL] {e}")
