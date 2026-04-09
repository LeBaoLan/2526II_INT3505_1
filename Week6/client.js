const axios = require('axios');
const BASE = 'http://localhost:3000';

async function testRole(username, password) {
  console.log(`\n--- Kiểm tra cho User: ${username} ---`);
  try {
    // 1. Login lấy cặp Token
    const loginRes = await axios.post(`${BASE}/login`, { username, password });
    const { accessToken, refreshToken } = loginRes.data;
    const headers = { Authorization: `Bearer ${accessToken}` }; // Bearer Token

    // 2. Thử xem danh sách (Scope: items:read)
    const list = await axios.get(`${BASE}/items`, { headers });
    console.log(`> Xem hàng: ${list.data.message}`);

    // 3. Thử xóa hàng (Role: admin / Scope: items:delete)
    try {
      const del = await axios.delete(`${BASE}/items/1`, { headers });
      console.log(`> Xóa hàng: ${del.data.message}`);
    } catch (e) {
      console.log(`> Xóa hàng: Thất bại (${e.response.data.error})`);
    }

    // 4. Minh họa Refresh Token khi Access Token hết hạn
    console.log(`> Đang dùng Refresh Token để lấy Access Token mới...`);
    const refreshRes = await axios.post(`${BASE}/refresh`, { token: refreshToken });
    console.log(`> Cấp mới thành công: ${refreshRes.data.accessToken}...`);

  } catch (e) {
    console.error('Lỗi hệ thống:', e.message);
  }
}

async function runDemo() {
  await testRole('user1', 'password'); // Role member
  await testRole('admin', '123456');   // Role admin
}

runDemo();