import pdfplumber
import re
import os

import tkinter as tk
from tkinter import filedialog
import shutil
import datetime
from tkinter import font


def re_text(bt, text):
    m1 = re.search(bt, text)
    if m1 is not None:
        return re_block(m1[0])


def re_block(text):
    return text.replace(' ', '').replace('　', '').replace('）', '').replace(')', '').replace('：', ':')


def get_pdf(dir_path):
    pdf_file = []
    for root, sub_dirs, file_names in os.walk(dir_path):
        for name in file_names:
            if name.endswith('.pdf'):
                filepath = os.path.join(root, name)
                pdf_file.append(filepath)
    return pdf_file


def find_key(d, value):
    for k, v in d.items():
        if v == value:
            return k
    return None


def read(file_path, paper_nums):
    try:
        filenames = get_pdf(file_path)  # 修改为自己的文件目录

        invoice_Info = {}
        num1 = []
        for filename in filenames:
            common_prefix, tail = os.path.split(filename)
            old_file_name, file_extension = os.path.splitext(tail)
            if common_prefix == file_path:
                with pdfplumber.open(filename) as pdf:
                    first_page = pdf.pages[0]
                    pdf_text = first_page.extract_text()
                    if '发票' not in pdf_text:
                        text_result.insert(tk.END, f"该文件不是可读的电子发票：{filename}")
                        continue
                    price = re_text(re.compile(r'小写.*(.*[0-9.]+)'), pdf_text)
                    invoice_Info[old_file_name] = str(float(price[3:]))
                    # invoice_Info[str(float(price[3:]))] = old_file_name
                    num1.append(float(price[3:]))
    except:
        text_result.insert(tk.END, "温馨提示，你没有导入电子发票或导入错误，如需请输入后重新求解!\n")
    
    if paper_nums:
        num1.extend(paper_nums)
    else:
        text_result.insert(tk.END, "温馨提示，你没有输入纸质发票的金额或输入的不全是数字，如需请输入后重新求解!\n")

    target = target_input.get()
    if target:
        try:
            target = float(target)
        except:
            text_result.insert(tk.END, "没有正确输入目标金额，笨猪猪!\n")
            return

        subset = [[]]
        for i in range(len(num1)):
            for j in range(len(subset)): 
                subset.append(subset[j]+[num1[i]]) #现有每个子集中添加新元素，作为新子集加入结果集中

        res = len(subset) - 1

        for i in range(len(subset)):
            if sum(subset[i]) >= target:
                text_result.insert(tk.END, f"满足条件的解:{subset[i]}, 与{target}的差值为：{sum(subset[i]) - target}元\n")
                if sum(subset[i]) <= sum(subset[res]):
                    res = i

        if sum(subset[res]) >= target:
            text_result.insert(tk.END, f"最优解为：{subset[res]}, 多出{sum(subset[res]) - target}元\n")
            folder_name = 'out'

            while (os.path.exists(file_path + '/' + folder_name)):
                now = datetime.datetime.now()
                now = str(now).replace(" ", "-").replace(".", "-").replace(":", "-")
                folder_name = 'out' + str(now)
                """
                这是删除out目录下所有文件的代码，但不建议这样做
                # for filename in os.listdir(folder_name):
                #     ex_file_path = os.path.join(folder_name, filename)
                #     try:
                #         if os.path.isfile(ex_file_path) or os.path.islink(ex_file_path):
                #             os.unlink(ex_file_path)
                #         elif os.path.isdir(ex_file_path):
                #             shutil.rmtree(ex_file_path)
                #     except Exception as e:
                #         print('Failed to delete %s. Reason: %s' % (ex_file_path, e))
                """
            if invoice_Info:
                os.makedirs(file_path + '/' + folder_name)

            paper_res = []
            for i in subset[res]:
                if find_key(invoice_Info, str(i)):
                    file_extension = '.pdf'
                    old_filename = find_key(invoice_Info, str(i)) + file_extension
                    new_filename = str(i) + '_' + find_key(invoice_Info, str(i)) + file_extension
                    old_file_path = os.path.join(file_path, old_filename)
                    new_file_path = os.path.join(file_path, folder_name, new_filename)
                    shutil.move(old_file_path, new_file_path)
                    del invoice_Info[find_key(invoice_Info, str(i))]
                else:
                    paper_res.append(i)

            if invoice_Info:
                text_result.insert(tk.END, f"电子发票最优结果的pdf已生成在{file_path+ '/' +folder_name}\n")
            text_result.insert(tk.END, f"需要的纸质发票最优结果为{paper_res}\n")
        else:
            text_result.insert(tk.END, f"发票钱不够, 与{target}最接近的解为{subset[res]}, 还差{target - sum(subset[res])}元\n")
    else:
        text_result.insert(tk.END, "没有输入目标金额，笨猪猪!\n")
    

