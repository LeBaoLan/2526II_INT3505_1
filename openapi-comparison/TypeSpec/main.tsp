import "@typespec/http";
import "@typespec/openapi3";

using TypeSpec.Http;

@doc("Hệ thống quản lý thư viện đơn giản chức năng cơ bản.")
@service(#{
  title: "API Quản lý sách"
})
namespace LibraryAPI;

model Book {
  id?: int32;
  title: string;
  author: string;
}

@route("/books")
interface Books {
  @get
  @summary("Lấy danh sách tất cả các sách")
  list(): Book[];

  @post
  @summary("Thêm một cuốn sách mới")
  create(@body book: Book): {
    @statusCode _: 201;
    @body result: Book;
  };
}