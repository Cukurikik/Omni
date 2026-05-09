// OMNI Business Logic script in Groovy for JVM integration
package com.omni.business

class OmniPricingEngine {
    
    static BigDecimal calculateDiscount(BigDecimal basePrice, String customerTier) {
        BigDecimal discountRate = 0.0
        
        switch(customerTier) {
            case "GOLD":
                discountRate = 0.20
                break
            case "SILVER":
                discountRate = 0.10
                break
            default:
                discountRate = 0.0
        }
        
        return basePrice - (basePrice * discountRate)
    }
    
    static void main(String[] args) {
        def finalPrice = calculateDiscount(100.0, "GOLD")
        println "OMNI Groovy Pricing Engine: Final Price is \$${finalPrice}"
    }
}
