import zipfile
import os
import shutil

unzip_file = 'tempfile'
data_path = 'data'


def unzip(zip_file_path, target_path):
    # 创建ZipFile对象
    zip_ref = zipfile.ZipFile(zip_file_path, 'r')
    # 解压缩文件
    zip_ref.extractall(target_path)  # 解压缩目标路径
    # 关闭ZipFile对象
    zip_ref.close()


def find_blend_files(folder_path):
    """
    找到一个路径下的所有.blend后缀文件
    """
    blend_files = []  # 用于存储找到的.blend文件路径
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".blend"):
                blend_files.append(os.path.join(root, file))
    return blend_files


def rename_file(src_file, new_name):
    # 获取文件所在的目录路径
    dir_path = os.path.dirname(src_file)
    # 构建新的文件路径
    new_file_path = os.path.join(dir_path, new_name)
    # 重命名文件
    os.rename(src_file, new_file_path)
    return new_file_path


def move(src_file, dst_file):
    # 覆盖移动
    if os.path.exists(dst_file):
        os.remove(dst_file)
    shutil.move(src_file, dst_file)
    return


def main():
    start_id = 1500
    end_id = 40000
    zip_file_path = os.path.join(data_path, "{}.blend")  # ZIP文件的路径
    for id in range(start_id, end_id + 1):
        try:
            # 解压，但有些blend可能不是压缩文件，同时也可以跳过不存在的文件
            unzip(zip_file_path.format(id), unzip_file)
        except:
            continue
        blend_files = find_blend_files(unzip_file)  # 找到所有的blend文件
        print('---', id, ''.join(blend_files))
        for i in range(len(blend_files)):
            # 一个压缩包中可能包含多个blend文件，极少数情况
            if i == 0:
                file_name = str(id) + '.blend'
            else:
                file_name = str(id) + '-{}.blend'.format(i)
            blend_files[i] = rename_file(blend_files[i], file_name)
            move(blend_files[i], os.path.join(data_path, file_name))  # 覆盖移动
        shutil.rmtree(unzip_file)  # 清空临时文件夹
    return


if __name__ == '__main__':
    main()
