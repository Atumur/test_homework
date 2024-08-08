import json

#читаем файл
with open ('detections.json') as f:
    data = json.load(f)

#выгружаем координаты с файла в отдельные переменные
def extract_coordinates(data):
    ext_line = data['eventSpecific']['nnDetect']['10_8_3_203_rtsp_camera_3']['cfg']['cross_lines'][0]['ext_line']
    int_line = data['eventSpecific']['nnDetect']['10_8_3_203_rtsp_camera_3']['cfg']['cross_lines'][0]['int_line']
    # print(ext_line, int_line)
    return ext_line, int_line

#функция получения остальных данных
def process_detections(data):
    frames = data['eventSpecific']['nnDetect']['10_8_3_203_rtsp_camera_3']['frames']
    
    all_ppl = {} #создаём пустой словарь для всех track_id
    
    for frame_data in frames.values(): #цикл прохода по всем данным за каждую вторую секунду
        persons = frame_data['detected']['person']
        for person in persons:#проходим по всем person для сбора данных
            if len(person) == 6:#проверяем, если данных меньше 6, то параметр достоверности <0.4, track_id не присваивается
                track_id = list(person[5].keys())[0]#считываем track_id
                coords = person[:4]#считываем координаты рамки детекции
                
                if track_id not in all_ppl:#проверка на уникальность
                    all_ppl[track_id] = []
                all_ppl[track_id].append(coords)
    # print(all_ppl)
    return all_ppl

#строим уравнение прямой через две точки
def get_line_equation(line):
    x1, y1, x2, y2 = line
    print(x1, y1, x2, y2)
    a = (y1 - y2)/(x1 - x2)
    b = y1 - ((x1 * (y1 - y2))/(x1 - x2))
    print(a, b)
    return a, b 

#проверяем положение точки относитлеьно прямой
def check_side(a, b, x, y):
    return a * x + b

def analyze_intersections(all_ppl, ext_line, int_line):
    #создаём два пустых списка для хранения уникальных track_id
    unic_ext_ppl = []
    unic_int_ppl = []

    #получаем a, b коэффициенты прямых
    ext_a, ext_b = get_line_equation(ext_line)
    int_a, int_b = get_line_equation(int_line)
    
    for track_id, points in all_ppl.items():
        current_ext_side = []
        current_int_side = []
        print("____", track_id, "_____")
        for point in points[0:]:
            x, y = point[:2] 
            y_ext = check_side(ext_a, ext_b, x, y)
            y_int = check_side(int_a, int_b, x, y)
            current_int_side.append(round((check_side(int_a, int_b, x, y)), 2))
            current_ext_side.append(round((check_side(ext_a, ext_b, x, y)), 2))
                    
        if len(current_int_side) >= 5:
            first_product = current_int_side[0]*current_int_side[1]
            for i in range(1, len(current_int_side) - 1):
                if current_int_side[0] > 0:
                    current_product = round((current_int_side[i] * current_int_side[i + 1]), 2)
                    if (first_product > 0) & (first_product*current_product < 0):
                        if max(max(p[:2]) for p in points) <= 427:
                            continue  # Пропускаем треки, у которых все координаты меньше или равны 427
                        unic_int_ppl.append(track_id)
                    first_product = current_product
                    
            first_product = current_ext_side[0]*current_ext_side[1]        
            for i in range(1, len(current_ext_side) - 1):
                if current_ext_side[0] < 0:
                    current_product = round((current_ext_side[i] * current_ext_side[i + 1]), 2)
                    if (first_product > 0) & (first_product*current_product < 0):
                        if max(max(p[:2]) for p in points) <= 361:
                            continue  # Пропускаем треки, у которых все координаты меньше или равны 361
                        unic_ext_ppl.append(track_id)
                    first_product = current_product
                    
        print(current_int_side)  
        print(current_ext_side)      
                            
    print("exit", list(set(unic_ext_ppl)))
    print("____")
    print("inter", list(set(unic_int_ppl)))
            
    return len(unic_ext_ppl), len(unic_int_ppl)        

def main():
    ext_line, int_line = extract_coordinates(data)
    all_ppl = process_detections(data)
    unic_ext_count, unic_int_count = analyze_intersections(all_ppl, ext_line, int_line)
    
    print("Number of people exiting:", unic_ext_count)
    print("Number of people entering:", unic_int_count)

if __name__ == "__main__":
    main()


