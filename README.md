# Sentinel Vault v1.0 🛡️

A secure, local password manager built with Python. This project demonstrates 
advanced cryptographic principles including Key Derivation Functions (KDF) 
and Envelope Encryption.

## 🛠️ Technical Security Features
* **PBKDF2-HMAC-SHA256**: Streches the master password with 480,000 iterations to prevent brute-force attacks.
* **AES-256 (Fernet)**: Industrial-grade symmetric encryption for all stored secrets.
* **Envelope Encryption**: Uses a Master Password to wrap a randomly generated Vault Key, allowing for efficient password changes without re-encrypting the entire database.
* **Salting**: Every vault uses a unique 16-byte random salt to prevent Rainbow Table attacks.
* **Auto-Type Integration**: Safely injects credentials into external applications using a timed delay to prevent clipboard sniffing.

## 🚀 How to Run
1. Install dependencies: `pip install cryptography pynput`
2. Run the application: `python main.py`