import streamlit_authenticator as stauth

passwords = ["teacher123", "admin123"]
hashed_passwords = stauth.Hasher(passwords).generate()

print(hashed_passwords)