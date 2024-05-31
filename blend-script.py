"""
用blender调用的python脚本
调用的是blender中的python解释器
"""
import bpy
import mathutils
import os
from mathutils import Vector
import random 

render_img_count = 300  # 设定的渲染图片数量
gpu_index_list  = [1,2,3]  # 一个列表，表示要用的设备的序号，编号是从零开始
gpu_index = random.choice(gpu_index_list)
print('gpu_index:', gpu_index)

def costume_scene():  # 对场景和渲染的自定义修改
    # bpy.ops.object.select_all(action='DESELECT')
    # --------------------------------------------------------------
    # 删除关键帧
    for obj in bpy.data.objects:
        obj.animation_data_clear()
    # 渲染设置，使用GPU加速渲染
    # --------------------------------------------------------------
    bpy.context.scene.render.engine = 'CYCLES'  # 选择渲染引擎
    bpy.context.preferences.addons['cycles'].preferences.compute_device_type = 'OPTIX'  # 使用NVIDIA光线追踪渲染
    devices = bpy.context.preferences.addons['cycles'].preferences.get_devices_for_type('OPTIX')  # 获取所有设备
    for index, device in enumerate(devices):
        device.use = (index == gpu_index)
    bpy.context.scene.cycles.device = 'GPU'  # 选择GPU计算
    bpy.context.scene.cycles.preview_samples = 512  # 采样-视图-最大采样
    bpy.context.scene.cycles.samples = 512  # 采样-渲染-最大采样
    bpy.context.scene.render.film_transparent = True  # 设置背景为透明：胶片-透明
    # --------------------------------------------------------------
    # 删除名为 plane 或者名字包含 plane 的对象
    # bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.data.objects:
        if 'plane' in obj.name.lower():
            obj.select_set(True)
            bpy.ops.object.delete()
    # --------------------------------------------------------------
    # 输出OutPut设置
    bpy.context.scene.render.resolution_x = 800
    bpy.context.scene.render.resolution_y = 800
    bpy.context.scene.render.image_settings.file_format = 'PNG'  # 文件格式
    bpy.context.scene.render.use_file_extension = True  # 保留后缀
    bpy.context.scene.render.image_settings.color_mode = 'RGBA'  # 颜色格式
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
    # bpy.ops.object.select_all(action='DESELECT')
    # --------------------------------------------------------------
    # 插件设置
    bpy.context.scene.train_data = True
    bpy.context.scene.test_data = True
    # 生成相机BlenderNerf相机
    bpy.context.scene.show_sphere = True
    bpy.context.scene.show_camera = True
    # 只取上半球面
    bpy.context.scene.upper_views = False
    # 设置相机半径，如何计算
    bpy.context.scene.sphere_radius = 2.0  # 放入bounding box(-1, -1, -1)-(1, 1, 1)之后选取半径为5，可以看到各个部分
    bpy.context.scene.focal = 50.0
    # 设置采集帧数量
    bpy.context.scene.cos_nb_frames = render_img_count
    # 设置保存位置
    file_path = bpy.data.filepath
    folder_path = os.path.dirname(file_path)  # ./data
    folder_path = os.path.join(os.path.dirname(folder_path), 'nerf-data')  # ./nerf-data
    file_name = bpy.path.display_name_from_filepath(file_path)
    bpy.context.scene.save_path = folder_path
    # 设置数据集名字
    bpy.context.scene.cos_dataset_name = file_name
    # 设置相机
    for i in range(10):
        try:
            bpy.context.scene.camera = bpy.data.objects["BlenderNeRF Camera"]
        except:
            if i % 2 == 0:
                bpy.context.scene.show_camera = False
            else:
                bpy.context.scene.show_camera = True
    return


def other2mesh():
    # 将所有类型转化成mesh对象，方便合并
    # 遍历所有对象
    # bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.data.objects:
        # 检查对象类型是否为可转换类型
        if obj.type in {'CURVE', 'SURFACE', 'FONT', 'META', 'POINTCLOUD'}:
            bpy.context.view_layer.objects.active = obj  # 设置为活动对象
            # bpy.ops.object.select_all(action='DESELECT')  # 取消选择所有其他对象
            obj.select_set(True)  # 选择当前对象
            bpy.ops.object.convert(target='MESH')  # 转换为mesh


# def merge():
#     # bpy.ops.object.select_all(action='DESELECT')  # 取消选择所有对象
#     for obj in bpy.data.objects:
#         if obj.type == 'MESH':
#             obj.select_set(True)
#     bpy.context.view_layer.objects.active = next(obj for obj in bpy.data.objects if obj.select_get() and obj.type == 'MESH')
#     bpy.ops.object.join()


# def merge():  # 合并物体
#     # bpy.ops.object.select_all(action='DESELECT')
#     clones = []
#     # 遍历场景中的所有物体
#     for obj in bpy.context.scene.objects:
#         # 只处理可见的物体
#         if obj.type == 'MESH':
#             # 复制物体 
#             clone = obj.copy()
#             clone.data = obj.data.copy()
#             clones.append(clone)
#             bpy.context.collection.objects.link(clone)  # 将复制的物体链接到当前集合
#     # 确保新复制的物体都被选中，原始的物体被取消选中
#     for obj in bpy.context.scene.objects:
#         obj.select_set(obj in clones)
#     # 设置活动对象为新复制的物体中的一个
#     bpy.context.view_layer.objects.active = clones[0] if clones else None
#     # 合并所有选中的物体
#     if clones:
#         bpy.ops.object.join()
#     # 删除原始的可见物体
#     for obj in bpy.context.scene.objects:
#         if obj.visible_get() and obj.type == 'MESH' and obj not in clones:
#             bpy.data.objects.remove(obj, do_unlink=True)
#     # 更新场景
#     bpy.context.view_layer.update()


