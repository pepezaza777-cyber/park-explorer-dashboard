"""Park Explorer: แดชบอร์ดนักท่องเที่ยวอุทยานแห่งชาติด้วย Streamlit."""
from html import escape
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Park Explorer | อุทยานไทย", page_icon="🌿", layout="wide")
SOURCE_URL = "https://data.go.th/th/dataset/gdpublish-stat-tourism"
DATA_PATH = Path(__file__).resolve().parent / "national_park_visitors.csv"
MONTHS = ["ต.ค.", "พ.ย.", "ธ.ค.", "ม.ค.", "ก.พ.", "มี.ค.",
          "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย."]
COLORS = ["#25664c", "#b88239", "#749788", "#476f8b", "#b67570",
          "#81749c", "#79983d", "#4a9896", "#96604b", "#b8a449"]

# CSS ตกแต่งหน้าจอเท่านั้น การกรองและคำนวณใช้ Pandas ด้านล่าง
st.markdown("""
<style>
.stApp { background: #f5f4ed; color: #233b30; }
.block-container { max-width: 1460px; padding: 2rem 3rem 3rem; }
header[data-testid="stHeader"] { background: rgba(245,244,237,.92); }
div[data-testid="stVerticalBlockBorderWrapper"] > div {
    background: #fffefa; border-color: #e1e5db !important; border-radius: 18px;
}
div[data-testid="stMetric"] { padding: .3rem .1rem; }
div[data-testid="stMetricValue"] { color: #215a42; font-size: 2rem; }
div[data-testid="stMetricLabel"] { color: #647268; }
.park-hero { position: relative; overflow: hidden; border-radius: 24px;
    min-height: 265px; padding: 36px 40px; background: #173e2e; color: #fff; }
.hero-copy { position: relative; z-index: 2; max-width: 63%; }
.hero-kicker { font-size: 12px; letter-spacing: 3px; color: #cee2c0; margin-bottom: 12px; }
.hero-title { font-size: clamp(32px,4vw,52px); line-height: 1.2; font-weight: 750; margin: 0 0 13px; }
.hero-sub { color: #dfebdf; font-size: 15px; line-height: 1.8; max-width: 620px; }
.hero-badge { display: inline-block; border: 1px solid #547b61; border-radius: 30px;
    padding: 6px 13px; color: #e7efdd; font-size: 12px; margin-top: 18px; }
.hero-art { position: absolute; right: 0; bottom: 0; width: 45%; height: 100%; }
.section-kicker { color: #6d8173; font-size: 11px; letter-spacing: 2px; font-weight: 650; margin-top: 4px; }
.park-insight { background: #e8eee1; border-left: 4px solid #779657;
    padding: 16px 20px; border-radius: 0 14px 14px 0; color: #35513e; line-height: 1.8; }
.park-footer { font-size: 12px; color: #788277; border-top: 1px solid #dde2d7; padding-top: 18px; margin-top: 28px; }
@media (max-width: 780px) {
    .block-container { padding: 1.3rem 1rem 2rem; }
    .park-hero { padding: 26px 24px; min-height: 285px; }
    .hero-copy { max-width: 100%; } .hero-art { opacity: .20; width: 80%; }
    .hero-sub { font-size: 14px; }
}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    """คงค่าจริงจาก CSV แล้วใช้ melt แปลง 12 คอลัมน์เดือนเป็นแถว."""
    df = pd.read_csv(DATA_PATH, encoding="utf-8-sig")
    df.columns = df.columns.str.strip()
    missing = set(["ปี", "อุทยานแห่งชาติ", "สังกัด", *MONTHS]) - set(df.columns)
    if missing:
        raise ValueError(f"ไฟล์ขาดคอลัมน์: {', '.join(sorted(missing))}")
    df["ปี"] = pd.to_numeric(df["ปี"], errors="raise").astype(int)
    for col in ["อุทยานแห่งชาติ", "สังกัด"]:
        df[col] = df[col].str.strip()
    long_df = df.melt(id_vars=["ปี", "อุทยานแห่งชาติ", "สังกัด"],
                      value_vars=MONTHS, var_name="เดือน", value_name="จำนวนผู้เข้าชม")
    long_df["จำนวนผู้เข้าชม"] = pd.to_numeric(
        long_df["จำนวนผู้เข้าชม"].astype(str).str.replace(",", "", regex=False).str.strip(),
        errors="coerce")
    long_df["ลำดับเดือน"] = long_df["เดือน"].map(
        {month: i for i, month in enumerate(MONTHS, 1)})
    return long_df


def style_chart(fig, height=380):
    """ใช้สีและตัวอักษรเดียวกันทุกกราฟ."""
    fig.update_layout(
        template="plotly_white", height=height,
        font=dict(family="Tahoma, sans-serif", color="#354c3d", size=12),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=12, r=20, t=20, b=35),
        legend=dict(title=None, orientation="h", y=1.13, x=0),
        hoverlabel=dict(bgcolor="#ffffff", font_size=13))
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(gridcolor="#e9ede3", zeroline=False)
    return fig


# ภาพภูเขาเป็น SVG เขียนในโค้ด จึงเปิดได้โดยไม่ต้องดาวน์โหลดภาพเพิ่ม
st.html("""
<div class="park-hero">
  <div class="hero-copy">
    <div class="hero-kicker">THAILAND / PARK EXPLORER</div>
    <div class="hero-title">มองอุทยานไทย<br>ผ่านการเดินทางของผู้คน</div>
    <div class="hero-sub">สำรวจแนวโน้มผู้เข้าชม เปรียบเทียบอุทยานยอดนิยม
    และค้นหาช่วงเดือนที่มีการท่องเที่ยวมากที่สุด</div>
    <div class="hero-badge">ข้อมูลปีงบประมาณ พ.ศ. 2559–2568</div>
  </div>
  <svg class="hero-art" viewBox="0 0 640 330" preserveAspectRatio="xMidYMax slice"
       role="img" aria-label="ภาพภูเขาและป่าประกอบหัวเรื่อง">
    <circle cx="490" cy="75" r="41" fill="#d9d5a3"/>
    <path d="M0 330 L140 130 L218 206 L348 73 L515 252 L640 170 L640 330Z" fill="#56775a"/>
    <path d="M0 330 L160 222 L265 285 L405 161 L640 312 L640 330Z" fill="#365b45"/>
    <path d="M0 330 Q130 234 275 300 Q420 225 640 294 L640 330Z" fill="#254c38"/>
    <path d="M366 330 Q375 295 415 282 Q454 270 468 249" fill="none" stroke="#9bae80" stroke-width="7"/>
    <g fill="#173e2e">
      <path d="M530 260 l-32 49 h64Z M530 233 l-25 46 h50Z M530 211 l-19 38 h38Z"/>
      <path d="M583 282 l-29 43 h58Z M583 257 l-23 42 h46Z"/>
      <path d="M110 280 l-32 48 h64Z M110 250 l-24 43 h48Z"/>
    </g>
  </svg>
</div>
""")

try:
    data = load_data()
except (OSError, ValueError, pd.errors.ParserError) as error:
    st.error(f"อ่านข้อมูลไม่ได้: {error}")
    st.info("วาง national_park_visitors.csv ไว้ในโฟลเดอร์เดียวกับ app.py")
    st.stop()

# ตัวกรองแนวนอนอยู่ในหน้าหลัก ไม่มีแถบตัวกรองด้านข้าง
with st.container(border=True):
    st.markdown('<div class="section-kicker">EXPLORE THE DATA</div>', unsafe_allow_html=True)
    st.markdown("**เลือกข้อมูลที่อยากสำรวจ**")
    f1, f2, f3, f4 = st.columns([1.1, 1.5, 1.5, .8])
    years = sorted(data["ปี"].unique().tolist())
    with f1:
        selected_years = st.multiselect("ปีงบประมาณ (พ.ศ.)", years, default=years[-3:], key="years")
    with f2:
        selected_offices = st.multiselect("สังกัด", sorted(data["สังกัด"].unique()),
                                          default=[], key="offices", placeholder="ทุกสังกัด")
    with f3:
        selected_parks = st.multiselect("อุทยานแห่งชาติ", sorted(data["อุทยานแห่งชาติ"].unique()),
                                        default=[], key="parks", placeholder="ทุกอุทยาน")
    with f4:
        top_n = st.selectbox("แสดงอันดับ", [5, 10, 15, 20], index=1, key="top_n")
    st.caption("เลือกปีอย่างน้อย 1 ปี • สังกัดและอุทยานเว้นว่าง = ดูทั้งหมด")

filtered = data[data["ปี"].isin(selected_years)].copy()
if selected_offices:
    filtered = filtered[filtered["สังกัด"].isin(selected_offices)]
if selected_parks:
    filtered = filtered[filtered["อุทยานแห่งชาติ"].isin(selected_parks)]
if filtered.empty:
    st.warning("ไม่พบข้อมูลตามตัวกรอง กรุณาเลือกปี หรือปรับสังกัดและอุทยาน")
    st.stop()

valid = filtered.dropna(subset=["จำนวนผู้เข้าชม"])
if valid.empty:
    st.warning("ข้อมูลที่เลือกไม่มีจำนวนผู้เข้าชมที่เป็นตัวเลข")
    st.stop()
if len(valid) != len(filtered):
    st.info(f"ไม่นำค่าที่อ่านเป็นตัวเลขไม่ได้ {len(filtered) - len(valid):,} รายการมารวม")

# สรุปข้อมูลครั้งเดียว แล้วนำไปใช้กับการ์ดและกราฟ
annual = filtered.groupby("ปี", as_index=False)["จำนวนผู้เข้าชม"].sum(min_count=1)
ranking = (filtered.groupby("อุทยานแห่งชาติ", as_index=False)["จำนวนผู้เข้าชม"]
           .sum(min_count=1).dropna().sort_values("จำนวนผู้เข้าชม", ascending=False))
monthly = (filtered.groupby(["ปี", "ลำดับเดือน", "เดือน"], as_index=False)["จำนวนผู้เข้าชม"]
           .sum(min_count=1).sort_values(["ปี", "ลำดับเดือน"]))
season = (filtered.groupby(["ลำดับเดือน", "เดือน"], as_index=False)["จำนวนผู้เข้าชม"]
          .sum(min_count=1).dropna())
peak = season.loc[season["จำนวนผู้เข้าชม"].idxmax()]

st.caption("กำลังสำรวจปีงบประมาณ " + " · ".join(str(y) for y in sorted(selected_years)))
m1, m2, m3, m4 = st.columns(4)
with m1, st.container(border=True):
    st.metric("ผู้เข้าชมรวม / คน", f"{valid['จำนวนผู้เข้าชม'].sum():,.0f}")
with m2, st.container(border=True):
    st.metric("ชื่ออุทยานในข้อมูล", f"{filtered['อุทยานแห่งชาติ'].nunique():,}")
with m3, st.container(border=True):
    st.metric("ปีงบประมาณที่เลือก", f"{filtered['ปี'].nunique():,}")
with m4, st.container(border=True):
    st.metric("เดือนที่มียอดรวมสูงสุด", peak["เดือน"])
st.caption("ทุกยอดคำนวณจากตัวกรองที่เลือก • จำนวนผู้เข้าชมไม่ใช่จำนวนบุคคลที่ไม่ซ้ำกัน")

overview_tab, monthly_tab, data_tab = st.tabs(["ภาพรวมการเดินทาง", "สำรวจรายเดือน", "ข้อมูลและแหล่งที่มา"])

with overview_tab:
    left, right = st.columns([1.15, 1])
    with left, st.container(border=True):
        st.markdown('<div class="section-kicker">THE BIG PICTURE</div>', unsafe_allow_html=True)
        st.subheader("แนวโน้มผู้เข้าชม")
        st.caption("ยอดรวมแยกตามปีงบประมาณ")
        # กราฟที่ 1: กราฟพื้นที่พร้อมเส้นแนวโน้ม
        fig_annual = px.area(annual, x="ปี", y="จำนวนผู้เข้าชม", markers=True,
                             color_discrete_sequence=[COLORS[0]],
                             labels={"ปี": "ปีงบประมาณ (พ.ศ.)", "จำนวนผู้เข้าชม": "ผู้เข้าชม / คน"})
        fig_annual.update_xaxes(tickmode="array", tickvals=annual["ปี"].tolist())
        fig_annual.update_traces(line=dict(width=3), fillcolor="rgba(93,139,101,.16)",
                                hovertemplate="ปีงบประมาณ %{x}<br>%{y:,.0f} คน<extra></extra>")
        st.plotly_chart(style_chart(fig_annual, 400), width="stretch", theme=None)
    with right, st.container(border=True):
        st.markdown('<div class="section-kicker">POPULAR PARKS</div>', unsafe_allow_html=True)
        st.subheader(f"อุทยานยอดนิยม {min(top_n, len(ranking))} อันดับ")
        st.caption("เรียงจากยอดผู้เข้าชมรวมของปีที่เลือก")
        # กราฟที่ 2: กราฟแท่งแนวนอน
        top = ranking.head(top_n)
        fig_ranking = px.bar(top, x="จำนวนผู้เข้าชม", y="อุทยานแห่งชาติ", orientation="h",
                             color_discrete_sequence=[COLORS[0]],
                             labels={"จำนวนผู้เข้าชม": "ผู้เข้าชม / คน", "อุทยานแห่งชาติ": ""})
        fig_ranking.update_yaxes(categoryorder="array",
                                 categoryarray=top["อุทยานแห่งชาติ"].tolist()[::-1])
        fig_ranking.update_traces(marker=dict(cornerradius=5),
                                 hovertemplate="%{y}<br>%{x:,.0f} คน<extra></extra>")
        st.plotly_chart(style_chart(fig_ranking, max(400, len(top) * 29)),
                        width="stretch", theme=None)
    leader = ranking.iloc[0]
    # escape ชื่ออุทยานจากไฟล์ก่อนใส่ HTML
    st.html(f"""<div class="park-insight"><b>อุทยานที่มียอดผู้เข้าชมสูงสุดในข้อมูลที่เลือก</b><br>
    {escape(str(leader['อุทยานแห่งชาติ']))} · {leader['จำนวนผู้เข้าชม']:,.0f} คน
    <br>เดือน {escape(str(peak['เดือน']))} มียอดผู้เข้าชมรวมทุกปีที่เลือกสูงสุด
    ({peak['จำนวนผู้เข้าชม']:,.0f} คน)</div>""")

with monthly_tab:
    with st.container(border=True):
        st.markdown('<div class="section-kicker">SEASONAL JOURNEYS</div>', unsafe_allow_html=True)
        st.subheader("การเดินทางในแต่ละเดือน")
        st.caption("เปรียบเทียบแต่ละปีด้วยเส้นคนละสี เรียงเดือนตามปีงบประมาณ")
        monthly["ปีงบประมาณ"] = monthly["ปี"].astype(str)
        # กราฟที่ 3: กราฟเส้นรายเดือน
        fig_monthly = px.line(monthly, x="เดือน", y="จำนวนผู้เข้าชม",
                              color="ปีงบประมาณ", markers=True,
                              color_discrete_sequence=COLORS,
                              category_orders={"เดือน": MONTHS},
                              labels={"จำนวนผู้เข้าชม": "ผู้เข้าชม / คน"})
        fig_monthly.update_traces(line=dict(width=2.5))
        fig_monthly.update_xaxes(categoryorder="array", categoryarray=MONTHS)
        st.plotly_chart(style_chart(fig_monthly, 430), width="stretch", theme=None)
    st.info("ปีงบประมาณเริ่ม ต.ค. ของปีก่อน ถึง ก.ย. ของปีที่ระบุ เช่น ปี 2568 = ต.ค. 2567–ก.ย. 2568")

with data_tab:
    st.subheader("ข้อมูลที่ใช้ในมุมมองนี้")
    table = filtered.sort_values(["ปี", "อุทยานแห่งชาติ", "ลำดับเดือน"])[
        ["ปี", "อุทยานแห่งชาติ", "สังกัด", "เดือน", "จำนวนผู้เข้าชม"]]
    st.download_button("ดาวน์โหลดข้อมูลที่เลือก (CSV)",
                        table.to_csv(index=False).encode("utf-8-sig"),
                        "filtered_park_visitors.csv", "text/csv")
    st.dataframe(table, width="stretch", hide_index=True)
    with st.expander("อ่านแหล่งที่มาและความหมายของข้อมูล"):
        st.markdown(f"**หน่วยงาน:** กรมอุทยานแห่งชาติ สัตว์ป่า และพันธุ์พืช\n\n[เปิดชุดข้อมูลบน data.go.th]({SOURCE_URL})")
        st.write("ใช้ไฟล์ tourism59-68.csv คงค่าจากต้นฉบับ หน่วย: คน")
        st.write("ชื่ออุทยานคงตามต้นทาง บางแห่งเปลี่ยนรูปแบบชื่อระหว่างปี จึงอาจมีหลายชื่อในตัวกรอง")
        st.write("ค่าศูนย์คงตามต้นฉบับ ไม่ตีความว่าเกิดจากไม่มีผู้เข้าชมหรือการปิดอุทยาน")
        st.write("ค่าที่แปลงเป็นตัวเลขไม่ได้ไม่นำมารวม และไม่แทนด้วยศูนย์")

st.html('<div class="park-footer">PARK EXPLORER · ข้อมูลเปิดจากกรมอุทยานแห่งชาติ สัตว์ป่า และพันธุ์พืช ผ่าน data.go.th</div>')
