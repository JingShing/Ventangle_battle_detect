import json
import tkinter as tk
from tkinter import filedialog, messagebox
# 失誤部分需要重寫一下
# 可能改 total 判定
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

def battle_detect(player, target):
    result = {
        "受到攻擊方": []
    }

    detect_all(player)
    detect_all(target)
    if (player["detect_total"] == target["detect_total"] and not (player["all_succ"] or target["all_succ"])) or (player["all_fail"] and target["all_fail"]):
        return result

    player_get_attack = generate_get_attacker(get_attacker="玩家", add_value=0)
    target_get_attack = generate_get_attacker(get_attacker="敵人", add_value=0)
    detect_attack(player, target, target_get_attack)
    detect_attack(target, player, player_get_attack)

    if player["detect_total"] > target["detect_total"] or target.get("all_fail"):
        target_get_attack["被攻擊"] = True
    elif player["detect_total"] < target["detect_total"] or player.get("all_fail"):
        player_get_attack["被攻擊"] = True

    if target_get_attack["被攻擊"] and not player.get("all_fail"):
        result["受到攻擊方"].append(target_get_attack)
    if player_get_attack["被攻擊"] and not target.get("all_fail"):
        result["受到攻擊方"].append(player_get_attack)
    return result

def detect_attack(target, target_2, get_attack_target):
    if target["all_succ"]:
        get_attack_target["攻擊加值"] += 2
        get_attack_target["被攻擊"] = True
        get_attack_target["加值原因"].append("對方奇效")
    if target["detect_total"] >= target_2["detect_total"] + target["GB"]:
        get_attack_target["攻擊加值"] += 2
        get_attack_target["被攻擊"] = True
        get_attack_target["加值原因"].append("對方GB加值")
    if target_2["all_fail"]:
        get_attack_target["攻擊加值"] += 2
        get_attack_target["加值原因"].append("自身失誤")

def generate_get_attacker(get_attack=False, get_attacker="", add_value=0):
    return {
        "被攻擊": get_attack,
        "攻擊對象": get_attacker,
        "攻擊加值": add_value,
        "加值原因":[]
    }

def detect_all(target):
    detect_if_all_fail(target)
    detect_if_all_success(target)
    detect_total(target)

def detect_if_all_fail(target):
    if target["出目"] <= target["失誤值"]:
        target["all_fail"] = True
    else:
        target["all_fail"] = False

def detect_if_all_success(target):
    if target["出目"] >= target["奇效值"]:
        target["all_succ"] = True
    else:
        target["all_succ"] = False

def detect_total(target):
    target["總和值"] = target["出目"] + target["修正值"]
    target["detect_total"] = target["出目"] + target["修正值"]

class BattleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ventangle Battle Detector")
        self.player_data = {}
        self.enemy_data = {}

        self.create_widgets()

    def create_widgets(self):
        self.load_button = tk.Button(self.root, text="Load(讀取) JSON", command=self.load_json_data)
        self.load_button.pack()

        self.save_player_button = tk.Button(self.root, text="Save(保存) JSON", command=lambda: self.save_json_data("player"))
        self.save_player_button.pack()

        self.detect_button = tk.Button(self.root, text="Detect Battle(戰鬥判定)", command=self.detect_battle)
        self.detect_button.pack()

        self.player_frame = tk.LabelFrame(self.root, text="Player(玩家) Data")
        self.player_frame.pack(fill="both", expand="yes")
        self.create_data_inputs(self.player_frame, "player")

        self.enemy_frame = tk.LabelFrame(self.root, text="Enemy(敵人) Data")
        self.enemy_frame.pack(fill="both", expand="yes")
        self.create_data_inputs(self.enemy_frame, "enemy")

    def create_data_inputs(self, frame, entity):
        setattr(self, f"{entity}_出目", self.create_input_field(frame, "出目", 6))
        setattr(self, f"{entity}_修正值", self.create_input_field(frame, "修正值", 2))
        setattr(self, f"{entity}_奇效值", self.create_input_field(frame, "奇效值", 12))
        setattr(self, f"{entity}_失誤值", self.create_input_field(frame, "失誤值", 2))
        setattr(self, f"{entity}_GB", self.create_input_field(frame, "GB", 5))

    def create_input_field(self, frame, label_text, default_value):
        frame_row = tk.Frame(frame)
        frame_row.pack(side="top", fill="x")

        label = tk.Label(frame_row, text=label_text)
        label.pack(side="left")

        entry = tk.Entry(frame_row)
        entry.insert(0, str(default_value))
        entry.pack(side="right")

        return entry

    def load_json_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            data = load_json(file_path)
            if data:
                self.player_data = data.get("player", {})
                self.enemy_data = data.get("enemy", {})
                self.update_inputs("player", self.player_data)
                self.update_inputs("enemy", self.enemy_data)

    def save_json_data(self, entity):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            data = {
                "player": self.collect_inputs("player"),
                "enemy": self.collect_inputs("enemy")
            }
            save_json(data, file_path)

    def update_inputs(self, entity, data):
        for key, value in data.items():
            input_field = getattr(self, f"{entity}_{key}", None)
            if input_field:
                input_field.delete(0, tk.END)
                input_field.insert(0, str(value))

    def collect_inputs(self, entity):
        data = {}
        for key in ["出目", "修正值", "奇效值", "失誤值", "GB"]:
            input_field = getattr(self, f"{entity}_{key}")
            if input_field:
                data[key] = int(input_field.get())
        return data

    def detect_battle(self):
        self.player_data = self.collect_inputs("player")
        self.enemy_data = self.collect_inputs("enemy")
        result = battle_detect(self.player_data, self.enemy_data)
        if result["受到攻擊方"] == []:
            messagebox.showinfo("Result", "雙方未受到傷害")
        else:
            results_text = ""
            for i in result["受到攻擊方"]:
                target = i["攻擊對象"]
                add_value = i["攻擊加值"]
                results_text += f"攻擊對象：{target}\n額外受到：{add_value}攻擊加值\n"
                if i["加值原因"]!=[]:
                    results_text += "加值原因：\n"
                    for j in i["加值原因"]:
                        results_text+=j+"\n"
                results_text+="\n"
            messagebox.showinfo("Result", results_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = BattleApp(root)
    root.geometry("350x400")
    root.mainloop()
