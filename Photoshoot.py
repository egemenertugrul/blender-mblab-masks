import bpy
from os import walk
import numpy as np
from mathutils import Vector
import time

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

def loadBaseScene(path):
    with bpy.data.libraries.load(path) as (data_from, data_to):
            data_to.objects = [name for name in data_from.objects]
    for o in data_to.objects:
        if o is not None:
            bpy.context.collection.objects.link(o)

if __name__ == "__main__":
    # bpy.ops.wm.open_mainfile(filepath="C:/Users/HP/Documents/Blender_Models/_photoshoot.blend")
    character_loadpath = "D:\\3D_Models\\Characters\\" # <- Change this
    basescene_loadpath = "C:\\Users\\HP\\Documents\\Blender_Models\\_photoshoot.blend" # <- and this
    renderpath = "C:\\Users\\HP\\Pictures\\Blender\\Mask\\" # <- and this

    scene = bpy.context.scene
    files = []
    for (dirpath, dirnames, filenames) in walk(character_loadpath):
        files.extend(filenames)
        break
    
    for fname in files:
        if not fname.endswith(".blend"):
            continue
        
        clearScene()
        loadBaseScene(basescene_loadpath)
        
        filepath = character_loadpath + fname
        
        # Add humanoid to scene
        with bpy.data.libraries.load(filepath) as (data_from, data_to):
            data_to.objects = [name for name in data_from.objects]

        obj = None
        for o in data_to.objects:
            if o is not None:
                bpy.context.collection.objects.link(o)
                if o.type != 'ARMATURE':
                    obj = o
        
        vg_idx = obj.vertex_groups['head'].index
        vs = [ v for v in obj.data.vertices if vg_idx in [ vg.group for vg in v.groups ] ]
        temp = np.array([(v.co[0],v.co[1],v.co[2]) for v in vs])
        max = np.max(temp,axis=0)
        min = np.min(temp,axis=0)
        center = np.sum(temp, axis=0) / temp.shape[0]
        print(center)
        cv = center.tolist()
        cv = Vector(cv)
        mat = obj.matrix_world
        cloc = mat @ cv
        
        track_obj = bpy.data.objects.new( "track_obj", None )
        bpy.context.collection.objects.link(track_obj)
        track_obj.location = cloc
    
        # mask_obj = bpy.data.objects['mask']
        
        cam_obj = bpy.data.objects['Camera']
        bpy.context.scene.camera = cam_obj

        vp_obj = bpy.data.objects['Viewpoints']
        vp_obj.location = track_obj.location
        
        cam_obj.constraints["Track To"].target = track_obj
        cam_obj.constraints["Track To"].track_axis = 'TRACK_NEGATIVE_Z'
        cam_obj.constraints["Track To"].use_target_z = False
        cam_obj.constraints["Track To"].up_axis = 'UP_Y'

        vp_vs = vp_obj.data.vertices

        scene.frame_start=1
        scene.frame_end=len(vp_vs)
        
        for (f,v) in enumerate(vp_vs,1):
            cam_obj.location = vp_obj.matrix_world @ v.co
            cam_obj.keyframe_insert(data_path="location", frame=f)
        
        cam_obj.data.type = 'PERSP'
        cam_obj.data.lens = 104
        # cam_obj.data.type = 'ORTHO'
        # cam_obj.data.ortho_scale = 0.3
        cam_obj.data.shift_y = 0.13

        scene.render.resolution_x = 416
        scene.render.resolution_y = 416
        scene.view_layers["View Layer"].use = True
        
        scene.render.engine = 'BLENDER_EEVEE'
        scene.render.image_settings.file_format = 'PNG'
        scene.render.image_settings.color_mode = 'RGBA'
        scene.render.film_transparent = True
        
        for frame in range(scene.frame_start, scene.frame_end + 1):
            scene.render.filepath = renderpath + str(frame).zfill(4)
            scene.frame_set(frame)
            bpy.ops.render.render(write_still=True)
            time.sleep(3)
            
        break