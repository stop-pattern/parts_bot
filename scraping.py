import discord
import requests
from bs4 import BeautifulSoup
import re
from datetime import date
from datetime import timedelta

prevDate = date.today() - timedelta(weeks=1)


def task():
    """
    定期実行する関数
    """
    url = 'http://freight.co.jp/'
    r = requests.get(url)
    r.raise_for_status()

    con = r.text.rstrip()

    obj = ''
    with open('freight.html', 'r', encoding='utf-8') as f:
        obj = f.read()

    if obj == con:
        print('equal')
    else:
        with open("freight.html", "w", encoding='utf-8') as f:
            f.write(con)
        print('!!! neq !!!')
        return True
    return False


def str2date(string: str, prev: date) -> date:
    """
    str2date 'Ｍ月Ｄ日' を入荷日 datetime.date に変換する

    Parameters
    ----------
    string : str
        入荷日
    prev : datetime.date
        年数参照用

    Returns
    -------
    str2date : datetime.date
        datetime.date オブジェクト
    """
    day = int(re.search(r'([0-9０-９]{1,2})日', string).group()[:-1])
    month = int(re.search(r'([0-9０-９]{1,2})月', string).group()[:-1])
    year = prev.year

    if prev < date(prev.year, month, day):
        # 日付の順序関係がおかしかったら1年前にする
        year -= 1

    return date(year, month, day)


prevDate = date.today() - timedelta(days=5)  # (weeks=1)


def html2Embed(arrival: date, arg) -> discord.Embed:
    """
    html2item html の文字列を Embed オブジェクトに変換する

    Parameters
    ----------
    arrival : datetime.date
        入荷日
    arg : obj
        商品情報

    Returns
    -------
    Embed : discord.Embed
        Embed オブジェクト
    """
    num = 'None'
    title = 'Null'
    desc = "Null"
    price = 0
    itemFlag = 0
    for item in arg.find_all('td'):
        text = item.get_text()

        # 品名
        if itemFlag == 1:
            text_split = text.splitlines()
            title = text_split.pop(0)
            if text_split is not None:
                desc = '\n'.join(text_split)
            itemFlag = 2
            continue

        # 金額
        if itemFlag == 2:
            if not re.search(r'[0-9０-９]+.*円', text):
                temp = 0
            temp_n = re.search(r'[0-9０-９]+', text).group()
            unit = text.replace(temp_n, '')
            temp = int(temp_n)
            if '千' in unit:
                unit = unit.replace('千', '')
                temp *= 1000
            if '万' in unit:
                unit = unit.replace('万', '')
                temp *= 10000
            if unit == '円':
                price = temp
            itemFlag = 0
            break

        # 品番
        if re.search(r'^[0-9０-９]{4}－[0-9０-９]{1,3}', text):
            num_up = int(re.search(r'([0-9０-９]{4})－', text).group()[:-1])
            num_down = int(
                re.search(r'－([0-9０-９]{1,3})', text).group()[1:])
            num = str(num_up) + str('-') + str(num_down)
            itemFlag = 1
            continue

        itemFlag = 0

    embed = discord.Embed(title=title, description=desc,
                          colour=discord.Colour.green())
    embed.set_author(
        name="フレイトライナー", url="http://freight.co.jp/", icon_url="https://pbs.twimg.com/profile_images/1119534836606066689/UjS_p5_x_400x400.png")
    embed.set_footer(text='フレイトライナー 更新検知')
    embed.add_field(name='入荷日', value=arrival.isoformat())
    embed.add_field(name='品番', value=num)
    embed.add_field(name='価格', value=price)
    embed.set_image(url="")  # 商品の画像がある場合はその画像

    # ch = bot.bot.get_channel(1020404427766644756)  # noneが帰ってくる
    # ch.send("", embed=embed)

    return embed


def scraping_FL():
    url = 'http://freight.co.jp/newpage43.htm'
    r = requests.get(url)
    r.raise_for_status()
    soup = BeautifulSoup(r.content, 'html.parser')
    # soup = BeautifulSoup(open('おすすめ新着商品・値下げ商品リスト.html',
    #                      encoding='utf-8'), 'html.parser')

    arrival = []
    dayFlag = False
    itemFlag = 0
    firstFlag = True
    newdate = date.today()
    cnt = 0
    # 新着入荷商品
    for elem in soup.select('body > div:nth-child(4) > table > tbody > tr'):
        for data in elem.find_all('td'):
            # continue で次の列
            # break で次の行
            text = data.get_text()

            # --- 凡例行 ---
            # 凡例欄判定
            if re.search(r'.*品.*番$', text):
                dayFlag = True
                continue
            # 入荷日設定
            if dayFlag:
                newdate = str2date(text, newdate)
                if newdate < prevDate:
                    return arrival
                dayFlag = False
                break

            # --- 商品情報 ---
            if re.search(r'[0-9０-９]{4}－[0-9０-９]{1,3}', text):
                arrival.append(html2Embed(newdate, data.parent))
                break
    return arrival


if __name__ == '__main__':
    scraping_FL()
