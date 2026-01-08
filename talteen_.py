#Toka
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


#EKa
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