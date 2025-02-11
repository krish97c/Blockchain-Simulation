import streamlit as st
import json
import os

TRANSACTIONS_FILE = "transaction_history.json"

def load_data(file, default):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return default

st.set_page_config(page_title="Transaction History", layout="wide")
st.title("📑 Full Transaction History")

transactions = load_data(TRANSACTIONS_FILE, [])

if transactions:
    for txn in reversed(transactions):  # Show latest transactions first
        st.write(f"🔹 **{txn['sender']}** sent **{txn['amount']} coins** to **{txn['receiver']}**")
        st.caption(f"🕒 {txn['timestamp']}")
else:
    st.info("No transactions found.")
