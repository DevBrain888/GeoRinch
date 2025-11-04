"""Модуль для поиска пути между кабинетами и отрисовки маршрута"""
from collections import deque
import os
from PIL import Image, ImageDraw
import io
from typing import Dict, List, Optional
from urllib.request import urlopen

"""Почти все готово, но нужно ввести более точные координаты для 1 этажа. 
Как пример можно использовать скрипт на python get_coordinates.py floorplans/floor_1.png, на всех остальных этажах стоят зашлущки кроме первого этажа.
"""
# Координаты центров кабинетов и точек коридора для 1 этажа
COORDS_FLOOR_1 = {
    # Кабинеты (центры)
    "101": (93, 693),
    "102": (96, 537),
    "103": (97, 437),
    "104": (97, 335),
    "105": (96, 131),
    "106": (96, 55),
    "107": (234, 258),
    "108": (234, 358),
    "109": (475, 642),
    "110": (624, 641),
    "111": (717, 642),
    "Охрана": (171, 797),
    "Гардероб": (383, 805),
    "Туалет": (229, 156),
    "Канцелярия (в колледже)": (476, 789),
    "Каб. Воспитательной работы": (585, 784),
    "Каб. Директора": (722, 775),
    
    # Точки входа из кабинетов в коридор (двери)
    "door_101": (140, 696),  # Дверь кабинета 101 в левый коридор
    "door_102": (142, 536),  # Дверь кабинета 102
    "door_103": (139, 437),  # Дверь кабинета 103
    "door_104": (139, 335),  # Дверь кабинета 104
    "door_105": (139, 131),  # Дверь кабинета 105
    "door_106": (139, 55),   # Дверь кабинета 106
    "door_107": (193, 259),  # Дверь кабинета 107
    "door_108": (194, 359),  # Дверь кабинета 108
    "door_109": (554, 640),  # Дверь кабинета 109
    "door_110": (556, 638),  # Дверь кабинета 110
    "door_111": (721, 670),  # Дверь кабинета 111
    "door_Охрана": (170, 736),  # Дверь Охраны в нижний коридор
    "door_Гардероб": (376, 720),  # Дверь Гардероба
    "door_Канцелярия": (475, 733),  # Дверь Канцелярии
    "door_Воспитательной": (584, 733),  # Дверь Каб. Воспитательной работы
    "door_Директора": (653, 734),  # Дверь Каб. Директора
    "door_Туалет": (190, 156),  # Дверь Туалета
    
    # Точки коридора (узлы навигации)
    "corridor_left_top": (170, 696),  # Верхняя точка левого коридора
    "corridor_left_1": (164, 613),    # Точка левого коридора между 101-102
    "corridor_left_2": (167, 488),    # Точка левого коридора между 102-103
    "corridor_left_3": (164, 404),    # Точка левого коридора между 103-104
    "corridor_left_4": (164, 300),    # Точка левого коридора между 104-105
    "corridor_left_5": (164, 99),     # Точка левого коридора между 105-106
    "corridor_left_bottom": (165, 55), # Нижняя точка левого коридора
    
    "corridor_bottom_left": (171, 705),  # Левая точка нижнего коридора
    "corridor_bottom_1": (379, 711),     # Точка нижнего коридора между Охрана-Гардероб
    "corridor_bottom_2": (476, 710),     # Точка нижнего коридора между Гардероб-Канцелярия
    "corridor_bottom_3": (539, 709),     # Точка нижнего коридора между Канцелярия-Воспитательной
    "corridor_bottom_4": (656, 710),     # Точка нижнего коридора между Воспитательной-Директора
    "corridor_bottom_right": (654, 765), # Правая точка нижнего коридора
    
    "corridor_center": (166, 153),  # Центральная точка коридора (около туалета)
    "corridor_horizontal": (170, 695),  # Горизонтальный коридор (к кабинетам 109-111)
}

