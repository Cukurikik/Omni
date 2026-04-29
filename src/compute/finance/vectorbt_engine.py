import numpy as np

class VectorBTEngine:
    def __init__(self, prices, signals):
        self.prices = np.array(prices)
        self.signals = np.array(signals) # 1 buy, -1 sell, 0 hold
        
    def run_backtest(self, initial_capital=10000.0):
        position = 0.0
        cash = initial_capital
        
        for p, s in zip(self.prices, self.signals):
            if s == 1 and cash >= p: # Buy 1 unit
                position += 1
                cash -= p
            elif s == -1 and position > 0: # Sell 1 unit
                position -= 1
                cash += p
                
        final_value = cash + (position * self.prices[-1])
        return_pct = (final_value - initial_capital) / initial_capital
        return final_value, return_pct

if __name__ == "__main__":
    engine = VectorBTEngine([100, 105, 102, 110], [1, 0, -1, 1])
    val, ret = engine.run_backtest()
    print(f"Final Value: {val}, Return: {ret*100:.2f}%")
