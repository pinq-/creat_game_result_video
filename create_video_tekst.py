
from PIL import Image, ImageDraw, ImageFont
import requests
import pandas as pd
import cv2
import numpy as np
import os


#HD
HD_w = 1280
HD_h = 720


color_red = "#eb2828"
color_blue = "#4ee711"
#color_blue = "#117de7"


w, h = int(HD_w / 4), int(HD_h / 7)

def get_data(game_id):
    url = 'http://pinq.kapsi.fi/DK/api/data/game/' + str(game_id)
    response = requests.get(url)
    return response.json()

def parse_data(game_id, home_first = True):
    game_data = get_data(game_id)
    df_res = pd.DataFrame(game_data['Throws'])
    teams = df_res['Player_team'].unique()
    home_throws_r1 = df_res[(df_res['Game_round'] == 1) & (df_res['Player_team'] == teams[0])].sort_values('Player_order')
    away_throws_r1 = df_res[(df_res['Game_round'] == 1) & (df_res['Player_team'] == teams[1])].sort_values('Player_order')
    order = create_order(len(home_throws_r1), 4, home_first)
    round_1 = pd.concat([home_throws_r1, away_throws_r1]).iloc[order]
    home_throws_r2 = df_res[(df_res['Game_round'] == 2) & (df_res['Player_team'] == teams[0])].sort_values('Player_order')
    away_throws_r2 = df_res[(df_res['Game_round'] == 2) & (df_res['Player_team'] == teams[1])].sort_values('Player_order')
    order = create_order(len(home_throws_r1), 4, not home_first)
    round_2 = pd.concat([home_throws_r2, away_throws_r2]).iloc[order]
    out = pd.concat([round_1, round_2])
    #print(out.head(40))
    return out

def create_order(length, phase, home_first):
    first_list = [i for i in range(length)]
    second_list = [i for i in range(length, length * 2)]
    start_i = 0
    out_list = []
    for i in range(phase, length + 1, phase):
        if home_first:
            out_list.extend(first_list[start_i:i])
            out_list.extend(second_list[start_i:i])
        else:
            out_list.extend(second_list[start_i:i])
            out_list.extend(first_list[start_i:i])
        start_i = i
    return out_list



def get_frames_with_data(game_id,  home_first):
    df_game_data = parse_data(game_id, home_first)
    images_names = []
    images_results = []
    team = "-"
    scores = [-80, -80, -80, -80]
    teams = df_game_data['Player_team'].unique()
    for index, row in df_game_data.iterrows():
        #print(row['player'], row['score'])
        point = check_point(str(row['Throw_points']))
        if point[0] != '-':
            images_results.append(result_frames(teams[0], teams[1], scores[0], scores[1], scores[2], scores[3], " "))
        if team == "-":
            team = row['Player_team']
        if team == row['Player_team']:
            if point[0] != '-':
                images_names.append(creat_name_frames(row['Name'], 1))
            if row['Game_round'] == 1:
                scores[0] += point[2]
            elif row['Game_round'] == 2:
                scores[2] += point[2]
        else:
            if point[0] != '-':
                images_names.append(creat_name_frames(row['Name'], 0))
            if row['Game_round'] == 1:
                scores[1] += point[2]
            elif row['Game_round'] == 2:
                scores[3] += point[2]
        if point[0] != '-':
            images_results.append(result_frames(teams[0], teams[1], scores[0], scores[1], scores[2], scores[3], str(point[0]))) 
    return [images_names, images_results]

