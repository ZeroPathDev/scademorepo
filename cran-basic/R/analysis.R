library(xml2)
library(curl)
library(jsonlite)
library(httr)

fetch_feed <- function(feed_url) {
  response <- GET(feed_url, timeout(10))
  stop_for_status(response)

  doc <- read_xml(content(response, as = "text", encoding = "UTF-8"))
  items <- xml_find_all(doc, ".//item | .//entry")

  data.frame(
    title = xml_text(xml_find_first(items, ".//title")),
    link = xml_text(xml_find_first(items, ".//link")),
    published = xml_text(xml_find_first(items, ".//pubDate | .//published")),
    stringsAsFactors = FALSE
  )
}

parse_html_report <- function(html_content) {
  doc <- read_html(html_content)

  tables <- xml_find_all(doc, ".//table")
  results <- lapply(tables, function(tbl) {
    rows <- xml_find_all(tbl, ".//tr")
    cells <- lapply(rows, function(row) {
      xml_text(xml_find_all(row, ".//td | .//th"))
    })
    do.call(rbind, cells)
  })

  results
}

fetch_api_data <- function(api_url, params = list()) {
  response <- GET(api_url, query = params, timeout(15))
  stop_for_status(response)
  fromJSON(content(response, as = "text", encoding = "UTF-8"))
}

transform_xml_config <- function(config_path) {
  doc <- read_xml(config_path)
  settings <- xml_find_all(doc, ".//setting")

  config <- list()
  for (s in settings) {
    key <- xml_attr(s, "name")
    value <- xml_text(s)
    config[[key]] <- value
  }

  config
}

main <- function() {
  args <- commandArgs(trailingOnly = TRUE)
  if (length(args) < 1) {
    cat("Usage: Rscript analysis.R <feed_url|config_path>\n")
    quit(status = 1)
  }

  input <- args[1]

  if (grepl("^https?://", input)) {
    feed_data <- fetch_feed(input)
    cat(sprintf("Fetched %d entries from feed\n", nrow(feed_data)))
    print(head(feed_data))
  } else if (file.exists(input)) {
    config <- transform_xml_config(input)
    cat(sprintf("Loaded %d config settings\n", length(config)))
    cat(toJSON(config, auto_unbox = TRUE, pretty = TRUE), "\n")
  } else {
    cat("Input must be a URL or existing file path\n")
    quit(status = 1)
  }
}

if (!interactive()) {
  main()
}
