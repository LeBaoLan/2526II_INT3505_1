require("dotenv").config();
const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");
const productRoutes = require("./routes/productRoutes");

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

app.use("/api/products", productRoutes);

app.get("/", (req, res) => {
    res.json({ message: "Product API đang chạy!" });
});

mongoose
    .connect(process.env.MONGODB_URI)
    .then(() => {
        console.log("✅ Kết nối MongoDB thành công!");
        app.listen(PORT, () => {
            console.log(`🚀 Server chạy tại http://localhost:${PORT}`);
        });
    })
    .catch((err) => {
        console.error("❌ Lỗi kết nối MongoDB:", err.message);
    });