# Граф связи с учетом коридоров для 1 этажа
GRAPH_FLOOR_1 = {
    # Кабинеты связаны с их дверями
    "101": ["door_101"],
    "102": ["door_102"],
    "103": ["door_103"],
    "104": ["door_104"],
    "105": ["door_105"],
    "106": ["door_106"],
    "107": ["door_107"],
    "108": ["door_108"],
    "109": ["door_109"],
    "110": ["door_110"],
    "111": ["door_111"],
    "Охрана": ["door_Охрана"],
    "Гардероб": ["door_Гардероб"],
    "Туалет": ["door_Туалет"],
    "Канцелярия (в колледже)": ["door_Канцелярия"],
    "Каб. Воспитательной работы": ["door_Воспитательной"],
    "Каб. Директора": ["door_Директора"],
    
    # Двери связаны с точками коридора
    "door_101": ["101", "corridor_left_top"],
    "door_102": ["102", "corridor_left_1"],
    "door_103": ["103", "corridor_left_2"],
    "door_104": ["104", "corridor_left_3"],
    "door_105": ["105", "corridor_left_4"],
    "door_106": ["106", "corridor_left_5"],
    "door_107": ["107", "corridor_center"],
    "door_108": ["108", "corridor_center"],
    "door_109": ["109", "corridor_horizontal"],
    "door_110": ["110", "corridor_horizontal"],
    "door_111": ["111", "corridor_horizontal"],
    "door_Охрана": ["Охрана", "corridor_bottom_left"],
    "door_Гардероб": ["Гардероб", "corridor_bottom_1"],
    "door_Канцелярия": ["Канцелярия (в колледже)", "corridor_bottom_2"],
    "door_Воспитательной": ["Каб. Воспитательной работы", "corridor_bottom_3"],
    "door_Директора": ["Каб. Директора", "corridor_bottom_4"],
    "door_Туалет": ["Туалет", "corridor_center"],
    
    # Вертикальный левый коридор (связи между точками)
    "corridor_left_top": ["door_101", "corridor_left_1"],
    "corridor_left_1": ["door_102", "corridor_left_top", "corridor_left_2"],
    "corridor_left_2": ["door_103", "corridor_left_1", "corridor_left_3"],
    "corridor_left_3": ["door_104", "corridor_left_2", "corridor_left_4"],
    "corridor_left_4": ["door_105", "corridor_left_3", "corridor_left_5"],
    "corridor_left_5": ["door_106", "corridor_left_4", "corridor_left_bottom"],
    "corridor_left_bottom": ["corridor_left_5", "corridor_center"],
    
    # Горизонтальный нижний коридор (соединен с левым коридором через лестницу/переход)
    "corridor_bottom_left": ["door_Охрана", "corridor_bottom_1", "corridor_left_top"],  # Соединение с верхним коридором (около 101)
    "corridor_bottom_1": ["door_Гардероб", "corridor_bottom_left", "corridor_bottom_2"],
    "corridor_bottom_2": ["door_Канцелярия", "corridor_bottom_1", "corridor_bottom_3"],
    "corridor_bottom_3": ["door_Воспитательной", "corridor_bottom_2", "corridor_bottom_4"],
    "corridor_bottom_4": ["door_Директора", "corridor_bottom_3", "corridor_bottom_right"],
    "corridor_bottom_right": ["corridor_bottom_4"],
    
    # Центральный коридор (соединяет левый коридор с правой частью)
    "corridor_center": ["corridor_left_bottom", "door_107", "door_108", "door_Туалет", "corridor_horizontal"],
    "corridor_horizontal": ["corridor_center", "door_109", "door_110", "door_111"],
    
    # Соединение нижнего коридора с левым коридором (для доступа от нижних кабинетов к верхним)
    # corridor_bottom_left уже соединен с corridor_left_top выше
}

# Координаты центров кабинетов для 2 этажа
# TODO: Уточнить координаты на основе реального плана этажа
COORDS_FLOOR_2 = {
    "201": (100, 700),
    "202": (100, 600),
    "203": (100, 500),
    "204": (100, 400),
    "205": (100, 300),
    "206": (100, 200),
    "207": (200, 200),
    "208": (300, 200),
    "209": (400, 200),
    "210": (500, 200),
    "211": (600, 200),
    "212": (600, 300),
    "213": (600, 400),
    "214": (600, 500),
    "215": (600, 600),
    "216": (600, 700),
    "217": (500, 700),
    "218": (400, 700),
    "Мужской Туалет": (250, 100),
    "Женский Туалет": (350, 100),
}

