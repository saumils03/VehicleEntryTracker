import tkinter as tk
import os
import cv2 as cv
from PIL import Image, ImageTk
import imutils
from pymysql import*
import xlwt
import pandas.io.sql as sql
import mysql.connector
import numpy as np 
import pytesseract as pyt

window = tk.Tk()
menubar = tk.Menu(window)
file_menu = tk.Menu(menubar, tearoff = 0)
file_menu.add_command(label = "Read Database")
file_menu.add_command(label = "Help")
file_menu.add_command(label = "Start")
file_menu.add_command(label="Exit", command= window.quit)  

edit_menu = tk.Menu(menubar, tearoff = 0)

menubar.add_cascade(label="File", menu=file_menu)  
menubar.add_cascade(label="Edit", menu=edit_menu)
window.config(menu = menubar)

load = cv.imread("C:\\Users\Saumil\Downloads\photocar.png")
load = cv.resize(load, (800, 600)) 
load = cv.cvtColor(load, cv.COLOR_BGR2RGBA)
load = Image.fromarray(load)
photo = ImageTk.PhotoImage(load)

video_label = tk.Label(window, image = photo, height = 600, width = 800)
video_label.pack(side = tk.LEFT, padx = 2, pady = 2, expand = 0)

text_label = tk.Label(window, text = "Current Vehicle Number: ",font=("Times New Roman", 14), justify = tk.LEFT)
text_label.pack(padx = 2, pady = 2)

vehicle_number_text = tk.Label(window, text = "WB 06 G 8224", font=("Century", 12), relief = "raised")
vehicle_number_text.pack(padx = 2 , pady = 20)

video_input = cv.VideoCapture('C:\\Users\Saumil\Downloads\Saumil_approvedvehicle.mp4')

def start_video():
    isPlaying = True
    check, frame = video_input.read()
    img = frame.copy()
    frame = cv.resize(frame, (800, 600))
    frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
    findPlate = PlateFinder()

    possible_plates = findPlate.find_possible_plates(img) 

    if possible_plates is not None: 

        for i, p in enumerate(possible_plates): 
            hsv_image = cv.cvtColor(p, cv.COLOR_BGR2HSV)

            white_lower = np.array([0,0,0], np.uint8) 
            white_upper = np.array([0,0,255], np.uint8) 
            white_mask = cv.inRange(hsv_image, white_lower, white_upper) 

            kernel = np.ones((5,5), "uint8")
            white_mask = cv.dilate(white_mask, kernel) 
            res_white = cv.bitwise_and(p, p, 
                                        mask = white_mask) 

            white_contours, hierarchy = cv.findContours(white_mask, 
                                                    cv.RETR_TREE, 
                                                    cv.CHAIN_APPROX_SIMPLE) 


            black_lower = np.array([0,0,0], np.uint8) 
            black_upper = np.array([180,255,0], np.uint8) 
            black_mask = cv.inRange(hsv_image, black_lower, black_upper) 

            kernel = np.ones((5,5), "uint8")
            black_mask = cv.dilate(black_mask, kernel) 
            res_black = cv.bitwise_and(p, p, 
                                        mask = black_mask) 

            black_contours, hierarchy = cv.findContours(black_mask, 
                                                    cv.RETR_TREE, 
                                                    cv.CHAIN_APPROX_SIMPLE) 
            if white_contours is not None and black_contours is not None:
                predicted_result = pyt.image_to_string(p, lang ='eng') 
                filter_predicted_result = "".join(predicted_result.split()).replace(":", "").replace("-", "").replace('"', "").replace('“', '')
                db = Database()
                db_output = db.exec(filter_predicted_result)
                video_input.release()
                vehicle_number_text.text = db_output
                vehicle_number_text.config(text = db_output)
                isPlaying = False 

    frame = Image.fromarray(frame)
    frame = ImageTk.PhotoImage(frame)
    video_label.image = frame
    video_label.config(image = frame)
    if isPlaying:
        video_label.after(10, start_video)

play_btn = tk.Button(window, bg = "red", fg = "white", width = 20, height = 2, text = "Play", command = start_video)
play_btn.pack(side = tk.BOTTOM, padx = 2, pady = 10)

class Database:
    def __init__(self):
        self.mydb = mysql.connector.connect(
            host = "localhost",
            user = "root",
            passwd = "password123",
            database = "approved_vehicles",
            )

        self.my_cursor = self.mydb.cursor()

        self.records = [('Kamala Rajan', 'UP24AX8793'),
            ('Karanjit Aulakh', 'PB44ES1234'),
            ('Suyash Matanhelia', 'UP32HD6262'),
            ('Aruna Ganguly', 'UP24HF8234'),
            ('Saumil Sood', 'HR20AB8008'),
            ('Arishmit Ghosh', 'WB06G8224'),
            ('Tanmay Singh', 'TN14AS3127'),
            ('Siddhant Nigam', 'KA03MX5058'),
            ('Farhan Ahmed', 'UP24AB2244'),
            ('Anthony Smith', 'UP24CZ1678')
        ]
        self.con=connect(user="root",password="password123",host="localhost",database="approved_vehicles")
        self.df=sql.read_sql('select * from approved_vehicles', self.con)

    def exec(self, num):
        self.my_cursor.execute("SELECT * FROM approved_vehicles")
        result = self.my_cursor.fetchall()
        for tup in result:
            if tup[1] == num:
                return("The vehicle is already a registered approved vehicle and belongs to {}".format(tup[0]))
        return ('No vehicle found')
    mydb1 = mysql.connector.connect(
        host = "localhost",
        user = "root",
        passwd = "password123",
        )
    my_cursor1 = mydb1.cursor()

    #my_cursor1.execute("CREATE DATABASE unapproved_vehicles")
    #my_cursor1.execute("CREATE TABLE unapproved_vehicles (License_plate_num VARCHAR(255))")

    #table_info = "INSERT INTO unapproved_vehicles (License_plate_num) VALUES (%s)"

