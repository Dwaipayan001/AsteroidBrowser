import streamlit as st
import re
from tavily import TavilyClient
import os
from dotenv import load_dotenv
load_dotenv()

# --------------------------
# 🧠 Basic Page Config
# --------------------------
st.set_page_config(page_title="Comet Browser Clone", layout="wide")
st.header("🌠 Asteroid")
st.write("A Comet Browser Clone....")

# --------------------------
# 🌐 Tavily Client
# --------------------------
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_SEARCH_API"))

# --------------------------
# 🧼 Text Cleaning Helper
# --------------------------
def clean_text(text: str) -> str:
    text = re.sub(r'\n+', '\n', text)          # collapse multiple newlines
    text = re.sub(r'[ \t]+', ' ', text)        # collapse excessive spaces
    return text.strip()

# --------------------------
# 🔍 Tavily Search Function
# --------------------------
def tavily_client_results(query: str):
    response = tavily_client.search(
        query,
        search_depth="basic",
        topic="news",
        time_range="year",
        max_results=20,
        include_images=True,
        include_answer=True,
        include_image_descriptions=True
    )

    # Extract answer
    answer = response.get('answer', '')

    # Extract sources (title, url, date, content)
    sources = [
        {
            'title': link.get('title', 'No title'),
            'url': link.get('url', '#'),
            'published_date': link.get('published_date', 'No date'),
            'content': (link.get('content', 'No description available')[:250] + '...')
        }
        for link in response.get('results', [])
    ]

    # Extract images with descriptions
    images = {img['url']: img.get('description', '') for img in response.get('images', [])}

    return answer, sources, images

# --------------------------
# 🧠 Session State Setup
# --------------------------
if "url" not in st.session_state:
    st.session_state.url = []

if "answer" not in st.session_state:
    st.session_state.answer = ""

if "image" not in st.session_state:
    st.session_state.image = {}

# --------------------------
# 🔍 Search Bar
# --------------------------
st.markdown("### 🔍 Search")
query = st.text_input("Enter your query...")

if st.button("Search"):
    with st.spinner("Fetching the latest info..."):
        st.session_state.answer, st.session_state.url, st.session_state.image = tavily_client_results(query)

# --------------------------
# 📑 Tabs
# --------------------------
results_tab, sources_tab, images_tab = st.tabs(["Results", "Sources", "Images"])

# --------------------------
# 📝 Results Tab
# --------------------------
with results_tab:
    if st.session_state.answer:
        cleaned_answer = clean_text(st.session_state.answer)
        st.markdown(cleaned_answer.replace('\n', '  \n'))
    else:
        st.info("Search for something to see the answer here.")

# --------------------------
# 🌐 Sources Tab
# --------------------------
with sources_tab:
    if st.session_state.url:
        st.markdown("### 🌐 Sources")
        for src in st.session_state.url:
            html = f"""
            <div style="margin-bottom: 20px;">
                <a href="{src['url']}" target="_blank" style="font-size:18px; font-weight:bold; text-decoration:none; color:#1a0dab;">
                    {src['title']}
                </a><br>
                <span style="font-size:12px; color:gray;">{src['published_date']}</span><br>
                <p style="margin:5px 0 0 0; font-size:14px; color:#202124;">{src['content']}</p>
            </div>
            """
            st.markdown(html, unsafe_allow_html=True)
    else:
        st.info("No sources to display yet.")

# --------------------------
# 🖼️ Images Tab
# --------------------------
with images_tab:
    if st.session_state.image:
        st.markdown("### 🖼️ Related Images")
        num_cols = 3
        cols = st.columns(num_cols)
        for idx, (img_url, img_desc) in enumerate(st.session_state.image.items()):
            with cols[idx % num_cols]:
                st.image(img_url, use_container_width=True, caption=img_desc)
                st.markdown(f"[🔗 Source Link]({img_url})")
    else:
        st.info("No images available for this query.")
