"""Модуль для поиска пути между кабинетами и отрисовки маршрута"""
from collections import deque
import os
from PIL import Image, ImageDraw
import io
from typing import Dict, List, Optional
from urllib.request import urlopen

# Координаты центров кабинетов для каждого этажа
COORDS_FLOOR_1 = {
    "101": (97, 725),
    "102": (96, 554),
    "103": (96, 449),
    "104": (96, 354),
    "105": (97, 202),
    "106": (96, 66),
    "107": (233, 256),
    "108": (234, 361),
    "109": (473, 638),
    "110": (626, 638),
    "111": (722, 638),
    "Охрана": (198, 792),
    "Гардероб": (385, 792),
    "Туалет": (234, 154),
    "Канцелярия (в колледже)": (481, 792),
    "Каб. Воспитательной работы": (588, 792),
    "Каб. Директора": (724, 792),
}

# Граф связи между кабинетами для 1 этажа
GRAPH_FLOOR_1 = {
    "101": ["102", "Охрана"],
    "102": ["101", "103"],
    "103": ["102", "104"],
    "104": ["103", "105"],
    "105": ["104", "106", "107"],
    "106": ["105", "Туалет"],
    "107": ["105", "108"],
    "108": ["107", "Туалет"],
    "109": ["110", "Туалет"],
    "110": ["109", "111"],
    "111": ["110"],
    "Охрана": ["101", "Гардероб"],
    "Гардероб": ["Охрана", "Канцелярия (в колледже)"],
    "Туалет": ["106", "108", "109"],
    "Канцелярия (в колледже)": ["Гардероб", "Каб. Воспитательной работы"],
    "Каб. Воспитательной работы": ["Канцелярия (в колледже)", "Каб. Директора"],
    "Каб. Директора": ["Каб. Воспитательной работы"],
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
        path: список кабинетов в порядке пути
        coords: словарь координат кабинетов
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
    
    for i in range(len(path) - 1):
        start_room = path[i]
        end_room = path[i + 1]
        
        if start_room in coords and end_room in coords:
            start_coord = coords[start_room]
            end_coord = coords[end_room]
            
            # Рисуем красную линию
            draw.line([start_coord, end_coord], fill="red", width=5)
            
            # Рисуем стрелку на последнем сегменте
            if i == len(path) - 2:
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

