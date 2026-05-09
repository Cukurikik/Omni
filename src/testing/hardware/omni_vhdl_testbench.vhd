-- OMNI Testing & Hardware Layer
-- VHDL Simulation Testbench
-- Verifies the logic of the Omni Pipelined Multiply-Accumulate (MAC) block before FPGA synthesis.

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity Omni_MAC_Testbench is
-- Testbench has no ports
end Omni_MAC_Testbench;

architecture Simulation of Omni_MAC_Testbench is

    -- Component Declaration for the Unit Under Test (UUT)
    component Omni_MAC_Pipelined
        Port ( 
            clk         : in STD_LOGIC;
            rst_n       : in STD_LOGIC;
            weight      : in signed(15 downto 0);
            activation  : in signed(15 downto 0);
            valid_in    : in STD_LOGIC;
            accumulator : out signed(31 downto 0);
            valid_out   : out STD_LOGIC
        );
    end component;

    -- Inputs
    signal clk        : std_logic := '0';
    signal rst_n      : std_logic := '0';
    signal weight     : signed(15 downto 0) := (others => '0');
    signal activation : signed(15 downto 0) := (others => '0');
    signal valid_in   : std_logic := '0';

    -- Outputs
    signal accumulator : signed(31 downto 0);
    signal valid_out   : std_logic;

    -- Clock period definition
    constant clk_period : time := 10 ns;

begin
    -- Instantiate the Unit Under Test (UUT)
    uut: Omni_MAC_Pipelined port map (
        clk => clk,
        rst_n => rst_n,
        weight => weight,
        activation => activation,
        valid_in => valid_in,
        accumulator => accumulator,
        valid_out => valid_out
    );

    -- Clock process definitions
    clk_process :process
    begin
        clk <= '0';
        wait for clk_period/2;
        clk <= '1';
        wait for clk_period/2;
    end process;

    -- Stimulus process
    stim_proc: process
    begin		
        -- Hold reset state for 20 ns
        wait for 20 ns;	
        rst_n <= '1';
        
        wait for clk_period;
        
        -- Test Case 1: 5 * 10
        weight <= to_signed(5, 16);
        activation <= to_signed(10, 16);
        valid_in <= '1';
        wait for clk_period;
        
        -- Test Case 2: -3 * 4
        weight <= to_signed(-3, 16);
        activation <= to_signed(4, 16);
        valid_in <= '1';
        wait for clk_period;
        
        -- Stop input
        valid_in <= '0';
        
        -- Wait for pipeline flushes (3 cycles)
        wait for clk_period * 4;
        
        -- End simulation
        assert false report "OMNI VHDL Testbench: Simulation Complete." severity note;
        wait;
    end process;

end Simulation;
