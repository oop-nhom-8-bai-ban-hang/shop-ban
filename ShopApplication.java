package com.shopban; // Tên package của bạn

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

@SpringBootApplication
public class ShopApplication {

    public static void main(String[] args) {
        // Khởi động ứng dụng Spring Boot
        SpringApplication.run(ShopApplication.class, args);
    }
}

// Controller để xử lý request và trả về giao diện
@Controller
class WebController {

    @GetMapping("/")
    public String index() {
        // Trả về template có tên là 'index.html'
        // Spring Boot sẽ tự động tìm trong /src/main/resources/templates/
        return "index"; 
    }
}
