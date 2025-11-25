package ru.yandex.practicum.orders;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;

@SpringBootApplication
@RestController
public class OrdersApplication {

	private RestTemplate restTemplate = new RestTemplate();

	@GetMapping
	public String call() {
		String response = restTemplate.getForObject("http://billing:8081", String.class);
		return "Orders -> " + response;
	}


	public static void main(String[] args) {
		SpringApplication.run(OrdersApplication.class, args);
	}

}
