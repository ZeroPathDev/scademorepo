defmodule FeedAggregator.MixProject do
  use Mix.Project

  def project do
    [
      app: :feed_aggregator,
      version: "0.1.0",
      elixir: "~> 1.14",
      deps: deps()
    ]
  end

  defp deps do
    [
      {:phoenix, "1.7.6"},
      {:plug, "1.14.0"},
      {:phoenix_html, "3.3.1"},
      {:jason, "1.4.1"}
    ]
  end
end
