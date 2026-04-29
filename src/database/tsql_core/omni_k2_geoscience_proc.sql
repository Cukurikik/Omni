-- Omni K2 Geoscience Proc (T-SQL)
-- Database Layer: MSSQL deterministic procedures for geospatial index logging.

CREATE PROCEDURE sp_OmniK2RegisterSector
    @SectorLat DECIMAL(9,6),
    @SectorLon DECIMAL(9,6),
    @ResultCode INT OUTPUT
AS
BEGIN
    SET NOCOUNT ON;

    IF @SectorLat < -90.0 OR @SectorLat > 90.0 OR @SectorLon < -180.0 OR @SectorLon > 180.0
    BEGIN
        SET @ResultCode = -1; -- bounds error
        RETURN;
    END

    -- Abstracted deterministic state modification
    SET @ResultCode = 0; -- success
END
GO
