# Civilian scooter rider

Approved essential asset, Route B: fresh CC0 MPFB body, casualsuit02 long-sleeve teal top and denim trousers, shoes01 adapted to low footwear. No uniform, insignia, equipment or original shirt logo. Source photos remain untouched.

Two mutually exclusive baked poses, facing Blender +Y on the approved Voi, common ground/axle origin. <=35,000 triangles per pose, single opaque 2048 atlas baked from ride only; matching index topology and UVs. Editable source rig in rider_rig.blend (native MPFB -Y; export rotates geometry pi about Z), poses on frames 1/2. Build: Blender 5.2 --background --factory-startup --threads 8 --python-exit-code 1 --python build.py; export independently with --python export.py. Validate with python verify.py.

Deck/grip targets are in spec.json. Analytic limb solves fail on unreachable targets rather than silently clamping. Both soles checked from adopted foot source indices; short source collars are trimmed to avoid bent trouser penetration. Actual approved scooter dashboard versus evaluated body and clothing triangle intersections are tested in preview.py before rendering. Contact renders are in previews/, including final fit board.
