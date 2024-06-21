import json

# save files
def load_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"Error: The file {file_path} does not exist.")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from file {file_path}: {e}")
    except Exception as e:
        print(f"An error occurred while reading the file {file_path}: {e}")

def save_json(data, file_path):
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Data successfully saved to {file_path}")
    except Exception as e:
        print(f"An error occurred while writing to the file {file_path}: {e}")

# detect
def battle_detect(player: dict, target:dict)->dict:
    result = {
        "受到攻擊方":[]
    }
    
    detect_all(player)
    detect_all(target)
    if((player["total"]==target["total"] and not(player["all_succ"] and target["all_succ"])) or (player["all_fail"] and target["all_fail"])):
        return result
    
    player_get_attack = generate_get_attacker(get_attacker="玩家", add_value=0)
    target_get_attack = generate_get_attacker(get_attacker="敵人", add_value=0)
    detect_attack(player, target, target_get_attack)
    detect_attack(target, player, player_get_attack)

    if(player["total"]>target["total"]):
        target_get_attack["被攻擊"]=True
    else:
        player_get_attack["被攻擊"]=True

    if target_get_attack["被攻擊"]:
        result["受到攻擊方"].append(target_get_attack)
    if player_get_attack["被攻擊"]:
        result["受到攻擊方"].append(player_get_attack)
    return result

def detect_attack(target, target_2, get_attack_target):
    if(target["all_succ"]):
        get_attack_target["攻擊加值"]+=2
        get_attack_target["被攻擊"]=True
    if(target_2["all_fail"]):
        get_attack_target["攻擊加值"]+=2
    if(target["total"]>=target_2["total"]+5):
        get_attack_target["攻擊加值"]+=2
        get_attack_target["被攻擊"]=True

def generate_get_attacker(get_attack=False, get_attacker="", add_value=0)->dict:
    return {
        "被攻擊":get_attack,
        "攻擊對象":get_attacker,
        "攻擊加值":add_value
    }

def detect_all(target:dict):
    detect_if_all_fail(target)
    detect_if_all_success(target)
    detect_total(target)

def detect_if_all_fail(target:dict):
    if target["出目"]<=target["失誤值"]:
        target["all_fail"] = True
    else:
        target["all_fail"] = False

def detect_if_all_success(target:dict):
    if target["出目"]>=target["奇效值"]:
        target["all_succ"] = True
    else:
        target["all_succ"] = False

def detect_total(target:dict):
    target["total"] = target["出目"]+target["修正值"]

if __name__ == "__main__":
    all_data_path = "all_data.json"
    all_data = load_json(all_data_path)
    player_data = all_data["player"]
    target_data = all_data["enemy"]
    result = battle_detect(player_data, target_data)
    if(result["受到攻擊方"]==[]):
        print("雙方未受到傷害")
    else:
        for i in result["受到攻擊方"]:
            target = i["攻擊對象"]
            add_value = i["攻擊加值"]
            print(f"攻擊對象：{target}\n額外受到：{add_value}攻擊加值\n")