def get_frames_with_data_henkkari():
    first_player = [[1,2,0,0,2,3,0,2,2,1,1,2,0,0,0,0,2,1,1],[1,1,1,2,3,0,1,1,2,1,0,1,2,2,1,1]]
    #first_player = [['H', 1, 1, 1, 1, 1], [2, 2, 2, 0, 1, 'H', 1]]
    second_player = [[1, 2, 0, 2,1, 3, 3, 1,1, 2, 1, 0, 1, 0, 1, 1,],[2, 4, 1, 1,3, 0, 1, 1, 2, 0, 0, 1,0, 1, 2, 1, ]]
    #second_player = [[0, 1, 0, 0, 0, 1, 1], [1, 2, 0, 3, 1, 1]]

    images_results = []
    player = "-"
    scores = [[-40, -40], [-40, -40]]
    bats = [[20, 20],[20, 20]]
    players = ['Karli vK', 'Olli-Pekka H']
    first_thorws_n = sum(len(l) for l in first_player)
    second_thorws_n = sum(len(l) for l in second_player)
    first_throw_n = 0
    second_throw_n = 0
    player_turn_start = 1
    for game_round in range(2):
        first_thorws_n = len(first_player[game_round])
        second_thorws_n = len(second_player[game_round])
        player_turn = 1 - player_turn_start
        player_turn_start = player_turn
        anti_player_turn = 1
        player_throw_n = [0,0]
        thorws = [first_player[game_round], second_player[game_round]]
        while(player_throw_n[0] < first_thorws_n or player_throw_n[1] < second_thorws_n):

            point = check_point(str(thorws[player_turn][player_throw_n[player_turn]]), True)
            #print(players[player_turn], point, player_throw_n[player_turn])
            player_throw_n[player_turn] += 1
            if point[0] != '-':
                images_results.append(creat_henkkari_frame(players[0], players[1], bats[0][0], bats[1][0], bats[0][1], bats[1][1], " "))
            scores[player_turn][game_round] += point[2]
            bats[player_turn][game_round] -= 1
            if (bats[player_turn][game_round] == 0):
                bats[player_turn][game_round] = scores[player_turn][game_round]
            if point[0] != '-':
                images_results.append(creat_henkkari_frame(players[0], players[1], bats[0][0], bats[1][0], bats[0][1], bats[1][1], point[0])) 
            if (player_throw_n[player_turn] < len(thorws[player_turn])):
                if (player_throw_n[player_turn] % 4 == 0 and player_throw_n[anti_player_turn] < len(thorws[anti_player_turn])):
                    anti_player_turn = player_turn
                    player_turn = 1 - player_turn
            elif (player_throw_n[anti_player_turn] < len(thorws[anti_player_turn])):
                anti_player_turn = player_turn
                player_turn = 1 - player_turn

    return images_results

def check_point(point, multi_2 = False):
    points = [point.lower(), 0, 0]
    try:
        if multi_2:
            points[2] = int(points[0]) * 2
            points[1] = int(points[0])
        else:
            points[2] = int(points[0])
            if abs(int(points[0]) % 2) == 1:
                points[1] = int((points[2] - 1) / 2)
            else:
                points[1] = int(points[2] / 2)
    except ValueError:
        if points[0] == "e":
            return False
        if points[0] == "-":
            points[2] = 1
    return points


def create_video(frames, fps, duration, name):
    duration_flip = 0
    videodims = frames[0].size
    fourcc = cv2.VideoWriter_fourcc(*'avc1')
    cwd = os.getcwd()
    video = cv2.VideoWriter(cwd + "\\" + name + ".mp4",fourcc, fps,videodims)
    for frame in frames:
        #print(frame)
        for fps_frame in range(duration[duration_flip] * fps):
            video.write(cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR))
        duration_flip = 1 - duration_flip
    #print(video)
    video.release()
    return 0
def creat_name_frames(name, home):  
    # creating new Image object 
    name_w = 300
    name_h = 50
    img = Image.new("RGB", (name_w + 4, name_h)) 
   
    font = ImageFont.truetype("arial.ttf", size = 30)
    text_color = (0, 0, 0)
    if home:
        team_color = color_red
    else:
        team_color = color_blue
    #text_position = (40, 0)
    G = Image.new('L', (256,256), color = (255)).crop((0, 100, 256, 200))     # 256x256, black, i.e. 0
    B = Image.linear_gradient('L').crop((0, 100, 256, 200))       # 256x256, black at top, white at bottom
    #R = B.rotate(180)               # 256x256, white at top, black at bottom
    grad = Image.merge("RGB",(B,B,G)).resize((name_w,name_h))
    img.paste(grad, (2,-2))
    draw = ImageDraw.Draw(img)
    draw.text((20, 0), str(name), fill = text_color, stroke_width = 1, font = font)
    line_h = 45
    draw.line([(2, line_h), (name_w + 1, line_h)], fill=team_color, width = 6, joint = "curve")
    #img.show()
    return img

