
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



def get_frames_with_data_henkkari(player_1, player_2):
    images_results = []
    first_throw_n = 0
    second_throw_n = 0
    player_turn_start = 1
    live_result = [[0,0], [0,0]]
    players = [player_1, player_2]
    for game_round in range(1,3):
        first_thorws_n = len(player_1[game_round]["throws"])
        second_thorws_n = len(player_2[game_round]["throws"])
        player_turn = 1 - player_turn_start
        player_turn_start = player_turn
        anti_player_turn = 1
        player_throw_n = [0,0]
        thorws = [player_1[game_round]["throws"], player_2[game_round]["throws"]]
        while(player_throw_n[0] < first_thorws_n or player_throw_n[1] < second_thorws_n):
            point = check_point(str(thorws[player_turn][player_throw_n[player_turn]]), True)
            #print(players[player_turn], point, player_throw_n[player_turn])
            player_throw_n[player_turn] += 1
            if point[0] != '-':
                images_results.append(creat_henkkari_frame(player_1, player_2, " ", live_result))
            players[player_turn][game_round]["points"] += point[2]
            players[player_turn][game_round]["kyykkas"] -= point[1]
            players[player_turn][game_round]["bats"] -= 1
            # if (players[player_turn][game_round]["bats"] == 0):
            #     players[player_turn][game_round]["bats"] = players[player_turn][game_round]["points"]

            # Add end result to the result fielt
            #print(player_throw_n[player_turn], len(thorws[player_turn]), player_turn, live_result)
            if (player_throw_n[player_turn] == len(thorws[player_turn])): # end result
                live_result[player_turn][game_round - 1] = players[player_turn][game_round]["result"]
            if point[0] != '-':
                images_results.append(creat_henkkari_frame(player_1, player_2, point[0], live_result)) 
            if (player_throw_n[player_turn] < len(thorws[player_turn])):
                if (player_throw_n[player_turn] % 4 == 0 and player_throw_n[anti_player_turn] < len(thorws[anti_player_turn])):
                    anti_player_turn = player_turn
                    player_turn = 1 - player_turn
            elif (player_throw_n[anti_player_turn] < len(thorws[anti_player_turn])):
                anti_player_turn = player_turn
                player_turn = 1 - player_turn
    return images_results


def generate_fames_vastaikkain(first_player, second_player, players, results, kyykkas, bats, scores, turn_max_bats):
    images_results = []
    first_thorws_n = sum(len(l) for l in first_player)
    second_thorws_n = sum(len(l) for l in second_player)
    first_throw_n = 0
    second_throw_n = 0
    player_turn_start = 1
    live_result = [[0,0], [0,0]]
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
            #print(players[player_turn], point, player_throw_n[player_turn], kyykkas)
            player_throw_n[player_turn] += 1
            if point[0] != '-':
                images_results.append(creat_vastakkain_frame(players, bats, kyykkas, " ", live_result))
            scores[player_turn][game_round] += point[2]
            kyykkas[player_turn][game_round] -= point[1]
            bats[player_turn][game_round] += 1
            if (player_throw_n[0] == first_thorws_n and player_throw_n[1] == second_thorws_n):
                live_result[game_round] = results[game_round]
            if point[0] != '-':
                images_results.append(creat_vastakkain_frame(players, bats, kyykkas, point[0], live_result)) 

            if (player_throw_n[player_turn] < len(thorws[player_turn])):
                if (player_throw_n[player_turn] % turn_max_bats == 0 and player_throw_n[anti_player_turn] < len(thorws[anti_player_turn])):
                    anti_player_turn = player_turn
                    player_turn = 1 - player_turn
            elif ((player_throw_n[anti_player_turn] -1) < len(thorws[anti_player_turn])):
                anti_player_turn = player_turn
                player_turn = 1 - player_turn
            #return images_results

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

