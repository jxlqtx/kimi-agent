import schedule
import time
import threading
from datetime import datetime

class TaskScheduler:
    def __init__(self):
        self.jobs = []
        self.running = False
    
    def add_daily_task(self, time_str, task_func, *args):
        """添加每日任务"""
        job = schedule.every().day.at(time_str).do(task_func, *args)
        self.jobs.append(job)
        return f"已添加每日任务: {time_str}"
    
    def add_interval_task(self, minutes, task_func, *args):
        """添加间隔任务"""
        job = schedule.every(minutes).minutes.do(task_func, *args)
        self.jobs.append(job)
        return f"已添加间隔任务: 每 {minutes} 分钟"
    
    def start(self):
        """启动调度器"""
        self.running = True
        def run_scheduler():
            while self.running:
                schedule.run_pending()
                time.sleep(1)
        
        thread = threading.Thread(target=run_scheduler)
        thread.daemon = True
        thread.start()
        return "调度器已启动"

# 示例任务
def daily_report():
    print(f"[{datetime.now()}] 生成每日报告...")
    # 调用 Kimi 生成报告
    # 发送邮件或保存文件

def health_check():
    print(f"[{datetime.now()}] 系统健康检查...")

# 使用示例
if __name__ == "__main__":
    scheduler = TaskScheduler()
    scheduler.add_daily_task("09:00", daily_report)
    scheduler.add_interval_task(30, health_check)
    scheduler.start()
    
    print("定时任务已启动，按 Ctrl+C 停止")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("已停止")
