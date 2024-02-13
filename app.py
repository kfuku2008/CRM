from flask import render_template,request
from models import app,db,Customer,Item,Purchase,Purchase_detail
import sqlalchemy
from datetime import datetime
from sqlalchemy import func

#ページ遷移
#トップページ兼顧客管理
@app.route("/")
def index():
    customers = Customer.query.all()
    return render_template("1_index.html",customers=customers)

#商品ページ
@app.route("/item")
def item():
    items = Item.query.all()
    return render_template("2_item.html",items=items)

#購入情報登録ページ
@app.route("/purchase")
def purchase():
    customers = Customer.query.all()
    items = Item.query.all()
    return render_template("3_purchase.html",customers=customers,items=items)


#機能系
#1-1.顧客登録
@app.route("/add_customer",methods=["POST"])
def add_customer():
    customer_id = request.form["input-customer-id"]
    customer_name = request.form["input-customer-name"]
    age = request.form["input-age"]
    gender = request.form["input-gender"]
    customer = Customer(customer_id,customer_name,age,gender)
    try:
        db.session.add(customer)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        return render_template("error.html")
    return render_template("1-1_confirm_added_customer.html",customer=customer)

#1-2.性別で抽出
@app.route("/select_gender",methods=["POST"])
def select_gender():
    gender = request.form["input-gender2"]
    customers = Customer.query.filter(Customer.gender==gender).all()
    return render_template("1-2_result_select_gender.html",customers=customers)

#2-1.商品登録
@app.route("/add_item",methods=["POST"])
def add_item():
    item_id = request.form["input-item-id"]
    item_name = request.form["input-item-name"]
    price = request.form["input-price"]
    item = Item(item_id,item_name,price)
    try:
        db.session.add(item)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        return render_template("error.html")
    return render_template("2-1_confirm_added_item.html",item=item)

#2-2.商品削除
@app.route("/delete_item",methods=["POST"])
def delete_item():
    item_id = request.form["input-item-id"]
    item = Item.query.filter_by(item_id=item_id).first()
    try:
        db.session.delete(item)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        return render_template("error.html")
    return render_template("2-2_confirm_deleted_item.html",item=item)


#2-3.商品更新
@app.route("/update_item",methods=["POST"])
def update_item():
    item_id = request.form["input-item-id"]
    updated_item_name = request.form["input-item-name"]
    updated_price = request.form["input-item-price"]
    item = Item.query.filter_by(item_id=item_id).first()
    try:
        item.item_name = updated_item_name
        item.price = updated_price
        db.session.add(item)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        return render_template("error.html")
    return render_template("2-3_confirm_updated_item.html",item=item)

#2-4.商品名で抽出
@app.route("/select_item_name",methods=["POST"])
def select_item_name():
    item_name = request.form["input-item-name"]
    select_target = "%{}%".format(item_name)
    items = Item.query.filter(Item.item_name.like(select_target)).all()
    result_type = "抽出"
    return render_template("2-4_result_items.html",items=items,result_type=result_type)

#2-5.単価で並び替え
@app.route("/sorting_item",methods=["POST"])
def sorting_item():
    order_type = request.form["order-type"]
    if order_type == "ascending":
        items = Item.query.order_by(Item.price)
    else:
        items = Item.query.order_by(Item.price.desc())
    result_type = "並び替え"
    return render_template("2-4_result_items.html",items=items,result_type=result_type)

