import bpy
from bpy.props import *
from .combiner_ops import *
from .packer import BinPacker
from ... import common as c

class Combiner(bpy.types.Operator):
    bl_idname = 'kkbp.combiner'
    bl_label = 'Create Atlas'
    bl_description = 'Combine materials'
    bl_options = {'UNDO', 'INTERNAL'}

    def execute(self, context: bpy.types.Context) -> Set[str]:
        #from invoke
        scn = context.scene
        bpy.ops.kkbp.refresh_ob_data()
        for index, object in enumerate([o for o in bpy.data.collections[c.get_name() + ' atlas'].all_objects if o.type == 'MESH' and not o.hide_get()]):
            set_ob_mode(context.view_layer, scn.kkbp_ob_data)
            self.data = get_data(scn.kkbp_ob_data, object)
            self.mats_uv = get_mats_uv(scn, self.data)
            clear_empty_mats(scn, self.data, self.mats_uv)
            get_duplicates(self.mats_uv)
            self.structure = get_structure(scn, self.data, self.mats_uv)
            
            #from execute
            scn.kkbp_save_path = os.path.join(context.scene.kkbp.import_dir, 'atlas_files')
            self.structure = BinPacker(get_size(scn, self.structure)).fit()

            size = get_atlas_size(self.structure)
            atlas_size = calculate_adjusted_size(scn, size)

            if max(atlas_size, default=0) > 20000:
                text = 'The output image size of {0}x{1}px is too large'.format(*atlas_size)
                c.kklog(text)
                self.report({'ERROR'}, text)
                return {'FINISHED'}
            
            bake_types = []
            if scn.kkbp.bake_light_bool:
                bake_types.append('light')
            if scn.kkbp.bake_dark_bool:
                bake_types.append('dark')
            if scn.kkbp.bake_norm_bool:
                bake_types.append('normal')

            for type in bake_types:
                #replace all images
                for material in [mat_slot.material for mat_slot in object.material_slots if mat_slot.material.get('simple')]:
                    image = material.node_tree.nodes['textures'].node_tree.nodes[type].image
                    if image:
                        if image.name == 'Template: Placeholder':
                            image = None
                    if not image:
                        continue
                    else:
                        material.node_tree.nodes['Image Texture'].image = image
                
                #then run the atlas creation
                atlas = get_atlas(scn, self.structure, atlas_size)
                comb_mats = get_comb_mats(scn, atlas, self.mats_uv, type, index)
                c.print_timer(f'save atlas for {object.name} {type}')

            align_uvs(scn, self.structure, atlas.size, size)
            bpy.ops.kkbp.refresh_ob_data()

        return {'FINISHED'}

