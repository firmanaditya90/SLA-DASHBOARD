import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard SLA Pembayaran", layout="wide")
st.title("📊 Dashboard SLA Pembayaran per Bagian")

@st.cache_data
def load_data():
    df = pd.read_excel("SLA Pembayaran.xlsx")
    df.columns = df.columns.str.strip().str.lower()
    return df

df = load_data()

if df.empty:
    st.warning("Data tidak tersedia.")
else:
    st.sidebar.header("🔍 Filter Data")

    # Inisialisasi daftar bagian
    bagian_list = ['fungsional', 'vendor', 'keuangan', 'perbendaharaan']

    # Buat filter dropdown berdasarkan isi kolom (semua lowercase)
    periode_list = sorted(df['periode'].dropna().unique())
    vendor_list = sorted(df['vendor'].dropna().unique())

    selected_periode = st.sidebar.multiselect("Pilih Periode", periode_list, default=periode_list)
    selected_vendor = st.sidebar.multiselect("Pilih Vendor", vendor_list, default=vendor_list)
    selected_bagian = st.sidebar.multiselect("Pilih Bagian", bagian_list, default=bagian_list)

    # Filter data berdasarkan pilihan
    df_filtered = df[
        df['periode'].isin(selected_periode) &
        df['vendor'].isin(selected_vendor)
    ]

    if df_filtered.empty:
        st.warning("Tidak ada data sesuai filter.")
    else:
        st.markdown("## 📈 Statistik Rata-Rata SLA per Bagian")
        mean_values = df_filtered[selected_bagian].mean().reset_index()
        mean_values.columns = ['bagian', 'rata-rata sla (hari)']

        # Tampilkan metrik rata-rata per bagian
        cols = st.columns(len(selected_bagian))
        for i, bagian in enumerate(selected_bagian):
            rata = df_filtered[bagian].mean()
            cols[i].metric(f"{bagian.capitalize()}", f"{rata:.2f} hari")

        # Bar chart
        st.markdown("### 📊 Grafik SLA Rata-rata per Bagian")
        fig = px.bar(mean_values, x='bagian', y='rata-rata sla (hari)', color='bagian', text_auto=True)
        st.plotly_chart(fig, use_container_width=True)

        # Tampilkan tabel
        with st.expander("📋 Lihat Data Terfilter"):
            st.dataframe(df_filtered[['periode', 'vendor'] + selected_bagian], use_container_width=True)

        # Tombol unduh CSV
        csv = df_filtered[['periode', 'vendor'] + selected_bagian].to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Unduh Data Terfilter (CSV)", csv, "sla_data_filtered.csv", "text/csv")