# Граф связи между кабинетами для 2 этажа
# TODO: Уточнить граф на основе реального плана этажа
GRAPH_FLOOR_2 = {
    "201": ["202"],
    "202": ["201", "203"],
    "203": ["202", "204"],
    "204": ["203", "205"],
    "205": ["204", "206"],
    "206": ["205", "207"],
    "207": ["206", "208"],
    "208": ["207", "209"],
    "209": ["208", "210"],
    "210": ["209", "211"],
    "211": ["210", "212"],
    "212": ["211", "213"],
    "213": ["212", "214"],
    "214": ["213", "215"],
    "215": ["214", "216"],
    "216": ["215", "217"],
    "217": ["216", "218"],
    "218": ["217"],
    "Мужской Туалет": ["206", "207"],
    "Женский Туалет": ["208", "209"],
}

# Координаты центров кабинетов для 3 этажа
# TODO: Уточнить координаты на основе реального плана этажа
COORDS_FLOOR_3 = {
    "301": (100, 700),
    "302": (100, 600),
    "303": (100, 500),
    "304": (100, 400),
    "305": (100, 300),
    "306": (100, 200),
    "307": (200, 200),
    "308": (300, 200),
    "309": (400, 200),
    "310": (500, 200),
    "311": (600, 200),
    "Актовый Зал": (350, 400),
    "Мужской Туалет": (250, 100),
    "Женский Туалет": (350, 100),
}

# Граф связи между кабинетами для 3 этажа
# TODO: Уточнить граф на основе реального плана этажа
GRAPH_FLOOR_3 = {
    "301": ["302"],
    "302": ["301", "303"],
    "303": ["302", "304"],
    "304": ["303", "305"],
    "305": ["304", "306"],
    "306": ["305", "307"],
    "307": ["306", "308"],
    "308": ["307", "309"],
    "309": ["308", "310"],
    "310": ["309", "311"],
    "311": ["310"],
    "Актовый Зал": ["304", "305", "308", "309"],
    "Мужской Туалет": ["306", "307"],
    "Женский Туалет": ["308", "309"],
}

# Координаты центров кабинетов для 4 этажа
# TODO: Уточнить координаты на основе реального плана этажа
COORDS_FLOOR_4 = {
    "403": (150, 500),
    "404": (250, 500),
    "405": (350, 500),
    "406": (450, 500),
    "407": (550, 500),
    "Каб. Психолога": (300, 300),
    "Мужской Туалет": (200, 100),
    "Женский Туалет": (400, 100),
}

# Граф связи между кабинетами для 4 этажа
# TODO: Уточнить граф на основе реального плана этажа
GRAPH_FLOOR_4 = {
    "403": ["404"],
    "404": ["403", "405"],
    "405": ["404", "406"],
    "406": ["405", "407"],
    "407": ["406"],
    "Каб. Психолога": ["405", "406"],
    "Мужской Туалет": ["403", "404"],
    "Женский Туалет": ["406", "407"],
}

# Словарь для доступа к координатам по номеру этажа
COORDS_BY_FLOOR = {
    1: COORDS_FLOOR_1,
    2: COORDS_FLOOR_2,
    3: COORDS_FLOOR_3,
    4: COORDS_FLOOR_4,
}

# Словарь для доступа к графам по номеру этажа
GRAPH_BY_FLOOR = {
    1: GRAPH_FLOOR_1,
    2: GRAPH_FLOOR_2,
    3: GRAPH_FLOOR_3,
    4: GRAPH_FLOOR_4,
}

# Пути к файлам планов этажей (для первого этажа используется URL)
FLOOR_PLAN_PATHS = {
    1: None,  # Используется URL из constants
    2: "floorplans/floor_2.png",
    3: "floorplans/floor_3.png",
    4: "floorplans/floor_4.png",
}

# URL изображения первого этажа
FIRST_FLOOR_IMAGE_URL = "https://i.ibb.co/tMvhp5nz/1Floor.jpg"


