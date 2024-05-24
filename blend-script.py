"""
用blender调用的python脚本
调用的是blender中的python解释器
"""
import bpy
import os


def costume_scene():  # 对场景和渲染的自定义修改
    # --------------------------------------------------------------
    # 删除关键帧
    for obj in bpy.data.objects:
        obj.animation_data_clear()
    # 渲染设置
    bpy.context.scene.render.engine = 'CYCLES'  # 选择渲染引擎
    bpy.context.scene.cycles.device = 'GPU'  # 选择GPU计算
    bpy.context.scene.cycles.preview_samples = 512  # 采样-视图-最大采样
    bpy.context.scene.cycles.samples = 512  # 采样-渲染-最大采样
    bpy.context.scene.render.film_transparent = True  # 胶片-透明
    # --------------------------------------------------------------
    # 输出OutPut设置
    bpy.context.scene.render.resolution_x = 800
    bpy.context.scene.render.resolution_y = 800
    bpy.context.scene.render.image_settings.file_format = 'PNG'  # 文件格式
    bpy.context.scene.render.use_file_extension = True  # 保留后缀
    bpy.context.scene.render.image_settings.color_mode = 'RGBA'  # 颜色格式
    # --------------------------------------------------------------
    # 物体设置
    try:
        bpy.context.object.visible_camera = False  # 若场景中存在背景/平面，则需要将其对摄像机隐藏
    except:
        a = 1
    # 选中所有对象
    for obj in bpy.context.scene.objects:
        if obj.type != 'CAMERA' and obj.type != 'EMPTY':
            obj.select_set(True)
    # 获取所选对象的中心位置
    selected_objs = [obj for obj in bpy.context.scene.objects if obj.select_get()]
    center = sum([obj.location for obj in selected_objs], bpy.context.scene.cursor.location) / len(selected_objs)
    # # todo 移动中心位置
    # # 将所选对象的中心移动到原点
    # for obj in selected_objs:
    #     obj.location -= center
    # 取消选择所有对象
    bpy.ops.object.select_all(action='DESELECT')
    # --------------------------------------------------------------
    # 帧设置
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 300  # 设置结束帧为300
    # --------------------------------------------------------------
    # # 删除所有的摄像机
    # for obj in bpy.context.scene.objects:
    #     # 判断对象类型是否为摄像机
    #     if obj.type == 'CAMERA':
    #         # 删除摄像机对象
    #         bpy.data.objects.remove(obj, do_unlink=True)
    return


def costume_addon_setting():  # 对插件的自定义修改
    # --------------------------------------------------------------
    # 插件设置
    bpy.context.scene.train_data = True
    bpy.context.scene.test_data = True
    # 生成相机BlenderNerf相机
    bpy.context.scene.show_sphere = True
    bpy.context.scene.show_camera = True
    # 设置相机
    bpy.context.scene.camera = bpy.data.objects["BlenderNeRF Camera"]
    # 只取上半球面
    bpy.context.scene.upper_views = True
    # 设置相机半径，如何计算 ?
    bpy.context.scene.sphere_radius = 4.0
    # 设置采集帧数量
    bpy.context.scene.cos_nb_frames = 100
    # 设置保存位置
    file_path = bpy.data.filepath
    folder_path = os.path.dirname(file_path)  # ./data
    folder_path = os.path.join(os.path.dirname(folder_path ), 'nerf-data')  # ./nerf-data
    file_name = bpy.path.display_name_from_filepath(file_path)
    bpy.context.scene.save_path = folder_path
    # 设置数据集名字
    bpy.context.scene.cos_dataset_name = file_name
    return


# 启用插件
bpy.ops.preferences.addon_enable(module="BlenderNeRF-main")
costume_scene()
costume_addon_setting()
# 点击PLAY COS按钮
bpy.ops.object.camera_on_sphere()
