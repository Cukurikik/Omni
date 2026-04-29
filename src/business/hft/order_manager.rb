module Omni
  module HFT
    class Result
      attr_reader :is_success, :value, :error
      def initialize(is_success, value, error); @is_success = is_success; @value = value; @error = error; end
      def self.success(value); new(true, value, nil); end
      def self.failure(error); new(false, nil, error); end
    end

    class Order
      attr_reader :id, :symbol, :qty, :price, :side, :status
      def initialize(symbol, qty, price, side)
        @id = "ORD-#{Time.now.to_i}-#{rand(1000..9999)}"
        @symbol = symbol
        @qty = qty
        @price = price
        @side = side # :buy or :sell
        @status = :pending
      end

      def mark_filled!
        @status = :filled
      end
    end

    class OrderManager
      def initialize(max_position_size = 1000)
        @positions = Hash.new(0)
        @max_position_size = max_position_size
      end

      def create_order(symbol, qty, price, side)
        return Result.failure("Invalid quantity") if qty <= 0
        return Result.failure("Invalid price") if price <= 0
        return Result.failure("Invalid side") unless [:buy, :sell].include?(side)

        current_position = @positions[symbol]
        projected_position = side == :buy ? current_position + qty : current_position - qty

        if projected_position.abs > @max_position_size
          return Result.failure("Risk check failed: position limit exceeded for #{symbol}")
        end

        order = Order.new(symbol, qty, price, side)
        # In a real system, this goes to the Disruptor ring buffer here
        Result.success(order)
      end

      def confirm_fill(order)
        return Result.failure("Order already filled") if order.status == :filled
        
        order.mark_filled!
        if order.side == :buy
          @positions[order.symbol] += order.qty
        else
          @positions[order.symbol] -= order.qty
        end
        
        Result.success(order)
      end
    end
  end
end
