-- OMNI Hardware Acceleration Layer
-- VHDL Custom Memory Controller for Direct Memory Access (DMA)
-- Streams data straight from physical sensors to the Omni LLVM runtime memory pool
-- avoiding OS kernel copy overhead entirely.

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity Omni_DMA_Controller is
    Port ( 
        clk           : in STD_LOGIC;
        rst           : in STD_LOGIC;
        
        -- AXI-Stream Interface from sensors
        s_axis_tdata  : in STD_LOGIC_VECTOR(31 downto 0);
        s_axis_tvalid : in STD_LOGIC;
        s_axis_tready : out STD_LOGIC;
        
        -- AXI-Lite Interface to Omni CPU Memory Space
        m_axi_awaddr  : out STD_LOGIC_VECTOR(31 downto 0);
        m_axi_awvalid : out STD_LOGIC;
        m_axi_awready : in STD_LOGIC;
        m_axi_wdata   : out STD_LOGIC_VECTOR(31 downto 0);
        m_axi_wvalid  : out STD_LOGIC;
        m_axi_wready  : in STD_LOGIC
    );
end Omni_DMA_Controller;

architecture Behavioral of Omni_DMA_Controller is
    signal current_address : UNSIGNED(31 downto 0) := x"40000000"; -- Base address of Omni Shared Mem
begin

    s_axis_tready <= m_axi_wready and m_axi_awready;

    process(clk)
    begin
        if rising_edge(clk) then
            if rst = '1' then
                m_axi_awvalid <= '0';
                m_axi_wvalid  <= '0';
                current_address <= x"40000000";
            else
                if s_axis_tvalid = '1' and m_axi_wready = '1' and m_axi_awready = '1' then
                    m_axi_awaddr <= std_logic_vector(current_address);
                    m_axi_wdata  <= s_axis_tdata;
                    m_axi_awvalid <= '1';
                    m_axi_wvalid  <= '1';
                    
                    current_address <= current_address + 4; -- Next 32-bit word
                else
                    m_axi_awvalid <= '0';
                    m_axi_wvalid  <= '0';
                end if;
            end if;
        end if;
    end process;
end Behavioral;
