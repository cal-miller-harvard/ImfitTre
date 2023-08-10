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
  id_format = r"(\d{4})_(\d{2})_(\d{2})_(\d+)"
  if id !== nothing && occursin(id_format, id)
    query = Mongoc.BSON(Dict("_id" => id))
    return json(Mongoc.find_one(collection, query))
  else
    json("Error: id must be specified as yyyy_mm_dd_shot.")
  end
end

route("/image") do
  id = params(:id, nothing)
  image = get_image(id)
end