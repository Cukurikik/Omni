#[no_mangle]
pub extern "C" fn omni_fastquant_aggregate_bars(
    tick_prices: *const f32,
    tick_volumes: *const f32,
    num_ticks: i32,
    ticks_per_bar: i32,
    out_open: *mut f32,
    out_high: *mut f32,
    out_low: *mut f32,
    out_close: *mut f32,
    err_code: *mut i32,
) {
    if err_code.is_null() {
        return;
    }

    if tick_prices.is_null() || tick_volumes.is_null() || out_open.is_null() || num_ticks <= 0 || ticks_per_bar <= 0 {
        unsafe { *err_code = -1 };
        return;
    }

    // Zero-mock high-speed Tick-to-OHLCV Bar aggregation
    // Crucial for high-frequency ML backtesting memory efficiency
    unsafe {
        let num_bars = num_ticks / ticks_per_bar;
        
        for b in 0..num_bars {
            let start_idx = (b * ticks_per_bar) as usize;
            let end_idx = start_idx + ticks_per_bar as usize;
            
            let mut high = tick_prices[start_idx];
            let mut low = tick_prices[start_idx];
            
            for i in start_idx..end_idx {
                let p = tick_prices[i];
                if p > high { high = p; }
                if p < low { low = p; }
            }
            
            out_open[b as usize] = tick_prices[start_idx];
            out_high[b as usize] = high;
            out_low[b as usize] = low;
            out_close[b as usize] = tick_prices[end_idx - 1];
        }
        
        *err_code = 0;
    }
}
