from time import sleep
import cv2
import numpy as np
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from urllib.request import urlretrieve
from selenium import webdriver
import PIL.Image as image
from PIL import Image

__all__ = ["LoginDisposeSliding"]
# 方块和缺口所在区域、图片路径
left_region = (0, 0, 63, 169)
right_region = (63, 0, 300, 169)
left_image = './images/left.png'
right_image = './images/right.png'


class LoginDisposeSliding(object):
    """
     登录 并 处理极验验证码
    """

    def __init__(self, username, password):
        self.url = "https://etax.jsgs.gov.cn/sso/login?service=https%3A%2F%2Fetax.jsgs.gov.cn%2Fportal%2Findex.do"
        self.browser = webdriver.Chrome()
        self.wait = WebDriverWait(self.browser, 100)
        self.BORDER = 2
        self.username = username
        self.password = password

    def login_open(self):
        """
        打开浏览器
        :return:
        """
        self.browser.get(self.url)
        # 窗口最大化
        self.browser.maximize_window()
        # 设置显示等待  等待页面 等待  弹窗出现
        # self.wait.until(EC.presence_of_element_located((By.ID, "dia_info")))
        # 关闭弹窗 可能在 页面加载的时候发生异常 进行异常处理。
        try:
            sleep(2)
            # 关闭弹窗。
            self.browser.find_element(By.CLASS_NAME, "xulayer_png32").click()
            print("关闭弹窗成功")
        except Exception as e:
            print(e)
            print("打开页面弹窗发生异常，记录用户名和密码。")
            pass
            return False
        # 找到登录页面的账号 和密码位置   可能页面加载  会发生异常
        try:
            sleep(1)
            # 点击登录按钮
            self.browser.find_element(By.CLASS_NAME, "go_login").click()
            # 等待
            username = self.wait.until(EC.presence_of_element_located((By.ID, "username")))
            username.clear()
            username.send_keys(self.username)
            # 等待
            password = self.wait.until(EC.presence_of_element_located((By.ID, "password")))
            password.clear()
            password.send_keys(self.password)
        except:
            print("登录页面弹窗发生异常，记录用户名和密码。")
            pass
            return False

    def get_images(self, bg_filename='./images/bg.jpg', fullbg_filename='./images/fullbg.jpg'):
        """
        获取验证图片
        :return:
        """
        # 获得背景图片的URL
        bg_url = self.browser.find_element_by_class_name("yidun_bg-img").get_attribute("src")
        # 把资源下载到临时目录
        urlretrieve(url=bg_url, filename=bg_filename)
        # 获取填充页面资源图片的URL
        fill_url = self.browser.find_element_by_class_name("yidun_jigsaw").get_attribute("src")
        # 把资源下载到临时目录
        urlretrieve(url=fill_url, filename=fullbg_filename)

    def get_img_pil(self, filename):
        """
        获取图片   用于  缺口查找
        :param filename: 图片名字
        :return: 图片
        """
        # 创建  img 对象
        img = image.open(filename)
        return img

    def is_pixel_equal(self, img1, img2, x, y):
        """
        判断  图片像素点是否相同。
        :param image1: 图片1
        :param image2: 图片2
        :param x: 位置x
        :param y: 位置y
        :return: 像素是否相同
        """
        # 取两个图片的像素点
        pix1 = img1.load()[x, y]
        print(pix1)
        pix2 = img2.load()[x, y]
        print(pix2)
        threshold = 15
        if (abs(pix1[0] - pix2[0]) < threshold and abs(pix1[1] - pix2[1]) < threshold and abs(
                pix1[2] - pix2[2]) < threshold):
            return True
        else:
            return False

    def get_gap(self, img1, img2):
        """
        获得缺口的偏移量
        :param img1: 不带缺口图片
        :param img2: 带缺口图片
        :return:
        """
        left = 90
        for i in range(left, img1.size[0]):
            for j in range(img1.size[1]):
                if not self.is_pixel_equal(img1, img2, i, j):
                    left = i + 1
                    print(left, "left")
                    return left
        return left

    def get_track(self, distance):
        """
        根据偏移量获取移动轨迹
        :param distance: 偏移量
        :return: 移动轨迹
        """
        # 移动轨迹
        track = []
        # 当前位移
        current = 0
        # 减速阈值
        mid = distance * 0.8
        # 计算间隔
        t = 0.05
        # 初速度
        v = 0
        while current < 1.5 * distance:
            if current < mid:
                # 加速度为正2
                a = 18
            else:
                # 加速度为负3
                a = -6
            # 初速度v0
            v0 = v
            # 当前速度v = v0 + at
            v = v0 + a * t
            # 移动距离x = v0t + 1/2 * a * t^2
            move = v0 * t + 1 / 2 * a * t * t
            # 当前位移
            current += move
            # 加入轨迹
            track.append(round(move))
            print('forword', current, distance)
        v = 0
        while current - distance > 3:
            a = -40
            v0 = v
            v = v0 + a * t
            # 移动距离x = v0t + 1/2 * a * t^2
            move = v0 * t + 1 / 2 * a * t * t
            # 当前位移
            current += move
            # 加入轨迹
            track.append(round(move))
            print('backword', current, distance)
        move = current - distance
        # 加入轨迹
        track.append(round(move))
        return track

    def get_slider(self):
        """
        获取滑块
        :return: 滑块对象
        """
        while True:
            try:
                slider = self.browser.find_element_by_xpath("//div[@class='yidun_slider']")
                break
            except Exception as e:
                print(e)
                sleep(0.5)
        return slider

    def move_to_gap(self, slider, track):
        """
        拖动滑块到缺口处
        :param slider: 滑块
        :param track: 轨迹
        :return:
        """
        ActionChains(self.browser).click_and_hold(slider).perform()
        while track:
            # x = random.choice(track)
            x = track.pop(0)
            ActionChains(self.browser).move_by_offset(xoffset=x, yoffset=0).perform()
            # track.remove(x)
            sleep(0.01)
        sleep(2)
        print('release')
        ActionChains(self.browser).release(slider).perform()
        sleep(2)

    def process_image(self, separation_fullbg_img='./images/fullbg.jpg'):
        """
        处理图片，主要进行二值化，使得缺口形状和方块形状凸显出来，并分别剪裁为两张图片.
        :param captcha_img: 需要处理的图片
        :return:
        """
        img = Image.open(separation_fullbg_img)
        img = img.convert('L')
        bw = img.point(lambda x: 0 if x < 20 else 255, '1')
        for region in [left_region, right_region]:
            crop_img = bw.crop(region)
            file_path = left_image if region[0] == 0 else right_image
            crop_img.save(file_path)

    def match(self, original_image="./images/bg.jpg", search_image="./images/fullbg.jpg"):
        """
        模板匹配，找到缺口位置.
        :return: 缺口位置。
        """
        # 加载原始RGB图像
        img_rgb = cv2.imread(original_image)
        # 创建一个原始图像的灰度版本，所有操作在灰度版本中处理，然后在RGB图像中使用相同坐标还原
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        # 加载将要搜索的图像模板
        template = cv2.imread(search_image, 0)
        # 记录图像模板的尺寸
        w, h = template.shape[::-1]
        print(w, h)
        # 查看三组图像(图像标签名称，文件名称)
        # cv2.imshow('rgb', img_rgb)
        # cv2.imshow('gray', img_gray)
        # cv2.imshow('template', template)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        # 使用matchTemplate在原始图像中查找并匹配图像模板中的内容，并设置阈值。
        # 使用matchTemplate对原始灰度图像和图像模板进行匹配
        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
        # 设定阈值
        threshold = 0.5
        # res大于50%
        loc = np.where(res >= threshold)
        # 匹配完成后在原始图像中使用灰度图像的坐标对原始图像进行标记。
        left_long = []
        for pt in zip(*loc[::-1]):
            cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (7, 249, 151), 2)
            print((pt[0] + w, pt[1] + h))
            left_long.append((pt[0] + w, pt[1] + h))
        # 显示图像
        # cv2.imshow('Detected', img_rgb)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        print(left_long)
        return left_long
        # run = 1
        # res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
        # # 使用二分法查找阈值的精确值
        # L = 0
        # R = 1
        # while run < 20:
        #     run += 1
        #     threshold = (R + L) / 2
        #     if threshold < 0:
        #         print('Error')
        #         return None
        #     loc = np.where(res >= threshold)
        #     if len(loc[1]) > 1:
        #         L += (R - L) / 2
        #     elif len(loc[1]) < 1:
        #         R -= (R - L) / 2
        #     elif len(loc[1]) == 1:
        #         return loc[1][0]

    def run(self):
        # 打开浏览器
        self.login_open()
        # 循环验证。直到  滑块验证码验证成功。
        while True:
            # 保存的图片的位置
            bg_filename = './images/bg.jpg'
            full_filename = './images/fullbg.jpg'
            # 下载图片
            self.get_images(bg_filename=bg_filename, fullbg_filename=full_filename)
            # 获取图片
            bg_img = self.get_img_pil(bg_filename)
            full_img = self.get_img_pil(full_filename)
            # 获取缺口位置 获取 偏移量。
            # self.process_image()
            gap_left = 0
            while True:
                local_list = self.match()
                if len(local_list) == 0:
                    # 再次点击滑块 刷新滑块
                    try:
                        sleep(2)
                        self.browser.find_element_by_class_name("yidun_slider__icon").click()
                        sleep(2)
                        self.browser.find_element_by_class_name("yidun_refresh").click()
                        sleep(2)
                    except:
                        print("滑块页面异常")
                        break
                    break
                if len(local_list) != 0:
                    local_tuple = local_list.pop()
                    gap_left = local_tuple[0] - 60
                    break
            # gap_left = self.get_gap(bg_img, bg_img)
            if gap_left == 0:
                continue
            print('缺口位置', gap_left)
            # 获取滑块
            slider = self.get_slider()
            # 获取滑动轨迹
            track = self.get_track(gap_left)
            # 滑动滑块  拖动滑块到缺口处
            self.move_to_gap(slider, track)
            sleep(1)
            try:
                sleep(4)
                is_value_null = self.browser.find_element_by_xpath('//input[@class="yidun_input"]/@value')
                print(is_value_null)
                print("滑块验证成功。")
                # 点击登录按钮
                sleep(2)
                # self.browser.find_element_by_class_name("btn_submit").click()
                sleep(2)
                break
            except Exception as e:
                print(e)
                # 发生异常说明
                print("滑块验证失败")
                # continue


if __name__ == "__main__":
    crack = LoginDisposeSliding('username', 'passwd')
    crack.run()
