
# 🏫 K.S.R. College of Engineering - Lab Attendance System

An automated, cloud-based Student Lab Attendance Tracking & Monitoring System built for K.S.R. College of Engineering. The system consists of a Desktop Client App for student logins and a Centralized Web Dashboard for real-time monitoring and reporting.

---

## 🌟 Key Features

* **Desktop Entry Application:** Built using Python (PyQt5) with continuous status tracking and validation.
* **Real-time Live Dashboard:** Web-based Admin Dashboard powered by Node.js and Socket.io for instantaneous logging and active student counts.
* **Cloud Database:** Hosted on Neon PostgreSQL database ensuring high availability and secure data retention.
* **Advanced Reporting:** Export filtered attendance logs directly to **Excel (.xlsx)** format.
* **Sorting & Filtering:** Admin panel allows live dynamic sorting (ASC/DESC) by Register Number, Student Name, System Number, and Entry Time alongside custom filters for Date, Department, Year, and Section.
* **Force Exit Control:** Admins can remotely terminate active student lab sessions directly from the web panel.

---

## 🏗️ Architecture & Tech Stack

* **Client Desktop App:** Python 3, PyQt5, Requests, SocketIO Client
* **Backend Server:** Node.js, Express.js, Socket.io
* **Database:** PostgreSQL (Neon Cloud DB)
* **Hosting:** Render (Backend Server & Static Hosting)

---

## 🗄️ Database Schema (`session_logs`)

```sql
CREATE TABLE session_logs (
    session_id SERIAL PRIMARY KEY,
    user_role VARCHAR(20) DEFAULT 'STUDENT',
    user_id VARCHAR(50),
    department VARCHAR(50),
    section VARCHAR(50),
    system_number VARCHAR(50),
    subject_name VARCHAR(100),
    entry_time TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    exit_time TIMESTAMP WITHOUT TIME ZONE,
    status VARCHAR(20) DEFAULT 'ACTIVE',
    "YEAR" VARCHAR(50),
    lab_start_time VARCHAR(20),
    lab_end_time VARCHAR(20),
    total_duration VARCHAR(50),
    faculty_name VARCHAR(100),
    student_name VARCHAR(100),
    lab_selection VARCHAR(100)
);

```

---

## 🚀 Getting Started

### 1. Backend Server Setup

```bash
# Clone repository
git clone [https://github.com/your-username/lab-attendance.git](https://github.com/your-username/lab-attendance.git)
cd lab-attendance

# Install dependencies
npm install

# Environment Variables Configuration (.env)
DATABASE_URL=your_neon_postgresql_connection_string
PORT=5000

# Start server
npm start

```

### 2. Client Application Setup

```bash
# Navigate to client directory
cd client

# Install required Python modules
pip install PyQt5 requests python-socketio

# Set Cloud Backend URL Environment Variable (Optional)
<--------*******************************>

# Run desktop application
python client_app.py

```

---

## 📊 Admin Dashboard Capabilities

1. **Active Lab Session Counters:** Instant metric cards showing live active users, total logs, and department logs.
2. **Horizontal Table Scroll:** Designed for complete visibility of student records, lab slots, duration, and status across all screen resolutions.
3. **Excel Export:** Download tailored reports matching active search filters with a single click.

---

## 🔒 License & Ownership

Developed for **K.S.R. College of Engineering (Autonomous), Tiruchengode**.

```

```