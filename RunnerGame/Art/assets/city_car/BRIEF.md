# City car build brief

Approved route B: adopt Innerscene CC0 unbranded compact hatchback. Category references in ref/ are existing licensed inputs, preserved. Generic five-door category match, no exact Volkswagen/Golf identity claim. Preserve original 4.28 m length and mirror width; face Blender +Y, ground zero. Body plus four axle-pivoted wheels; target 12k / hard 18k triangles, opaque 2048 atlas.

build.py performs source SHA verification, normalization, named-family reduction, procedural opaque material replacement, independent pre-bake checks, editable.blend save and one 8-thread/32-sample shared atlas bake. normalize_export.py removes a measured inherited wheel node height offset without rebaking or changing UVs. verify.py independently parses actual OBJs/manifest/image and checks normals, triangles, nondegenerate faces, UVs, ground and axle centers. Do not commit, install or modify shared tools.
