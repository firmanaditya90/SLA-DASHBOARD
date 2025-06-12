import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard SLA Pembayaran", layout="wide")
st.title("📊 Dashboard SLA Pembayaran per Bagian")

@st.cache_data
def load_data():
    df = pd.read_excel("SLA Terbaru1.xlsx")
    df.columns = df.columns.str.strip().str.lower()
    return df

df = load_data()

if df.empty:
    st.warning("Data tidak tersedia.")
else:
    st.sidebar.header("🔍 Filter Data")

    # Deteksi kolom periode & vendor secara dinamis
    periode_col = [col for col in df.columns if 'periode' in col.lower()]
    vendor_col = [col for col in df.columns if 'vendor' in col.lower()]

    if not periode_col or not vendor_col:
        st.error("❌ Kolom 'Periode' atau 'Vendor' tidak ditemukan.")
        st.stop()

    periode_col = periode_col[0]
    vendor_col = vendor_col[0]

    df[periode_col] = df[periode_col].astype(str)
    df[vendor_col] = df[vendor_col].astype(str)

    # Mapping kolom bagian -> nama label
    bagian_map = {
        'fungsi vendor': 'vendor',
        'fungsi fungsi': 'fungsional',
        'fungsi keuangan': 'keuangan',
        'fungsi perbendaharaan': 'perbendaharaan'
    }
    bagian_all = list(bagian_map.values())

    # Sidebar Filter
    periode_list = sorted(df[periode_col].dropna().unique())
    vendor_list = sorted(df[vendor_col].dropna().unique())

    selected_periode = st.sidebar.multiselect("🗓 Pilih Periode", periode_list, default=periode_list)
    selected_vendor = st.sidebar.multiselect("🏢 Pilih Vendor", vendor_list, default=vendor_list)
    selected_bagian = st.sidebar.multiselect("🏬 Pilih Bagian", bagian_all, default=bagian_all)

    # Filter data
    df_filtered = df[
        df[periode_col].isin(selected_periode) &
        df[vendor_col].isin(selected_vendor)
    ]

    if df_filtered.empty:
        st.warning("⚠️ Tidak ada data untuk filter tersebut.")
    else:
        st.subheader("📈 Rata-Rata SLA per Bagian")

        # Hitung rata-rata
        hasil = {}
        for kolom_asli, nama_bagian in bagian_map.items():
            if nama_bagian in selected_bagian and kolom_asli in df_filtered.columns:
                hasil[nama_bagian] = df_filtered[kolom_asli].mean()

        # Metrik per bagian
        if hasil:
    cols = st.columns(len(hasil))
    for i, (bagian, nilai) in enumerate(hasil.items()):
        cols[i].metric(bagian.capitalize(), f"{nilai:.2f} hari")
else:
    st.info("Silakan pilih bagian yang memiliki data untuk ditampilkan.")

        # Chart bar
        st.markdown("### 📊 Grafik SLA Rata-rata")
        chart_df = pd.DataFrame({
            'Bagian': list(hasil.keys()),
            'Rata-Rata SLA (hari)': list(hasil.values())
        })
        fig = px.bar(chart_df, x="Bagian", y="Rata-Rata SLA (hari)", color="Bagian", text_auto=True)
        st.plotly_chart(fig, use_container_width=True)

        # Tabel hasil
        with st.expander("📋 Data Terfilter"):
            kolom_tampil = [periode_col, vendor_col] + list(bagian_map.keys())
            kolom_tampil = [k for k in kolom_tampil if k in df_filtered.columns]
            st.dataframe(df_filtered[kolom_tampil], use_container_width=True)

        # Tombol unduh
        csv = df_filtered[kolom_tampil].to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Unduh Data (CSV)", csv, "data_sla.csv", "text/csv")