def creat_henkkari_frame(home_player, away_player, home_first_round, away_first_round, home_second_round, away_second_round, throw):  
    # creating new Image object 
    name_w = 700
    name_h = 100
    img = Image.new("RGB", (name_w + 4, name_h)) 
   
    font = ImageFont.truetype("arial.ttf", size = 30)
    text_color = (0, 0, 0)
    #text_position = (40, 0)
    G = Image.new('L', (256,256), color = (255)).crop((0, 100, 256, 200))     # 256x256, black, i.e. 0
    B = Image.linear_gradient('L').crop((0, 100, 256, 200))       # 256x256, black at top, white at bottom
    #R = B.rotate(180)               # 256x256, white at top, black at bottom
    grad = Image.merge("RGB",(B,B,G)).resize((name_w,name_h))
    img.paste(grad, (2,-2))
    draw = ImageDraw.Draw(img)
    box_size = name_w / 2 - 40
    bg_color = 15
    draw.line([(0, bg_color), (box_size, bg_color)], fill=color_red, width = 30, joint = "curve")
    draw.line([(name_w - box_size, bg_color), (name_w, bg_color)], fill=color_blue, width = 30, joint = "curve")
    name_h = 6
    draw.text((box_size / 2, name_h), str(home_player), fill = text_color, anchor="mt", font = font)
    draw.text(((name_w - box_size / 2) , name_h), str(away_player), fill = text_color, anchor="mt", font = font)

    font_vs = ImageFont.truetype("arial.ttf", size = 25)
    draw.text((name_w / 2, name_h + 15), 'vs.', fill = text_color, anchor="mt", font = font_vs)
    #line_h = 45
    result_head_h = name_h + 35
    font_head = ImageFont.truetype("arial.ttf", size = 20)
    head_text_color = "#696969"
    draw.text((box_size / 2 + 20, result_head_h), "1.      2.     Tulos", fill = head_text_color, anchor="mt", font = font_head)
    draw.text(((name_w - box_size / 2) - 10, result_head_h), "Tulos      2.      1.", fill = head_text_color, anchor="mt", font = font_head)

    result_h = result_head_h + 20
    draw.text((box_size / 2, result_h), "|      |", fill = text_color, anchor="mt", font = font)
    draw.text(((name_w - box_size / 2), result_h), "|      |", fill = text_color, anchor="mt", font = font)

    draw.text((box_size / 2 - 55, result_h), str(home_first_round), fill = text_color, anchor="mt", font = font)
    draw.text((box_size / 2, result_h), str(home_second_round), fill = text_color, anchor="mt", font = font)
    draw.text((box_size / 2 + 55, result_h), str(home_first_round + home_second_round), fill = text_color, anchor="mt", font = font)

    draw.text(((name_w - box_size / 2) + 55, result_h), str(away_first_round), fill = text_color, anchor="mt", font = font)
    draw.text(((name_w - box_size / 2), result_h), str(away_second_round), fill = text_color, anchor="mt", font = font)
    draw.text(((name_w - box_size / 2) - 55, result_h), str(away_first_round + away_second_round), fill = text_color, anchor="mt", font = font)
    if throw != " ":
        font_throw = ImageFont.truetype("arial.ttf", size = 40)
        draw.text(((name_w / 2), result_h), str(throw), fill = (255, 255, 255), anchor="mt", font = font_throw)
    #draw.line([(2, line_h), (name_w + 1, line_h)], fill=team_color, width = 6, joint = "curve")
    #img.show()
    return img

