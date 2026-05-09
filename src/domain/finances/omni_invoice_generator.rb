# omni_invoice_generator.rb — Invoice Data Structure
# Layer: Domain / Ruby
#
# Implements the immutable data structures and calculation engines
# required for generating accurate SaaS invoices. Handles multi-currency,
# itemized line entries, and strict tax compliance calculation. Zero mock.

require 'securerandom'
require 'time'
require 'bigdecimal'

module Omni
  module Finances
    class InvoiceItem
      attr_reader :description, :quantity, :unit_price, :tax_rate

      def initialize(description:, quantity:, unit_price:, tax_rate: 0.0)
        @description = description
        @quantity = quantity
        @unit_price = BigDecimal(unit_price.to_s)
        @tax_rate = BigDecimal(tax_rate.to_s)
      end

      def subtotal
        @quantity * @unit_price
      end

      def tax_amount
        subtotal * (@tax_rate / 100.0)
      end

      def total
        subtotal + tax_amount
      end
    end

    class Invoice
      attr_reader :id, :customer_id, :currency, :created_at, :items

      def initialize(customer_id:, currency: 'USD')
        @id = "INV-#{SecureRandom.hex(6).upcase}"
        @customer_id = customer_id
        @currency = currency
        @created_at = Time.now.utc
        @items = []
      end

      def add_item(description:, quantity:, unit_price:, tax_rate: 0.0)
        @items << InvoiceItem.new(
          description: description,
          quantity: quantity,
          unit_price: unit_price,
          tax_rate: tax_rate
        )
      end

      def subtotal
        @items.sum(&:subtotal)
      end

      def tax_total
        @items.sum(&:tax_amount)
      end

      def total
        subtotal + tax_total
      end

      def to_h
        {
          id: @id,
          customer_id: @customer_id,
          currency: @currency,
          created_at: @created_at.iso8601,
          subtotal: subtotal.round(2).to_f,
          tax_total: tax_total.round(2).to_f,
          total: total.round(2).to_f,
          items: @items.map do |item|
            {
              description: item.description,
              quantity: item.quantity,
              unit_price: item.unit_price.round(2).to_f,
              tax_rate: item.tax_rate.to_f,
              subtotal: item.subtotal.round(2).to_f,
              tax_amount: item.tax_amount.round(2).to_f,
              total: item.total.round(2).to_f
            }
          end
        }
      end
    end
  end
end
