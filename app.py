# app.py - Tạo token Polygon chỉ 1 click - Python tinh gọn
import streamlit as st
from web3 import Web3
import solcx
import json
import os

# --- Cấu hình ---
st.set_page_config(page_title="Tạo Token Polygon", layout="centered")
st.markdown("<h1 style='text-align:center'>Tạo Token ERC20 trên Polygon</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#aaa'>Không code • 3 giây • Phí ~0.0001 MATIC</p>", unsafe_allow_html=True)

# RPC Polygon
RPC = "https://polygon-rpc.com"
w3 = Web3(Web3.HTTPProvider(RPC))

# Contract source
CONTRACT_SOURCE = '''
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract MyToken is ERC20, ERC20Burnable, Ownable {
    constructor(string memory name_, string memory symbol_, uint256 supply_, address owner_) ERC20(name_, symbol_) {
        _mint(owner_, supply_ * 10 ** decimals());
    }
}
'''

# Cache compile
@st.cache_resource
def compile_contract():
    solcx.install_solc('0.8.20')
    compiled = solcx.compile_source(
        CONTRACT_SOURCE,
        output_values=['abi', 'bin'],
        import_remappings={'@openzeppelin=': 'https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/'}
    )
    abi = compiled['<stdin>:MyToken']['abi']
    bytecode = compiled['<stdin>:MyToken']['bin']
    return abi, bytecode

abi, bytecode = compile_contract()

# --- Giao diện ---
col1, col2, col3 = st.columns([1,2,1])
with col2:
    name = st.text_input("Tên token", "My Coin")
    symbol = st.text_input("Ký hiệu", "MC")
    supply = st.number_input("Tổng cung", min_value=1, value=1000000)
    
    if st.button("Connect Wallet & Tạo Token", type="primary", use_container_width=True):
        if not name or not symbol:
            st.error("Điền tên và ký hiệu!")
        else:
            with st.spinner("Đang tạo transaction..."):
                # Tạo data deploy
                encoded = w3.codec.encode(
                    ['string', 'string', 'uint256', 'address'],
                    [name, symbol, supply, "0x000000000000000000000000000000000000dEaD"]  # placeholder
                ).hex()
                
                tx = {
                    "to": None,
                    "data": "0x" + bytecode + encoded[130:],  # cắt 130 ký tự đầu của encoded
                    "gas": 3000000,
                    "gasPrice": w3.to_wei(50, 'gwei'),
                    "chainId": 137
                }
                
                st.session_state.tx = tx
                st.session_state.abi = abi
                st.success("Sẵn sàng! Dán đoạn này vào MetaMask → Send Transaction")

# --- Hiển thị TX để gửi ---
if 'tx' in st.session_state:
    st.code(json.dumps(st.session_state.tx, indent=2), language="json")
    st.markdown(f"[Xem ABI](data:application/json, {json.dumps(st.session_state.abi)})")

    st.markdown("""
    ### Hướng dẫn:
    1. Mở MetaMask → Import Transaction  
    2. Dán đoạn JSON trên vào  
    3. Đổi `to` thành địa chỉ của bạn  
    4. Send → Xong!
    """)
