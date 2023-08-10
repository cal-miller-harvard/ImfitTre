using Genie.Router, Genie.Requests, Genie.Renderer.Json
using Dates

route("/") do
  serve_static_file("welcome.html")
end

route("/jsonpayload", method = POST) do
  @show jsonpayload()
  @show rawpayload()

  json(jsonpayload())
end

route("/shot") do
  id = params(:id, nothing)
  return json(get_shot(id))
end

route("/image") do
  id = params(:id, nothing)
  return json(get_image(id))
end