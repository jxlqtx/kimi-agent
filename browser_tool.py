from playwright.sync_api import sync_playwright
import json

class BrowserTool:
    def __init__(self):
        self.playwright = sync_playwright().start()
        self.browser = None
        self.page = None
    
    def start(self, headless=False):
        """启动浏览器"""
        self.browser = self.playwright.chromium.launch(headless=headless)
        self.page = self.browser.new_page()
        return "浏览器已启动"
    
    def navigate(self, url):
        """访问网页"""
        self.page.goto(url)
        return f"已访问: {url}"
    
    def search(self, query):
        """执行搜索"""
        self.page.goto(f"https://www.bing.com/search?q={query}")
        results = self.page.query_selector_all('li.b_algo')
        return [r.inner_text()[:200] for r in results[:5]]
    
    def get_content(self, selector):
        """获取页面元素内容"""
        element = self.page.query_selector(selector)
        return element.inner_text() if element else "未找到元素"
    
    def screenshot(self, path="screenshot.png"):
        """截图保存"""
        self.page.screenshot(path=path)
        return f"截图已保存: {path}"
    
    def close(self):
        """关闭浏览器"""
        if self.browser:
            self.browser.close()
        self.playwright.stop()
        return "浏览器已关闭"

# 与 AutoAgent 集成
def browser_search(query):
    tool = BrowserTool()
    tool.start(headless=True)
    results = tool.search(query)
    tool.close()
    return json.dumps(results, ensure_ascii=False, indent=2)
