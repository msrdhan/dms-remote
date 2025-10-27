import pandas as pd
import os

# === Konfigurasi ===
INPUT_FILE = 'input.xlsx'
OUTPUT_DIR = 'output_dir'
SHEET_NAME = 0  # Ganti jika sheet bukan yang pertama

# === Load data dengan NIP sebagai string ===
df = pd.read_excel(INPUT_FILE, sheet_name=SHEET_NAME, dtype={'NIP': str})

# Hapus kolom '#' jika ada
if '#' in df.columns:
    df = df.drop(columns=['#'])

# Sortir berdasarkan 'nip' sebagai string (descending)
df = df.sort_values(by='NIP', ascending=False)

# Hapus duplikat berdasarkan seluruh baris
df = df.drop_duplicates(subset='NIP')

# Buat folder output jika belum ada
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Pisahkan dan simpan per instansi
for instansi, group in df.groupby('Instansi'):
    jumlah = len(group)
    filename = f"({jumlah}) {instansi}.xlsx"
    filepath = os.path.join(OUTPUT_DIR, filename)
    group.to_excel(filepath, index=False)

print(f"Selesai. File disimpan di folder '{OUTPUT_DIR}'.")