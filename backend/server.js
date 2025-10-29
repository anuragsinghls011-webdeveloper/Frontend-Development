// server.js

// --- Dependencies Import karna ---
// Express.js: Web server framework
// body-parser: Incoming request bodies ko parse karne ke liye (JSON format mein)
// cors: Cross-Origin Resource Sharing ko enable karne ke liye (frontend aur backend ko communicate karne deta hai)
const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');

// --- Server Setup ---
const app = express();
const PORT = 3000; // Server is port par chalega

// --- Middleware ka istemaal ---
app.use(cors()); // CORS ko enable karna
app.use(bodyParser.json()); // JSON requests ko samajhne ke liye

// --- Mock Database (Abhi ke liye data yahan store kar rahe hain) ---
// Asli project mein, yeh data MongoDB ya SQL database mein hoga.

const db = {
    students: [
        { email: 'student@srms.ac.in', password: 'password123', name: 'Rohan Kumar' }
    ],
    admins: [
        { email: 'admin@srms.ac.in', password: 'admin123', name: 'Admin User' }
    ],
    academics: [
        {
            title: "Engineering Mathematics-I",
            faculty: "Dr. Anuj Kumar",
            description: "Core concepts of calculus, matrices, and differential equations.",
            branch: "CS/IT/EC",
            color: "blue-500",
            links: { pdf: "#", youtube: "#", drive: "#" },
            keywords: "engineering mathematics-i dr. anuj kumar"
        },
        {
            title: "Programming for Problem Solving",
            faculty: "Prof. Shweta Sharma",
            description: "Introduction to C programming, loops, arrays, and functions.",
            branch: "CS/IT",
            color: "green-500",
            links: { pdf: "#", youtube: "#", drive: "#" },
            keywords: "programming for problem solving prof. shweta sharma"
        },
        // ... Baaki subjects yahan add honge
    ],
    faculty: [
        {
            name: "Prof. Ritu Singh",
            title: "Ph.D, M.Tech (HOD, B.tech First year)",
            subjects: "Engineering Maths, Data Structures",
            email: "ritu.s@srms.ac.in",
            linkedin: "#",
            img: "https://placehold.co/150x150/667eea/FFFFFF/png?text=RS",
            keywords: "prof ritu singh hod b.tech first year engineering maths data structures"
        },
        {
            name: "Prof. Ashutosh Pandey",
            title: "M.Tech (CSE)",
            subjects: "C Programming, Web Tech",
            email: "ashutosh.p@srms.ac.in",
            linkedin: "#",
            img: "https://placehold.co/150x150/794acf/FFFFFF/png?text=AP",
            keywords: "prof ashutosh pandey cse c programming web tech"
        },
        // ... Baaki faculty yahan add honge
    ],
    events: {
        tech: [
            { name: "CodeClash 2025", date: "Aug 15, 2025", description: "A competitive programming contest for all students." }
        ],
        cultural: [
            { name: "Spandan - Annual Fest", date: "Oct 10, 2025", description: "The biggest cultural extravaganza of the year." }
        ],
        fest: [
             { name: "Zest - Sports Fest", date: "Nov 20, 2025", description: "Get ready for a week of intense sporting action." }
        ]
    }
};

// --- API Routes ---

// 1. Login API
app.post('/api/login/:type', (req, res) => {
    const { type } = req.params;
    const { email, password } = req.body;

    console.log(`Login attempt for ${type}: ${email}`);

    const userList = type === 'student' ? db.students : db.admins;
    const user = userList.find(u => u.email === email && u.password === password);

    if (user) {
        res.json({ success: true, message: 'Login successful!', user: { name: user.name, email: user.email } });
    } else {
        res.status(401).json({ success: false, message: 'Invalid credentials' });
    }
});

// 2. Data Fetching APIs
app.get('/api/academics', (req, res) => {
    res.json(db.academics);
});

app.get('/api/faculty', (req, res) => {
    res.json(db.faculty);
});

app.get('/api/events', (req, res) => {
    res.json(db.events);
});

// 3. Event Registration API
app.post('/api/register', (req, res) => {
    const registrationData = req.body;
    // Asli application mein, is data ko database mein save karenge.
    console.log('New Event Registration Received:');
    console.log(registrationData);
    
    // Frontend ko success response bhejna
    res.json({ success: true, message: 'Registration successful!', data: registrationData });
});


// --- Server ko Start karna ---
app.listen(PORT, () => {
    console.log(`Backend server SRMS Portal ke liye http://localhost:${PORT} par chal raha hai`);
});
