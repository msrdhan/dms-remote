import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time

# === BACA INPUT ===
df_input = pd.read_excel("input.xlsx")
results = []

# === KONFIGURASI SELENIUM ===


# brave_path = '/usr/bin/brave-browser'
# Ganti ini dengan path ke profil Brave yang kamu gunakan sekarang (harus aktif Vimium-nya)
# user_data_dir = r"C:\Users\<USERNAME>\AppData\Local\BraveSoftware\Brave-Browser\User Data"
# profile_dir = "Work"  # atau "Profile 1", tergantung profil aktif kamu

options = webdriver.ChromeOptions()
options.binary_location = brave_path
# options.add_argument(f"user-data-dir={user_data_dir}")
options.add_argument(f"profile-directory={profile_dir}")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

driver = webdriver.Chrome(options=options)
driver.get("https://dms-siasn.bkn.go.id/")

# === LOGIN OTOMATIS ===
try:
    print("🔐 Melakukan login otomatis...")

    # Klik tombol "Login"
    login_btn = driver.find_element(By.XPATH, '//button[contains(text(), "Login")]')
    login_btn.click()
    time.sleep(2)

    # Isi username dan password
    driver.find_element(By.ID, "username").send_keys("199402242018011001")
    driver.find_element(By.ID, "password").send_keys("199402242018011001Aa!")

    # Klik login (submit)
    driver.find_element(By.ID, "kc-login").click()

    print("📲 Silakan masukkan OTP di halaman dan tekan ENTER jika sudah.")
    input("Tekan ENTER setelah OTP dimasukkan dan login selesai...")

except Exception as e:
    print(f"❌ Gagal login: {e}")
    driver.quit()
    exit(1)

# === LOOP PER NIP ===
try:
    index = 0
    while index < len(df_input):
        nip = str(df_input.iloc[index]['nip']).strip()
        print(f"\n🔍 Memproses NIP [baris {index + 1}]: {nip}")

        try:
            # Masukkan NIP ke input field
            nip_input = driver.find_element(By.XPATH, '//input[@placeholder="Masukan Nomor Induk Pegawai"]')
            nip_input.clear()
            nip_input.send_keys(nip)
            time.sleep(1)

            # Klik tombol "Load Data"
            load_button = driver.find_element(By.XPATH, '//button[contains(text(), "Load Data")]')
            load_button.click()
            time.sleep(3)

            # Klik "Lanjut Verifikasi" atau "Verifikasi" jika ada
            try:
                try:
                    verif_btn = driver.find_element(By.XPATH, '//button[@data="Lanjut Verifikasi"]')
                except NoSuchElementException:
                    verif_btn = driver.find_element(By.XPATH, '//button[@data="Verifikasi"]')

                verif_btn.click()
                time.sleep(2)

                # Ambil nama jika tersedia
                try:
                    nama_elem = driver.find_element(By.XPATH, '//div[contains(text(), "Nama")]/following-sibling::div')
                    nama = nama_elem.text.strip()
                except NoSuchElementException:
                    nama = "Nama tidak ditemukan"

            except NoSuchElementException:
                print("⚠️ Tombol Verifikasi tidak ditemukan.")
                nama = "Tombol Verifikasi tidak ditemukan"

        except Exception as e:
            print(f"❌ Error saat proses NIP {nip}: {e}")
            nama = "Error saat proses"

        # Simpan hasil sementara
        results.append({"nip": nip, "nama": nama})

        # === TUNGGU INPUT USER ===
        while True:
            action = input("➡️ Ketik [n]ext, [b]ack, [r]eload, [exit], angka (go to row), atau tekan ENTER untuk next: ").strip().lower()

            if action == '' or action == 'n':  # Enter atau 'n' = next
                index += 1
                break
            elif action == 'b':
                if index > 0:
                    index -= 1
                    print("⏪ Mundur ke NIP sebelumnya...")
                    results.pop()  # Hapus hasil sebelumnya
                else:
                    print("🚫 Sudah di awal data.")
                break
            elif action == 'r':
                print("🔄 Me-reload halaman...")
                driver.refresh()
                time.sleep(5)
                break
            elif action == 'exit':
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
                print("❌ Input tidak dikenali. Gunakan 'n', 'b', 'r', 'exit', angka, atau tekan ENTER.")

except KeyboardInterrupt:
    print("\n⛔ Proses dihentikan.")

finally:
    # Simpan hasil ke report.xlsx
    df_output = pd.DataFrame(results)
    df_output.to_excel("report.xlsx", index=False)
    print("✅ Selesai. Data disimpan di 'report.xlsx'")
    driver.quit()

