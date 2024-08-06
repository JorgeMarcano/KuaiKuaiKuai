import random
from Table import Table

class Game():
    def __init__(self):
        self.__table = Table()
        self.__player = -1
        self.__turn = -1

    def connect(self, address, port):
        pass

    def play(self):
        pass















































class Game:
    def __init__(self, isHost=None):
        self.__isHost = isHost if isHost != None else False
        self.__table = T.Table()
        self.__current_player = 0

        if self.__isHost:
            self.__table.new()
            self.__current_player = random.randint(2)

    @staticmethod
    def check_play(action_cards):
        cards = T.Pile.compile_set(action_cards)
        cards = [v for v, _ in cards].sort()

        #TODO: make dict of the cards to be checking

class Pyramid(Drawpile):
    def __init__(self, deck, root, difficulty):
        self.count = 2 - difficulty
        self.root = root
        super().__init__(deck.deck, root)
        self.b = ImageTk.PhotoImage(Image.open("cardset-standard/"+"back192.gif"))
        self.total = 0
        self.score = 0
        self.score_plus(0)
        self.cod = []
        self.__py = []

        self.j = Button(root, command=self.count_joker, image=self.b)
        self.j.image = self.b
        self.joker()
        
        self.d = Button(self.root, command = lambda: self.open_drawing(), image=self.b)
        self.d.image = self.b
        self.d.place(x =140, y=500)
        self.newpy()

    def game_clear(self):
        if self.__py[0][0] == None:
            self.score += self.count * 500
            Reader.the_end(self.root,2,self.score)


    def score_plus(self,plus_score):
        self.score += plus_score
        Label(text = "점수: " + str(self.score),font = ("",20), \
           bg = "Darkgreen", fg = "White").place(x = 525, y = 25)
        

    def count_joker(self):
        self.count-=1
        self.joker()
        return self.doh(self.root)

    def newpy(self):
        self.__py = []
        for i in range(7):
            self.__py.append([])
            for j in range(i+1):
                p = self.get
                if i != 6:
                    self.__py[i].append(Checkbutton(self.root, text = p.value, image=p.cardImage, 
                        selectimage=self.b))
                    self.nn(self.__py,i,j)
                    self.__py[i][j]["state"] = DISABLED
                    self.__py[i][j].select()
                else:
                    self.__py[i].append(Checkbutton(self.root, text = p.value, image=p.cardImage, 
                        selectimage=self.b))
                    self.nn(self.__py,i,j)
                    self.__py[i][j].deselect()
                self.__py[i][j].image = p.cardImage
                self.__py[i][j].selectimage = self.b
        self.__py.append([])
        self.open_drawing()
    
    def _sum(self, i, j):
        self.cod.append((i,j))
        if self.total != 0:
            self.total += int(self.py[i][j]["text"])
            if self.total == 13 or self.total < 0:
                self.total = 0
                for x in self.cod:
                    self.remove(x[0],x[1])
                    self.score_plus(150)
                self.cod = []
                self.isfail()
                self.game_clear()
            else:
                self.total = 0
                for x in self.cod:
                    self.__py[x[0]][x[1]].deselect()  
                self.cod = []
        else:
            self.total += int(self.py[i][j]["text"])
            if self.total == 13:
                self.total = 0
                for x in self.cod:
                    self.score_plus(150)
                    self.remove(x[0],x[1])
                self.cod = []
                self.isfail()
                self.game_clear()   

    def nn(self, ll, i,j):
        ll[i][j]["command"] = lambda: self._sum(i,j)

    def open_drawing(self):
        tmp = self.get
        if tmp != None:
            self.py[7].insert(0,Checkbutton(self.root, text = tmp.value, \
                image=tmp.cardImage, command = lambda: self._sum(7,0) ,selectimage=self.b))
            self.py[7][0].image = tmp.cardImage
            self.py[7][0].deselect()
            self.py[7][0].place(x =250 , y =500)
        self.draw()
        self.isfail()
    
    @property
    def py(self):
        return self.__py

    def open(self):
        for i in range(0,7):
            for j in range(i+1):
                if i != 6  and self.isselect(i, j):
                    self.__py[i][j]["state"] = NORMAL
                    self.__py[i][j].deselect()
        if self.py[7] != []:
            self.__py[7][0]["state"] = NORMAL
                    
    def print_py(self):
        for i in range(7):
            x = (6-i) * 80 / 2
            y = i * 98 / 2
            for j in range(i+1):
                if self.__py[i][j] != None:
                    self.__py[i][j].place(x = x + 80*j + 40, y = 49 + y)
        

    def isselect(self, x, y):
        if 0 <= x <= 7 and 0 <= y <= x and self.py[x][y] != None:
            if x in [6,7]:
                return True
            return self.py[x+1][y] == None and self.py[x+1][y+1] == None
        else:
            return False

    def iscorrect(self, x1, y1, x2, y2):
        if self.__py[x1][y1]["text"] == "0" or self.__py[x2][y2]["text"] == "0":
            return True
        else:
            return int(self.__py[x1][y1]["text"]) + int(self.__py[x2][y2]["text"]) == 13

    # 리팩토링 필요
    def remove(self, x, y):
        self.py[x][y].destroy()
        if x == 7:
            if len(self.py[7]) == 1:
                self.open_drawing()
                self.__py[7] = self.__py[7][:1]
            else:
                self.py[7] = self.__py[7][1:]
        else:
            self.__py[x][y] = None
        self.open()
        self.print_py()

    def draw(self):
        if self.pile != []:
            self.d.place(x =140, y=500)
        Label(text =str(len(self.pile)).center(4),font = ("",15), \
          bg = "Darkgreen", fg = "White").place(x = 100, y = 580)


    def joker(self):
        if self.count <= 0:
            self.j.destroy()
        else:
            self.j.place(x =420, y=500)
        Label(text =str(self.count),font = ("",15), \
            bg = "Darkgreen", fg = "White").place(x = 510, y = 580)

    def isfail(self):
        open_card_list = []
        if self.py[7] != []:
            open_card_list = [self.py[7][0]]
        check_list = []
        if self.count == 0 and self.pile == []:
            pyramid_card = []
            for i in range(7):
                pyramid_card.append(self.py[i])  
            for i in pyramid_card:
                for j in i:
                    if j != None and j["state"] == NORMAL :
                        open_card_list.append(j)
            for i in open_card_list :
                if int(i["text"]) == 13 :
                    return False
                for j in open_card_list :
                    check_list.append(int(i["text"]) + int(j["text"]))
            if 13 in check_list :
                return False
            else :
                Reader.the_end(self.root,1,self.score)
        else:
            return False

