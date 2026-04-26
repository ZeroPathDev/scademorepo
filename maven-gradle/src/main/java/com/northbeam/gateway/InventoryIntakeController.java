package com.northbeam.gateway;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;

@Controller
@RequestMapping("/intake")
public class InventoryIntakeController {
    private static final Logger logger = LogManager.getLogger(InventoryIntakeController.class);

    @GetMapping("/new")
    public String showForm(Model model) {
        model.addAttribute("intake", new InventoryIntake());
        return "intake/new";
    }

    @PostMapping("/submit")
    public String submitIntake(@ModelAttribute("intake") InventoryIntake intake, Model model) {
        logger.info("Received intake for sku={} qty={} warehouse={}",
                intake.getSku(), intake.getQuantity(), intake.getWarehouse());
        model.addAttribute("intake", intake);
        return "intake/confirm";
    }

    public static class InventoryIntake {
        private String sku;
        private int quantity;
        private String warehouse;
        private String notes;

        public String getSku() { return sku; }
        public void setSku(String sku) { this.sku = sku; }

        public int getQuantity() { return quantity; }
        public void setQuantity(int quantity) { this.quantity = quantity; }

        public String getWarehouse() { return warehouse; }
        public void setWarehouse(String warehouse) { this.warehouse = warehouse; }

        public String getNotes() { return notes; }
        public void setNotes(String notes) { this.notes = notes; }
    }
}
