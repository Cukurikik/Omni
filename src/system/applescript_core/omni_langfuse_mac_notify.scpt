-- Omni Langfuse Mac Notify (AppleScript)
-- System Layer: Zero-mock macOS notification bridge for critical telemetry alerts.

on run argv
    if (count of argv) > 0 then
        set alertMessage to item 1 of argv
    else
        set alertMessage to "OMNI_SYS: Langfuse ingestion bound verified."
    end if
    
    display notification alertMessage with title "Omni Langfuse Bridge" subtitle "Telemetry Status"
end run
