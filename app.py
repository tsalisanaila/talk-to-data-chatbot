import streamlit as st
import pandas as pd
import plotly.express as px
import re
from sqlalchemy import create_engine, text
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import ast

# ==========================================
# 1. KONFIGURASI
# ==========================================

# API Key Groq
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

# Database Credentials
DB_USER = "root"
DB_PASSWORD = ""      
DB_HOST = "localhost"
DB_NAME = "db_retail" 

st.set_page_config(page_title="Retail AI Analyst", page_icon="🛍️", layout="wide")
with st.sidebar:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/128/11083/11083341.png", width=100)
    st.title("Tentang Aplikasi")
    st.markdown("""
    Aplikasi ini memungkinkan Anda melakukan **analisis data** menggunakan **Bahasa Manusia**.
    
    **Teknologi:**
    - 🧠 LLM: Llama 3 (via Groq)
    - 🦜 Framework: LangChain
    - 🗄️ Database: MySQL
    - 📊 Viz: Plotly
    
    **Created by:** Tsalisa Naila Ghaniyya
    **2026**
    """)
    st.divider()
    if st.button("🗑️ Hapus Riwayat Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    st.info("💡 Tips: Coba tanya 'Bagaimana tren penjualan setiap tahunnya?'")

# ==========================================
# 2. DEFINISI SCHEMA
# ==========================================
SCHEMA_TEXT = """
Table Name: transactions

Columns:
- transaction_id (Text)
- date (Date/Time) -> Format YYYY-MM-DD
- customer_name (Text)
- product (Text) -> Represents: Product Category, Jenis Produk, Kategori Barang
- total_items (Number) -> Represents: Quantity, Jumlah Barang
- total_cost (Number) -> Represents: Sales, Penjualan, Omzet, Revenue, Total Harga
- payment_method (Text)
- city (Text) -> Represents: Kota, Lokasi, Wilayah
- store_type (Text)
- discount_applied (Boolean)
- customer_category (Text) -> Represents: Jenis Pelanggan, Tipe Customer, Member/Non-member
- season (Text)
- promotion (Text)

RULES:
1. ONLY use the table 'transactions'. DO NOT JOIN with any other table.
2. If asked for 'Jumlah Transaksi', use `COUNT(*)`.
3. If asked for 'Total Penjualan/Omzet', use `SUM(total_cost)`.
4. Group by the relevant column if aggregation is needed.
"""

# ==========================================
# 3. FUNGSI UTAMA
# ==========================================

def get_engine():
    """Membuat koneksi ke database"""
    return create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}")

def generate_sql_from_text(question):
    """
    Meminta LLM mengubah dari Teks -> SQL
    """
    llm = ChatGroq(
        temperature=0, 
        model_name="llama-3.3-70b-versatile", 
        api_key=GROQ_API_KEY
    )
    
    # Template prompt
    template = """
    You are a SQL Expert converting natural language to SQL queries.
    
    DATABASE SCHEMA:
    {schema}
    
    USER QUESTION:
    {question}
    
    YOUR TASK:
    Generate a valid MySQL query to answer the question.
    - Return ONLY the SQL query.
    - Do NOT wrap it in markdown (no ```sql ... ```).
    - Do NOT add explanations.
    - Start the query with SELECT.
    """
    
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | llm
    
    response = chain.invoke({"schema": SCHEMA_TEXT, "question": question})
    
    # Cleaning hasil LLM
    sql_query = response.content.replace("```sql", "").replace("```", "").strip()
    return sql_query

def execute_sql(query):
    """Menjalankan SQL Query dan mengembalikan DataFrame"""
    try:
        engine = get_engine()
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        st.error(f"❌ SQL Error: {e}")
        return None

# ==========================================
# 4. VISUALISASI
# ==========================================

