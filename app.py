import hashlib
import json
import os
import bcrypt
import streamlit as st
import graphviz
from datetime import datetime
import importlib


# File Constants
BLOCKCHAIN_FILE = "blockchain_data.json"
USERS_FILE = "users.json"
WALLETS_FILE = "wallets.json"
TRANSACTIONS_FILE = "transaction_history.json"
MINING_REWARD = 10
DIFFICULTY = 4



  # Flag for showing authentication


# Utility Functions
def load_data(file, default):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return default


def save_data(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)


def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())


def log_transaction(transaction):
    transactions = load_data(TRANSACTIONS_FILE, [])
    transactions.append(transaction)
    save_data(TRANSACTIONS_FILE, transactions)


def update_wallet_balance(sender, receiver, amount):
    wallets = load_data(WALLETS_FILE, {})
    if sender != "Network":
        wallets[sender] = wallets.get(sender, 0) - amount
    wallets[receiver] = wallets.get(receiver, 0) + amount
    save_data(WALLETS_FILE, wallets)


def get_balance(wallet):
    return load_data(WALLETS_FILE, {}).get(wallet, 0)


class Block:
    def __init__(self, index, transactions, previous_hash, difficulty=DIFFICULTY, nonce=0):
        self.index = index
        self.timestamp = datetime.utcnow().isoformat()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.difficulty = difficulty
        self.hash = self.mine_block()

    def compute_hash(self):
        block_content = json.dumps(self.__dict__, sort_keys=True).encode()
        return hashlib.sha256(block_content).hexdigest()

    def mine_block(self):
        while True:
            self.hash = self.compute_hash()
            if self.hash[:self.difficulty] == "0" * self.difficulty:
                return self.hash
            self.nonce += 1


