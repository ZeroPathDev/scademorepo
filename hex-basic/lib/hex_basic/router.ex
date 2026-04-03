defmodule FeedAggregator.Router do
  use Phoenix.Router
  import Plug.Conn

  pipeline :api do
    plug :accepts, ["json"]
  end

  scope "/api", FeedAggregator do
    pipe_through :api

    get "/feeds", FeedController, :index
    post "/feeds/import", FeedController, :import_feed
    get "/proxy", ProxyController, :forward
  end
end

defmodule FeedAggregator.FeedController do
  use Phoenix.Controller, formats: [:json]

  def index(conn, %{"url" => feed_url}) do
    case HTTPoison.get(feed_url) do
      {:ok, %HTTPoison.Response{body: body, status_code: 200}} ->
        entries = parse_feed(body)
        json(conn, %{entries: entries})

      {:error, reason} ->
        conn
        |> put_status(502)
        |> json(%{error: "Failed to fetch feed: #{inspect(reason)}"})
    end
  end

  def index(conn, _params) do
    conn
    |> put_status(400)
    |> json(%{error: "url parameter required"})
  end

  def import_feed(conn, %{"url" => url, "category" => category}) do
    case HTTPoison.get(url) do
      {:ok, %HTTPoison.Response{body: body}} ->
        entries = parse_feed(body)
        stored = Enum.map(entries, fn entry ->
          Map.put(entry, :category, category)
        end)
        json(conn, %{imported: length(stored), entries: stored})

      _ ->
        conn |> put_status(502) |> json(%{error: "import failed"})
    end
  end

  defp parse_feed(xml_body) do
    xml_body
    |> Floki.parse_document!()
    |> Floki.find("item, entry")
    |> Enum.map(fn entry ->
      %{
        title: entry |> Floki.find("title") |> Floki.text(),
        link: entry |> Floki.find("link") |> Floki.text(),
        published: entry |> Floki.find("pubDate, published") |> Floki.text()
      }
    end)
  end
end

defmodule FeedAggregator.ProxyController do
  use Phoenix.Controller, formats: [:json]

  def forward(conn, %{"target" => target_url}) do
    case HTTPoison.get(target_url) do
      {:ok, %HTTPoison.Response{body: body, status_code: status}} ->
        conn
        |> put_status(status)
        |> text(body)

      {:error, reason} ->
        conn
        |> put_status(502)
        |> json(%{error: inspect(reason)})
    end
  end

  def forward(conn, _params) do
    conn |> put_status(400) |> json(%{error: "target parameter required"})
  end
end
