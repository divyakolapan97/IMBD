import streamlit as st
import pandas as pd

import numpy as np
from sqlalchemy import create_engine


username = 'root'
password = '1997'
host = '127.0.0.1'
database = 'imdb' 


# SQL Connection setup
def get_data_from_sql():
    engine = create_engine(f'mysql+mysqlconnector://{username}:{password}@{host}/{database}')  # Replace with your database connection
    query = """
    SELECT * FROM top_moviedata_imdb
    """
    return pd.read_sql(query, engine)

# Load data
data = get_data_from_sql()
print(data.head(5))
import streamlit as st
import plotly.express as px
data['Duration'] = pd.to_numeric(data['Duration'], errors='coerce')
data['Ratings'] = pd.to_numeric(data['Ratings'], errors='coerce')
#data['Voting Counts'] = pd.to_numeric(data['Voting Counts'], errors='coerce')

st.title("Movie Data Analysis and Visualization")

# Sidebar for Filtering
st.sidebar.header("Filter Options")
genres = st.sidebar.multiselect("Select Genre(s)", options=data['Genre'].unique())
  
duration_filter = st.sidebar.slider("Duration Filter (in hours)", 0, 10, (0, 10))
rating_filter = st.sidebar.slider("Rating Filter", 0.0, 10.0, (0.0, 10.0))
voting_filter = st.sidebar.slider("Votes Count Filter", 0, int(data['Votes Count'].max()), (0, int(data['Votes Count'].max())))

filtered_data = data

# Apply genre filter
if genres:
    filtered_data = filtered_data[filtered_data['Genre'].apply(lambda x: any(genre in x for genre in genres))]

# Apply duration filter (convert hours to minutes)
filtered_data = filtered_data[(filtered_data['Duration'] >= duration_filter[0] * 60) & 
                               (filtered_data['Duration'] <= duration_filter[1] * 60)]

# Apply rating filter
filtered_data = filtered_data[(filtered_data['Ratings'] >= rating_filter[0]) & 
                               (filtered_data['Ratings'] <= rating_filter[1])]

# Apply votes count filter
filtered_data = filtered_data[(filtered_data['Votes Count'] >= voting_filter[0]) & 
                               (filtered_data['Votes Count'] <= voting_filter[1])]

# Display the filtered data
st.write(filtered_data)

## Top 10 Movies by Rating and Voting Counts
top_10_movies = filtered_data.sort_values(by=['Ratings', 'Votes Count'], ascending=False).head(10)
fig1 = px.bar(top_10_movies, x='Name of movie', y='Ratings', color='Votes Count', title='Top 10 Movies by Rating and Voting Counts')
st.plotly_chart(fig1)

## Genre Distribution
# Create the genre distribution data
genre_counts = filtered_data['Genre'].value_counts().reset_index()

genre_counts.columns = ['Genre', 'Count']

fig2 = px.bar(genre_counts, x='Genre', y='Count', title='Genre Distribution')
fig2.update_layout(xaxis_title="Genre", yaxis_title="Count of Movies")
st.plotly_chart(fig2)

# Calculate the average duration by genre
avg_duration = filtered_data.groupby('Genre')['Duration'].mean().reset_index()
fig3 = px.bar(avg_duration, x='Duration', y='Genre', title='Average Duration by Genre', orientation='h')
st.plotly_chart(fig3)

# Average Voting Counts by Genre
avg_voting = filtered_data.groupby('Genre')['Votes Count'].mean().reset_index()  # Fixed column name
fig4 = px.bar(avg_voting, x='Genre', y='Votes Count', title='Average Voting Counts by Genre')  # Fixed column name
st.plotly_chart(fig4)

# Rating Distribution
fig5 = px.histogram(filtered_data, x='Ratings', title='Rating Distribution')
st.plotly_chart(fig5)

# Genre-Based Rating Leaders
top_rated_movies = filtered_data.loc[filtered_data.groupby('Genre')['Ratings'].idxmax()][['Genre', 'Name of movie', 'Ratings']]  # Fixed column name
st.write("Top-Rated Movies by Genre", top_rated_movies)

# Most Popular Genres by Voting
total_votes_by_genre = filtered_data.groupby('Genre')['Votes Count'].sum().reset_index()  # Fixed column name
fig6 = px.pie(total_votes_by_genre, names='Genre', values='Votes Count', title='Most Popular Genres by Voting')  # Fixed column name
st.plotly_chart(fig6)

# Duration Extremes
shortest_movie = filtered_data.loc[filtered_data['Duration'].idxmin()]
longest_movie = filtered_data.loc[filtered_data['Duration'].idxmax()]
st.write("Shortest Movie: ", shortest_movie[['Name of movie', 'Duration']])  # Fixed column name
st.write("Longest Movie: ", longest_movie[['Name of movie', 'Duration']])  # Fixed column name

# Ratings by Genre (Heatmap)
rating_by_genre = filtered_data.pivot_table(values='Ratings', index='Genre', aggfunc='mean')
fig7 = px.imshow(rating_by_genre.T, title="Ratings by Genre Heatmap")
st.plotly_chart(fig7)

# Correlation Analysis (Ratings vs Voting Counts)
fig8 = px.scatter(filtered_data, x='Votes Count', y='Ratings', title='Correlation between Ratings and Voting Counts')  # Fixed column name
st.plotly_chart(fig8)




