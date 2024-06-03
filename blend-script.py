"""
用blender调用的python脚本
调用的是blender中的python解释器
"""
import bpy
import mathutils
import os
from mathutils import Vector
import random 
import bmesh


render_img_count = 300  # 设定的渲染图片数量
gpu_index_list  = [1, 2, 3]  # 一个列表，表示要用的设备的序号，编号是从零开始
gpu_index = random.choice(gpu_index_list)
print('gpu_index:', gpu_index)


def change_type(type = 2):
    """
    更改预览模式
    """
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            # 获取3D视图的space_data
            space_data = area.spaces.active
            # 更改渲染模式
            # 设置为材质预览模式
            if type == 1:
                space_data.shading.type = 'SOLID'
            elif type == 2:
                space_data.shading.type = 'MATERIAL'
            elif type == 3:
                space_data.shading.type = 'RENDERED'


def object_mode():
    """
    转换到object模式
    """
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.view_layer.update()
    for obj in bpy.context.view_layer.objects:
        if obj.type == 'MESH':
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.select_all(action='DESELECT')
            return


def costume_scene():
    """
    对场景和渲染的自定义修改
    """
    # --------------------------------------------------------------
    # 输出OutPut设置
    bpy.context.scene.render.resolution_x = 800
    bpy.context.scene.render.resolution_y = 800
    bpy.context.scene.render.resolution_percentage = 100
    bpy.context.scene.render.image_settings.file_format = 'PNG'  # 文件格式
    bpy.context.scene.render.use_file_extension = True  # 保留后缀
    bpy.context.scene.render.image_settings.color_mode = 'RGBA'  # 颜色格式
    bpy.context.scene.cycles.preview_samples = 512  # 采样-视图-最大采样
    bpy.context.scene.cycles.samples = 512  # 采样-渲染-最大采样
    bpy.context.scene.render.film_transparent = True  # 设置背景为透明：胶片-透明
    # --------------------------------------------------------------
    # 帧设置
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 300  # 设置结束帧为300
    # --------------------------------------------------------------
    # 删除关键帧
    for obj in bpy.data.objects:
        obj.animation_data_clear()
    # --------------------------------------------------------------
    # 渲染设置，使用GPU加速渲染
    bpy.context.scene.render.engine = 'CYCLES'  # 选择渲染引擎
    bpy.context.preferences.addons['cycles'].preferences.compute_device_type = 'OPTIX'  # 使用NVIDIA光线追踪渲染
    devices = bpy.context.preferences.addons['cycles'].preferences.get_devices_for_type('OPTIX')  # 获取所有设备
    for index, device in enumerate(devices):
        device.use = (index == gpu_index)
    bpy.context.scene.cycles.device = 'GPU'  # 选择GPU计算
    return


def costume_addon_setting():
    """
    对插件的自定义修改
    """
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
    bpy.context.scene.sphere_radius = 3.0
    bpy.context.scene.focal = 30.0
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
    for i in range(4):
        try:
            bpy.context.scene.camera = bpy.data.objects["BlenderNeRF Camera"]
        except:
            if i % 2 == 0:
                bpy.context.scene.show_camera = False
            else:
                bpy.context.scene.show_camera = True
    return


def convert():
    """
    转换为mesh、合并物体、应用变换、简化场景
    """
    # 确保在对象模式
    object_mode()
    # 选择所有对象
    bpy.ops.object.select_all(action='SELECT')
    # 创建一个列表，用于存储要删除的物体
    objects_to_remove = [obj for obj in bpy.data.objects if not obj.select_get()]
    # 确认有对象被选中
    if bpy.context.selected_objects:
        # 转换选中的对象为网格
        bpy.ops.object.convert(target='MESH')
        # bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN') # 设置中心点为几何中心
        # 取消选择非mesh类型的对象，有些对象不能转化成mesh
        for obj in bpy.context.selected_objects:
            if obj.type != 'MESH':
                obj.select_set(False)
        bpy.ops.object.join()  # 合并物体
        bpy.context.active_object.name = 'merge_object'
        # todo 存在问题：尝试对一个多用户对象（通常是网格或者物体）进行某种修改或应用某种操作，但是这个操作要求对象不被多个用户共享。
        try:
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True) # 应用变换
        except:
            print('error: bpy.ops.object.transform_apply()')
    else:
        print("没有选中的对象可进行转换。")
    # 遍历列表并删除每个未选中的物体
    for obj in objects_to_remove:
        bpy.data.objects.remove(obj, do_unlink=True)
    # 更新视图层
    bpy.context.view_layer.update()


