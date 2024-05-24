import subprocess
import pandas as pd

data_fold = 'data'
nerf_data_fold = 'nerf-data'
csv_path = 'data.csv'


def blend2nerfdata(blend_path):
    """
    .blend -> nerf dataset
    """
    # 要把blender加入路径，否则用完整的blender路径
    # blender -b xxx.blend --python blend-script.py
    # blender无窗口模式启动并自动执行python脚本
    command = "blender -b {} --python blend-script.py".format(blend_path)
    try:
        # 捕获输出
        output = subprocess.check_output(command, shell=True, universal_newlines=True, encoding='utf-8')
        return True
    except subprocess.CalledProcessError as e:
        output = e.output
        print('-' * 100, '\nerror message: ')
        print(output)
        return False


def main():
    try:
        df = pd.read_csv(csv_path)
    except:
        df = pd.read_csv(csv_path, encoding='gbk')
    for index in range(0, len(df)):
        line = df.iloc[index]
        if line.is_download == 'yes' and line.nerf_data_path == 'no':
            blend_file_path = line.path
            if blend2nerfdata(blend_file_path):
                # 运行成功
                df.loc[index, ['nerf_data_path']] = nerf_data_fold + '/' + str(line.id) + '.zip'
                df.to_csv(csv_path, index=False)
                print('-' * 100)
                print('success', line.id)
            else:
                # 运行失败，可能是blender和模型版本不匹配
                print('-' * 100)
                print('error', line.id)
                continue
    return


if __name__ == '__main__':
    main()
