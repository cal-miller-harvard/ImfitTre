using Genie.Router, Genie.Requests, Genie.Renderer.Json
using Dates
using Mongoc: as_json

route("/") do
  model = @init
  page(model, ui()) |> html
end

route("/jsonpayload", method = POST) do
  @show jsonpayload()
  @show rawpayload()

  return json(jsonpayload())
end

route("/shot") do
  id = params(:id, nothing)
  return as_json(get_shot(id))
end

route("/image") do
  id = params(:id, nothing)
  return as_json(get_image(id))
end
