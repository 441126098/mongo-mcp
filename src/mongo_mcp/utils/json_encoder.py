"""自定义JSON编码器，处理MongoDB特殊类型的序列化问题。"""

import base64
import json
import datetime
from bson.objectid import ObjectId
from bson.binary import Binary
from typing import Any


class MongoJSONEncoder(json.JSONEncoder):
    """MongoDB特殊类型的JSON编码器。
    
    处理以下类型:
    - ObjectId: 转换为字符串
    - datetime: 转换为ISO格式字符串
    - Binary: 转换为base64编码字符串
    """
    
    def default(self, obj: Any) -> Any:
        """处理特殊类型的转换。"""
        if isinstance(obj, ObjectId):
            return str(obj)
        elif isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif isinstance(obj, Binary):
            return {
                "_type": "binary",
                "base64": base64.b64encode(obj).decode('ascii'),
                "subtype": obj.subtype
            }
        # 让父类处理其他类型或抛出TypeError
        return super().default(obj)


def mongodb_json_serializer(obj: Any) -> str:
    """将MongoDB对象序列化为JSON字符串。
    
    Args:
        obj: 要序列化的对象
        
    Returns:
        str: JSON字符串
    """
    return json.dumps(obj, cls=MongoJSONEncoder)


def clean_document_for_json(doc: dict) -> dict:
    """递归清理文档，确保所有字段都可JSON序列化。
    
    Args:
        doc: MongoDB文档
        
    Returns:
        dict: 清理后的文档
    """
    if not isinstance(doc, dict):
        return doc
        
    result = {}
    for key, value in doc.items():
        if isinstance(value, ObjectId):
            result[key] = str(value)
        elif isinstance(value, datetime.datetime):
            result[key] = value.isoformat()
        elif isinstance(value, Binary):
            result[key] = {
                "_type": "binary",
                "base64": base64.b64encode(value).decode('ascii'),
                "subtype": value.subtype
            }
        elif isinstance(value, dict):
            result[key] = clean_document_for_json(value)
        elif isinstance(value, list):
            result[key] = [clean_document_for_json(item) if isinstance(item, dict) else item for item in value]
        else:
            result[key] = value
    return result 