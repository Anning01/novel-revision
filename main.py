#!/usr/bin/python
# -*- coding: UTF-8 -*-
# @author:anning
# @email:anningforchina@gmail.com
# @time:2024/05/01 18:55
# @file:main.py

import os
import time

from openai import OpenAI

client = OpenAI(
    api_key="",
    base_url="",
)

# 设置令牌限制和清空历史记录的阈值
TOKEN_LIMIT = 15000
HISTORY_CLEAR_THRESHOLD = 800

# 记录已使用的令牌数
token_count = 0


prompt = open("prompt.txt", "r", encoding="utf-8").read()

def chat(query, history):
    global token_count

    # 检查令牌是否超出限制
    if token_count >= TOKEN_LIMIT:
        # 如果超出限制，等待一段时间
        time.sleep(3)  # 假设等待一分钟
        # 重置令牌计数器
        token_count = 0
        # 清空历史记录
        history = [{"role": "system", "content": prompt}]

    history += [{
        "role": "user",
        "content": query
    }]

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=history,
        temperature=0.3,
    )
    # 更新令牌计数器
    token_count += completion["total_characters"]

    result = completion.choices[0].message.content

    history += [{
        "role": "assistant",
        "content": result
    }]

    return result


def combine_strings(strings, min_words, max_words):
    combined = []
    current_srt = ""
    for s in strings:
        if min_words <= len(current_srt + s) <= max_words:
            combined.append(current_srt + s + "\n")
            current_srt = ""
        elif len(current_srt) > max_words:
            combined.append(current_srt + "\n")
            current_srt = s
        else:
            current_srt += s
    if current_srt:
        combined.append(current_srt + "\n")
    return combined


def participle(text, min_words, max_words):
    PUNCTUATION = ["，", "。", "！", "？", "；", "：", "”", ",", "!", "…"]

    def clause():
        start = 0
        i = 0
        text_list = []
        while i < len(text):
            if text[i] in PUNCTUATION:
                try:
                    while text[i] in PUNCTUATION:
                        i += 1
                except IndexError:
                    pass
                text_list.append(text[start:i].strip())
                start = i
            i += 1
        return text_list

    text_list = clause()
    result = combine_strings(text_list, min_words, max_words)
    return result

def generate_text(prompt, file_name, min_words, max_words):
    global token_count

    # 分段 使用句号，逗号分段，长度大于100则为一段
    text_list = participle(prompt, min_words, max_words)

    history = [
        {"role": "system", "content": prompt}
    ]
    token_count = 0
    for text in text_list:
        content = chat(text, history)

        # 打开文件以追加模式
        with open(os.path.join(dest_path, file_name), "a", encoding="utf-8") as file:
            # 写入内容
            file.write(content)

if  __name__ == "__main__":
    source_path = "./source"
    dest_path = "./dest"
    min_words = 200
    max_words = 250
    # 查询出source_path下的所有txt文件
    for file_name in os.listdir(source_path):
        if file_name.endswith(".txt"):
            with open(os.path.join(source_path, file_name), "r", encoding="utf-8") as f:
                content = f.read()
            generate_text(content, file_name, min_words, max_words)
            os.remove(os.path.join(source_path, file_name))
