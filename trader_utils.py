import time

from pywinauto import Application, keyboard, findwindows

from stock_utils import setup_logger

logging = setup_logger()


def start_app(app_path):
    """
    启动同花顺股票交易顺软件
    :param app_path:
    :return:
    """
    ths_app = Application(backend='uia').start(app_path)
    time.sleep(5)

    # 获取窗口对象
    # app_window = ths_app.window(control_id=0xC370)

    # 聚焦应用窗口
    ths_app.windows()

    # 模拟按键F12启动交易窗口
    keyboard.send_keys('{F12}')  # Ctrl + A 和 Ctrl + C
    time.sleep(2)

    # 获得交易系统窗口句柄
    trade_app = Application().connect(title_re="网上股票交易系统*", timeout=10)
    trade_window = trade_app.window(title_re="网上股票交易系统*")

    # 激活窗口
    trade_app.top_window().set_focus()
    keyboard.send_keys("{ENTER}")

    # 找到菜单子窗口
    menu_tree = trade_window.window(control_id=0x81, class_name='SysTreeView32')

    return ths_app, trade_window, menu_tree


def buy_or_sell_stock(app_test, main_window, code, price, count):
    main_window.window(control_id=0x408, class_name="Edit").set_text("")  # 设置股票代码
    time.sleep(1)
    main_window.window(control_id=0x408, class_name="Edit").type_keys(str(code))  # 设置股票代码
    time.sleep(1)
    main_window.window(control_id=0x40A, class_name="Edit").set_text("")  # 设置股数目
    time.sleep(1)
    main_window.window(control_id=0x40A, class_name="Edit").type_keys(str(count))  # 设置股数目
    time.sleep(1)
    main_window.window(control_id=0x409, class_name="Edit").set_text("")  # 设置股票价格
    time.sleep(1)
    main_window.window(control_id=0x409, class_name="Edit").type_keys(str(price))  # 设置股票价格
    time.sleep(1)
    main_window.window(control_id=0x3EE, class_name="Button").click()  # 点击卖出or买入

    time.sleep(1)
    keyboard.send_keys("{ENTER}")

    # 委托确认
    time.sleep(1)
    logging.info("识别委托确认窗口")

    window_parent = None
    ok_btn = None
    elements = findwindows.find_elements(
        class_name='#32770', backend='win32', process=app_test.process)

    for e in elements:
        window_parent = app_test.window(handle=e.handle)
        ok_btn = window_parent.window(control_id=0x06)

        try:
            ok_btn.window_text()  # 确认找到了验证码子窗口
            logging.info("找到委托确认窗口")
            break

        except Exception as e:
            ok_btn = None
            logging.warning(e)
            continue

    if ok_btn is not None:
        logging.info("点击委托确认按钮")
        ok_btn.click()

    result = {"success": True}

    keyboard.send_keys("{ENTER}")

    return result


def cancel_stock(app_test, main_window, cancel_type):
    """
    根据取消类型执行相应的撤单操作。
    :param cancel_type: 撤单类型 (str)，例如 '撤买'、'撤卖'、'撤最后'、'全撤'
    """
    # 使用 switch 语句模拟选择不同的撤单操作
    if cancel_type == "全撤":
        main_window.window(control_id=0x7531, class_name="Button").click()  # 点击全撤
    elif cancel_type == "撤买":
        main_window.window(control_id=0x7532, class_name="Button").click()  # 点击撤买
    elif cancel_type == "撤卖":
        main_window.window(control_id=0x7533, class_name="Button").click()  # 点击撤卖
    elif cancel_type == "撤最后":
        main_window.window(control_id=0x79A, class_name="Button").click()  # 点击撤最后
    else:
        print(f"错误：无效的撤单类型 '{cancel_type}'")

    time.sleep(1)
    window_parent = None
    ok_btn = None
    elements = findwindows.find_elements(
        class_name='#32770', backend='win32', process=app_test.process)

    for e in elements:
        window_parent = app_test.window(handle=e.handle)
        ok_btn = window_parent.window(control_id=0x06)

        try:
            ok_btn.window_text()  # 确认找到了验证码子窗口
            logging.info("找到委托确认窗口")
            break

        except Exception as e:
            ok_btn = None
            logging.warning(e)
            continue

    time.sleep(1)
    if ok_btn is not None:
        logging.info("点击委托确认按钮")
        ok_btn.click()

    result = {"success": True}

    keyboard.send_keys("{ENTER}")

    return result


def query_stock():
    pass


def stock_buy(app, menu, window, stock_code, stock_price, stock_number):
    menu.get_item(['买入[F1]']).click()
    menu.wait('ready', 2)  # 等待窗口响应
    buy_or_sell_stock(app, window, stock_code, stock_price, stock_number)
    time.sleep(3)
    keyboard.send_keys("{ENTER}")
    print('买入操作完成！')
    time.sleep(1)


def stock_sell(app, menu, window, stock_code, stock_price, stock_number):
    menu.get_item(['卖出[F2]']).click()
    menu.wait('ready', 2)  # 等待窗口响应
    buy_or_sell_stock(app, window, stock_code, stock_price, stock_number)
    time.sleep(3)
    keyboard.send_keys("{ENTER}")
    print('卖出操作完成!')
    time.sleep(1)


def stock_cancel(app, menu, window):
    menu.get_item(['撤单[F3]']).click()
    menu.wait('ready', 2)  # 等待窗口响应
    cancel_stock(app, window, "撤卖")
    time.sleep(3)
    keyboard.send_keys("{ENTER}")
    print('撤单操作完成!')
    time.sleep(1)