# Blockchain Class
class Blockchain:
    def __init__(self, difficulty=DIFFICULTY):
        self.chain = load_data(BLOCKCHAIN_FILE, [])
        self.transactions = load_data(TRANSACTIONS_FILE, [])
        self.users = load_data(USERS_FILE, {})
        self.wallets = load_data(WALLETS_FILE, {})
        self.difficulty = difficulty
        if not self.chain:
            self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = {
            "index": 0,
            "timestamp": datetime.utcnow().isoformat(),
            "transactions": [{"sender": "Network", "receiver": "Genesis", "amount": 0}],
            "previous_hash": "0" * 64,
            "hash": "0" * 64
        }
        self.chain.append(genesis_block)
        self.save_blockchain()

    def save_blockchain(self):
        save_data(BLOCKCHAIN_FILE, self.chain)

    def validate_chain(self):
        """Check if the blockchain is valid by verifying hashes and links."""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            # Recalculate hash to verify integrity
            recalculated_hash = Block(
                current_block["index"],
                current_block["transactions"],
                current_block["previous_hash"],
                current_block.get("difficulty", self.difficulty),
                current_block.get("nonce", 0)
            ).compute_hash()

            if current_block["hash"] != recalculated_hash:
                return f"❌ Tampering detected at Block {current_block['index']}! Hash mismatch."

            if current_block["previous_hash"] != previous_block["hash"]:
                return f"❌ Tampering detected at Block {current_block['index']}! Previous hash mismatch."

        return "✅ Blockchain is valid"

    def add_block(self, transactions):
        previous_hash = self.chain[-1]["hash"]
        new_block = Block(len(self.chain), transactions, previous_hash, self.difficulty)
        self.chain.append(new_block.__dict__)
        self.save_blockchain()
    def tamper_with_block(self, block_index, new_transactions):
        if block_index < len(self.chain):
            self.chain[block_index]["transactions"] = new_transactions
            self.chain[block_index]["hash"] = hashlib.sha256(json.dumps(self.chain[block_index], sort_keys=True).encode()).hexdigest()
            self.save_blockchain()
            return f"Block {block_index} tampered with!"
        return "Invalid block index!"
    def register_user(self, username, password):
        if username in self.users:
            return "❌ Username already exists!"
        self.users[username] = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        self.wallets[username] = 100
        save_data(USERS_FILE, self.users)
        save_data(WALLETS_FILE, self.wallets)
        return f"✅ Registration successful! {username} starts with 100 coins."

    def authenticate_user(self, username, password):
        return username in self.users and bcrypt.checkpw(password.encode(), self.users[username].encode())

    def add_transaction(self, sender, receiver, amount):
        """Add a transaction to the transaction pool without modifying balances immediately."""
        if sender != "Network" and self.wallets.get(sender, 0) < amount:
            return "⚠️ Insufficient balance!"

        transaction = {
            "sender": sender, "receiver": receiver, "amount": amount,
            "timestamp": datetime.utcnow().isoformat()
        }
    
        self.transactions.append(transaction)  # Store in transaction pool
        save_data(TRANSACTIONS_FILE, self.transactions)
    
        return "✅ Transaction added to pool!"

            
    def adjust_difficulty(self):
        
        
        """Adjust mining difficulty based on the average mining time of the last few blocks."""
        if len(self.chain) < 2:
            return  # No adjustment for genesis block

    # Time difference between the last two blocks
        last_block_time = datetime.fromisoformat(self.chain[-1]["timestamp"])
        prev_block_time = datetime.fromisoformat(self.chain[-2]["timestamp"])
        time_diff = (last_block_time - prev_block_time).total_seconds()

        # Adjust difficulty based on mining speed
        target_time = 10  # Desired block time in seconds
        if time_diff < target_time / 2:
        
            self.difficulty += 1  # Increase difficulty if mining is too fast
        elif time_diff > target_time * 2:
            self.difficulty = max(1, self.difficulty - 1)  # Decrease difficulty


    def mine_block(self, miner):
        """Mine a block using transactions from the pool."""
        if not self.transactions:
            return "⚠️ No transactions available to mine!"

        previous_hash = self.chain[-1]["hash"]
    
        # Include transactions and mining reward
        transactions_to_mine = self.transactions[:]
        transactions_to_mine.append({
            "sender": "Network", "receiver": miner,
            "amount": MINING_REWARD, "timestamp": datetime.utcnow().isoformat()
        })
    
        new_block = Block(len(self.chain), transactions_to_mine, previous_hash, self.difficulty)
        self.chain.append(new_block.__dict__)
        self.save_blockchain()
    
        # Update balances now that the block is confirmed
        for tx in transactions_to_mine:
            self.wallets[tx["sender"]] = self.wallets.get(tx["sender"], 0) - tx["amount"]
            self.wallets[tx["receiver"]] = self.wallets.get(tx["receiver"], 0) + tx["amount"]

        save_data(WALLETS_FILE, self.wallets)
    
    # Clear the transaction pool
        self.transactions = []
        save_data(TRANSACTIONS_FILE, self.transactions)

    # Adjust difficulty dynamically
        self.adjust_difficulty()

        return f"✅ Block Mined! Reward sent to {miner} | New Difficulty: {self.difficulty}"
    def search_transactions(self, query):
        
        """Search transactions by sender or receiver."""
        transactions = load_data(TRANSACTIONS_FILE, [])
        results = [tx for tx in transactions if query.lower() in tx["sender"].lower() or query.lower() in tx["receiver"].lower()]
        return results

    def get_transaction_history(self):
        
        """Retrieve the full transaction history from the blockchain."""
        return load_data(TRANSACTIONS_FILE, [])



blockchain = Blockchain()

st.set_page_config(page_title="Blockchain Dashboard", layout="wide")
# Home Page - Show only if no user is logged in
if "user" not in st.session_state:
    st.session_state["user"] = None

st.title("🌐 Blockchain Social Dashboard")
st.subheader("🔗 Your decentralized hub for secure transactions and blockchain management!")
st.info("🔐 Built for security, transparency, and decentralization!")

st.markdown("### 🔹 **Features**")
col1, col2 = st.columns(2)

with col1:
    st.success("✅ **User Authentication** – Secure login & registration.")
    st.success("✅ **Secure Transactions** – Send and receive digital assets.")
    st.success("✅ **Mining & Rewards** – Earn coins by mining blocks.")

with col2:
    st.success("✅ **Blockchain Visualization** – Explore an interactive blockchain network.")
    st.success("✅ **Tamper Detection** – Verify blockchain integrity anytime.")

# Sidebar Authentication
st.sidebar.header("🔑 Authentication")

# Initialize session state for user if not already set
if "user" not in st.session_state:
    st.session_state["user"] = None  

# Switch between Login, Register, and Logout
if st.session_state["user"]:
    auth_option = st.sidebar.radio("Select an option:", ["Logout"], index=0)
else:
    auth_option = st.sidebar.radio("Select an option:", ["Login", "Register"], index=0)

