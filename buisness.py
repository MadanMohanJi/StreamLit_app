import streamlit as st
import pandas as pd
import requests
from Bio import Entrez
import time

# --- CONFIGURATION ---
st.set_page_config(page_title="BD Web Agent Dashboard", layout="wide")
PROXYCURL_API_KEY = "YOUR_PROXYCURL_API_KEY"
Entrez.email = "your.email@example.com" # Required by NCBI for PubMed access

# --- STAGE 2 & 3: ENRICHMENT & SCORING LOGIC ---
def get_pubmed_score(name, company):
    """Checks PubMed for papers on DILI/3D models in the last 2 years (+40 pts)"""
    try:
        query = f'("{name}"[Author]) AND (DILI OR "liver toxicity" OR "3D in-vitro")'
        handle = Entrez.esearch(db="pubmed", term=query, mindate="2023", maxdate="2025")
        results = Entrez.read(handle)
        count = int(results["Count"])
        return 40 if count > 0 else 0
    except:
        return 0

def calculate_score(row):
    """Applies weighted criteria from the assignment (0-100)"""
    score = 0
    # Role Fit (+30)
    target_keywords = ['Toxicology', 'Safety', 'Hepatic', '3D']
    if any(kw.lower() in str(row['Title']).lower() for kw in target_keywords):
        score += 30
    
    # Scientific Intent (+40) - Handled by PubMed function
    score += row['Scientific_Score']
    
    # Hub Location (+10)
    hubs = ['Boston', 'Cambridge', 'Bay Area', 'Basel', 'UK']
    if any(hub.lower() in str(row['Location']).lower() for hub in hubs):
        score += 10
        
    # Company Intent (+20) - Simulation of Funding News check
    if "Series B" in str(row['Company']):
        score += 20
        
    return score

# --- STAGE 4: DASHBOARD UI ---
st.title("🚀 Business Development Lead Dashboard")
st.markdown("Ranked leads for 3D In-Vitro Model adoption.")

# Simulation: Input a LinkedIn Search or CSV
uploaded_file = st.file_uploader("Upload Lead List (CSV)", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    if st.button("Run Web Agent Research"):
        with st.spinner("Agent is crawling PubMed and Enriching Data..."):
            # Stage 2: Enrichment
            df['Scientific_Score'] = df.apply(lambda x: get_pubmed_score(x['Name'], x['Company']), axis=1)
            
            # Stage 3: Ranking
            df['Probability'] = df.apply(calculate_score, axis=1)
            df = df.sort_values(by="Probability", ascending=False)
            
            # Add Rank Column
            df.insert(0, 'Rank', range(1, len(df) + 1))

        # --- OUTPUT TABLE ---
        st.subheader("Qualified Lead Pipeline")
        
        # Search Functionality
        search_query = st.text_input("Filter list (e.g., 'Boston' or 'Oncology')")
        if search_query:
            df = df[df.apply(lambda row: search_query.lower() in row.astype(str).str.lower().values, axis=1)]

        st.dataframe(df, use_container_width=True)

        # Export Functionality
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Export to CSV", data=csv, file_name="qualified_leads.csv", mime="text/csv")

else:
    st.info("Please upload a CSV file with 'Name', 'Title', 'Company', and 'Location' columns to begin.")