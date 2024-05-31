#!/lv01/home/liyuke/anaconda3/envs/blendswap/bin/ python
import subprocess
import pandas as pd
import zipfile
import shutil
import os
# import signal


data_fold = 'data'
nerf_data_fold = 'nerf-data'
csv_path = 'data.csv'
max_render_time = 1200  # 单个文件的最大渲染时间
render_img_count = 300  # 设定的渲染图片数量


def blend2nerfdata(blend_path):
    """
    .blend -> nerf dataset
    """
    # 要把blender加入路径，否则用完整的blender路径
    # blender -b xxx.blend --python blend-script.py
    # blender无窗口模式启动并自动执行python脚本
    command = "blender -b {} --python  /home/liyuke/script/blend-script.py".format(blend_path)
    try:
        result = subprocess.run(command, shell=True, check=True, universal_newlines=True, encoding='utf-8', timeout=max_render_time)
        return True
    except subprocess.TimeoutExpired:
        # 存在问题，超时之后，指令仍在运行，没有终止
        # 不过超时运行的都是有问题的
        print('-' * 100, '\nerror message: ')
        print("Command timed out after {} seconds".format(max_render_time))
        return False
    except subprocess.CalledProcessError as e:
        output = e.output
        print('-' * 100, '\nerror message: ')
        print(output)
        return False
    

def judge_zip(zip_path):
    """
    判断zip文件是否合理，包含train中{render_img_count}张图片，transforms_test.json和transforms_train.json
    """
    target_path = './zip_path_temp'
    try:
        zip_ref = zipfile.ZipFile(zip_path, 'r')
        zip_ref.extractall(target_path)  # 解压缩目标路径
        zip_ref.close()
        res = True
        # 判断.json文件是否存在
        res = res and os.path.isfile(os.path.join(target_path, 'transforms_train.json'))
        res = res and os.path.isfile(os.path.join(target_path, 'transforms_test.json'))
        items = os.listdir(os.path.join(target_path, 'train'))
        items_count = len(items)
        # 判断train中的图片数量是否为整百
        if items_count == render_img_count:
            res = res and True
        else:
            res = res and False
        shutil.rmtree(target_path)  # 清空临时文件夹
        return res
    except:
        return False


def main():
    # 读取文件
    try:
        df = pd.read_csv(csv_path)
    except:
        df = pd.read_csv(csv_path, encoding='gbk')
    for index in range(0, len(df)):
        line = df.iloc[index]
        if line.is_download == 'yes' and line.nerf_data_path == 'no':
            blend_file_path = line.path
            print('-' * 100)
            print('start:',line.id)
            if blend2nerfdata(blend_file_path):
                # 命令执行完毕，没有报错
                zip_file_path = nerf_data_fold + '/' + str(line.id) + '.zip'
                if judge_zip(zip_file_path):  # 如果zip文件也验证无误
                    # 运行成功
                    df.loc[index, ['nerf_data_path']] = zip_file_path
                    df.to_csv(csv_path, index=False)
                    print('-' * 100)
                    print('success', line.id)
                    continue
            # 运行失败
            df.loc[index, ['nerf_data_path']] = 'error'
            df.to_csv(csv_path, index=False)
            print('-' * 100)
            print('error', line.id)
            continue
    return


if __name__ == '__main__':
    main()
