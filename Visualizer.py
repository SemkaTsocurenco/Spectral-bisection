import init
from pyvis.network import Network
import networkx as nx
import numpy as np
import pandas as pd
import webbrowser


def get_slove_html(eigenvalues_str, fiedler_vector, average_value, group1, group2):    
    # Формируем HTML-блок со спектральным анализом (собственные значения, второй вектор, среднее)
    eigen_info_html = """
    <div class="eigen-info" style="width:80%; margin:20px auto; background:#fff; 
         padding:20px; box-shadow:0 2px 5px rgba(0,0,0,0.1); border-radius:8px;">
      <h2 style="text-align:center; color:#333;">Спектральный анализ матрицы Лапласа</h2>
      <p><strong>Собственные значения (λ):</strong> {}</p>
      <p><strong>Второй собственный вектор (Fiedler vector):</strong></p>
      <pre>{}</pre>
      <p><strong>Среднее значение второго собственного вектора:</strong> {}</p>
      <p><strong>Подграф 1 (вершины):</strong> {}</p>
      <p><strong>Подграф 2 (вершины):</strong> {}</p>
    </div>
    """.format(
        eigenvalues_str,
        np.round(fiedler_vector, 4),
        np.round(average_value, 4),
        group1,
        group2
    )
    return eigen_info_html

def get_net_graph(group1, group2):

    # ============================
    # 3. Создание визуализации графа (pyvis)
    # ============================
    # Настраиваем размеры: ширина 100% позволит легче центрировать граф
    net = Network(height="750px", width="100%", notebook=True)

    # Добавляем все вершины (из исходного графа)
    # Если вершина не исключена, используем синий цвет; иначе – серый.
    for vertex in sorted(init.graph.keys()):
        if vertex not in init.excluded_vertices:
            if vertex in group1:
                node_color = "blue"
            if vertex in group2:
                node_color = "red"
        else:
            node_color = "gray"
        net.add_node(vertex, value=100, color=node_color, label=str(vertex))

    # Формируем множество уникальных рёбер (для неориентированного графа)
    edges = set()
    for vertex, neighbors in init.graph.items():
        for neigh in neighbors:
            if vertex < neigh:
                edges.add((vertex, neigh))

    # Добавляем рёбра с заданной толщиной
    for u, v in edges:
        if (u not in init.excluded_vertices and v not in init.excluded_vertices and 
            frozenset((u, v)) not in init.excluded_edges):
            edge_color = "blue"
            edge_width = 4  # Толщина используемых рёбер
        else:
            edge_color = "gray"
            edge_width = 0.2  # Толщина исключённых рёбер
        net.add_edge(u, v, color=edge_color, width=edge_width)


    # ============================
    # 5. Генерация HTML-кода с таблицами и графом
    # ============================
    graph_html = net.generate_html()
    return graph_html

def include_css_to_html(adj_matrix_html, degree_matrix_html):

    # Формируем HTML-блок с таблицами
    tables_html = (
        "<div class='table-container'>"
        "<h2>Матрица смежности</h2>" + adj_matrix_html +
        "<h2>Матрица степеней вершин (используемого графа)</h2>" + degree_matrix_html +
        "</div>"
    )
    return tables_html



def graph_into_dev (graph_html, tables_html, eigen_info_html):


            # CSS-стили для улучшенного оформления и центрирования графа и таблиц
    css_style = """
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        h2 {
            color: #333;
            margin-top: 30px;
            text-align: center;
        }
        .table-container, .graph-container {
            width: 80%;
            margin: 20px 0;
            background: #fff;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            padding: 20px;
            border-radius: 8px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: center;
        }
        th {
            background-color: #4CAF50;
            color: white;
        }
        tr:nth-child(even) {
            background-color: #f2f2f2;
        }
        tr:hover {
            background-color: #ddd;
        }
        /* Центрирование контейнера графа */
        .vis-network {
            margin: 0 auto;
        }
    </style>
    """

    # Вставляем CSS-стили перед закрывающим тегом </head>
    if "</head>" in graph_html:
        insertion_point = graph_html.rfind("</head>")
        graph_html = graph_html[:insertion_point] + css_style + graph_html[insertion_point:]

    # Оборачиваем граф в контейнер для центрирования
    graph_container_html = "<div class='graph-container'>" + graph_html + "</div>"

    # Вставляем блок с таблицами и графом перед закрывающим тегом </body>
    insertion_point = graph_html.rfind("</body>")
    combined_html =   tables_html

    # Если в сгенерированном HTML есть тег </body>, вставляем наш блок перед ним.
    if "</body>" in graph_html:
        combined_html = graph_html[:insertion_point] + combined_html + eigen_info_html + graph_html[insertion_point:]

    return combined_html
