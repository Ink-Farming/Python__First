file_name = input("请输入文件名：")
old_word = input("请输入需要替换的单词或字符：")
new_word = input("请输入新的单词或字符：")

f = open(file_name, 'r', encoding='utf-8')
content = f.read()
f.close()

count = content.count(old_word)
print(f"文件 {file_name} 中共有{count}个【{old_word}】")

confirm = input(f"您确定要把所有的【{old_word}】替换为【{new_word}】吗？【YES/NO】: ")

if confirm.lower() == 'yes':
    new_content = content.replace(old_word, new_word)
    f = open(file_name, 'w', encoding='utf-8')
    f.write(new_content)
    f.close()
    print("替换成功！")
else:
    print("已取消替换。")