class PyramidController():
    def __init__(self, difficulty, root):
        """
        컨트롤러가 하는일이 없음...... 이것도 리팩토링 대상
        """
        self.root = root
        self.difficulty = difficulty
        self.canvas = Canvas(root, width=100, height=100, bg='DarkGreen', \
            bd=0, highlightthickness=0, relief='ridge')
        self.canvas.grid()
        self.nowhour = int(time.strftime('%H'))
        self.nowminate = int(time.strftime('%M'))
        self.nowsecond = int(time.strftime('%S'))
        self.Pyramid = Pyramid(Deck(), root, self.difficulty)
        self.animate()
        self.Pyramid.print_py()

    def animate(self):
        self.canvas.delete(ALL)
        timer = 120 - ((int(time.strftime('%H')) * 3600 + int(time.strftime('%M')) * \
            60 + int(time.strftime('%S'))) - (self.nowhour * 3600 + self.nowminate * 60 + self.nowsecond))
        
        if timer == 0:
            Reader.the_end(self.root,0,self.Pyramid.score)
        else:
            self.canvas.after(10, self.animate)
            if timer > 50:
                self.canvas.create_text(50, 40,text=timer,font = ("",20),fill="White")
            elif timer > 10:
                self.canvas.create_text(50, 40,text=timer,font = ("",20),fill="Yellow")
            else:
                self.canvas.create_text(50, 40,text=timer,font = ("",20),fill="Red")

class Reader:
    @staticmethod
    def difficulty_widgets(root):
        frame = Frame(root)
        Label(frame, text ='난이도',font = ("",15)).grid(row=0,column=1,pady=6, sticky=S)
        difficulty = IntVar()
        b1=Radiobutton(frame, text=' 쉬움',
            variable = difficulty, value = 0).grid(row = 1, column = 0, padx = 10, pady = 3)
        b2=Radiobutton(frame, text=' 보통',
            variable = difficulty, value = 1).grid(row = 1, column = 1, padx = 10)
        b3=Radiobutton(frame, text='어려움',
            variable = difficulty, value = 2).grid(row = 1, column = 2, padx = 10)
        Button(frame, text="게임 시작",command = lambda : Reader.closed(root, frame, difficulty.get())
            ).grid(row=2, column=1, pady=3)
        frame.pack(pady=270)

    @staticmethod
    def the_end(root,n,total_score):
        frame = Frame(root)
        if n == 0:
            Label(frame, text="시간 초과!").grid(row=0,column=1,padx=50,pady=3)
            Label(frame, text="당신의 점수는 " + str(total_score) + "점 입니다.") \
               .grid(row=1,column=1,padx=50,pady=3)
        if n == 1:
            Label(frame, text="더 이상 합이 13이 되는 카드가 없습니다.").grid(row=0,column=1,padx=50,pady=3)
            Label(frame, text="당신의 점수는 " + str(total_score) + "점 입니다.") \
               .grid(row=1,column=1,padx=50,pady=3)
        if n == 2:
            Label(frame, text="클리어!").grid(row=0,column=1,padx=50,pady=3)
            Label(frame, text="당신의 점수는 " + str(total_score) + "점 입니다.") \
               .grid(row=1,column=1,padx=50,pady=3)
        Button(frame, command = quit, text="OK!").grid(row=2, column=1,padx=10,pady=3)
        frame.pack(pady=280)

    @staticmethod
    def closed(root, frame, num):
        frame.pack_forget()
        PyramidController(num, root)

    @staticmethod
    def score(root,total_score):
        frame = Frame(root)
        Label(frame, text="당신의 점수는 " + str(total_score) + "점 입니다.").grid(row=0,column=1,padx=50,pady=3)
        Button(frame, command = quit, text="OK!").grid(row=1, column=1,padx=10,pady=3)
        frame.pack(pady=280)


def main():
    root = Tk()
    root.title("Pyramid Solitaire")
    root.geometry("650x650")
    root.configure(bg='darkgreen')
    Reader.difficulty_widgets(root)
    root.mainloop()

main()