pyt.pytesseract.tesseract_cmd = r'C://Program Files/Tesseract-OCR/tesseract'
class PlateFinder: 
    def __init__(self): 
        self.min_area = 27000
        self.max_area = 28000
        self.element_structure = cv.getStructuringElement( 
                              shape = cv.MORPH_RECT, ksize =(22, 3)) 
  
    def preprocess(self, input_img):   
        imgBlurred = cv.GaussianBlur(input_img, (7, 7), 0) 
        gray = cv.cvtColor(imgBlurred, cv.COLOR_BGR2GRAY)  
        sobelx = cv.Sobel(gray, cv.CV_8U, 1, 0, ksize = 3)
        ret2, threshold_img = cv.threshold(sobelx, 0, 255, 
                         cv.THRESH_BINARY + cv.THRESH_OTSU)  
        element = self.element_structure 
        morph_n_thresholded_img = threshold_img.copy() 
        cv.morphologyEx(src = threshold_img,  
                         op = cv.MORPH_CLOSE, 
                         kernel = element, 
                         dst = morph_n_thresholded_img) 
        return morph_n_thresholded_img 
  
    def extract_contours(self, after_preprocess): 
          
        contours, _ = cv.findContours(after_preprocess,  
                                          mode = cv.RETR_EXTERNAL, 
                                          method = cv.CHAIN_APPROX_NONE) 
        return contours 
  
    def clean_plate(self, plate): 
          
        gray = cv.cvtColor(plate, cv.COLOR_BGR2GRAY) 
        thresh = cv.adaptiveThreshold(gray, 
                                       255,  
                                       cv.ADAPTIVE_THRESH_GAUSSIAN_C,  
                                       cv.THRESH_BINARY, 
                                       11, 2) 
          
        contours, _ = cv.findContours(thresh.copy(),  
                                          cv.RETR_EXTERNAL, 
                                          cv.CHAIN_APPROX_NONE) 
  
        if contours: 
            areas = [cv.contourArea(c) for c in contours]
            max_index = np.argmax(areas)   
            max_cnt = contours[max_index] 
            max_cntArea = areas[max_index] 
            x, y, w, h = cv.boundingRect(max_cnt) 
            rect = cv.minAreaRect(max_cnt)  
            if not self.ratioCheck(max_cntArea, plate.shape[1],  
                                                plate.shape[0]): 
                return plate, None   
            return plate, [x, y, w, h]      
        else: 
            return plate, None
  
  
  
    def check_plate(self, input_img, contour): 
          
        min_rect = cv.minAreaRect(contour) 
          
        if self.validateRatio(min_rect): 
            x, y, w, h = cv.boundingRect(contour) 
            after_validation_img = input_img[y:y + h, x:x + w] 
            after_clean_plate_img, coordinates = self.clean_plate( 
                                                        after_validation_img)         
            return after_clean_plate_img, coordinates          
        return None, None
  
  
    def find_possible_plates(self, input_img): 
        plates = [] 
        self.char_on_plate = [] 
        self.corresponding_area = [] 
        self.after_preprocess = self.preprocess(input_img) 
        possible_plate_contours = self.extract_contours(self.after_preprocess) 
        for cnts in possible_plate_contours: 
            plate, coordinates = self.check_plate(input_img, cnts)         
            if plate is not None: 
                plates.append(plate) 
                self.corresponding_area.append(coordinates) 
        if (len(plates) > 0): 
            return plates  
        else: 
            return None
  
    def ratioCheck(self, area, width, height):    
        min = self.min_area 
        max = self.max_area 
        ratioMin = 3
        ratioMax = 6
        ratio = float(width) / float(height)      
        if ratio < 1: 
            ratio = 1 / ratio       
        if (area < min or area > max) or (ratio < ratioMin or ratio > ratioMax): 
            return False   
        return True
  
    def preRatioCheck(self, area, width, height):        
        min = self.min_area 
        max = self.max_area 
        ratioMin = 2.5
        ratioMax = 7
        ratio = float(width) / float(height)        
        if ratio < 1: 
            ratio = 1 / ratio 
        if (area < min or area > max) or (ratio < ratioMin or ratio > ratioMax): 
            return False   
        return True
  
    def validateRatio(self, rect): 
        (x, y), (width, height), rect_angle = rect 
        if (width > height): 
            angle = -rect_angle 
        else: 
            angle = 90 + rect_angle 
        if angle > 15: 
            return False   
        if (height == 0 or width == 0): 
            return False
        area = width * height      
        if not self.preRatioCheck(area, width, height): 
            return False
        else: 
            return True
            
window.geometry("1920x1080")
window.mainloop()
