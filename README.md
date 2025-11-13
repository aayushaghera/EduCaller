# 🎓 EduCaller – Voice Assistant for Parents

EduCaller is an automated **voice calling system** built using **Flask**, **Twilio**, and **Google Text-to-Speech (gTTS)**.  
It automatically calls parents to inform them about their child's semester results — eliminating the need for manual calls.

---

## 👨‍💻 Team Members

- **Abhay Bathani**
- **Aayush Aghera**

---

## 🧠 Project Overview

In many colleges, staff must manually call parents to share student performance results.  
EduCaller automates this entire process — it reads a **CSV file** containing student details and automatically:

1. Generates personalized **voice messages** using **gTTS**.
2. Calls parents through the **Twilio API**.
3. Plays the generated message when the parent answers the call.

This project saves time, ensures accuracy, and demonstrates practical **AI and cloud communication integration**.

---

## ⚙️ Tech Stack

| Component | Technology Used |
|------------|-----------------|
| **Backend Framework** | Flask |
| **Telephony API** | Twilio |
| **Text-to-Speech** | Google gTTS |
| **Language** | Python 3 |
| **Frontend** | HTML, CSS (Flask Templates) |
| **Data Handling** | Pandas |
| **Environment Management** | python-dotenv |

---

## 🧾 How It Works

1. The user uploads a **CSV file** containing:
   - Student Name  
   - Roll Number  
   - Semester  
   - SPI  
   - Result  
   - Father's Name  
   - Father's Contact Number  

2. Flask reads the CSV file using **Pandas**.

3. For each student record:
   - A personalized text message is created.
   - gTTS converts the message into an **audio file (MP3)**.
   - Twilio calls the parent's number and plays that audio.

4. Logs are displayed on the webpage showing the call progress.

---

## ⚡ Setup Instructions

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/your-username/EduCaller.git
cd EduCaller
```

### 2️⃣ Create and Activate Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Create a `.env` File
Create a `.env` file in the project root with your Twilio credentials:

```env
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1XXXXXXXXXX
```

### 5️⃣ Run the Flask App

```bash
python app.py
```

The application will start on `http://localhost:5000`

---

## 🧩 Example Message

When a parent answers the call, they hear something like:

> "Hello Mr. Sharma, this is an automated call from your child's college. Your son, Rohan Sharma, has completed Semester 5 with an SPI of 8.72 and has successfully passed. Thank you."

---

## 🚀 Features

✅ Automatic voice generation (gTTS)  
✅ Real-time calling via Twilio API  
✅ CSV upload & data parsing  
✅ Simple Flask-based web interface  
✅ Reduces manual work and human error  

---

## 🔒 Environment Variables

| Variable | Description |
|----------|-------------|
| `TWILIO_ACCOUNT_SID` | Your Twilio account SID |
| `TWILIO_AUTH_TOKEN` | Twilio authentication token |
| `TWILIO_PHONE_NUMBER` | Verified Twilio phone number |

---

## 🛠️ Dependencies

```txt
Flask
twilio
pandas
gTTS
python-dotenv
```

---

## 📋 CSV File Format

Your CSV file should have the following columns:

| Student Name | Roll Number | Semester | SPI | Result | Father Name | Father Contact |
|--------------|-------------|----------|-----|--------|-------------|----------------|
| Rohan Sharma | 21CE001 | 5 | 8.72 | Pass | Mr. Sharma | +919876543210 |

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## 📞 Contact

For any queries or suggestions:

- **Aayush Aghera** | 📱 +91 8511663820
- **Abhay Bathani** | 📱 +91 9313837439

---

## ⭐ Show Your Support

If you found this project helpful, please give it a ⭐ on GitHub!

---

**Made with ❤️ by Aayush Aghera & Abhay Bathani**
