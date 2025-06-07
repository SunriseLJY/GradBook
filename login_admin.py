import sqlite3


def add_user(role='user'):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    while True:
        username = input(f"请输入要添加的{'管理员' if role == 'admin' else '用户'}用户名: ").strip()
        if not username:
            print("用户名不能为空，请重新输入。")
            continue
        break

    while True:
        password = input(f"请输入{'管理员' if role == 'admin' else '用户'}密码: ").strip()
        if not password:
            print("密码不能为空，请重新输入。")
            continue
        break

    try:
        c.execute("INSERT INTO users (username, password, role) VALUES (?,?,?)", (username, password, role))
        conn.commit()
        print(f"{'管理员' if role == 'admin' else '用户'}添加成功！")
    except sqlite3.IntegrityError:
        print("错误：用户名已存在，请选择其他用户名。")
    finally:
        conn.close()


def delete_user():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    username = input("请输入要删除的用户的用户名: ").strip()
    if not username:
        print("用户名不能为空，请重新输入。")
        return

    c.execute("DELETE FROM users WHERE username =?", (username,))
    if c.rowcount == 0:
        print("错误：未找到该用户名，删除失败。")
    else:
        conn.commit()
        print("用户删除成功！")
    conn.close()


def update_user_info():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    username = input("请输入要修改信息的用户的用户名: ").strip()
    if not username:
        print("用户名不能为空，请重新输入。")
        return

    new_password = input("请输入新密码（留空则不修改）: ").strip()
    new_role = input("请输入新角色（user 或 admin，留空则不修改）: ").strip()

    update_query = "UPDATE users SET "
    params = []
    if new_password:
        update_query += "password =? "
        params.append(new_password)
        if new_role:
            update_query += ", role =? "
            params.append(new_role)
    elif new_role:
        update_query += "role =? "
        params.append(new_role)
    else:
        print("未输入需要修改的信息，操作取消。")
        conn.close()
        return

    update_query += "WHERE username =? "
    params.append(username)

    c.execute(update_query, tuple(params))
    if c.rowcount == 0:
        print("错误：未找到该用户名，修改失败。")
    else:
        conn.commit()
        print("用户信息修改成功！")
    conn.close()


def main():
    while True:
        print("\n请选择操作：")
        print("1. 注册用户")
        print("2. 注册管理员")
        print("3. 删除用户")
        print("4. 更改用户信息")
        print("5. 退出")
        choice = input("输入选项编号: ").strip()

        if choice == '1':
            add_user()
        elif choice == '2':
            add_user(role='admin')
        elif choice == '3':
            delete_user()
        elif choice == '4':
            update_user_info()
        elif choice == '5':
            print("退出程序。")
            break
        else:
            print("无效的选项，请重新输入。")


if __name__ == "__main__":
    main()