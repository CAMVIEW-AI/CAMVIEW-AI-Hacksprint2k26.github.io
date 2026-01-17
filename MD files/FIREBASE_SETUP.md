# Firebase Setup Guide for CAMVIEW.AI Traffic Safety System

This guide will walk you through setting up Firebase Firestore to store all traffic safety events from the detection engine.

---

## Step 1: Create a Firebase Project

1. **Go to Firebase Console**  
   Visit: https://console.firebase.google.com/

2. **Sign in** with your Google account

3. **Click "Add project"** or "Create a project"

4. **Enter project name**  
   Example: `camview-traffic-safety`

5. **Disable Google Analytics** (optional, not needed for this project)  
   Click "Continue"

6. **Click "Create Project"**  
   Wait for the project to be created (takes ~30 seconds)

7. **Click "Continue"** when ready

---

## Step 2: Enable Firestore Database

1. **In the Firebase Console**, click **"Build"** → **"Firestore Database"** in the left sidebar

2. **Click "Create database"**

3. **Choose mode:**
   - Select **"Start in production mode"** (we'll set security rules later)
   - Click "Next"

4. **Choose location:**
   - Select a region close to you (e.g., `asia-south1` for India)
   - Click "Enable"

5. **Wait for Firestore to initialize** (~30 seconds)

---

## Step 3: Generate Service Account Key (IMPORTANT)

1. **Click the gear icon** (⚙️) next to "Project Overview" → **"Project settings"**

2. **Go to the "Service accounts" tab**

3. **Click "Generate new private key"** button at the bottom

4. **Click "Generate key"** in the confirmation dialog

5. **A JSON file will download automatically**  
   This file contains your secret credentials!

6. **Rename the file to:**  
   ```
   firebase_service_account.json
   ```

7. **Move the file to your project folder:**  
   ```
   C:\Users\ahadd\OneDrive\Documents\ppt\CAMVIEW.AI\firebase_service_account.json
   ```

   ⚠️ **SECURITY WARNING:**  
   - DO NOT commit this file to Git/GitHub  
   - DO NOT share this file with anyone  
   - Keep it safe – it grants full access to your Firebase project

---

## Step 4: Install Firebase Admin SDK

Open your terminal in the project directory and activate the virtual environment:

```powershell
cd C:\Users\ahadd\OneDrive\Documents\ppt\CAMVIEW.AI
& .venv\Scripts\Activate.ps1
```

Install the Firebase Admin package:

```powershell
pip install firebase-admin
```

---

## Step 5: Verify the Setup

1. **Check that the credentials file exists:**
   ```
   C:\Users\ahadd\OneDrive\Documents\ppt\CAMVIEW.AI\firebase_service_account.json
   ```

2. **Run the detection engine on a test video:**
   ```powershell
   python main.py --source "path\to\your\video.mp4"
   ```

3. **Check the console output** – you should see:
   ```
   [SYSTEM] Logger initialized. Writing to ...
   Firebase initialized successfully
   Firestore client ready. Collection: traffic_safety_events
   ```

4. **Go back to Firebase Console** → **Firestore Database**

5. **You should see a new collection: `traffic_safety_events`**

6. **Click on the collection** – you'll see documents (events) appearing with:
   - Document ID = event UUID
   - Fields: `type`, `severity`, `camera`, `time`, `metadata`, etc.

---

## Step 6: Set Firestore Security Rules (Optional but Recommended)

To prevent unauthorized access:

1. **In Firestore Console**, click the "Rules" tab

2. **Replace the rules with:**
   ```javascript
   rules_version = '2';
   service cloud.firestore {
     match /databases/{database}/documents {
       // Allow server-side writes (from service account)
       match /traffic_safety_events/{document=**} {
         allow read, write: if false;  // No public access
       }
     }
   }
   ```

3. **Click "Publish"**

This ensures only your service account (the detection engine) can write to the database.

---

## Step 7: View Your Events in Firebase Console

1. **Go to Firestore Database** in Firebase Console

2. **Click `traffic_safety_events` collection**

3. **You'll see all events** with fields:
   - `id` – Unique event ID
   - `type` – Event type (WRONG_SIDE, EMERGENCY_VEHICLE, etc.)
   - `severity` – WARNING, CRITICAL, INFO
   - `camera` – Camera ID
   - `time` – Unix timestamp
   - `time_fmt` – Human-readable timestamp
   - `metadata` – Additional details (track_id, frame_id, confidence, etc.)

4. **Filter and search events** using the Firestore query interface

---

## Troubleshooting

### Error: "Firebase credentials not found"
- Make sure `firebase_service_account.json` is in the project root directory
- Check the file path in `config/settings.py`

### Error: "firebase-admin not installed"
- Run: `pip install firebase-admin`

### No events appearing in Firestore
- Check console for Firebase initialization messages
- Make sure the engine is running and detecting events
- Check for error messages in the terminal

### Permission denied errors
- Verify your service account has "Cloud Datastore User" role
- Re-download the service account key if needed

---

## What Happens Now?

✅ **All events are automatically saved to Firestore** in addition to the local `events.jsonl` file

✅ **Streamlit dashboard** continues to work with the local file (no changes needed)

✅ **You can build additional dashboards** that read directly from Firestore (web apps, mobile apps, etc.)

✅ **Data is persistent** and accessible from anywhere with proper authentication

---

## Next Steps (Optional)

1. **Build a web dashboard** that reads from Firestore in real-time
2. **Set up Firebase Cloud Functions** to trigger alerts (email, SMS) on critical events
3. **Export data** for analytics using BigQuery integration
4. **Add authentication** to allow multiple users to view the dashboard

---

## Security Checklist

- [ ] `firebase_service_account.json` is NOT in Git
- [ ] `.gitignore` includes `firebase_service_account.json`
- [ ] Firestore security rules are set to production mode
- [ ] Service account key is stored securely
- [ ] Only authorized personnel have access to Firebase Console

---

## Support

For Firebase documentation:
- https://firebase.google.com/docs/firestore
- https://firebase.google.com/docs/admin/setup

For project-specific issues, check the logs or contact your system administrator.
