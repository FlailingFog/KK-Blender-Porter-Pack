import bpy, time, traceback
from bpy.props import StringProperty

def kklog(log_text, type = 'standard'):
    if not bpy.data.texts.get('KKBP Log'):
        bpy.data.texts.new(name='KKBP Log')
        if bpy.data.screens.get('Scripting'):
            for area in bpy.data.screens['Scripting'].areas:
                if area.type == 'TEXT_EDITOR':
                    area.spaces[0].text = bpy.data.texts['KKBP Log']

    if type == 'error':
        log_text = '\nError:          ' + log_text
    elif type == 'warn':
        log_text = 'Warning:        ' + log_text
    bpy.data.texts['KKBP Log'].write(log_text + '\n')

    print(log_text)

def import_pmx_model(directory):
    #import the pmx file with mmd_tools
    bpy.ops.mmd_tools.import_model('EXEC_DEFAULT',
        files=[{'name': directory}],
        directory=directory,
        scale=0.08,
        types={'MESH', 'ARMATURE', 'MORPHS'},
        log_level='WARNING')
    
    #get rid of the text files mmd tools generates
    if bpy.data.texts.get('Model'):
            bpy.data.texts.remove(bpy.data.texts['Model'])
            bpy.data.texts.remove(bpy.data.texts['Model_e'])

class quick_import(bpy.types.Operator):
    bl_idname = "kkb.quickimport"
    bl_label = "Import .pmx file"
    bl_description = "Imports a KK model (.pmx format) and applies fixes to it"
    bl_options = {'REGISTER', 'UNDO'}

    filepath : StringProperty(maxlen=1024, default='', options={'HIDDEN'})
    filter_glob : StringProperty(default='*.pmx', options={'HIDDEN'})
    
    def execute(self, context):
        #do this thing because cats does it
        if hasattr(context.scene, 'layers'):
            context.scene.layers[0] = True

        #delete the default scene if present
        if len(bpy.data.objects) == 3:
            for obj in ['Camera', 'Light', 'Cube']:
                if bpy.data.objects.get(obj):
                    bpy.data.objects.remove(bpy.data.objects[obj])

        #Set the view transform 
        bpy.context.scene.view_settings.view_transform = 'Standard'

        #create KKLog
        kklog('====    KKBP Log    ====')

        #save filepath for later
        context.scene.kkbp.import_dir = str(self.filepath)

        if context.scene.kkbp.categorize_dropdown == 'A':
            commands = [
                import_pmx_model(context.scene.kkbp.import_dir),
                bpy.ops.kkb.finalizepmx('INVOKE_DEFAULT'),
                bpy.ops.kkb.shapekeys('INVOKE_DEFAULT'),
                bpy.ops.kkb.separatebody('INVOKE_DEFAULT'),
                bpy.ops.kkb.cleanarmature('INVOKE_DEFAULT'),
                bpy.ops.kkb.bonedrivers('INVOKE_DEFAULT'),
                bpy.ops.kkb.importeverything('INVOKE_DEFAULT'),
                bpy.ops.kkb.importcolors('EXEC_DEFAULT'),
            ]
        elif context.scene.kkbp.categorize_dropdown == 'B':
            commands = [
                import_pmx_model(context.scene.kkbp.import_dir),
                bpy.ops.kkb.finalizepmx('INVOKE_DEFAULT'),
                bpy.ops.kkb.shapekeys('INVOKE_DEFAULT'),
                bpy.ops.kkb.separatebody('INVOKE_DEFAULT'),
                bpy.ops.kkb.cleanarmature('INVOKE_DEFAULT'),
                bpy.ops.kkb.bonedrivers('INVOKE_DEFAULT'),
            ]
        else:
            commands = [
                import_pmx_model(context.scene.kkbp.import_dir),
                bpy.ops.kkb.finalizepmx('INVOKE_DEFAULT'),
                bpy.ops.kkb.shapekeys('INVOKE_DEFAULT'),
                bpy.ops.kkb.separatebody('INVOKE_DEFAULT'),
                bpy.ops.kkb.cleanarmature('INVOKE_DEFAULT'),
                bpy.ops.kkb.bonedrivers('INVOKE_DEFAULT'),
                bpy.ops.kkb.importeverything('INVOKE_DEFAULT'),
                bpy.ops.kkb.separatemeshes('EXEC_DEFAULT'),
                bpy.ops.kkb.importcolors('EXEC_DEFAULT'),
            ]

        for command in commands:
            try:
                #run the command
                command

            #if it fails then abort and print the error
            except:
                kklog('Unknown python error occurred', type = 'error')
                kklog(traceback.format_exc())
                self.report({'ERROR'}, traceback.format_exc())
                return {"CANCELLED"}

        if context.scene.kkbp.armature_dropdown == 'B' and context.scene.kkbp.categorize_dropdown in ['A', 'B']:
            bpy.ops.kkb.rigifyconvert('INVOKE_DEFAULT')
            bpy.ops.kkb.rigifyconvert('INVOKE_DEFAULT')

        return {'FINISHED'}
        
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class mat_import(bpy.types.Operator):
    bl_idname = "kkb.matimport"
    bl_label = "Open Export folder"
    bl_description = "Open the folder containing your model.pmx file"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        
        bpy.ops.kkb.importeverything('INVOKE_DEFAULT')
        bpy.ops.kkb.importcolors('EXEC_DEFAULT')

        if context.scene.kkbp.armature_dropdown == 'B':
            bpy.ops.kkb.rigifyconvert('INVOKE_DEFAULT')
            bpy.ops.kkb.rigifyconvert('INVOKE_DEFAULT')

        return {'FINISHED'}

if __name__ == "__main__":
    bpy.utils.register_class(quick_import)
    bpy.ops.kkb.quickimport('INVOKE_DEFAULT')
    bpy.utils.register_class(mat_import)