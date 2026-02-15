import pandas as pd
from sqlalchemy import create_engine

# 1. Konfigurasi Database (Sesuaikan dengan phpMyAdmin kamu)
user = "root"
password = "" # Kosongkan jika default XAMPP
host = "localhost"
port = "3306"
db_name = "db_retail" # Pastikan database ini sudah dibuat di phpMyAdmin

# 2. Path ke file CSV yang kamu download dari Kaggle
csv_file_path = "dataset\Retail_Transactions_Dataset.csv" 

try:
    # Buat koneksi ke MySQL
    engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}")
    
    print("⏳ Sedang membaca file CSV...")
    # Membaca CSV dengan Pandas
    df = pd.read_csv(csv_file_path)
    
    # Opsional: Membersihkan nama kolom agar tidak ada spasi (penting untuk SQL)
    df.columns = [c.replace(' ', '_').lower() for c in df.columns]
    
    print(f"✅ Berhasil membaca {len(df)} baris data.")
    print("⏳ Sedang mengupload ke phpMyAdmin (MySQL)...")
    
    # Upload ke MySQL (Tabel akan dibuat otomatis jika belum ada)
    df.to_sql('transactions', con=engine, if_exists='replace', index=False)
    
    print("✨ Selesai! Data berhasil di-import ke tabel 'transactions'.")

except Exception as e:
    print(f"❌ Terjadi kesalahan: {e}")