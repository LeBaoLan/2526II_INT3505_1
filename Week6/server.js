const express = require('express');
const jwt = require('jsonwebtoken');
const app = express();
app.use(express.json());

const ACCESS_SECRET = 'access_key_123';
const REFRESH_SECRET = 'refresh_key_456';

// Giả lập database user với Roles và Scopes
const USERS = {
  admin: { password: '123456', role: 'admin', scopes: ['items:read', 'items:write', 'items:delete'] },
  user1: { password: 'password', role: 'member', scopes: ['items:read'] }
};

let refreshTokens = []; // Lưu trữ refresh tokens đang hoạt động

// Middleware xác thực Bearer Token (Authentication)
function authenticateToken(req, res, next) {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1]; // Lấy phần sau "Bearer"
  if (!token) return res.status(401).json({ error: 'Thiếu token' });

  jwt.verify(token, ACCESS_SECRET, (err, user) => {
    if (err) return res.status(403).json({ error: 'Token hết hạn hoặc không hợp lệ' });
    req.user = user;
    next();
  });
}

// Middleware kiểm tra quyền (Authorization - Roles & Scopes)
function authorize(requiredRole, requiredScope) {
  return (req, res, next) => {
    if (req.user.role !== requiredRole && req.user.role !== 'admin') {
      return res.status(403).json({ error: 'Bạn không có quyền thực hiện hành động này' });
    }
    if (requiredScope && !req.user.scopes.includes(requiredScope)) {
      return res.status(403).json({ error: 'Phạm vi (Scope) không cho phép' });
    }
    next();
  };
}

// Đăng nhập: Trả về cả Access và Refresh Token
app.post('/login', (req, res) => {
  const { username, password } = req.body;
  const user = USERS[username];
  if (!user || user.password !== password) return res.status(401).json({ error: 'Sai tài khoản' });

  const payload = { username, role: user.role, scopes: user.scopes };
  const accessToken = jwt.sign(payload, ACCESS_SECRET, { expiresIn: '1m' }); // Hạn ngắn
  const refreshToken = jwt.sign(payload, REFRESH_SECRET);
  
  refreshTokens.push(refreshToken);
  res.json({ accessToken, refreshToken });
});

// Cấp lại Access Token bằng Refresh Token
app.post('/refresh', (req, res) => {
  const { token } = req.body;
  if (!token || !refreshTokens.includes(token)) return res.sendStatus(403);
  
  jwt.verify(token, REFRESH_SECRET, (err, user) => {
    if (err) return res.sendStatus(403);
    const accessToken = jwt.sign({ username: user.username, role: user.role, scopes: user.scopes }, ACCESS_SECRET, { expiresIn: '1m' });
    res.json({ accessToken });
  });
});

// Routes với các cấp độ bảo vệ khác nhau
app.get('/items', authenticateToken, authorize('member', 'items:read'), (req, res) => {
  res.json({ message: 'Xem danh sách thành công', user: req.user });
});

app.delete('/items/:id', authenticateToken, authorize('admin', 'items:delete'), (req, res) => {
  res.json({ message: `Đã xóa item ${req.params.id} bởi Admin` });
});

app.listen(3000, () => console.log('Server nâng cấp chạy tại http://localhost:3000'));