#3-1.購入情報登録(DBに登録する処理)
@app.route("/add_purchase",methods=["POST"])
def add_purchase():
    #リクエストで入力情報を持ってくる
    customer_name = request.form["input-customer-name"]
    item_name1 = request.form["input-item-name1"]
    quantity1 = request.form["input-quantity1"]
    item_name2 = request.form["input-item-name2"]
    quantity2 = request.form["input-quantity2"]
    date = request.form["input-date"]#このままだとstr
    date = datetime.strptime(date,"%Y-%m-%d")

    #Customerテーブルに対して入力した顧客名情報を抽出させる
    customer = Customer.query.filter_by(customer_name=customer_name).first()#ブラウザで入力した名前のインスタンスができあがる

    #Purchaseテーブルに対して↑で抽出した顧客名情報の内、顧客IDとリクエストの日付を格納した変数を作成
    purchase = Purchase(customer.customer_id,date)

    #作成した変数を格納
    try:
        db.session.add(purchase)
        db.session.commit()

    except sqlalchemy.exc.IntegrityError:
        return render_template("error.html")
    
    #purchase_detailテーブルはpurchaseテーブルと同様に購入が発生すれば必ず記入イベントが発生するものなので★同時に作ることで整合を確保

    #itemテーブルからリクエストで持ってきたitem1の情報を抽出
    item1 = Item.query.filter_by(item_name=item_name1).first()

    #purchase_detailテーブルからpurchase.purchase_id(対象の顧客で抽出したpurchase_id)かつitemテーブルから抽出したitem_idとリクエストで取得したquantity1を変数に格納
    purchase_detail = Purchase_detail(purchase.purchase_id,item1.item_id,quantity1)#★purchase_detailに複合キーが必要である事を思い出す

    #変数をdbに格納
    try:
        db.session.add(purchase_detail)
        db.session.commit()

    except sqlalchemy.exc.IntegrityError:
        return render_template("error.html")

    #２つ目はない可能性があるのでif文で処理
    if item_name2:

        item2 = Item.query.filter_by(item_name=item_name2).first()
        purchase_detail = Purchase_detail(purchase.purchase_id,item2.item_id,quantity2)#purchase_detailに複合キーが必要である事を思い出す

        try:
            db.session.add(purchase_detail)
            db.session.commit()

        except sqlalchemy.exc.IntegrityError:
            return render_template("error.html")       


    return render_template("3-1_confirm_purchase.html",purchase=purchase)

#3-2.購入情報削除
@app.route("/delete_purchase",methods=["POST"])
def delete_purchase():
    purchase_id = request.form["input-purchase-id"]
    purchase = Purchase.query.filter_by(purchase_id=purchase_id).first()
    try:
        db.session.delete(purchase)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        return render_template("error.html")
    return render_template("3-2_confirm_deleted_purchase.html",purchase=purchase)
#★models.pyのcascade=deleteのお陰で複数テーブル連動で消えている

#4.購入情報検索/分析ページ
@app.route("/purchase_data_statistics")
def purchase_data_statistics():
    #joinしたいクラス名を記述していく(今回はインナージョインの例)→db.session.query(クラス1,クラス2).join(クラス2,クラス1.key1==クラス2.key2).all()
    #3以上テーブル結合の場合はdb.session.query(クラス1,クラス2,クラス3,クラス4).join(クラス2,クラス1.key1==クラス2.key2).join(...).join(...).all()
    joined_purchase_details = db.session.query(Purchase,Purchase_detail).join(Purchase_detail,Purchase.purchase_id==Purchase_detail.purchase_id).all()
    joined_purchase_details = db.session.query(Purchase,Purchase_detail,Customer).join(Purchase_detail,Purchase.purchase_id==Purchase_detail.purchase_id).join(Customer,Purchase.customer_id==Customer.customer_id).all()
    joined_purchase_details = db.session.query(Purchase,Purchase_detail,Customer,Item).join(Purchase_detail,Purchase.purchase_id==Purchase_detail.purchase_id).join(Customer,Purchase.customer_id==Customer.customer_id).join(Item,Purchase_detail.item_id==Item.item_id).all()
    customers = Customer.query.all()
    #引数として何を渡せばいいかを考える。人が視覚的に見やすくDBでも実現可能な第一正規化位の表をイメージする
    return render_template("4_purchase_data_statistics.html",joined_parchase_details=joined_purchase_details,customers=customers)

