using Mongoc

function get_shot(id)
  id_format = r"^(\d{4})_(\d{2})_(\d{2})_(\d+)$"
  if id !== nothing && occursin(id_format, id)
    query = Mongoc.BSON(Dict("_id" => id))
    return Mongoc.find_one(collection, query)
  end
end

function get_image(id)
  id_format = r"^(\d{4})_(\d{2})_(\d{2})_(\d+)_(.+)$"
  if id !== nothing && occursin(id_format, id)
    query = Mongoc.BSON(Dict("_id" => id))
    metadata = Mongoc.find_one(db["fs.files"], query)
    dtype, shape = get_image_params(metadata)
    image = Array{dtype}(undef, shape...)
    Mongoc.open_download_stream(bucket, Mongoc.get_as_bson_value(query, "_id")) do io
      im_string = Vector{UInt8}(read(io, String))
      image .= reshape(reinterpret(dtype, im_string), shape...)
    end
    return image
  else
    error("Error: id must be specified as yyyy_mm_dd_shot_name.")
  end
end


function get_image_params(metadata::Mongoc.BSON)
    if !haskey(metadata, "dtype")
        throw("Metadata does not contain field dtype.")
    end
    if !haskey(metadata, "shape")
        throw("Metadata does not contain field shape.")
    end

    type_map = Dict(
        "int16" => Int16,
        "int32" => Int32,
        "int64" => Int64
    )

    if !(metadata["dtype"] in keys(type_map))
        throw("Invalid data type: $(metadata["dtype"])")
    end

    shape = (Int64(i) for i in metadata["shape"])
    dtype = type_map[metadata["dtype"]]

    return dtype, shape
end
