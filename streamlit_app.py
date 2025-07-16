
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import re

# Set page config
st.set_page_config(page_title="Netflix Data Explorer", layout="wide")

# Title
st.title("🎬 Netflix Content Explorer")
st.markdown("Analyze and visualize Netflix's catalog by type, country, genre, rating, and more.")

# Load dataset
@st.cache_data
def load_data():
    df = pd.read_csv("netflix_titles.csv")
    df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce')
    df['duration_minutes'] = df['duration'].apply(lambda d: int(re.search(r'\d+', d).group()) if pd.notnull(d) and 'min' in d else np.nan)
    df['num_seasons'] = df['duration'].apply(lambda d: int(re.search(r'\d+', d).group()) if pd.notnull(d) and 'Season' in d else np.nan)
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("📊 Filters")
types = st.sidebar.multiselect("Select Type", options=df['type'].unique(), default=df['type'].unique())
countries = st.sidebar.multiselect("Select Country", options=sorted(set(df['country'].dropna().str.split(', ').explode())), default=None)
genres = st.sidebar.multiselect("Select Genre", options=sorted(set(df['listed_in'].dropna().str.split(', ').explode())), default=None)
ratings = st.sidebar.multiselect("Select Rating", options=sorted(df['rating'].dropna().unique()), default=None)
year_range = st.sidebar.slider("Select Release Year Range", int(df['release_year'].min()), int(df['release_year'].max()), (2010, 2021))

# Apply filters
filtered_df = df[df['type'].isin(types)]
if countries:
    filtered_df = filtered_df[filtered_df['country'].notna()]
    filtered_df = filtered_df[filtered_df['country'].apply(lambda x: any(c in x for c in countries))]
if genres:
    filtered_df = filtered_df[filtered_df['listed_in'].notna()]
    filtered_df = filtered_df[filtered_df['listed_in'].apply(lambda x: any(g in x for g in genres))]
if ratings:
    filtered_df = filtered_df[filtered_df['rating'].isin(ratings)]
filtered_df = filtered_df[(filtered_df['release_year'] >= year_range[0]) & (filtered_df['release_year'] <= year_range[1])]

# Show summary
st.subheader("📈 Dataset Overview")
st.write(f"Number of titles: {filtered_df.shape[0]}")
st.dataframe(filtered_df[['title', 'type', 'country', 'release_year', 'rating', 'listed_in']].head(10))

# Visualizations
st.subheader("🎞️ Titles by Type")
fig1, ax1 = plt.subplots()
sns.countplot(data=filtered_df, x='type', palette='pastel', ax=ax1)
ax1.set_title("Number of Titles by Type")
st.pyplot(fig1)
st.markdown('💡 **Insight:** Netflix’s catalog is predominantly composed of movies, reflecting a content strategy focused on one-off productions.')

st.subheader("📅 Titles Released Over Time")
fig2, ax2 = plt.subplots()
filtered_df['release_year'].value_counts().sort_index().plot(kind='line', ax=ax2)
ax2.set_title("Titles Released per Year")
ax2.set_xlabel("Year")
ax2.set_ylabel("Count")
st.pyplot(fig2)
st.markdown('💡 **Insight:** There was steady growth in releases until 2019, with a slight drop in 2020 likely due to COVID-19 production delays.')

st.subheader("🌍 Top 10 Countries")
fig3, ax3 = plt.subplots()
top_countries = filtered_df['country'].dropna().str.split(', ').explode().value_counts().head(10)
sns.barplot(x=top_countries.values, y=top_countries.index, palette='Blues_r', ax=ax3)
ax3.set_title("Top Countries by Content Count")
st.pyplot(fig3)
st.markdown('💡 **Insight:** The United States dominates Netflix's content library, but India and the UK are also major contributors.')

st.subheader("🏷️ Rating Distribution")
fig4, ax4 = plt.subplots()
sns.countplot(y='rating', data=filtered_df, order=filtered_df['rating'].value_counts().index, palette='viridis', ax=ax4)
ax4.set_title("Rating Distribution")
st.pyplot(fig4)
st.markdown('💡 **Insight:** TV-MA and TV-14 are the most common ratings, indicating content is mainly aimed at teens and adults.')

if 'duration_minutes' in filtered_df.columns and filtered_df['type'].str.contains('Movie').any():
    st.subheader("⏱️ Movie Duration Distribution")
    fig5, ax5 = plt.subplots()
    movie_durations = filtered_df[filtered_df['type'] == 'Movie']['duration_minutes'].dropna()
    if not movie_durations.empty:
        sns.histplot(movie_durations, bins=30, kde=True, ax=ax5)
        ax5.set_title("Distribution of Movie Durations")
        st.pyplot(fig5)
st.markdown('💡 **Insight:** Most movies are between 80–120 minutes long, which aligns with standard feature film lengths.')

if 'num_seasons' in filtered_df.columns and filtered_df['type'].str.contains('TV Show').any():
    st.subheader("📺 TV Show Seasons Count")
    fig6, ax6 = plt.subplots()
    tv_seasons = filtered_df[filtered_df['type'] == 'TV Show']['num_seasons'].dropna()
    if not tv_seasons.empty:
        sns.countplot(x=tv_seasons, palette='coolwarm', ax=ax6)
        ax6.set_title("Number of Seasons in TV Shows")
        ax6.set_xlabel("Seasons")
        st.pyplot(fig6)
st.markdown('💡 **Insight:** TV shows tend to have 1–2 seasons, showing Netflix’s preference for limited series or experimental runs.')

# Footer
st.markdown("---")
st.markdown("Developed by **Wesley Gonzales** | Final Project – Summer 2025")
