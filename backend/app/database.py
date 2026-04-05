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
        # 先查一下数据库里是不是已经有张警官了
        statement = select(User).where(User.police_number == "PC123456")
        existing_user = session.exec(statement).first()
        
        # 如果没有，说明是第一次运行，我们赶紧插入两个测试账号！
        if not existing_user:
            print("🌱 检测到全新数据库，正在注入测试警员数据...")
            user1 = User(police_number="PC123456", password="123", name="张警官", department="刑侦大队")
            user2 = User(police_number="PC888888", password="123", name="李警官", department="扫黑除恶中队")
            
            session.add(user1)
            session.add(user2)
            session.commit() # 提交保存到硬盘
            print("✅ 测试警员账号注入成功！")

# 5. 依赖注入函数 (将来给 FastAPI 接口用的)
def get_session():
    with Session(engine) as session:
        yield session