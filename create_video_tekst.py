
from PIL import Image, ImageDraw, ImageFont
import requests
import pandas as pd
import cv2
import numpy as np
import os
import argparse


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

def parse_data(game_id, home_first, player_1, player_2):
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
    teams = out['Player_team'].unique()
    player_1["name"] = teams[0]
    player_2["name"] = teams[1]
    if home_first:
        player_1[1]["result"] = game_data['Results'][0]['Home_round1']
        player_2[1]["result"] = game_data['Results'][0]['Away_round1']
        player_1[2]["result"] = game_data['Results'][0]['Home_round2']
        player_2[2]["result"] = game_data['Results'][0]['Away_round2']
    else:
        player_2[1]["result"] = game_data['Results'][0]['Home_round1']
        player_1[1]["result"] = game_data['Results'][0]['Away_round1']
        player_2[2]["result"] = game_data['Results'][0]['Home_round2']
        player_1[2]["result"] = game_data['Results'][0]['Away_round2']
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



def get_frames_with_data(game_id,  home_first, player_1, player_2, generate_names = False):
    df_game_data = parse_data(game_id, home_first, player_1, player_2)
    images_names = ['Names']
    images_results = ['Game']
    team = "-"
    live_result = [[0,0], [0,0]]
    Game_round = True
    last_index = len(df_game_data)
    for index, row in df_game_data.iterrows():
        #print(index)
        point = check_point(str(row['Throw_points']))
        if row['Game_round'] == 2 and Game_round:
            player_1[1]["points"] = player_1[1]["result"]
            player_2[1]["points"] = player_2[1]["result"]
            Game_round = False
        if point[0] != '-':
            images_results.append(creat_ongoing_game_frame(player_1, player_2, " ", live_result))

            #images_results.append(result_frames(teams, scores[0], scores[1], scores[2], scores[3], " "))
        if team == "-":
            team = row['Player_team']
        if team == row['Player_team']:
            if point[0] != '-' and generate_names:
                images_names.append(creat_name_frame(row['Name'], 1))
            player_1[row['Game_round']]["points"] += point[2]
            player_1[row['Game_round']]["kyykkas"] -= point[1]
            player_1[row['Game_round']]["bats"] -= 1
            # if row['Game_round'] == 1:
            #     scores[0] += point[2]
            # elif row['Game_round'] == 2:
            #     scores[2] += point[2]
        else:
            if point[0] != '-' and generate_names:
                images_names.append(creat_name_frame(row['Name'], 0))
            player_2[row['Game_round']]["points"] += point[2]
            player_2[row['Game_round']]["kyykkas"] -= point[1]
            player_2[row['Game_round']]["bats"] -= 1
            # if row['Game_round'] == 1:
            #     scores[1] += point[2]
            # elif row['Game_round'] == 2:
            #     scores[3] += point[2]
        if (index -1) == last_index:
            player_1[2]["points"] = player_1[2]["result"]
            player_2[2]["points"] = player_2[2]["result"]
        if point[0] != '-':
            images_results.append(creat_ongoing_game_frame(player_1, player_2, str(point[0]), live_result))
            #images_results.append(result_frames(teams[0], teams[1], scores[0], scores[1], scores[2], scores[3], str(point[0]))) 
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

#GENERATE FAMRES###################################################
def creat_name_frame(name, home):  

    font = ImageFont.truetype("arial.ttf", size = 30)
    text_color = (0, 0, 0)
    if home:
        img = Image.open('Nimi_tausta_home.png') 
    else:
        img = Image.open('Nimi_tausta_away.png') 
    draw = ImageDraw.Draw(img)
    draw.text((5, 5), str(name), fill = text_color, stroke_width = 1, font = font)
    #img.show()
    return img




def creat_ongoing_game_frame(player_1, player_2, throw, live_result):  
    # creating new Image object 
    name_w = 700
    name_h = 150
    #img = Image.new("RGB", (name_w + 4, name_h)) 
    img = Image.open('Tausta.png') 
   
    font_names = ImageFont.truetype("arial.ttf", size = 30)
    font_points = ImageFont.truetype("arial.ttf", size = 27)
    text_color = (0, 0, 0)
    draw = ImageDraw.Draw(img)
    box_size = name_w / 2
    bg_color = 15

    #Team names
    name_h = 6
    draw.text((box_size / 2, name_h), str(player_1["name"]), fill = text_color, anchor="mt", font = font_names)
    draw.text(((name_w - box_size / 2) , name_h), str(player_2["name"]), fill = text_color, anchor="mt", font = font_names)

    #Bats left
    result_h = name_h + 55
    draw.text((box_size / 2 - 50, result_h), str(player_1[1]["bats"]), fill = text_color, anchor="mt", font = font_points)
    draw.text((box_size / 2 - 10, result_h), str(player_1[2]["bats"]), fill = text_color, anchor="mt", font = font_points)

    draw.text(((name_w - box_size / 2) + 45, result_h), str(player_2[2]["bats"]), fill = text_color, anchor="mt", font = font_points)
    draw.text(((name_w - box_size / 2), result_h), str(player_2[1]["bats"]), fill = text_color, anchor="mt", font = font_points)

    #Kyykkas left
    result_h += 30
    draw.text((box_size / 2 - 50, result_h), str(player_1[1]["kyykkas"]), fill = text_color, anchor="mt", font = font_points)
    draw.text((box_size / 2 - 10, result_h), str(player_1[2]["kyykkas"]), fill = text_color, anchor="mt", font = font_points)

    draw.text(((name_w - box_size / 2) + 45, result_h), str(player_2[2]["kyykkas"]), fill = text_color, anchor="mt", font = font_points)
    draw.text(((name_w - box_size / 2), result_h), str(player_2[1]["kyykkas"]), fill = text_color, anchor="mt", font = font_points)

    # Team points
    result_h += 30
    draw.text((box_size / 2 - 55, result_h), str(player_1[1]["points"]), fill = text_color, anchor="mt", font = font_points)
    draw.text((box_size / 2 - 10, result_h), str(player_1[2]["points"]), fill = text_color, anchor="mt", font = font_points)

    draw.text(((name_w - box_size / 2) + 45, result_h), str(player_2[2]["points"]), fill = text_color, anchor="mt", font = font_points)
    draw.text(((name_w - box_size / 2) , result_h), str(player_2[1]["points"]), fill = text_color, anchor="mt", font = font_points)

    #Throw point
    if throw != " ":
        font_throw = ImageFont.truetype("arial.ttf", size = 80)
        draw.text(((name_w / 2) , result_h - 45), str(throw), fill = (0, 0, 0), anchor="mt", font = font_throw, stroke_width = 2, stroke_fill = (255,255,255))
    return img


