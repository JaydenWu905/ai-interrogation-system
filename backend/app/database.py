import json # 记得顶部引入 json 模块，因为我们要用它来处理字符串和字典之间的转换
from sqlmodel import SQLModel, create_engine, Session, select
from app.models import User, Record # 必须引入刚才写的模型，不然系统不知道要建什么表

# 1. 指定数据库文件名，它会自动在你项目的根目录生成一个 database.db 文件
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# 2. 创建引擎 (echo=True 可以在终端打印出它底层偷偷执行的 SQL 语句，方便你学习)
engine = create_engine(sqlite_url, echo=False, connect_args={"check_same_thread": False})

# 3. 建表函数
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# 4. 核心：自动播种测试数据的函数
def seed_test_data():
    with Session(engine) as session:
        # 1. 注入警员账号 (之前的逻辑)
        statement = select(User).where(User.police_number == "PC123456")
        existing_user = session.exec(statement).first()
        
        if not existing_user:
            print("🌱 检测到全新数据库，正在注入测试警员数据...")
            user1 = User(police_number="PC123456", password="123", name="张警官", department="刑侦大队")
            user2 = User(police_number="PC888888", password="123", name="李警官", department="扫黑除恶中队")
            session.add(user1)
            session.add(user2)
            session.commit()
            print("✅ 测试警员账号注入成功！")

        # 2. 【新增】注入历史笔录数据
        record_statement = select(Record).where(Record.police_number == "PC123456")
        existing_record = session.exec(record_statement).first()
        
        if not existing_record:
            print("📜 正在注入历史笔录测试数据...")
            
            # 伪造一份已经完结的偷窃案笔录
            fake_info = json.dumps({
                "案情": "报案人称在网吧打游戏时，放在桌上的手机被盗。",
                "发生时间": "2023年10月24日 晚上22:00左右",
                "发生地点": "星际网吧 08号机位",
                "嫌疑人信息": "疑似一名穿黑色连帽卫衣的瘦高男子"
            }, ensure_ascii=False)
            
            record1 = Record(
                police_number="PC123456",
                title="网吧手机被盗案",
                content="AI警官：我们是xx区公安分局...\n嫌疑人：明白。\nAI警官：请你详细叙述...\n嫌疑人：我昨天晚上在网吧打游戏，手机放桌上被偷了。\nAI警官：时间地点是？\n嫌疑人：十点多，星际网吧08号机。\nAI警官：有没有嫌疑人线索？\n嫌疑人：有个穿黑卫衣的瘦高个一直在后面转悠，就这些了。\nAI警官：本次笔录已结束...",
                status="笔录结束",
                extracted_info=fake_info
            )
            
            session.add(record1)
            session.commit()
            print("✅ 历史笔录数据注入成功！")

# 5. 依赖注入函数 (将来给 FastAPI 接口用的)
def get_session():
    with Session(engine) as session:
        yield session