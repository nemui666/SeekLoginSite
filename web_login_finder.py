from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import time
import re
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# 検索に使用する語句を設定
SEARCH_WORD = "toto login"

class LoginPageFinder:
    def __init__(self, debug=False):
        self.debug = debug  # デバッグフラグを追加
        
        # Chromeオプションの設定
        self.chrome_options = Options()
        
        # ウィンドウサイズを設定
        self.chrome_options.add_argument('--window-size=1920,1080')
        
        # ロボット検出を回避するための追加設定
        self.chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        self.chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        self.chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # ChromeDriverManagerを使用
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=self.chrome_options)
        
        # JavaScriptを実行してwebdriverフラグを削除
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        self.login_keywords = ['ログイン', 'サインイン', 'login', 'sign in', 'signin']
        
    def debug_print(self, message):
        """デバッグメッセージを表示する補助関数"""
        if self.debug:
            print(message)

    def search_google(self, query, num_pages=10):
        all_links = []
        self.debug_print(f"\n[DEBUG] Google検索を開始: クエリ「{query}」")
        
        # より人間らしい動作を模倣
        self.driver.get('https://www.google.com')
        time.sleep(2)
        
        search_box = self.driver.find_element(By.NAME, 'q')
        for char in query:
            search_box.send_keys(char)
            time.sleep(0.1)
        
        time.sleep(1)
        search_box.send_keys(Keys.RETURN)
        
        for page in range(num_pages):
            time.sleep(2)
            self.debug_print(f"\n[DEBUG] ページ {page + 1}/{num_pages} を処理中...")
            
            # ページを一番下までスクロール
            self.debug_print("[DEBUG] ページを一番下までスクロール中...")
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)  # スクロール後の読み込みを待つ
            
            links = self.driver.find_elements(By.CSS_SELECTOR, 'div.yuRUbf > a')
            self.debug_print("[DEBUG] div.yuRUbf > a でリンクを検索中...")
            
            if not links:
                self.debug_print("[DEBUG] 最初のセレクターで結果なし。h3.r > a で再試行...")
                links = self.driver.find_elements(By.CSS_SELECTOR, 'h3.r > a')
            if not links:
                self.debug_print("[DEBUG] 2番目のセレクターでも結果なし。XPATHで再試行...")
                links = self.driver.find_elements(By.XPATH, "//a[h3]")
            
            current_page_links = [link.get_attribute('href') for link in links if link.get_attribute('href')]
            self.debug_print(f"[DEBUG] 現在のページで {len(current_page_links)} 件のリンクを発見")
            
            all_links.extend(current_page_links)
            
            # 次のページへ移動（最後のページ以外）
            if page < num_pages - 1:
                try:
                    self.debug_print("[DEBUG] 次のページへの移動を試行...")
                    
                    # 「次へ」ボタンの検索方法を改善
                    next_button = None
                    
                    # 複数の方法で「次へ」ボタンを探す
                    selectors = [
                        "//span[text()='次へ']/parent::a",  # 日本語の「次へ」
                        "//span[text()='Next']/parent::a",  # 英語の「Next」
                        "//a[@id='pnnext']",  # IDによる検索
                        "//a[@aria-label='次のページ']",  # aria-labelによる検索
                        "//a[@aria-label='Next page']"  # 英語のaria-label
                    ]
                    
                    for selector in selectors:
                        try:
                            next_button = self.driver.find_element(By.XPATH, selector)
                            if next_button:
                                self.debug_print(f"[DEBUG] 「次へ」ボタンを発見: {selector}")
                                break
                        except:
                            continue
                    
                    if next_button and next_button.is_displayed() and next_button.is_enabled():
                        # スクロールして「次へ」ボタンを表示
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                        time.sleep(1)
                        
                        # クリックを試行
                        try:
                            next_button.click()
                            self.debug_print("[DEBUG] 「次へ」ボタンのクリックに成功")
                        except:
                            # JavaScriptでのクリックを試行
                            self.driver.execute_script("arguments[0].click();", next_button)
                            self.debug_print("[DEBUG] JavaScriptでの「次へ」ボタンのクリックに成功")
                        
                        time.sleep(2)  # ページ遷移を待つ
                    else:
                        self.debug_print("[DEBUG] クリック可能な「次へ」ボタンが見つかりません")
                        break
                        
                except Exception as e:
                    self.debug_print(f"[DEBUG] 次のページへの移動失敗: {str(e)}")
                    break
        
        unique_links = list(set(all_links))
        self.debug_print(f"\n[DEBUG] 重複除去後の総リンク数: {len(unique_links)} 件")
        return unique_links

    def is_login_page(self, url):
        try:
            self.debug_print(f"\n[DEBUG] URLにアクセス中: {url}")
            self.driver.get(url)
            time.sleep(2)
            
            # ページ内のテキストとHTML要素を確認
            page_source = self.driver.page_source.lower()
            
            # パスワードフィールドの確認
            password_fields = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="password"]')
            self.debug_print(f"[DEBUG] パスワードフィールド数: {len(password_fields)}")
            
            # キーワードの確認
            found_keywords = [keyword for keyword in self.login_keywords if keyword.lower() in page_source]
            self.debug_print("[DEBUG] 検出されたキーワード:")
            if found_keywords:
                for keyword in found_keywords:
                    self.debug_print(f"  - {keyword}")
            else:
                self.debug_print("  キーワードは検出されませんでした")
            
            has_password_field = len(password_fields) > 0
            has_login_keywords = len(found_keywords) > 0
            
            result = has_password_field and has_login_keywords
            self.debug_print(f"[DEBUG] 判定結果: {'ログインページです' if result else 'ログインページではありません'}")
            self.debug_print(f"  - パスワードフィールド: {'あり' if has_password_field else 'なし'}")
            self.debug_print(f"  - ログインキーワード: {'あり' if has_login_keywords else 'なし'}")
            
            return result
            
        except TimeoutException:
            self.debug_print(f"[DEBUG] タイムアウトエラー: {url}")
            return False
        except Exception as e:
            self.debug_print(f"[DEBUG] エラー発生: {url}")
            self.debug_print(f"エラー内容: {str(e)}")
            return False

    def find_login_sites(self, search_query):
        login_sites = []
        self.debug_print(f"\n検索クエリ「{search_query}」でGoogleの検索を開始します...")
        urls = self.search_google(search_query)
        
        # 検索結果の件数を表示
        total_urls = len(urls)
        self.debug_print(f"\n【検索結果サマリー】")
        self.debug_print(f"・検索でヒットしたURL数: {total_urls} 件")
        self.debug_print(f"・ログインページ検査を開始します...\n")
        
        for i, url in enumerate(urls, 1):
            self.debug_print(f"[{i}/{total_urls}] {url} を検査中...")
            if self.is_login_page(url):
                login_sites.append(url)
                self.debug_print(f"✓ ログインページを検出しました！")
            else:
                self.debug_print("× ログインページではありません")
            self.debug_print("-" * 80)  # 区切り線
        
        # 最終結果のサマリーを表示
        self.debug_print(f"\n【最終結果】")
        self.debug_print(f"・検索でヒットしたURL数: {total_urls} 件")
        self.debug_print(f"・ログインページと判定されたURL数: {len(login_sites)} 件")
        self.debug_print(f"・検出率: {(len(login_sites)/total_urls*100):.1f}%" if total_urls > 0 else "・検出率: 0%")
        return login_sites

    def close(self):
        self.driver.quit()

def main():
    # デバッグモードを指定してインスタンスを作成
    finder = LoginPageFinder(debug=True)  # Trueで詳細表示、Falseで通常表示
    try:
        search_query = SEARCH_WORD
        print("\n処理を開始します...")
        print("Chromeブラウザを初期化中...")
        login_sites = finder.find_login_sites(search_query)
        
        print("\n【検出されたログインページ一覧】")
        if login_sites:
            for i, site in enumerate(login_sites, 1):
                print(f"{i}. {site}")
        else:
            print("ログインページは見つかりませんでした。")
            
    finally:
        print("\nブラウザを終了しています...")
        finder.close()

if __name__ == "__main__":
    main() 