import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
#import matplotlib.font_manager as fm

# 한글 폰트 설정
plt.rcParams['font.family'] = "NanumGothic"
plt.rcParams['axes.unicode_minus'] = False

st.set_page_config(page_title="퇴직율 대시보드", layout="wide")
sns.set(style="whitegrid",font="Malgun Gothic")

# 1) 데이터 로드
@st.cache_data
def load_df(path:str ="HR Data.csv") -> pd.DataFrame:
    try:
        df = pd.read_csv(path, encoding="utf-8")
    except: 
        return df 
    df["퇴직"] = df["퇴직여부"].map({"Yes":1, "No":0}).astype("int8")
    df.drop(['직원수', '18세이상'], axis=1, inplace=True)
    return df

df = load_df()
if df.empty:
    st.error("데이터가 없습니다. 'HR Data.csv' 파일을 확인하세요.")
    st.stop()

# ===== KPI  =====
# 1) 헤더 & KPI
st.title("퇴직율 분석 및 인사이트")
n = len(df); quit_n = int(df["퇴직"].sum())
quit_rate = df["퇴직"].mean()*100
stay_rate = 100 - quit_rate
k1,k2,k3,k4 = st.columns(4)
k1.metric("전체 직원 수", f"{n:,}명")
k2.metric("퇴직자 수", f"{quit_n:,}명")
k3.metric("유지율", f"{stay_rate:.1f}%")
k4.metric("퇴직율", f"{quit_rate:.1f}%")



dist_home = df["집과의거리"].mean()
satis=df["업무환경만족도"].mean()
av_age=df["나이"].mean()

l1,l2, = st.columns(2) 
with l1:  
    l1.metric("평균 귀가 거리:train:", f"{dist_home:.2f} km")

with l2:
    l2.metric("평균 업무 만족도는?",f"{satis:2f}/5")
    if st.button("지금 우리는", key="satis_btn"):
        st.info("ㅠㅠ")



# 3) 그래프 1: 부서별 평균 근속연수
if "부서" in df.columns:
    dept_avg_years = df.groupby('부서')['근속연수'].mean()
    st.subheader("부서별 평균 근속연수")
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.pie(dept_avg_years, labels=[f'{label}: {value:.1f}' for label, value in dept_avg_years.items()])
    ax.set_title('부서별 평균 근속연수')
    st.pyplot(fig)
# 4) 그래프 2/3를 두 칼럼으로
c1, c2, c3 = st.columns(3)

# (좌) 급여인상율과 퇴직율 (정수%로 라운딩 후 라인)
if "급여증가분백분율" in df.columns:
    tmp = df[["급여증가분백분율","퇴직"]].dropna().copy()
    tmp["인상률(%)"] = tmp["급여증가분백분율"].round().astype(int)
    sal = tmp.groupby("인상률(%)")["퇴직"].mean()*100
    with c1:
        st.subheader("💰 급여인상율과 퇴직율")
        fig2, ax2 = plt.subplots(figsize=(6.5,3.5))
        sns.lineplot(x=sal.index, y=sal.values, marker="o", ax=ax2)
        ax2.set_xlabel("급여인상율(%)"); 
        ax2.set_ylabel("퇴직율(%)")
        st.pyplot(fig2)

# (우) 야근정도별 퇴직율 (Yes/No 막대)
col_name = "야근정도"
if col_name in df.columns:
    ot = (df.groupby(col_name)["퇴직"].mean()*100)
#    ot.index = ot.index.map({"No":"없음","Yes":"있음"}).astype(str)
    with c2:
        st.subheader("⏰ 야근정도별 퇴직율")
        fig3, ax3 = plt.subplots(figsize=(6.5,3.5))
        sns.barplot(x=ot.index, y=ot.values, ax=ax3)
        ax3.set_ylabel("퇴직율(%)"); 
        ax3.bar_label(ax3.containers[0], fmt="%.1f")
        st.pyplot(fig3)

if "업무환경만족도" in df.columns:
    satisfaction = df.groupby('부서')['업무환경만족도'].mean().sort_values(ascending=False)
    with c3:
        st.subheader("부서 별 만족도:smile:")
        fig, ax = plt.subplots(figsize=(4, 3))
        sns.barplot(x=satisfaction.index, y=satisfaction.values, ax=ax)
        ax.set_title('부서별 업무 환경 만족도 평균')
        ax.set_xlabel('부서')
        ax.set_ylabel('업무 환경 만족도 평균')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig)