def bfs_shortest_path(graph: Dict[str, List[str]], start: str, end: str) -> Optional[List[str]]:
    """Поиск кратчайшего пути с помощью BFS"""
    if start == end:
        return [start]
    
    if start not in graph or end not in graph:
        return None
    
    queue = deque([(start, [start])])
    visited = {start}
    
    while queue:
        current, path = queue.popleft()
        
        if current == end:
            return path
        
        for neighbor in graph.get(current, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    
    return None


def draw_path(image_path_or_url: str, path: List[str], coords: Dict[str, tuple]) -> Image.Image:
    """Рисует путь на изображении плана этажа
    
    Args:
        image_path_or_url: путь к локальному файлу или URL изображения
        path: список узлов пути (кабинеты, двери, коридоры)
        coords: словарь координат всех узлов
    """
    # Проверяем, это URL или локальный файл
    if image_path_or_url.startswith('http://') or image_path_or_url.startswith('https://'):
        # Загружаем изображение по URL
        try:
            with urlopen(image_path_or_url) as response:
                img = Image.open(io.BytesIO(response.read()))
        except Exception as e:
            raise FileNotFoundError(f"Не удалось загрузить изображение по URL: {image_path_or_url}") from e
    else:
        # Локальный файл
        if not os.path.exists(image_path_or_url):
            raise FileNotFoundError(f"Файл плана этажа не найден: {image_path_or_url}")
        img = Image.open(image_path_or_url)
    draw = ImageDraw.Draw(img)
    
    if len(path) < 2:
        return img
    
    # Рисуем весь путь, включая коридорные точки, чтобы путь следовал по коридорам
    for i in range(len(path) - 1):
        start_node = path[i]
        end_node = path[i + 1]
        
        if start_node in coords and end_node in coords:
            start_coord = coords[start_node]
            end_coord = coords[end_node]
            
            # Рисуем красную линию
            draw.line([start_coord, end_coord], fill="red", width=5)
            
            # Рисуем стрелку на последнем сегменте (только если конечный узел - кабинет)
            if i == len(path) - 2 and not end_node.startswith("corridor_") and not end_node.startswith("door_"):
                arrow_size = 15
                dx = end_coord[0] - start_coord[0]
                dy = end_coord[1] - start_coord[1]
                length = (dx**2 + dy**2)**0.5
                
                if length > 0:
                    dx_norm = dx / length
                    dy_norm = dy / length
                    
                    arrow_x1 = end_coord[0] - arrow_size * dx_norm + arrow_size * 0.5 * dy_norm
                    arrow_y1 = end_coord[1] - arrow_size * dy_norm - arrow_size * 0.5 * dx_norm
                    arrow_x2 = end_coord[0] - arrow_size * dx_norm - arrow_size * 0.5 * dy_norm
                    arrow_y2 = end_coord[1] - arrow_size * dy_norm + arrow_size * 0.5 * dx_norm
                    
                    draw.polygon([end_coord, (arrow_x1, arrow_y1), (arrow_x2, arrow_y2)], fill="red")
    
    return img


def get_path_image(start_room: str, end_room: str, floor_number: int) -> Optional[io.BytesIO]:
    """
    Главная функция для получения изображения с путем между кабинетами
    
    Args:
        start_room: начальный кабинет (например, "102")
        end_room: конечный кабинет (например, "405")
        floor_number: номер этажа (например, 1 или 4)
    
    Returns:
        io.BytesIO: байтовый поток с изображением PNG или None, если путь не найден
    """
    # Проверяем наличие данных для этажа
    if floor_number not in COORDS_BY_FLOOR or floor_number not in GRAPH_BY_FLOOR:
        return None
    
    coords = COORDS_BY_FLOOR[floor_number]
    graph = GRAPH_BY_FLOOR[floor_number]
    
    # Проверяем, что кабинеты существуют
    if start_room not in coords or end_room not in coords:
        return None
    
    # Находим путь через BFS
    path = bfs_shortest_path(graph, start_room, end_room)
    if not path:
        return None
    
    # Получаем путь к файлу или URL плана этажа
    if floor_number == 1:
        # Для первого этажа используем URL
        image_path_or_url = FIRST_FLOOR_IMAGE_URL
    elif floor_number in FLOOR_PLAN_PATHS:
        image_path_or_url = FLOOR_PLAN_PATHS[floor_number]
    else:
        return None
    
    # Рисуем путь на изображении
    try:
        img = draw_path(image_path_or_url, path, coords)
    except FileNotFoundError:
        return None
    except Exception:
        return None
    
    # Сохраняем в BytesIO
    img_io = io.BytesIO()
    img.save(img_io, format='PNG')
    img_io.seek(0)
    
    return img_io

