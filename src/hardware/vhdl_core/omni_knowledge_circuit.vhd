-- Omni Knowledge Circuit FPGA (VHDL)
-- Hardware Layer: Gate-level attribution thresholding.
-- Ref: zjunlp/KnowledgeCircuits

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity omni_knowledge_circuit is
    Port ( clk : in STD_LOGIC; rst : in STD_LOGIC;
           activation_in : in signed(15 downto 0);
           threshold : in signed(15 downto 0);
           is_significant : out STD_LOGIC );
end omni_knowledge_circuit;

architecture Behavioral of omni_knowledge_circuit is
begin
    process(clk, rst)
    begin
        if rst = '1' then is_significant <= '0';
        elsif rising_edge(clk) then
            if abs(activation_in) >= abs(threshold) then is_significant <= '1';
            else is_significant <= '0'; end if;
        end if;
    end process;
end Behavioral;
