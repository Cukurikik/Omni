-- OMNI Database Layer: SQL Server / T-SQL
-- Stored procedure for highly concurrent logging of inference transactions.

CREATE PROCEDURE [Omni].[LogInferenceTransaction]
    @TransactionId UNIQUEIDENTIFIER,
    @ModelVersion NVARCHAR(50),
    @DurationMs INT,
    @TokensGenerated INT,
    @RequesterId NVARCHAR(100),
    @ErrorCode INT = 0
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    BEGIN TRY
        BEGIN TRANSACTION;

        INSERT INTO [Omni].[InferenceLogs] (
            [TransactionId],
            [ModelVersion],
            [DurationMs],
            [TokensGenerated],
            [RequesterId],
            [ErrorCode],
            [Timestamp]
        )
        VALUES (
            @TransactionId,
            @ModelVersion,
            @DurationMs,
            @TokensGenerated,
            @RequesterId,
            @ErrorCode,
            GETUTCDATE()
        );

        -- Update cumulative billing stats for the user
        UPDATE [Omni].[UserQuotas]
        SET [TokensUsed] = [TokensUsed] + @TokensGenerated,
            [TotalInferences] = [TotalInferences] + 1
        WHERE [UserId] = @RequesterId;

        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;

        -- Rethrow error using monadic principles mapped to SQL Error handling
        DECLARE @ErrorMessage NVARCHAR(4000) = ERROR_MESSAGE();
        DECLARE @ErrorSeverity INT = ERROR_SEVERITY();
        DECLARE @ErrorState INT = ERROR_STATE();

        RAISERROR (@ErrorMessage, @ErrorSeverity, @ErrorState);
    END CATCH
END;
GO
