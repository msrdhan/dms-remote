import pandas as pd
import time
from playwright.sync_api import sync_playwright, TimeoutError

# === BACA INPUT ===
df_input = pd.read_excel("input.xlsx")
results = []

# === KONFIGURASI PLAYWRIGHT ===
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=100)  # GUI + slow motion
    context = browser.new_context()  # cross-platform user profile kosong
    page = context.new_page()
    page.goto("https://dms-siasn.bkn.go.id/", wait_until="networkidle")
    print("🌐 Halaman DMS SIASN dibuka.")

    # === LOGIN OTOMATIS ===
    try:
        print("🔐 Melakukan login otomatis...")

        # Klik tombol "Login"
        page.click('button:has-text("Login")', timeout=5000)
        time.sleep(2)

        # Isi username dan password
        page.fill("#username", "199402242018011001")
        page.fill("#password", "199402242018011001Aa!")

        # Klik tombol login
        page.click("#kc-login")

        print("📲 Silakan masukkan OTP di halaman dan tekan ENTER jika sudah login.")
        input("Tekan ENTER setelah OTP dimasukkan dan login selesai...")

    except Exception as e:
        print(f"❌ Gagal login: {e}")
        browser.close()
        exit(1)

    # === LOOP PER NIP ===
    try:
        index = 0
        while index < len(df_input):
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
                    # Coba "Lanjut Verifikasi" dulu
                    try:
                        verif_btn = page.locator('button[data="Lanjut Verifikasi"]')
                        if not verif_btn.is_visible():
                            raise Exception
                    except:
                        verif_btn = page.locator('button[data="Verifikasi"]')

                    verif_btn.click()
                    time.sleep(2)

                    # Ambil nama
                    try:
                        nama_elem = page.locator('//div[contains(text(), "Nama")]/following-sibling::div')
                        nama = nama_elem.inner_text(timeout=3000).strip()
                    except TimeoutError:
                        nama = "Nama tidak ditemukan"

                except Exception:
                    print("⚠️ Tombol Verifikasi tidak ditemukan.")
                    nama = "Tombol Verifikasi tidak ditemukan"

            except Exception as e:
                print(f"❌ Error saat proses NIP {nip}: {e}")
                nama = "Error saat proses"

            # Simpan hasil sementara
            results.append({"nip": nip, "nama": nama})

            # === INTERAKSI MANUAL ===
            while True:
                action = input("➡️ Ketik [n]ext, [b]ack, [r]eload, [exit], angka (go to row), atau ENTER untuk next: ").strip().lower()

                if action == "" or action == "n":
                    index += 1
                    break
                elif action == "b":
                    if index > 0:
                        index -= 1
                        print("⏪ Mundur ke NIP sebelumnya...")
                        results.pop()
                    else:
                        print("🚫 Sudah di awal data.")
                    break
                elif action == "r":
                    print("🔄 Me-reload halaman...")
                    page.reload(wait_until="networkidle")
                    time.sleep(5)
                    break
                elif action == "exit":
                    print("🚪 Keluar dari loop atas permintaan pengguna.")
                    raise KeyboardInterrupt
                elif action.isdigit():
                    target = int(action)
                    if 1 <= target <= len(df_input):
                        index = target - 1
                        print(f"🔁 Lompat ke baris ke-{target} (index: {index})")
                        break
                    else:
                        print(f"🚫 Baris {target} tidak valid. Harus antara 1 - {len(df_input)}")
                else:
                    print("❌ Input tidak dikenali.")

    except KeyboardInterrupt:
        print("\n⛔ Proses dihentikan oleh pengguna.")

    finally:
        df_output = pd.DataFrame(results)
        df_output.to_excel("report.xlsx", index=False)
        print("✅ Selesai. Data disimpan di 'report.xlsx'")
        print("🧭 Browser dibiarkan terbuka untuk inspeksi manual.")
        input("Tekan ENTER untuk menutup browser...")
        browser.close()
