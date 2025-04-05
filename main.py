import pytesseract
import cv2
import numpy as np
import keyboard
from PIL import ImageGrab

# Укажи путь к tesseract.exe, если нужно (например, "C:\\Program Files\\Tesseract-OCR\\tesseract.exe")
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

# Задать координаты области (x1, y1, x2, y2)
region = (100, 540, 340, 1000) #фиолетовый

# Задаем целевой цвет, который нужно искать (например, красный цвет в формате RGB)
target_color = (170, 170, 255)  # красный цвет

def grab_screen(region=None):
    img = ImageGrab.grab(bbox=region)
    img.save("dota.png")  # сохраняем скрин для отладки
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

def get_text_lines_with_color(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Повышаем контраст для лучшего OCR
    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    # Читаем данные по словам
    data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)

    lines = {}
    for i in range(len(data['text'])):
        text = data['text'][i].strip()
        if text == "":
            continue

        block = data['block_num'][i]
        par = data['par_num'][i]
        line = data['line_num'][i]
        key = (block, par, line)

        if key not in lines:
            lines[key] = {
                'words': [],
                'top': data['top'][i],
                'bottom': data['top'][i] + data['height'][i],
                'left': data['left'][i],
                'right': data['left'][i] + data['width'][i]
            }

        lines[key]['words'].append(text)
        # Обновим нижнюю границу, если надо
        lines[key]['bottom'] = max(lines[key]['bottom'], data['top'][i] + data['height'][i])

    results = []
    for key, value in lines.items():
        full_line = ' '.join(value['words'])
        top = value['top']
        bottom = value['bottom']
        left = value['left']
        right = value['right']
        
        line_img = image[top:bottom, left:right]  # Выделяем только строку текста

        # Проверяем, есть ли пиксели с целевым цветом
        match_found = False
        for row in line_img:
            for pixel in row:
                # Сравниваем каждый пиксель с целевым цветом
                if np.allclose(pixel[::-1], target_color, atol=30):  # BGR → RGB, проверка на цвет
                    match_found = True
                    break
            if match_found:
                break

        # Если найден цвет, то помечаем строку как "AAA"
        if match_found:
            results.append((full_line, "AAA", True))
        else:
            results.append((full_line, "Не найден", False))

    return results

print("Нажми 'K' для скриншота...")

while True:
    if keyboard.is_pressed('k'):
        print("Делаю скриншот...")
        screenshot = grab_screen(region)
        results = get_text_lines_with_color(screenshot)

        print("\n📋 Распознанные строки:\n")
        for text, color, is_target in results:
            match_status = "✔️ Совпадает" if is_target else "❌ Не совпадает"
            print(f"📝 '{text}' | Цвет: {color} | {match_status}")
        break