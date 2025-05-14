import bpy
from ..interface.dictionary_en import t
from .. import common as c

class mat_comb_setup(bpy.types.Operator):
    bl_idname = "kkbp.matcombsetup"
    bl_label = "Material combiner setup"
    bl_description = t('mat_comb_tt')
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        def recurLayerCollection(layerColl, collName):
            found = None
            if (layerColl.name == collName):
                return layerColl
            for layer in layerColl.children:
                found = recurLayerCollection(layer, collName)
                if found:
                    return found
        
        def remove_orphan_data():
            #revert the image back from the atlas file to the baked file   
            for mat in bpy.data.materials:
                if mat.name[-4:] == '-ORG':
                    simplified_name = mat.name[:-4]
                    if bpy.data.materials.get(simplified_name):
                        simplified_mat = bpy.data.materials[simplified_name]
                        for bake_type in ['light', 'dark', 'normal']:
                            simplified_mat.node_tree.nodes['textures'].node_tree.nodes[bake_type].image = bpy.data.images.get(simplified_name + ' ' + bake_type + '.png')
            #delete orphan data
            for cat in [bpy.data.armatures, bpy.data.objects, bpy.data.meshes, bpy.data.materials, bpy.data.images, bpy.data.node_groups]:
                for block in cat:
                    if block.users == 0:
                        cat.remove(block)

        if bpy.data.collections.get(c.get_name() + ' atlas'):
            c.kklog('deleting previous collection "Model with atlas" and regenerating atlas model...')
            def del_collection(coll):
                for c in coll.children:
                    del_collection(c)
                bpy.data.collections.remove(coll,do_unlink=True)
            del_collection(bpy.data.collections[c.get_name() + ' atlas'])
            remove_orphan_data()
            #show the original collection again
            layer_collection = bpy.context.view_layer.layer_collection
            layerColl = recurLayerCollection(layer_collection, 'Scene Collection')
            bpy.context.view_layer.active_layer_collection = layerColl
            bpy.context.scene.view_layers[0].active_layer_collection.children[0].exclude = False

        #Change the Active LayerCollection to 'My Collection'
        layer_collection = bpy.context.view_layer.layer_collection
        layerColl = recurLayerCollection(layer_collection, c.get_name())
        bpy.context.view_layer.active_layer_collection = layerColl

        # https://blender.stackexchange.com/questions/157828/how-to-duplicate-a-certain-collection-using-python
        from collections import  defaultdict
        def copy_objects(from_col, to_col, linked, dupe_lut):
            for o in from_col.objects:
                dupe = o.copy()
                if not linked and o.data:
                    dupe.data = dupe.data.copy()
                to_col.objects.link(dupe)
                dupe_lut[o] = dupe
        def copy(parent, collection, linked=False):
            dupe_lut = defaultdict(lambda : None)
            def _copy(parent, collection, linked=False):
                if collection.name == 'Bone Widgets':
                    return
                cc = bpy.data.collections.new(collection.name)
                copy_objects(collection, cc, linked, dupe_lut)
                for c in collection.children:
                    _copy(cc, c, linked)
                parent.children.link(cc)
            _copy(parent, collection, linked)
            for o, dupe in tuple(dupe_lut.items()):
                parent = dupe_lut[o.parent]
                if parent:
                    dupe.parent = parent

        context = bpy.context
        scene = context.scene
        col = context.collection
        assert(col is not scene.collection)
        copy(scene.collection, col)

        #setup materials for the combiner script
        for obj in [o for o in bpy.data.collections[c.get_name() + '.001'].all_objects if not o.hide_get() and o.type == 'MESH']:
            for mat in [mat_slot.material for mat_slot in obj.material_slots if mat_slot.material.get('simple')]:
                nodes = mat.node_tree.nodes
                links = mat.node_tree.links
                emissive_node = nodes.new('ShaderNodeEmission')
                image_node = nodes.new('ShaderNodeTexImage')
                links.new(emissive_node.inputs[0], image_node.outputs[0])
                image_node.image = nodes['textures'].node_tree.nodes['light'].image
            context.view_layer.objects.active = obj
            bpy.ops.object.material_slot_remove_unused()

            #update the modifiers
            for mod in obj.modifiers:
                if mod.type == 'ARMATURE':
                    #fix the armature modifier to use the copied aramture
                    copied_armature = [o for o in bpy.data.collections[c.get_name() + '.001'].all_objects if o.type == 'ARMATURE'][0]
                    mod.object = copied_armature
                elif mod.type == 'SOLIDIFY':
                    #disable the outline on the atlased object because I don't feel like fixing it
                    obj.modifiers['Outline Modifier'].show_render = False
                    obj.modifiers['Outline Modifier'].show_viewport = False
                elif mod.type == 'UV_WARP':
                    #fix the UV warp modifier to use the copied armature
                    copied_armature = [o for o in bpy.data.collections[c.get_name() + '.001'].all_objects if o.type == 'ARMATURE'][0]
                    mod.object_from = copied_armature
                    mod.object_to = copied_armature

        return {'FINISHED'}
