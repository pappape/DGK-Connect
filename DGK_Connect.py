import tkinter as tk
from PIL import Image, ImageTk
import subprocess
import threading

class CloudflareApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DGK Server Connect")
        
        # 最低ウィンドウサイズを設定
        self.root.minsize(300, 350)
        self.root.maxsize(300, 350)
        
        # 背景画像を読み込む
        self.bg_image = Image.open("./background.jpg")  # ここに画像ファイルパス
        self.bg_image = self.bg_image.resize((300, 350))  # ウィンドウに合わせてリサイズ
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)
        
        # キャンバスに背景画像を表示
        self.canvas = tk.Canvas(root, width=300, height=350)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")
        
        # 接続ボタン
        self.connect_button = tk.Button(root, text="サーバーへ接続", command=self.start_tunnel)
        self.canvas.create_window(150, 80, window=self.connect_button)  # ボタンの位置を調整
        
        # エラーメッセージ表示用ラベル
        self.error_label = tk.Label(root, text="", fg="red")  # 背景色なし
        self.error_label_window = self.canvas.create_window(150, 220, window=self.error_label)  # ラベルをキャンバスに配置
        self.canvas.itemconfig(self.error_label_window, state="hidden")  # ラベルを非表示

        # サーバー接続状況表示用リストラベル
        self.server_list_label = tk.Label(root, text="", fg="black", wraplength=450)  # テキストが折り返される
        self.server_list_window = self.canvas.create_window(150, 160, window=self.server_list_label)  # リストラベルをキャンバスに配置

        # バージョン情報と著作権情報をキャンバスに追加
        self.info_label1 = tk.Label(root, text="DGK Server Connect 1.0", fg="gray")
        self.info_label2 = tk.Label(root, text="Copyright © 2024 pappape. All rights reserved.", fg="gray")
        self.canvas.create_window(150, 340, window=self.info_label2)  # 著作権ラベルをキャンバスに配置
        self.canvas.create_window(150, 310, window=self.info_label1)  # バージョンラベルをキャンバスに配置
        
        self.processes = []  # プロセスを保持するリスト
        self.server_labels = {
            "mc-dgk01.pappape.f5.si": "DGK01 → localhost:25565",
            "mc-dgk02.pappape.f5.si": "DGK02 → localhost:25566",
            "mc-dgk03.pappape.f5.si": "DGK03 → localhost:25567",
            "mc-dgk04.pappape.f5.si": "DGK04 → localhost:25568"
        }

        # ウィンドウを閉じる際のイベント処理
        root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def start_tunnel(self):
        if not self.processes:
            # エラーメッセージをクリア
            self.error_label.config(text="")
            self.canvas.itemconfig(self.error_label_window, state="hidden")  # ラベルを非表示
            # サーバーリストを初期化
            self.server_list_label.config(text="\n".join(self.server_labels.values()))
            # サブスレッドでコマンドを実行
            threading.Thread(target=self.run_cloudflared).start()

    def run_cloudflared(self):
        try:
            # cloudflaredを複数実行
            servers = [
                ("mc-dgk01.pappape.f5.si", "localhost:25565"),
                ("mc-dgk02.pappape.f5.si", "localhost:25566"),
                ("mc-dgk03.pappape.f5.si", "localhost:25567"),
                ("mc-dgk04.pappape.f5.si", "localhost:25568")
            ]
            
            for hostname, local_url in servers:
                process = subprocess.Popen(
                    ["cloudflared", "access", "rdp", "--hostname", hostname, "--url", local_url],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL  # 出力を無効化
                )
                self.processes.append(process)
            
            # 接続ボタンを無効化し、切断ボタンを有効化
            self.connect_button.config(text="切断", command=self.stop_tunnel)
        except FileNotFoundError:
            # cloudflaredがインストールされていない場合
            self.show_error("Cloudflaredがインストールされていません。\nwingetでインストールを試みます...")
            self.install_cloudflared()
        except Exception as e:
            # その他のエラー
            self.show_error(f"エラーが発生しました: {str(e)}")

    def install_cloudflared(self):
        try:
            # cmdでwingetを使ってcloudflaredをインストールする
            subprocess.run(["cmd", "/c", "start", "cmd", "/k", "winget install --id Cloudflare.cloudflared"], check=True)
            self.show_error("Cloudflaredがインストールされていません。\nインストールが完了したら再度接続を試みてください。")
        except Exception as e:
            # インストール失敗時のエラー表示
            self.show_error(f"インストールに失敗しました: {str(e)}")
    
    def show_error(self, message):
        # エラーメッセージをラベルに表示
        self.error_label.config(text=message)
        self.canvas.itemconfig(self.error_label_window, state="normal")  # ラベルを表示
    
    def stop_tunnel(self):
        for process in self.processes:
            if process is not None:
                # プロセスを終了
                process.terminate()
                process.wait()
        self.processes = []  # プロセスリストをリセット
        # ボタンの状態を戻す
        self.connect_button.config(text="サーバーへ接続", command=self.start_tunnel)
        self.error_label.config(text="")
        self.canvas.itemconfig(self.error_label_window, state="hidden")  # ラベルを非表示
        # サーバーリストをクリア
        self.server_list_label.config(text="")
    
    def on_closing(self):
        self.stop_tunnel()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = CloudflareApp(root)
    root.mainloop()