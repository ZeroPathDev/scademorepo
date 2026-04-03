require "rack"
require "nokogiri"
require "net/http"
require "json"
require "uri"

class FeedAggregator
  def call(env)
    request = Rack::Request.new(env)

    case [request.request_method, request.path_info]
    when ["GET", "/api/feeds"]
      handle_feeds(request)
    when ["POST", "/api/parse"]
      handle_parse(request)
    when ["GET", "/api/proxy"]
      handle_proxy(request)
    when ["GET", "/health"]
      [200, { "content-type" => "application/json" }, ['{"status":"ok"}']]
    else
      [404, { "content-type" => "text/plain" }, ["Not Found"]]
    end
  end

  private

  def handle_feeds(request)
    feed_url = request.params["url"]
    return [400, {}, ["url param required"]] unless feed_url

    uri = URI.parse(feed_url)
    response = Net::HTTP.get_response(uri)
    doc = Nokogiri::XML(response.body)

    items = doc.xpath("//item | //entry").map do |entry|
      {
        title: entry.at_xpath("title")&.text,
        link: entry.at_xpath("link")&.text || entry.at_xpath("link/@href")&.value,
        published: entry.at_xpath("pubDate | published | updated")&.text,
        summary: entry.at_xpath("description | summary")&.text&.strip
      }
    end

    body = JSON.generate({ feed_url: feed_url, items: items })
    [200, { "content-type" => "application/json" }, [body]]
  end

  def handle_parse(request)
    raw_body = request.body.read
    doc = Nokogiri::HTML(raw_body)

    links = doc.css("a[href]").map { |a| { text: a.text.strip, href: a["href"] } }
    headings = doc.css("h1, h2, h3").map(&:text)
    images = doc.css("img[src]").map { |img| img["src"] }

    result = { links: links, headings: headings, images: images }
    [200, { "content-type" => "application/json" }, [JSON.generate(result)]]
  end

  def handle_proxy(request)
    target = request.params["target"]
    return [400, {}, ["target param required"]] unless target

    uri = URI.parse(target)
    response = Net::HTTP.get_response(uri)

    [
      response.code.to_i,
      { "content-type" => response["content-type"] || "text/plain" },
      [response.body]
    ]
  end
end

if __FILE__ == $0
  Rack::Handler::WEBrick.run(FeedAggregator.new, Port: ENV.fetch("PORT", 9292).to_i)
end
