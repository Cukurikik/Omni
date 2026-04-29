-- Omni Massive Activations (VHDL)
-- Hardware Layer: FPGA gate-level description for activation thresholding.

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity omni_massive_activations is
    Port ( 
        clk : in STD_LOGIC;
        rst : in STD_LOGIC;
        activation_in : in signed(15 downto 0);
        threshold : in signed(15 downto 0);
        activation_out : out signed(15 downto 0)
    );
end omni_massive_activations;

architecture Behavioral of omni_massive_activations is
begin
    process(clk, rst)
    begin
        if rst = '1' then
            activation_out <= (others => '0');
        elsif rising_edge(clk) then
            if activation_in > threshold then
                -- Hard clipping for massive activations
                activation_out <= threshold;
            else
                activation_out <= activation_in;
            end if;
        end if;
    end process;
end Behavioral;
