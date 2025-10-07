import streamlit as st
from datetime import datetime
import time

# ---------------- Blockchain Class ----------------
class Blockchain:
    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self.balances = {"Bank Network": 1_000_000}
        self.create_genesis_block()

    def create_genesis_block(self):
        self.chain.append({
            "index": 0,
            "timestamp": str(datetime.now()),
            "transactions": [],
            "previous_hash": "0"
        })

    def ensure_user_balance(self, user, default_balance=100):
        if user not in self.balances:
            self.balances[user] = default_balance

    def add_transaction(self, sender, receiver, amount):
        self.ensure_user_balance(sender)
        self.ensure_user_balance(receiver)
        if amount <= 0:
            return False, "Amount must be greater than 0."
        if sender != "Bank Network" and self.balances[sender] < amount:
            return False, f"{sender} has insufficient balance."
        if sender != "Bank Network":
            self.balances[sender] -= amount
        self.balances[receiver] += amount
        self.pending_transactions.append({
            "sender": sender,
            "receiver": receiver,
            "amount": amount
        })
        return True, f"{sender} → {receiver}: {amount} coins"

    def mine_block(self, miner_name):
        self.ensure_user_balance(miner_name)
        block = {
            "index": len(self.chain),
            "timestamp": str(datetime.now()),
            "transactions": self.pending_transactions.copy(),
            "previous_hash": str(len(self.chain) - 1)
        }
        self.chain.append(block)
        self.pending_transactions = []
        reward_amount = 10
        self.balances[miner_name] += reward_amount
        return block, f"Block mined by {miner_name}, reward: {reward_amount} coins"

# ---------------- Streamlit Setup ----------------
st.set_page_config(page_title="Bank Blockchain Simulator", layout="wide")

# ---------------- Bank Theme CSS ----------------
st.markdown("""
<style>
body {background-color: #1e293b; color: #f3f4f6; font-family: 'Helvetica', sans-serif;}
h1,h2,h3 {color: #fbbf24;}
.stButton>button {background-color:#fbbf24; color:#1e293b; font-weight:bold; border-radius:5px; padding:0.35em 0.75em; margin-top:5px;}
.stTextInput>div>div>input, .stNumberInput>div>div>input {background-color:#374151; color:#f3f4f6; border-radius:5px; padding:0.5em;}
.card {background-color:#1f2937; padding:15px; border-radius:10px; box-shadow: 0 4px 12px rgba(0,0,0,0.3); margin-bottom:10px; word-wrap: break-word;}
.kpi-card {background-color:#111827; padding:15px; border-radius:10px; margin-bottom:10px; text-align:center;}
@media only screen and (max-width: 768px) {
    .stColumns {flex-direction: column !important;}
    .stButton>button {width: 100% !important;}
}
</style>
""", unsafe_allow_html=True)

# ---------------- Initialize Blockchain ----------------
if "blockchain" not in st.session_state:
    st.session_state.blockchain = Blockchain()
blockchain = st.session_state.blockchain

# ---------------- Header ----------------
st.markdown("<h1 style='text-align:center;'>🏦 Bank Blockchain Simulator</h1>", unsafe_allow_html=True)
st.markdown("<hr style='border-color:#374151'>", unsafe_allow_html=True)

# ---------------- KPI Panel ----------------
col1, col2, col3, col4 = st.columns(4)
col1.markdown(f"<div class='kpi-card'><h3>Total Accounts</h3><h2>{len(blockchain.balances)}</h2></div>", unsafe_allow_html=True)
col2.markdown(f"<div class='kpi-card'><h3>Total Coins</h3><h2>{sum(blockchain.balances.values()):,.2f}</h2></div>", unsafe_allow_html=True)
col3.markdown(f"<div class='kpi-card'><h3>Pending Transactions</h3><h2>{len(blockchain.pending_transactions)}</h2></div>", unsafe_allow_html=True)
col4.markdown(f"<div class='kpi-card'><h3>Last Block</h3><h2>{blockchain.chain[-1]['index']}</h2></div>", unsafe_allow_html=True)

st.markdown("<hr style='border-color:#374151'>", unsafe_allow_html=True)

# ---------------- Main Dashboard Layout ----------------
# Use responsive columns
left_col, right_col = st.columns([1,1.5])

# ---------- Left Column: Actions ----------
with left_col:
    st.markdown("<h2>💳 New Transaction</h2>", unsafe_allow_html=True)
    sender = st.text_input("Sender", key="tx_sender")
    receiver = st.text_input("Receiver", key="tx_receiver")
    amount = st.number_input("Amount", min_value=0.0, step=0.01, key="tx_amount")
    if st.button("Submit Transaction"):
        success, msg = blockchain.add_transaction(sender, receiver, amount)
        st.markdown(f"<div class='card' style='color:{'#10b981' if success else '#ef4444'}'>{msg}</div>", unsafe_allow_html=True)

    st.markdown("<h2>⛏️ Mine Block</h2>", unsafe_allow_html=True)
    miner_name = st.text_input("Miner Name", value="Bank Network", key="miner_name")
    
    if st.button("Start Mining"):
        progress_text = f"⛏️ Mining block by {miner_name}..."
        progress_bar = st.progress(0, text=progress_text)
        for percent_complete in range(101):
            time.sleep(0.03)
            progress_bar.progress(percent_complete, text=progress_text)
        block, msg = blockchain.mine_block(miner_name)
        st.markdown(f"<div class='card' style='color:#10b981'>{msg}</div>", unsafe_allow_html=True)

# ---------- Right Column: Accounts & Pending ----------
with right_col:
    st.markdown("<h2>👥 Account Balances</h2>", unsafe_allow_html=True)
    balances = blockchain.balances
    for user, bal in balances.items():
        st.markdown(f"<div class='card'><b>{user}</b><br>💰 {bal:.2f} coins</div>", unsafe_allow_html=True)

    st.markdown("<h2>📄 Pending Transactions</h2>", unsafe_allow_html=True)
    if blockchain.pending_transactions:
        for tx in blockchain.pending_transactions:
            st.markdown(f"<div class='card'>{tx['sender']} → {tx['receiver']} : {tx['amount']} coins</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='card'>No pending transactions</div>", unsafe_allow_html=True)

# ---------------- Blockchain Overview ----------------
st.markdown("<h2>📦 Blockchain Overview</h2>", unsafe_allow_html=True)
for idx, block in enumerate(blockchain.chain):
    bg_color = "#374151" if idx % 2 == 0 else "#1f2937"
    st.markdown(f"<div class='card' style='background-color:{bg_color}'>"
                f"<b>Block #{block['index']}</b><br>"
                f"Timestamp: {block['timestamp']}<br>"
                f"Previous Hash: {block['previous_hash']}<br><b>Transactions:</b></div>", unsafe_allow_html=True)
    if block['transactions']:
        for tx in block['transactions']:
            st.markdown(f"<div class='card' style='padding:5px; margin-bottom:3px;'>{tx['sender']} → {tx['receiver']} : {tx['amount']} coins</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='card'>No transactions</div>", unsafe_allow_html=True)
