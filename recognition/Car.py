import cv2
import numpy as np
import sys
from shapely.geometry import LineString
from .Messages import Messages


class CarOpenCV:
    @staticmethod
    def videoCapture():
        cap = cv2.VideoCapture(0)
        ret, img = cap.read()
        while not ret:
            ret, img = cap.read()
        return img

    @staticmethod
    def edgeDetecion(img):
        imgGauss = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(50,50))
        imgGauss = clahe.apply(imgGauss)
        imgGauss = cv2.GaussianBlur(imgGauss, (15, 15), 0)
        ret, thresh = cv2.threshold(imgGauss, 127, 255, cv2.THRESH_BINARY)
        edges = cv2.Canny(thresh, 100, 300)
        rawLines = cv2.HoughLinesP(edges, 1, np.pi / 180, 20, np.array([]), 100, 20)
        return rawLines

    @staticmethod
    def calculateAngles(rawLines):
        angles = []
        if not rawLines:
            print("No lines detected.")
        else:
            for rawLine in rawLines:
                x1, y1, x2, y2 = rawLine[0]
                angle = np.arctan2(y1-y2,x1-x2)*180/np.pi
                if np.abs(angle) > 10 and np.abs(angle) < 170:
                    angles.append([angle,rawLine[0]])
        return angles

    @staticmethod
    def groupAngles(angles):
        lines = []
        linesSize = 1
        groupSize = 1
        angles.sort(key=CarOpenCV.sortFirst)
        med = 0
        for angle in angles:
            if len(lines) == 0:
                lines.append([angle[1]])
                med = angle[0]
                continue
            if np.abs(angle[0] - med) <= 5:
                lines[linesSize - 1].append(angle[1])
                groupSize = groupSize + 1
                med = (med + angle[0]) / 2
            else:
                lines.append([angle[1]])
                linesSize = linesSize + 1
                groupSize = 1
                med = angle[0]
        angles.clear()
        return lines

    @staticmethod
    def joinLines(lines):
        newLines = []
        for line in lines:
            minX = sys.maxsize
            maxX = -1
            minY = sys.maxsize
            maxY = -1
            for l in line:
                x1, y1, x2, y2 = l
                if x1 < minX:
                    minX = x1
                    minY = y1
                if x2 < minX:
                    minX = x2
                    minY = y2
                if x1 > maxX:
                    maxX = x1
                    maxY = y1
                if x2 > maxX:
                    maxX = x2
                    maxY = y2
            newLines.append([minX,minY,maxX,maxY])
        lines.clear()
        return newLines

    @staticmethod
    def findIntersection(newLines,img,angles):
        height, width, channels = img.shape
        shapeGreenLine = LineString([(0, height / 2), (width, height / 2)])
        for line in newLines:
            x1, y1, x2, y2 = line
            cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 50)
            shapelyLine = LineString([(x1, y1), (x2, y2)])
            interSec = shapeGreenLine.intersection(shapelyLine)
            angle = np.arctan2(y1 - y2, x1 - x2)*180/np.pi
            if not interSec.is_empty:
                lineLen = np.sqrt((x1-x2)*(x1-x2)+(y1-y2)*(y1-y2))
                if x1 < width/2:
                    direction = "LEFT"
                else:
                    direction = "RIGHT"
                if lineLen > 100:
                    angles.append([angle, lineLen, direction])
                    cv2.line(img,(x1,y1),(x2,y2),(255,0,0),50)
        cv2.line(img, (0, int(height / 2)), (int(width), int(height/2)), (0, 255, 0), 50)
        return None

    @staticmethod
    def calculatePosition(angles):
        sum = 0
        it = 0
        if angles.count() > 2:
            return Messages.SIGNAL_NOISE
        for a in angles:
            if a[0] < 0:
                angles[it][0] = a[0] + 180
            if a[0] > 90:
                angles[it][0] = 180 - a[0]
            angles[it][0] = 90 - angles[it][0]
            sum = sum + angles[it][0]
            it = it + 1
        it = 0
        for a in angles:
            angles[it][0] = angles[it][0] / sum * 100
            it = it + 1
        if angles[0][0] > angles[1][0]:
            return Messages.TURN_LEFT
        else:
            return Messages.TURN_RIGHT

    @staticmethod
    def driving():
        #preparing data
        img = CarOpenCV.videoCapture()
        rawLines = CarOpenCV.edgeDetecion(img)
        angles = CarOpenCV.calculateAngles(rawLines)
        lines = CarOpenCV.groupAngles(angles)
        newLines = CarOpenCV.joinLines(lines)
        CarOpenCV.findIntersection(newLines,img,angles)
        return CarOpenCV.calculatePosition(angles)

    @staticmethod
    def parking():
        img = CarOpenCV.videoCapture()
        lines = CarOpenCV.edgeDetecion(img)
        height, width, channels = img.shape
        shapeGreenLine = LineString([(width/2,height/2),(width/2,height)])
        angles = []
        if not lines:
            print("No lines detected")
        else:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                angle = np.arctan2(y1 - y2, x1 - x2) * 180 / np.pi
                if 10 < np.abs(angle) < 160:
                    continue
                cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 10)
                shapelyLine = LineString([(x1, y1), (x2, y2)])
                interSec = shapeGreenLine.intersection(shapelyLine)
                if not interSec.is_empty:
                    angles.append(angle)
        cv2.line(img, (int(width/2),int(height/2)), (int(width/2),int(height)), (0, 255, 0), 15)
        print(angles)
        for a in angles:
            if np.abs(a) < 5 or np.abs(a) > 178:
                return Messages.STOP_TURNING
        return Messages.CONTINUE_TURNING

    @staticmethod
    def sortFirst(val):
        return val[0]
