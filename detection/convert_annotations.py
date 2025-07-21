#!/usr/bin/env python3
import json
import os

# 类别映射：TiaoZhanCup类别ID -> Objects365类别ID
CATEGORY_ID_MAPPING = {
    0: 108,  # drone -> airplane
    1: 8,    # car -> car
    2: 215,  # ship -> ship
    3: 85,   # bus -> bus
    4: 0,    # pedestrian -> person
    5: 58,   # cyclist -> bicycle
}

# Objects365的80个类别
OBJECTS365_CLASSES = [
    'person', 'sneakers', 'chair', 'hat', 'lamp', 'bottle',
    'cabinet/shelf', 'cup', 'car', 'glasses', 'picture/frame', 'desk',
    'handbag', 'street lights', 'book', 'plate', 'helmet', 'leather shoes',
    'pillow', 'glove', 'potted plant', 'bracelet', 'flower', 'tv',
    'storage box', 'vase', 'bench', 'wine glass', 'boots', 'bowl',
    'dining table', 'umbrella', 'boat', 'flag', 'speaker', 'trash bin/can',
    'stool', 'backpack', 'couch', 'belt', 'carpet', 'basket',
    'towel/napkin', 'slippers', 'barrel/bucket', 'coffee table', 'suv',
    'toy', 'tie', 'bed', 'traffic light', 'pen/pencil', 'microphone',
    'sandals', 'canned', 'necklace', 'mirror', 'faucet', 'bicycle',
    'bread', 'high heels', 'ring', 'van', 'watch', 'sink', 'horse', 'fish',
    'apple', 'camera', 'candle', 'teddy bear', 'cake', 'motorcycle',
    'wild bird', 'laptop', 'knife', 'traffic sign', 'cell phone', 'paddle',
    'truck', 'cow', 'power outlet', 'clock', 'drum', 'fork', 'bus',
    'hanger', 'nightstand', 'pot/pan', 'sheep', 'guitar', 'traffic cone',
    'tea pot', 'keyboard', 'tripod', 'hockey', 'fan', 'dog', 'spoon',
    'blackboard/whiteboard', 'balloon', 'air conditioner', 'cymbal',
    'mouse', 'telephone', 'pickup truck', 'orange', 'banana', 'airplane',
    'luggage', 'skis', 'soccer', 'trolley', 'oven', 'remote', 'baseball glove',
    'paper towel', 'refrigerator', 'train', 'tomato', 'machinery vehicle',
    'tent', 'shampoo/shower gel', 'head phone', 'lantern', 'donut',
    'cleaning products', 'sailboat', 'tangerine', 'pizza', 'kite',
    'computer box', 'elephant', 'toiletries', 'gas stove', 'broccoli',
    'toilet', 'stroller', 'shovel', 'baseball bat', 'microwave',
    'skateboard', 'surfboard', 'surveillance camera', 'gun', 'life saver',
    'cat', 'lemon', 'liquid soap', 'zebra', 'duck', 'sports car',
    'giraffe', 'pumpkin', 'piano', 'stop sign', 'radiator', 'converter',
    'tissue ', 'carrot', 'washing machine', 'vent', 'cookies',
    'cutting/chopping board', 'tennis racket', 'candy',
    'skating and skiing shoes', 'scissors', 'folder', 'baseball',
    'strawberry', 'bow tie', 'pigeon', 'pepper', 'coffee machine',
    'bathtub', 'snowboard', 'suitcase', 'grapes', 'ladder', 'pear',
    'american football', 'basketball', 'potato', 'paint brush', 'printer',
    'billiards', 'fire hydrant', 'goose', 'projector', 'sausage',
    'fire extinguisher', 'extension cord', 'facial mask', 'tennis ball',
    'chopsticks', 'electronic stove and gas stove', 'pie', 'frisbee',
    'kettle', 'hamburger', 'golf club', 'cucumber', 'clutch', 'blender',
    'tong', 'slide', 'hot dog', 'toothbrush', 'facial cleanser', 'mango',
    'deer', 'egg', 'violin', 'marker', 'ship', 'chicken', 'onion',
    'ice cream', 'tape', 'wheelchair', 'plum', 'bar soap', 'scale',
    'watermelon', 'cabbage', 'router/modem', 'golf ball', 'pine apple',
    'crane', 'fire truck', 'peach', 'cello', 'notepaper', 'tricycle',
    'toaster', 'helicopter', 'green beans', 'brush', 'carriage', 'cigar',
    'earphone', 'penguin', 'hurdle', 'swing', 'radio', 'CD',
    'parking meter', 'swan', 'garlic', 'french fries', 'horn', 'avocado',
    'saxophone', 'trumpet', 'sandwich', 'cue', 'kiwi fruit', 'bear',
    'fishing rod', 'cherry', 'tablet', 'green vegetables', 'nuts', 'corn',
    'key', 'screwdriver', 'globe', 'broom', 'pliers', 'volleyball',
    'hammer', 'eggplant', 'trophy', 'dates', 'board eraser', 'rice',
    'tape measure/ruler', 'dumbbell', 'hamimelon', 'stapler', 'camel',
    'lettuce', 'goldfish', 'meat balls', 'medal', 'toothpaste', 'antelope',
    'shrimp', 'rickshaw', 'trombone', 'pomegranate', 'coconut',
    'jellyfish', 'mushroom', 'calculator', 'treadmill', 'butterfly',
    'egg tart', 'cheese', 'pig', 'pomelo', 'race car', 'rice cooker',
    'tuba', 'crosswalk sign', 'papaya', 'hair drier', 'green onion',
    'chips', 'dolphin', 'sushi', 'urinal', 'donkey', 'electric drill',
    'spring rolls', 'tortoise/turtle', 'parrot', 'flute', 'measuring cup',
    'shark', 'steak', 'poker card', 'binoculars', 'llama', 'radish',
    'noodles', 'yak', 'mop', 'crab', 'microscope', 'barbell', 'bread/bun',
    'baozi', 'lion', 'red cabbage', 'polar bear', 'lighter', 'seal',
    'mangosteen', 'comb', 'eraser', 'pitaya', 'scallop', 'pencil case',
    'saw', 'table tennis paddle', 'okra', 'starfish', 'eagle', 'monkey',
    'durian', 'game board', 'rabbit', 'french horn', 'ambulance',
    'asparagus', 'hoverboard', 'pasta', 'target', 'hotair balloon',
    'chainsaw', 'lobster', 'iron', 'flashlight'
]

