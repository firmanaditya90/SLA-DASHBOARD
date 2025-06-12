import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Dashboard SLA Pembayaran",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 Dashboard SLA Pembayaran")

@st.cache_data
def load_data():
    try:
        df = pd.read_excel("SLA Pembayaran.xlsx")
        df.columns = df.columns.str.strip().str.lower()

        rename_map = {
            'vendor': 'Vendor',
            'unit': 'Unit',
            'periode': 'Periode',
            'sla (hari)': 'SLA (hari)'
        }
        df = df.rename(columns=rename_map)

        required_columns = ['Vendor', 'Unit', 'Periode', 'SLA (hari)']
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            st.error(f"Kolom berikut tidak ditemukan dalam file: {missing}")
            return pd.DataFrame()

        df = df.dropna(subset=['SLA (hari)', 'Periode'])
        return df
    except Exception as e:
        st.error(f"Gagal memuat data: {e}")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.warning("Data tidak tersedia atau format file tidak sesuai.")
else:
    with st.sidebar:
        st.header("🔍 Filter Data")
        selected_periode = st.multiselect("Periode (Bulan/Tahun)", sorted(df['Periode'].unique()), default=sorted(df['Periode'].unique()))
        selected_vendors = st.multiselect("Vendor", df['Vendor'].unique(), default=df['Vendor'].unique())
        selected_units = st.multiselect("Unit", df['Unit'].unique(), default=df['Unit'].unique())

    df_filtered = df[
        (df['Periode'].isin(selected_periode)) &
        (df['Vendor'].isin(selected_vendors)) &
        (df['Unit'].isin(selected_units))
    ]

    avg_sla = df_filtered['SLA (hari)'].mean()
    min_sla = df_filtered['SLA (hari)'].min()
    max_sla = df_filtered['SLA (hari)'].max()

    st.markdown("## 📈 Statistik SLA")
    col1, col2, col3 = st.columns(3)
    col1.metric("🎯 Rata-rata SLA", f"{avg_sla:.2f} hari")
    col2.metric("📉 SLA Tercepat", f"{min_sla:.0f} hari")
    col3.metric("📈 SLA Terlama", f"{max_sla:.0f} hari")

    st.markdown("### 🧾 Rata-rata SLA per Vendor")
    fig_vendor = px.bar(
        df_filtered.groupby("Vendor")["SLA (hari)"].mean().reset_index(),
        x="Vendor", y="SLA (hari)", text_auto=True,
        color="SLA (hari)", title="Rata-rata SLA per Vendor"
    )
    st.plotly_chart(fig_vendor, use_container_width=True)

    st.markdown("### 🏢 Rata-rata SLA per Unit")
    fig_unit = px.bar(
        df_filtered.groupby("Unit")["SLA (hari)"].mean().reset_index(),
        x="Unit", y="SLA (hari)", color="SLA (hari)", text_auto=True,
        title="Rata-rata SLA per Unit"
    )
    st.plotly_chart(fig_unit, use_container_width=True)

    with st.expander("📋 Lihat Tabel Data Terfilter"):
        st.dataframe(df_filtered, use_container_width=True)

    csv = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Unduh Data Terfilter (CSV)", csv, "data_sla_terfilter.csv", "text/csv")