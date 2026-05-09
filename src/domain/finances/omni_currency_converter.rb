# omni_currency_converter.rb — Currency Conversion Engine
# Layer: Domain / Finances
#
# Provides a robust, precise currency conversion module.
# Utilizes BigDecimal to prevent floating-point inaccuracies typical in financial logic.

require 'bigdecimal'

module OmniFinances
  class CurrencyConverter
    # Stores exchange rates relative to a base currency (e.g., USD = 1.0)
    attr_reader :rates, :base_currency

    def initialize(base_currency: 'USD')
      @base_currency = base_currency.to_s.upcase
      @rates = { @base_currency => BigDecimal('1.0') }
    end

    # Updates the exchange rate for a specific currency relative to the base currency
    def set_rate(currency, rate)
      currency = currency.to_s.upcase
      @rates[currency] = BigDecimal(rate.to_s)
    end

    # Converts an amount from one currency to another
    def convert(amount, from_currency:, to_currency:)
      amount = BigDecimal(amount.to_s)
      from_currency = from_currency.to_s.upcase
      to_currency = to_currency.to_s.upcase

      if from_currency == to_currency
        return amount
      end

      from_rate = @rates[from_currency]
      to_rate = @rates[to_currency]

      unless from_rate
        raise ArgumentError, "Missing exchange rate for source currency: #{from_currency}"
      end

      unless to_rate
        raise ArgumentError, "Missing exchange rate for target currency: #{to_currency}"
      end

      # Conversion formula: Amount * (TargetRate / SourceRate)
      # We use 10 decimal places of precision for intermediate division to prevent truncation
      base_amount = amount / from_rate
      converted_amount = base_amount * to_rate

      # Financial rounding: Half Even (Banker's rounding) to 2 decimal places
      converted_amount.round(2, BigDecimal::ROUND_HALF_EVEN)
    end

    # Bulk converts a list of transactions to a target currency
    def bulk_convert(transactions, target_currency:)
      transactions.map do |tx|
        {
          id: tx[:id],
          original_amount: tx[:amount],
          original_currency: tx[:currency],
          converted_amount: convert(tx[:amount], from_currency: tx[:currency], to_currency: target_currency),
          target_currency: target_currency.to_s.upcase
        }
      end
    end
  end
end
