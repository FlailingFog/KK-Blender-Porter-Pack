#Finalize the accessory placements

import bpy
from mathutils import Vector

class finalize_grey(bpy.types.Operator):
    bl_idname = "kkb.finalizegrey"
    bl_label = "Finalize accessory placements"
    bl_description = "Finalize accessory placements"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context): 
        def runIt():
            
            bpy.ops.object.mode_set(mode='OBJECT')
            armature = bpy.data.objects['Armature']
            
            def return_child(parent):
                try:
                    new_parent = parent.children[0]
                    return return_child(new_parent)
                except:
                    return parent
                
            #go through the empties that have children
            for empty in [ob for ob in bpy.data.objects if ob.type == 'EMPTY' and len(ob.children) > 0]:
                #get the last child of the empty and check if it's a mesh (accessory object)
                if empty.parent_bone != None and empty.parent_bone != '':
                    empty_name = empty.name
                    empty_parent = bpy.data.objects[empty_name].parent_bone
                    last_child = return_child(empty)
                    if last_child.type == 'MESH':
                        
                        #unparent the mesh (accessory) and keep location
                        bpy.ops.object.select_all(action='DESELECT')
                        bpy.context.view_layer.objects.active = last_child
                        last_child.select_set(True)
                        #empty.select_set(True)
                        bone_location = empty.location
                        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
                        
                        #create a bone on the armature for this accessory
                        bpy.context.view_layer.objects.active = armature
                        bpy.ops.object.mode_set(mode='EDIT')
                        
                        height_adder = Vector((0,0.1,0))
                        
                        new_bone = armature.data.edit_bones.new(last_child.name)
                        new_bone.head = armature.data.edit_bones[empty_parent].head + bone_location
                        new_bone.tail = armature.data.edit_bones[empty_parent].head + bone_location + height_adder
                        new_bone.parent = armature.data.edit_bones[empty_parent]
                        
                        #parent the accessory to the new armature bone
                        bone = new_bone.name
                        bpy.ops.object.mode_set(mode='POSE')
                        
                        bpy.ops.pose.select_all(action='DESELECT')
                        armature.data.bones.active = armature.data.bones[bone]
                        armature.data.bones[bone].select = True
                        armature.data.bones[bone].select_head = True
                        armature.data.bones[bone].select_tail = True
                        bpy.ops.object.parent_set(type='BONE_RELATIVE')
                        bpy.ops.object.mode_set(mode='OBJECT')
                        
                        #make sure the accessory has a vertex group for the bone when it's merged
                        vertex_group = last_child.vertex_groups.new(name=bone)
                        verticesToAdd = []
                        for vertex in last_child.data.vertices:
                            verticesToAdd.append(vertex.index)
                        vertex_group.add(verticesToAdd, 1.0, 'ADD')
                        
                        #delete the empty
                        bpy.ops.object.select_all(action='DESELECT')
                        empty.select_set(True)
                        bpy.ops.object.delete(use_global=False, confirm=False)
                        
                else:
                    #delete the empty
                    bpy.ops.object.select_all(action='DESELECT')
                    empty.select_set(True)
                    bpy.ops.object.delete(use_global=False, confirm=False)
            
            #delete the rest of the empties
            bpy.ops.object.select_all(action='DESELECT')
            for empty in [ob for ob in bpy.data.objects if ob.type == 'EMPTY']:
                empty.select_set(True)
            bpy.ops.object.delete(use_global=False, confirm=False)
            
        #I need a better way to do this
        runIt()
        
        return {'FINISHED'}
    
if __name__ == "__main__":
    bpy.utils.register_class(finalize_grey)
    
    # test call
    print((bpy.ops.kkb.finalizegrey('INVOKE_DEFAULT')))
