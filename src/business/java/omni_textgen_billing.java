// OMNI Framework - Java Enterprise Billing for TextGenerator.io
package com.omni.textgen.billing;

import java.math.BigDecimal;
import java.time.LocalDateTime;

public class OmniTextGenBillingService {

    private static final BigDecimal COST_PER_1K_TOKENS = new BigDecimal("0.02");

    public Invoice generateInvoice(String customerId, long totalTokensProcessed) {
        BigDecimal tokenMultiplier = new BigDecimal(totalTokensProcessed).divide(new BigDecimal("1000"));
        BigDecimal totalAmount = COST_PER_1K_TOKENS.multiply(tokenMultiplier);
        
        Invoice invoice = new Invoice();
        invoice.setCustomerId(customerId);
        invoice.setAmountDue(totalAmount);
        invoice.setBillingDate(LocalDateTime.now());
        invoice.setStatus("PENDING");
        
        // Log transaction to OMNI Enterprise Bus
        System.out.println("OMNI Billing: Generated invoice for " + customerId + " - $" + totalAmount);
        
        return invoice;
    }

    public static class Invoice {
        private String customerId;
        private BigDecimal amountDue;
        private LocalDateTime billingDate;
        private String status;

        public void setCustomerId(String id) { this.customerId = id; }
        public void setAmountDue(BigDecimal amt) { this.amountDue = amt; }
        public void setBillingDate(LocalDateTime date) { this.billingDate = date; }
        public void setStatus(String status) { this.status = status; }
        
        public String getCustomerId() { return customerId; }
        public BigDecimal getAmountDue() { return amountDue; }
    }
}
