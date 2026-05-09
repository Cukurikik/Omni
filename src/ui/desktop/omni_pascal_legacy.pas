{ OMNI UI & Legacy Interop Layer }
{ Object Pascal (Delphi) implementation bridging legacy Windows desktop applications }
{ to the modern Omni Universal Binary via DLL invocation. }

unit OmniLegacyBridge;

interface

uses
  System.SysUtils, System.Classes;

type
  { Defines the C-ABI function signature exported by omni_universal_binary.dll }
  TOmniExecuteInference = function(InputData: PAnsiChar; out OutputData: PAnsiChar): Integer; cdecl;
  TOmniFreeBuffer = procedure(Buffer: PAnsiChar); cdecl;

  TOmniEngine = class
  private
    FHandle: THandle;
    FOmniExecute: TOmniExecuteInference;
    FOmniFree: TOmniFreeBuffer;
  public
    constructor Create;
    destructor Destroy; override;
    function GenerateText(Prompt: string): string;
  end;

implementation

uses
  Winapi.Windows;

constructor TOmniEngine.Create;
begin
  // Load the Omni Universal Binary dynamically
  FHandle := LoadLibrary('omni_universal_binary.dll');
  if FHandle = 0 then
    raise Exception.Create('OMNI Engine: Failed to load omni_universal_binary.dll');

  @FOmniExecute := GetProcAddress(FHandle, 'omni_execute_inference_str');
  @FOmniFree := GetProcAddress(FHandle, 'omni_free_str_buffer');

  if not Assigned(FOmniExecute) or not Assigned(FOmniFree) then
    raise Exception.Create('OMNI Engine: Failed to bind C-ABI methods.');
end;

destructor TOmniEngine.Destroy;
begin
  if FHandle <> 0 then
    FreeLibrary(FHandle);
  inherited;
end;

function TOmniEngine.GenerateText(Prompt: string): string;
var
  InputAnsi: AnsiString;
  OutputAnsiPtr: PAnsiChar;
  Status: Integer;
begin
  InputAnsi := AnsiString(Prompt);
  
  // Call the C-ABI
  Status := FOmniExecute(PAnsiChar(InputAnsi), OutputAnsiPtr);
  
  if Status = 0 then
  begin
    Result := string(OutputAnsiPtr);
    // Free the memory allocated by the C library to prevent leaks
    FOmniFree(OutputAnsiPtr);
  end
  else
  begin
    raise Exception.CreateFmt('OMNI Engine: Inference failed with status %d', [Status]);
  end;
end;

end.
