import streamlit as st
import pandas as pd
import json

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(page_title="Scope 66", layout="wide")

# ----------------------------
# SESSION STATE
# ----------------------------
if "onboarding_step" not in st.session_state:
    st.session_state["onboarding_step"] = 0

if "selected_topic" not in st.session_state:
    st.session_state["selected_topic"] = None

# ----------------------------
# ONBOARDING
# ----------------------------
if st.session_state["onboarding_step"] < 3:

    st.markdown(
        """
    <style>
    .onboard-box {
        background-color: #1c1f26;
        padding: 30px;
        border-radius: 16px;
        margin-top: 20px;
        color: white;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="onboard-box">', unsafe_allow_html=True)

    step = st.session_state["onboarding_step"]

    if step == 0:
        st.header("Welcome to Scope 66 🚀")
        st.write(
            """
The aim of this project is to summarize what academic research is producing and detect emerging technologies.

We also aim to highlight technologies that may become important over the next 3 years.

Technologies labelled as **persistent** are those that have remained dominant (highly cited) over the past 3 years.

We analyze approximately **5,000 academic papers per year**.
        """
        )

    elif step == 1:
        st.header("How it works 🔍")
        st.write(
            """
We do not try to predict the future — although that would be cool 🙂

Instead, we surface:
- 🌱 Emerging technologies  
- 🧱 Persistent technologies  
- 🤖 Model-predicted trends  
- 🔥 Dominant research areas  

Only for **2025**, you can click a topic and read a deeper analysis.
        """
        )

    elif step == 2:
        st.header("About this MVP 🧪")
        st.write(
            """
This is an MVP.

In the future, topics can be filtered by broader domains like *science*, *medicine*, or specific areas like *word embeddings*.

Constructive feedback is very welcome 🙌

**Yours sincerely,**  
Ilan Grynszpan
        """
        )

    col1, col2 = st.columns([1, 1])

    with col1:
        if step > 0 and st.button("← Back"):
            st.session_state["onboarding_step"] -= 1

    with col2:
        if step < 2:
            if st.button("Next →"):
                st.session_state["onboarding_step"] += 1
        else:
            if st.button("Enter Scope 66"):
                st.session_state["onboarding_step"] = 3
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ----------------------------
# STYLE
# ----------------------------
st.markdown(
    """
<style>
html, body {
    background-color: #0e1117;
    color: #e6e6e6;
}

.topic-card {
    background-color: #1c1f26;
    padding: 12px;
    border-radius: 12px;
    margin-bottom: 10px;
}

.meta {
    font-size: 12px;
    color: #9aa4b2;
}

.analysis-box {
    background-color: #1c1f26;
    padding: 20px;
    border-radius: 12px;
    margin-top: 20px;
}
</style>
""",
    unsafe_allow_html=True,
)

# ----------------------------
# HEADER
# ----------------------------
col1, col2 = st.columns([1, 6])

with col1:
    try:
        st.image("scope66_logo.png", width=70)
    except:
        pass

with col2:
    st.title("Scope 66")
    st.caption("Scientific Trend Intelligence")


# ----------------------------
# LOAD DATA
# ----------------------------
@st.cache_data
def load_data():
    dashboard = pd.read_parquet("dashboard.parquet")
    papers = pd.read_parquet("classified_papers.parquet")

    with open("topic_outputs.json") as f:
        outputs = json.load(f)

    return dashboard, papers, outputs


dashboard, papers, outputs = load_data()

dashboard = dashboard[dashboard["year"] > 2017]

# ----------------------------
# SCORE
# ----------------------------
dashboard["bar_score"] = dashboard.get("final_score")
dashboard["bar_score"] = dashboard["bar_score"].fillna(dashboard.get("prd_prob", 0))
dashboard["bar_score"] = dashboard["bar_score"] / dashboard.groupby("year")[
    "bar_score"
].transform("max")

# ----------------------------
# YEAR SELECTOR
# ----------------------------
years = sorted(dashboard["year"].unique())
year = st.slider("Year", int(min(years)), int(max(years)), max(years))

year_data = dashboard[dashboard["year"] == year]

# ----------------------------
# 2025 MESSAGE
# ----------------------------
if year == 2025:
    st.info("📌 Click a topic and scroll down to read its description and analysis.")

# ----------------------------
# CARDS
# ----------------------------
categories = ["dominant", "emerging", "growth", "persistent", "model"]

for cat in categories:
    st.markdown(f"## {cat.capitalize()}")

    subset = year_data[year_data["category"] == cat]

    if subset.empty:
        continue

    subset = subset.sort_values("bar_score", ascending=False)

    for i, row in subset.iterrows():
        topic = int(row["topic"])
        topic_name = row.get("topic_name", f"Topic {topic}")

        share = row.get("share", 0)
        score = float(row.get("bar_score", 0))

        st.markdown('<div class="topic-card">', unsafe_allow_html=True)

        col1, col2 = st.columns([5, 1])

        with col1:
            if st.button(topic_name, key=f"{cat}_{topic}_{i}"):
                st.session_state["selected_topic"] = topic

        with col2:
            st.markdown(f"<div class='meta'>{share:.2%}</div>", unsafe_allow_html=True)

        st.progress(score)

        st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------
# ANALYSIS SECTION (BOTTOM)
# ----------------------------
if st.session_state["selected_topic"] is not None:

    topic = st.session_state["selected_topic"]

    st.markdown("---")
    st.header("Topic Analysis")

    key = f"{topic}_{year}"

    description = outputs.get(key, {}).get("description")
    report = outputs.get(key, {}).get("report")

    st.subheader("Description")
    st.write(description if description else "Not available")

    if year == 2025:
        st.subheader("Analysis")
        st.write(report if report else "Not generated")

    topic_papers = papers[papers["topic"] == topic]

    st.subheader("Recent Papers")
    st.dataframe(
        topic_papers.sort_values("year", ascending=False)[["year", "title"]].head(10)
    )
