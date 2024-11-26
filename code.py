import os  
import json  
import numpy as np  

def read_json_file(file_path):
   
    with open(file_path, 'r', encoding='utf-8') as f:
      
        return json.load(f)

def write_json_file(data, file_path):
    
    with open(file_path, 'w', encoding='utf-8') as f:
    
        json.dump(data, f, indent=4)

def invert_matrix(matrix):
    # 将输入的矩阵转换为NumPy数组，并重塑为4x4矩阵，然后计算其逆矩阵
    return np.linalg.inv(np.array(matrix).reshape(4, 4))

def dConver(matrix):
    # 将矩阵转换为4x4数组
    return np.array(matrix).reshape((4, 4))

def multiply_matrices(m1, m2):
    # 计算两个矩阵的点积，并将结果展平为一维列表返回
    return np.dot(m1, m2).flatten().tolist()

def get_src_layer_paths(directory):
    # 初始化源图层路径列表
    src_layer_paths = []
    # 遍历目录中的文件名
    for file_name in os.listdir(directory):
        # 检查文件名是否以Tileset开头并以.json结尾
        if file_name.endswith(".json") and file_name.startswith("Tileset"):
            # 将符合条件的文件路径添加到源图层路径列表中,使用os.path.join将目录路径和文件名拼接成完整路径
            src_layer_paths.append(os.path.join(directory, file_name))
    return src_layer_paths

def join_layer(join_layer_path, src_layer_paths, is_append):
    # 初始化合并配置和逆变换矩阵为None
    join_cfgo, join_trsf_inv = None, None
    # 打印开始合并的提示信息
    print(f"开始合并 {join_layer_path}...")
    
    for i, src_layer_path in enumerate(src_layer_paths):
        src_cfgo = read_json_file(src_layer_path)
        if not src_cfgo:
            continue  # 如果配置文件不存在，则跳过该图层
        
        if i == 0:
            if not is_append:
                # 如果不是追加模式，初始化合并配置文件
                join_cfgo = {
                    "asset": src_cfgo["asset"],
                    "geometricError": 4096,
                    "root": {
                        "boundingVolume": {
                            "box": []
                        },
                        "children": [],
                        "geometricError": 512,
                        "transform": src_cfgo["root"]["transform"]
                    }
                }
            else:
                # 如果是追加模式，读取现有的合并配置文件
                join_cfgo = read_json_file(os.path.join(join_layer_path, "tileset.json"))
            # 计算合并配置文件根节点变换矩阵的逆矩阵
            join_trsf_inv = invert_matrix(join_cfgo["root"]["transform"])
        
        # 计算源图层根节点变换矩阵相对于合并配置文件根节点的变换矩阵
        src_trsf = multiply_matrices(dConver(src_cfgo["root"]["transform"]),join_trsf_inv)
        src_rt_chos= src_cfgo["root"]
        src_rt_chos["transform"] = src_trsf
        join_cfgo["root"]["children"].append(src_rt_chos)
        print(f"{src_layer_path} 已合并。")

    join_rt_chs = join_cfgo["root"]["children"]
    max_x, min_x, max_y, min_y, max_z, min_z = [None] * 6
    for i, join_rt_ch in enumerate(join_rt_chs):
        o = [
            join_rt_ch["boundingVolume"]["box"][0] + join_rt_ch["transform"][12],
            join_rt_ch["boundingVolume"]["box"][1] + join_rt_ch["transform"][13],
            join_rt_ch["boundingVolume"]["box"][2] + join_rt_ch["transform"][14]
        ]
        r = [
            join_rt_ch["boundingVolume"]["box"][3],
            join_rt_ch["boundingVolume"]["box"][7],
            join_rt_ch["boundingVolume"]["box"][11]
        ]
        xa = [o[0] - r[0], o[0] + r[0]]
        ya = [o[1] - r[1], o[1] + r[1]]
        za = [o[2] - r[2], o[2] + r[2]]
        min_x = xa[0] if i == 0 else min(xa[0], min_x)
        max_x = xa[1] if i == 0 else max(xa[1], max_x)
        min_y = ya[0] if i == 0 else min(ya[0], min_y)
        max_y = ya[1] if i == 0 else max(ya[1], max_y)
        min_z = za[0] if i == 0 else min(za[0], min_z)
        max_z = za[1] if i == 0 else max(za[1], max_z)

    boxs = [0] * 12
    boxs[0] = (max_x + min_x) / 2
    boxs[1] = (max_y + min_y) / 2
    boxs[2] = (max_z + min_z) / 2
    boxs[3] = (max_x - min_x) / 2
    boxs[7] = (max_y - min_y) / 2
    boxs[11] = (max_z - min_z) / 2
    join_cfgo["root"]["boundingVolume"]["box"] = boxs

    # geometric_error = np.sqrt(boxs[3] ** 2 + boxs[7] ** 2) * 2
    # join_cfgo["geometricError"] = geometric_error
    # join_cfgo["root"]["geometricError"] = geometric_error

    try:
        # 将更新后的合并配置文件写入到合并图层路径的tileset.json文件中
        write_json_file(join_cfgo, os.path.join(join_layer_path, "tileset.json"))
    except Exception as e:
        print(e)
    print("图层合并完成。")

tiles_directory= '.../tileset'
src_layer_paths=get_src_layer_paths(tiles_directory)
join_layer_path= '.../tileset'
is_append = False
join_layer(join_layer_path,src_layer_paths,is_append)