def create_video(frames, fps, duration, name):
    duration_flip = 0
    videodims = frames[0].size
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    #cwd = os.getcwd()
    #print(cwd)
    video = cv2.VideoWriter(name + ".mp4",fourcc, fps,videodims)
    for frame in frames:
        for fps_frame in range(duration[duration_flip] * fps):
            video.write(cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR))
        duration_flip = 1 - duration_flip
    video.release()
    return 0

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


#Get data from this game id
game_id = 29972
fps = 1 
#scores = [[-80, -80], [-80, -80]]
#bats = [[0, 0],[0, 0]] 
#kyykkas = [[40, 40], [40, 40]]
#max_bats = 20
#turn_max_bats = 4
#first_player = [[4,4,0,4,6,2,2,2,6,0,2,2,0,3,1,0],[4,3,4,6,5,1,1,2,7,2,1,0,0,2,1,0]]
#second_player = [[0,1,2,6,0,0,5,1,2,3,3,1,4,3,1,0],[4,1,2,1,0,2,1,3,3,4,4,2,1,3,1,1]]
#results = [[0, -12], [0, -12]] # [First round first team, second team], second round
#players = ['Tammer III', 'Seka I']

player_1 = {
    1:{
    "points":-80,
    #"bats":20, #Henkkari
    "bats":16, #Joukkue
    #"bats":0, # Vastakkain
    #"kyykkas":20, # Henkkari
    "kyykkas":40, #Joukkue
    "throws": [4,0,0,0, 4,1,0,1, 0,1,0,1,  0,0,3,1,  0,1,0,1, ], #Manuaalinen syöttö
    "result": 0
    },    
    2:{
    "points":-80,
    #"bats":20, #Henkkari
    "bats":16, #Joukkue
    #"bats":0, # Vastakkain
    #"kyykkas":20, # Henkkari
    "kyykkas":40, #Joukkue
    "throws": [2,3,4,1,1,1,1,1,1,0,2,0,0,1,0,1,1], #Manuaalinen syöttö
    "result": 0
    },
    "name": '-',
}

player_2 = {
    1:{
    "points":-80,
    #"bats":20, #Henkkari
    "bats":16, #Joukkue
    #"bats":0, # Vastakkain
    #"kyykkas":20,# Henkkari
    "kyykkas":40, #Joukkue
    "throws": [2,3,4,1, 1,1,1,1, 1,0,2,0, 0,1,0,1, 1], #Manuaalinen syöttö
    "result": 0
    },    
    2:{
    "points":-80,
    #"bats":20, #Henkkari
    "bats":16, #Joukkue
    #"bats":0, # Vastakkain
    #"kyykkas":20,# Henkkari
    "kyykkas":40, #Joukkue
    "throws": [4,0,0,0,4,1,0,1,0,1,0,1,0,0,3,1,0,1,0,1, ], #Manuaalinen syöttö
    "result": 0
    },
    "name": '-',
}

names_duration = [7,7] # how meany second first throw lasts and second one
results_duration = [5,2] # seconds
def Make_video(game_id, names, home_first, fps):
    print("Luodaan kuvia pelistä", game_id)
    #pinq.kapsi.fi/kyykka sivulta peli id
    frames = get_frames_with_data(game_id, home_first, player_1, player_2, names)

    #Kesäpelejä varten
    #frames = get_frames_with_data_henkkari(player_1, player_2)
    #frames = generate_fames_vastaikkain(first_player, second_player, players, results, kyykkas, bats, scores, turn_max_bats)

    print("Luodaan videoita")
    for frame_set in frames:
        video_name = frame_set[0] + "_" + player_1["name"] + "-" + player_2["name"]
        frame_set.pop(0)
        if frame_set:
            create_video(frame_set, fps, results_duration, video_name)
            print("Video valmis nimellä", video_name)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Script that adds 3 numbers from CMD"
    )
    parser.add_argument("--game_id", type=int, help="Hale peli_id sivulta pinq.kapsi.fi/kyykka")
    parser.add_argument("--fps", type=int, help= "Kannattaa tämä pitää 1")
    parser.add_argument("--names", action=argparse.BooleanOptionalAction, help= "Generoi myös nimet taustan")
    parser.add_argument("--home_first", action=argparse.BooleanOptionalAction, help = "Jos pelijärjestys on väärä, vaihda vuoroa tällä")
    args = parser.parse_args()
    if not args.fps:
         args.fps = 1
    Make_video(args.game_id, args.names, args.home_first, args.fps)