def delete_unvisable():  # 删除不可见物体
    # bpy.ops.object.select_all(action='DESELECT')
    # 遍历场景中的所有物体
    for obj in bpy.context.scene.objects:
        # 检查物体的可见性
        if not obj.visible_get():
            # 删除不可见的物体
            bpy.data.objects.remove(obj, do_unlink=True)
    # 更新场景
    bpy.context.view_layer.update()


def remove_all_special():
    """
    解除物体之间的连接，钩子，父子关系，骨骼绑定，并保持原始位置，这一步需要在移动物体之前完成
    """
    # 遍历所有物体
    for obj in bpy.data.objects:
        # 选择对象作为操作的活动对象
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        # 检查物体是否是网格并且是否含有形态键
        if obj.type == 'MESH' and obj.data.shape_keys:
            # 删除所有形态键
            bpy.context.object.active_shape_key_index = 0
            bpy.ops.object.shape_key_add(from_mix=True)
            try:
                while obj.data.shape_keys.key_blocks:
                    bpy.ops.object.shape_key_remove(all=False)
            except:
                a = 1
        # 如果物体是网格，并且有绑定的骨骼修饰符
        if obj.type == 'MESH':
            armature_modifiers = [mod for mod in obj.modifiers if mod.type == 'ARMATURE']
            for mod in armature_modifiers:
                # 应用骨骼修饰符
                bpy.ops.object.modifier_apply(modifier=mod.name)
        # 对允许的物体类型应用位置、旋转和缩放变换
        if obj.type in {'MESH', 'CURVE', 'SURFACE', 'FONT', 'VOLUME', 'META', 'LATTICE'}:
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        # 清除父对象，保持变换
        if obj.parent:
            bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
        # 清除所有约束
        obj.constraints.clear()
        # 清除与钩子的关联，假设钩子作为修饰符实现
        for mod in obj.modifiers:
            if mod.type == 'HOOK':
                obj.modifiers.remove(mod)
        # 取消选择当前对象，为下一个操作做准备
        obj.select_set(False)
    # 更新场景，确保所有变化生效
    bpy.context.view_layer.update()

def move_to_center():
    # 初始化最大和最小坐标向量
    min_coord = Vector((float('inf'), float('inf'), float('inf')))
    max_coord = Vector((float('-inf'), float('-inf'), float('-inf')))
    # 遍历场景中的所有物体
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            # 将每个顶点转换到世界坐标系，更新最小和最大坐标
            for vertex in obj.data.vertices:
                world_vertex = obj.matrix_world @ vertex.co
                min_coord = Vector(min(min_coord[i], world_vertex[i]) for i in range(3))
                max_coord = Vector(max(max_coord[i], world_vertex[i]) for i in range(3))
    # 打印结果
    print("min:", min_coord)
    print("max:", max_coord)
    offset = (min_coord + max_coord) / 2
    print('center:', offset)
    for obj in bpy.data.objects:
        # 只对能移动的物体类型进行操作，如 'MESH', 'CURVE', 等
        if obj.type == 'MESH':
            obj.location -= offset

def merge_mesh():
    # 确保在对象模式下
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    # bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
    if len(bpy.context.selected_objects) > 1:
        bpy.ops.object.join()

def center_and_scale_scene():  # 将场景中心置于(0, 0, 0)并缩放至指定的bounding box
    # bpy.ops.object.select_all(action='DESELECT')
    scene = bpy.context.scene
    for obj in scene.objects:
        if obj.type == 'MESH':
            # 选择物体
            obj.select_set(True)
            scene.view_layers[0].objects.active = obj
            break
    obj = bpy.context.active_object
    # 计算中心并移动物体
    center = sum((Vector(b) for b in obj.bound_box), Vector()) / 8
    obj.location -= obj.matrix_world @ center
    # 确定缩放因子
    scale_factor = 1 / max(obj.dimensions)
    # 应用缩放
    obj.scale *= scale_factor
    bpy.context.view_layer.update()

def lamp():
    # bpy.ops.object.select_all(action='DESELECT')
    # 删除所有现有的光源
    bpy.ops.object.select_by_type(type='LIGHT')
    bpy.ops.object.delete()
    # 创建并放置多个光源，环绕物体
    positions = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
    energies = [15, 15, 15, 10, 8, 8]  # 调整每个光源的能量值
    for i, pos in enumerate(positions):
        light_data = bpy.data.lights.new(name=f'Light_{i}', type='POINT')
        light_object = bpy.data.objects.new(name=f'Light_{i}', object_data=light_data)
        bpy.context.collection.objects.link(light_object)
        light_object.location = pos
        light_data.energy = energies[i]  # 设置光源的能量值
    bpy.context.view_layer.update()


# -----------------------------------------
# # 安装blender脚本拓展BlenderNeRF
# addon_filepath = '/lv01/home/liyuke/software/package/BlenderNeRF-main.zip'  # 替换为插件zip文件的路径
# bpy.ops.preferences.addon_install(overwrite=True, filepath=addon_filepath) # 安装插件
# -----------------------------------------
bpy.ops.preferences.addon_enable(module="BlenderNeRF-main")  # 启用插件
costume_scene()  # 场景和渲染设置
other2mesh()  # 把可以转化成mesh的类别转化成mesh类别
remove_all_special()  # 删除特殊关系
merge_mesh() # 合并物体
delete_unvisable() # 删除不可视物体
center_and_scale_scene()  # 缩放到boundingbox
move_to_center()  # 移动到零点
lamp()  # 光源设置
costume_addon_setting()  # 插件设置
bpy.ops.object.camera_on_sphere()  # 点击PLAY COS按钮