def creat_henkkari_frame(player_1, player_2, throw, live_result):  
    # creating new Image object 
    name_w = 700
    name_h = 150
    img = Image.new("RGB", (name_w + 4, name_h)) 
   
    font = ImageFont.truetype("arial.ttf", size = 30)
    text_color = (0, 0, 0)

    karttu_img = Image.open('Karttu.png')
    kyykka_img = Image.open('Kyykka.png')
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
    draw.text((box_size / 2, name_h), str(player_1["name"]), fill = text_color, anchor="mt", font = font)
    draw.text(((name_w - box_size / 2) , name_h), str(player_2["name"]), fill = text_color, anchor="mt", font = font)

    font_vs = ImageFont.truetype("arial.ttf", size = 25)
    draw.text((name_w / 2, name_h + 15), 'vs.', fill = text_color, anchor="mt", font = font_vs)
    #line_h = 45
    result_head_h = name_h + 35
    font_head = ImageFont.truetype("arial.ttf", size = 20)
    head_text_color = "#696969"
    draw.text((box_size / 2 - 25, result_head_h), "1.      2.", fill = head_text_color, anchor="mt", font = font_head)
    draw.text(((name_w - box_size / 2) + 10, result_head_h), "      2.      1.", fill = head_text_color, anchor="mt", font = font_head)

    result_h = result_head_h + 20
    draw.text((box_size / 2 - 30, result_h), "|", fill = text_color, anchor="mt", font = font)
    draw.text(((name_w - box_size / 2) + 30, result_h), "|", fill = text_color, anchor="mt", font = font)

    draw.text((box_size / 2 - 55, result_h), str(player_1[1]["bats"]), fill = text_color, anchor="mt", font = font)
    draw.text((box_size / 2, result_h), str(player_1[2]["bats"]), fill = text_color, anchor="mt", font = font)

    draw.text(((name_w - box_size / 2) + 55, result_h), str(player_2[1]["bats"]), fill = text_color, anchor="mt", font = font)
    draw.text(((name_w - box_size / 2), result_h), str(player_2[2]["bats"]), fill = text_color, anchor="mt", font = font)

    result_h += 30
    draw.text((box_size / 2 - 30, result_h), "|", fill = text_color, anchor="mt", font = font)
    draw.text(((name_w - box_size / 2) + 30, result_h), "|", fill = text_color, anchor="mt", font = font)

    draw.text((box_size / 2 - 55, result_h), str(player_1[1]["kyykkas"]), fill = text_color, anchor="mt", font = font)
    draw.text((box_size / 2, result_h), str(player_1[2]["kyykkas"]), fill = text_color, anchor="mt", font = font)

    draw.text(((name_w - box_size / 2) + 55, result_h), str(player_2[1]["kyykkas"]), fill = text_color, anchor="mt", font = font)
    draw.text(((name_w - box_size / 2), result_h), str(player_2[2]["kyykkas"]), fill = text_color, anchor="mt", font = font)


    result_h += 30
    draw.text((box_size / 2 - 30, result_h), "|", fill = text_color, anchor="mt", font = font)
    draw.text(((name_w - box_size / 2) + 30, result_h), "|", fill = text_color, anchor="mt", font = font)

    draw.text((box_size / 2 - 55, result_h), str(live_result[0][0]), fill = text_color, anchor="mt", font = font)
    draw.text((box_size / 2, result_h), str(live_result[0][1]), fill = text_color, anchor="mt", font = font)

    draw.text(((name_w - box_size / 2) + 55, result_h), str(live_result[1][0]), fill = text_color, anchor="mt", font = font)
    draw.text(((name_w - box_size / 2), result_h), str(live_result[1][1]), fill = text_color, anchor="mt", font = font)

    if throw != " ":
        font_throw = ImageFont.truetype("arial.ttf", size = 80)
        draw.text(((name_w / 2) , result_h - 45), str(throw), fill = (0, 0, 0), anchor="mt", font = font_throw)
        font_throw = ImageFont.truetype("arial.ttf", size = 70)
        draw.text(((name_w / 2) , result_h - 40), str(throw), fill = (255, 255, 255), anchor="mt", font = font_throw)
    #draw.line([(2, line_h), (name_w + 1, line_h)], fill=team_color, width = 6, joint = "curve")
    #img.show()
    karttu_scale = 0.5
    karttu_img = karttu_img.resize((int(karttu_img.width * karttu_scale), int(karttu_img.height * karttu_scale)))
    img.paste(karttu_img, (25, 50), karttu_img)
    img.paste(karttu_img, (name_w - 90,50), karttu_img)    
    kyykka_scale = 0.4
    kyykka_img = kyykka_img.resize((int(kyykka_img.width * ( kyykka_scale - 0.1)), int(kyykka_img.height * kyykka_scale)))
    img.paste(kyykka_img, (40, 85), kyykka_img)
    img.paste(kyykka_img, (name_w - 80, 85), kyykka_img)
    return img