def convert_annotations(input_file, output_file):
    """转换标注文件，将类别ID映射到Objects365的80个类别"""
    print(f"正在处理: {input_file}")
    
    # 读取原始文件
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 创建原始类别ID到名称的映射
    original_categories = {cat['id']: cat['name'] for cat in data['categories']}
    print(f"原始类别: {original_categories}")
    
    # 更新类别信息
    new_categories = []
    for i, class_name in enumerate(OBJECTS365_CLASSES):
        new_categories.append({
            'id': i,
            'name': class_name,
            'supercategory': 'none'
        })
    
    # 更新标注中的类别ID
    updated_annotations = []
    for ann in data['annotations']:
        original_cat_id = ann['category_id']
        
        if original_cat_id in CATEGORY_ID_MAPPING:
            # 映射到新的类别ID
            new_cat_id = CATEGORY_ID_MAPPING[original_cat_id]
            ann['category_id'] = new_cat_id
            updated_annotations.append(ann)
            print(f"  映射: {original_categories[original_cat_id]} (ID: {original_cat_id}) -> {OBJECTS365_CLASSES[new_cat_id]} (ID: {new_cat_id})")
        else:
            print(f"  警告: 未找到类别映射 {original_cat_id}")
    
    # 更新数据
    data['categories'] = new_categories
    data['annotations'] = updated_annotations
    
    # 保存修改后的文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"已保存到: {output_file}")
    print(f"更新了 {len(updated_annotations)} 个标注")
    print()

def main():
    annotations_dir = 'data/TiaoZhanCup/annotations'
    
    # 处理三个文件
    files = ['train.json', 'val.json', 'test.json']
    
    for filename in files:
        input_path = os.path.join(annotations_dir, filename)
        output_path = os.path.join(annotations_dir, f'converted_{filename}')
        
        if os.path.exists(input_path):
            convert_annotations(input_path, output_path)
        else:
            print(f"文件不存在: {input_path}")
    
    print("转换完成！")
    print("请检查转换后的文件，确认无误后可以替换原文件。")

if __name__ == '__main__':
    main() 