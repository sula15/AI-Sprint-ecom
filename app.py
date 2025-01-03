#app.py
import streamlit as st
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

from src.ai_sprint.crew import EcommerceAgent

st.title("AI Deal Finder")

# Add some context information
st.write("""
Find the best deals for your desired product across multiple online stores.
We'll analyze prices, shipping costs, and overall value to help you make the best choice.
""")

# Input section
col1, col2 = st.columns(2)
with col1:
    product_type = st.text_input("What product are you looking for?", 
                                placeholder="e.g., wireless headphones")
with col2:
    budget = st.number_input("Your Budget ($)", min_value=0, value=100)

if st.button("Find Deals", type="primary"):
    if not product_type:
        st.error("Please enter a product type")
    else:
        with st.spinner("🔍 Finding the best deals for you..."):
            try:
                crew = EcommerceAgent().crew()
                result = crew.kickoff(inputs={
                    "product_type": product_type, 
                    "budget": budget
                })
                
                # Create tabs for different stages
                url_tab, deals_tab, analysis_tab = st.tabs([
                    "Found URLs", "Scraped Deals", "Analysis"
                ])
                
                with url_tab:
                    st.write("### 🌐 Discovered Deal Pages")
                    if hasattr(crew.tasks[0], 'output'):
                        st.markdown(crew.tasks[0].output)
                    else:
                        st.info("No URLs found yet")
                        
                with deals_tab:
                    st.write("### 🛍️ Available Deals")
                    if hasattr(crew.tasks[1], 'output'):
                        st.markdown(crew.tasks[1].output)
                    else:
                        st.info("No deals scraped yet")
                        
                with analysis_tab:
                    st.write("### 📊 Deal Analysis")
                    if hasattr(crew.tasks[2], 'output'):
                        st.markdown(crew.tasks[2].output)
                    else:
                        st.info("No analysis available yet")

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.info("Please try again with different search parameters")

# Add footer with additional information
st.markdown("---")
st.caption("This tool searches across multiple platforms to find the best deals. " 
          "Prices and availability are updated in real-time.")