# MIT License

# Copyright (c) 2017 GiveMeAllYourCats

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the 'Software'), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Code author: Hotox
# Repo: https://github.com/michaeldegroot/cats-blender-plugin
# Edits by: GiveMeAllYourCats

import bpy

from . import common as Common
#from .register import register_wrap
#from .translations import t

#@register_wrap
class MergeWeights(bpy.types.Operator):
    bl_idname = 'kkbp.cats_merge_weights'
    bl_label = 'cats merge weights'
    #bl_description = t('MergeWeights.desc')
    bl_options = {'REGISTER', 'UNDO'}
    '''
    @classmethod
    def poll(cls, context):
        active_obj = bpy.context.active_object
        if not active_obj or not bpy.context.active_object.type == 'ARMATURE':
            return False
        if active_obj.mode == 'EDIT' and bpy.context.selected_editable_bones:
            return True
        if active_obj.mode == 'POSE' and bpy.context.selected_pose_bones:
            return True

        return False
    '''
    def execute(self, context):
        saved_data = Common.SavedData()

        armature = bpy.context.object

        Common.switch('EDIT')

        # Find which bones to work on and put their name and their parent in a list
        parenting_list = {}
        for bone in bpy.context.selected_editable_bones:
            parent = bone.parent
            while parent and parent.parent and parent in bpy.context.selected_editable_bones:
                parent = parent.parent
            if not parent:
                continue
            parenting_list[bone.name] = parent.name

        # Merge all the bones in the parenting list
        merge_weights(armature, parenting_list)

        saved_data.load()

        self.report({'INFO'}, 'cats merge weights success')
        return {'FINISHED'}
    
def merge_weights(armature, parenting_list):
    Common.switch('OBJECT')
    # Merge the weights on the meshes
    for mesh in Common.get_meshes_objects(armature_name=armature.name, visible_only=bpy.context.scene.merge_visible_meshes_only if bpy.context.scene.get('merge_visible_meshes_only') != None else True):
        Common.set_active(mesh)

        for bone, parent in parenting_list.items():
            if not mesh.vertex_groups.get(bone):
                continue
            if not mesh.vertex_groups.get(parent):
                mesh.vertex_groups.new(name=parent)
            Common.mix_weights(mesh, bone, parent)

    # Select armature
    Common.unselect_all()
    Common.set_active(armature)
    Common.switch('EDIT')

    # Delete merged bones
    if True:
        for bone in parenting_list.keys():
            armature.data.edit_bones.remove(armature.data.edit_bones.get(bone))
