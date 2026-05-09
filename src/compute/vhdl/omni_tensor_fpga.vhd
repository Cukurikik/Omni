-- OMNI Tensor Core FPGA Logic (VHDL)
-- Implements an 8-bit Integer MAC unit for edge AI

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity Omni_MAC is
    Port ( clk : in STD_LOGIC;
           a : in signed(7 downto 0);
           b : in signed(7 downto 0);
           acc_out : out signed(15 downto 0));
end Omni_MAC;

architecture Behavioral of Omni_MAC is
    signal acc : signed(15 downto 0) := (others => '0');
begin
    process(clk)
    begin
        if rising_edge(clk) then
            acc <= acc + (a * b);
        end if;
    end process;
    
    acc_out <= acc;
end Behavioral;
