#!/usr/bin/env python3
import os
import json
import cv2
from PIL import Image
import numpy as np
from datetime import datetime

def get_image_size(image_path):
    """获取图片尺寸"""
    try:
        with Image.open(image_path) as img:
            return img.size[0], img.size[1]  # width, height
    except Exception as e:
        print(f"Error reading image {image_path}: {e}")
        return None, None

def parse_label_file(label_path, img_width, img_height):
    """解析标签文件，返回边界框信息"""
    annotations = []
    try:
        with open(label_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split()
                    if len(parts) == 5:
                        class_id = int(parts[0])
                        # YOLO格式：中心点坐标和宽高（归一化）
                        center_x = float(parts[1]) * img_width
                        center_y = float(parts[2]) * img_height
                        width = float(parts[3]) * img_width
                        height = float(parts[4]) * img_height
                        
                        # 转换为COCO格式：左上角坐标和宽高
                        x = center_x - width / 2
                        y = center_y - height / 2
                        
                        annotations.append({
                            'class_id': class_id,
                            'bbox': [x, y, width, height],
                            'area': width * height
                        })
    except Exception as e:
        print(f"Error reading label file {label_path}: {e}")
    
    return annotations

def generate_test_json():
    """生成test.json文件"""
    
    # 基础路径
    base_path = "/root/lucica/InternImage/detection/data/TiaoZhanCup"
    images_path = os.path.join(base_path, "images")
    labels_path = os.path.join(base_path, "labels")
    
    # 读取类别信息
    class_file = os.path.join(base_path, "annotations/class.json")
    with open(class_file, 'r') as f:
        class_dict = json.load(f)
    
    # 获取所有文件夹并排序，取后六个文件夹
    all_folders = sorted([d for d in os.listdir(images_path) if os.path.isdir(os.path.join(images_path, d))])
    image_folders = all_folders[-6:]  # 取后六个文件夹
    
    print(f"Processing {len(image_folders)} folders: {image_folders}")
    
    # COCO格式数据结构
    coco_data = {
        "info": {
            "description": "TiaoZhanCup Test Dataset",
            "url": "",
            "version": "1.0",
            "year": 2024,
            "contributor": "TiaoZhanCup",
            "date_created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        "licenses": [
            {
                "url": "",
                "id": 1,
                "name": "Unknown"
            }
        ],
        "images": [],
        "annotations": [],
        "categories": []
    }
    
    # 添加类别信息
    for class_id, class_name in class_dict.items():
        coco_data["categories"].append({
            "id": int(class_id),
            "name": class_name,
            "supercategory": class_name
        })
    
    image_id = 1
    annotation_id = 1
    
    # 处理每个文件夹
    for folder in image_folders:
        print(f"Processing folder: {folder}")
        
        folder_images_path = os.path.join(images_path, folder)
        folder_labels_path = os.path.join(labels_path, folder)
        
        if not os.path.exists(folder_labels_path):
            print(f"Warning: Labels folder {folder_labels_path} does not exist")
            continue
        
        # 获取文件夹中的所有图片
        image_files = [f for f in os.listdir(folder_images_path) if f.lower().endswith(('.bmp', '.jpg', '.jpeg', '.png'))]
        
        for image_file in image_files:
            # 图片路径
            image_path = os.path.join(folder_images_path, image_file)
            
            # 获取图片尺寸
            img_width, img_height = get_image_size(image_path)
            if img_width is None or img_height is None:
                print(f"Skipping {image_path} due to size reading error")
                continue
            
            # 添加图片信息
            coco_data["images"].append({
                "id": image_id,
                "file_name": f"{folder}/{image_file}",
                "width": img_width,
                "height": img_height,
                "license": 1,
                "flickr_url": "",
                "coco_url": "",
                "date_captured": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            
            # 对应的标签文件
            label_file = image_file.rsplit('.', 1)[0] + '.txt'
            label_path = os.path.join(folder_labels_path, label_file)
            
            if os.path.exists(label_path):
                # 解析标签文件
                annotations = parse_label_file(label_path, img_width, img_height)
                
                # 添加标注信息
                for ann in annotations:
                    coco_data["annotations"].append({
                        "id": annotation_id,
                        "image_id": image_id,
                        "category_id": ann['class_id'],
                        "bbox": ann['bbox'],  # [x, y, width, height]
                        "area": ann['area'],
                        "segmentation": [],  # 暂时为空
                        "iscrowd": 0,
                        "ignore": 0
                    })
                    annotation_id += 1
            
            image_id += 1
    
    # 保存JSON文件
    output_path = os.path.join(base_path, "annotations/test.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(coco_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nGenerated test.json with:")
    print(f"  - {len(coco_data['images'])} images")
    print(f"  - {len(coco_data['annotations'])} annotations")
    print(f"  - {len(coco_data['categories'])} categories")
    print(f"  - Saved to: {output_path}")
    
    return output_path

if __name__ == "__main__":
    generate_test_json() 