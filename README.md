# 🏆 Blockchain-Based Application

This is a **Blockchain-based system** built with **Python & Streamlit**, designed for **secure transactions, mining, and blockchain exploration**. The application is **Dockerized**, making it easy to deploy and run in a containerized environment.

---

## 🚀 Features
✔ **User Authentication** – Secure login & registration using `bcrypt`.  
✔ **Transactions & Wallets** – Send and receive digital assets.  
✔ **Mining & Rewards** – Earn coins by mining blocks.  
✔ **Blockchain Explorer** – Visualize blocks and transactions.  
✔ **Tamper Detection** – Validate blockchain integrity.  
✔ **Dockerized** – Easily deployable with **Docker**.  

---

## 🛠️ Installation & Setup

### **1️⃣ Clone the Repository**
```bash
git clone https://github.com/yourusername/blockchain-app.git
cd blockchain-app
pip install -r requirements.txt
streamlit run app.py

🐳 Running with Docker
1️⃣ Build the Docker Image
docker build -t blockchain-app .
2️⃣ Run the Docker Container
docker run -p 8501:8501 blockchain-app
Now visit http://localhost:8501 to access the app
📂 Project Structure
/blockchain-app
│
├── app.py               # Main Streamlit app
├── blockchain_data.json # Blockchain data storage
├── wallets.json         # Wallet balance storage
├── transaction_history.json # Transaction history
├── Dockerfile           # Dockerfile for containerization
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
🧠 Algorithms & Technologies Used:
🔹 SHA-256 Hashing – Used to link blocks securely in the blockchain.
🔹 Proof-of-Work (PoW) Algorithm – Implements computational mining for block validation.
🔹 Dynamic Difficulty Adjustment – Adjusts mining difficulty based on block time.
🔹 Bcrypt Password Hashing – Secure user authentication.
🔹 Tamper Detection Algorithm – Recomputes and verifies block hashes.
🔹 Graphviz Visualization – Provides an interactive blockchain explorer.
🔹 Dockerized System – Runs in isolated, portable containers for scalability.