def scale_object():
    """
    将指定物体的缩放比例调整，使其最大维度为1单位长度
    参数：
    - target_object: 要缩放的目标物体
    """
    target_object=bpy.data.objects.get("merge_object")
    bpy.context.view_layer.objects.active = target_object
    # 确定缩放因子
    scale_factor = 2 / max(target_object.dimensions)
    # 应用缩放
    target_object.scale *= scale_factor
    # 更新视图层
    bpy.context.view_layer.update()
    # 设置中心点为几何中心
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
    # 移动到零点
    target_object.location -= target_object.location
    

def get_bounding_box_dimensions(obj):
    """
    计算一个物体的bounding box的长宽高
    """
    if obj.type == 'MESH':
        # 确保物体的矩阵变换被应用
        bpy.context.view_layer.update()
        # 获取经过世界坐标变换的边界盒顶点
        bbox_corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
        # 计算X, Y, Z轴上的最大值和最小值
        x_coords = [v.x for v in bbox_corners]
        y_coords = [v.y for v in bbox_corners]
        z_coords = [v.z for v in bbox_corners]
        # 计算长度，宽度和高度
        length = max(x_coords) - min(x_coords)
        width = max(y_coords) - min(y_coords)
        height = max(z_coords) - min(z_coords)
        return (length, width, height)
    else:
        return None
    

def is_plane_bbox(obj):
    # todo 存在问题，如果是倾斜放置的平面，则不符合要求
    """
    该物体是否是平面？

    这样的方法只能判断出横平竖直的平面
    如果这个物体的bounding box的长宽高至少有一项为零则判断为平面
    其实也有可能是线条或者点
    不过符合要删除对象的要求
    """
    if obj.type != 'MESH':
        return False
    length, width, height = get_bounding_box_dimensions(obj)
    if length * width * height == 0.0:
        return True
    else:
        return False


def is_plane_normal(obj):
    # 确保对象是选中状态并且类型为MESH
    if obj is not None and obj.type == 'MESH':
        # 切换到编辑模式
        bpy.ops.object.mode_set(mode='EDIT')
        # 创建一个bmesh对象，这样我们可以操作mesh
        bm = bmesh.from_edit_mesh(obj.data)
        bm.faces.ensure_lookup_table()
        # 选中的面
        face = bm.faces.active
        if face is not None:
            # 计算面的法线
            face_normal = face.normal
            # 遍历面的所有顶点
            for vert in face.verts:
                # 计算从此顶点到另一个顶点的向量
                for edge in vert.link_edges:
                    other_vert = edge.other_vert(vert)
                    # 创建一个从当前顶点到另一个顶点的向量
                    edge_vector = (other_vert.co - vert.co).normalized()
                    # 计算此向量与面法线的点积
                    dot_product = edge_vector.dot(face_normal)
                    # 如果点积不接近0，则面不是平面
                    if not abs(dot_product) < 0.0001:
                        return False
            return True
        else:
            print("No active face selected.")
            return False
    else:
        print("No active mesh object selected.")
        return False
    

def is_plane_volume(obj):
    if obj.type != 'MESH':
        return False
    mesh = obj.data
    volume = 0.0
    for poly in mesh.polygons:
        # 获取多边形的顶点索引
        verts = [mesh.vertices[i] for i in poly.vertices]
        # 计算多边形的面积
        area = poly.area
        # 计算多边形的法向量
        normal = poly.normal
        # 计算多边形的体积贡献
        volume += area * obj.matrix_world.to_scale().x * normal.x / 3.0
        # print(volume, obj)
    if volume == 0.0:
        return True
    else:
        return False


