-- OMNI Framework - VHDL for Tensor Accelerator
-- Implements hardware-accelerated Matrix Multiply-Accumulate (MAC) for Inference

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity OmniTensorAccelerator is
    Port ( 
           clk      : in  STD_LOGIC;
           rst      : in  STD_LOGIC;
           en       : in  STD_LOGIC;
           weight_in: in  STD_LOGIC_VECTOR(15 downto 0);
           act_in   : in  STD_LOGIC_VECTOR(15 downto 0);
           mac_out  : out STD_LOGIC_VECTOR(31 downto 0)
         );
end OmniTensorAccelerator;

architecture Behavioral of OmniTensorAccelerator is
    signal accumulator : signed(31 downto 0) := (others => '0');
begin
    process(clk, rst)
    begin
        if rst = '1' then
            accumulator <= (others => '0');
        elsif rising_edge(clk) then
            if en = '1' then
                -- Perform 16-bit signed multiplication and accumulate
                accumulator <= accumulator + (signed(weight_in) * signed(act_in));
            end if;
        end if;
    end process;

    mac_out <= std_logic_vector(accumulator);
end Behavioral;
