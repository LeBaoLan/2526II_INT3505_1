# TypeSpec Demo
# Cài đặt TypeSpec Compiler

npm install -g @typespec/compiler

# Khởi tạo thư viện hỗ trợ

npm install @typespec/http @typespec/openapi3

# Tiến hành biên dịch

tsp compile main.tsp

# Dùng file openapi.yaml kết quả trên các nền tảng như Swagger Editor hoặc Redoc để hiển thị thành trang web giao diện người dùng.