import json

with open ('detections.json') as f:
    data = json.load(f)

def extract_coordinates(data):
    ext_line = data['eventSpecific']['nnDetect']['10_8_3_203_rtsp_camera_3']['cfg']['cross_lines'][0]['ext_line']
    int_line = data['eventSpecific']['nnDetect']['10_8_3_203_rtsp_camera_3']['cfg']['cross_lines'][0]['int_line']
    return ext_line, int_line

def process_detections(data):
    frames = data['eventSpecific']['nnDetect']['10_8_3_203_rtsp_camera_3']['frames']
    
    all_ppl = {}
    
    for frame_data in frames.values():
        persons = frame_data['detected']['person']
        for person in persons:
            if len(person) == 6:
                track_id = list(person[5].keys())[0]
                coords = person[:4]
                
                if track_id not in all_ppl:
                    all_ppl[track_id] = []
                all_ppl[track_id].append(coords)
    
    return all_ppl

def get_line_equation(line):
    x1, y1, x2, y2 = line
    a = y2 - y1
    b = x1 - x2
    c = x2 * y1 - x1 * y2
    return a, b, c

def check_side(a, b, c, x, y):
    return a * x + b * y + c

def analyze_intersections(all_ppl, ext_line, int_line):
    unic_ext_ppl = []
    unic_int_ppl = []

    ext_a, ext_b, ext_c = get_line_equation(ext_line)
    int_a, int_b, int_c = get_line_equation(int_line)

    for track_id, points in all_ppl.items():
        if len(points) >= 2:
            start_point = points[0][:2]
            current_point = []
            start_ext_side = check_side(ext_a, ext_b, ext_c, *start_point)
            start_int_side = check_side(int_a, int_b, int_c, *start_point)
            
            crossed_ext = False
            crossed_int = False

            for point in points[1:]:
                x, y = point[:2]
                current_ext_side = check_side(ext_a, ext_b, ext_c, x, y)
                current_int_side = check_side(int_a, int_b, int_c, x, y)
                current_point.append(x)
                current_point.append(y)
                if start_ext_side * current_ext_side < 0:
                    if start_int_side * current_int_side > 0:
                        if start_point > current_point:
                            crossed_int = True
                            print(f"Track ID: {track_id}")
                            print(f"Start Point: {start_point}, Current Point: ({x}, {y})")
                            print(f"Start Ext Side: {start_ext_side}, Current Ext Side: {current_ext_side}")
                            print(f"Start Int Side: {start_int_side}, Current Int Side: {current_int_side}")
                            print(f"Crossed Ext: {crossed_ext}, Crossed Int: {crossed_int}")
                            print("------")
                
                if crossed_int:
                    break
                
            for point in points[1:]:
                x, y = point[:2]
                current_ext_side = check_side(ext_a, ext_b, ext_c, x, y)
                current_int_side = check_side(int_a, int_b, int_c, x, y)
                current_point.append(x)
                current_point.append(y)
                if start_int_side * current_int_side < 0:
                    if start_ext_side * current_ext_side > 0:
                        if start_point < current_point:
                            crossed_ext = True
                            print(f"Track ID: {track_id}")
                            print(f"Start Point: {start_point}, Current Point: ({x}, {y})")
                            print(f"Start Ext Side: {start_ext_side}, Current Ext Side: {current_ext_side}")
                            print(f"Start Int Side: {start_int_side}, Current Int Side: {current_int_side}")
                            print(f"Crossed Ext: {crossed_ext}, Crossed Int: {crossed_int}")
                            print("------")
                
                if crossed_ext:
                    break
            
            if crossed_ext:
                unic_ext_ppl.append(track_id)
            if crossed_int:
                unic_int_ppl.append(track_id)
    
    # print("exit", list(set(unic_ext_ppl)))
    # print("____")
    # print("inter", list(set(unic_int_ppl)))
    
    return len(unic_ext_ppl), len(unic_int_ppl)



def main():
    ext_line, int_line = extract_coordinates(data)
    all_ppl = process_detections(data)
    unic_ext_count, unic_int_count = analyze_intersections(all_ppl, ext_line, int_line)
    
    print("Number of people exiting:", unic_ext_count)
    print("Number of people entering:", unic_int_count)

if __name__ == "__main__":
    main()
