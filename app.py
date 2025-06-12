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

    # Normalisasi nama kolom
    bagian_map = {
        'fungsi vendor': 'vendor',
        'fungsi fungsi': 'fungsional',
        'fungsi keuangan': 'keuangan',
        'fungsi perbendaharaan': 'perbendaharaan'
    }

    bagian_all = list(bagian_map.values())

    # Pilihan filter
    periode_list = sorted(df['periode'].dropna().unique())
    vendor_list = sorted(df['vendor'].dropna().unique())

    selected_periode = st.sidebar.multiselect("🗓 Pilih Periode", periode_list, default=periode_list)
    selected_vendor = st.sidebar.multiselect("🏢 Pilih Vendor", vendor_list, default=vendor_list)
    selected_bagian = st.sidebar.multiselect("🏬 Pilih Bagian", bagian_all, default=bagian_all)

    df_filtered = df[
        df['periode'].isin(selected_periode) &
        df['vendor'].isin(selected_vendor)
    ]

    if df_filtered.empty:
        st.warning("⚠️ Tidak ada data untuk filter tersebut.")
    else:
        st.subheader("📈 Rata-Rata SLA per Bagian")

        # Hitung rata-rata berdasarkan kolom asli
        hasil = {}
        for kolom_asli, nama_bagian in bagian_map.items():
            if nama_bagian in selected_bagian:
                if kolom_asli in df_filtered.columns:
                    hasil[nama_bagian] = df_filtered[kolom_asli].mean()
        
        # Tampilkan metrik
        cols = st.columns(len(hasil))
        for i, (bagian, nilai) in enumerate(hasil.items()):
            cols[i].metric(bagian.capitalize(), f"{nilai:.2f} hari")

        # Tampilkan chart
        st.markdown("### 📊 Grafik SLA Rata-rata")
        chart_df = pd.DataFrame({
            'Bagian': list(hasil.keys()),
            'Rata-Rata SLA (hari)': list(hasil.values())
        })

        fig = px.bar(chart_df, x="Bagian", y="Rata-Rata SLA (hari)", color="Bagian", text_auto=True)
        st.plotly_chart(fig, use_container_width=True)

        # Tampilkan tabel
        with st.expander("📋 Data Terfilter"):
            kolom_tampil = ['periode', 'vendor'] + list(bagian_map.keys())
            df_tampil = df_filtered[kolom_tampil]
            st.dataframe(df_tampil, use_container_width=True)

        # Unduh data
        csv = df_tampil.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Unduh Data (CSV)", csv, "data_sla.csv", "text/csv")
