#!/usr/bin/env python3
"""Create password-protected zip for John the Ripper challenge"""
import zipfile
import sys

# Password for the zip file - SIMPLE password for easy cracking
PASSWORD = b"hack"

# Create password-protected zip
zip_path = "john_lab.zip"

with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    zipf.write('flag.txt')
    # Set password
    zipf.setpassword(PASSWORD)

print(f"Created {zip_path} with password: {PASSWORD.decode()}")
print("Flag inside: CTF{p4ssw0rd_cr4ck3d_success}")
