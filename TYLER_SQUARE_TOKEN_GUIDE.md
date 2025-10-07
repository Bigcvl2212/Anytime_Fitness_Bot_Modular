# How to Get Your Square Access Token
## Simple 5-Minute Guide for Tyler

---

## ❓ Why do I need a "token" instead of just my password?

**Short answer:** Square requires it for security. Your password stays private, and the token can be deleted if needed without changing your password.

**Think of it like:** Your password is the key to your house. The token is a temporary key card you give to the cleaning service - it works, but can be turned off anytime without changing your house key.

---

## 📝 Step-by-Step Instructions

### **Step 1: Open Square Developer Portal**

1. Click this link: **https://developer.squareup.com/apps**
2. Log in with your **normal Square email and password**
   - (The same one you use every day for Square)
3. If it asks for permission, click **"Allow"**

---

### **Step 2: Create an App (One-Time Setup)**

**First time only:**

1. You'll see a page that might be empty or have some apps
2. Click the **"+ Create App"** button (big blue button)
3. Give it a name: **"Gym Bot"** (or anything you want)
4. Click **"Save"**

**If you already have an app:**
- Just click on it to open it

---

### **Step 3: Get Your Access Token**

1. On the left side menu, click **"Credentials"**
2. You'll see two sections:
   - ❌ Sandbox (ignore this)
   - ✅ **Production** (this is what you want!)

3. In the **Production** section, find **"Access Token"**
   - It will be hidden (shows dots: •••••••)

4. Click the **"Show"** button next to it
   - A long code will appear (starts with "EAA...")
   - It's about 60 characters long

5. **Copy the entire thing:**
   - Triple-click on it to select all
   - Press `Ctrl+C` (Windows) or `Cmd+C` (Mac)

6. Paste it into the **"Square Access Token"** field in the gym bot app

---

### **Step 4: Get Your Location ID**

1. Still on the same **"Credentials"** page, scroll down a little
2. Find **"Location ID"** (also in the Production section)
3. It looks like: `L1234ABCD5678`
4. **Copy it** and paste into the **"Square Location ID"** field

---

## ✅ You're Done!

Now click **"Save Credentials"** in the gym bot app and you're all set!

---

## 🆘 Troubleshooting

### "I don't see Production, only Sandbox"
- Your Square account might not be activated for production yet
- Contact Square support: **1-855-700-6000**
- Or use Sandbox token for testing (won't work with real money though)

### "I can't find the Credentials page"
- Make sure you clicked on your app name first
- Look for "Credentials" in the left sidebar
- Try refreshing the page

### "The token is really long and hard to copy"
- Click "Show" first
- Triple-click on the token to select all of it
- Press Ctrl+C (or Cmd+C on Mac)
- Should start with "EAA" and be about 60 characters

### "It says my token is invalid"
- Make sure you copied the **Production** token, not Sandbox
- Make sure you got the entire thing (no spaces at beginning/end)
- Try clicking "Show" again and re-copy it

---

## 🔒 Security Note

- ✅ Your password is never stored in the gym bot
- ✅ The token only allows the gym bot to access Square
- ✅ You can delete/regenerate the token anytime from the Square Developer portal
- ✅ The token is encrypted when saved

---

## 📞 Need More Help?

**Contact Mayo (the developer):**
- He can walk you through it
- Takes 2-3 minutes on a screen share

**Or watch Square's video:**
- https://developer.squareup.com/docs/devtools/credentials

---

## 🎯 Quick Reference Card

**When Tyler asks: "What do I need?"**

Tell him:
1. Go to: developer.squareup.com/apps
2. Log in with normal Square login
3. Create app called "Gym Bot"
4. Click "Credentials" → Copy "Production Access Token"
5. Copy "Production Location ID"
6. Paste both into gym bot app → Save

**Time: 2-3 minutes**

---

**Version:** 1.0
**Last Updated:** 2025-10-03
**Print this page and give it to Tyler!** 📄
