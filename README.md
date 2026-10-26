# 🏛️ Heritage Hub - AI-Powered Heritage Object Recognition System

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-2.0%2B-black?style=for-the-badge&logo=flask)
![MySQL](https://img.shields.io/badge/MySQL-8.0-orange?style=for-the-badge&logo=mysql)
![Groq](https://img.shields.io/badge/AI-Groq_%7C_Llama_3-red?style=for-the-badge)

**Heritage Hub** is an advanced, AI-driven web application designed to identify, analyze, and preserve the history of ancient artifacts, monuments, and heritage objects. Built with Python (Flask), MySQL, and Groq API (Qwen/Llama Vision), it provides a seamless, ChatGPT-like experience for history enthusiasts, archaeologists, and researchers.

---

## 📖 Table of Contents
- [Key Features](#-key-features)
- [Core Modules](#-our-core-modules)
- [Tech Stack](#-tech-stack)
- [Installation & Setup](#-installation--setup)
- [Database Schema](#-database-schema)
- [Admin Panel Features](#-admin-panel-features)
- [Project Structure](#-project-structure)

---

## ✨ Key Features

- **AI Image Analysis:** Upload any heritage object and get detailed, museum-quality research reports instantly.
- **Ultra-Detailed Reports (10-12 Paragraphs):** AI generates deep insights including historical context, creator details, inscriptions translation, and current status.
- **Smart Auto-Title Generation:** Chats automatically name themselves based on the image (e.g., "Shivaji Rajmudra").
- **PDF Export:** Download beautifully formatted research reports as PDF documents.
- **Chat History:** All conversations are securely saved in MySQL and easily accessible from the sidebar.
- **Voice Input:** Speak your queries using the built-in microphone feature.
- **Dark/Light Theme:** Toggle between themes for a comfortable viewing experience.
- **Role-Based Access:** Separate interfaces for normal Users and Admins.

---

## 🧩 Our Core Modules

After every AI analysis, Heritage Hub provides 6 specialized interactive modules to dive deeper:

| Module | Description |
| :--- | :--- |
| 🔍 **HeritageCheck** | Instant site verification and artifact authentication using advanced AI. |
| 🗺️ **Heritage Origin Finder** | Trace the cultural roots and geographical origins of any ancient object. |
| 🕰️ **Heritage Time Travel Map** | Visualize the journey of an artifact across different historical eras. |
| 🕸️ **Heritage Connection Graph** | Discover how different heritage sites and historical figures are linked. |
| 📊 **Preservation Dashboard** | Track and analyze the condition and preservation needs of artifacts. |
| 🛍️ **Customize Product** | Design and order customized heritage-inspired merchandise securely. |

---

## 🛠️ Tech Stack

**Frontend:**
- HTML5, CSS3, JavaScript (Vanilla)
- Chart.js (For interactive data visualization)
- FontAwesome (Icons)
- Marked.js (Markdown parsing)

**Backend:**
- Python 3.x
- Flask (Web Framework)
- MySQL (Relational Database)
- Groq API (LLM for Vision & Text)
- `xhtml2pdf` (For generating beautiful PDFs)

---

## ⚙️ Installation & Setup

Follow these steps to run the project on your local machine:

### 1. Clone the Repository
```bash
git clone https://github.com/ShrutikaShingane/HeritageHub.git
cd HeritageHub
2. Create Virtual Environment & Install Dependencies
bash
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
3. Environment Variables (.env)
Create a .env file in the root directory and add your credentials:

env
GROQ_API_KEY=your_groq_api_key_here
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=heritage_hub
4. Run the Application
bash
python app.py
Open your browser and navigate to http://127.0.0.1:5000

🗄️ Database Schema
Open your MySQL command line and run the following commands:

sql
CREATE DATABASE heritage_hub;
USE heritage_hub;

-- Users Table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('user', 'admin') DEFAULT 'user',
    is_blocked BOOLEAN DEFAULT FALSE,
    profile_pic LONGTEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Chats Table
CREATE TABLE chats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(255) DEFAULT 'New Chat',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Messages Table
CREATE TABLE messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    chat_id INT NOT NULL,
    sender ENUM('user', 'ai') NOT NULL,
    content TEXT,
    image_path LONGTEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chat_id) REFERENCES chats(id) ON DELETE CASCADE
);

-- Site Content Table
CREATE TABLE site_content (
    id INT PRIMARY KEY DEFAULT 1,
    about_us TEXT,
    contact_us TEXT
);

INSERT INTO site_content (id, about_us, contact_us) VALUES (1, 'Welcome to Heritage Hub.', 'support@heritagehub.com');
🛡️ Admin Panel Features
Heritage Hub comes with a powerful Admin Panel (/admin) providing full control over the platform:

Dashboard Analytics: Real-time graphs of user registrations and image analyses.

User Management: Search, filter, block/unblock, and promote users to Admins.

Global Chat History: View what users are searching and analyzing.

Content Editor: Dynamically update the "About Us" and "Contact Us" sections on the landing page without touching the code.

📁 Project Structure
text
HeritageHub/
│
├── static/
│   ├── css/          # Styling (dashboard, auth, style)
│   └── images/       # Background images & UI assets
│
├── templates/
│   ├── index.html    # Landing Page
│   ├── auth.html     # Login/Signup UI
│   ├── dashboard.html# User Chat Interface
│   ├── profile.html  # User Profile
│   └── admin.html    # Admin Panel UI
│
├── app.py            # Main Flask Application & Routes
├── auth.py           # Authentication Logic (Blueprint)
├── database.py       # MySQL Connection
├── requirements.txt  # Dependencies
├── .env              # Environment variables
└── README.md         # Project Documentation
🚀 Future Scope
Multi-Language Support: Adding Hindi, Marathi, and Sanskrit translations for AI responses.

3D Model Generation: Using AI to convert 2D images of monuments into 3D viewable models.

Community Contribution: Allowing verified users to upload historical data to a public database.

Offline Mode: Integrating a local LLM (like Llama 3 via Ollama) for offline heritage analysis.
