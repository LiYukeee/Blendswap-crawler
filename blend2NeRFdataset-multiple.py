#!/lv01/home/liyuke/anaconda3/envs/blendswap/bin/ python
import subprocess
import pandas as pd
import zipfile
import shutil
import os
import signal
import shlex
import threading


data_fold = 'data'
nerf_data_fold = 'nerf-data'
csv_path = 'data.csv'
max_render_time = 3000  # 单个文件的最大渲染时间
render_img_count = 300  # 设定的渲染图片数量
num_threads = 8  # 最大线程数量
lock = threading.Lock()  # 定义一个共享锁

# 读取文件
try:
    df = pd.read_csv(csv_path)
except:
    df = pd.read_csv(csv_path, encoding='gbk')


def blend2nerfdata(blend_path, max_render_time=max_render_time):
    """
    .blend -> nerf dataset
    """
    # 确保blender脚本路径正确
    blender_script_path = "/home/liyuke/script/blend-script.py"
    if not os.path.isfile(blender_script_path):
        print(f"Error: The script file {blender_script_path} does not exist.")
        return False
    # 构建blender命令
    command = "blender -b {} --python {}".format(blend_path, blender_script_path)
    print('-' * 100, '\ncommand: ')
    print(command)
    args = shlex.split(command)
    # 启动监控Blender进程的子进程
    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    # 定义一个函数来发送SIGTERM信号给Blender进程
    def terminate_process(process):
        os.kill(process.pid, signal.SIGTERM)
    # 使用一个循环监控进程和时间
    try:
        # 等待进程结束或超时
        process.wait(timeout=max_render_time)
    except subprocess.TimeoutExpired:
        print('-' * 100, '\nerror message: ')
        print("Command timed out after {} seconds".format(max_render_time))
        terminate_process(process)  # 超时后终止Blender进程
        return False
    else:
        # 获取标准输出和错误输出
        stdout, stderr = process.communicate()
        if process.returncode == 0:
            print('-' * 100, '\nerror message: ')
            print("Blender process exited successfully.")
            return True
        else:
            print('-' * 100, '\nerror message: ')
            print(stdout)
            print(stderr)
            return False

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


def work():
    global df
    for index in range(0, len(df)):
        with lock:
            line = df.iloc[index]
            if line.is_download == 'yes' and line.nerf_data_path == 'no':
                # 写入df进行标记，表示正s在运行这一项
                df.loc[index, ['nerf_data_path']] = 'running'
                df.to_csv(csv_path, index=False)
            else:
                continue
        # 在标记之后开始渲染
        print('-' * 100)
        print('start:',line.id)
        render_res = False
        blend_file_path = line.path
        if blend2nerfdata(blend_file_path):
            # 命令执行完毕，没有报错
            zip_file_path = nerf_data_fold + '/' + str(line.id) + '.zip'
            if judge_zip(zip_file_path):  # 如果zip文件也验证无误
                # 运行成功
                with lock:
                    df.loc[index, ['nerf_data_path']] = zip_file_path
                    df.to_csv(csv_path, index=False)
                print('-' * 100)
                print('success', line.id)
                continue
        # 运行失败
        # 渲染结束写入
        with lock:
            df.loc[index, ['nerf_data_path']] = 'error'
            df.to_csv(csv_path, index=False)
        print('-' * 100)
        print('error', line.id)

def main():
    threads = []
    for _ in range(num_threads):
        thread = threading.Thread(target=work)
        thread.start()
        threads.append(thread)

if __name__ == '__main__':
    main()
