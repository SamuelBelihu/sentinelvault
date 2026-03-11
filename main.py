import json
import os
import getpass
import base64
import string
from cryptography.fernet import InvalidToken
from vault_engine import get_key, encrypt_data, decrypt_data, generate_vault_key
import time
from pynput import keyboard

kb_controller = keyboard.Controller()
VAULT_FILE = "vault.json"

def load_vault_data():
    """Loads the vault or returns a clean structure if it doesn't exist."""
    if os.path.exists(VAULT_FILE):
        with open(VAULT_FILE, "r") as f:
            return json.load(f)
    return {"header": {}, "entries": {}}

def save_vault_data(data):
    """Saves the entire vault structure to disk."""
    with open(VAULT_FILE, "w") as f:
        json.dump(data, f, indent=4)

def change_master_password(data, current_vault_key):
    """Re-encrypts the Vault Key with a NEW Master Password and a NEW Salt."""
    print("\n--- Master Password Change ---")
    new_pwd = get_new_password()
    confirm_pwd = getpass.getpass("Confirm NEW Master Password: ")

    if new_pwd != confirm_pwd:
        print("Passwords do not match. Change aborted.")
        return data

    # Generate a new random salt for the new password
    new_salt = base64.b64encode(os.urandom(16)).decode()
    new_master_kdf_key = get_key(new_pwd, new_salt.encode())

    # Re-wrap the vault key
    data["header"]["salt"] = new_salt
    data["header"]["encrypted_vault_key"] = encrypt_data(current_vault_key.decode(), new_master_kdf_key)
    
    print("Master Password and Salt updated successfully!")
    return data

def clear_screen():
    # Use 'cls' for Windows CMD/PowerShell, 'clear' for Git Bash/Linux
    os.system('cls' if os.name == 'nt' else 'clear')

def get_new_password():
    """Check the criteria for a new password"""
    while True:
        score = 0
        feedback = []
        master_pwd = getpass.getpass("Create a new Master Password: ")
        #length of the password 
        if len(master_pwd) >= 8 and len(master_pwd) <= 30: score += 1
        else: feedback.append("Password must be at least 8 characters")
        #mixed case
        if any(c.isupper() for c in master_pwd) and any(c.islower() for c in master_pwd): score += 1
        else: feedback.append("use both Upper and lower case.")
        if any(c.isdigit() for c in master_pwd): score += 1
        else: feedback.append("Add at least one number.")
        if any(c in string.punctuation for c in master_pwd): score += 1
        else: feedback.append("Add a special character (e.g ., !, @, #).")
        
        if score == 4:
            return master_pwd
        else:
            for suggestion in feedback:
                print("-->"+ suggestion) 
def execute_outtype(password, app_name, delay=10):
    print(f"Switch to {app_name} now! Typing in {delay} seconds...") 
    # Visual countdown
    for i in range(delay, 0, -1):
        print(f"{i}... ", end="\r")
        time.sleep(1)
        
    print("\nTyping now...")
    kb_controller.type(password)
    print("Done.")
def main():
    print("\n" + "="*30 + "\n  SENTINEL Vault v1.0\n" + "="*30)
    
    data = load_vault_data()
    # --- INITIALIZATION OR UNLOCK ---
    if not data["header"]:
        master_pwd = get_new_password()
        print("Initializing New Vault...")
        # Generate initial random salt and vault key
        salt = base64.b64encode(os.urandom(16)).decode()
        vault_key = generate_vault_key()
        
        # Derive Master Key using the new salt
        master_kdf_key = get_key(master_pwd, salt.encode())
        
        # Store in header
        data["header"]["salt"] = salt
        data["header"]["encrypted_vault_key"] = encrypt_data(vault_key.decode(), master_kdf_key)
        save_vault_data(data)
    else:
        master_pwd = getpass.getpass("Master Password: ")
        try:
            # Pull the unique salt from the file to derive the key
            salt = data["header"]["salt"].encode()
            master_kdf_key = get_key(master_pwd, salt)
            
            # Unlock the "Envelope" (the Vault Key)
            encrypted_vk = data["header"]["encrypted_vault_key"]
            vault_key = decrypt_data(encrypted_vk, master_kdf_key).encode()
            print("Vault Unlocked.")
        except (InvalidToken, KeyError):
            print("Access Denied: Incorrect Master Password.")
            return

    while True:
        print("\n[1] Add  [2] View  [3] Delete  [4] Change Master Pwd  [5] Exit")
        choice = input("Sentinel> ")

        if choice == "1":
            app = input("App Name: ")
            user = input("Username: ")
            while True:
                password = getpass.getpass(f"Password for {app}: ")
                if password:
                    break
                else:
                    print("Password cannot to empty")
            # Save as a dict for better organization
            encrypted_entry = {
                "user": user,
                "secret": encrypt_data(password, vault_key)
            }
            data["entries"][app] = encrypted_entry
            save_vault_data(data)
            print(f"{app} secured.")

        elif choice == "2":
            query = input("Search App: ")
            found = False
            for app, info in data["entries"].items():
                if query.lower() in app.lower():
                    # Check if entry is old format or new dict format
                    secret = info["secret"] if isinstance(info, dict) else info
                    user = info.get("user", "N/A") if isinstance(info, dict) else "N/A"
                    
                    decrypted = decrypt_data(secret, vault_key)
                    print(f"\n--- {app} ---\nUser: {user}")
                    execute_outtype(decrypted,app)
                    found = True
            if not found: print("No matches.")

        elif choice == "3":
            target = input("App to Delete: ")
            if data["entries"].pop(target, None):
                save_vault_data(data)
                print(f"{target} removed.")
            else:
                print("Not found.")

        elif choice == "4":
            data = change_master_password(data, vault_key)
            save_vault_data(data)

        elif choice == "5":
            clear_screen()
            print("Vault Sealed. Goodbye.")
            break

if __name__ == "__main__":
    main()