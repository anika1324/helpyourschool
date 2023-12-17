import streamlit as st
from pymongo import MongoClient
import requests
import uuid

#Replace these 
current_user_token_id = "<ADD YOUR TOKEN>"
current_user_wallet_id = "<ADD YOUR WALLET_ID"
api_key = "CIRCLE API KEY" 
entity_secret_ciphertext = ""

def transfer_amount(api_key, entity_secret_ciphertext, amount, token_id, wallet_id, destination_wallet_id):
    url = 'https://api.circle.com/v1/w3s/developer/transactions/transfer'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    entity_secret_ciphertext='<ADD ENTITY SECRET'

    payload = {
        'idempotencyKey': str(uuid.uuid4()),
        'entitySecretCipherText': entity_secret_ciphertext,
        'amounts': [amount],
        'feeLevel': 'HIGH',
        'tokenId': token_id,
        'walletId': wallet_id,
        'destinationAddress': destination_wallet_id
    }
    
    st.write("Transferred from your wallet ", wallet_id) 
    response = requests.post(url, headers=headers, json=payload)
    return response.json()


# Function to connect to MongoDB and retrieve fundraiser data
def get_fundraiser_data():
    # Replace with your MongoDB Atlas connection URI
    client = MongoClient("<mongodb uri>")

    # Replace with your specific database and collection name
    db = client["community_fundraiser"]
    collection = db["community"]

    data = list(collection.find())
    client.close()
    return data



# Function to inject custom CSS for titles
def local_css():
    st.markdown("""
        <style>
            .title {
                color: maroon;
                font-weight: bold;
            }
        </style>
        """, unsafe_allow_html=True)

# Initialize session state
if 'contribute_item' not in st.session_state:
    st.session_state.contribute_item = {'id': None, 'title': None, 'wallet_address':None}

# Function to handle contribute button click
def contribute(item_id, item_title, wallet_address):
    st.session_state.contribute_item = {'id': item_id, 'title': item_title, 'wallet_address':wallet_address}


# Function to post contribution to MongoDB
def post_contribution(fundraiser_id, from_user_id, amount):
    contribution_record = {
        "fundraiser_id": fundraiser_id,
        "from_user_id": from_user_id,
        "amount": amount,
        "date": datetime.now()
    }

     # Replace with your MongoDB Atlas connection URI
    client = MongoClient("<mongodb_uri>")

    db = client["community_fundraiser"]
    contributions_collection = db["contributions"]
    contributions_collection.insert_one(contribution_record)
    client.close()


# Title of the app
st.title('HelpYourSchool')

# Custom CSS for titles
local_css()

# Retrieve fundraiser data from MongoDB
fundraiser_data = get_fundraiser_data()

# Display fundraiser data with contribute buttons
for fundraiser in fundraiser_data:
    # Display the title with custom style
    st.markdown(f"<div class='title'>{fundraiser['title']}</div>", unsafe_allow_html=True)
    with st.expander("See details"):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write("Description:", fundraiser['description'])
            st.write("Goal Amount:", fundraiser['goal_amount'])
            st.write("Current Amount:", fundraiser['current_amount'])
            st.write("Start Date:", fundraiser['start_date'])
            st.write("End Date:", fundraiser['end_date'])

        with col2:
            if st.button('Contribute', key=f"button_{fundraiser['_id']}"):
                contribute(fundraiser['_id'], fundraiser['title'], fundraiser['wallet_address'])

#Streamlit does not allow modal popups
if st.session_state.contribute_item['id'] is not None:
    with st.form(key='contribution_form'):
        st.write(f"You are contributing to: {st.session_state.contribute_item['title']} with wallet {st.session_state.contribute_item['wallet_address']} ")
        amount = st.number_input('Amount', min_value=0.0)
        submit_button = st.form_submit_button('Submit')
        if submit_button:
            # Fetch destination wallet address from MongoDB
            destination_wallet_id = st.session_state.contribute_item['wallet_address'] # from  MongoDB based on the item_id

            # Call the transfer function
            transfer_result = transfer_amount(
                api_key, 
                entity_secret_ciphertext, 
                str(amount), 
                current_user_token_id, 
                current_user_wallet_id, 
                destination_wallet_id
            )

            if transfer_result.get('status') == 'success':
                post_contribution(
                    fundraiser_id=st.session_state.contribute_item['id'],
                    from_user_id=current_user_wallet_id,  # Assuming this is the user ID
                    amount=amount
                )
                st.success("Transfer successful")
            else:
                st.error("Transfer Error")

            st.write("Thank you for contributing", amount, "to", st.session_state.contribute_item['title'])
            st.session_state.contribute_item = {'id': None, 'title': None}

