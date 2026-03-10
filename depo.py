import streamlit as st
import sqlite3
import pandas as pd

# --- Veritabanı ---
def init_db():
    conn = sqlite3.connect("depo_profesyonel.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, role TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS categories (id INTEGER PRIMARY KEY AUTOINCREMENT, name_tr TEXT, name_ar TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT, name_tr TEXT, name_ar TEXT, cat_id INTEGER, price REAL, stock INTEGER)")
    c.execute("CREATE TABLE IF NOT EXISTS requests (id INTEGER PRIMARY KEY AUTOINCREMENT, user TEXT, item_tr TEXT, qty INTEGER, status TEXT)")
    c.execute("INSERT OR IGNORE INTO users VALUES ('admin', '1234', 'admin')")
    conn.commit(); conn.close()

init_db()

if 'user' not in st.session_state: st.session_state.user = None

# --- Giriş ---
if not st.session_state.user:
    st.title("🔐 5CVH ERP")
    u, p = st.text_input("Kullanıcı / اسم المستخدم"), st.text_input("Şifre / كلمة المرور", type="password")
    if st.button("Giriş / دخول"):
        conn = sqlite3.connect("depo_profesyonel.db")
        user = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (u, p)).fetchone()
        if user: st.session_state.user, st.session_state.role = user[0], user[2]; st.rerun()
        conn.close()
    st.stop()

# --- Sidebar ---
st.sidebar.title(f"👤 {st.session_state.user}")
if st.sidebar.button("Çıkış / خروج"): st.session_state.user = None; st.rerun()

menu_options = ["Stok Durumu / حالة المخزون"]
if st.session_state.role == 'personel': menu_options.append("Taleplerim / طلباتي")
else: menu_options.extend(["Gelen Talepler / الطلبات الواردة", "Ürün Girişi / إدخال منتج", "Kategoriler / التصنيفات", "Kullanıcı Yönetimi / إدارة المستخدمين"])
menu = st.sidebar.radio("Menu", menu_options)

conn = sqlite3.connect("depo_profesyonel.db")

# --- Modüller ---
if "Stok Durumu" in menu:
    st.header("Stok Durumu / حالة المخزون")
    df = pd.read_sql("SELECT name_tr AS 'Ürün(TR)', name_ar AS 'المنتج(AR)', price AS 'Fiyat/السعر', stock AS 'Adet/الكمية' FROM products", conn)
    st.dataframe(df, use_container_width=True)
    if st.session_state.role == 'personel':
        item = st.selectbox("Ürün / المنتج", df.iloc[:,0].tolist())
        qty = st.number_input("Adet / الكمية", min_value=1)
        if st.button("Talep Et / طلب"):
            conn.execute("INSERT INTO requests (user, item_tr, qty, status) VALUES (?,?,?,?)", (st.session_state.user, item, qty, 'Bekliyor / انتظار'))
            conn.commit(); st.rerun()

elif "Taleplerim" in menu:
    st.header("Taleplerim / طلباتي")
    df_req = pd.read_sql(f"SELECT item_tr AS 'Ürün / المنتج', qty AS 'Adet / الكمية', status AS 'Durum / الحالة' FROM requests WHERE user = '{st.session_state.user}'", conn)
    st.dataframe(df_req, use_container_width=True)

elif "Gelen Talepler" in menu:
    st.header("Gelen Talepler / الطلبات الواردة")
    reqs = conn.execute("SELECT * FROM requests WHERE status != 'Teslim / تسليم'").fetchall()
    for r in reqs:
        st.write(f"👤 {r[1]} | 📦 {r[2]} | Adet: {r[3]} | Durum: {r[4]}")
        c1, c2, c3 = st.columns(3)
        if c1.button("Onayla / تأكيد", key=f"o{r[0]}"): conn.execute("UPDATE requests SET status='Hazır / جاهز' WHERE id=?", (r[0],)); conn.commit(); st.rerun()
        if c2.button("Hazır / جاهز", key=f"h{r[0]}"): conn.execute("UPDATE requests SET status='Hazır / جاهز' WHERE id=?", (r[0],)); conn.commit(); st.rerun()
        if c3.button("Teslim / تسليم", key=f"t{r[0]}"):
            conn.execute("UPDATE products SET stock = stock - ? WHERE name_tr=?", (r[3], r[2]))
            conn.execute("UPDATE requests SET status='Teslim / تسليم' WHERE id=?", (r[0],)); conn.commit(); st.rerun()

elif "Ürün Girişi" in menu:
    cats = pd.read_sql("SELECT name_tr FROM categories", conn)
    with st.form("u"):
        at = st.text_input("Ürün(TR) / المنتج(TR)"); aa = st.text_input("Ürün(AR) / المنتج(AR)")
        kat = st.selectbox("Kategori / التصنيف", cats['name_tr'].tolist() if not cats.empty else ["Yok"])
        f = st.number_input("Fiyat / السعر"); s = st.number_input("Adet / الكمية")
        if st.form_submit_button("Kaydet / حفظ"):
            conn.execute("INSERT INTO products (name_tr, name_ar, price, stock) VALUES (?,?,?,?)", (at, aa, f, s))
            conn.commit(); st.rerun()

elif "Kategoriler" in menu:
    with st.form("kat"):
        tr, ar = st.text_input("Kategori(TR)"), st.text_input("Kategori(AR)")
        if st.form_submit_button("Ekle / إضافة"):
            conn.execute("INSERT INTO categories (name_tr, name_ar) VALUES (?,?)", (tr, ar)); conn.commit(); st.rerun()

elif "Kullanıcı Yönetimi" in menu:
    with st.form("user"):
        u, p, r = st.text_input("Kullanıcı / اسم المستخدم"), st.text_input("Şifre / كلمة المرور"), st.selectbox("Rol / الدور", ["admin", "personel"])
        if st.form_submit_button("Kaydet / حفظ"):
            conn.execute("INSERT INTO users VALUES (?,?,?)", (u, p, r)); conn.commit(); st.rerun()

conn.close()