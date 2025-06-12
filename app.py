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

    # Deteksi kolom PERIODE dan VENDOR
    periode_col = next((col for col in df.columns if 'periode' in col), None)
    vendor_col = next((col for col in df.columns if 'vendor' == col), None)

    if not periode_col or not vendor_col:
        st.error("❌ Kolom 'PERIODE' atau 'VENDOR' tidak ditemukan.")
        st.stop()

    # Mapping bagian berdasarkan kolom Excel yang tersedia
    bagian_map = {
        'fungsi vendor': 'Vendor',
        'fungsi fungsi': 'Fungsional',
        'fungsi keuangan': 'Keuangan',
        'fungsi perbendaharaan': 'Perbendaharaan'
    }
    available_bagian = {k: v for k, v in bagian_map.items() if k in df.columns}
    bagian_list = list(available_bagian.values())

    # Sidebar filter
    periode_list = sorted(df[periode_col].dropna().unique())
    vendor_list = sorted(df[vendor_col].dropna().unique())

    selected_periode = st.sidebar.multiselect("🗓 Periode", periode_list, default=periode_list)
    selected_vendor = st.sidebar.multiselect("🏢 Vendor", vendor_list, default=vendor_list)
    selected_bagian = st.sidebar.multiselect("🏬 Bagian", bagian_list, default=bagian_list)

    # Filter Data
    df_filtered = df[
        df[periode_col].isin(selected_periode) &
        df[vendor_col].isin(selected_vendor)
    ]

    if df_filtered.empty:
        st.warning("⚠️ Tidak ada data sesuai filter.")
    else:
        st.subheader("📈 Rata-rata SLA per Bagian")

        hasil = {}
        for kolom_asli, label_bagian in available_bagian.items():
            if label_bagian in selected_bagian:
                nilai_rata = df_filtered[kolom_asli].mean()
                hasil[label_bagian] = nilai_rata

        if hasil:
            cols = st.columns(len(hasil))
            for i, (bagian, nilai) in enumerate(hasil.items()):
                cols[i].metric(label=bagian, value=f"{nilai:.2f} hari")

            st.markdown("### 📊 Grafik SLA Rata-rata per Bagian")
            chart_df = pd.DataFrame({
                'Bagian': list(hasil.keys()),
                'Rata-Rata SLA (hari)': list(hasil.values())
            })
            fig = px.bar(chart_df, x="Bagian", y="Rata-Rata SLA (hari)", text_auto=True, color="Bagian")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("🔍 Tidak ada bagian terpilih atau tersedia di data.")

        # Tabel Data
        with st.expander("📋 Lihat Tabel Data Terfilter"):
            tampil_cols = [periode_col, vendor_col] + list(available_bagian.keys())
            st.dataframe(df_filtered[tampil_cols], use_container_width=True)

        # Download CSV
        csv = df_filtered[tampil_cols].to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Unduh Data Terfilter", csv, "data_sla.csv", "text/csv")
