-- Omni Lion Adversarial FPGA Accelerator (VHDL)
-- Hardware-level hash filtering for adversarial prompts.

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity omni_lion_adversarial_fpga is
    Port ( clk : in STD_LOGIC;
           rst : in STD_LOGIC;
           payload_hash : in STD_LOGIC_VECTOR (255 downto 0);
           hash_valid : in STD_LOGIC;
           is_adversarial : out STD_LOGIC);
end omni_lion_adversarial_fpga;

architecture Behavioral of omni_lion_adversarial_fpga is
    -- Deterministic known-bad hash prefix matching
    constant BAD_PREFIX : STD_LOGIC_VECTOR(15 downto 0) := x"DEAD";
begin
    process(clk)
    begin
        if rising_edge(clk) then
            if rst = '1' then
                is_adversarial <= '0';
            elsif hash_valid = '1' then
                if payload_hash(255 downto 240) = BAD_PREFIX then
                    is_adversarial <= '1';
                else
                    is_adversarial <= '0';
                end if;
            end if;
        end if;
    end process;
end Behavioral;
