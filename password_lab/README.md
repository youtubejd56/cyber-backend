# JohnCrack Lab Setup

## Challenge: Crack the Password!

This is a static challenge - no machine needed. Just download, crack, and get the flag!

### Files

1. **john_lab.zip** - Password-protected ZIP file
2. **hash.txt** - Pre-generated hash for John the Ripper

### How to Solve

**Option 1: Using the ZIP file**

1. Download `john_lab.zip`
2. Extract the hash:
   ```bash
   zip2john john_lab.zip > hash.txt
   ```
3. Crack with John:
   ```bash
   john hash.txt --wordlist=/usr/share/wordlists/rockyou.txt
   ```
4. Password is: `hack`
5. Unzip with password: `unzip -P hack john_lab.zip`
6. Read flag.txt

**Option 2: Using pre-generated hash**

1. Edit hash.txt with the hash from zip2john
2. Run: `john hash.txt --wordlist=/usr/share/wordlists/rockyou.txt`

### Flag

```
CTF{p4ssw0rd_cr4ck3d_success}
```

### To Add to Your Server

Upload `john_lab.zip` to a publicly accessible location and update the `download_url` in the JohnCrack machine settings.
