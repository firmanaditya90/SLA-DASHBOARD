import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard SLA Pembayaran", layout="wide")
st.title("📊 Dashboard SLA Pembayaran per Bagian")

@st.cache_data
def load_data():
    df = pd.read_excel("SLA Pembayaran.xlsx")
    df.columns = df.columns.str.strip()
    return df

df = load_data()

if df.empty:
    st.warning("Data tidak tersedia.")
else:
    st.sidebar.header("🔍 Filter Data")

    # Ambil daftar unik untuk filter
    periode_list = sorted(df['PERIODE'].dropna().unique())
    vendor_list = sorted(df['VENDOR].dropna().unique())
    bagian_list = ['FUNGSIONAL', 'VENDOR', 'KEUANGAN', 'PERBENDAHARAAN']

    # Sidebar filters
    selected_periode = st.sidebar.multiselect("Pilih PERIODE", periode_list, default=periode_list)
    selected_vendor = st.sidebar.multiselect("Pilih VENDOR", vendor_list, default=vendor_list)
    selected_bagian = st.sidebar.multiselect("Pilih BAGIAN", bagian_list, default=bagian_list)

    # Filter data
    df_filtered = df[
        df['PERIODE'].isin(selected_periode) &
        df['VENDOR'].isin(selected_vendor)
    ]

    if df_filtered.empty:
        st.warning("Tidak ada data sesuai filter.")
    else:
        st.markdown("## 📈 Statistik Rata-Rata SLA per Bagian")
        mean_values = df_filtered[selected_bagian].mean().reset_index()
        mean_values.columns = ['Bagian', 'Rata-rata SLA (hari)']

        # Display metrics
        cols = st.columns(len(selected_bagian))
        for i, bagian in enumerate(selected_bagian):
            rata = df_filtered[bagian].mean()
            cols[i].metric(f"{bagian}", f"{rata:.2f} hari")

        # Bar chart
        st.markdown("### 📊 Grafik SLA Rata-rata per Bagian")
        fig = px.bar(mean_values, x='Bagian', y='Rata-rata SLA (hari)', color='Bagian', text_auto=True)
        st.plotly_chart(fig, use_container_width=True)

        # Tampilkan tabel
        with st.expander("📋 Lihat Data Terfilter"):
            st.dataframe(df_filtered[['Periode', 'Vendor'] + selected_bagian], use_container_width=True)

        # Tombol unduh CSV
        csv = df_filtered[['Periode', 'Vendor'] + selected_bagian].to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Unduh Data Terfilter (CSV)", csv, "sla_data_filtered.csv", "text/csv")