def creat_vastakkain_frame(players, bats, kyykas, throw, live_result):  
    # creating new Image object 
    name_w = 700
    name_h = 150
    img = Image.new("RGB", (name_w + 4, name_h)) 
   
    font = ImageFont.truetype("arial.ttf", size = 30)
    text_color = (0, 0, 0)

    karttu_img = Image.open('Karttu.png')
    kyykka_img = Image.open('Kyykka.png')
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
    draw.text((box_size / 2, name_h), str(players[0]), fill = text_color, anchor="mt", font = font)
    draw.text(((name_w - box_size / 2) , name_h), str(players[1]), fill = text_color, anchor="mt", font = font)

    font_vs = ImageFont.truetype("arial.ttf", size = 25)
    draw.text((name_w / 2, name_h + 15), 'vs.', fill = text_color, anchor="mt", font = font_vs)
    #line_h = 45
    result_head_h = name_h + 35
    font_head = ImageFont.truetype("arial.ttf", size = 20)
    head_text_color = "#696969"
    draw.text((box_size / 2 - 25, result_head_h), "1.      2.", fill = head_text_color, anchor="mt", font = font_head)
    draw.text(((name_w - box_size / 2) + 10, result_head_h), "      2.      1.", fill = head_text_color, anchor="mt", font = font_head)

    result_h = result_head_h + 20
    draw.text((box_size / 2 - 30, result_h), "|", fill = text_color, anchor="mt", font = font)
    draw.text(((name_w - box_size / 2) + 30, result_h), "|", fill = text_color, anchor="mt", font = font)

    draw.text((box_size / 2 - 55, result_h), str(bats[0][0]), fill = text_color, anchor="mt", font = font)
    draw.text((box_size / 2, result_h), str(bats[0][1]), fill = text_color, anchor="mt", font = font)

    draw.text(((name_w - box_size / 2) + 55, result_h), str(bats[1][0]), fill = text_color, anchor="mt", font = font)
    draw.text(((name_w - box_size / 2), result_h), str(bats[1][1]), fill = text_color, anchor="mt", font = font)

    result_h += 30
    draw.text((box_size / 2 - 30, result_h), "|", fill = text_color, anchor="mt", font = font)
    draw.text(((name_w - box_size / 2) + 30, result_h), "|", fill = text_color, anchor="mt", font = font)

    draw.text((box_size / 2 - 55, result_h), str(kyykas[0][0]), fill = text_color, anchor="mt", font = font)
    draw.text((box_size / 2, result_h), str(kyykas[0][1]), fill = text_color, anchor="mt", font = font)

    draw.text(((name_w - box_size / 2) + 55, result_h), str(kyykas[1][0]), fill = text_color, anchor="mt", font = font)
    draw.text(((name_w - box_size / 2), result_h), str(kyykas[1][1]), fill = text_color, anchor="mt", font = font)

    result_h += 30
    draw.text((box_size / 2 - 30, result_h), "|", fill = text_color, anchor="mt", font = font)
    draw.text(((name_w - box_size / 2) + 30, result_h), "|", fill = text_color, anchor="mt", font = font)

    draw.text((box_size / 2 - 55, result_h), str(live_result[0][0]), fill = text_color, anchor="mt", font = font)
    draw.text((box_size / 2, result_h), str(live_result[1][0]), fill = text_color, anchor="mt", font = font)

    draw.text(((name_w - box_size / 2) + 55, result_h), str(live_result[0][1]), fill = text_color, anchor="mt", font = font)
    draw.text(((name_w - box_size / 2), result_h), str(live_result[1][1]), fill = text_color, anchor="mt", font = font)

    if throw != " ":
        font_throw = ImageFont.truetype("arial.ttf", size = 80)
        draw.text(((name_w / 2) , result_h - 40), str(throw), fill = (0, 0, 0), anchor="mt", font = font_throw)
        font_throw = ImageFont.truetype("arial.ttf", size = 70)
        draw.text(((name_w / 2) , result_h - 40), str(throw), fill = (255, 255, 255), anchor="mt", font = font_throw)
    #draw.line([(2, line_h), (name_w + 1, line_h)], fill=team_color, width = 6, joint = "curve")
    #img.show()
    karttu_scale = 0.5
    karttu_img = karttu_img.resize((int(karttu_img.width * karttu_scale), int(karttu_img.height * karttu_scale)))
    img.paste(karttu_img, (25, 50), karttu_img)
    img.paste(karttu_img, (name_w - 90,50), karttu_img)    
    kyykka_scale = 0.4
    kyykka_img = kyykka_img.resize((int(kyykka_img.width * ( kyykka_scale - 0.1)), int(kyykka_img.height * kyykka_scale)))
    img.paste(kyykka_img, (40, 85), kyykka_img)
    img.paste(kyykka_img, (name_w - 80, 85), kyykka_img)
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
fps = 60
# scores = [[-80, -80], [-80, -80]]
# bats = [[0, 0],[0, 0]] 
# #bats = [[0, 0],[0, 0]] # Vastakkai
# kyykkas = [[40, 40], [40, 40]]
max_bats = 20
turn_max_bats = 4
# first_player = [[4,4,0,4,6,2,2,2,6,0,2,2,0,3,1,0],[4,3,4,6,5,1,1,2,7,2,1,0,0,2,1,0]]
# second_player = [[0,1,2,6,0,0,5,1,2,3,3,1,4,3,1,0],[4,1,2,1,0,2,1,3,3,4,4,2,1,3,1,1]]
# results = [[0, -12], [0, -12]] # [First round first team, second team], second round
# players = ['Tammer III', 'Seka I']

