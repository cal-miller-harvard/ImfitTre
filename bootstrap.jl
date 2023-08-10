(pwd() != @__DIR__) && cd(@__DIR__) # allow starting app from bin/ dir

using ImfitTre
const UserApp = ImfitTre
ImfitTre.main()
