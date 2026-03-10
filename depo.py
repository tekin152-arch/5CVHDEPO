import streamlit as st
import psycopg2

# 1. Veritabanı Bağlantı Fonksiyonu
# Bu fonksiyon, Streamlit'in güvenli Secrets alanındaki URL'i kullanır.
def get_db_connection():
    try:
        # st.secrets, Streamlit Cloud ayarlarındaki [Secrets] kısmından veriyi çeker
        conn = psycopg2.connect(st.secrets["DATABASE_URL"])
        return conn
    except Exception as e:
        st.error(f"Veritabanına bağlanılamadı: {e}")
        return None

# 2. Tabloyu Hazırlama (Uygulama ilk açıldığında çalışır)
def init_db():
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS stoklar (
                id SERIAL PRIMARY KEY,
                urun_adi TEXT NOT NULL,
                miktar INT NOT NULL
            )
        """)
        conn.commit()
        cur.close()
        conn.close()

# Uygulama Başlangıcı
st.set_page_config(page_title="Bulut ERP Sistemi", page_icon="📦")
st.title("📦 Bulut Tabanlı ERP Sistemi")
init_db() # Tabloyu kontrol et

# 3. Arayüz: Veri Ekleme
st.subheader("Yeni Ürün Ekle")
with st.form("ekle_formu"):
    urun = st.text_input("Ürün Adı")
    miktar = st.number_input("Miktar", min_value=0, step=1)
    submit = st.form_submit_button("Kaydet")

    if submit:
        if urun:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO stoklar (urun_adi, miktar) VALUES (%s, %s)", (urun, miktar))
            conn.commit()
            cur.close()
            conn.close()
            st.success(f"{urun} başarıyla eklendi!")
        else:
            st.warning("Lütfen ürün adı girin.")

# 4. Arayüz: Verileri Gösterme
st.subheader("Stok Listesi")
if st.button("Listeyi Güncelle"):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT urun_adi, miktar FROM stoklar")
    veriler = cur.fetchall()
    
    if veriler:
        for row in veriler:
            st.write(f"✅ **{row[0]}** - Adet: {row[1]}")
    else:
        st.info("Stokta ürün bulunmuyor.")
    cur.close()
    conn.close()