def result_frames(home_team, away_team, home_first_round, away_first_round, home_second_round, away_second_round, throw):  
    # creating new Image object 
    result_w = 300
    result_h = 300
    img = Image.new("RGB", (result_w, result_h)) 
   
    font = ImageFont.truetype("arial.ttf", size = 35)
    text_color = (0, 0, 0)
    #text_position = (40, 0)
    G = Image.new('L', (256,256), color = (255)).crop((0, 100, 256, 200))     # 256x256, black, i.e. 0
    B = Image.linear_gradient('L').crop((0, 100, 256, 200))       # 256x256, black at top, white at bottom
    #R = B.rotate(180)               # 256x256, white at top, black at bottom
    grad = Image.merge("RGB",(B,B,G)).resize((result_w, result_h))
    img.paste(grad, (0,0))
    draw = ImageDraw.Draw(img)

    name_h = 8
    line_h = name_h + 12 # 20
    draw.line([(0, line_h), (result_w, line_h)], fill = color_red, width = 30, joint = "curve")
    draw.line([(0, line_h + 45), (result_w, line_h + 45)], fill = color_blue, width = 30, joint = "curve")

    font_vs = ImageFont.truetype("arial.ttf", size = 20)
    draw.text((result_w / 2, name_h), str(home_team), fill = text_color,  anchor="mt", font = font, stroke_width = 1)
    draw.text((result_w / 2, name_h + 30), "vs.", fill = text_color,  anchor="mt", font = font_vs, stroke_width = 1)
    draw.text((result_w / 2, name_h + 45), str(away_team), fill = text_color,  anchor="mt", font = font, stroke_width = 1)
    
    first_r_h = line_h + 90 # 90
    draw.text((5, first_r_h), str(home_first_round), fill = text_color,  anchor="lt", font = font, stroke_width = 1)
    draw.text((result_w - 5, first_r_h), str(away_first_round), fill = text_color,  anchor="rt", font = font, stroke_width = 1)
    first_r_diff = abs(home_first_round - away_first_round)
    if home_first_round > away_first_round:
        first_r_color = color_red
    elif home_first_round < away_first_round:
        first_r_color = color_blue
    else:
        first_r_color = text_color
    draw.text((result_w / 2, first_r_h), str(first_r_diff), fill = first_r_color,  anchor="mt", font = font, stroke_width = 1, stroke_fill = text_color)
    
    second_r_h = first_r_h + 40 # 130
    draw.text((5, second_r_h), str(home_second_round), fill = text_color,  anchor="lt", font = font, stroke_width = 1)
    draw.text((result_w - 5, second_r_h), str(away_second_round), fill = text_color,  anchor="rt", font = font, stroke_width = 1)
    second_r_diff = abs(home_second_round - away_second_round)
    if home_second_round > away_second_round:
        second_r_color = color_red
    elif home_second_round < away_second_round:
        second_r_color = color_blue
    else:
        second_r_color = text_color
    draw.text((result_w / 2, second_r_h), str(second_r_diff), fill = second_r_color,  anchor="mt", font = font, stroke_width = 1, stroke_fill = text_color)
    
    result_line_h = second_r_h + 35 #165
    draw.line([(0, result_line_h), (result_w, result_line_h)], fill = text_color, width=6, joint = "curve")
    
    result_h = result_line_h + 10 # 175
    total_home = home_first_round + home_second_round
    total_away = away_first_round + away_second_round
    draw.text((5, result_h), str(total_home), fill = text_color,  anchor="lt", font = font, stroke_width = 1)
    draw.text((result_w - 5, result_h), str(total_away), fill = text_color,  anchor="rt", font = font, stroke_width = 1)
    total_diff = abs(total_home - total_away)
    if total_home > total_away:
        total_color = color_red
    elif total_home < total_away:
        total_color = color_blue
    else:
        total_color = text_color
    draw.text((result_w / 2, result_h), str(total_diff), fill = total_color,  anchor="mt", font = font, stroke_width = 1, stroke_fill = text_color)
    if throw != " ":
        throw_h = result_h + 100
        font_throw = ImageFont.truetype("arial.ttf", size = 80)
        draw.text((60, throw_h - 20), "Heitto", fill = (255, 255, 255),  anchor="ls", font = font, stroke_width = 2, stroke_fill = text_color)
        draw.text((result_w - 60, throw_h), throw, fill = (255, 255, 255),  anchor="ms", font = font_throw, stroke_width = 2, stroke_fill = text_color)
    
    #img.show()
    return img

#Get data from this game id
game_id = 29164
fps = 30

names_duration = [7,7] # how meany second first throw lasts and second one
results_duration = [5,2] # seconds
home_first = False
print("Luodaan kuvia")
#frames = get_frames_with_data(game_id, home_first)
frames = get_frames_with_data_henkkari()
create_video(frames, fps, results_duration, 'results_henkkari_')

print("Luodaan videoita")
#create_video(frames[0], fps, names_duration, 'names_' + str(game_id))
#¤create_video(frames[1], fps, results_duration, 'results_' + str(game_id))