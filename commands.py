from models.post import BoardModel, PostModel
from models.user import PermissionModel, RoleModel, PermissionEnum, UserModel
from exts import db
from faker import Faker

import click
import random

def create_permission():
    for permission_name in dir(PermissionEnum):
        if permission_name.startswith("__"):
            continue
        permission = PermissionModel(name=getattr(PermissionEnum,permission_name))
        db.session.add(permission)
    db.session.commit()
    click.echo("权限添加成功！")


def create_role():
    # 稽查
    inspector = RoleModel(name="稽查",desc="负责审核帖子和评论是否合法合规！")
    inspector.permissions = PermissionModel.query.filter(PermissionModel.
    name.in_([PermissionEnum.POST,PermissionEnum.COMMENT])).all()

    # 运营
    operator = RoleModel(name="运营", desc="复制网站持续正常运营！")
    operator.permissions = PermissionModel.query.filter(PermissionModel.
    name.in_([
     PermissionEnum.POST,
     PermissionEnum.COMMENT,
     PermissionEnum.BOARD,
     PermissionEnum.FRONT_USER,
     PermissionEnum.CMS_USER
    ])).all()

    # 管理员
    administrator = RoleModel(name="管理员",desc="负责整个网站所有工作！")
    administrator.permissions = PermissionModel.query.all()

    normal_user = RoleModel(name="普通用户", desc="网站的基础注册用户，仅限前台操作！")
    normal_user.permissions = PermissionModel.query.filter(PermissionModel.name.in_([
        PermissionEnum.POST,
        PermissionEnum.COMMENT
    ])).all()

    db.session.add_all([inspector, operator, administrator, normal_user])
    db.session.commit()
    click.echo("角色添加成功！")


def create_test_user():
    common_role = RoleModel.query.filter_by(name="普通用户").first()

    if not common_role:
        click.echo("❌ 找不到'普通用户'角色，请先运行 flask create-role")
        return

    # 18 个真实感网名（已避开已有用户）
    names = [
        "星空下的猫", "风之子", "代码搬运工", "夏天吃西瓜", "孤独的根号三",
        "晚风", "追光者", "林深见鹿", "一蓑烟雨", "木木",
        "清晨的露水", "山海不可平", "橘子汽水", "南山南", "落日余晖",
        "半夏微凉", "流年似水", "听风者"
    ]

    # 配套的拼音前缀（用作邮箱和密码，全小写）
    prefixes = [
        "xingkong", "fengzhizi", "daima", "xigua", "gudu",
        "wanfeng", "zhuiguang", "linshen", "yisuo", "mumu",
        "qingchen", "shanhai", "juzi", "nanshan", "luori",
        "banxia", "liunian", "tingfeng"
    ]

    added_count = 0
    skipped_count = 0

    for i in range(len(names)):
        username = names[i]
        prefix = prefixes[i]
        email = f"{prefix}@qq.com"
        password = f"{prefix}123"  # 密码加上123，防止太简单被拦截

        # 查重，防止重复运行报错
        existing_user = UserModel.query.filter_by(email=email).first()

        if not existing_user:
            new_user = UserModel(
                username=username,
                email=email,
                password=password,
                is_staff=False,
                role=common_role
            )
            db.session.add(new_user)
            added_count += 1
        else:
            skipped_count += 1

    db.session.commit()

    click.echo(f"🎉 本次新添加了 {added_count} 个真实感用户。")
    if skipped_count > 0:
        click.echo(f"⚠️ 有 {skipped_count} 个用户已存在，自动跳过。")

@click.option("--username", '-u')
@click.option("--email", '-e')
@click.option("--password", '-p')
def create_admin(username, email, password):
    admin_role = RoleModel.query.filter_by(name="管理员").first()
    admin_user = UserModel(username=username, email=email, password=password,
    is_staff=True, role=admin_role)
    db.session.add(admin_user)
    db.session.commit()
    click.echo("管理员创建成功！")

def create_board():
    board_names = ['Python语法', 'Web开发', '数据分析', '测试开发', '运维开发']
    for board_name in board_names:
        board = BoardModel(name=board_name)
        db.session.add(board)
    db.session.commit()
    click.echo("板块添加成功！")

def create_test_post():
    fake = Faker(locale="zh_CN")
    author = UserModel.query.first()
    boards = BoardModel.query.all()
    if not author:
        click.echo("数据库里没有用户，请先注册一个账号！")
        return

    click.echo("开始生成测试帖子...")
    for x in range(98):
        title = fake.sentence()
        content = fake.paragraph(nb_sentences=10)
        random_index = random.randint(0, 4)
        board = boards[random_index]
        post = PostModel(title=title, content=content, board=board, author=author)
        db.session.add(post)
    db.session.commit()
    click.echo("测试帖子生成成功！")
