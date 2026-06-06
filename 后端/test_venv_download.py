import sys
import os
import importlib.util


def print_status(component, status, message=""):
    color = "\033[92m" if status else "\033[91m"  # Green or Red
    reset = "\033[0m"
    icon = "[OK]" if status else "[MISSING]"
    print(f"{color}{icon} {component:<30}{reset} {message}")
    return status


def check_venv():
    print("\n=== 1. 虚拟环境检查 ===")
    # 检查 sys.prefix 是否与 sys.base_prefix 不同，或者路径中是否包含 venv/.venv
    is_venv = (sys.prefix != sys.base_prefix) or ('venv' in sys.prefix) or ('.venv' in sys.prefix)

    if is_venv:
        print_status("Virtual Environment", True, f"已激活: {sys.prefix}")
    else:
        print_status("Virtual Environment", False, "警告: 当前未检测到虚拟环境！建议激活 .venv")
    return is_venv


def check_dependencies():
    print("\n=== 2. 关键依赖库检查 ===")
    # (Pip包名, 导入名)
    requirements = [
        ("Django", "django"),
        ("Django REST Framework", "rest_framework"),
        ("Django CORS Headers", "corsheaders"),  # 刚才报错的元凶
        ("Simple JWT", "rest_framework_simplejwt"),  # 刚才新增的鉴权
        ("Pillow", "PIL"),  # 图片处理
        ("Requests", "requests"),  # 用于测试脚本
    ]

    all_passed = True
    for package_name, import_name in requirements:
        if importlib.util.find_spec(import_name) is None:
            print_status(package_name, False, f"未安装 (请运行 pip install {package_name.lower().replace(' ', '-')})")
            all_passed = False
        else:
            # 尝试获取版本
            try:
                module = __import__(import_name)
                ver = getattr(module, '__version__', '未知版本')
                print_status(package_name, True, f"Ver: {ver}")
            except:
                print_status(package_name, True, "已安装")

    return all_passed


def check_django_settings():
    print("\n=== 3. Django 配置检查 ===")
    try:
        # 设置 Django 环境
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
        import django
        django.setup()
        from django.conf import settings

        apps = settings.INSTALLED_APPS
        middleware = settings.MIDDLEWARE

        # 检查 CORS
        has_cors_app = 'corsheaders' in apps
        has_cors_mw = 'corsheaders.middleware.CorsMiddleware' in middleware
        print_status("CORS App", has_cors_app, "INSTALLED_APPS 包含 'corsheaders'")
        print_status("CORS Middleware", has_cors_mw, "MIDDLEWARE 包含 CorsMiddleware")

        # 检查 JWT
        has_jwt_app = 'rest_framework_simplejwt' in apps
        print_status("SimpleJWT App", has_jwt_app, "INSTALLED_APPS 包含 'rest_framework_simplejwt'")

        # 检查 User Model
        user_model = settings.AUTH_USER_MODEL
        print_status("User Model", user_model == 'users.UserProfile', f"当前设置: {user_model}")

        return True
    except Exception as e:
        print(f"\033[91m[ERROR] Django 配置加载失败: {e}\033[0m")
        print("提示: 这通常意味着 settings.py 里有语法错误，或者依赖没装好。")
        return False


if __name__ == "__main__":
    print("🚀 开始全栈环境自检...")
    v = check_venv()
    d = check_dependencies()

    # 只有依赖都齐了，才检查 Django 配置，否则肯定报错
    if d:
        s = check_django_settings()
    else:
        print("\n⚠️ 跳过 Django 配置检查，请先修复缺失的依赖库。")
        s = False

    print("\n" + "=" * 40)
    if v and d and s:
        print("\033[92m✅ 环境完美！可以启动 Django (python manage.py runserver)\033[0m")
    else:
        print("\033[91m❌ 环境存在问题，请根据上方提示修复。\033[0m")
    print("=" * 40)