def smart_explode_data(df):
    """
    Fungsi untuk memecah data kolom produk dari keranjang belanja menjadi item satuan
    """
    if 'product' not in df.columns:
        return df

    sample = str(df['product'].iloc[0])
    if not (sample.startswith('[') and sample.endswith(']')):
        return df 

    try:
        df['product'] = df['product'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) and x.startswith('[') else x)
        df_exploded = df.explode('product')
        numeric_cols = df_exploded.select_dtypes(include=['number']).columns.tolist()
        
        agg_dict = {}
        for col in numeric_cols:
            if 'count' in col.lower() or 'jumlah' in col.lower():
                agg_dict[col] = 'sum'
            else:
                agg_dict[col] = 'mean' 
                
        if agg_dict:
            df_final = df_exploded.groupby('product', as_index=False).agg(agg_dict)
            return df_final
        
        return df_exploded
        
    except Exception as e:
        print(f"Explode failed: {e}")
        return df

def clean_labels(value):
    """Pembersih label"""
    if isinstance(value, str):
        return value.replace("['", "").replace("']", "").replace('["', '').replace('"]', "").replace("'", "")
    return value

def auto_visualize(df):
    if df is None or df.empty:
        return None
    
    if len(df) == 1:
        return None

    df = smart_explode_data(df)

    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

    for col in cat_cols:
        df[col] = df[col].apply(clean_labels)

    time_col = None
    time_keywords = ['date', 'time', 'year', 'month', 'day', 'bulan', 'tahun', 'tanggal', 'waktu']
    for col in df.columns:
        if any(keyword in col.lower() for keyword in time_keywords):
            time_col = col
            break
    
    fig = None
    
    # Logic Chart
    if time_col and len(numeric_cols) > 0:
        y_cols = [c for c in numeric_cols if c != time_col]
        if y_cols:
            y_col = y_cols[0]
            df = df.sort_values(by=time_col)
            fig = px.line(df, x=time_col, y=y_col, title=f"Tren {y_col} per {time_col}", markers=True)

    elif len(cat_cols) > 0 and len(numeric_cols) > 0:
        x_col = cat_cols[0]
        y_col = numeric_cols[0]
 
        df = df.sort_values(by=y_col, ascending=False)
        
        if df.shape[0] > 10: 
            df = df.head(10)
            title = f"Top 10 {x_col} by {y_col}"
        else:
            title = f"{y_col} per {x_col}"
            
        fig = px.bar(df, x=x_col, y=y_col, title=title, color=x_col)
        
    return fig

# ==========================================
# 5. USER INTERFACE STREAMLIT
# ==========================================

st.title("💬 Talk-to-Data: Retail Assistant")
st.caption("Tanyakan apa saja tentang penjualanmu, biarkan AI membuatkan query SQL dan grafiknya.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "dataframe" in message:
            st.dataframe(message["dataframe"])

        if "chart" in message and message["chart"] is not None:
            st.plotly_chart(message["chart"])

# Input User
if prompt := st.chat_input("Contoh: Tampilkan jumlah transaksi per jenis pelanggan"):
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("⏳ *Sedang menerjemahkan ke SQL...*")
        
        try:
            sql_query = generate_sql_from_text(prompt)
            placeholder.markdown(f"```sql\n{sql_query}\n```") 
            
            df_result = execute_sql(sql_query)
            
            if df_result is not None and not df_result.empty:
                st.success("✅ Data ditemukan!")
                st.dataframe(df_result) 
                
                fig = auto_visualize(df_result)
                if fig:
                    st.plotly_chart(fig)

                response_data = {
                    "role": "assistant", 
                    "content": f"Berikut datanya berdasarkan query:\n```sql\n{sql_query}\n```",
                    "dataframe": df_result
                }
                if fig is not None:
                    response_data["chart"] = fig
                
                st.session_state.messages.append(response_data)
            else:
                st.warning("⚠️ Query berhasil dijalankan, tapi datanya kosong.")
                st.session_state.messages.append({"role": "assistant", "content": "Data tidak ditemukan."})

        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")