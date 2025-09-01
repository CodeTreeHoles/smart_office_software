import struct


def bytes_to_vector(bytes_data):
    """将二进制向量数据转换为浮点数列表"""
    return list(struct.unpack('f' * (len(bytes_data) // 4), bytes_data))
