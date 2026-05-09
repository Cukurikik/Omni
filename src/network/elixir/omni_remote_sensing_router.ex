defmodule OmniFramework.RemoteSensingRouter do
  @moduledoc """
  OMNI Route handler for satellite imagery intended for DINOv2
  """
  use Plug.Router

  plug :match
  plug :dispatch

  post "/api/v1/analyze/satellite" do
    {:ok, body, conn} = Plug.Conn.read_body(conn)
    # Forward to Python DINOv2 compute node
    case OmniFramework.RPC.call_node(:dinov2_worker, body) do
      {:ok, features} ->
        send_resp(conn, 200, Jason.encode!(%{status: "success", features: features}))
      {:error, reason} ->
        send_resp(conn, 500, Jason.encode!(%{error: reason}))
    end
  end

  match _ do
    send_resp(conn, 404, "OMNI Route not found")
  end
end
