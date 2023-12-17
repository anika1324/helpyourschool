import streamlit as st
import pandas as pd
from pymongo import MongoClient
import plotly.express as px


# Function to fetch unique fundraiser IDs and titles
def get_unique_fundraiser_ids_and_titles():
    client = MongoClient("mongodb_uri")
    db = client["community_fundraiser"]
    fundraisers_collection = db["community"]
    id_title_pairs = []
    fundraiser_data = list(fundraisers_collection.find())

    #st.write(fundraiser_data)
    for fundraiser in fundraiser_data:
        funid =fundraiser['_id']
        title= fundraiser['title']
        id_title_pairs.append(f"{funid} - {title}")
    
    client.close()
    return id_title_pairs


# Function to connect to MongoDB and retrieve contributions for a specific fundraiser
def get_contributions(fundraiser_id):

    client = MongoClient("mongodb+srv://...")
    db = client["community_fundraiser"]
    contributions_collection = db["contributions"]

    query = {"fundraiser_id": fundraiser_id}
    contributions = list(contributions_collection.find(query))
    client.close()

    return pd.DataFrame(contributions)

# Streamlit UI
st.title('Fundraisers Contributions Visualization')

# Get unique fundraiser IDs and titles from MongoDB
fundraiser_options = get_unique_fundraiser_ids_and_titles()

# Dropdown to select a fundraiser
selected_option = st.selectbox('Select a Fundraiser', fundraiser_options)
selected_fundraiser_id = int(selected_option.split(' - ')[0])  # Extracting the ID

# Get contributions data for the selected fundraiser
contributions_df = get_contributions(selected_fundraiser_id)

# Visualization
if not contributions_df.empty:
    # Process the DataFrame as needed for visualization
    fig = px.bar(contributions_df, x='date', y='amount',
                 labels={'date': 'Date', 'amount': 'Contribution Amount'},
                 title=f'Contributions for Fundraiser: {selected_option}')
    # Update the layout to adjust the y-axis range
    fig.update_layout(yaxis=dict(range=[0, 500]))
    st.plotly_chart(fig)
else:
    st.write("No contributions found for this fundraiser.")


