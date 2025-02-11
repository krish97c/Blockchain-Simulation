import streamlit as st
from block import blockchain  # Import blockchain instance

st.title("🔗 Blockchain Explorer")
st.write("Browse blocks and transactions.")

for block in blockchain.chain:
    st.subheader(f"Block {block['index']}")
    st.json(block)
