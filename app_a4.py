from flask import Flask, render_template, request
import sqlite3 as sql
import io
import base64
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import datetime
import random

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index_a4.html')

@app.route('/mag', methods=['GET','POST'])
def mag():
    categories = []
    counts = []
    with sql.connect("a4database.db") as con:
        cur = con.cursor()
        query = """
        SELECT 
            CASE
                WHEN mag < 1 THEN 'Less than 1'
                WHEN mag >= 1 AND mag < 2 THEN '1 - 2'
                WHEN mag >= 2 AND mag < 3 THEN '2 - 3'
                WHEN mag >= 3 AND mag < 4 THEN '3 - 4'
                WHEN mag >= 4 AND mag < 5 THEN '4 - 5'
                ELSE 'Greater than or equal to 5'
            END AS magnitude_category,
            COUNT(*) AS count
        FROM
            earthquake
        GROUP BY
            magnitude_category;
        """
        cur.execute(query)
        rows = cur.fetchall()
        for i in rows:
            categories.append(i[0])
            counts.append(i[1])
        
    con.close()

    return render_template('mag.html', categories=categories, counts=counts)


@app.route('/magdep', methods=['GET', 'POST'])
def magdep():
    magnitudes = []
    depths = []
    with sql.connect('a4database.db') as con:
        # print("Connected to database")
        cursor = con.cursor()
        # Fetch the recent earthquake data
        cursor.execute("SELECT mag, depth FROM earthquake ORDER BY date(time) DESC LIMIT 100")
        data = cursor.fetchall()
        # print(len(data))
        for row in data:
            magnitudes.append(row[0])
            depths.append(row[1])
        # print(magnitudes)
    con.close()

    return render_template('magdep.html', magnitudes=magnitudes, depths=depths)

@app.route('/net', methods=['GET', 'POST'])
def net():
    net = []
    counts = []
    with sql.connect("a4database.db") as con:
        cur = con.cursor()
        cur.execute("select distinct net , count(*) as total from earthquake group by net")
        rows = cur.fetchall()
        for i in rows:
            net.append(i[0])
            counts.append(i[1])
        
    con.close()

    return render_template('net.html', net=net, counts=counts)

@app.route('/specified', methods=['GET', 'POST'])
def specified():
    return render_template('specified.html')

@app.route('/specifiedresult', methods=['GET', 'POST'])
def specifiedresult():
    if request.method=='POST':
        data=[]
        count=[]
        restriction=request.form['restriction']
        if restriction=='location':
            location_inputs=request.form['location_inputs']
            con = sql.connect('a4database.db')
            cursor = con.cursor()
            cursor.execute("SELECT date(time), count(*) as total FROM earthquake WHERE net=? and type='earthquake' GROUP BY date(time)", (location_inputs,))
            row=cursor.fetchall()
            print(row)
            for i in row:
                data.append(i[0])
                count.append(i[1])
            con.close()
            return render_template('specifiedlocation.html', location_inputs=location_inputs,data=data,count=count)

        elif restriction=='time_range':
            start_time=request.form['start_time']
            end_time=request.form['end_time']
            con = sql.connect('a4database.db')
            cursor = con.cursor()
            query = """
                SELECT date(time), COUNT(*) AS total
                FROM earthquake
                WHERE date(time) BETWEEN ? AND ? and type='earthquake'
                GROUP BY date(time)
                        """
            cursor.execute(query,(start_time,end_time))
            row=cursor.fetchall()
            print(row)
            for i in row:
                data.append(i[0])
                count.append(i[1])
            con.close()
            print(data)
            print(count)
            return render_template('specifiedtime.html', data=data, count=count, start_time=start_time, end_time=end_time)

        elif restriction == 'mag_range':
            min_mag = request.form['min_mag']
            max_mag = request.form['max_mag']

            con = sql.connect('a4database.db')
            cursor = con.cursor()
            cursor.execute("""
                SELECT mag, COUNT(*) AS total
                FROM earthquake
                WHERE mag BETWEEN ? AND ? AND type = 'earthquake'
                GROUP BY mag
            """, (min_mag, max_mag))
            rows = cursor.fetchall()

            for row in rows:
                data.append(row[0])
                count.append(row[1])

        con.close()

    return render_template('specifiedmag.html', data=data,count=count,min_mag=min_mag,max_mag=max_mag)

@app.route('/generate_chart')
def generate_chart():
    return render_template('chart.html')

@app.route('/generate_chart1', methods=['POST'])
def generate_chart1():
    n = int(request.form['n'])
    
    # Generate random data for the pie chart
    data = [random.randint(50, 250) for _ in range(n)]
    
    # Calculate the fraction for each pie slice
    total_entries = sum(data)
    fraction = 1 / n
    
    chart_data = []
    for count in data:
        chart_data.append({
            # 'name': '',
            'y': count * fraction
        })
    print(chart_data)
    return render_template('chart.html', n=n, chart_data=chart_data)

if __name__ == '__main__':
    app.run(port=8000, debug=True)