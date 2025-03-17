from pyvis.network import Network
import networkx as nx
import numpy as np
import pandas as pd
import webbrowser
import Visualizer
import init

def main():


    # ============================
    # 2. Формирование "используемого" графа (для матриц)
    # ============================
    filtered_graph = {}
    for vertex, neighbors in init.graph.items():
        if vertex not in init.excluded_vertices:
            # Берём только соседей, которые тоже не исключены и ребро не находится в списке исключаемых
            filtered_neighbors = {
                neigh for neigh in neighbors
                if neigh not in init.excluded_vertices and frozenset((vertex, neigh)) not in init.excluded_edges
            }
            filtered_graph[vertex] = filtered_neighbors

    # Подсчёт степеней вершин (для используемого графа) и создание диагональной матрицы
    neighbor_counts = [len(neighbors) for vertex, neighbors in filtered_graph.items()]
    degree_matrix = np.diag(neighbor_counts)



    # ============================
    # 4. Вычисление матрицы смежности (только для используемого графа)
    # ============================
    G = nx.Graph()
    for vertex, neighbors in filtered_graph.items():
        G.add_node(vertex)
        for neigh in neighbors:
            G.add_edge(vertex, neigh)

    adj_matrix = nx.to_pandas_adjacency(G, nodelist=sorted(filtered_graph.keys()), dtype=int)
    adj_matrix_html = adj_matrix.to_html(classes="adjacency-matrix", border=1, col_space=25, justify='center')
    degree_matrix_html = pd.DataFrame(degree_matrix).to_html(
        index=False, header=False, classes="degree-matrix", border=1, col_space=25, justify='center'
    )
    vertices_filtered = sorted(filtered_graph.keys())
    A = nx.to_numpy_array(G, nodelist=vertices_filtered, dtype=float)
    degrees = np.sum(A, axis=1)
    B = np.diag(degrees)
    Laplasian_mat = B - A
    print(Laplasian_mat)

    
    eigvals, eigvecs = np.linalg.eigh(Laplasian_mat)
    # (np.linalg.eigh возвращает отсортированные по возрастанию собственные значения, но для явности отсортируем)
    idx = np.argsort(eigvals)
    eigvals = eigvals[idx]
    eigvecs = eigvecs[:, idx]
    # Вывод собственных значений (округлим до 4 знаков)
    eigenvalues_str = np.round(eigvals, 4)
    print (eigenvalues_str)

    # Для задачи бисекции используем второй собственный вектор (Fiedler vector)
    fiedler_vector = eigvecs[:, 1]
    average_value = np.mean(fiedler_vector)
    
    # Выполняем спектральную бисекцию: делим вершины на две группы по сравнению с average_value
    group1 = [vertex for i, vertex in enumerate(vertices_filtered) if fiedler_vector[i] > average_value]
    group2 = [vertex for i, vertex in enumerate(vertices_filtered) if fiedler_vector[i] <= average_value]

    print ("group 1 : ", group1)
    print ("group 2 : ", group2)
   
    eigen_info_html = Visualizer.get_slove_html(eigenvalues_str, fiedler_vector, average_value, group1, group2)
    graph_html = Visualizer.get_net_graph(group1, group2)

    tables_html = Visualizer.include_css_to_html(adj_matrix_html, degree_matrix_html)
    combined_html = Visualizer.graph_into_dev (graph_html, tables_html, eigen_info_html)
    

    # ============================
    # 6. Запись результата и открытие в браузере
    # ============================
    output_file = "./res/graph_with_matrix.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(combined_html)

    webbrowser.open(output_file)

if __name__ == '__main__':
    main()
