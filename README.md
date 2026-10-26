🏛️ Heritage Hub - AI-Powered Heritage Object Recognition System
Heritage Hub is an advanced, AI-driven web application designed to identify, analyze, and preserve the history of ancient artifacts, monuments, and heritage objects. Built with Python (Flask), MySQL, and Groq (Llama 3 Vision), it provides a seamless, ChatGPT-like experience for history enthusiasts, archaeologists, and researchers.

🚀 Features
AI Image Analysis: Upload any heritage object (coins, statues, inscriptions) and get detailed, museum-quality research reports.

Ultra-Detailed Reports: AI generates 10-12 paragraph long responses, including historical context, creator details, inscriptions translation, and current status.

Smart Auto-Title Generation: Chats automatically name themselves based on the uploaded image (e.g., "Shivaji Rajmudra").

Chat History & Persistence: All conversations are securely saved in MySQL and can be accessed from the sidebar.

PDF Export: Download your research reports as beautifully formatted PDF documents.

Voice Input: Speak your queries using the built-in microphone feature.

Dark/Light Theme: Toggle between themes for a comfortable viewing experience.

Role-Based Access Control: Separate dashboards for normal Users and Admins.

🧩 Our Core Modules (6 Features)
Heritage Hub provides 6 specialized interactive modules generated after every AI analysis. These modules help users dive deeper into the historical context:

🔍 HeritageCheck (Site Verification): Instant site verification and artifact authentication using advanced AI.

🗺️ Heritage Origin Finder (Cultural Tracing): Trace the cultural roots and geographical origins of any ancient object.

🕰️ Heritage Time Travel Map (Visualization): Visualize the journey of an artifact across different historical eras.

🕸️ Heritage Connection Graph (Network Analysis): Discover how different heritage sites and historical figures are linked.

📊 Preservation Dashboard (Analytics): Track and analyze the condition and preservation needs of artifacts.

🛍️ Customize a Heritage Product (Monetization): Design and order customized heritage-inspired merchandise securely.

🛠️ Tech Stack
Frontend: HTML5, CSS3, Vanilla JavaScript, Chart.js

Backend: Python 3.x, Flask

Database: MySQL

AI Engine: Groq API (using qwen/qwen3.8-27b for Vision and Text)

PDF Generation: xhtml2pdf

Image Processing: Pillow (PIL)

⚙️ Installation & Setup
Follow these steps to run the project locally:

1. Clone the Repository
bash
git clone https://github.com/your-username/HeritageHub.git
cd HeritageHub
2. Set Up Virtual Environment & Install Dependencies
bash
python -m venv venv
# Activate venv (Windows)
venv\Scripts\activate
# Activate venv (Mac/Linux)
source venv/bin/activate

pip install -r requirements.txt
(Dependencies include: flask, mysql-connector-python, groq, python-dotenv, pillow, xhtml2pdf, fpdf)

3. Database Setup (MySQL)
Open your MySQL command line and run the following commands:

sql
CREATE DATABASE heritage_hub;
USE heritage_hub;

-- Create Users Table
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

-- Create Chats Table
CREATE TABLE chats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(255) DEFAULT 'New Chat',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create Messages Table
CREATE TABLE messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    chat_id INT NOT NULL,
    sender ENUM('user', 'ai') NOT NULL,
    content TEXT,
    image_path LONGTEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chat_id) REFERENCES chats(id) ON DELETE CASCADE
);

-- Create Site Content Table (For Admin CMS)
CREATE TABLE site_content (
    id INT PRIMARY KEY DEFAULT 1,
    about_us TEXT,
    contact_us TEXT
);

INSERT INTO site_content (id, about_us, contact_us) VALUES (1, 'Welcome to Heritage Hub.', 'support@heritagehub.com');
4. Environment Variables (.env)
Create a .env file in the root directory and add your credentials:

env
GROQ_API_KEY=your_groq_api_key_here
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=heritage_hub
5. Run the Application
bash
python app.py
Open your browser and go to http://127.0.0.1:5000

📁 Project Structure
text
HeritageHub/
│
├── static/
│   ├── css/
│   │   ├── style.css         # Welcome Page Styles
│   │   ├── auth.css          # Login/Signup Styles
│   │   └── dashboard.css     # User & Admin Dashboard Styles
│   └── images/               # Background & UI Images
│
├── templates/
│   ├── index.html            # Welcome/Landing Page
│   ├── auth.html             # Login & Signup Page
│   ├── dashboard.html        # User Chat Interface
│   ├── profile.html          # User Profile Management
│   └── admin.html            # Admin Control Panel
│
├── app.py                    # Main Flask Application & Routes
├── auth.py                   # Authentication Logic (Blueprint)
├── database.py               # MySQL Connection Helper
├── requirements.txt          # Python Dependencies
├── .env                      # Environment Variables
└── README.md                 # Project Documentation
👨‍💻 Admin Access
To access the Admin Dashboard:

Sign up with the Role selected as "Admin".

Or, manually insert an admin into the database:
(Use the generate_password_hash from werkzeug.security in Python to get a hash)

sql
INSERT INTO users (name, email, password_hash, role) VALUES ('Admin', 'admin@heritagehub.com', 'hashed_password_here', 'admin');
Navigate to http://127.0.0.1:5000/admin.

🔮 Future Scope
Multi-Language Support: Adding Hindi, Marathi, and Sanskrit translations for AI responses.

3D Model Generation: Using AI to convert 2D images of monuments into 3D viewable models.

Community Contribution: Allowing users to upload verified historical data to the database.

Offline Mode: Integrating a local LLM (like Llama 3 via Ollama) for offline heritage analysis.

