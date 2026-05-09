-- OMNI Hardware Acceleration Layer
-- VHDL description of an FPGA accelerator block for Non-Linear Activation Functions (e.g., ReLU)
-- This allows zero-cost inferences on edge FPGA SoCs (e.g., Xilinx Zynq).

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity Omni_ReLU_Accelerator is
    Port ( 
        clk : in STD_LOGIC;
        rst : in STD_LOGIC;
        data_in : in STD_LOGIC_VECTOR (15 downto 0); -- 16-bit fixed point input
        data_out : out STD_LOGIC_VECTOR (15 downto 0);
        valid_in : in STD_LOGIC;
        valid_out : out STD_LOGIC
    );
end Omni_ReLU_Accelerator;

architecture Behavioral of Omni_ReLU_Accelerator is
begin
    process(clk)
    begin
        if rising_edge(clk) then
            if rst = '1' then
                data_out <= (others => '0');
                valid_out <= '0';
            else
                valid_out <= valid_in;
                if valid_in = '1' then
                    -- MSB is sign bit in 2's complement. If '1', number is negative -> output 0.
                    if data_in(15) = '1' then
                        data_out <= (others => '0');
                    else
                        data_out <= data_in;
                    end if;
                else
                    data_out <= (others => '0');
                end if;
            end if;
        end if;
    end process;
end Behavioral;