#4-1購入情報検索
@app.route("/search_purchase",methods=["POST"])
def search_purchase():
    item_name = request.form["input-item-name"]
    customer_name = request.form["input-customer-name"]
    date = request.form["input-date"]

    if item_name:
        search_target = "%{}%".format(item_name)
        items = Item.query.filter(Item.item_name.like(search_target)).all()
        # item_id_list = []
        # for item in items:
        #     item_id_list.append(item.item_id)
        item_id_list = [item.item_id for item in items]
    if customer_name:
        customer = Customer.query.filter_by(customer_name=customer_name).first()
        customer_id = customer.customer_id
    else:
        customer = None
    if date:
        date = datetime.strptime(date,"%Y-%m-%d")

    is_customer_or_date = True
    if customer and date:
        purchases = Purchase.query.filter(Purchase.customer_id==customer_id,Purchase.date==date).all()
    elif customer:
        purchases = Purchase.query.filter(Purchase.customer_id==customer_id).all()
    elif date:
        purchases = Purchase.query.filter(Purchase.date==date).all()
    else:
        is_customer_or_date = False

    if is_customer_or_date:
        # purchase_id_list = []
        # for purchase in purchases:
        #     purchase_id_list.append(purchase.purchase_id)
        purchase_id_list = [purchase.purchase_id for purchase in purchases]

    if is_customer_or_date and item_name:
        purchase_details = Purchase_detail.query.filter(Purchase_detail.item_id.in_(item_id_list),Purchase_detail.purchase_id.in_(purchase_id_list)).all()
        return render_template("4-1_result_search_purchase.html",purchase_details=purchase_details)
    elif is_customer_or_date:
        purchase_details = Purchase_detail.query.filter(Purchase_detail.purchase_id.in_(purchase_id_list)).all()
        return render_template("4-1_result_search_purchase.html",purchase_details=purchase_details)
    elif item_name:
        purchase_details = Purchase_detail.query.filter(Purchase_detail.item_id.in_(item_id_list)).all()
        return render_template("4-1_result_search_purchase.html",purchase_details=purchase_details)
    else:
        return render_template("error.html")

#4-2.総顧客数算出
@app.route("/sum_count_customers",methods=["POST"])
def sum_count_customers():
    statistics_type = "総顧客数"   
    number_of_customers = db.session.query(Customer).count()
    result = str(number_of_customers)+"人"
    return render_template("4-2_result_statistics.html",statistics_type=statistics_type,result=result)

#4-3.総販売数量算出
@app.route("/count_quantity",methods=["POST"])
def count_quantitys():
    statistics_type = "総販売商品数量"
    #sum関数は存在しないため、sqlalchemyからfuncをインポートする
    #query(func.sum(テーブル.カラム名)).first()→クエリの形から変換 
    total_quantity = db.session.query(func.sum(Purchase_detail.quantity)).first()
    #(4.0,)という形で格納されている型はsqlalchemy.engine.row.Row
    for row in total_quantity:
        result =row
    #4.0を4に直しstrへ変換
    result = str(int(result))+"個"
    return render_template("4-2_result_statistics.html",statistics_type=statistics_type,result=result)

#4-4.総売上算出
@app.route("/total_sales",methods=["POST"])
def total_sales():
    statistics_type = "総売上"
    joined_table = db.session.query(Purchase_detail.purchase_id,Item.price,Item.item_id,Purchase_detail.quantity).join(Item,Purchase_detail.item_id==Item.item_id).all()
    total_sales = 0

    for row in joined_table:
        if row.quantity:
            sale = row.price * row.quantity
            total_sales += sale
    
    result = str(total_sales)+"円"
    return render_template("4-2_result_statistics.html",statistics_type=statistics_type,result=result)

#4-5.販売数量別ランキング
@app.route("/ranking_items",methods=["POST"])
def ranking_items():
    statistics_type = "販売数量別ランキング"
    purchase_details = Purchase_detail.query.all()
    #order byは列内の並び替えだが、今回は商品ごとに足しあげた上で並び替えが必要（通常のpythonプログラムでカバーする）
    item_count_dict ={}
    #{item_A:総数量,
    #item_B:総数量}→辞書型に対してカウンター形式で値を更新していく
    for purchase_detail in purchase_details:
        item_id = purchase_detail.item_id
        quantity = purchase_detail.quantity
        if quantity:
            if item_count_dict.get(item_id) is None:
                item_count_dict[item_id]=quantity
            else:
                item_count_dict[item_id] = item_count_dict[item_id] + quantity

    #数量に基づいて並び替える
    #無名関数
    #def func(x):
        #return x[1]と同じ
    #items()→listの中にタプルでkeyとvalueが入っている
    item_count_dict = sorted(item_count_dict.items(),key=lambda x:x[1],reverse=True)

    items =[]
    #enumerateでソート後の辞書型からindex:何番目（高い順）とその商品名を
    for index,item_tuple in enumerate(item_count_dict):
        #商品名の入ったリスト
        item = list(item_tuple)
        #クエリからitem_idに該当する商品名を抽出
        item_name = Item.query.filter_by(item_id=item[0]).first().item_name
        item.append(item_name)
        item.append(str(index+1)+"位")
        items.append(item)
    #itemsの中にはitem_id,総数量,item_name,順位で格納されている
    return render_template("4-3_result_ranking_items.html",statistics_type=statistics_type,items=items)

if __name__=="__main__":
    app.run(debug=True)