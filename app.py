import streamlit as st
import pandas as pd
import json
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize OpenAI
llm = OpenAI()

st.markdown(
    """
    <style>
    .stApp {
        background-color: #34495E;
    }
    .black-title {
        color: black;
        font-size: 32px;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)


def generate_item_list(prompt):
    completion = llm.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an assistant that helps users generate a list of items needed for their household project. Please do not add additional items from your own. Extract all items from user input."},
            {"role": "user", "content": prompt}
        ],
        functions=[
            {
                "name": "get_list_of_items",
                "description": "Get the list of items needed for a price estimate.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "item_list": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "The list of items needed.",
                        }
                    },
                    "required": ["item_list"],
                },
            }
        ],
        function_call="auto"
    )

    output = completion.choices[0].message
    item_list = json.loads(output.function_call.arguments).get("item_list")
    return item_list

st.title("Household Project Item List Generator")

prompt = st.text_input("Describe your household project:", "I need an estimate for a 100 square foot master bathroom remodel that involves a bathtub and shower surround with a new tiled shower pan, full height tile walls, and a new double vanity")

if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame({"Items": []})

if st.button("Generate Item List"):
    with st.spinner("Generating item list..."):
        try:
            item_list = generate_item_list(prompt)
            if item_list:
                st.session_state.df = pd.DataFrame({"Items": item_list})
                st.success("Item list generated successfully!")
            else:
                st.warning("No items found in the prompt.")
        except Exception as e:
            st.error(f"An error occurred: {e}")

if not st.session_state.df.empty:
    st.write("### Items List")
    dited_df = st.data_editor(st.session_state.df, height=400 , width=500) 

    # Dropdown to select the item to remove
    remove_item = st.selectbox("Select an item to remove:", st.session_state.df["Items"])
    if st.button("Remove Item"):
        if remove_item:
            st.session_state.df = st.session_state.df[st.session_state.df["Items"] != remove_item].reset_index(drop=True)
            st.success(f"Removed item: {remove_item}")
        else:
            st.warning("Please select an item to remove.")


st.write("### Edit Items")

# Input field to add a new item
new_item = st.text_input("Add a new item:")

# Button to add the new item
if st.button("Add Item"):
    if new_item:
        st.session_state.df = st.session_state.df.append({"Items": new_item}, ignore_index=True)
        st.success(f"Added item: {new_item}")
    else:
        st.warning("Please enter an item name to add.")

# Display the DataFrame with an option to remove items

