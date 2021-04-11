import bpy
import itertools
import random

def clearScene():
    for c in scene.collection.children:
            for o in c.objects:
                bpy.data.objects.remove(o)
                
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)

    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)

    for block in bpy.data.textures:
        if block.users == 0:
            bpy.data.textures.remove(block)

    for block in bpy.data.images:
        if block.users == 0:
            bpy.data.images.remove(block)

if __name__ == '__main__':
    savepath = "D:\\3D_Models\\Characters\\" # <- Change this

    bpy.context.area.type = 'VIEW_3D'

    scene = bpy.context.scene

    genders = ['m', 'f']
    races = ['af', 'as', 'ca', 'la']
    ages = [-0.6, 0, 0.5]

    comb_base_setting = list(itertools.product(genders, races, ages))

    for (g,r,a) in comb_base_setting:
        # bpy.ops.wm.open_mainfile(filepath="C:/Users/HP/Documents/Blender_Models/_empty.blend")
        clearScene()

        scene.mblab_use_eevee = True
        scene.mblab_use_lamps = False

        scene.mblab_character_name = g + '_' + r + '01'

        # bpy.ops.object.editmode_toggle()
        bpy.ops.mbast.init_character()

        bpy.context.object.character_age = a # -1, 1
        # bpy.context.object.character_mass = 0.39 # 0, 1

        scene.mblab_random_engine = 'RE' # realistic , 'NO': noticable
        
        # Random generator

        scene.mblab_preserve_height = True
        scene.mblab_preserve_fantasy = True
        bpy.ops.mbast.character_generator()

        # Skin & Eyes
        eyes_hue = random.random()
        skin_oil = random.random()
        bpy.context.object.eyes_hue = eyes_hue # 0 - 1
        bpy.context.object.eyes_iris_mix = eyes_hue # 0 - 1
        # bpy.context.object.skin_complexion = 0.2 # 0.2 - 0.6
        bpy.context.object.skin_oil = skin_oil # 0 - 1

        bpy.data.objects[scene.mblab_character_name + "_skeleton"].rest_pose = 'ii-pose'

        # Finalize

        scene.mblab_save_images_and_backup = False
        for collection in bpy.data.collections:
               if collection.name != "MB_LAB_Character":
                    continue
               for obj in collection.all_objects:
                   if obj.type != 'ARMATURE':
                        continue
                   print('   obj: ', obj.name)
                   bpy.context.view_layer.objects.active = obj
                   bpy.ops.object.modifier_apply(apply_as='DATA', modifier="mbastlab_armature")
                   # bpy.ops.pose.armature_apply()
                   break
        bpy.ops.mbast.finalize_character()

        bpy.ops.wm.save_as_mainfile(filepath=savepath + g + '_' + r + str(int((a * 31)+49)) + '.blend')

        bpy.context.area.type = 'TEXT_EDITOR'