def plane():
    """
    该物体是否是平面？
    方法1：如果这个物体的bounding box的长宽高至少有一项为零则判断为平面
    其实也有可能是线条或者点
    不过符合要删除对象的要求
    如果是倾斜放置的平面则无法检测
    方法2：判断体积是否为零
    """
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            if is_plane_normal(obj):
                print(obj)


def delete_obj():
    """
    删除光源和平面

    一般场景中会有一个或者多个平面，这些平面有些是当作地面，也有些是当作自发光光源
    对于平面不能简单的用名称是否包含plane来处理，因为很多情况下有些物体的组件的名称也是plane
    （blend文件作者可能先生成plane之后将其变形成自己想要的形状，而之后没有进行重命名）
    还有一些平面的名称不包含plane，故要对所有的mesh物体进行形状检测
    """
    object_mode()
    # 删除光源，因为后续会添加统一的光源
    lights_to_remove = [obj for obj in bpy.data.objects if obj.type == 'LIGHT']
    for light in lights_to_remove:
        bpy.data.objects.remove(light)
    # 删除平面类型
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            if is_plane_bbox(obj) or is_plane_volume(obj) or 'plane' in obj.name.lower():  #  or 'plane' in obj.name.lower()
                bpy.data.objects.remove(obj)
    # 删除EMPTY类型对象
    for obj in bpy.data.objects:
        if obj.type == 'EMPTY':
            bpy.data.objects.remove(obj)
    # 删除相机类型
    for obj in bpy.data.objects:
        if obj.type == 'CAMERA':
            bpy.data.objects.remove(obj)
    return


def move_to_center():
    """
    根据物体的bbox移动到零点
    """
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

def delete_amature():
    """
    删除骨骼
    """
    object_mode()
    # 删除骨骼
    for obj in bpy.data.objects:
        if obj.type == 'ARMATURE':
            bpy.data.objects.remove(obj)
    return


def lamp():
    """
    创建并放置多个光源，环绕物体
    """
    positions = [
        (1.5, 0, 0), (-1.5, 0, 0), (0, 1.5, 0), (0, -1.5, 0), 
        (1, 1, 0), (1, -1, 0), (-1, 1, 0), (-1, -1, 0),
        (0, 0, 1.5), (0, 0, -1.5)
        ]
    energies = [15, 15, 15, 15, 15, 15, 15, 15, 15, 15]  # 调整每个光源的能量值
    radius = 1
    for i, pos in enumerate(positions):
        light_data = bpy.data.lights.new(name=f'Light_{i}', type='POINT')
        light_object = bpy.data.objects.new(name=f'Light_{i}', object_data=light_data)
        bpy.context.collection.objects.link(light_object)
        light_object.location = pos
        light_data.energy = energies[i]  # 设置光源的能量值
        light_data.shadow_soft_size = radius
    bpy.context.view_layer.update()


bpy.ops.preferences.addon_disable(module="BlenderNeRF-main")  # 禁用插件

delete_obj()  # 删除光源和平面
bpy.context.view_layer.update() # 这一步非常关键，相当于等待指令执行完毕，场景更新完毕。

costume_scene()  # 渲染设备、输出设置
bpy.context.view_layer.update() 

for _ in range(2):
    try:
        convert()  # 转换和简化模型
        bpy.context.view_layer.update()
    except:
        _
bpy.context.view_layer.update()

scale_object()  # 缩放并放置到中心
bpy.context.view_layer.update()

delete_amature() # 删除骨骼
bpy.context.view_layer.update()

move_to_center()
bpy.context.view_layer.update()

lamp() # 添加光源
bpy.context.view_layer.update()

bpy.ops.preferences.addon_enable(module="BlenderNeRF-main")  # 启用插件
costume_addon_setting() # 设置插件
bpy.context.view_layer.update()

bpy.ops.object.camera_on_sphere()  # 点击PLAY COS按钮