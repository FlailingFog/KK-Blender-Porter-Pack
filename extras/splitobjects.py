import bpy
from ..interface.dictionary_en import t
from .. import common as c

class split_objects(bpy.types.Operator):
    bl_idname = "kkbp.splitobjects"
    bl_label = "Split Objects"
    bl_description = t('split_objects_tt')
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        
        object_to_split = bpy.context.active_object
        if object_to_split == None:
            return {'CANCELLED'}
        materials = [m for m in object_to_split.data.materials if 'Outline ' not in m.name and 'KK Outline' != m.name]
        materials = materials[:int(len(materials)/2)]
        outlines = [bpy.data.materials['Outline' + m.name[2:]] for m in materials if bpy.data.materials.get('Outline' + m.name[2:])]
        materials.extend(outlines)
        def separate_materials(object_to_split, mat_list):
            '''Separates the materials in the mat_list on object, and creates a new object'''
            c.switch(object_to_split, 'edit')    
            for mat in mat_list:
                mat_index = object_to_split.data.materials.find(mat.name)
                bpy.context.object.active_material_index = mat_index
                bpy.ops.object.material_slot_select()
            try:
                #separate
                bpy.ops.mesh.separate(type='SELECTED')
                #delete unused materials on the new object
                new_object = bpy.data.objects[object_to_split.name + '.001']
                new_object.name = object_to_split.name + ' split'
                c.switch(new_object, 'object')
                bpy.ops.object.material_slot_remove_unused()
                new_object.modifiers['Outline Modifier'].show_viewport = False
                new_object.modifiers['Outline Modifier'].show_render = False
                #delete unused materials on old object
                c.switch(object_to_split, 'object')
                bpy.ops.object.material_slot_remove_unused()
                new_object.modifiers['Outline Modifier'].show_viewport = False
                new_object.modifiers['Outline Modifier'].show_render = False
            except:
                c.kklog('Nothing was selected when separating materials from: ' + object.name, 'warn')
            bpy.ops.object.mode_set(mode = 'OBJECT')
        separate_materials(object_to_split, materials)

        return {'FINISHED'}

if __name__ == "__main__":
    bpy.utils.register_class(split_objects)