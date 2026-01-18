package ru.yandex.practicum.billing;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@SpringBootApplication
@RestController
public class BillingApplication {

	@GetMapping
	public String call() {
		return "Billing";
	}

	public static void main(String[] args) {
		SpringApplication.run(BillingApplication.class, args);
	}

}
