-- @omni-layer System | @omni-lang VHDL | @omni-batch 18 | @omni-semester 16
-- @omni-description VHDL softmax co-processor for transformer FPGA inference:
-- pipelined exp and normalization unit for attention score computation.

library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;
use IEEE.math_real.all;

entity omni_softmax_unit is
    generic (
        SEQ_LEN    : integer := 32;
        DATA_WIDTH : integer := 16
    );
    port (
        clk       : in  std_logic;
        rst       : in  std_logic;
        start     : in  std_logic;
        data_in   : in  std_logic_vector(SEQ_LEN * DATA_WIDTH - 1 downto 0);
        data_out  : out std_logic_vector(SEQ_LEN * DATA_WIDTH - 1 downto 0);
        done      : out std_logic
    );
end entity;

architecture rtl of omni_softmax_unit is
    type state_type is (IDLE, FIND_MAX, COMPUTE_EXP, NORMALIZE, FINISHED);
    signal state : state_type := IDLE;

    type data_array is array (0 to SEQ_LEN - 1) of signed(DATA_WIDTH - 1 downto 0);
    signal scores    : data_array;
    signal exp_vals  : data_array;
    signal max_val   : signed(DATA_WIDTH - 1 downto 0);
    signal sum_exp   : signed(DATA_WIDTH * 2 - 1 downto 0);
    signal idx       : integer range 0 to SEQ_LEN;

begin

    process(clk, rst)
    begin
        if rst = '1' then
            state <= IDLE;
            done <= '0';
            idx <= 0;
            max_val <= (others => '0');
            sum_exp <= (others => '0');
        elsif rising_edge(clk) then
            case state is
                when IDLE =>
                    done <= '0';
                    if start = '1' then
                        -- Load input data
                        for i in 0 to SEQ_LEN - 1 loop
                            scores(i) <= signed(data_in(
                                (i + 1) * DATA_WIDTH - 1 downto i * DATA_WIDTH));
                        end loop;
                        state <= FIND_MAX;
                        idx <= 0;
                        max_val <= signed(data_in(DATA_WIDTH - 1 downto 0));
                    end if;

                when FIND_MAX =>
                    if idx < SEQ_LEN then
                        if scores(idx) > max_val then
                            max_val <= scores(idx);
                        end if;
                        idx <= idx + 1;
                    else
                        state <= COMPUTE_EXP;
                        idx <= 0;
                        sum_exp <= (others => '0');
                    end if;

                when COMPUTE_EXP =>
                    if idx < SEQ_LEN then
                        -- Approximate exp(x - max) using linear piece
                        exp_vals(idx) <= scores(idx) - max_val + to_signed(256, DATA_WIDTH);
                        if exp_vals(idx) < to_signed(0, DATA_WIDTH) then
                            exp_vals(idx) <= to_signed(1, DATA_WIDTH);
                        end if;
                        sum_exp <= sum_exp + resize(exp_vals(idx), DATA_WIDTH * 2);
                        idx <= idx + 1;
                    else
                        state <= NORMALIZE;
                        idx <= 0;
                    end if;

                when NORMALIZE =>
                    if idx < SEQ_LEN then
                        -- Normalize: out = exp_val * 256 / sum_exp
                        if sum_exp /= to_signed(0, DATA_WIDTH * 2) then
                            exp_vals(idx) <= resize(
                                shift_left(resize(exp_vals(idx), DATA_WIDTH * 2), 8)
                                / sum_exp, DATA_WIDTH);
                        end if;
                        idx <= idx + 1;
                    else
                        state <= FINISHED;
                    end if;

                when FINISHED =>
                    -- Output results
                    for i in 0 to SEQ_LEN - 1 loop
                        data_out((i + 1) * DATA_WIDTH - 1 downto i * DATA_WIDTH)
                            <= std_logic_vector(exp_vals(i));
                    end loop;
                    done <= '1';
                    state <= IDLE;
            end case;
        end if;
    end process;

end architecture;
