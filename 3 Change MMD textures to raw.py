##########################################
# CHANGE MMD TEXTURES TO RAW SCRIPT
##########################################
# change color spaces of all the image textures named "Mmd Base Tex" to RAW:

import bpy

for mat in bpy.data.materials:
    for node in mat.node_tree.nodes:
        if node.type == 'TEX_IMAGE':
            if node.name=='mmd_base_tex':
                node.image.colorspace_settings.name = 'Raw'
