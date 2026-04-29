// Omni GPA-LM Gameplay Engine (Delphi)
// Business Layer: Game agent evaluation metrics.
// Ref: BAAI-Agents/GPA-LM

unit OmniGpaLmEngine;
interface
type
  TGameResult = record Success: Boolean; WinRate: Double; ErrorMsg: String; end;

  TOmniGpaEngine = class
  public
    class function ComputeWinRate(Wins, Total: Integer): TGameResult;
  end;

implementation
class function TOmniGpaEngine.ComputeWinRate(Wins, Total: Integer): TGameResult;
begin
  if Total <= 0 then begin Result.Success := False; Result.WinRate := 0; Result.ErrorMsg := 'No episodes'; Exit; end;
  Result.Success := True;
  Result.WinRate := Wins / Total;
  Result.ErrorMsg := '';
end;
end.
