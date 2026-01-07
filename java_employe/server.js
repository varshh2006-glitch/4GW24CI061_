const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const app = express();

const db = new sqlite3.Database('./database.db');

app.use(express.json());
app.use(express.static('public')); // Serves HTML from the public folder

// Initialize Tables
db.serialize(() => {
    db.run(`CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, email TEXT, phone TEXT, gender TEXT, dept TEXT
    )`);
    db.run(`CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        emp_name TEXT, status TEXT, time TEXT
    )`);
});

// APIs
app.get('/api/employees', (req, res) => {
    db.all("SELECT * FROM employees", [], (err, rows) => res.json(rows));
});

app.post('/api/employees', (req, res) => {
    const { name, email, phone, gender, dept } = req.body;
    db.run("INSERT INTO employees (name, email, phone, gender, dept) VALUES (?,?,?,?,?)", 
        [name, email, phone, gender, dept], () => res.json({ success: true }));
});

app.post('/api/log', (req, res) => {
    const { name, status } = req.body;
    const time = new Date().toLocaleString();
    db.run("INSERT INTO logs (emp_name, status, time) VALUES (?,?,?)", [name, status, time], () => res.json({ success: true }));
});

app.get('/api/logs', (req, res) => {
    db.all("SELECT * FROM logs ORDER BY id DESC", [], (err, rows) => res.json(rows));
});

// Start Server
app.listen(3000, () => {
    console.log('SERVER STARTED!');
    console.log('Open your browser and go to: http://localhost:3000/login.html');
});