def on_entry_clicked(event):
    entry.delete(0, tk.END)

def on_target_input_clicked(event):
    target_input.delete(0, tk.END)


def on_paper_invoice_input_clicked(event):
    paper_invoice_input.delete(0, tk.END)


def select_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        entry.delete(0, tk.END)
        entry.insert(0, folder_path)
        text_result.insert(tk.END, "File imported successfully.\n")
    else:
        text_result.insert(tk.END, f"没有输入发票路径，笨猪猪!\n")


def on_button2_click():
    folder_path = entry.get()
    paper_string = paper_invoice_input.get()
    paper_nums = []
    try:
        paper_nums = paper_string.split()
        paper_nums = list(map(float, paper_nums))
    except:
        paper_nums = []
    if os.path.isdir(folder_path) or paper_nums:
        read(folder_path, paper_nums)
    else:
        text_result.insert(tk.END, f"没有正确输入发票路径也没有输入纸质发票的金额，笨猪猪!\n")


def main():
    global entry, target_input, text_result, paper_invoice_input

    root = tk.Tk()
    # 创建字体
    my_font = font.Font(family='宋体', size=15)
    root.title("猪猪小程序3.0")

    entry = tk.Entry(root, width=100, font=my_font)
    entry.insert(0, "可以在这里输入发票所在文件夹(或点击下方导入按钮输入)")
    entry.pack()
    entry.bind("<FocusIn>", on_entry_clicked)

    label1 = tk.Label(root, text="输入目标金额:", font=my_font)
    label1.pack()

    target_input = tk.Entry(root, width=100, font=my_font)
    target_input.insert(0, "输入目标金额:")
    target_input.pack()
    target_input.bind("<FocusIn>", on_target_input_clicked)

    label2 = tk.Label(root, text="输入纸质发票的金额:(中间用空格间隔，可以不用输入)", font=my_font)
    label2.pack()

    paper_invoice_input = tk.Entry(root, width=100, font=my_font)
    paper_invoice_input.insert(0, "输入纸质发票的金额:(中间用空格间隔，可以不用输入)")
    paper_invoice_input.pack()
    paper_invoice_input.bind("<FocusIn>", on_paper_invoice_input_clicked)

    button1 = tk.Button(root, text="导入发票所在文件夹", command=select_folder, height=2, width=20, font=my_font)
    button1.pack()

    button2 = tk.Button(root, text="导出最优解", command=on_button2_click, height=2, width=20, font=my_font)
    button2.pack()

    text_result = tk.Text(root, height=30, width=100, font=my_font)
    text_result.insert(tk.END, f"   这里是猪猪小程序3.0版本，我们根据某女士的使用需求增加了纸质发票的手动输入功能，并增大了字体大小，以提升用户体验，感谢你的使用！！！！！\n\n   该程序会将最优解的那些发票，剪切至out目录下(具体目录请看运行完成后的提示信息)，因此使用前建议将发票提前备份，请谨慎使用哦，亲！\n")
    text_result.pack()

    root.mainloop()

    

if __name__ == "__main__":
    main()

# # 29 17.2 32 29 243 572 272 27.2 152 140 592.8    测试发票金额
