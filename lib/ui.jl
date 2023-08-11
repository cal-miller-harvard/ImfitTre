using Stipple, Stipple.ReactiveTools
using StippleUI, StipplePlotly
using FileIO, Images, Base64

@appname Display

@app begin
  @in load = false
  @out output = ""
  @in shot = "2023_08_10_69"
  @in camera = "Side"
  # @out image

  cameras::Vector{String} = []

  @onchange shot begin
    params = get_shot(shot)
    if params !== nothing && "images" in keys(params)
      cameras = [k for k in keys(params["images"])]
    end
    
  end

  @onbutton load begin
    image_id = "$(shot)_$(camera)"
    image = get_image(image_id)

    # buffer = Base.IOBuffer()
    # save(Stream{format"PNG"}(buffer), Gray.(Float64.(image[1,:,:])))
    # image = Base64.base64encode(take!(buffer))
    # close(buffer)
    save(Stream{format"PNG"}("fart.png"), Gray.(Float64.(image[1,:,:])))
    
    output = "Loaded image $(image_id)"
  end
end

function ui()
  row(cell(class = "st-module", [
    textfield(class = "q-my-md", "Input", :shot, hint = "Shot ID")
    select(:camera, options= :cameras, label="Camera", emitvalue=true, class = "q-my-md")
    btn(class = "q-my-md", "Load", @click(:load), color = "primary")
    textfield(class = "q-my-md", "Output", :output, readonly = true)
    # """<img src="data:image/png;base64,$(image)">"""
    imageview(src = "fart.png", class = "q-my-md")
  ]))
end