player_1 = {
    1:{
    "points":-80,
    "bats":20,
    #"bats":0, # Vastakkain
    "kyykkas":20, 
    #"kyykkas":40, #joukkue
    "throws": [4,0,0,0, 4,1,0,1, 0,1,0,1,  0,0,3,1,  0,1,0,1, ],
    "result": -4
    },    
    2:{
    "points":-80,
    "bats":20,
    #"bats":0, # Vastakkain
    "kyykkas":20,
    #"kyykkas":40, #joukkue
    "throws": [2,3,4,1,1,1,1,1,1,0,2,0,0,1,0,1,1],
    "result": "x"
    },
    "name": 'Karli vK',
}

player_2 = {
    1:{
    "points":-80,
    "bats":20,
    #"bats":0, # Vastakkain
    "kyykkas":20,
    #"kyykkas":40, #joukkue
    "throws": [2,3,4,1, 1,1,1,1, 1,0,2,0, 0,1,0,1, 1],
    "result": 3
    },    
    2:{
    "points":-80,
    "bats":20,
    #"bats":0, # Vastakkain
    "kyykkas":20,
    #"kyykkas":40, #joukkue
    "throws": [4,0,0,0,4,1,0,1,0,1,0,1,0,0,3,1,0,1,0,1, ],
    "result": "x"
    },
    "name": 'Karli vK',
}

names_duration = [7,7] # how meany second first throw lasts and second one
results_duration = [5,2] # seconds
home_first = False
print("Luodaan kuvia")
#frames = get_frames_with_data(game_id, home_first)
frames = get_frames_with_data_henkkari(player_1, player_2)
#frames = get_frames_with_data_henkkari(first_player, second_player, players, scores, bats, kyykkas)
#frames = generate_fames_vastaikkain(first_player, second_player, players, results, kyykkas, bats, scores, max_bats, turn_max_bats)
create_video(frames, fps, results_duration, 'results_henkkari_' + player_1["name"] + "-" + player_2["name"])

print("Luodaan videoita")
#create_video(frames[0], fps, names_duration, 'names_' + str(game_id))
#¤create_video(frames[1], fps, results_duration, 'results_' + str(game_id))