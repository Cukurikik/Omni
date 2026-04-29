// Omni KnowPAT Engine (Delphi / Object Pascal)
// Business Layer: Native executable logic for Knowledgeable Preference Alignment rules.

unit OmniKnowPatEngine;

interface

type
  TAlignmentResult = record
    Success: Boolean;
    ConfidenceScore: Double;
    ErrorMessage: String;
  end;

  TOmniKnowPat = class
  public
    class function AlignPreference(BaseScore: Double; TargetNodeExists: Boolean): TAlignmentResult;
  end;

implementation

class function TOmniKnowPat.AlignPreference(BaseScore: Double; TargetNodeExists: Boolean): TAlignmentResult;
begin
  if BaseScore < 0.0 then
  begin
    Result.Success := False;
    Result.ConfidenceScore := 0.0;
    Result.ErrorMessage := 'Score must be non-negative';
    Exit;
  end;

  if TargetNodeExists then
    Result.ConfidenceScore := BaseScore * 1.1
  else
    Result.ConfidenceScore := BaseScore * 0.9;

  Result.Success := True;
  Result.ErrorMessage := '';
end;

end.
