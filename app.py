# app.py
import streamlit as st
import pandas as pd
import re
from recommendation import recommend_products

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(page_title="Retail Product Recommender", layout="wide")
st.title("🛒 Market Basket Analysis - Retail Recommender System")

# ==============================
# LOAD DATA
# ==============================
@st.cache_data
def load_data():
    df = pd.read_csv("cleaned_data.csv")
    df["Description"] = df["Description"].astype(str).str.strip().str.upper()
    return df

@st.cache_data
def load_rules():
    rules = pd.read_csv("association_rules.csv")
    
    def parse_frozenset(s):
        if pd.isna(s):
            return set()
        s_clean = re.sub(r"frozenset\(|\)$", "", s)
        if s_clean.strip() == "":
            return set()
        items = [x.strip().strip("'").strip('"') for x in s_clean.strip("{}").split(",")]
        return set(items)

    rules["antecedents"] = rules["antecedents"].apply(parse_frozenset)
    rules["consequents"] = rules["consequents"].apply(parse_frozenset)
    return rules

df = load_data()
rules = load_rules()

# ==============================
# PRODUCT SELECTION
# ==============================
all_products = sorted(df["Description"].unique())
selected_products = st.multiselect(
    "Select Products in Basket:",
    all_products,
    help="Select one or more products to get recommendations"
)

# ==============================
# GET RECOMMENDATIONS BUTTON
# ==============================
if st.button("Get Recommendations"):
    if not selected_products:
        st.warning("Please select at least one product.")
    else:
        # You can adjust these if needed
        min_conf = 0.05
        top_n = 5

        recommendations = recommend_products(
            rules,
            selected_products,
            min_confidence=min_conf,
            top_n=top_n
        )

        if recommendations:
            rec_df = pd.DataFrame(recommendations, columns=["Product", "Confidence", "Lift"])
            st.success(f"Recommended Products ({len(recommendations)}):")
            st.dataframe(rec_df.style.format({"Confidence": "{:.2f}", "Lift": "{:.2f}"}))
        else:
            st.warning("No strong recommendations found (fallback failed).")