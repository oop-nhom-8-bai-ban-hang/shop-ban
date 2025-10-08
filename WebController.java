package com.yourusername.shopban;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class WebController {

    @GetMapping("/")
    public String index() {
        return "index"; // Trả về file index.html trong thư mục templates
    }
}
