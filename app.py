from flask import Flask, render_template, request, redirect, url_for, session
import networkx as nx
import matplotlib.pyplot as plt
import io
import base64
import matplotlib
matplotlib.use('Agg')

app = Flask(__name__)
app.secret_key = 'ваш_секретный_ключ'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        matrix_input = request.form['matrix']
        matrix_input = matrix_input.strip().replace(',', ' ')
        matrix = [list(map(int, row.split())) for row in matrix_input.split('\n')]
        session['matrix'] = matrix
        return redirect(url_for('visualize_graph'))
    # Очистка данных о матрице при первом заходе на страницу
    session.pop('matrix', None)
    return render_template('index.html')

@app.route('/visualize', methods=['GET', 'POST'])
def visualize_graph():
    matrix = session.get('matrix')
    if not matrix:
        return redirect(url_for('index'))

    G = nx.Graph()
    for i in range(len(matrix)):
        for j in range(len(matrix)):
            if matrix[i][j] != 0:
                G.add_edge(i + 1, j + 1, weight=matrix[i][j])

    pos = nx.spring_layout(G)
    edges = G.edges(data=True)

    plt.figure()
    nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=500, font_size=10)
    nx.draw_networkx_edge_labels(G, pos, edge_labels={(u, v): d['weight'] for u, v, d in edges})

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()

    mst = nx.minimum_spanning_tree(G, algorithm='kruskal')

    if request.method == 'POST':
        start = int(request.form['start'])
        end = int(request.form['end'])
        algorithm = request.form['algorithm']
        if algorithm == 'dijkstra':
            path = nx.dijkstra_path(G, start, end)
        elif algorithm == 'prim':
            mst = nx.minimum_spanning_tree(G, algorithm='prim')
            path = list(nx.shortest_path(mst, start, end))
        else:  # kruskal
            mst = nx.minimum_spanning_tree(G, algorithm='kruskal')
            path = list(nx.shortest_path(mst, start, end))

        edges = [(path[i], path[i + 1]) for i in range(len(path) - 1)]

        plt.figure()
        nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=500, font_size=10)
        nx.draw_networkx_edge_labels(G, pos, edge_labels={(u, v): d['weight'] for u, v, d in G.edges(data=True)})
        nx.draw_networkx_edges(G, pos, edgelist=edges, edge_color='r', width=2)

        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        image_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()

        path_weight = sum(G[u][v]['weight'] for u, v in zip(path[:-1], path[1:]))
        return render_template('visualize.html', image_base64=image_base64, path=' -> '.join(map(str, path)), path_weight=path_weight)

    return render_template('visualize.html', image_base64=image_base64)

if __name__ == '__main__':
    app.run(debug=True)
