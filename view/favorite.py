
# 유저의 관심종목 불러오기
@app.route("/user/stock/get", methods=["GET"])
def user_stock_get():
    stock_list = list(db.user_stock.find({}, {'_id': False}))

    result = []
    for stock in stock_list:
        url = 'https://finance.naver.com/'
        url += 'item/main.naver?code=' + stock['stock_code']
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
        data = requests.get(url, headers=headers)
        soup = BeautifulSoup(data.text, 'html.parser')

        close = soup.select_one("#chart_area > div.rate_info > div > p.no_today > em > span.blind").text

        temp_doc = {
            'stock_name': stock['stock_name'],
            'stock_code': stock['stock_code'],
            'buy_price': stock['buy_price'],
            'close': close,
            'date_delta': str(datetime.datetime.now() - stock['buy_date'])[:1]
        }
        result.append(temp_doc)

    return jsonify({'result': result})

# 유저의 관심종목 등록
@app.route("/user/stock/post", methods=["POST"])
def user_stock_post():
    code_receive = request.form['code_give']
    buy_price_receive = request.form['buy_price_give']
    buy_date_receive = request.form['buy_date_give']
    url = 'https://finance.naver.com/'
    url += 'item/main.naver?code=' + code_receive
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url, headers=headers)

    soup = BeautifulSoup(data.text, 'html.parser')

    stock_name = soup.select_one('#middle > div.h_company > div.wrap_company > h2 > a').text
    # close = soup.select_one("#chart_area > div.rate_info > div > p.no_today > em > span.blind").text

    a = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    doc = {
        'stock_name': stock_name,
        'stock_code': code_receive,
        'buy_price': buy_price_receive,
        'buy_date': datetime.datetime.strptime(buy_date_receive, "%Y-%m-%d")
    }
    db.user_stock.insert_one(doc)

    return jsonify({'msg': '저장 완료!'})

