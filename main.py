from tkinter import *
from enetedu.downHtml import *
import tkinter as tk
import _thread

window = Tk()


def flush(event):
    pi = tk.PhotoImage(file=downImg())
    imgLabel.image = pi
    imgLabel.configure(image=pi)
    imgLabel.update()


def sub(event):
    # text.delete(0, END)
    text.insert(END, '用户名:{}\n'.format(userName.get()))
    resp = login(userName.get(), password.get(), vaild.get())
    _thread.start_new_thread(study, (resp, text))


userName = tk.Entry(window)
userName.pack()
userName.focus()

password = tk.Entry(window)
password.pack()

vaild = tk.Entry(window)
vaild.pack()

img = tk.PhotoImage(file=downImg())
imgLabel = tk.Label(window, image=img)
imgLabel.pack()
imgLabel.bind("<Button-1>", flush)

submit = tk.Button(window, text="提交")
submit.pack()
submit.bind("<Button-1>", sub)

text = tk.Text(window, height=10)
text.pack()

if __name__ == '__main__':
    window.geometry('500x300')
    window.title("tk")
    window.mainloop()

# id_number=130531199208160022&idd=&pwd=160022&code=3259
