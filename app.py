import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Dashboard SLA Verifikasi Pembayaran",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 Dashboard SLA Verifikasi Pembayaran")

@st.cache_data
def load_data():
    try:
        df = pd.read_excel("SLA Pembayaran.xlsx")
        df.columns = df.columns.str.strip().str.lower()

        rename_map = {
            'tanggal pembayaran': 'Tanggal Pembayaran',
            'tanggal verifikasi': 'Tanggal Verifikasi',
            'vendor': 'Vendor',
            'unit': 'Unit'
        }
        df = df.rename(columns=rename_map)

        df['Tanggal Pembayaran'] = pd.to_datetime(df['Tanggal Pembayaran'], errors='coerce')
        df['Tanggal Verifikasi'] = pd.to_datetime(df['Tanggal Verifikasi'], errors='coerce')

        df = df.dropna(subset=['Tanggal Pembayaran', 'Tanggal Verifikasi'])

        df['SLA (hari)'] = (df['Tanggal Verifikasi'] - df['Tanggal Pembayaran']).dt.days
        df['Minggu'] = df['Tanggal Pembayaran'].dt.strftime('%Y-%U')
        return df
    except Exception as e:
        st.error(f"Gagal memuat data: {e}")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.warning("Data tidak tersedia atau terjadi kesalahan pada file Excel.")
else:
    with st.sidebar:
        st.header("🔍 Filter Data")
        date_range = st.date_input("Periode Pembayaran", [
            df['Tanggal Pembayaran'].min(),
            df['Tanggal Pembayaran'].max()
        ])
        selected_vendors = st.multiselect("Vendor", df['Vendor'].unique(), default=df['Vendor'].unique())
        selected_units = st.multiselect("Unit", df['Unit'].unique(), default=df['Unit'].unique())

    df_filtered = df[
        (df['Tanggal Pembayaran'] >= pd.to_datetime(date_range[0])) &
        (df['Tanggal Pembayaran'] <= pd.to_datetime(date_range[1])) &
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

    st.markdown("### 📅 Tren SLA per Minggu")
    fig_mingguan = px.line(
        df_filtered.groupby("Minggu")["SLA (hari)"].mean().reset_index(),
        x="Minggu", y="SLA (hari)", markers=True,
        title="Rata-rata SLA Verifikasi Pembayaran per Minggu"
    )
    st.plotly_chart(fig_mingguan, use_container_width=True)

    st.markdown("### 🏢 SLA per Unit")
    fig_unit = px.bar(
        df_filtered.groupby("Unit")["SLA (hari)"].mean().reset_index(),
        x="Unit", y="SLA (hari)", color="SLA (hari)", text_auto=True,
        title="Rata-rata SLA Verifikasi Pembayaran per Unit"
    )
    st.plotly_chart(fig_unit, use_container_width=True)

    with st.expander("📋 Lihat Tabel Data Terfilter"):
        st.dataframe(df_filtered, use_container_width=True)

    csv = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Unduh Data Terfilter (CSV)", csv, "data_sla_terfilter.csv", "text/csv")