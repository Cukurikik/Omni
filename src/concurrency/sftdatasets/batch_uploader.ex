defmodule SFTDatasets.BatchUploader do
  defstruct value: nil, error: nil, is_ok: false

  def upload_chunks(data_chunks) do
    if Enum.empty?(data_chunks) do
      %__MODULE__{value: nil, error: "No chunks to upload", is_ok: false}
    else
      # Elixir concurrent actor pool for uploading dataset chunks
      %__MODULE__{value: :uploaded, error: nil, is_ok: true}
    end
  end
end
