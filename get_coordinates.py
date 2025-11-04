"""
Скрипт для определения координат на изображении плана этажа.
При клике на изображение выводит координаты точки в консоль.
"""
import tkinter as tk
from PIL import Image, ImageTk
import sys

def get_coordinates(image_path):
    """Открывает изображение и позволяет кликать для получения координат"""
    
    # Создаем окно
    root = tk.Tk()
    root.title("Определение координат - кликните на изображении")
    
    # Загружаем изображение
    try:
        img = Image.open(image_path)
    except Exception as e:
        print(f"Ошибка загрузки изображения: {e}")
        print(f"Проверьте путь: {image_path}")
        return
    
    # Получаем размеры изображения
    width, height = img.size
    print(f"Размер изображения: {width}x{height} пикселей")
    
    # Масштабируем если изображение слишком большое
    max_width = 1200
    max_height = 900
    if width > max_width or height > max_height:
        scale = min(max_width / width, max_height / height)
        new_width = int(width * scale)
        new_height = int(height * scale)
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        print(f"Изображение масштабировано до {new_width}x{new_height} для отображения")
        print(f"Коэффициент масштабирования: {scale}")
        print("ВАЖНО: Координаты будут в оригинальном размере!")
    
    # Конвертируем для Tkinter
    photo = ImageTk.PhotoImage(img)
    
    # Создаем canvas
    canvas = tk.Canvas(root, width=img.width, height=img.height)
    canvas.pack()
    canvas.create_image(0, 0, anchor=tk.NW, image=photo)
    
    # Коэффициент масштабирования для пересчета координат
    scale_x = width / img.width
    scale_y = height / img.height
    
    def on_click(event):
        """Обработчик клика мыши"""
        # Координаты в окне
        display_x = event.x
        display_y = event.y
        
        # Координаты в оригинальном изображении
        original_x = int(display_x * scale_x)
        original_y = int(display_y * scale_y)
        
        print(f"Координаты: ({original_x}, {original_y})")
        print(f"  (на экране: {display_x}, {display_y})")
        print("-" * 40)
    
    canvas.bind("<Button-1>", on_click)
    
    # Инструкция
    instruction = tk.Label(
        root, 
        text="Кликните на изображении для получения координат точки.\n"
             "Координаты будут выведены в консоль.",
        font=("Arial", 10)
    )
    instruction.pack()
    
    print("=" * 40)
    print("Инструкция:")
    print("1. Кликните на центре каждого кабинета")
    print("2. Кликните на дверях кабинетов (точки входа в коридор)")
    print("3. Кликните на точках коридора (узлы навигации)")
    print("4. Записывайте координаты для каждого объекта")
    print("=" * 40)
    
    root.mainloop()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python get_coordinates.py <путь_к_изображению>")
        print("Пример: python get_coordinates.py floorplans/floor_1.png")
        print("Или для URL: сначала скачайте изображение")
        sys.exit(1)
    
    image_path = sys.argv[1]
    get_coordinates(image_path)