if auth_option == "Login":
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        if blockchain.authenticate_user(username, password):
            st.session_state["user"] = username
            st.sidebar.success(f"✅ Logged in as {username}")
            st.rerun()  # Refresh UI after login
        else:
            st.sidebar.error("❌ Invalid username or password!")

elif auth_option == "Register":
    new_username = st.sidebar.text_input("New Username")
    new_password = st.sidebar.text_input("New Password", type="password")

    if st.sidebar.button("Register"):
        if new_username and new_password:
            message = blockchain.register_user(new_username, new_password)
            st.sidebar.success(message)
        else:
            st.sidebar.error("❌ Please enter a username and password!")
if st.session_state["user"]:
    balance = get_balance(st.session_state["user"])
    st.sidebar.info(f"💰 Your Balance: {balance} Coins")


if st.session_state["user"]:
    st.sidebar.header("📤 Send Coins")
    
    receiver = st.sidebar.text_input("Receiver:")
    amount = st.sidebar.number_input("Amount:", min_value=1, step=1)

    if st.sidebar.button("Send"):
        if receiver and amount > 0:
            message = blockchain.add_transaction(st.session_state["user"], receiver, amount)
            st.sidebar.success(message)
        else:
            st.sidebar.error("❌ Please enter a valid receiver and amount!")
    
    if st.sidebar.button("Mine"):
        st.sidebar.success(blockchain.mine_block(st.session_state["user"]))
else:
    st.sidebar.warning("⚠️ Please log in to send transactions or mine blocks.")



if st.session_state["user"]:
    st.sidebar.markdown("---")  # Divider for UI clarity
    

# Ensure show_explorer is always defined
show_explorer = False  # Default value


if st.session_state["user"]:
    show_explorer = st.sidebar.toggle("🔎 Blockchain Explorer", value=True)

if show_explorer:
    st.sidebar.header("⚡ Blockchain Actions")

    option = st.sidebar.radio("Choose an option:", 
                     ["View Blockchain", "Search Transactions", "Transaction History", "Check Blockchain Integrity","Tamper with Blockchain"],
                     index=0)

    # Function to Display Blockchain Graph
    def display_blockchain():
        st.header("🔗 Blockchain Visualization")
        dot = graphviz.Digraph()
        for block in blockchain.chain:
            dot.node(str(block["index"]), f'Block {block["index"]}\nHash: {block["hash"][:10]}...')
        for i in range(1, len(blockchain.chain)):
            dot.edge(str(blockchain.chain[i-1]["index"]), str(blockchain.chain[i]["index"]))
        st.graphviz_chart(dot)

    # View Blockchain
    if option == "View Blockchain":
        display_blockchain()

    # Search Transactions
    elif option == "Search Transactions":
        st.header("🔍 Search Transactions")
        query = st.text_input("Enter Sender or Receiver:")
        if st.button("Search"):
            results = blockchain.search_transactions(query)
            if results:
                st.dataframe(results)  # Display as table for better UI
            else:
                st.warning("No transactions found!")

    # Transaction History
    elif option == "Transaction History":
        st.header("📜 Transaction History")
        transactions = blockchain.get_transaction_history()  # Assume this method exists
        if transactions:
            for tx in transactions:
                st.write(f'**{tx["sender"]} → {tx["receiver"]}** | 💰 {tx["amount"]} coins | 🕒 {tx["timestamp"]}')
        else:
            st.info("No transactions recorded yet.")

    # Blockchain Integrity Check
    elif option == "Check Blockchain Integrity":
        st.header("✅ Blockchain Integrity Check")
        valid = blockchain.validate_chain()
        st.success("✅ Blockchain is valid" if valid else "❌ Blockchain is tampered!")

        if st.sidebar.button("Visualize Blockchain"):
            display_blockchain()
    elif option == "Tamper with Blockchain":
        st.header("⚠️ Tamper with Blockchain")
        
        block_index = st.number_input("Enter Block Index to Tamper:", min_value=0, max_value=len(blockchain.chain)-1, step=1)
        new_transactions = st.text_area("Enter New Transactions (JSON Format):")
        if st.button("Tamper Block"):
            try:
                new_transactions = json.loads(new_transactions)
                result = blockchain.tamper_with_block(block_index, new_transactions)
                st.warning(result)
            except json.JSONDecodeError:
                st.error("Invalid JSON format!")

# Logout Section (Always Visible)
if "user" in st.session_state and st.session_state["user"]:
    st.sidebar.markdown("---")  # Divider line
    if st.sidebar.button("Logout"):
        st.session_state["user"] = None
        st.rerun()
 