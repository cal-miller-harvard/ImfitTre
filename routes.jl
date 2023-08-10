using Genie.Router, Genie.Requests, Genie.Renderer.Json

route("/") do
  serve_static_file("welcome.html")
end

route("/jsonpayload", method = POST) do
  @show jsonpayload()
  @show rawpayload()

  json(jsonpayload())
end
