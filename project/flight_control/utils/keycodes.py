"""
这个是用来在tkinter编程时输出按键对应的keycode和char等信息的，
如果不使用tkinter就没啥用
"""

if __name__ == '__main__':
    import sys

    if sys.version_info.major >= 3:
        from tkinter import *
    else:
        from Tkinter import *

    root = Tk()
    root.title("Get Key")
    root.geometry("600x600+200+20")

    label = Label(root)
    label.focus_set()
    label.pack()


    def func(event):
        print()
        print("event.char =", event.char)
        print("event.keycode =", event.keycode)
        print(event)
        print(type(event))


    # <Key> 响应所有的按键，但是不响应Mac的触控板输入
    label.bind("<Key>", func)
    root.mainloop()
