const express = require('express');
require('dotenv').config();
const { Pool } = require('pg');
const http = require('http');
const { Server } = require('socket.io');
const cors = require('cors');

const app = express();
const server = http.createServer(app);
const io = new Server(server, { cors: { origin: '*' } });

io.on('connection', (socket) => {
  socket.on('admin_force_exit', ({ session_id } = {}) => {
    if (session_id === undefined || session_id === null) return;
    io.emit(`force_exit_${session_id}`, { message: 'Terminated by Admin' });
  });
});

app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// -------------------------------------------------------------
// PostgreSQL Connection Configuration
// -------------------------------------------------------------
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: process.env.DATABASE_URL ? { rejectUnauthorized: false } : false
});

// -------------------------------------------------------------
// 1. ENTRY API Endpoint
// -------------------------------------------------------------
app.post('/api/entry', async (req, res) => {
  const { 
    user_role, user_id, student_name, department, section, system_number,
    year, subject_name, faculty_name, lab_selection, lab_name,
    lab_start_time, lab_end_time
  } = req.body;

  try {
    const query = `
      INSERT INTO session_logs 
        (user_role, user_id, student_name, department, section, system_number, "YEAR", subject_name, faculty_name, lab_selection, lab_start_time, lab_end_time, status)
      VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, 'ACTIVE')
      RETURNING session_id, entry_time;
    `;
    
    const values = [
      user_role, 
      user_id,
      student_name || '',
      department,
      section || '', 
      system_number, 
      year || 'I Year', 
      subject_name || '',
      faculty_name || '',
      lab_selection || lab_name || '',
      lab_start_time || '', 
      lab_end_time || ''
    ];

    const result = await pool.query(query, values);

    const newSession = {
      session_id: result.rows[0].session_id,
      entry_time: result.rows[0].entry_time,
      ...req.body
    };

    // Emit event to update dashboard in real-time
    io.emit('NEW_ENTRY_EVENT', newSession);
    res.json({ success: true, session_id: result.rows[0].session_id, entry_time: result.rows[0].entry_time });
  } catch (err) {
    console.error('Entry Database Error:', err);
    res.status(500).json({ success: false, error: err.message });
  }
});

// -------------------------------------------------------------
// 2. EXIT API Endpoint
// -------------------------------------------------------------
app.post('/api/exit', async (req, res) => {
  const { session_id, duration } = req.body;

  try {
    const query = `
      UPDATE session_logs 
      SET exit_time = CURRENT_TIMESTAMP, status = 'COMPLETED', total_duration = $1
      WHERE session_id = $2
      RETURNING *;
    `;
    const result = await pool.query(query, [duration, session_id]);

    // Emit event to update dashboard
    io.emit('STUDENT_EXIT_EVENT', result.rows[0]);
    res.json({ success: true, record: result.rows[0] });
  } catch (err) {
    console.error('Exit Database Error:', err);
    res.status(500).json({ success: false, error: err.message });
  }
});

// -------------------------------------------------------------
// 3. FETCH ADMIN LOGS (With Date and Department Filtering)
// -------------------------------------------------------------
app.get('/api/logs', async (req, res) => {
  const { date, dept = 'ALL' } = req.query;
  try {
    const result = await pool.query(`
      SELECT session_id AS id, session_id, user_role, user_id, student_name,
        department, section, "YEAR" AS year, system_number, subject_name,
        faculty_name, entry_time, exit_time, total_duration, status
      FROM session_logs
      WHERE ($1::date IS NULL OR entry_time::date = $1::date)
        AND ($2 = 'ALL' OR LOWER(department) = LOWER($2))
      ORDER BY entry_time DESC;
    `, [date || null, dept]);
    res.json(result.rows);
  } catch (err) {
    console.error('Logs Fetch Error:', err);
    res.status(500).json({ error: err.message });
  }
});

app.delete('/api/logs/:id', async (req, res) => {
  try {
    const result = await pool.query(
      'DELETE FROM session_logs WHERE session_id = $1 RETURNING session_id',
      [req.params.id]
    );
    if (result.rowCount === 0) {
      return res.status(404).json({ error: 'Session log not found' });
    }
    res.json({ success: true });
  } catch (err) {
    console.error('Log Delete Error:', err);
    res.status(500).json({ error: err.message });
  }
});

// Start Server
const PORT = Number(process.env.PORT) || 5000;
async function startServer() {
  try {
    await pool.query(`
      ALTER TABLE session_logs
        ADD COLUMN IF NOT EXISTS student_name VARCHAR(100),
        ADD COLUMN IF NOT EXISTS faculty_name VARCHAR(100),
        ADD COLUMN IF NOT EXISTS lab_selection VARCHAR(100)
    `);
  } catch (err) {
    console.error('Database schema check failed:', err.message);
  }

  server.listen(PORT, () => {
    console.log(`===================================================`);
    console.log(`🚀 Lab Server running at http://localhost:${PORT}`);
    console.log(`===================================================`);
  });
}

startServer();